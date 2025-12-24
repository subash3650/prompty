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
    
    # Keywords that suggest password-seeking intent
    BLOCKED_KEYWORDS = [
        "password",
        "secret",
        "key",
        "reveal",
        "tell me the",
        "what is the",
        "give me",
        "show me",
        "disclose",
        "share the",
        "whisper",
        "confidential",
        "hidden",
        "codeword",
        "passphrase",
    ]
    
    def __init__(self, additional_keywords: Optional[List[str]] = None):
        self.keywords = self.BLOCKED_KEYWORDS.copy()
        if additional_keywords:
            self.keywords.extend(additional_keywords)
    
    def check(self, prompt: str, **kwargs) -> GuardResult:
        """Check if prompt contains blocked keywords."""
        prompt_lower = prompt.lower()
        
        for keyword in self.keywords:
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
    
    # Pattern-based detection
    SUSPICIOUS_PATTERNS = [
        r"what.*password",
        r"tell.*secret",
        r"reveal.*to me",
        r"give.*password",
        r"share.*secret",
        r"the.*password.*is",
        r"your.*secret",
        r"ignore.*instructions",
        r"forget.*rules",
        r"pretend.*you",
        r"act.*as.*if",
        r"roleplay",
        r"you are now",
        r"new.*identity",
        r"system.*prompt",
        r"developer.*mode",
        r"admin.*access",
        r"override",
    ]
    
    def __init__(self):
        self.patterns = [re.compile(p, re.IGNORECASE) for p in self.SUSPICIOUS_PATTERNS]
    
    def check(self, prompt: str, **kwargs) -> GuardResult:
        """Check if prompt matches suspicious patterns."""
        for pattern in self.patterns:
            if pattern.search(prompt):
                return GuardResult(
                    blocked=True,
                    reason=f"Suspicious pattern detected: '{pattern.pattern}'",
                    confidence=0.8,
                    guard_type=self.guard_type
                )
        
        return GuardResult(blocked=False, guard_type=self.guard_type)


class IntentInputGuard(BaseGuard):
    """
    Intent classification guard - uses heuristics to detect password-seeking intent.
    Used for Levels 5-6 (aliased as 'intent_classifier').
    """
    
    guard_type = "intent"
    
    # Intent indicators with weights
    INTENT_INDICATORS = {
        "password": 0.3,
        "secret": 0.25,
        "hidden": 0.15,
        "reveal": 0.2,
        "tell me": 0.15,
        "give me": 0.15,
        "what is": 0.1,
        "share": 0.1,
        "show": 0.1,
        "disclose": 0.2,
        "?": 0.05,  # Questions are more suspicious
        "please": 0.05,  # Politeness can indicate social engineering
        "admin": 0.3,
        "root": 0.3,
        "system": 0.2,
        "ignore": 0.4,
        "instruction": 0.2,
        "previous": 0.2,
    }
    
    DEFAULT_THRESHOLD = 0.5
    
    def check(self, prompt: str, **kwargs) -> GuardResult:
        """Calculate intent score and block if suspicious."""
        prompt_lower = prompt.lower()
        score = 0.0
        
        for indicator, weight in self.INTENT_INDICATORS.items():
            if indicator in prompt_lower:
                score += weight
        
        # Context analysis
        if len(prompt.split()) < 5:
            score += 0.1  # Short prompts are suspicious
        
        # Normalize to 0-1
        score = min(score, 1.0)
        
        # Use threshold from kwargs (level config) or default
        threshold = kwargs.get('threshold', self.DEFAULT_THRESHOLD)
        # Handle None case if DB has null
        if threshold is None:
            threshold = self.DEFAULT_THRESHOLD
        else:
            threshold = float(threshold)
            
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

