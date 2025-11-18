import asyncio

from typing import Any, Dict, List, Optional, Sequence, Generator

from loguru import logger

try:
    from llama_index.core.base.llms.base import BaseLLM
    from llama_index.core.base.llms.types import (
        ChatMessage,
        ChatResponse,
        ChatResponseGen,
        CompletionResponse,
        CompletionResponseGen,
        MessageRole,
        LLMMetadata,
    )
    from llama_index.core.callbacks import CallbackManager
    from llama_index.core.types import BaseOutputParser, PydanticProgramMode
    
    LLAMA_INDEX_AVAILABLE = True
except ImportError:
    LLAMA_INDEX_AVAILABLE = False
    BaseLLM = object

from ..client import FreeOpenRouterClient
from ..models import ModelInfo


def _message_to_dict(message: ChatMessage) -> Dict[str, str]:
    role_map = {
        MessageRole.SYSTEM: "system",
        MessageRole.USER: "user",
        MessageRole.ASSISTANT: "assistant",
        MessageRole.FUNCTION: "function",
    }
    
    return {
        "role": role_map.get(message.role, "user"),
        "content": message.content or "",
    }


class LlamaORFAdapter(BaseLLM):
    def __init__(
        self,
        model: str | ModelInfo,
        api_keys: List[str],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        callback_manager: Optional[CallbackManager] = None,
        **kwargs
    ):
        if not LLAMA_INDEX_AVAILABLE:
            raise ImportError(
                "LlamaIndex is not installed. "
                "Install it with: pip install llama-index-core"
            )
        
        self._client = FreeOpenRouterClient(model=model, api_keys=api_keys, **kwargs)
        self._model = self._client.model
        self._temperature = temperature
        self._max_tokens = max_tokens or self._model.max_output_tokens
        
        super().__init__(
            callback_manager=callback_manager or CallbackManager(),
        )
    
    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=self._model.context_length,
            num_output=self._max_tokens,
            model_name=self._model.openrouter_name,
            is_chat_model=True,
            is_function_calling_model=False,
        )
    
    @property
    def _model_kwargs(self) -> Dict[str, Any]:
        return {
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
        }
    
    def _run_sync(self, coro):
        """Run async coroutine synchronously with proper error handling."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if loop.is_running():
            # If we're already in an async context, use ThreadPoolExecutor
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        else:
            return loop.run_until_complete(coro)
    
    def chat(
        self,
        messages: Sequence[ChatMessage],
        **kwargs: Any
    ) -> ChatResponse:
        openai_messages = [_message_to_dict(msg) for msg in messages]
        
        completion_kwargs = {**self._model_kwargs, **kwargs}
        
        response = self._run_sync(
            self._client.chat_completion(
                messages=openai_messages,
                **completion_kwargs
            )
        )
        
        return ChatResponse(
            message=ChatMessage(
                role=MessageRole.ASSISTANT,
                content=response.choices[0].message.content or "",
            ),
            raw=response.model_dump(),
            delta=None,
        )
    
    def stream_chat(
        self,
        messages: Sequence[ChatMessage],
        **kwargs: Any
    ) -> ChatResponseGen:
        """Stream chat completion with proper chunk handling."""
        openai_messages = [_message_to_dict(msg) for msg in messages]
        
        completion_kwargs = {**self._model_kwargs, **kwargs}
        
        async def async_generator():
            content_buffer = ""
            async for chunk in self._client.stream_chat_completion(
                messages=openai_messages,
                **completion_kwargs
            ):
                if chunk.choices and chunk.choices[0].delta.content:
                    delta_content = chunk.choices[0].delta.content
                    content_buffer += delta_content
                    
                    yield ChatResponse(
                        message=ChatMessage(
                            role=MessageRole.ASSISTANT,
                            content=content_buffer,
                        ),
                        raw=chunk.model_dump(),
                        delta=delta_content,
                    )
        
        gen = async_generator()
        
        def sync_generator():
            try:
                while True:
                    chunk = self._run_sync(gen.__anext__())
                    yield chunk
            except StopAsyncIteration:
                return
        
        return sync_generator()
    
    async def achat(
        self,
        messages: Sequence[ChatMessage],
        **kwargs: Any
    ) -> ChatResponse:
        openai_messages = [_message_to_dict(msg) for msg in messages]
        
        completion_kwargs = {**self._model_kwargs, **kwargs}
        
        response = await self._client.chat_completion(
            messages=openai_messages,
            **completion_kwargs
        )
        
        return ChatResponse(
            message=ChatMessage(
                role=MessageRole.ASSISTANT,
                content=response.choices[0].message.content or "",
            ),
            raw=response.model_dump(),
            delta=None,
        )
    
    async def astream_chat(
        self,
        messages: Sequence[ChatMessage],
        **kwargs: Any
    ) -> ChatResponseGen:
        """Async stream chat completion with proper content accumulation."""
        openai_messages = [_message_to_dict(msg) for msg in messages]
        
        completion_kwargs = {**self._model_kwargs, **kwargs}
        
        content_buffer = ""
        async for chunk in self._client.stream_chat_completion(
            messages=openai_messages,
            **completion_kwargs
        ):
            if chunk.choices and chunk.choices[0].delta.content:
                delta_content = chunk.choices[0].delta.content
                content_buffer += delta_content
                
                yield ChatResponse(
                    message=ChatMessage(
                        role=MessageRole.ASSISTANT,
                        content=content_buffer,
                    ),
                    raw=chunk.model_dump(),
                    delta=delta_content,
                )
    
    def complete(
        self,
        prompt: str,
        formatted: bool = False,
        **kwargs: Any
    ) -> CompletionResponse:
        messages = [{"role": "user", "content": prompt}]
        
        completion_kwargs = {**self._model_kwargs, **kwargs}
        
        response = self._run_sync(
            self._client.chat_completion(
                messages=messages,
                **completion_kwargs
            )
        )
        
        return CompletionResponse(
            text=response.choices[0].message.content or "",
            raw=response.model_dump(),
            delta=None,
        )
    
    def stream_complete(
        self,
        prompt: str,
        formatted: bool = False,
        **kwargs: Any
    ) -> CompletionResponseGen:
        messages = [{"role": "user", "content": prompt}]
        
        completion_kwargs = {**self._model_kwargs, **kwargs}
        
        async def async_generator():
            async for chunk in self._client.stream_chat_completion(
                messages=messages,
                **completion_kwargs
            ):
                if chunk.choices and chunk.choices[0].delta.content:
                    yield CompletionResponse(
                        text=chunk.choices[0].delta.content,
                        raw=chunk.model_dump(),
                        delta=chunk.choices[0].delta.content,
                    )
        
        gen = async_generator()
        
        def sync_generator():
            try:
                while True:
                    chunk = self._run_sync(gen.__anext__())
                    yield chunk
            except StopAsyncIteration:
                return
        
        return sync_generator()
    
    async def acomplete(
        self,
        prompt: str,
        formatted: bool = False,
        **kwargs: Any
    ) -> CompletionResponse:
        messages = [{"role": "user", "content": prompt}]
        
        completion_kwargs = {**self._model_kwargs, **kwargs}
        
        response = await self._client.chat_completion(
            messages=messages,
            **completion_kwargs
        )
        
        return CompletionResponse(
            text=response.choices[0].message.content or "",
            raw=response.model_dump(),
            delta=None,
        )
    
    async def astream_complete(
        self,
        prompt: str,
        formatted: bool = False,
        **kwargs: Any
    ) -> CompletionResponseGen:
        messages = [{"role": "user", "content": prompt}]
        
        completion_kwargs = {**self._model_kwargs, **kwargs}
        
        async for chunk in self._client.stream_chat_completion(
            messages=messages,
            **completion_kwargs
        ):
            if chunk.choices and chunk.choices[0].delta.content:
                yield CompletionResponse(
                    text=chunk.choices[0].delta.content,
                    raw=chunk.model_dump(),
                    delta=chunk.choices[0].delta.content,
                )
    
    @property
    def available_keys(self) -> int:
        return self._client.available_keys_count
    
    def add_key(self, api_key: str):
        self._client.add_key(api_key)
    
    def remove_key(self, api_key: str) -> bool:
        return self._client.remove_key(api_key)
    
    def reset_keys(self):
        self._client.reset_keys()
