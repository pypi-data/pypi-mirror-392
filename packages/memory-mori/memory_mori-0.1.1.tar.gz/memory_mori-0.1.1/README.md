# Memory Mori

**Persistent memory for LLMs** - Give your AI conversations long-term memory with intelligent context retrieval.

Memory Mori is a Python library that provides persistent, searchable memory for Large Language Models (LLMs). It remembers past conversations, user preferences, and important context, then intelligently retrieves relevant information when needed.

Perfect for building chatbots, AI assistants, and conversational agents that need to remember user interactions across sessions.

**Key capabilities:**
- 🧠 **Persistent Memory**: Store and retrieve conversation history across sessions
- 🔍 **Smart Retrieval**: Hybrid search combines semantic understanding with keyword matching
- 👤 **User Profiles**: Automatically learns and remembers user preferences, skills, and context
- ⏰ **Time Awareness**: Recent memories are prioritized, old ones fade naturally
- 🏷️ **Entity Tracking**: Remembers people, organizations, tools, and technologies mentioned
- 🚀 **Easy Integration**: Works with OpenAI, Claude, Ollama, and any LLM

## Features

### 🔍 Hybrid Search (Layer 1)
- **Semantic Search**: all-mpnet-base-v2 embeddings for meaning-based retrieval
- **Keyword Search**: BM25 algorithm for exact term matching
- **Optimized Weighting**: 80% semantic, 20% keyword (tuned for precision)
- **ChromaDB Backend**: Efficient vector storage and retrieval

### 🏷️ Entity Extraction (Layer 2)
- **Named Entity Recognition**: Using spaCy en_core_web_lg with custom tech patterns
- **50+ Tech Patterns**: Python, React, Docker, Kubernetes, GPT-4, etc.
- **5 Core Types**: PERSON, ORG, DATE, PRODUCT, EVENT
- **Entity Filtering**: Search within specific entity types

### 👤 Profile Learning (Layer 3)
- **SQLite Backend**: Persistent user profile storage
- **5 Categories**: role, preference, project, skill, context
- **Confidence-Based**: Higher confidence facts override lower ones
- **Auto-Extraction**: Profile facts learned from conversations

### ⏰ Time-Based Decay (Layer 4)
- **Exponential Decay**: score = base × e^(-λ × time)
- **Smart Aging**: Recent memories prioritized over old ones
- **Access Tracking**: Documents track created_at, last_accessed
- **Auto Cleanup**: Remove stale documents below threshold

### ✨ Recent Improvements
- **GPU Acceleration**: Automatic GPU detection and support (2-3x faster with CUDA)
- **Score Thresholding**: Filter low-confidence results (min_score=0.3)
- **Focused Results**: Default max_items=3 for higher precision
- **Custom Tech Patterns**: Better detection of programming languages, frameworks, tools

## Installation

```bash
# Install Memory Mori from PyPI
pip install memory-mori

# Download spaCy language model (required)
python -m spacy download en_core_web_lg
```

That's it! Memory Mori will automatically install all dependencies (ChromaDB, sentence-transformers, spaCy, etc.).

## Quick Start

```python
from memory_mori import MemoryMori, MemoryConfig

# Initialize with defaults (recommended)
mm = MemoryMori()

# Store information
mm.store("I'm working on a Python project using Django and PostgreSQL")
mm.store("Our deployment uses Docker containers on AWS")

# Retrieve relevant memories
results = mm.retrieve("Tell me about my tech stack")

for result in results:
    print(f"[{result.score:.2f}] {result.text}")

# Get formatted context for AI prompts
context = mm.get_context("What's my deployment setup?")
print(context)
```

## Configuration

```python
from memory_mori import MemoryConfig

# Custom configuration
config = MemoryConfig(
    alpha=0.8,                    # 80% semantic, 20% keyword
    lambda_decay=0.05,            # Slow decay rate
    entity_model="en_core_web_md", # Entity extraction model
    enable_entities=True,         # Enable entity extraction
    enable_profile=True,          # Enable profile learning
    device="auto"                 # Device: "auto", "cpu", or "cuda"
)

mm = MemoryMori(config)

# Or use presets
config = MemoryConfig.from_preset('standard')     # Balanced
config = MemoryConfig.from_preset('high_accuracy') # Uses larger model
config = MemoryConfig.from_preset('minimal')      # Lightweight
```

### GPU Acceleration

Memory Mori automatically detects and uses GPU when available for 2-3x performance improvement:

