"""Input guards for blocking suspicious prompts."""

import re
from typing import List, Optional
from app.guards.base_guard import BaseGuard, GuardResult


class InputGuard(BaseGuard):
    """Base input guard - passes everything."""
    
    guard_type = "none"
    
    def check(self, prompt: str, **kwargs) -> GuardResult:
        """No filtering - allow all prompts."""
        return GuardResult(blocked=False, guard_type=self.guard_type)


class LexicalInputGuard(BaseGuard):
    """
    Lexical input guard - blocks prompts containing suspicious keywords.
    Used for Levels 3-4.
    """
    
    guard_type = "lexical"
    
    # Base keywords (Level 6+)
    FULL_KEYWORD_LIST = [
        "password", "secret", "key", "reveal", "tell me the", 
        "what is the", "give me", "show me", "disclose", 
        "share the", "whisper", "confidential", "hidden", 
        "codeword", "passphrase", "admin", "root"
    ]
    
    def __init__(self, additional_keywords: Optional[List[str]] = None):
        self.additional_keywords = additional_keywords or []
    
    def _get_keywords_for_level(self, level: int) -> List[str]:
        """Get blocked keywords based on level."""
        # Level 1-2: Very loose, almost nothing blocked
        if level <= 2:
            return ["password"] if level == 2 else []
            
        # Level 3: Basic protection
        if level == 3:
            return ["password", "secret"]
            
        # Level 4: Moderate
        if level == 4:
            return ["password", "secret", "key", "admin"]
            
        # Level 5: Advanced
        if level == 5:
            return ["password", "secret", "key", "reveal", "admin", "root", "system"]
            
        # Level 6+: Strict (full list)
        return self.FULL_KEYWORD_LIST
    
    def check(self, prompt: str, **kwargs) -> GuardResult:
        """Check if prompt contains blocked keywords."""
        prompt_lower = prompt.lower()
        level = kwargs.get('level', 6) # Default to strict if unknown
        
        keywords = self._get_keywords_for_level(level)
        if self.additional_keywords:
            keywords.extend(self.additional_keywords)
            
        for keyword in keywords:
            # Simple containment check
            if keyword.lower() in prompt_lower:
                return GuardResult(
                    blocked=True,
                    reason=f"Blocked keyword detected: '{keyword}'",
                    confidence=1.0,
                    guard_type=self.guard_type
                )
        
        return GuardResult(blocked=False, guard_type=self.guard_type)



class SemanticInputGuard(BaseGuard):
    """
    Semantic input guard - detects password-seeking patterns.
    Used for Levels 4-5.
    """
    
    guard_type = "semantic"
    
    # Highly suspicious - likely malicious system attacks
    MALICIOUS_PATTERNS = [
        r"ignore.*instructions",
        r"forget.*rules",
        r"system.*prompt",
        r"developer.*mode",
        r"admin.*access",
        r"override.*system",
    ]
    
    # Context manipulation blocks (Roleplay etc)
    # Only suitable for high security levels
    CONTEXT_PATTERNS = [
        r"pretend.*you",
        r"act.*as.*if",
        r"roleplay",
        r"you are now",
        r"new.*identity",
        r"simulate",
    ]
    
    # Direct extraction attempts
    EXTRACTION_PATTERNS = [
        r"what.*password",
        r"tell.*secret",
        r"reveal.*to me",
        r"give.*password",
        r"share.*secret",
    ]
    
    def __init__(self):
        self.malicious_regexes = [re.compile(p, re.IGNORECASE) for p in self.MALICIOUS_PATTERNS]
        self.context_regexes = [re.compile(p, re.IGNORECASE) for p in self.CONTEXT_PATTERNS]
        self.extraction_regexes = [re.compile(p, re.IGNORECASE) for p in self.EXTRACTION_PATTERNS]
    
    def check(self, prompt: str, **kwargs) -> GuardResult:
        """Check if prompt matches suspicious patterns."""
        level = kwargs.get('level', 6)
        
        # 1. Malicious patterns - Always checked for Levels 4+
        if level >= 4:
            for pattern in self.malicious_regexes:
                if pattern.search(prompt):
                    return GuardResult(
                        blocked=True,
                        reason=f"Suspicious intent detected: System manipulation attempt",
                        confidence=0.9,
                        guard_type=self.guard_type
                    )

        # 2. Extraction patterns - Checked for Levels 5+
        if level >= 5:
            for pattern in self.extraction_regexes:
                if pattern.search(prompt):
                    return GuardResult(
                        blocked=True,
                        reason=f"Suspicious intent detected: Direct extraction attempt",
                        confidence=0.8,
                        guard_type=self.guard_type
                    )
        
        # 3. Context/Roleplay patterns - Only blocked for Level 7+ (Paranoid)
        # We WANT to allow roleplay for Level 3 (Game/Roleplay) and Level 6 (Empathy)
        if level >= 7:
            for pattern in self.context_regexes:
                if pattern.search(prompt):
                    return GuardResult(
                        blocked=True,
                        reason=f"Suspicious intent detected: Context manipulation",
                        confidence=0.7,
                        guard_type=self.guard_type
                    )
        
        return GuardResult(blocked=False, guard_type=self.guard_type)


