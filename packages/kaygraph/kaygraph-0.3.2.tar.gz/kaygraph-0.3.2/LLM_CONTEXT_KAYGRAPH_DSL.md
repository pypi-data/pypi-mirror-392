# KayGraph DSL Reference - For LLMs

**Purpose:** The complete, authoritative guide for AI agents to build KayGraph workflows.
**Last Updated:** 2025-11-09
**Framework:** KayGraph v0.3.0
**Core:** 500 lines | Zero dependencies | Pure Python

---

## What is KayGraph?

KayGraph is a **domain-specific language (DSL)** for expressing business problems as agent pipelines using **functional programming** principles. It's building blocks for AI workflows.

**Philosophy:**
- Humans design workflows (the graph)
- AI agents implement them (the nodes)
- "If humans can't specify the graph, AI agents can't automate it"

---

## Core DSL: The 500-Line Foundation

### The 3-Phase Node Lifecycle

**EVERY node follows this pattern:**

```python
class MyNode(Node):
    def prep(self, shared: dict) -> Any:
        """
        Phase 1: READ from shared store
        - Gather data needed for execution
        - Access shared context
        - Return data for exec()
        """
        return shared.get("input_data")

    def exec(self, prep_res: Any) -> Any:
        """
        Phase 2: EXECUTE logic (NO shared access!)
        - Pure function: prep_res → result
        - Can be retried independently
        - Should be idempotent if retries enabled
        - LLM calls, APIs, processing happen here
        """
        return process_data(prep_res)

    def post(self, shared: dict, prep_res: Any, exec_res: Any) -> str | None:
        """
        Phase 3: WRITE to shared store, return next action
        - Update shared context with results
        - Return action string for branching OR None for default
        """
        shared["output_data"] = exec_res
        return None  # or "action_name" for conditional routing
```

**Why 3 phases?**
- `prep()` - Separates data gathering
- `exec()` - Pure, retryable logic
- `post()` - Separates side effects

---

## Graph Construction: Functional Composition

### Operator Overloading

```python
from kaygraph import Graph, Node

# Sequential flow (default action)
node1 >> node2 >> node3

# Named actions (conditional routing)
decision_node >> ("approve", approval_node)
decision_node >> ("reject", rejection_node)

# Alternative syntax
decision_node - "approve" >> approval_node
decision_node - "reject" >> rejection_node

# Create graph
graph = Graph(node1)
result = graph.run(shared={})
```

**Rules:**
- `>>` connects nodes with default action
- `-` creates named action transition
- Nodes are copied before execution (thread-safe)
- `post()` returns action name or None

---

## Node Types

### 1. BaseNode
Foundation for all nodes:
```python
from kaygraph import BaseNode

class MyNode(BaseNode):
    def prep(self, shared): return shared.get("x")
    def exec(self, prep_res): return prep_res * 2
    def post(self, shared, prep_res, exec_res):
        shared["result"] = exec_res
        return None
```

### 2. Node (with retries & fallbacks)
```python
from kaygraph import Node

class ResilientNode(Node):
    max_retries = 3
    wait = 1.0  # seconds between retries

    def exec(self, prep_res):
        # This can fail and will retry 3 times
        return unreliable_api_call(prep_res)

    def exec_fallback(self, prep_res):
        # Called if all retries fail
        return {"status": "degraded", "result": None}
```

### 3. AsyncNode
```python
from kaygraph import AsyncNode

class APINode(AsyncNode):
    async def exec_async(self, prep_res):
        # Async I/O operations
        return await fetch_data(prep_res)
```

### 4. BatchNode
```python
from kaygraph import BatchNode

class ProcessItems(BatchNode):
    def prep(self, shared):
        # Return iterable
        return shared["items"]

    def exec(self, item):  # Called per item!
        return process_single_item(item)

    def post(self, shared, prep_res, exec_res_list):
        shared["results"] = exec_res_list
```

### 5. ParallelBatchNode
```python
from kaygraph import ParallelBatchNode

class ParallelProcess(ParallelBatchNode):
    max_workers = 4

    def exec(self, item):
        # Executed in parallel (ThreadPoolExecutor)
        return expensive_operation(item)
```

### 6. ValidatedNode
```python
from kaygraph import ValidatedNode

class TypeSafeNode(ValidatedNode):
    def validate_input(self, prep_res) -> bool:
        return isinstance(prep_res, dict) and "key" in prep_res

    def validate_output(self, exec_res) -> bool:
        return isinstance(exec_res, str)
```

