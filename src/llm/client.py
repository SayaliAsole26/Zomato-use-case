"""LLM client interface and Groq adapter."""

from __future__ import annotations

import logging
import time
from typing import Protocol

from groq import Groq
from groq.types.chat import ChatCompletion

try:
    from groq import AuthenticationError
except ImportError:
    AuthenticationError = Exception  # groq version compatibility

from src.config.settings import Settings, get_settings

logger = logging.getLogger(__name__)


class LLMClient(Protocol):
    """Protocol for LLM completion clients."""
    
    def complete(self, system: str, user: str) -> str:
        """Generate a completion from the LLM.
        
        Args:
            system: System message for the LLM
            user: User message for the LLM
            
        Returns:
            The LLM's response text
        """
        ...


class GroqClient:
    """Groq LLM client with retry logic."""
    
    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        temperature: float = 0.3,
        timeout: int = 30,
        max_retries: int = 2,
        settings: Settings | None = None,
    ) -> None:
        """Initialize Groq client.
        
        Args:
            api_key: Groq API key (from settings if None)
            model: Model name (from settings if None)
            temperature: Sampling temperature (0.0-1.0)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries on failure
            settings: Application settings (uses default if None)
        """
        settings = settings or get_settings()
        self.api_key = settings.groq_api_key if api_key is None else api_key
        self.model = model or settings.llm_model
        self.temperature = temperature
        self.timeout = timeout
        self.max_retries = max_retries
        self._max_attempts = max_retries + 1  # initial attempt + retries
        
        logger.info("GroqClient initializing with model=%s", self.model)
        logger.info("API key present: %s", bool(self.api_key))
        
        if not self.api_key:
            raise ValueError("Groq API key is required. Set GROQ_API_KEY environment variable.")
        
        self._client = Groq(api_key=self.api_key)
        logger.info("GroqClient initialized successfully")
    
    def complete(self, system: str, user: str) -> str:
        """Generate a completion from Groq with retry logic.
        
        Args:
            system: System message for the LLM
            user: User message for the LLM
            
        Returns:
            The LLM's response text
            
        Raises:
            RuntimeError: If all retries are exhausted
        """
        last_error: Exception | None = None

        for attempt in range(1, self._max_attempts + 1):
            try:
                logger.debug(
                    "Groq request attempt %d/%d: model=%s temperature=%s",
                    attempt,
                    self._max_attempts,
                    self.model,
                    self.temperature,
                )
                
                response: ChatCompletion = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=self.temperature,
                    timeout=self.timeout,
                )
                
                content = response.choices[0].message.content
                if not content:
                    raise RuntimeError("Groq returned empty response")
                
                logger.debug("Groq response received (length: %d)", len(content))
                return content
                
            except Exception as exc:
                last_error = exc
                if isinstance(exc, AuthenticationError) or "401" in str(exc):
                    raise ValueError(
                        "Groq rejected the API key (401). "
                        "Check GROQ_API_KEY in .env - create a new key at "
                        "https://console.groq.com/keys"
                    ) from exc
                logger.warning(
                    "Groq request failed (attempt %d/%d): %s",
                    attempt,
                    self._max_attempts,
                    exc,
                )
                if attempt < self._max_attempts:
                    # Exponential backoff
                    backoff = 2 ** attempt
                    logger.info("Retrying in %d seconds...", backoff)
                    time.sleep(backoff)
        
        raise RuntimeError(
            f"Failed to get Groq response after {self._max_attempts} attempts"
        ) from last_error