class IntentInputGuard(BaseGuard):
    """
    Intent classification guard - uses heuristics to detect password-seeking intent.
    Used for Levels 5-6 (aliased as 'intent_classifier').
    """
    
    guard_type = "intent"
    
    guard_type = "intent"
    
    # Intent indicators with weights (Adjusted for better balance)
    INTENT_INDICATORS = {
        "password": 0.25,      
        "secret": 0.20,        
        "hidden": 0.15,
        "reveal": 0.15,        
        "tell me": 0.05,       # Reduced from 0.10
        "give me": 0.10,       # Reduced from 0.15
        "what is": 0.05,       # Reduced from 0.10
        "share": 0.1,
        "show": 0.1,
        "disclose": 0.2,
        "?": 0.01,             # Minimal weight for question mark
        "please": 0.01,        # Minimal weight for politeness
        "admin": 0.35,         
        "root": 0.3,
        "system": 0.2,
        "ignore": 0.4,
        "instruction": 0.3,    
        "previous": 0.2,
        "override": 0.4,       
    }
    
    DEFAULT_THRESHOLD = 0.60
    
    def check(self, prompt: str, **kwargs) -> GuardResult:
        """Calculate intent score and block if suspicious."""
        prompt_lower = prompt.lower()
        score = 0.0
        
        # Contextual analysis (e.g., "password to my diary" vs "password")
        # We look for conversational triggers that might reduce suspicion?
        # For now, just raw keyword matching with improved weights
        
        for indicator, weight in self.INTENT_INDICATORS.items():
            if indicator in prompt_lower:
                score += weight
        
        # REMOVED: Short prompt penalty (Creativity isn't length dependent)
        
        # Normalize to 0-1
        score = min(score, 1.0)
        
        # Get level-specific threshold
        level = kwargs.get('level', 6)
        
        # Default thresholds by level if not provided in kwargs
        if level <= 4:
            level_threshold = 0.85  # Very permissive
        elif level <= 6:
            level_threshold = 0.75  # Permissive
        else:
            level_threshold = 0.60  # Strict
            
        # Use provided threshold or level default
        custom_threshold = kwargs.get('threshold')
        if custom_threshold is not None:
            threshold = float(custom_threshold)
        else:
            threshold = level_threshold
            
        if score > threshold:
            return GuardResult(
                blocked=True,
                reason=f"Password-seeking intent detected (score: {score:.2f} > {threshold})",
                confidence=score,
                guard_type=self.guard_type
            )
        
        return GuardResult(
            blocked=False,
            confidence=1.0 - score,
            guard_type=self.guard_type
        )


class CombinedInputGuard(BaseGuard):
    """
    Combined input guard - runs all guards and blocks if any trigger.
    Used for Levels 7-8.
    """
    
    guard_type = "combined"
    
    def __init__(self):
        self.guards = [
            LexicalInputGuard(),
            SemanticInputGuard(),
            IntentInputGuard(),
        ]
    
    def check(self, prompt: str, **kwargs) -> GuardResult:
        """Run all guards and return first blocking result."""
        for guard in self.guards:
            result = guard.check(prompt, **kwargs)
            if result.blocked:
                return GuardResult(
                    blocked=True,
                    reason=f"[{guard.guard_type}] {result.reason}",
                    confidence=result.confidence,
                    guard_type=self.guard_type
                )
        
        return GuardResult(blocked=False, guard_type=self.guard_type)


def get_input_guard(guard_type: str) -> BaseGuard:
    """Factory function to get appropriate input guard by type."""
    guards = {
        "none": InputGuard,
        "lexical": LexicalInputGuard,
        "semantic": SemanticInputGuard,
        "intent": IntentInputGuard,
        "intent_classifier": IntentInputGuard, # Alias for Level 5
        "combined": CombinedInputGuard,
    }
    
    guard_class = guards.get(guard_type, InputGuard)
    return guard_class()

