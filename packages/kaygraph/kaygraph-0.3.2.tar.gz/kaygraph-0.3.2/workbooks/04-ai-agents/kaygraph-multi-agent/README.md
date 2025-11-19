# KayGraph Multi-Agent System

**Category**: 🟡 Requires Setup (LLM API Key Required)

This workbook demonstrates how to build a multi-agent system using KayGraph where specialized agents collaborate asynchronously to complete complex tasks using real LLM APIs.

## What it does

The multi-agent system features:
- **Supervisor Agent**: Coordinates and delegates tasks
- **Research Agent**: Gathers information and analysis
- **Writer Agent**: Creates content based on research
- **Reviewer Agent**: Reviews and improves output
- **Message Queue**: Asynchronous communication between agents
- **Shared Workspace**: Collaborative data sharing

## How to run

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your LLM API key (choose one):
   ```bash
   export OPENAI_API_KEY="sk-..."      # OpenAI
   export ANTHROPIC_API_KEY="sk-ant-..." # Anthropic Claude
   export GROQ_API_KEY="gsk_..."       # Groq (free tier available)
   ```

3. Run with a task:
```bash
python main.py "Write a blog post about renewable energy"
```

4. Run demo mode:
```bash
python main.py --demo
```

## How it works

### Architecture

```
┌─────────────────┐
│   Supervisor    │ ← Coordinates all agents
└────────┬────────┘
         │
    ┌────┴────┬──────────┬────────┐
    ↓         ↓          ↓        ↓
┌────────┐ ┌────────┐ ┌────────┐ Message
│Research│ │ Writer │ │Reviewer│  Queue
└────────┘ └────────┘ └────────┘    ↕
    ↓         ↓          ↓      Workspace
    └─────────┴──────────┘
         Shared Data
```

### Key Components

1. **MultiAgentCoordinator**:
   - Runs all agents concurrently
   - Manages iteration cycles
   - Monitors task completion

2. **Message Queue**:
   - Async message passing
   - Agent-to-agent communication
   - Task assignments and completions

3. **Shared Workspace**:
   - Common data storage
   - Research findings
   - Draft content
   - Review feedback

4. **Agent Lifecycle**:
   - Wait for messages
   - Process assignments
   - Execute tasks
   - Share results

### Execution Flow

1. **Initialization**: Task is provided to the system
2. **Planning**: Supervisor creates delegation plan
3. **Research Phase**: Researcher gathers information
4. **Writing Phase**: Writer creates content using research
5. **Review Phase**: Reviewer evaluates and improves
6. **Completion**: Final output is assembled

### Features from KayGraph

- **AsyncNode**: All agents run asynchronously
- **AsyncGraph**: Coordinates async execution
- **Self-looping**: Coordinator iterates until complete
- **Message passing**: Through shared state

## Agent Behaviors

### Supervisor Agent
- Analyzes the main task
- Creates delegation plan
- Monitors progress
- Triggers next phases

### Research Agent
- Receives research assignments
- Gathers relevant information
- Provides structured findings
- Shares via workspace

### Writer Agent
- Uses research findings
- Creates structured content
- Follows style guidelines
- Produces drafts

### Reviewer Agent
- Evaluates content quality
- Checks accuracy
- Suggests improvements
- Approves final version

## Customization

### Add New Agent Types

```python
class FactCheckerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="factchecker",
            capabilities="Verify facts and citations"
        )
    
    async def exec_async(self, prep_res):
        # Implement fact checking logic
        pass
```

### Custom Communication Patterns

1. **Broadcast**: Send to all agents
2. **Pipeline**: Sequential processing
3. **Voting**: Consensus mechanisms
4. **Hierarchical**: Multi-level supervision

### Enhanced Workspace

Add features like:
- Version control for drafts
- Conflict resolution
- Access control
- Audit trails

## Example Output

```
🤖 Multi-Agent System Starting
📋 Task: Write a blog post about AI safety
============================================================

🔄 Agents working...

Multi-Agent Task Completion Report
=====================================

Original Task: Write a blog post about AI safety

Agent Contributions:
-------------------

Supervisor Agent:
Created delegation plan for research, writing, and review phases

Researcher Agent:
Research Findings:
1. Key Facts:
   - AI safety focuses on ensuring AI systems are beneficial
   - Major concerns include alignment and control
   - Current research explores various safety approaches

Writer Agent:
[Title: Navigating the Future: AI Safety Essentials]
Introduction: As AI becomes more powerful...
[Full article content]

Reviewer Agent:
Review Assessment:
Overall Rating: Good (8/10)
Strengths: Well-researched, clear structure
Recommendations: APPROVE with minor edits

Task Status: Completed Successfully

✅ Multi-agent task completed
📊 Execution Statistics:
   - Total iterations: 7
   - Agents involved: supervisor, researcher, writer, reviewer
```

## Advanced Patterns

### 1. Parallel Research
Multiple research agents investigate different aspects simultaneously

### 2. Iterative Refinement
Writer and reviewer collaborate through multiple rounds

### 3. Specialized Teams
Groups of agents for different domains (technical, creative, analytical)

