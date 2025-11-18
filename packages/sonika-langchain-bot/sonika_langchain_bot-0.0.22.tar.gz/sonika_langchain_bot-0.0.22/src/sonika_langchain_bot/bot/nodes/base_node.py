"""Clase base abstracta para todos los nodos."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging


class TokenUsage:
    """Tracking de tokens."""
    def __init__(self, prompt_tokens=0, completion_tokens=0, total_tokens=0):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens


class BaseNode(ABC):
    """Clase base para nodos del workflow."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        if logger is None:
            self.logger.addHandler(logging.NullHandler())
    
    @abstractmethod
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa el estado."""
        pass
    
    def _extract_token_usage(self, response) -> TokenUsage:
        """Extrae tokens de respuesta del LLM."""
        if hasattr(response, 'response_metadata'):
            token_data = response.response_metadata.get('token_usage', {})
            return TokenUsage(
                prompt_tokens=token_data.get('prompt_tokens', 0),
                completion_tokens=token_data.get('completion_tokens', 0),
                total_tokens=token_data.get('total_tokens', 0)
            )
        return TokenUsage()
    
    def _accumulate_tokens(self, state: Dict[str, Any], new_tokens: TokenUsage) -> None:
        """Acumula tokens en el estado."""
        state["token_usage"]["prompt_tokens"] += new_tokens.prompt_tokens
        state["token_usage"]["completion_tokens"] += new_tokens.completion_tokens
        state["token_usage"]["total_tokens"] += new_tokens.total_tokens