### 7. MetricsNode
```python
from kaygraph import MetricsNode

class MonitoredNode(MetricsNode):
    def exec(self, prep_res):
        # Metrics auto-collected: execution_times, retry_counts, etc.
        return do_work(prep_res)

# Later: node.get_stats()
```

---

## v0.3.0 Enhanced Features

### PersistentGraph (State Persistence)
```python
from kaygraph.persistence import PersistentGraph

graph = PersistentGraph(
    start_node,
    checkpoint_dir="./checkpoints"
)

# Auto-saves state at each node
graph.run(shared)

# Resume after crash
shared, node_id = graph.resume_from_checkpoint()
```

### SubGraphNode (Composition)
```python
from kaygraph.composition import SubGraphNode

# Encapsulate entire workflows
validation_workflow = Graph(validate_start)
validation_node = SubGraphNode(
    graph=validation_workflow,
    input_keys=["data", "rules"],  # Only pass these
    output_keys=["is_valid", "errors"]  # Only return these
)

# Use in larger workflow
main_flow = input_node >> validation_node >> process_node
```

### InteractiveGraph (Loops)
```python
from kaygraph.interactive import InteractiveGraph

graph = InteractiveGraph(start_node)

# Run until exit condition
graph.run_interactive(
    shared={},
    max_iterations=100,
    exit_key="_exit"
)

# In your node:
def post(self, shared, prep_res, exec_res):
    if should_stop:
        shared["_exit"] = True
    return None
```

### Agent Module (ReAct Pattern)
```python
from kaygraph.agent import create_react_agent, ToolRegistry

# Register tools
registry = ToolRegistry()
registry.register("search", search_function)
registry.register("calculate", calc_function)

# Create agent
agent = create_react_agent(
    tools=registry,
    model="gpt-4",
    max_iterations=10
)

# Run
result = agent.run({"task": "Find population of Tokyo"})
```

---

## Shared Store Design

### Rules
1. **Use dictionaries:** `shared = {"key": value}`
2. **Params for identifiers, Shared for data**
3. **Don't repeat data** - use references
4. **No complex objects** - keep it JSON-serializable

### Patterns
```python
# ✅ Good: Pass identifiers
shared = {
    "user_id": "user123",
    "order_id": "order456"
}

# ✅ Good: Store processed data
shared = {
    "user": {"name": "Alice", "email": "..."},
    "orders": [{...}, {...}]
}

# ❌ Bad: Duplicate large data
shared = {
    "raw_data": [...huge list...],
    "processed_data": [...same data transformed...],
    "analyzed_data": [...same data again...]
}

# ✅ Better: Store once, reference
shared = {
    "data": {...},
    "analysis_results": {"data_ref": "data", "insights": [...]}
}
```

---

## Common Patterns

### 1. Agent Pattern (ReAct)
```python
think_node >> analyze_node >> ("use_tool", tool_node)
analyze_node >> ("respond", response_node)
tool_node >> think_node  # Loop back
```

### 2. RAG Pattern
```python
# Offline indexing
extract >> chunk >> embed >> store

# Online retrieval
query >> search >> rerank >> generate
```

### 3. Approval Workflow
```python
process >> review >> ("approve", execute)
review >> ("reject", notify)
review >> ("modify", process)  # Loop
```

### 4. Fault-Tolerant Pipeline
```python
class ResilientNode(Node):
    max_retries = 3
    wait = 1.0

    def exec_fallback(self, prep_res):
        return {"status": "degraded"}
```

### 5. Multi-Agent System
```python
coordinator >> ("research", research_agent)
coordinator >> ("write", writer_agent)
coordinator >> ("review", reviewer_agent)
research_agent >> coordinator
writer_agent >> coordinator
reviewer_agent >> coordinator
```

---

## Declarative YAML Workflows

### Basic Syntax
```yaml
workflows:
  main:
    description: "Process documents"
    concepts:
      extract: ExtractorNode
      validate: ValidatorNode
      transform: TransformNode
    graph:
      extract >> validate >> transform
```

### With Conditional Routing
```python
# In Python (YAML parser supports >> only currently)
decision >> ("approve", node_a)
decision >> ("reject", node_b)
```

### Load and Run
```python
from kaygraph import load_workflow

workflow = load_workflow("workflow.kg.yaml")
result = workflow.run(shared={})
```

---

## LLM Integration Patterns

