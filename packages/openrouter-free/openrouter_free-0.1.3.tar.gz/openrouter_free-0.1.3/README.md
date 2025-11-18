# OpenRouter Free Client

A Python library for managing multiple free OpenRouter API keys with automatic rotation and seamless integration with LlamaIndex and LangChain.

## Features

- **Automatic Key Rotation**: Automatically switches between multiple API keys when rate limits are reached
- **Smart Rate Limit Handling**: Detects daily limits and seamlessly rotates to the next available key
- **Framework Integration**: Native support for LlamaIndex and LangChain
- **Comprehensive Logging**: Tracks key usage with masked key display for security
- **Async Support**: Full async/await support for high-performance applications
- **Error Handling**: Robust error handling with custom exceptions
- **Pre-configured Models**: Includes configurations for popular free models

## Supported Models

The library includes pre-configured free models from OpenRouter:

| Model Key | Full Model Name | Context Length | Max Output |
|-----------|----------------|----------------|------------|
| `gpt-oss-20b` | `openai/gpt-oss-20b:free` | 137,072 | 137,072 |
| `deepseek-chat-v3.1` | `deepseek/deepseek-chat-v3.1:free` | 163,800 | 163,800 |
| `deepseek-r1t2-chimera` | `tngtech/deepseek-r1t2-chimera:free` | 163,840 | 163,840 |


## Installation

### Basic Installation
```bash
pip install openrouter-free
```

### With LlamaIndex Support
```bash
pip install openrouter-free[llama-index]
```

### With LangChain Support
```bash
pip install openrouter-free[langchain]
```

### Full Installation (All Integrations)
```bash
pip install openrouter-free[all]
```

## Quick Start

### Basic Usage

```python
import asyncio
from openrouter_free import FreeOpenRouterClient, MODELS

# Initialize client with multiple API keys
client = FreeOpenRouterClient(
    model=MODELS["gpt-oss-20b"],
    api_keys=[
        "sk-or-v1-key1...",
        "sk-or-v1-key2...",
        "sk-or-v1-key3...",
    ]
)

# Async usage
async def main():
    response = await client.chat_completion(
        messages=[
            {"role": "user", "content": "Hello, how are you?"}
        ]
    )
    print(response.choices[0].message.content)

# Run async function
asyncio.run(main())
```

### Using Predefined Models

```python
from openrouter_free import FreeOpenRouterClient, MODELS

# Use predefined model configuration
client = FreeOpenRouterClient(
    model=MODELS["gpt-oss-20b"],
    api_keys=["key1", "key2", "key3"]
)
```

### Stream Responses

```python
async def stream_example():
    async for chunk in client.stream_chat_completion(
        messages=[{"role": "user", "content": "Tell me a story"}]
    ):
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="")
```

## LlamaIndex Integration

```python
from openrouter_free import LlamaORFAdapter, MODELS

# Create LlamaIndex-compatible LLM
llm = LlamaORFAdapter(
    model=MODELS["gpt-oss-20b"],
    api_keys=["key1", "key2", "key3"],
    temperature=0.7,
    max_tokens=2000
)

# Use with LlamaIndex
response = llm.chat([
    ChatMessage(role=MessageRole.USER, content="What is machine learning?")
])
print(response.message.content)

# Stream responses
for chunk in llm.stream_chat([
    ChatMessage(role=MessageRole.USER, content="Explain quantum computing")
]):
    print(chunk.delta, end="")
```

## LangChain Integration

```python
from openrouter_free import LangChainORFAdapter, MODELS
from langchain_core.messages import HumanMessage

# Create LangChain-compatible chat model
chat = LangChainORFAdapter(
    model=MODELS["gpt-oss-20b"],
    api_keys=["key1", "key2", "key3"],
    temperature=0.7
)

# Use with LangChain
messages = [HumanMessage(content="What is the capital of France?")]
response = chat.invoke(messages)
print(response.content)

# Stream responses
for chunk in chat.stream(messages):
    print(chunk.content, end="")
```

## Advanced Features

### Key Management

```python
# Add new key at runtime
client.add_key("sk-or-v1-newkey...")

# Remove a key
client.remove_key("sk-or-v1-oldkey...")

# Check available keys
print(f"Available keys: {client.available_keys_count}/{client.total_keys_count}")

# Reset all keys (mark as non-exhausted)
client.reset_keys()
```

### Custom Model Configuration

```python
from openrouter_free import ModelInfo, FreeOpenRouterClient

# Create custom model configuration
custom_model = ModelInfo(
    name="meta-llama/llama-3.2-90b-text-preview",
    context_length=131072,
    max_output_tokens=8192
)

client = FreeOpenRouterClient(
    model=custom_model,
    api_keys=["key1", "key2"]
)
```

### Error Handling

```python
from openrouter_free import AllKeysExhausted, InvalidKeyError, RateLimitError

try:
    response = await client.chat_completion(messages=[...])
except AllKeysExhausted:
    print("All API keys have reached their daily limits")
except InvalidKeyError:
    print("Invalid API key detected")
except RateLimitError:
    print("Rate limit exceeded")
```

### Logging Configuration

```python
from loguru import logger

# Loguru provides automatic configuration
# To enable debug level:
logger.enable("openrouter_free")
logger.add("debug.log", level="DEBUG")
```

## API Key Format

OpenRouter API keys should follow the format: `sk-or-v1-...`

You can get free API keys by:
1. Creating an account on [OpenRouter](https://openrouter.ai)
2. Adding credits or using free tier models
3. Generating API keys from your account settings

## Best Practices

1. **Multiple Keys**: Use at least 3-5 API keys for better reliability
2. **Error Handling**: Always implement proper error handling for production use
3. **Logging**: Enable logging to monitor key usage and rotation
4. **Async Operations**: Use async methods for better performance in production
5. **Key Security**: Never hardcode API keys; use environment variables

## Example: Complete Application

```python
import asyncio
import os
from openrouter_free import FreeOpenRouterClient, MODELS, AllKeysExhausted
from loguru import logger

# Setup is automatic with loguru

async def main():
    # Load keys from environment
    keys = [
        os.getenv("OPENROUTER_KEY_1"),
        os.getenv("OPENROUTER_KEY_2"),
        os.getenv("OPENROUTER_KEY_3"),
    ]
    
    # Initialize client
    client = FreeOpenRouterClient(
        model=MODELS["gpt-oss-20b"],
        api_keys=[k for k in keys if k],  # Filter out None values
        max_retries=3
    )
    
    try:
        # Simple chat
        response = await client.chat_completion(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is Python?"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        print(response.choices[0].message.content)
        
        # Check remaining keys
        print(f"Keys available: {client.available_keys_count}/{client.total_keys_count}")
        
    except AllKeysExhausted:
        print("All API keys exhausted. Please try again tomorrow.")

if __name__ == "__main__":
    asyncio.run(main())
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions, please use the [GitHub Issues](https://github.com/Mediano4e/openrouter-free-client/issues) page.

## Disclaimer

This library is not officially affiliated with OpenRouter. It's an independent project designed to help manage multiple free-tier API keys efficiently.