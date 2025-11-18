from dataclasses import dataclass


@dataclass
class KeyState:
    key: str
    exhausted: bool = False
    invalid: bool = False
    
    def mask(self) -> str:
        if len(self.key) < 12:
            return "***"
        return f"{self.key[:6]}...{self.key[-6:]}"
