# Central Config Example

This example demonstrates **KayGraph's Config system** for centralized configuration management.

## Problem

When building AI agent pipelines, you often need to:
- Share LLM parameters (model, temperature, max_tokens) across multiple nodes
- Manage prompt templates centrally
- Configure retry settings globally
- Switch configurations between dev/prod environments

**Without Config**, you'd hardcode these in each node or pass them manually.

## Solution

The `Config` class provides **centralized, hierarchical configuration** that:
- ✅ Propagates from Graph to all nodes automatically
- ✅ Supports node-level overrides
- ✅ Works with any configuration (prompts, LLM params, API keys, etc.)
- ✅ **100% backward compatible** - existing code works unchanged

## Features Demonstrated

1. **Graph-level config** - set once, used by all nodes
2. **Node-level overrides** - customize specific nodes
3. **Dynamic prompts** - template-based prompt generation
4. **LLM parameters** - centralized model/temperature settings
5. **Environment switching** - easy dev/prod config changes

## Quick Start

```bash
# Run the example
python main.py

# No dependencies required - uses mock LLM
```

## Key Concepts

### Creating Config

```python
from kaygraph import Config

config = Config(
    # LLM settings
    model="gpt-4o-mini",
    temperature=0.7,
    max_tokens=1000,

    # Prompts
    system_prompt="You are a helpful assistant",
    think_prompt="Analyze: {query}",

    # App settings
    retry_limit=3,
    timeout=30
)
```

### Using Config in Graphs

```python
# Pass to graph - automatically propagates to all nodes
graph = Graph(start_node, config=config)
```

### Accessing Config in Nodes

```python
class MyNode(Node):
    def exec(self, prep_res):
        # Access config with defaults
        model = self.config.get("model", "gpt-4o-mini")
        temp = self.config.get("temperature", 0.7)

        # Use prompt templates
        prompt_template = self.config.get("think_prompt", "Think about: {query}")
        prompt = prompt_template.format(query=prep_res)

        return call_llm(prompt, model=model, temperature=temp)
```

### Node-level Overrides

```python
# Most nodes use graph config
node1 = ThinkNode()  # Uses graph config

# But you can override specific nodes
node2 = ThinkNode(config=Config(temperature=0.3))  # Custom config
```

## When to Use Config

**Use Config when:**
- Building AI agent systems with multiple LLM calls
- Managing prompt templates centrally
- Need environment-specific settings (dev/prod)
- Want to experiment with different LLM parameters
- Building reusable node libraries

**Don't use Config when:**
- Simple single-node workflows
- All settings are hardcoded and never change
- Using node parameters is sufficient

## File Structure

```
kaygraph-central-config/
├── README.md          # This file
├── main.py            # Entry point with examples
├── nodes.py           # Config-aware nodes
└── config_profiles.py # Example config profiles (dev/prod)
```

## Related Examples

- **kaygraph-agent** - AI agent using config for prompts
- **kaygraph-workflow** - Workflow with centralized settings
- **kaygraph-chat** - Chat system with config-based prompts

## Implementation Notes

- Config is **completely optional** - nodes work without it
- Empty config (`Config()`) is created by default
- Graph propagates config only if node doesn't have its own
- All config methods return defensive copies
- Config can be serialized via `to_dict()` for persistence
