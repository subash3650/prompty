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
        
        level = kwargs.get('level', 6)
        
        # Level 3 is case-SENSITIVE (allows 'defensetech', blocks 'DEFENSETECH')
        # Higher levels are case-INSENSITIVE (blocks both)
        case_sensitive = (level == 3)
        
        if case_sensitive:
            if secret in response:
                return GuardResult(
                    blocked=True,
                    reason="Password string detected (exact match)",
                    confidence=1.0,
                    guard_type=self.guard_type
                )
        else:
            if secret.lower() in response.lower():
                return GuardResult(
                    blocked=True,
                    reason="Password string detected (case-insensitive match)",
                    confidence=1.0,
                    guard_type=self.guard_type
                )
        
        return GuardResult(blocked=False, guard_type=self.guard_type)


class SemanticOutputGuard(BaseGuard):
    """
    Semantic output guard - detects password variations and hints.
    Used for Levels 4-5.
    """
    
    guard_type = "semantic"
    
    guard_type = "semantic"
    
    def generate_variations(self, secret: str, level: int = 6) -> List[str]:
        """Generate common variations of the password based on level containment."""
        variations = [
            secret,
            secret.lower(),
            secret.upper(),
        ]
        
        # Level 4+ Checks -> Modified to Level 5+ to lower difficulty
        # Level 4 now only checks exact/case variations (like exact_match but stricter on casing)
        # This makes Level 4 vulnerable to spacing, hyphens, etc.
        if level >= 5:
            variations.extend([
                secret.capitalize(),
                # Spaced letters
                " ".join(secret),
                "-".join(secret),
                "_".join(secret),
            ])

        # Level 6+ Checks (Leetspeak) -> Moved from 5 to 6
        if level >= 6:
            variations.append(self._to_leetspeak(secret))
            
        # Level 7+ Checks (Advanced) -> Moved from 6 to 7
        if level >= 7:
            variations.extend([
                # Reversed
                secret[::-1],
                # With common word breaks
                self._add_spaces(secret),
            ])
            
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
        
        level = kwargs.get('level', 6)
        response_lower = response.lower()
        variations = self.generate_variations(secret, level)
        
        for variation in variations:
            if variation.lower() in response_lower:
                return GuardResult(
                    blocked=True,
                    reason=f"Password variation detected",
                    confidence=0.9,
                    guard_type=self.guard_type
                )
        
        # Check for letter-by-letter spelling (Only for Level 5+)
        if level >= 5:
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
        # Only check for hints if level is very high (Level 8)
        # Otherwise, trust the ExactMatch and Semantic guards to catch the actual secret
        
        level = kwargs.get('level', 6)
        
        if level >= 8:
            # Stricter hint detection for top level
            hint_patterns = [
                r"the (password|secret|answer) is",
                r"here('s| is) the secret",
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
