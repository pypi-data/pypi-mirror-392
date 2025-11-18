from .models import ModelInfo, MODELS
from .key_state import KeyState
from .client import FreeOpenRouterClient
from .exceptions import (
    AllKeysExhausted,
    InvalidKeyError,
    RateLimitError,
    OpenRouterError
)

try:
    from .adapters.llama_adapter import LlamaORFAdapter
except ImportError:
    LlamaORFAdapter = None

try:
    from .adapters.langchain_adapter import LangChainORFAdapter
except ImportError:
    LangChainORFAdapter = None

__version__ = "0.1.4"

__all__ = [
    "ModelInfo",
    "MODELS",
    "KeyState",
    "FreeOpenRouterClient",
    "LlamaORFAdapter",
    "LangChainORFAdapter",
    "AllKeysExhausted",
    "InvalidKeyError",
    "RateLimitError",
    "OpenRouterError",
]
