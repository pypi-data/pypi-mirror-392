import asyncio

from typing import Any, Dict, List, Optional, Iterator, AsyncIterator

from loguru import logger

try:
    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.messages import (
        BaseMessage,
        HumanMessage,
        AIMessage,
        SystemMessage,
        FunctionMessage,
        ChatMessage as LangChainChatMessage,
        AIMessageChunk,
    )
    from langchain_core.outputs import ChatResult, ChatGeneration, ChatGenerationChunk
    from langchain_core.callbacks import CallbackManagerForLLMRun, AsyncCallbackManagerForLLMRun
    from langchain_core.pydantic_v1 import Field, root_validator
    
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    BaseChatModel = object

from ..client import FreeOpenRouterClient
from ..models import ModelInfo


def _message_to_dict(message: BaseMessage) -> Dict[str, str]:
    if isinstance(message, SystemMessage):
        role = "system"
    elif isinstance(message, HumanMessage):
        role = "user"
    elif isinstance(message, AIMessage):
        role = "assistant"
    elif isinstance(message, FunctionMessage):
        role = "function"
    elif isinstance(message, LangChainChatMessage):
        role = message.role
    else:
        role = "user"
    
    return {
        "role": role,
        "content": message.content,
    }


class LangChainORFAdapter(BaseChatModel):
    client: Optional[FreeOpenRouterClient] = Field(default=None, exclude=True)
    model: str = Field(...)
    api_keys: List[str] = Field(...)
    temperature: float = Field(default=0.7)
    max_tokens: Optional[int] = Field(default=None)
    model_info: Optional[ModelInfo] = Field(default=None, exclude=True)
    
    class Config:
        arbitrary_types_allowed = True
    
    @root_validator(pre=True)
    def validate_environment(cls, values: Dict) -> Dict:
        if not LANGCHAIN_AVAILABLE:
            raise ImportError(
                "LangChain is not installed. "
                "Install it with: pip install langchain-core"
            )
        
        model = values.get("model")
        api_keys = values.get("api_keys")
        
        if not api_keys:
            raise ValueError("At least one API key must be provided")
        
        model_info = values.get("model_info")
        if not model_info:
            if isinstance(model, ModelInfo):
                model_info = model
            else:
                model_info = ModelInfo(model, 128000)
            values["model_info"] = model_info
        
        client = FreeOpenRouterClient(
            model=model_info,
            api_keys=api_keys,
        )
        values["client"] = client
        
        return values
    
    @property
    def _llm_type(self) -> str:
        return "openrouter-free"
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "available_keys": self.client.available_keys_count if self.client else 0,
        }
    
    def _run_sync(self, coro):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        else:
            return loop.run_until_complete(coro)
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        openai_messages = [_message_to_dict(msg) for msg in messages]
        
        generation_kwargs = {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **kwargs,
        }
        if stop:
            generation_kwargs["stop"] = stop
        
        response = self._run_sync(
            self.client.chat_completion(
                messages=openai_messages,
                **generation_kwargs
            )
        )
        
        message = AIMessage(
            content=response.choices[0].message.content or "",
            additional_kwargs={
                "model": response.model,
                "usage": response.usage.model_dump() if response.usage else {},
            }
        )
        
        generation = ChatGeneration(message=message)
        
        return ChatResult(
            generations=[generation],
            llm_output={
                "model": response.model,
                "usage": response.usage.model_dump() if response.usage else {},
            }
        )
    
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        openai_messages = [_message_to_dict(msg) for msg in messages]
        
        generation_kwargs = {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **kwargs,
        }
        if stop:
            generation_kwargs["stop"] = stop
        
        response = await self.client.chat_completion(
            messages=openai_messages,
            **generation_kwargs
        )
        
        message = AIMessage(
            content=response.choices[0].message.content or "",
            additional_kwargs={
                "model": response.model,
                "usage": response.usage.model_dump() if response.usage else {},
            }
        )
        
        generation = ChatGeneration(message=message)
        
        return ChatResult(
            generations=[generation],
            llm_output={
                "model": response.model,
                "usage": response.usage.model_dump() if response.usage else {},
            }
        )
    
    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        openai_messages = [_message_to_dict(msg) for msg in messages]
        
        generation_kwargs = {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **kwargs,
        }
        if stop:
            generation_kwargs["stop"] = stop
        
        async def async_generator():
            try:
                async for chunk in self.client.stream_chat_completion(
                    messages=openai_messages,
                    **generation_kwargs
                ):
                    if chunk.choices and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        message_chunk = AIMessageChunk(
                            content=content,
                            additional_kwargs={"model": chunk.model} if chunk.model else {}
                        )
                        
                        yield ChatGenerationChunk(message=message_chunk)
                        
                        if run_manager:
                            run_manager.on_llm_new_token(content)
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                raise
        
        gen = async_generator()
        
        try:
            while True:
                chunk = self._run_sync(gen.__anext__())
                yield chunk
        except StopAsyncIteration:
            return
        except Exception as e:
            logger.error(f"Sync streaming error: {e}")
            raise
    
    async def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        openai_messages = [_message_to_dict(msg) for msg in messages]
        
        generation_kwargs = {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **kwargs,
        }
        if stop:
            generation_kwargs["stop"] = stop
        
        try:
            async for chunk in self.client.stream_chat_completion(
                messages=openai_messages,
                **generation_kwargs
            ):
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    message_chunk = AIMessageChunk(
                        content=content,
                        additional_kwargs={"model": chunk.model} if chunk.model else {}
                    )
                    
                    yield ChatGenerationChunk(message=message_chunk)
                    
                    if run_manager:
                        await run_manager.on_llm_new_token(content)
        except Exception as e:
            logger.error(f"Async streaming error: {e}")
            raise
    
    @property
    def available_keys(self) -> int:
        return self.client.available_keys_count if self.client else 0
    
    def add_key(self, api_key: str):
        if self.client:
            self.client.add_key(api_key)
    
    def remove_key(self, api_key: str) -> bool:
        if self.client:
            return self.client.remove_key(api_key)
        return False
    
    def reset_keys(self):
        if self.client:
            self.client.reset_keys()
