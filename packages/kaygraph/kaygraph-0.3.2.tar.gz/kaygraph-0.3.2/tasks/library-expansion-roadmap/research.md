# Research: KayGraph Library Expansion Roadmap

## Task Overview
Plan and prioritize improvements/expansions for the KayGraph library based on 21 identified enhancement opportunities across 6 priority tiers.

## Current State Analysis

### Core Framework (kaygraph/__init__.py)
**Strengths:**
- Zero dependencies (pure Python stdlib)
- Clean 3-phase node lifecycle: prep → exec → post
- Multiple node types: Node, AsyncNode, BatchNode, ParallelBatchNode, ValidatedNode, MetricsNode
- Graph orchestration with action-based routing
- Thread-safe via node copying
- Built-in resilience: retries, fallbacks, error hooks
- 536 lines of well-structured code

**Limitations Found:**
1. **Conditional branching in YAML** (workflow_loader.py:153-192)
   - Current parser only supports `>>` sequential chains
   - Comment at line 159: "Connect with named action (future)"
   - Cannot express `node - "action" >> target` in declarative workflows

2. **Type safety** (kaygraph/__init__.py:8-12)
   - Generic types defined but not fully leveraged
   - No TypedDict patterns for shared store
   - Prep/exec return types not enforced

3. **Error context** (kaygraph/__init__.py:155-162)
   - Basic error logging exists
   - Missing structured error types
   - No error context preservation (shared state, params)

4. **Graph validation** (kaygraph/__init__.py:282-326)
   - Runtime validation only
   - No pre-flight checks for unreachable nodes
   - No cycle detection warnings

### Declarative Workflows (kaygraph/workflow_loader.py)
**Capabilities:**
- YAML/JSON workflow loading (optional PyYAML dependency)
- Node discovery via sys.modules
- Simple graph syntax parsing
- Export workflows back to YAML
- Validation utilities

**Gaps:**
- No conditional action syntax in parser
- No subgraph/composition support
- Limited to linear chains currently
- No parameter passing in YAML

### Documentation Structure
**Comprehensive docs found:**
- Fundamentals: node.md, graph.md, async.md, batch.md, parallel.md, communication.md
- Patterns: agent.md, rag.md, multi_agent.md, chat.md, tools.md, validation.md, streaming.md, state_machine.md
- Production: api.md, deployment.md, monitoring.md, metrics.md, validation.md
- Integrations: llm.md, embedding.md, vector.md, websearch.md, viz.md

**Missing:**
- Interactive tutorials/notebooks
- Video content
- Community recipes repository
- Migration guides

### Workbooks (71 Examples)
**Categories identified:**
- Core patterns: hello-world, workflow, batch, parallel-batch, nested-batch, async
- AI/ML: agent, multi-agent, rag, chat variants, structured-output, streaming
- Production: fault-tolerant, monitoring, tracing, fastapi integration, supervisor
- UI/UX: human-in-the-loop, streamlit, gradio, voice-chat
- Integrations: google-calendar, sql-scheduler, text2sql, tool-*, mcp

**Observation:** Excellent example coverage, but no indexing by use-case difficulty

### Testing Infrastructure (tests/)
Found tests for:
- test_graph_basic.py (225 lines) - comprehensive graph execution tests
- Async tests exist (pytest.ini configured with asyncio_mode)
- Coverage available (pytest-cov in dev dependencies)

**Gap:** No performance benchmarks, no integration test suite

### Scaffolding Tool (scripts/kaygraph_scaffold.py)
Generates boilerplate for patterns:
- node, async_node, batch_node, parallel_batch
- chat, agent, rag
- supervisor, validated_pipeline, metrics, workflow

**Potential:** Could be enhanced with plugin/custom pattern support

## Existing Patterns to Reuse

### 1. Optional Dependencies Pattern
```python
# workflow_loader.py:31-36
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
```
**Reuse for:** Plugin system, pre-built nodes library

