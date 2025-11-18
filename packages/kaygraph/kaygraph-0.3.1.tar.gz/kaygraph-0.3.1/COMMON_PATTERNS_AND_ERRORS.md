# Common Patterns and Errors in KayGraph

**Quick reference for avoiding common mistakes and following best practices.**

---

## Table of Contents

1. [Common Errors](#common-errors)
2. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
3. [Best Practices](#best-practices)
4. [Common Patterns](#common-patterns)
5. [Debugging Tips](#debugging-tips)
6. [For Coding Agents](#for-coding-agents)

---

## Common Errors

### ❌ Error 1: Accessing `shared` in `exec()`

**Problem:**
```python
class BadNode(Node):
    def exec(self, prep_res):
        # ❌ WRONG: Accessing shared in exec
        data = self.shared.get("something")
        return process(data)
```

**Why it's wrong:**
- `exec()` is meant to be a pure function that can be retried
- No access to `shared` makes retries safe and predictable

**✅ Fix:**
```python
class GoodNode(Node):
    def prep(self, shared):
        # Get everything you need here
        return {
            "data": shared.get("something"),
            "other": shared.get("other_thing")
        }

    def exec(self, prep_res):
        # Use only what prep() provided
        return process(prep_res["data"])
```

---

### ❌ Error 2: Forgetting to Return Action from `post()`

**Problem:**
```python
class BadDecisionNode(Node):
    def post(self, shared, prep_res, exec_res):
        shared["result"] = exec_res
        # ❌ WRONG: Forgot to return action for routing
```

**Why it's wrong:**
- When you have multiple paths (branching), you MUST return the action string
- None is only for default/end of pipeline

**✅ Fix:**
```python
class GoodDecisionNode(Node):
    def post(self, shared, prep_res, exec_res):
        shared["result"] = exec_res

        # Return explicit action for routing
        if exec_res["score"] > 0.8:
            return "approve"
        elif exec_res["score"] > 0.5:
            return "review"
        else:
            return "reject"

# In graph construction
decision >> ("approve", approve_node)
decision >> ("review", review_node)
decision >> ("reject", reject_node)
```

---

### ❌ Error 3: Not Making `exec()` Idempotent When Using Retries

**Problem:**
```python
class BadNode(Node):
    max_retries = 3

    def exec(self, prep_res):
        # ❌ WRONG: Side effects in retryable exec
        with open("counter.txt", "a") as f:
            f.write("1\n")  # This will run 3+ times!

        return call_flaky_api(prep_res)
```

**Why it's wrong:**
- If `exec()` fails and retries, side effects happen multiple times
- Data corruption, duplicate records, incorrect counts

**✅ Fix:**
```python
class GoodNode(Node):
    max_retries = 3

    def exec(self, prep_res):
        # Pure function - no side effects
        # Only returns a value
        return call_flaky_api(prep_res)

    def post(self, shared, prep_res, exec_res):
        # Side effects go here (only runs once)
        with open("counter.txt", "a") as f:
            f.write("1\n")

        shared["result"] = exec_res
        return None
```

---

### ❌ Error 4: Circular Imports

**Problem:**
```python
# nodes.py
from graph import my_graph  # ❌

class MyNode(Node):
    pass
```

```python
# graph.py
from nodes import MyNode  # ❌

my_graph = Graph(MyNode())
```

**Why it's wrong:**
- Python can't resolve circular imports
- Import error at runtime

**✅ Fix:**
```python
# nodes.py
class MyNode(Node):
    pass
```

```python
# graph.py
from nodes import MyNode

def create_graph():
    return Graph(MyNode())
```

---

### ❌ Error 5: Modifying Shared Store References

**Problem:**
```python
class BadNode(Node):
    def prep(self, shared):
        # Get list reference
        return shared.get("items", [])

    def exec(self, items):
        # ❌ WRONG: Modifying the original list!
        items.append("new_item")
        return items

    def post(self, shared, prep_res, exec_res):
        # This modifies the original shared["items"]!
        shared["items"] = exec_res
```

**Why it's wrong:**
- Mutating references breaks the prep/exec/post separation
- Hard to debug, unpredictable behavior

**✅ Fix:**
```python
class GoodNode(Node):
    def prep(self, shared):
        # Return a copy
        return shared.get("items", []).copy()

    def exec(self, items):
        # Work on the copy
        new_items = items + ["new_item"]
        return new_items

    def post(self, shared, prep_res, exec_res):
        # Update shared with new list
        shared["items"] = exec_res
```

---

## Anti-Patterns to Avoid

### ⚠️ Anti-Pattern 1: God Nodes

**Bad:**
```python
class DoEverythingNode(Node):
    """This node does EVERYTHING"""

    def exec(self, prep_res):
        # ❌ 500 lines of code doing 10 different things
        data = extract_data(prep_res)
        cleaned = clean_data(data)
        analyzed = analyze(cleaned)
        report = generate_report(analyzed)
        send_email(report)
        log_to_db(report)
        update_cache(report)
        # ... 300 more lines
        return report
```

**Good:**
```python
# Break into focused nodes
class ExtractNode(Node):
    def exec(self, prep_res):
        return extract_data(prep_res)

class CleanNode(Node):
    def exec(self, data):
        return clean_data(data)

class AnalyzeNode(Node):
    def exec(self, data):
        return analyze(data)

# Build a clear pipeline
extract >> clean >> analyze >> report >> notify
```

**Why:**
- Each node has one responsibility
- Easy to test, debug, and reuse
- Clear workflow visualization

---

### ⚠️ Anti-Pattern 2: Shared Store Soup

**Bad:**
```python
# Different nodes using inconsistent keys
class Node1(Node):
    def post(self, shared, prep_res, exec_res):
        shared["data"] = exec_res

class Node2(Node):
    def prep(self, shared):
        return shared.get("Data")  # ❌ Different case!

class Node3(Node):
    def prep(self, shared):
        return shared.get("user_data")  # ❌ Different key!
```

**Good:**
```python
# Use constants for keys
class SharedKeys:
    USER_DATA = "user_data"
    ANALYSIS_RESULT = "analysis_result"
    VALIDATION_STATUS = "validation_status"

class Node1(Node):
    def post(self, shared, prep_res, exec_res):
        shared[SharedKeys.USER_DATA] = exec_res

class Node2(Node):
    def prep(self, shared):
        return shared.get(SharedKeys.USER_DATA)
```

**Why:**
- Typo-proof
- Autocomplete works
- Easy to refactor

---

### ⚠️ Anti-Pattern 3: Storing Entire Objects

**Bad:**
```python
def prep(self, shared):
    # ❌ Storing huge objects in shared
    shared["entire_dataframe"] = pandas_df_10gb
    shared["full_model"] = huge_ml_model
```

**Good:**
```python
def prep(self, shared):
    # ✅ Store references or IDs
    shared["dataframe_path"] = "/tmp/data.parquet"
    shared["model_id"] = "model_v123"

    # Or store just what you need
    shared["summary_stats"] = {
        "row_count": len(df),
        "columns": list(df.columns)
    }
```

**Why:**
- Shared store should be lightweight
- Pass references, not copies
- Better performance, less memory

---

## Best Practices

### ✅ Pattern 1: Use Type Hints

```python
from typing import Dict, Any, List

class WellTypedNode(Node):
    def prep(self, shared: Dict[str, Any]) -> Dict[str, str]:
        """Prepare user data for validation."""
        return {
            "username": shared.get("username", ""),
            "email": shared.get("email", "")
        }

    def exec(self, prep_res: Dict[str, str]) -> Dict[str, bool]:
        """Validate user data."""
        return {
            "valid_username": len(prep_res["username"]) >= 3,
            "valid_email": "@" in prep_res["email"]
        }

    def post(
        self,
        shared: Dict[str, Any],
        prep_res: Dict[str, str],
        exec_res: Dict[str, bool]
    ) -> str:
        """Store validation results and route."""
        shared["validation"] = exec_res

        if all(exec_res.values()):
            return "valid"
        else:
            return "invalid"
```

**Why:**
- Clear contracts
- Better IDE support
- Catches errors early
- Self-documenting

---

### ✅ Pattern 2: Use Logging

```python
import logging

logger = logging.getLogger(__name__)

class WellLoggedNode(Node):
    def prep(self, shared):
        logger.debug(f"Preparing with shared keys: {list(shared.keys())}")
        user_id = shared.get("user_id")
        logger.info(f"Processing user: {user_id}")
        return user_id

    def exec(self, user_id):
        logger.info(f"Calling external API for user {user_id}")
        try:
            result = call_api(user_id)
            logger.info(f"API call successful: {len(result)} records")
            return result
        except Exception as e:
            logger.error(f"API call failed: {e}", exc_info=True)
            raise

    def post(self, shared, prep_res, exec_res):
        logger.debug(f"Storing {len(exec_res)} records")
        shared["records"] = exec_res
        logger.info("Processing complete")
        return None
```

**Why:**
- Easy debugging
- Production monitoring
- Audit trail
- Performance insights

---

### ✅ Pattern 3: Use Context Managers for Resources

```python
class DatabaseNode(Node):
    def __enter__(self):
        """Setup resources"""
        self.connection = create_db_connection()
        logger.info("Database connection opened")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup resources"""
        if hasattr(self, 'connection'):
            self.connection.close()
            logger.info("Database connection closed")

    def exec(self, prep_res):
        # Use self.connection safely
        return self.connection.query(prep_res["sql"])

# Usage
with Graph(DatabaseNode()) as graph:
    graph.run(shared)
# Connection auto-closed
```

**Why:**
- Guaranteed cleanup
- No resource leaks
- Exception-safe

---

### ✅ Pattern 4: Validation at Boundaries

```python
class ValidatedInputNode(ValidatedNode):
    def validate_prep(self, prep_res):
        """Validate before exec"""
        assert isinstance(prep_res, dict), "prep_res must be dict"
        assert "user_id" in prep_res, "Missing user_id"
        assert isinstance(prep_res["user_id"], str), "user_id must be string"
        return prep_res

    def validate_exec(self, exec_res):
        """Validate after exec"""
        assert isinstance(exec_res, dict), "exec_res must be dict"
        assert "status" in exec_res, "Missing status"
        assert exec_res["status"] in ["success", "failed"], "Invalid status"
        return exec_res
```

**Why:**
- Fail fast with clear errors
- Catch data issues early
- Production safety

---

## Common Patterns

### 🎯 Pattern: Conditional Branching

```python
# Decision node returns different actions
class RoutingNode(Node):
    def exec(self, data):
        return analyze(data)

    def post(self, shared, prep_res, exec_res):
        shared["analysis"] = exec_res

        # Route based on analysis
        if exec_res["confidence"] > 0.9:
            return "high_confidence"
        elif exec_res["confidence"] > 0.5:
            return "medium_confidence"
        else:
            return "low_confidence"

# Graph with branching
router >> ("high_confidence", auto_approve)
router >> ("medium_confidence", manual_review)
router >> ("low_confidence", reject)
```

---

### 🎯 Pattern: Loop-Back (Retry Logic)

```python
# Agent that loops until done
think >> analyze >> ("continue", tool)
analyze >> ("done", finish)
tool >> think  # Loop back

# Prevent infinite loops
class SafeThinkNode(Node):
    max_iterations = 10

    def post(self, shared, prep_res, exec_res):
        iterations = shared.get("iterations", 0) + 1
        shared["iterations"] = iterations

        if iterations >= self.max_iterations:
            logger.warning("Max iterations reached")
            return "done"

        if exec_res["needs_more_info"]:
            return "continue"
        else:
            return "done"
```

---

### 🎯 Pattern: Parallel Fan-Out + Gather

```python
from kaygraph import ParallelBatchNode

class FanOutNode(Node):
    def exec(self, items):
        # Return list of items to process
        return items

class ProcessNode(ParallelBatchNode):
    def exec(self, item):
        # Process each item in parallel
        return process_one(item)

class GatherNode(Node):
    def prep(self, shared):
        # Collect all results
        return shared.get("batch_results")

    def exec(self, results):
        # Aggregate
        return {"total": len(results), "summary": aggregate(results)}

# Graph
fan_out >> process_parallel >> gather
```

---

## Debugging Tips

### 🔍 Tip 1: Inspect Shared Store

```python
def post(self, shared, prep_res, exec_res):
    # Add this temporarily
    logger.debug(f"Shared store state: {json.dumps(shared, indent=2)}")
    shared["result"] = exec_res
    return None
```

### 🔍 Tip 2: Use `--` Operator for Graph Logging

```python
graph = Graph(start_node)
-- graph  # Logs graph structure
```

### 🔍 Tip 3: Check Node Execution Context

```python
def after_exec(self):
    ctx = self._execution_context
    logger.info(f"Execution took: {ctx['duration']:.2f}s")
    logger.info(f"Retries: {ctx.get('retry_count', 0)}")
```

### 🔍 Tip 4: Validate Incrementally

Start simple, add complexity:
```python
# Step 1: Just pass-through
class DebugNode(Node):
    def exec(self, prep_res):
        logger.info(f"Got: {prep_res}")
        return prep_res

# Step 2: Add real logic once working
class RealNode(Node):
    def exec(self, prep_res):
        logger.info(f"Processing: {prep_res}")
        result = complex_processing(prep_res)
        logger.info(f"Result: {result}")
        return result
```

---

## For Coding Agents

### 🤖 When Generating KayGraph Code:

1. **Always use 3-phase lifecycle**
   - `prep()` reads from shared
   - `exec()` is pure (no shared access)
   - `post()` writes to shared and returns action

2. **Always return action from `post()` when branching**
   - Return `None` only for default/end
   - Return string for named actions

3. **Always make `exec()` idempotent if `max_retries` > 0**
   - No side effects in `exec()`
   - Move side effects to `post()`

4. **Always use type hints**
   - Makes code self-documenting
   - Helps catch errors

5. **Always add logging**
   - At least INFO level for key operations
   - DEBUG level for detailed flow

6. **Always use constants for shared keys**
   - Prevents typos
   - Makes refactoring easier

### 🤖 Code Template for Coding Agents:

```python
from kaygraph import Node, Graph
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Constants for shared store keys
class Keys:
    INPUT = "input"
    OUTPUT = "output"
    STATUS = "status"

class MyNode(Node):
    """Clear docstring explaining what this node does."""

    def prep(self, shared: Dict[str, Any]) -> Any:
        """Phase 1: Read from shared store."""
        logger.debug(f"prep: shared keys = {list(shared.keys())}")
        data = shared.get(Keys.INPUT)
        logger.info(f"prep: processing {type(data)}")
        return data

    def exec(self, prep_res: Any) -> Any:
        """Phase 2: Execute logic (pure function)."""
        logger.info("exec: starting processing")
        result = process(prep_res)  # Your logic here
        logger.info(f"exec: result = {type(result)}")
        return result

    def post(
        self,
        shared: Dict[str, Any],
        prep_res: Any,
        exec_res: Any
    ) -> str | None:
        """Phase 3: Write to shared store and route."""
        logger.debug("post: storing results")
        shared[Keys.OUTPUT] = exec_res
        shared[Keys.STATUS] = "success"
        logger.info("post: complete")
        return None  # or "action_name" for routing

# Build graph
def create_graph():
    node1 = MyNode()
    # Add more nodes and connections
    return Graph(node1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    graph = create_graph()
    shared = {Keys.INPUT: "test data"}
    graph.run(shared)
    print(shared[Keys.OUTPUT])
```

---

## Summary Checklist

Before committing your KayGraph code, verify:

- [ ] `exec()` doesn't access `shared`
- [ ] `post()` returns action when branching
- [ ] `exec()` is idempotent if using retries
- [ ] Type hints on all methods
- [ ] Logging at key points
- [ ] Constants for shared keys
- [ ] Docstrings on nodes
- [ ] Resource cleanup in `__exit__` if needed
- [ ] Validation at boundaries
- [ ] No God Nodes (each node does one thing)

---

## 🔗 Related Documentation

- 📘 **[README.md](README.md)** - Main documentation and quickstart
- 🤖 **[LLM_CONTEXT_KAYGRAPH_DSL.md](LLM_CONTEXT_KAYGRAPH_DSL.md)** - Complete DSL reference for AI agents
- 📖 **[CLAUDE.md](CLAUDE.md)** - Development guide for Claude Code
- 📚 **[WORKBOOK_INDEX_CONSOLIDATED.md](workbooks/WORKBOOK_INDEX_CONSOLIDATED.md)** - All 70 examples
- 🎯 **[QUICK_FINDER.md](workbooks/QUICK_FINDER.md)** - Find examples by task
- 🧪 **[Workbook Testing Report](tasks/workbook-testing/TESTING_REPORT.md)** - Quality validation
