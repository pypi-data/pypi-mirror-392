# Claro Python SDK

Official Python SDK for **Claro**, part of [Bayt OS](https://baytos.ai) - The Collaborative Intelligence platform.

## 📚 Documentation

**Complete documentation is available at [docs.baytos.ai](https://docs.baytos.ai)**

## Quick Install

```bash
pip install baytos-claro
```

## Quick Example

```python
from baytos.claro import BaytClient
import os

# Initialize client
client = BaytClient(api_key=os.getenv("BAYT_API_KEY"))

# Get a prompt
prompt = client.get_prompt("@workspace/my-prompt:v1")

# Use it with your LLM
print(prompt.generator)
```

## Get Started

1. **[Get your API key](https://claro.baytos.ai)** from Claro
2. **[Read the quickstart](https://docs.baytos.ai/quickstart)** guide
3. **[Explore examples](https://docs.baytos.ai/examples/basic-usage)**

## Documentation Links

- **[Installation Guide](https://docs.baytos.ai/sdk/python/installation)** - Setup and requirements
- **[Quickstart](https://docs.baytos.ai/sdk/python/quickstart)** - Your first API call
- **[Working with Prompts](https://docs.baytos.ai/sdk/python/prompts)** - Core concepts
- **[API Reference](https://docs.baytos.ai/sdk/python/api-reference)** - Complete SDK reference
- **[Examples](https://docs.baytos.ai/examples/basic-usage)** - Production-ready code
- **[Error Handling](https://docs.baytos.ai/sdk/python/error-handling)** - Robust patterns
- **[Advanced Features](https://docs.baytos.ai/sdk/python/advanced)** - Performance optimization

## Support

- **Documentation:** [docs.baytos.ai](https://docs.baytos.ai)
- **Email:** [support@baytos.ai](mailto:support@baytos.ai)
- **Platform:** [claro.baytos.ai](https://claro.baytos.ai)

## License

Copyright © 2025 Bayt, Inc. All rights reserved.