### 4. Dynamic Agent Creation
Supervisor spawns new agents based on task requirements

## Performance Considerations

1. **Async Execution**: Agents work concurrently
2. **Message Batching**: Process multiple messages per iteration
3. **Workspace Optimization**: Efficient data structures
4. **Iteration Limits**: Prevent infinite loops
5. **Resource Management**: Control agent concurrency

## Debugging Tips

- Enable detailed logging for message flow
- Monitor workspace state changes
- Track iteration counts
- Visualize agent interactions
- Add checkpoints for long tasks

## Production Considerations

- **Rate Limiting**: Add delays between agent calls if hitting API limits
- **Error Handling**: The framework handles retries automatically
- **Cost Management**: Monitor token usage across multiple agents
- **Response Quality**: Adjust temperature and prompts for better results
- **Logging**: All agent interactions are logged for debugging

---

# Advanced: Agent-to-Agent (A2A) Communication Patterns

This section demonstrates advanced communication patterns for building complex multi-agent systems with sophisticated message passing and coordination.

## Communication Patterns

### 1. Request-Response
Direct interaction between two agents:
```python
# Agent A requests help from Agent B
response = await agent_a.request(
    agent_b,
    "analyze_data",
    {"data": [1, 2, 3]},
    timeout=30
)
```

### 2. Publish-Subscribe
Topic-based message distribution:
```python
# Agent publishes to a topic
agent.publish("market_data", {
    "symbol": "AAPL",
    "price": 150.00
})

# Other agents subscribe
agent.subscribe("market_data", handle_market_update)
```

### 3. Broadcast
Send messages to all agents:
```python
agent.broadcast("system_alert", {
    "level": "warning",
    "message": "High memory usage"
})
```

### 4. Direct Messaging
Private agent-to-agent communication:
```python
agent.send_message("agent_b", {
    "type": "private_info",
    "content": "confidential data"
})
```

## Coordination Patterns

### 1. Task Distribution
Load balancing across multiple workers:
```python
# Coordinator distributes tasks among workers
tasks = split_workload(big_task)
for i, task in enumerate(tasks):
    worker = workers[i % len(workers)]
    coordinator.assign_task(worker, task)
```

### 2. Consensus Building
Democratic decision-making:
```python
# Agents vote on a decision
proposal = "increase_processing_capacity"
votes = await coordinator.collect_votes(proposal, timeout=60)
decision = majority_decision(votes)
```

### 3. Leader Election
Distributed leadership selection:
```python
# Agents elect a leader using Raft-like algorithm
if current_leader_timeout():
    candidate = agent.become_candidate()
    votes = await candidate.request_votes()
    if votes > num_agents // 2:
        agent.become_leader()
```

### 4. Hierarchical Delegation
Multi-level task breakdown:
```
CEO → Managers → TeamLeads → Workers
```

## Message Format

Standard message structure for agent communication:
```python
class Message:
    sender: str          # Agent ID
    recipient: str       # Agent ID or "broadcast"
    message_id: str      # Unique ID
    correlation_id: str  # For request-response
    timestamp: datetime
    type: str           # Message type
    payload: Dict       # Message content
    priority: int       # 0-10
    ttl: int           # Time to live
```

## Advanced Features

### Message Persistence
Store and replay messages:
```python
# Store important messages
message_store.save(message)

# Replay messages after restart
for msg in message_store.get_unprocessed():
    agent.handle_message(msg)
```

### Circuit Breaker
Prevent cascading failures:
```python
# Prevent cascading failures
if agent_b.failure_rate > 0.5:
    circuit_breaker.open()
    # Route to backup agent
    agent_c.handle_message(message)
```

### Load Balancing
Distribute work efficiently:
```python
# Distribute load among agents
least_loaded = min(workers, key=lambda w: w.current_load)
coordinator.assign_task(least_loaded, task)
```

### Message Routing
Smart routing based on capabilities:
```python
# Smart routing based on capabilities
router = MessageRouter()
router.add_rule("nlp_*", specialist_agents["nlp"])
router.add_rule("data_*", specialist_agents["data"])
```

## Monitoring & Debugging

### Message Tracing
Track message flow through the system:
```python
# Trace message flow
tracer.start_trace(message_id)
# ... message flows through agents
trace = tracer.get_trace(message_id)
print(trace.path)  # [agent_a, agent_b, agent_c]
```

### Performance Metrics
Monitor system health:
```python
metrics = {
    "messages_sent": counter,
    "messages_received": counter,
    "avg_response_time": histogram,
    "active_agents": gauge
}
```

## Best Practices for A2A Communication

1. **Message Design**: Keep messages small and focused
2. **Idempotency**: Ensure message handlers are idempotent
3. **Timeouts**: Always set reasonable timeouts
4. **Error Handling**: Implement proper retry and fallback
5. **Monitoring**: Track all agent communications
6. **Security**: Encrypt sensitive messages
7. **Testing**: Test agent failures and network partitions

---

*This advanced section shows patterns from `kaygraph-a2a-communication` merged into the multi-agent workbook for comprehensive coverage of agent coordination.*