### 2. Hook System Pattern
```python
# kaygraph/__init__.py:51-61
def before_prep(self, shared: T_Shared): pass
def after_exec(self, shared, prep_res, exec_res): pass
def on_error(self, shared, error: Exception) -> bool: return False
```
**Reuse for:** Plugin system, audit logging, cost tracking

### 3. Context Manager Pattern
```python
# kaygraph/__init__.py:63-79
def __enter__(self): self.setup_resources(); return self
def __exit__(self, exc_type, exc_val, exc_tb): self.cleanup_resources()
```
**Reuse for:** State persistence, distributed execution, connection pooling

### 4. Execution Context Pattern
```python
# kaygraph/__init__.py:29,43-49
self._execution_context: dict[str, Any] = {}
def get_context(self, key: str, default=None)
def set_context(self, key: str, value: Any)
```
**Reuse for:** Profiling, cost tracking, metrics collection

### 5. Copy-on-Execute Pattern
```python
# kaygraph/__init__.py:328,335
current_node = copy.copy(self.start_node)
current_node = copy.copy(self.get_next_node(...))
```
**Critical for:** Thread safety in all new features

### 6. Operator Overloading Pattern
```python
# kaygraph/__init__.py:180-186
def __rshift__(self, other): return self.next(other)
def __sub__(self, action: str): return _ConditionalTransition(self, action)
```
**Reuse for:** Enhanced DSL features

### 7. Metrics Collection Pattern
```python
# kaygraph/__init__.py:486-525
class MetricsNode(Node):
    metrics = {"execution_times": [], "retry_counts": [], ...}
    def get_stats(self) -> dict[str, Any]
```
**Reuse for:** Cost tracking, profiling, audit logging

### 8. Module Discovery Pattern
```python
# workflow_loader.py:83-150
def discover_node_class(node_type: str, search_modules):
    # Search sys.modules, try import patterns
```
**Reuse for:** Plugin discovery

## Technology Stack Analysis

### Current Dependencies
- **Core:** Python 3.11+ (stdlib only)
- **Dev:** pytest, pytest-asyncio, pytest-cov
- **Optional:** PyYAML (for declarative workflows)

### Potential Dependencies for New Features
**Visualization/Debugger:**
- FastAPI + websockets (real-time updates)
- graphviz or mermaid (graph rendering)
- plotly/altair (metrics visualization)

**Distributed Execution:**
- ray (first choice - pythonic, popular in ML)
- dask (alternative - pandas ecosystem)
- celery (enterprise, mature)
- redis (shared state backend)

**Caching:**
- diskcache (pure Python, simple)
- redis-py (enterprise scale)
- lmdb (high performance)

**Plugins/Integrations:**
- opentelemetry-api (tracing)
- prometheus-client (metrics)
- sentry-sdk (error tracking)

### Maintaining Zero-Dependency Philosophy
**Strategy:** Keep kaygraph core dependency-free, create optional packages:
- `kaygraph` - core framework (no deps)
- `kaygraph-viz` - visualization tools
- `kaygraph-distributed` - distributed execution
- `kaygraph-nodes` - pre-built node library
- `kaygraph-plugins` - plugin framework + common plugins

## Community & Ecosystem Research

### Similar Frameworks (for inspiration, not competition)
1. **LangGraph** (LangChain ecosystem)
   - Focus: LLM-specific workflows
   - Strength: LLM integrations, streaming
   - Weakness: Heavy dependencies, opinionated

2. **Prefect/Airflow**
   - Focus: Data pipelines
   - Strength: Mature, enterprise features
   - Weakness: Complex setup, not AI-native

3. **Temporal**
   - Focus: Durable execution
   - Strength: State persistence, reliability
   - Weakness: Requires server infrastructure

**KayGraph's Unique Position:**
- Zero dependencies core
- AI-native but not AI-locked
- Simple enough for beginners, powerful for production
- Python-native (no DSL to learn)

### Target User Personas
1. **AI Engineers** - Building agents, RAG, chat systems
2. **Data Scientists** - Batch processing, pipelines
3. **Backend Engineers** - Workflow orchestration, automation
4. **Researchers** - Experimentation, rapid prototyping

## Internet Research Notes

