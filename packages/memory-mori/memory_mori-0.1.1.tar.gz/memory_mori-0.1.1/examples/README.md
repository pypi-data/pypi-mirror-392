# Memory Mori Integration Examples

Minimal examples showing how to integrate Memory Mori with different LLM providers.

## Examples

### 1. OpenAI Integration (`example_openai.py`)

Integrate with OpenAI's GPT models.

**Setup:**
```bash
pip install openai
```

**Usage:**
```bash
# Edit the file to add your API key
python example_openai.py
```

**Key Features:**
- Uses `gpt-4o-mini` by default
- Automatic context retrieval
- Conversation storage
- ~50 lines of code

---

### 2. Claude Integration (`example_claude.py`)

Integrate with Anthropic's Claude models.

**Setup:**
```bash
pip install anthropic
```

**Usage:**
```bash
# Edit the file to add your API key
python example_claude.py
```

**Key Features:**
- Uses `claude-3-5-sonnet-20241022` by default
- System prompt with context
- Conversation storage
- ~50 lines of code

---

### 3. Ollama Integration (`example_ollama.py`)

Integrate with local Ollama models.

**Setup:**
```bash
# Install Ollama
# Visit: https://ollama.ai

# Start Ollama server
ollama serve

# Pull a model
ollama pull llama3.2
```

**Usage:**
```bash
# No API key needed - uses local models
python example_ollama.py
```

**Key Features:**
- Works with any Ollama model
- Completely local and private
- No API costs
- ~50 lines of code

**Supported Models:**
- `llama3.2` (default)
- `llama3.1`
- `mistral`
- `phi3`
- `gemma2`
- And more...

---

## Common Pattern

All examples follow the same pattern:

```python
# 1. Initialize Memory Mori
from api import MemoryMori
from config import MemoryConfig

config = MemoryConfig(
    collection_name="my_app",
    persist_directory="./my_data"
)
mm = MemoryMori(config)

# 2. Create chat function
def chat(user_message: str) -> str:
    # Get relevant context
    context = mm.get_context(user_message, max_items=3)

    # Build messages with context
    messages = [...]

    # Call LLM API
    response = api.call(messages)

    # Store conversation
    mm.store(f"User: {user_message}\nAssistant: {response}")

    return response

# 3. Use it
response = chat("What's my tech stack?")
```

## Memory Features Used

All examples demonstrate:

✅ **Context Retrieval** - Get relevant memories for each query
✅ **Conversation Storage** - Automatically save exchanges
✅ **Hybrid Search** - Semantic + keyword matching
✅ **Entity Extraction** - Extract important entities
✅ **Time Decay** - Recent memories prioritized

## Configuration Options

Customize Memory Mori for your use case:

```python
config = MemoryConfig(
    # Collection name (unique per app)
    collection_name="my_app",

    # Storage location
    persist_directory="./memory_data",

    # Search balance (0=keyword, 1=semantic)
    alpha=0.8,

    # Memory decay rate
    lambda_decay=0.05,

    # GPU acceleration
    device="auto",  # or "cpu" or "cuda"

    # Entity extraction
    enable_entities=True,
    entity_model="en_core_web_lg",

    # Profile learning
    enable_profile=True
)
```

## Extending the Examples

### Add Streaming

**OpenAI:**
```python
stream = client.chat.completions.create(
    model=model,
    messages=messages,
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

**Ollama:**
```python
response = requests.post(
    OLLAMA_API,
    json={"model": model, "messages": messages, "stream": True},
    stream=True
)

for line in response.iter_lines():
    if line:
        chunk = json.loads(line)
        print(chunk["message"]["content"], end="")
```

### Add Timing

```python
import time

start = time.time()
response = chat(user_message)
elapsed = time.time() - start

print(f"Response time: {elapsed:.2f}s")
```

### Add Error Handling

```python
def chat(user_message: str, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            # ... chat logic ...
            return response
        except Exception as e:
            if attempt == retries - 1:
                raise
            print(f"Retry {attempt + 1}/{retries}...")
            time.sleep(2 ** attempt)  # Exponential backoff
```

### Add Token Counting

**OpenAI:**
```python
response = client.chat.completions.create(...)
tokens = response.usage.total_tokens
print(f"Tokens used: {tokens}")
```

**Ollama:**
```python
# Install tiktoken
import tiktoken

encoder = tiktoken.encoding_for_model("gpt-4")
tokens = len(encoder.encode(user_message + response))
```

## API Keys

### OpenAI
Get your API key at: https://platform.openai.com/api-keys

```python
from openai import OpenAI
client = OpenAI(api_key="sk-...")
```

Or use environment variable:
```bash
export OPENAI_API_KEY="sk-..."
```
```python
client = OpenAI()  # Automatically reads from env
```

### Claude (Anthropic)
Get your API key at: https://console.anthropic.com/

```python
from anthropic import Anthropic
client = Anthropic(api_key="sk-ant-...")
```

Or use environment variable:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```
```python
client = Anthropic()  # Automatically reads from env
```

### Ollama
No API key needed - runs locally!

```bash
# Install
curl https://ollama.ai/install.sh | sh

# Start server
ollama serve

# Pull a model
ollama pull llama3.2
```

## Performance Comparison

| Provider | Speed | Cost | Privacy | Notes |
|----------|-------|------|---------|-------|
| OpenAI | Fast | $$ | Cloud | Best quality |
| Claude | Fast | $$$ | Cloud | Great reasoning |
| Ollama | Medium | Free | Local | Fully private |

## Troubleshooting

### OpenAI Issues

**Error: Invalid API key**
- Check your API key is valid
- Ensure you have credits

**Error: Rate limit**
- Wait a moment and retry
- Upgrade your plan

### Claude Issues

**Error: Invalid API key**
- Get key from https://console.anthropic.com/
- Check key format: `sk-ant-...`

**Error: Overloaded**
- Claude is experiencing high demand
- Retry after a few seconds

### Ollama Issues

**Error: Connection refused**
- Start Ollama: `ollama serve`
- Check it's running on port 11434

**Error: Model not found**
- Pull the model: `ollama pull llama3.2`
- List available: `ollama list`

**Slow responses**
- Use smaller model: `phi3` or `gemma2:2b`
- Check GPU is being used
- Reduce `max_tokens`

## Next Steps

1. **Try the examples** - Run each one to see how they work
2. **Customize** - Modify for your specific use case
3. **Add features** - Implement streaming, error handling, etc.
4. **Build your app** - Use these as templates for your project

## See Also

- [Main README](../README.md) - Full Memory Mori documentation
- [OpenAI Integration Guide](../OPENAI_INTEGRATION.md) - Detailed OpenAI guide
- [Timed Conversations](../TIMED_CONVERSATIONS.md) - Performance tracking
- [GPU Support](../GPU_SUPPORT.md) - GPU acceleration setup

---

**Questions?** Check the main documentation or create an issue on GitHub.