```python
# Auto-detect GPU (default)
config = MemoryConfig(device="auto")

# Force CPU usage
config = MemoryConfig(device="cpu")

# Force GPU usage (with CPU fallback)
config = MemoryConfig(device="cuda")
```

**Requirements for GPU:**
- NVIDIA GPU with CUDA support
- PyTorch with CUDA: `pip install torch --index-url https://download.pytorch.org/whl/cu118`

## API Reference

### MemoryMori

#### `store(text, metadata=None) -> str`
Store a memory.

```python
doc_id = mm.store(
    "Python is great for data science",
    metadata={"source": "conversation"}
)
```

#### `retrieve(query, filters=None, max_items=3, min_score=0.3) -> List[Memory]`
Retrieve relevant memories.

```python
# Basic retrieval
results = mm.retrieve("Python programming")

# With filters and thresholds
results = mm.retrieve(
    "web development",
    max_items=5,
    min_score=0.5,
    filters={"entity_type": "PRODUCT"}
)
```

#### `get_context(query, max_items=3, include_profile=True) -> str`
Get formatted context for LLM prompts.

```python
context = mm.get_context("What technologies do I use?")
# Returns formatted string with relevant memories and profile
```

#### `update_profile(facts: Dict)`
Manually update profile facts.

```python
mm.update_profile({
    "job_title": ("Software Engineer", "role", 0.9),
    "likes_coffee": ("true", "preference", 0.8)
})
```

#### `get_profile(category=None) -> Dict`
Get profile facts.

```python
profile = mm.get_profile()
# Or filter by category
preferences = mm.get_profile(category="preference")
```

#### `cleanup(threshold=0.01) -> int`
Clean up stale memories.

```python
removed_count = mm.cleanup(threshold=0.01)
```

## Examples

See the [examples/](examples/) folder for minimal integration examples:
- **[example_openai.py](examples/example_openai.py)** - OpenAI/GPT integration
- **[example_claude.py](examples/example_claude.py)** - Claude/Anthropic integration
- **[example_ollama.py](examples/example_ollama.py)** - Ollama/Local models integration

All examples are interactive and simple to run.

## Project Structure

```
memory_mori/
├── api.py                      # Main MemoryMori class
├── config.py                   # Configuration and data classes
├── core/
│   ├── search.py              # Hybrid search
│   ├── entities.py            # Entity extraction with tech patterns
│   ├── profile.py             # Profile management
│   ├── decay.py               # Time-based decay
│   └── device.py              # GPU/CPU device management
├── stores/
│   ├── vector_store.py        # ChromaDB wrapper
│   └── profile_store.py       # SQLite profile storage
├── examples/
│   ├── example_openai.py      # Minimal OpenAI integration
│   ├── example_claude.py      # Minimal Claude integration
│   └── example_ollama.py      # Minimal Ollama integration
├── tests/                      # Testing and benchmarking tools
└── utils/                      # Utility functions
```

## Performance

Based on benchmarks:

- **Storage**: ~19 docs/sec
- **Retrieval**: ~25ms per query (40 queries/sec)
- **Context Generation**: ~22ms per query


## Advanced Features

### Entity-Based Filtering

```python
# Only retrieve memories about products/tools
results = mm.retrieve(
    "programming tools",
    filters={"entity_type": "PRODUCT"}
)
```

### Score Thresholding

```python
# Only high-confidence results
results = mm.retrieve(query, min_score=0.6)

# All results (no threshold)
results = mm.retrieve(query, min_score=0.0)
```

### Profile-Enhanced Context

```python
# Get context with user profile
context = mm.get_context(query, include_profile=True)

# Without profile
context = mm.get_context(query, include_profile=False)
```

### Custom Decay Rates

```python
config = MemoryConfig(
    lambda_decay=0.01,      # Very slow decay
    decay_mode="combined"   # Use both creation and access time
)
```

## Use Cases

1. **Personal AI Assistant**: Remember user preferences, habits, and context
2. **Technical Support Bot**: Track user's tech stack and previous issues
3. **Learning Companion**: Remember what user has learned, provide progressive lessons
4. **Project Assistant**: Track project details, decisions, and progress
5. **Research Tool**: Store and retrieve research notes with smart ranking

## Requirements

- Python 3.8+
- chromadb
- sentence-transformers
- spacy (with en_core_web_md)
- rank_bm25
- openai (for OpenAI integration)

## Contributing

This is a personal project, but suggestions and feedback are welcome!

## License

MIT License

## Author

David Halvarson

---

**Note**: For production use, consider:
- Using environment variables for API keys
- Implementing proper error handling
- Adding logging
- Setting up proper data persistence paths
- Monitoring memory usage and performance