### Popular Workflow Patterns (2024-2025)
- **ReAct/TAR** - Think-Act-Reflect loops (already have examples)
- **Multi-agent collaboration** - Supervisor-worker, debate patterns
- **Streaming UX** - Real-time token streaming for LLMs
- **Human-in-loop** - Approval workflows, feedback loops
- **RAG evolution** - Agentic RAG, GraphRAG, hybrid search

### Developer Experience Trends
- **Type safety** - Python typing becoming standard
- **Observability** - OpenTelemetry adoption growing
- **Local-first** - Developers want to run everything locally
- **Fast feedback** - Hot reload, interactive debugging
- **AI-assisted coding** - Cursor rules, Claude integration

### Deployment Trends
- **Modal/Banana** - Serverless GPU inference
- **Railway/Fly.io** - Simple deployment
- **Kubernetes** - Still enterprise standard
- **Edge computing** - Cloudflare Workers, Vercel

## Key Findings Summary

### High-Impact, Low-Effort (Quick Wins)
1. **Enhanced error messages** - 1-2 days, huge DX improvement
2. **Graph validation** - 2-3 days, prevents common mistakes
3. **Conditional branching in YAML** - 3-5 days, completes declarative workflows
4. **Profiling utilities** - 2-3 days, helps performance optimization

### High-Impact, Medium-Effort
1. **Interactive visualizer** - 2-3 weeks, great for marketing + debugging
2. **Plugin system** - 2-3 weeks, enables ecosystem growth
3. **Type safety improvements** - 1-2 weeks, better IDE support
4. **State persistence** - 2-3 weeks, enables long-running workflows

### High-Impact, High-Effort
1. **Pre-built nodes library** - 1-2 months, requires many integrations
2. **Distributed execution** - 1-2 months, complex architecture
3. **Cloud deployment helpers** - 1-2 months, platform-specific

### Strategic Decisions Needed

**Question 1: Package Structure**
- Option A: Monorepo with optional packages (kaygraph-viz, kaygraph-nodes)
- Option B: Separate repos for each major component
- Option C: Core + community plugins repo
- **Recommendation:** Option A - easier to maintain, better DX

**Question 2: Visualization Approach**
- Option A: Web-based (FastAPI + React/Svelte)
- Option B: Terminal-based (Rich/Textual)
- Option C: Jupyter notebook widgets
- **Recommendation:** Start with C (easiest), add A later

**Question 3: Plugin Distribution**
- Option A: Builtin plugin registry (like WordPress)
- Option B: PyPI-based (each plugin is a package)
- Option C: GitHub-based (clone and import)
- **Recommendation:** Option B - leverages existing ecosystem

**Question 4: Backward Compatibility**
- Follow semantic versioning strictly
- Deprecation warnings for 1 major version
- Clear migration guides for breaking changes

## Recommended Phasing

### Phase 1: Foundation (v0.3.0) - 1-2 months
**Goal:** Improve core DX and complete existing features
1. Conditional branching in YAML
2. Enhanced error messages
3. Graph validation
4. Profiling utilities
5. Type safety improvements

### Phase 2: Ecosystem (v0.4.0) - 2-3 months
**Goal:** Enable community contributions and integrations
1. Plugin system architecture
2. Interactive visualizer (Jupyter widget)
3. Pre-built nodes library (Phase 1: 10-15 common nodes)
4. Documentation overhaul (interactive tutorials)

### Phase 3: Scale (v0.5.0) - 3-4 months
**Goal:** Production-grade features for scale
1. State persistence layer
2. Distributed execution (Ray integration)
3. Caching layer
4. Streaming support

### Phase 4: Enterprise (v1.0.0) - 4-6 months
**Goal:** Enterprise features and stability
1. Access control & permissions
2. Audit logging
3. Cloud deployment helpers
4. Cost tracking
5. Comprehensive security audit

## Next Steps for Planning Phase
1. Prioritize specific features for Phase 1 (v0.3.0)
2. Create detailed technical designs for each feature
3. Define API interfaces and backward compatibility strategy
4. Create sub-tasks for each feature
5. Estimate effort and dependencies
