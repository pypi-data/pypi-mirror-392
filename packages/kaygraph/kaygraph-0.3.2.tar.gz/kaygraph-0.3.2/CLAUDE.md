# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KayGraph is a **domain-specific language (DSL)** for expressing business problems as AI agent pipelines. The core abstraction is **Context Graph + Shared Store**, where Nodes handle operations (including LLM calls) and Graphs connect nodes through Actions (labeled edges) to create sophisticated workflows.

**Key Features:**
- **500-line DSL core** - pure Python standard library, zero dependencies
- **70 production-ready examples** across 16 organized categories
- Supports sync, async, batch, and parallel execution
- Built-in resilience with retries, fallbacks, and validation
- Thread-safe execution with node copying
- Optimized for **agentic coding** - humans design, AI agents implement

## Documentation Quick Reference

### For Humans
- 📘 **[README.md](README.md)** - Start here! Complete overview with 10-minute quickstart
- 📕 **[COMMON_PATTERNS_AND_ERRORS.md](COMMON_PATTERNS_AND_ERRORS.md)** - Avoid common mistakes (5 errors, 3 anti-patterns, 4 best practices)
- 🎯 **[workbooks/QUICK_FINDER.md](workbooks/QUICK_FINDER.md)** - Task-based navigation ("I need to build...")
- 📚 **[workbooks/WORKBOOK_INDEX_CONSOLIDATED.md](workbooks/WORKBOOK_INDEX_CONSOLIDATED.md)** - All 70 examples organized in 16 categories
- 🚀 **[workbooks/guides/LLM_SETUP.md](workbooks/guides/LLM_SETUP.md)** - Set up local LLMs with Ollama

### For AI Coding Agents
- 🤖 **[LLM_CONTEXT_KAYGRAPH_DSL.md](LLM_CONTEXT_KAYGRAPH_DSL.md)** - Complete DSL specification (load this first!)
- ⚠️ **[COMMON_PATTERNS_AND_ERRORS.md](COMMON_PATTERNS_AND_ERRORS.md)** - Common errors and how to avoid them
- 📝 **[workbooks/WORKBOOK_INDEX_CONSOLIDATED.md](workbooks/WORKBOOK_INDEX_CONSOLIDATED.md)** - All examples with descriptions

### Testing & Quality
- 🧪 **[tasks/workbook-testing/validate_all_workbooks.py](tasks/workbook-testing/validate_all_workbooks.py)** - Validate all 70 workbooks
- 📊 **[tasks/workbook-testing/TESTING_REPORT.md](tasks/workbook-testing/TESTING_REPORT.md)** - 100% pass rate achieved

## Development Commands

### Testing
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_graph_basic.py

# Run with verbose output
pytest -v tests/

# Run with coverage
pytest --cov=kaygraph tests/

# Run async tests
pytest tests/test_async.py -v
```

### Installation
```bash
# Install the framework
pip install kaygraph

# Or install from source for development
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"

# Using uv (recommended)
uv pip install kaygraph
```

### Linting and Code Quality
```bash
# Run ruff linter
ruff check kaygraph/

# Fix linting issues automatically
ruff check --fix kaygraph/

# Format code
ruff format kaygraph/
```

### Building and Publishing
```bash
# Build the package
python -m build

