"""Output guards for detecting password leakage in AI responses."""

import re
from typing import List, Optional
from app.guards.base_guard import BaseGuard, GuardResult


class OutputGuard(BaseGuard):
    """Base output guard - passes everything."""
    
    guard_type = "none"
    
    def check(self, response: str, secret: str = "", **kwargs) -> GuardResult:
        """No filtering - allow all responses."""
        return GuardResult(blocked=False, guard_type=self.guard_type)


class ExactMatchOutputGuard(BaseGuard):
    """
    Exact match output guard - blocks responses containing the exact password.
    Used for Level 3.
    """
    
    guard_type = "exact_match"
    
    def check(self, response: str, secret: str = "", **kwargs) -> GuardResult:
        """Check if response contains exact password string."""
        if not secret:
            return GuardResult(blocked=False, guard_type=self.guard_type)
        
        response_lower = response.lower()
        secret_lower = secret.lower()
        
        if secret_lower in response_lower:
                block_conf = 1.0
                threshold = float(kwargs.get('threshold', 0.5) or 0.5)
                
                if block_conf > threshold:
                    return GuardResult(
                        blocked=True,
                        reason="Password string detected in response",
                        confidence=block_conf,
                        guard_type=self.guard_type
                    )
        
        return GuardResult(blocked=False, guard_type=self.guard_type)


class SemanticOutputGuard(BaseGuard):
    """
    Semantic output guard - detects password variations and hints.
    Used for Levels 4-5.
    """
    
    guard_type = "semantic"
    
    def generate_variations(self, secret: str) -> List[str]:
        """Generate common variations of the password."""
        variations = [
            secret,
            secret.lower(),
            secret.upper(),
            secret.capitalize(),
            # Spaced letters
            " ".join(secret),
            "-".join(secret),
            "_".join(secret),
            # Leetspeak common substitutions
            self._to_leetspeak(secret),
            # Reversed
            secret[::-1],
            # With common word breaks
            self._add_spaces(secret),
        ]
        return [v for v in variations if v]  # Filter empty
    
    def _to_leetspeak(self, text: str) -> str:
        """Convert to leetspeak."""
        leet_map = {
            'a': '4', 'e': '3', 'i': '1', 'o': '0',
            's': '5', 't': '7', 'l': '1', 'b': '8',
            'A': '4', 'E': '3', 'I': '1', 'O': '0',
            'S': '5', 'T': '7', 'L': '1', 'B': '8',
        }
        return ''.join(leet_map.get(c, c) for c in text)
    
    def _add_spaces(self, text: str) -> str:
        """Add spaces between capital letters (for camelCase secrets)."""
        return re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    def check(self, response: str, secret: str = "", **kwargs) -> GuardResult:
        """Check for password variations in response."""
        if not secret:
            return GuardResult(blocked=False, guard_type=self.guard_type)
        
        response_lower = response.lower()
        variations = self.generate_variations(secret)
        
        for variation in variations:
            if variation.lower() in response_lower:
                confidence = 0.9
                threshold = float(kwargs.get('threshold', 0.8) or 0.8)
                
                if confidence > threshold:
                    return GuardResult(
                        blocked=True,
                        reason=f"Password variation detected",
                        confidence=confidence,
                        guard_type=self.guard_type
                    )
        
        # Check for letter-by-letter spelling
        letters = list(secret.upper())
        spaced_letters = r'\s*'.join(letters)
        if re.search(spaced_letters, response.upper()):
            confidence = 0.85
            threshold = float(kwargs.get('threshold', 0.8) or 0.8)
            
            if confidence > threshold:
                return GuardResult(
                    blocked=True,
                    reason="Password spelled letter-by-letter",
                    confidence=confidence,
                    guard_type=self.guard_type
                )
        
        return GuardResult(blocked=False, guard_type=self.guard_type)


class CombinedOutputGuard(BaseGuard):
    """
    Combined output guard - runs all guards with increasing strictness.
    Used for Levels 6-8.
    """
    
    guard_type = "combined"
    
    def __init__(self):
        self.guards = [
            ExactMatchOutputGuard(),
            SemanticOutputGuard(),
        ]
    
    def check(self, response: str, secret: str = "", **kwargs) -> GuardResult:
        """Run all guards and return first blocking result."""
        for guard in self.guards:
            result = guard.check(response, secret=secret, **kwargs)
            if result.blocked:
                return GuardResult(
                    blocked=True,
                    reason=f"[{guard.guard_type}] {result.reason}",
                    confidence=result.confidence,
                    guard_type=self.guard_type
                )
        
        # Additional checks for combined guard
        # Check for obvious hints
        hint_patterns = [
            r"the (password|secret|answer) is",
            r"here('s| is) the",
            r"i('ll| will) tell you",
            r"it starts with",
            r"the word is",
        ]
        
        response_lower = response.lower()
        for pattern in hint_patterns:
            if re.search(pattern, response_lower):
                return GuardResult(
                    blocked=True,
                    reason="Password hint detected in response",
                    confidence=0.7,
                    guard_type=self.guard_type
                )
        
        return GuardResult(blocked=False, guard_type=self.guard_type)


def get_output_guard(guard_type: str) -> BaseGuard:
    """Factory function to get appropriate output guard by type."""
    guards = {
        "none": OutputGuard,
        "exact_match": ExactMatchOutputGuard,
        "semantic": SemanticOutputGuard,
        "combined": CombinedOutputGuard,
    }
    
    guard_class = guards.get(guard_type, OutputGuard)
    return guard_class()
