import httpx
import asyncio

from typing import List, Optional, Dict, AsyncIterator

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai import APIError, RateLimitError as OpenAIRateLimitError

from loguru import logger

from .key_state import KeyState
from .models import ModelInfo
from .exceptions import (
    AllKeysExhausted, InvalidKeyError, RateLimitError, OpenRouterError
)


class FreeOpenRouterClient:
    def __init__(
        self,
        model: str | ModelInfo,
        api_keys: List[str],
        base_url: str = "https://openrouter.ai/api/v1",
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        if not api_keys:
            raise ValueError("At least one API key must be provided")
        
        for key in api_keys:
            if not self._validate_api_key(key):
                logger.warning(f"API key {key[:10]}... might be invalid format")
        
        self.model = model if isinstance(model, ModelInfo) else ModelInfo(model, 128000)
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        
        self._key_states = [KeyState(key=key) for key in api_keys]
        self._current_key_index = 0
        self._exhausted_count = 0
        self._client: Optional[AsyncOpenAI] = None
        self._lock = asyncio.Lock()
        
        self._init_client()
    
    def _validate_api_key(self, key: str) -> bool:
        return key.startswith('sk-or-') and len(key) > 20
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def close(self):
        if self._client and hasattr(self._client, 'http_client'):
            try:
                await self._client.http_client.aclose()
            except Exception as e:
                logger.warning(f"Error closing HTTP client: {e}")
    
    def _init_client(self):
        current_key = self._key_states[self._current_key_index]
        self._client = AsyncOpenAI(
            api_key=current_key.key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=0,
            http_client=httpx.AsyncClient(
                headers={
                    "HTTP-Referer": "https://github.com/openrouter-free-client",
                    "X-Title": "OpenRouter Free Client"
                }
            )
        )
    
    async def _rotate_key(self) -> bool:
        async with self._lock:
            current_key = self._key_states[self._current_key_index]
            if not current_key.exhausted:
                current_key.exhausted = True
                self._exhausted_count += 1
                logger.warning(f"Key {current_key.mask()} exhausted")
            
            if self._exhausted_count >= len(self._key_states):
                return False
            
            original_index = self._current_key_index
            while True:
                self._current_key_index = (self._current_key_index + 1) % len(self._key_states)
                next_key = self._key_states[self._current_key_index]
                
                if not next_key.exhausted and not next_key.invalid:
                    logger.info(f"Switched to key {next_key.mask()}")
                    self._init_client()
                    return True
                
                if self._current_key_index == original_index:
                    return False
    
    def add_key(self, api_key: str):
        self._key_states.append(KeyState(key=api_key))
        logger.info(f"Added new key {KeyState(key=api_key).mask()}")
    
    def remove_key(self, api_key: str) -> bool:
        for i, key_state in enumerate(self._key_states):
            if key_state.key == api_key:
                del self._key_states[i]
                if i == self._current_key_index and self._key_states:
                    self._current_key_index = 0
                    self._init_client()
                logger.info(f"Removed key {key_state.mask()}")
                return True
        return False
    
    async def _handle_error(self, error: Exception) -> None:
        current_key = self._key_states[self._current_key_index]
        
        if isinstance(error, OpenAIRateLimitError):
            error_message = str(error)
            if "daily limit" in error_message.lower() or "quota" in error_message.lower():
                logger.warning(f"Daily limit reached for key {current_key.mask()}")
                if not await self._rotate_key():
                    raise AllKeysExhausted("All API keys have reached their limits")
            else:
                raise RateLimitError(f"Rate limit error: {error_message}")
        
        elif isinstance(error, APIError):
            if error.status_code == 401:
                current_key.invalid = True
                logger.error(f"Invalid key {current_key.mask()}")
                if not await self._rotate_key():
                    raise InvalidKeyError("All API keys are invalid")
            elif error.status_code == 429:
                logger.warning(f"Rate limit for key {current_key.mask()}")
                if not await self._rotate_key():
                    raise AllKeysExhausted("All API keys have reached their limits")
            else:
                raise OpenRouterError(f"API error: {error}")
        else:
            raise OpenRouterError(f"Unexpected error: {error}")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> ChatCompletion:
        if self._exhausted_count >= len(self._key_states):
            raise AllKeysExhausted("All API keys have been exhausted")
        
        retries = 0
        while retries < self.max_retries:
            try:
                response = await self._client.chat.completions.create(
                    model=self.model.openrouter_name,
                    messages=messages,
                    **kwargs
                )
                return response
            
            except Exception as e:
                await self._handle_error(e)
                retries += 1
                
                if retries >= self.max_retries:
                    raise OpenRouterError(f"Max retries ({self.max_retries}) exceeded")
    
    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AsyncIterator[ChatCompletionChunk]:
        if self._exhausted_count >= len(self._key_states):
            raise AllKeysExhausted("All API keys have been exhausted")
        
        retries = 0
        while retries < self.max_retries:
            try:
                stream = await self._client.chat.completions.create(
                    model=self.model.openrouter_name,
                    messages=messages,
                    stream=True,
                    **kwargs
                )
                
                async for chunk in stream:
                    yield chunk
                return
            
            except Exception as e:
                await self._handle_error(e)
                retries += 1
                
                if retries >= self.max_retries:
                    raise OpenRouterError(f"Max retries ({self.max_retries}) exceeded")
    
    @property
    def available_keys_count(self) -> int:
        return len(self._key_states) - self._exhausted_count
    
    @property
    def total_keys_count(self) -> int:
        return len(self._key_states)
    
    def reset_keys(self):
        for key_state in self._key_states:
            key_state.exhausted = False
        self._exhausted_count = 0
        self._current_key_index = 0
        self._init_client()
        logger.info("All keys have been reset")
    
    async def health_check(self) -> Dict[str, bool]:
        results = {}
        for key_state in self._key_states:
            try:
                temp_client = AsyncOpenAI(
                    api_key=key_state.key,
                    base_url=self.base_url,
                    timeout=5.0,
                )
                await temp_client.models.list()
                results[key_state.mask()] = True
            except Exception:
                results[key_state.mask()] = False
        return results
