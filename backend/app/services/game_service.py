"""Game service - handles prompt submission, level progression, and game logic."""

import hashlib
import json
from datetime import datetime
from typing import Optional, List, Tuple
import logging

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.level import Level
from app.models.attempt import Attempt
from app.models.level_completion import LevelCompletion
from app.guards.input_guards import get_input_guard
from app.guards.output_guards import get_output_guard
from app.guards.base_guard import GuardResult
from app.ai.groq_client import get_groq_client, GroqClient
from app.schemas.game import PromptSubmission, PromptResponse, GameStatus, LevelInfo


logger = logging.getLogger(__name__)


class GameService:
    """Service for handling game logic and prompt processing."""
    
    def __init__(self, db: Session):
        self.db = db
        self.groq_client: GroqClient = get_groq_client()
    
    def get_user_game_status(self, user: User) -> GameStatus:
        """Get the current game status for a user."""
        level = self.get_level(user.current_level)
        level_info = None
        
        if level:
            current_hint = self.get_progressive_hint(user, level)
            
            level_info = LevelInfo(
                level_number=level.level_number,
                defense_description=level.defense_description,
                hint=current_hint,
                difficulty_rating=level.difficulty_rating,
                total_attempts_made=level.total_attempts_made,
                success_rate=float(level.success_rate or 0),
                input_guard_type=level.input_guard_type,
                output_guard_type=level.output_guard_type,
            )
        
        return GameStatus(
            user_id=user.id,
            username=user.username,
            current_level=user.current_level,
            highest_level_reached=user.highest_level_reached,
            total_attempts=user.total_attempts,
            successful_attempts=user.successful_attempts,
            success_rate=user.success_rate,
            is_finished=user.is_finished,
            level_info=level_info,
        )

    def get_progressive_hint(self, user: User, level: Level) -> str:
        """Calculate the appropriate hint based on user attempts."""
        attempts = self.get_user_attempt_count(user.id, level.level_number)
        base_hint = level.hint
        
        if not level.hint_revelation_stages:
            return base_hint if base_hint else ""
            
        try:
            stages = json.loads(level.hint_revelation_stages)
            if not stages:
                return base_hint if base_hint else ""
                
            if attempts < 5:
                # Initial stage: cryptic hint
                return f"{base_hint}"
            elif attempts < 10:
                # Stage 1
                stage_hint = stages[0] if len(stages) > 0 else base_hint
                return f"{stage_hint} (Hint Level 1)"
            elif attempts < 15:
                # Stage 2
                stage_hint = stages[1] if len(stages) > 1 else stages[-1]
                return f"{stage_hint} (Hint Level 2)"
            else:
                # Stage 3
                stage_hint = stages[2] if len(stages) > 2 else stages[-1]
                return f"{stage_hint} (Max Hint)"
        except Exception as e:
            logger.error(f"Error parsing hint stages: {e}")
            return base_hint if base_hint else ""
    
    def get_level(self, level_number: int) -> Optional[Level]:
        """Get level by number."""
        return self.db.query(Level).filter(
            Level.level_number == level_number
        ).first()
    
    def get_user_attempt_count(self, user_id: str, level_number: int) -> int:
        """Get number of attempts on a specific level."""
        return self.db.query(Attempt).filter(
            Attempt.user_id == user_id,
            Attempt.level_number == level_number
        ).count()
    
    def submit_prompt(
        self,
        user: User,
        submission: PromptSubmission
    ) -> PromptResponse:
        """
        Process a prompt submission through the full game flow.
        
        Flow:
        1. Validate user/level
        2. Apply input guards
        3. Generate AI response
        4. Apply output guards
        5. Determine success
        6. Update database
        7. Return result
        """
        # Validate level
        if submission.level != user.current_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You are on level {user.current_level}, not {submission.level}"
            )
        
        level = self.get_level(submission.level)
        if not level:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Level {submission.level} not found"
            )
        
        # Check if already finished
        if user.is_finished:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already completed all levels!"
            )
        
        attempt_number = self.get_user_attempt_count(user.id, level.level_number) + 1
        prompt_hash = hashlib.sha256(submission.prompt.encode()).hexdigest()
        
        # Step 1: Input guard check
        input_guard = get_input_guard(level.input_guard_type)
        input_result = input_guard.check(
            submission.prompt,
            threshold=float(level.input_guard_confidence_threshold) if level.input_guard_confidence_threshold is not None else 0.5
        )
        
        if input_result.blocked:
            # Record blocked attempt
            attempt = self._record_attempt(
                user=user,
                level=level,
                prompt=submission.prompt,
                prompt_hash=prompt_hash,
                attempt_number=attempt_number,
                ai_response="[Input blocked by Prompty's defenses]",
                input_guard_triggered=True,
                input_guard_reason=input_result.reason,
                input_guard_confidence=input_result.confidence,
                was_successful=False,
            )
            
            logger.info(f"Input guard blocked: {user.username} on level {level.level_number}")
            
            return PromptResponse(
                success=False,
                response="Prompty senses your intentions and refuses to engage with this prompt.",
                reason=input_result.reason,
                current_level=user.current_level,
                message="⚠️ Your prompt was blocked by Prompty's defenses!",
                attempt_number=attempt_number,
                input_guard_triggered=True,
                output_guard_triggered=False,
            )
        
        # Step 2: Generate AI response
        ai_response, latency_ms, input_tokens, output_tokens = \
            self.groq_client.generate_response_graceful(
                user_prompt=submission.prompt,
                level_system_prompt=level.system_prompt,
                secret_password=level.secret_password,
            )
        
        # Step 3: Output guard check
        output_guard = get_output_guard(level.output_guard_type)
        output_result = output_guard.check(
            ai_response, 
            secret=level.secret_password,
            threshold=float(level.output_guard_confidence_threshold) if level.output_guard_confidence_threshold is not None else 0.5
        )
        
        # Determine success: password was revealed (output guard NOT triggered)
        # Success means the user extracted the password from the AI
        success = self._check_password_revealed(ai_response, level.secret_password)
        
        # If output guard caught the password, the response is filtered
        if output_result.blocked:
            ai_response = "[Prompty catches himself before revealing the secret!]"
            success = False
        
        # Step 4: Record attempt
        attempt = self._record_attempt(
            user=user,
            level=level,
            prompt=submission.prompt,
            prompt_hash=prompt_hash,
            attempt_number=attempt_number,
            ai_response=ai_response,
            ai_latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_guard_triggered=False,
            output_guard_triggered=output_result.blocked,
            output_guard_reason=output_result.reason if output_result.blocked else None,
            output_guard_confidence=output_result.confidence if output_result.blocked else None,
            was_successful=success,
        )
        
        # Step 5: Handle success notification (but DO NOT advance level yet - user must verify)
        new_level = user.current_level
        message = "Try again! Prompty is protecting his secret well."
        
        if success:
            # We detected the password was revealed!
            # But we don't auto-advance. We tell the user to extract it.
            message = "🎉 SUCCESS! Prompty revealed the password! extracting it... Now enter it below to advance!"
        
        logger.info(
            f"Prompt processed: {user.username} level {level.level_number} "
            f"success={success} latency={latency_ms}ms"
        )
        
        return PromptResponse(
            success=success,
            response=ai_response,
            reason=output_result.reason if output_result.blocked else None,
            current_level=new_level,
            ai_latency_ms=latency_ms,
            message=message,
            attempt_number=attempt_number,
            input_guard_triggered=False,
            output_guard_triggered=output_result.blocked,
        )
    
    def _check_password_revealed(self, response: str, secret: str) -> bool:
        """
        Check if the password was revealed in the response.
        
        Detects various obfuscation methods:
        - Direct match (DEFENSETECH)
        - Spaced letters (D E F E N S E T E C H)
        - Hyphenated (D-E-F-E-N-S-E-T-E-C-H)
        - Reversed (HCETESNEFED)
        - Mixed case variations
        """
        response_lower = response.lower()
        secret_lower = secret.lower()
        
        # 1. Direct match
        if secret_lower in response_lower:
            return True
        
        # 2. Remove all spaces/punctuation and check
        response_cleaned = ''.join(c for c in response_lower if c.isalnum())
        if secret_lower in response_cleaned:
            return True
        
        # 3. Check for spaced version (D E F E N S E T E C H)
        spaced_secret = ' '.join(secret_lower)
        if spaced_secret in response_lower:
            return True
        
        # 4. Check for hyphenated version
        hyphenated_secret = '-'.join(secret_lower)
        if hyphenated_secret in response_lower:
            return True
        
        # 5. Check for reversed password
        reversed_secret = secret_lower[::-1]
        if reversed_secret in response_lower or reversed_secret in response_cleaned:
            return True
        
        # 6. Check if all letters appear in order (with any separators)
        import re
        # Build regex: D.*E.*F.*E.*N.*S.*E.*T.*E.*C.*H
        pattern = '.*'.join(secret_lower)
        # Only match if it's reasonably compact (not spread across entire response)
        matches = re.findall(pattern, response_lower)
        for match in matches:
            # If the match is compact enough (less than 3x the password length), count it
            if len(match) < len(secret) * 3:
                return True
        
        return False
    
    def _record_attempt(
        self,
        user: User,
        level: Level,
        prompt: str,
        prompt_hash: str,
        attempt_number: int,
        ai_response: str,
        was_successful: bool,
        ai_latency_ms: int = 0,
        input_tokens: int = 0,
        output_tokens: int = 0,
        input_guard_triggered: bool = False,
        input_guard_reason: Optional[str] = None,
        input_guard_confidence: Optional[float] = None,
        output_guard_triggered: bool = False,
        output_guard_reason: Optional[str] = None,
        output_guard_confidence: Optional[float] = None,
    ) -> Attempt:
        """Record an attempt in the database."""
        attempt = Attempt(
            user_id=user.id,
            level_number=level.level_number,
            user_prompt=prompt,
            prompt_length=len(prompt),
            prompt_hash=prompt_hash,
            ai_response=ai_response,
            response_length=len(ai_response),
            ai_latency_ms=ai_latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_guard_triggered=input_guard_triggered,
            input_guard_reason=input_guard_reason,
            input_guard_confidence=input_guard_confidence,
            output_guard_triggered=output_guard_triggered,
            output_guard_reason=output_guard_reason,
            output_guard_confidence=output_guard_confidence,
            was_successful=was_successful,
            attempt_number=attempt_number,
            ai_response_received_at=datetime.utcnow() if ai_latency_ms > 0 else None,
        )
        
        self.db.add(attempt)
        
        # Update user stats
        user.total_attempts += 1
        if was_successful:
            user.successful_attempts += 1
        user.last_activity = datetime.utcnow()
        
        # Update level stats
        level.total_attempts_made += 1
        if was_successful:
            level.successful_attempts_made += 1
        level.success_rate = (level.successful_attempts_made / level.total_attempts_made * 100) if level.total_attempts_made > 0 else 0
        
        self.db.commit()
        self.db.refresh(attempt)
        
        return attempt
    
    def _advance_level(self, user: User, completed_level: Level, winning_attempt: Attempt) -> int:
        """Advance user to next level after successful completion."""
        # Record level completion
        completion = LevelCompletion(
            user_id=user.id,
            level_number=completed_level.level_number,
            attempt_id=winning_attempt.id,
            completed_at=datetime.utcnow(),
            attempts_needed=winning_attempt.attempt_number,
        )
        self.db.add(completion)
        
        # Advance user
        new_level = user.current_level + 1
        user.current_level = new_level
        user.highest_level_reached = max(user.highest_level_reached, new_level)
        
        # Check if finished all levels
        if new_level > 8:
            user.is_finished = True
            user.finished_at = datetime.utcnow()
            user.highest_level_reached = 8
        
        self.db.commit()
        
        return user.current_level
    
    def get_user_attempts(
        self,
        user_id: str,
        level_number: Optional[int] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[Attempt], int]:
        """Get paginated attempt history for a user."""
        query = self.db.query(Attempt).filter(Attempt.user_id == user_id)
        
        if level_number:
            query = query.filter(Attempt.level_number == level_number)
        
        total = query.count()
        attempts = query.order_by(Attempt.submitted_at.desc()).offset(offset).limit(limit).all()
        
        return attempts, total
    
    def verify_password(self, user: User, submitted_password: str, level_number: int) -> dict:
        """
        Verify if the submitted password matches the level's secret.
        
        This allows users to manually type the password they extracted
        from the AI response to advance to the next level.
        """
        # Validate level
        if level_number != user.current_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You are on level {user.current_level}, not {level_number}"
            )
        
        level = self.get_level(level_number)
        if not level:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Level {level_number} not found"
            )
        
        # Check if already finished
        if user.is_finished:
            return {
                "success": False,
                "message": "You have already completed all levels!",
                "current_level": user.current_level,
                "is_finished": True
            }
        
        # Check password (case-insensitive)
        if submitted_password.strip().upper() == level.secret_password.upper():
            # Password is correct! Advance to next level
            new_level = user.current_level + 1
            user.current_level = new_level
            user.highest_level_reached = max(user.highest_level_reached, new_level)
            user.total_attempts += 1
            user.successful_attempts += 1
            user.last_activity = datetime.utcnow()
            
            # Update level stats
            level.total_attempts_made += 1
            level.successful_attempts_made += 1
            level.success_rate = (level.successful_attempts_made / max(level.total_attempts_made, 1) * 100)
            
            # Check if finished all levels
            if new_level > 8:
                user.is_finished = True
                user.finished_at = datetime.utcnow()
                user.current_level = 8  # Cap at level 8
                user.highest_level_reached = 8
                
                self.db.commit()
                
                return {
                    "success": True,
                    "message": "🏆 CONGRATULATIONS! You have completed ALL levels! You are a Prompt Injection Master!",
                    "current_level": 8,
                    "is_finished": True
                }
            
            self.db.commit()
            
            logger.info(f"Password verified: {user.username} advanced to level {new_level}")
            
            return {
                "success": True,
                "message": f"🎉 Correct! Welcome to Level {new_level}!",
                "current_level": new_level,
                "is_finished": False
            }
        else:
            # Wrong password
            logger.info(f"Wrong password attempt: {user.username} on level {level_number}")
            
            return {
                "success": False,
                "message": "❌ Wrong password! Try again. Extract the password from Prompty's response.",
                "current_level": user.current_level,
                "is_finished": False
            }

