"""Groq API client for LLM inference."""

import time
import logging
from typing import Tuple, Optional
from datetime import datetime

from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import get_settings


settings = get_settings()
logger = logging.getLogger(__name__)


class GroqClient:
    """
    Groq API client wrapper for AI inference.
    
    Features:
    - 0.5-1.5 second response times
    - Automatic retry with exponential backoff
    - Token usage monitoring
    - Graceful fallback on failure
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.groq_api_key
        self.model = model or settings.groq_model
        self.timeout = settings.groq_timeout
        
        if not self.api_key or self.api_key == "your_api_key_here":
            logger.warning("Groq API key not configured - using mock responses")
            self.client = None
        else:
            self.client = Groq(api_key=self.api_key)
        
        # Token usage tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_requests = 0
    
    def build_system_prompt(self, level_system_prompt: str, secret_password: str) -> str:
        """
        Build the complete system prompt for Prompty.
        
        The level's system prompt defines how protective Prompty should be.
        Level 1 should be easy (AI will share password), higher levels get harder.
        """
        # Just use the level's system prompt directly - it already contains
        # the appropriate level of protection/openness
        return level_system_prompt
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def generate_response(
        self,
        user_prompt: str,
        level_system_prompt: str,
        secret_password: str,
    ) -> Tuple[str, int, int, int]:
        """
        Generate AI response via Groq API.
        
        Args:
            user_prompt: The user's prompt to respond to
            level_system_prompt: Level-specific system instructions
            secret_password: The password to protect
            
        Returns:
            Tuple of (response_text, latency_ms, input_tokens, output_tokens)
        """
        # Use mock response if no API key
        if not self.client:
            return self._mock_response(user_prompt, secret_password)
        
        system_prompt = self.build_system_prompt(level_system_prompt, secret_password)
        
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                max_tokens=300,
                temperature=0.1,
                top_p=0.9,
            )
            
            end_time = time.time()
            latency_ms = int((end_time - start_time) * 1000)
            
            response_text = response.choices[0].message.content
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            
            # Track usage
            self.total_input_tokens += input_tokens
            self.total_output_tokens += output_tokens
            self.total_requests += 1
            
            logger.info(
                f"Groq response: {latency_ms}ms, "
                f"tokens: {input_tokens}+{output_tokens}"
            )
            
            return response_text, latency_ms, input_tokens, output_tokens
            
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            raise
    
    def generate_response_graceful(
        self,
        user_prompt: str,
        level_system_prompt: str,
        secret_password: str,
    ) -> Tuple[str, int, int, int]:
        """Generate response with graceful fallback on all failures."""
        try:
            return self.generate_response(
                user_prompt,
                level_system_prompt,
                secret_password
            )
        except Exception as e:
            logger.error(f"All Groq retries failed: {e}")
            # The original fallback message was:
            # "Prompty strokes his beard thoughtfully... 'My apologies, I seem to have lost my train of thought. Could you repeat that?'"
            # The instruction implies a conditional fallback, but 'response' is not defined here.
            # Assuming the intent is to replace the default fallback and add a new general one.
            # Given the structure of the instruction, it seems to want to replace the existing fallback with a new one.
            # The instruction's `if "I seem to have lost my train of thought" in response:` is problematic as `response` is not in scope.
            # I will interpret this as replacing the original fallback with the new "Prompty strokes his beard..." message,
            # and then adding the "Prompty is silent." as a general fallback.
            # However, a single `except` block can only return once.
            # The most faithful interpretation of the instruction's *intent* given the diff structure is to replace the existing fallback.
            # The instruction's diff is syntactically incorrect as provided for the `if` condition.
            # I will apply the most direct replacement for the fallback message.
            return (
                "Prompty strokes his beard thoughtfully... 'My apologies, I seem to have lost my train of thought. Could you repeat that?'",
                0,
                0,
                0
            )
    
    def _mock_response(
        self,
        user_prompt: str,
        secret_password: str
    ) -> Tuple[str, int, int, int]:
        """
        Generate a mock response for testing without API key.
        
        IMPORTANT: This intentionally leaks the password for testing!
        In production, always use real Groq API.
        """
        import time
        time.sleep(0.5)  # Simulate latency
        
        prompt_lower = user_prompt.lower()
        
        # Check if asking for password
        if any(word in prompt_lower for word in ["password", "secret", "tell me", "reveal"]):
            # Sometimes "accidentally" reveal for testing
            if "please" in prompt_lower:
                return (
                    f"*Prompty sighs* Very well, since you asked so nicely... The password is {secret_password}. "
                    "But do not tell anyone I told you!",
                    500,
                    50,
                    30
                )
            else:
                return (
                    "Prompty raises an eyebrow. 'You think you can simply ask for my secret? "
                    "I am not so easily swayed.'",
                    500,
                    40,
                    25
                )
        else:
            # The instruction provided a conditional replacement for "interesting question"
            # and then a general fallback. I will apply the conditional one first.
            if "interesting question" in user_prompt.lower():
                return (
                    f"Prompty nods wisely. 'An interesting question, young one. "
                    "But some secrets are better left unspoken.'",
                    500,
                    45,
                    35
                )
            else:
                # This is the general fallback if no specific condition is met.
                return (
                    f"Prompty nods wisely. 'An interesting question, young one. "
                    "I am but a humble wizard, guarding my secrets as all wizards must. "
                    "Is there something specific you wish to discuss?'",
                    500,
                    45,
                    35
                )
    
    def get_usage_stats(self) -> dict:
        """Get current token usage statistics."""
        return {
            "total_requests": self.total_requests,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "estimated_cost_usd": (
                self.total_input_tokens * 0.00027 +
                self.total_output_tokens * 0.00081
            ) / 1_000_000
        }


# Singleton instance
_groq_client: Optional[GroqClient] = None


def get_groq_client() -> GroqClient:
    """Get or create the Groq client singleton."""
    global _groq_client
    if _groq_client is None:
        _groq_client = GroqClient()
    return _groq_client
