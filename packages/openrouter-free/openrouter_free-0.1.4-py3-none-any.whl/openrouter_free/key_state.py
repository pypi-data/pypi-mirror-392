from dataclasses import dataclass


@dataclass
class KeyState:
    key: str
    exhausted: bool = False
    invalid: bool = False
    
    def __post_init__(self):
        if not isinstance(self.key, str) or not self.key.strip():
            raise ValueError("API key must be a non-empty string")
    
    def mask(self) -> str:
        if len(self.key) < 12:
            return "***"
        return f"{self.key[:6]}...{self.key[-6:]}"
    
    @property
    def is_usable(self) -> bool:
        return not self.exhausted and not self.invalid
    
    def reset(self) -> None:
        self.exhausted = False
        self.invalid = False
