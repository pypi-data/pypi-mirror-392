# PromptGuard 🛡️

**The Framework for Reliable LLM Orchestration**

PromptGuard is a Python library that brings production-grade reliability, type safety, and observability to LLM applications. Think of it as "Pydantic meets Circuit Breaker for AI" - reducing boilerplate by 80% while making your AI apps bulletproof.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

---

## 🎯 The Problem We Solve

Every AI engineer writes the same boilerplate:
- Manual retry logic with exponential backoff
- Model fallback chains when primary fails
- Response parsing with regex/string manipulation
- Token counting and cost tracking
- Response validation and error handling

**PromptGuard eliminates all of this.**

---

## ✨ Core Features

### 1. Smart Execution with Auto-Retry & Fallbacks
```python
from promptguard import PromptChain

chain = PromptChain(
    models=["anthropic/claude-3-5-sonnet", "openai/gpt-4o", "groq/llama-70b"],
    strategy="cascade",
    max_retries=3,
    retry_delay="exponential"
)

result = await chain.execute("Analyze this document...")
print(result.response)  # Guaranteed to succeed or raise clear error
```

### 2. Type-Safe Response Validation
```python
from pydantic import BaseModel, Field
from promptguard import PromptChain

class EvaluationResponse(BaseModel):
    evaluation: str = Field(description="Overall evaluation")
    score: int = Field(ge=0, le=100)
    reason: str

chain = PromptChain(
    models=["anthropic/claude-3-5-sonnet"],
    response_schema=EvaluationResponse,
    validation_mode="strict"
)

result = await chain.execute(prompt)
print(result.response.score)  # Type-safe!
```

### 3. Multi-Provider Support
```python
chain = PromptChain(
    models=[
        "anthropic/claude-3-5-sonnet",
        "openai/gpt-4o",
        "groq/llama-3-70b",
        "cohere/command-r-plus",
        "google/gemini-1.5-pro"
    ]
)
```

### 4. Automatic Token Tracking & Cost Estimation
```python
result = await chain.execute(prompt)

print(result.metadata.tokens_used)
print(result.metadata.estimated_cost)
print(result.metadata.model_used)
print(result.metadata.execution_time_ms)
```

### 5. Response Caching
```python
from promptguard import CacheBackend

chain = PromptChain(
    models=["anthropic/claude-3-5-sonnet"],
    cache=CacheBackend.memory(),  # or .redis() or .disk()
    cache_ttl=3600
)

result1 = await chain.execute("What is AI?", cache_key="ai_def_v1")
result2 = await chain.execute("What is AI?", cache_key="ai_def_v1")
assert result2.metadata.cached == True
```

### 6. Semantic Response Validation
```python
from promptguard import validators

chain = PromptChain(
    models=["anthropic/claude-3-5-sonnet"],
    validators=[
        validators.length_range(min_chars=100, max_chars=5000),
        validators.contains_keywords(["risk", "evaluation"]),
        validators.has_citations(required=True),
        validators.sentiment_check(allowed=["neutral", "positive"])
    ]
)
```

### 7. Streaming Support
```python
chain = PromptChain(models=["anthropic/claude-3-5-sonnet"])

async for chunk in chain.stream("Write a long essay..."):
    print(chunk.delta, end="", flush=True)
```

### 8. Batch Processing
```python
prompts = ["Evaluate doc 1...", "Evaluate doc 2...", ...]

results = await chain.batch_execute(
    prompts,
    max_concurrent=5,
    show_progress=True
)
```

---

## 📦 Installation

```bash
# Basic installation
pip install promptguard

# With all features
pip install promptguard[all]

# With specific features
pip install promptguard[cache]      # Redis caching
pip install promptguard[validation]  # Semantic validators
pip install promptguard[metrics]     # Prometheus metrics
```

---

## 🚀 Quick Start

```python
import asyncio
from promptguard import PromptChain, validators, CacheBackend
from pydantic import BaseModel

class Analysis(BaseModel):
    summary: str
    score: int
    recommendations: list[str]

async def main():
    chain = PromptChain(
        models=[
            "anthropic/claude-3-5-sonnet",
            "openai/gpt-4o",
            "groq/llama-70b"
        ],
        strategy="cascade",
        max_retries=3,
        response_schema=Analysis,
        validators=[
            validators.length_range(min_chars=100),
            validators.has_citations()
        ],
        cache=CacheBackend.memory(),
        cache_ttl=3600
    )
    
    result = await chain.execute(
        prompt="Analyze this document: ...",
        cache_key="analysis_v1"
    )
    
    print(f"Score: {result.response.score}")
    print(f"Cost: ${result.metadata.estimated_cost:.4f}")
    print(f"Time: {result.metadata.execution_time_ms:.0f}ms")

asyncio.run(main())
```
---

## 📚 Documentation

- [Getting Started](./docs/getting_started.md)
- [API Reference](./docs/api_reference.md)
- [Examples](./examples/)
- [Advanced Usage](./docs/advanced.md)
- [Contributing](./CONTRIBUTING.md)

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=promptguard --cov-report=html

# Run specific test file
pytest tests/unit/test_core.py -v
```

---

## 🔧 Configuration

### Environment Variables

```bash
# API Keys
export ANTHROPIC_API_KEY=sk-ant-...
export OPENAI_API_KEY=sk-...
export GROQ_API_KEY=gsk-...
export COHERE_API_KEY=...
export GOOGLE_API_KEY=...

# Redis
export REDIS_URL=redis://localhost:6379
```

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License - See [LICENSE](./LICENSE) file for details

---