### 1. Simple LLM Call
```python
class LLMNode(Node):
    def prep(self, shared):
        return shared.get("prompt")

    def exec(self, prompt):
        return call_llm(prompt)  # Your implementation

    def post(self, shared, prep_res, exec_res):
        shared["llm_response"] = exec_res
        return None
```

### 2. Chain-of-Thought
```python
class ThinkNode(Node):
    def exec(self, problem):
        return call_llm(f"Think step by step: {problem}")

class ReasonNode(Node):
    def exec(self, thoughts):
        return call_llm(f"Based on: {thoughts}, conclude:")

# Chain them
think >> reason >> output
```

### 3. Tool-Using Agent
```python
class DecideNode(Node):
    def exec(self, task):
        return call_llm(f"To accomplish '{task}', should I use a tool? Yes/No and which?")

    def post(self, shared, prep_res, exec_res):
        if "search" in exec_res.lower():
            return "use_search"
        elif "calculate" in exec_res.lower():
            return "use_calculator"
        return "respond"

decide_node >> ("use_search", search_node)
decide_node >> ("use_calculator", calc_node)
decide_node >> ("respond", response_node)
```

---

## Error Handling

### Hooks
```python
class MyNode(Node):
    def before_prep(self, shared):
        # Called before prep
        pass

    def after_exec(self, shared, prep_res, exec_res):
        # Called after exec
        pass

    def on_error(self, shared, error) -> bool:
        # Called on error
        # Return True to suppress error, False to raise
        return False
```

### Context Managers
```python
class DatabaseNode(Node):
    def __enter__(self):
        self.conn = connect_to_db()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
```

---

## Anti-Patterns (AVOID)

### ❌ Modifying shared in exec()
```python
class BadNode(Node):
    def exec(self, prep_res):
        self.shared["data"] = "BAD"  # BREAKS RETRY LOGIC
        return prep_res
```

### ❌ Not returning actions from conditional nodes
```python
class BadDecisionNode(Node):
    def post(self, shared, prep_res, exec_res):
        # Must return action string!
        if exec_res == "approve":
            # ❌ Missing return
            pass
        # ✅ Should be:
        # return "approve"
```

### ❌ Circular dependencies without exit
```python
# ❌ Infinite loop
node_a >> node_b >> node_a  # No exit condition!

# ✅ Better
node_a >> node_b >> ("continue", node_a)
node_b >> ("complete", final_node)
```

---

## Quick Reference

### Imports
```python
from kaygraph import (
    Graph, Node, AsyncNode, BatchNode,
    ParallelBatchNode, ValidatedNode, MetricsNode
)
from kaygraph.persistence import PersistentGraph
from kaygraph.composition import SubGraphNode
from kaygraph.interactive import InteractiveGraph
from kaygraph.agent import create_react_agent, ToolRegistry
```

### Minimal Example
```python
from kaygraph import Graph, Node

class Step1(Node):
    def exec(self, _): return "Hello"
    def post(self, shared, _, res): shared["msg"] = res

class Step2(Node):
    def prep(self, shared): return shared["msg"]
    def exec(self, msg): return f"{msg}, World!"
    def post(self, shared, _, res): shared["final"] = res

# Build & run
graph = Graph(Step1("step1"))
Step1("step1") >> Step2("step2")
result = graph.run(shared={})
print(result["final"])  # "Hello, World!"
```

---

## Code Generation Guidelines for LLMs

### When Creating Nodes

1. **Always use 3-phase pattern:** prep → exec → post
2. **Keep exec() pure:** No shared access
3. **Return actions in post():** For conditional routing
4. **Use retries for unreliable ops:** Set `max_retries`
5. **Add node_id:** `Node("descriptive_id")`

### When Creating Graphs

1. **Start simple:** Linear flow first
2. **Add branching:** Use named actions
3. **Test incrementally:** One node at a time
4. **Log extensively:** Use Python logging
5. **Document actions:** Comment what each action means

### When Using LLMs

1. **One node = one LLM call:** Keep it focused
2. **Store prompts in constants:** Easy to modify
3. **Parse responses carefully:** LLMs can be inconsistent
4. **Add retries:** LLMs can fail
5. **Validate outputs:** Use ValidatedNode

---

## Complete Example Templates

