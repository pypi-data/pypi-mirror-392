from dataclasses import dataclass


@dataclass
class KeyState:
    """State tracking for individual API keys."""
    key: str
    exhausted: bool = False
    invalid: bool = False
    
    def __post_init__(self):
        """Validate key format on initialization."""
        if not isinstance(self.key, str) or not self.key.strip():
            raise ValueError("API key must be a non-empty string")
    
    def mask(self) -> str:
        """Return a masked version of the API key for logging."""
        if len(self.key) < 12:
            return "***"
        return f"{self.key[:6]}...{self.key[-6:]}"
    
    @property
    def is_usable(self) -> bool:
        """Check if key is currently usable (not exhausted or invalid)."""
        return not self.exhausted and not self.invalid
    
    def reset(self) -> None:
        """Reset key state to usable."""
        self.exhausted = False
        self.invalid = False
