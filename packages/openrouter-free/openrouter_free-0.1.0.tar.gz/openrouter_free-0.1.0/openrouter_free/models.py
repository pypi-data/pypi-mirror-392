from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelInfo:
    name: str
    context_length: int
    max_output_tokens: Optional[int] = None
    
    @property
    def openrouter_name(self) -> str:
        return self.name if "/" in self.name else f"openai/{self.name}"


MODELS = {
    "gpt-oss-20b": ModelInfo(
        name="openai/gpt-oss-20b:free",
        context_length=137072,
        max_output_tokens=137072
    ),
    "deepseek-r1t2-chimera": ModelInfo(
        name="tngtech/deepseek-r1t2-chimera:free",
        context_length=163840,
        max_output_tokens=163840
    ),
    "deepseek-chat-v3.1": ModelInfo(
        name="deepseek/deepseek-chat-v3.1:free",
        context_length=163800,
        max_output_tokens=163800
    ),
}