# Upload to PyPI (requires account setup)
python -m twine upload dist/*

# Version bumping (update kaygraph/__init__.py)
# Then tag and push:
git tag v0.0.1
git push origin v0.0.1
```

### Scaffolding New Projects
```bash
# Generate boilerplate code from production-tested patterns
python scripts/kaygraph_scaffold.py <pattern> <name>

# Examples:
python scripts/kaygraph_scaffold.py node DataProcessor
python scripts/kaygraph_scaffold.py chat CustomerSupport
python scripts/kaygraph_scaffold.py agent ResearchBot
python scripts/kaygraph_scaffold.py rag DocumentQA

# Available patterns:
# - node, async_node, batch_node, parallel_batch
# - chat, agent, rag
# - supervisor, validated_pipeline, metrics, workflow

# The scaffolding tool generates:
# - Complete working example with proper structure
# - Comprehensive documentation and TODOs
# - Requirements.txt with optional dependencies
# - README with quick start instructions
```

## Architecture & Key Components

### Core Framework (`/kaygraph/__init__.py`)
The framework provides these opinionated abstractions:

#### Base Classes
- **BaseNode**: Foundation with 3-step lifecycle: `prep()` → `exec()` → `post()`
  - Includes hooks: `before_prep()`, `after_exec()`, `on_error()`
  - Context manager support for resource management
  - Execution context storage per node
- **Node**: Standard node with retry and fallback capabilities
  - `max_retries` and `wait` parameters for resilience
  - `exec_fallback()` for graceful degradation
- **Graph**: Orchestrates node execution through Actions
  - Supports operator overloading: `>>` for default, `-` for named actions
  - Copy nodes before execution for thread safety

#### Specialized Nodes
- **BatchNode/Graph**: Process iterables of items
  - `prep()` returns iterable, `exec()` called per item
- **AsyncNode/Graph**: Asynchronous versions for I/O operations
  - Replace methods with `_async` versions
  - `run_async()` for standalone execution
- **ParallelBatchNode/Graph**: Concurrent execution using ThreadPoolExecutor
- **ValidatedNode**: Input/output validation with custom validators
- **MetricsNode**: Execution metrics collection
  - Tracks execution times, retry counts, success/error rates
  - `get_stats()` for comprehensive metrics

### Node Design Principles
1. **prep(shared)**: Read from shared store, prepare data for execution
   - Access shared context to gather required data
   - Return data needed for exec phase
   - Should be lightweight and fast
2. **exec(prep_res)**: Execute compute logic (LLM calls, APIs) - NO shared access
   - Pure function that processes prep_res
   - Can be retried independently
   - Should be idempotent when retries are enabled
3. **post(shared, prep_res, exec_res)**: Write to shared store, return next action
   - Update shared context with results
   - Return action string for next node or None for default
   - Nodes for conditional branching MUST return specific action strings

### Shared Store Design
- Use dictionary for simple systems: `shared = {"key": value}`
- Params are for identifiers, Shared Store is for data
- Don't repeat data - use references or foreign keys
- Thread-safe when used with proper node copying

## Available Examples (70 Total in 16 Categories)

The `workbooks/` directory contains comprehensive examples organized into logical categories. For complete details, see **[WORKBOOK_INDEX_CONSOLIDATED.md](workbooks/WORKBOOK_INDEX_CONSOLIDATED.md)**.

### Quick Navigation

**For task-based finding** ("I need to build..."): See **[QUICK_FINDER.md](workbooks/QUICK_FINDER.md)**

**16 Categories:**
1. **Getting Started** (1) - `01-getting-started/kaygraph-hello-world/`
2. **Core Patterns** (2) - `02-core-patterns/kaygraph-async-basics/`, `kaygraph-basic-communication/`
3. **Batch Processing** (5) - `03-batch-processing/kaygraph-batch/`, `kaygraph-parallel-batch/`, etc.
4. **AI Agents** (9) - `04-ai-agents/kaygraph-agent/`, `kaygraph-multi-agent/`, `kaygraph-agent-tools/`, etc.
5. **Workflows** (12) - `05-workflows/kaygraph-workflow/`, `kaygraph-fault-tolerant-workflow/`, etc.
6. **AI Reasoning** (4) - `06-ai-reasoning/kaygraph-thinking/`, `kaygraph-think-act-reflect/`, etc.
7. **Chat & Conversation** (4) - `07-chat-conversation/kaygraph-chat/`, `kaygraph-chat-memory/`, etc.
8. **Memory Systems** (3) - `08-memory-systems/kaygraph-memory-persistent/`, etc.
9. **RAG & Retrieval** (1) - `09-rag-retrieval/kaygraph-rag/`
10. **Code Development** (2) - `10-code-development/kaygraph-code-generator/`, etc.
11. **Data & SQL** (4) - `11-data-sql/kaygraph-sql-scheduler/`, `kaygraph-text2sql/`, etc.
12. **Tools Integration** (7) - `12-tools-integration/kaygraph-tool-crawler/`, `kaygraph-google-calendar/`, etc.
13. **Production & Monitoring** (8) - `13-production-monitoring/kaygraph-production-ready-api/`, etc.
14. **UI/UX** (4) - `14-ui-ux/kaygraph-human-in-the-loop/`, `kaygraph-streamlit-fsm/`, etc.
15. **Streaming & Realtime** (2) - `15-streaming-realtime/kaygraph-streaming-llm/`, etc.
16. **Advanced Patterns** (2) - `16-advanced-patterns/kaygraph-distributed-mapreduce/`, `kaygraph-supervisor/`

### Most Common Starting Points

```bash
# 1. Absolute basics (5 minutes)
cd workbooks/01-getting-started/kaygraph-hello-world
python main.py

# 2. Simple workflow (10 minutes)
cd workbooks/05-workflows/kaygraph-workflow
python main.py

# 3. AI agent (15 minutes)
cd workbooks/04-ai-agents/kaygraph-agent
python main.py

# 4. Chat with memory (15 minutes)
cd workbooks/07-chat-conversation/kaygraph-chat-memory
python main.py

# 5. RAG system (20 minutes)
cd workbooks/09-rag-retrieval/kaygraph-rag
python main.py
```

## Implementation Guidelines

### Node Implementation
```python
class MyNode(Node):
    def prep(self, shared):
        # Read from shared store
        return shared.get("input_data")
    
    def exec(self, prep_res):
        # Process data (LLM calls, etc)
        # This should be idempotent if retries enabled
        return process_data(prep_res)
    
    def post(self, shared, prep_res, exec_res):
        # Write results to shared store
        shared["output_data"] = exec_res
        return "next_action"  # or None for "default"
```

### Graph Connection
```python
# Connect nodes with default action
node1 >> node2 >> node3

# Connect with named actions
node1 >> ("success", node2)
node1 >> ("error", error_handler)

# Complex branching
decision_node >> ("approve", approval_flow)
decision_node >> ("reject", rejection_handler)
decision_node >> ("escalate", manager_review)
```

### Utility Functions
- One file per external API (`utils/call_llm.py`, `utils/search_web.py`)
- Include `if __name__ == "__main__"` test in each utility
- Document input/output and necessity
- NO vendor lock-in - implement your own wrappers

## Best Practices

1. **FAIL FAST**: Avoid try/except in initial implementation
2. **No Complex Features**: Keep it simple, avoid overengineering
3. **Extensive Logging**: Add logging throughout for debugging
4. **Separation of Concerns**: Data storage (shared) vs processing (nodes)
5. **Idempotent exec()**: Required when using retries
6. **Test Utilities**: Each utility should have a simple test
7. **Thread Safety**: Nodes are copied before execution
8. **Resource Cleanup**: Use context managers in nodes
9. **Validation First**: Use ValidatedNode for critical paths
10. **Metrics Always**: Add MetricsNode for production

## Common Patterns

### Agent Pattern
```python
# Decision-making with context and tools
think_node >> analyze_node >> ("use_tool", tool_node)
analyze_node >> ("respond", response_node)
tool_node >> think_node  # Loop back
```

### RAG Pattern
```python
# Offline indexing
extract >> chunk >> embed >> store

# Online retrieval
query >> search >> rerank >> generate
```

### Approval Workflow
```python
# Human-in-the-loop
process >> review >> ("approve", execute)
review >> ("reject", notify)
review >> ("modify", process)  # Loop back
```

### Fault-Tolerant Pipeline
```python
# With retries and fallbacks
class ResilientNode(Node):
    max_retries = 3
    wait = 1.0
    
    def exec_fallback(self, prep_res):
        return {"status": "degraded", "result": None}
```

## Project Structure Template
```
my_project/
├── main.py                  # Entry point
├── nodes/                   # Node definitions
│   ├── __init__.py
│   ├── processing.py        # Business logic nodes
│   ├── validation.py        # Input/output validation
│   └── integration.py       # External service nodes
├── graphs/                  # Graph definitions
│   ├── __init__.py
│   └── workflows.py         # Workflow orchestration
├── utils/                   # Utility functions
│   ├── __init__.py
│   ├── call_llm.py         # LLM integration
│   ├── database.py         # DB operations
│   └── monitoring.py       # Metrics/logging
├── tests/                   # Test suite
│   ├── test_nodes.py
│   ├── test_graphs.py
│   └── test_integration.py
├── docs/                    # Documentation
│   └── design.md           # High-level design
├── requirements.txt         # Dependencies
└── README.md               # Project documentation
```

## Debugging Tips

1. **Use Graph Logging**: Enable with `--` operator
   ```python
   graph = Graph()
   -- graph  # Logs graph structure
   ```

2. **Node Execution Context**: Access via `_execution_context`
   ```python
   def after_exec(self):
       logger.info(f"Execution took: {self._execution_context['duration']}s")
   ```

3. **Shared Store Inspection**: Log at each phase
   ```python
   def post(self, shared, prep_res, exec_res):
       logger.debug(f"Shared state: {shared.keys()}")
   ```

4. **Action Flow Tracing**: Log action decisions
   ```python
   def post(self, shared, prep_res, exec_res):
       action = "approve" if exec_res["score"] > 0.8 else "review"
       logger.info(f"Routing to action: {action}")
       return action
   ```

## Performance Optimization

1. **Use AsyncNode** for I/O-bound operations
2. **Use ParallelBatchNode** for CPU-bound batch processing
3. **Minimize shared store size** - use references not copies
4. **Profile with MetricsNode** to identify bottlenecks
5. **Cache expensive computations** in utility functions

## Security Considerations

1. **Never store secrets in shared store** - use environment variables
2. **Validate all external inputs** with ValidatedNode
3. **Sanitize data before logging** to prevent leaks
4. **Use timeout parameters** for external calls
5. **Implement rate limiting** for API calls

## Common Pitfalls to Avoid

**See [COMMON_PATTERNS_AND_ERRORS.md](COMMON_PATTERNS_AND_ERRORS.md) for detailed examples and fixes.**

1. **Modifying shared in exec()** - This breaks retry logic
2. **Not returning actions from conditional nodes** - Causes routing failures
3. **Non-idempotent exec() with retries** - Side effects run multiple times
4. **Circular dependencies in graphs** - Use careful action design
5. **Overcomplicating node design** - Keep nodes focused (avoid God Nodes)
6. **Ignoring thread safety** - Always let Graph copy nodes
7. **Forgetting cleanup** - Use context managers
8. **Not testing edge cases** - Test failures and timeouts
9. **Modifying shared store references** - Mutates original data
10. **Inconsistent shared keys** - Use constants to avoid typos

## Version Management

Current version: 0.0.1

When updating:
1. Update version in `kaygraph/__init__.py`
2. Update CHANGELOG.md
3. Tag release: `git tag v0.0.1`
4. Build: `python -m build`
5. Upload: `python -m twine upload dist/*`

## Important Notes

- The framework has ZERO dependencies - only Python standard library
- All utility functions (LLM calls, embeddings, etc.) must be implemented by you
- When humans can't specify the graph, AI agents can't automate it
- Node instances are copied before execution for thread safety
- Use `--` operator to log graph structure during development
- Conditional nodes must explicitly return action strings from `post()`
- Default transitions (>>) expect `post()` to return None
- This is an opinionated framework - embrace the patterns

## Getting Help

### Documentation
- 📘 **[README.md](README.md)** - Start here for complete overview
- 🤖 **[LLM_CONTEXT_KAYGRAPH_DSL.md](LLM_CONTEXT_KAYGRAPH_DSL.md)** - Complete DSL spec for AI agents
- ⚠️ **[COMMON_PATTERNS_AND_ERRORS.md](COMMON_PATTERNS_AND_ERRORS.md)** - Avoid common mistakes
- 🎯 **[workbooks/QUICK_FINDER.md](workbooks/QUICK_FINDER.md)** - Find examples by task
- 📚 **[workbooks/WORKBOOK_INDEX_CONSOLIDATED.md](workbooks/WORKBOOK_INDEX_CONSOLIDATED.md)** - All 70 examples

### Best Practices
- Review examples in `workbooks/` for patterns (organized in 16 categories)
- Check test files for usage examples
- Use logging extensively during development
- Keep nodes simple and focused (one responsibility per node)
- When in doubt, fail fast and log clearly
- Use type hints for better IDE support and error catching

## Claude Code Integration Guide

### When to Use KayGraph

Use KayGraph when users ask for:
- AI agents with decision making
- Multi-step workflows 
- RAG systems
- Chat with memory
- Batch processing
- Parallel operations

### Finding the Right Pattern

1. **Use QUICK_FINDER.md** for task-based navigation:
   - **[workbooks/QUICK_FINDER.md](workbooks/QUICK_FINDER.md)** - "I need to build X" → direct path
   - Examples organized by use case (agent, chatbot, RAG, workflow, etc.)

2. **Check workbooks/** for similar examples (new 16-category structure):
   - `04-ai-agents/kaygraph-agent/` - Decision-making agents
   - `07-chat-conversation/kaygraph-chat-memory/` - Conversational AI
   - `03-batch-processing/kaygraph-batch/` - Processing multiple items
   - `09-rag-retrieval/kaygraph-rag/` - Retrieval systems
   - `05-workflows/kaygraph-workflow/` - Multi-step pipelines

3. **Load the DSL specification** for AI agents:
   - **[LLM_CONTEXT_KAYGRAPH_DSL.md](LLM_CONTEXT_KAYGRAPH_DSL.md)** - Complete reference
   - **[COMMON_PATTERNS_AND_ERRORS.md](COMMON_PATTERNS_AND_ERRORS.md)** - Avoid mistakes

4. **Use the scaffolding tool** for quick starts:
   ```bash
   python scripts/kaygraph_scaffold.py agent MyAgent
   python scripts/kaygraph_scaffold.py rag DocumentQA
   python scripts/kaygraph_scaffold.py chat Assistant
   ```

5. **Start simple** - Chain first, add complexity later:
   ```python
   # Start with:
   node1 >> node2 >> node3

   # Then add branching:
   node2 >> ("error", error_handler)
   node2 >> ("success", next_node)
   ```

### Quick Reference

```python
# Node lifecycle (always this order)
class MyNode(Node):
    def prep(self, shared):      # 1. Read from shared
        return data
    def exec(self, prep_res):    # 2. Process (no shared!)
        return result
    def post(self, shared, prep_res, exec_res):  # 3. Write & route
        shared["result"] = exec_res
        return "next_action"  # or None for default

# Connections
node1 >> node2                    # Default path
node1 - "action" >> node2         # Named action
node1 >> node2 >> node3          # Chain

# Running
graph = Graph(start_node)
result = graph.run(shared)
```