### Template 1: Simple Agent
```python
from kaygraph import Graph, Node

class AnalyzeNode(Node):
    def prep(self, shared):
        return shared.get("task")

    def exec(self, task):
        # Call LLM
        return call_llm(f"Analyze: {task}")

    def post(self, shared, _, result):
        shared["analysis"] = result
        # Decide next action
        if "needs_tool" in result.lower():
            return "use_tool"
        return "complete"

class ToolNode(Node):
    def prep(self, shared):
        return shared["analysis"]

    def exec(self, analysis):
        # Execute tool based on analysis
        return execute_tool(analysis)

    def post(self, shared, _, result):
        shared["tool_result"] = result
        return "complete"

class OutputNode(Node):
    def prep(self, shared):
        return shared

    def exec(self, all_data):
        return format_output(all_data)

    def post(self, shared, _, result):
        shared["final_output"] = result

# Build graph
analyze = AnalyzeNode("analyze")
tool = ToolNode("tool")
output = OutputNode("output")

analyze >> ("use_tool", tool)
analyze >> ("complete", output)
tool >> output

graph = Graph(analyze)
result = graph.run({"task": "Find weather in Tokyo"})
```

### Template 2: RAG System
```python
# See workbooks/kaygraph-rag/ for full example

class QueryNode(Node):
    def prep(self, shared):
        return shared.get("question")

    def exec(self, question):
        # Generate embedding
        return embed_text(question)

    def post(self, shared, question, embedding):
        shared["query_embedding"] = embedding

class SearchNode(Node):
    def prep(self, shared):
        return shared["query_embedding"]

    def exec(self, embedding):
        # Vector search
        return search_vector_db(embedding)

    def post(self, shared, _, results):
        shared["search_results"] = results

class GenerateNode(Node):
    def prep(self, shared):
        return {
            "question": shared["question"],
            "context": shared["search_results"]
        }

    def exec(self, data):
        prompt = f"Question: {data['question']}\nContext: {data['context']}\nAnswer:"
        return call_llm(prompt)

    def post(self, shared, _, answer):
        shared["answer"] = answer

# Connect
query >> search >> generate
```

---

## Debugging Tips

1. **Log shared state:**
   ```python
   def post(self, shared, _, __):
       logger.info(f"Shared: {shared.keys()}")
   ```

2. **Use graph logging:**
   ```python
   -- graph  # Logs graph structure
   ```

3. **Check execution context:**
   ```python
   def after_exec(self, shared, prep_res, exec_res):
       logger.info(f"Duration: {self._execution_context['duration']}")
   ```

---

## Version-Specific Features

### v0.0.1 (Initial)
- Core abstractions (Node, Graph)
- Async support
- Batch processing
- Retries & fallbacks

### v0.2.0 (Nov 2025)
- Declarative workflows (YAML)
- Visual converter
- CLI tools
- Enhanced error messages

### v0.3.0 (Nov 2025)
- **PersistentGraph** - Checkpointing
- **SubGraphNode** - Composition
- **InteractiveGraph** - Loops
- **Agent Module** - ReAct patterns

---

## Summary for LLMs

**KayGraph = Functional DSL for Agent Pipelines**

**Core Concepts:**
1. **Nodes** = Functions (prep → exec → post)
2. **Graphs** = Function composition (>> operator)
3. **Shared** = Data flow (dictionary)
4. **Actions** = Routing (conditional branching)

**When to use:**
- Agent workflows
- RAG systems
- Multi-step pipelines
- Chat with memory
- Batch processing
- Any "business problem → agent pipeline" transformation

**Philosophy:**
- Simple core (500 lines)
- Zero dependencies
- Functional programming
- Fail fast
- Extensively logged

**70 Production Examples:** See `/workbooks/WORKBOOK_INDEX_CONSOLIDATED.md`

---

**This document is the complete reference. Any LLM with this context can build production KayGraph workflows.**

**Version:** 1.0
**Date:** 2025-11-09
**Framework:** KayGraph v0.3.0

---

## 🔗 Related Documentation

- 📘 **[README.md](README.md)** - Main documentation for humans
- ⚠️ **[COMMON_PATTERNS_AND_ERRORS.md](COMMON_PATTERNS_AND_ERRORS.md)** - Common mistakes and how to avoid them
- 📚 **[WORKBOOK_INDEX_CONSOLIDATED.md](workbooks/WORKBOOK_INDEX_CONSOLIDATED.md)** - All 70 examples
- 🎯 **[QUICK_FINDER.md](workbooks/QUICK_FINDER.md)** - Find examples by task
- 📖 **[CLAUDE.md](CLAUDE.md)** - Development guide for Claude Code
