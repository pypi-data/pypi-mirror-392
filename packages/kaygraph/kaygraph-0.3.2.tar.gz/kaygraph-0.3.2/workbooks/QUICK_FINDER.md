# KayGraph Workbook Quick Finder

## 🎯 Find the Right Example Fast

### "I need to build..."

#### **An AI Agent**
- Simple agent with decisions → `04-ai-agents/kaygraph-agent/`
- Agent with memory → `04-ai-agents/kaygraph-agent-memory/`
- Agent with tools/functions → `04-ai-agents/kaygraph-agent-tools/`
- Multiple agents working together → `04-ai-agents/kaygraph-multi-agent/`
- Agent that learns from feedback → `04-ai-agents/kaygraph-agent-feedback/`

#### **A Chatbot**
- Basic chat → `07-chat-conversation/kaygraph-chat/`
- Chat with conversation memory → `07-chat-conversation/kaygraph-chat-memory/`
- Chat with safety guardrails → `07-chat-conversation/kaygraph-chat-guardrail/`
- Voice chat interface → `07-chat-conversation/kaygraph-voice-chat/`

#### **A RAG System**
- Complete RAG pipeline → `09-rag-retrieval/kaygraph-rag/`
- Text to SQL queries → `11-data-sql/kaygraph-text2sql/`
- PDF processing with vision → `12-tools-integration/kaygraph-tool-pdf-vision/`
- Web crawler + search → `12-tools-integration/kaygraph-tool-crawler/`

#### **Batch Processing**
- Process multiple items → `03-batch-processing/kaygraph-batch/`
- Parallel batch processing → `03-batch-processing/kaygraph-parallel-batch/`
- Nested batch operations → `03-batch-processing/kaygraph-nested-batch/`
- MapReduce pattern → `16-advanced-patterns/kaygraph-distributed-mapreduce/`

#### **A Workflow**
- Simple pipeline → `05-workflows/kaygraph-workflow/`
- With human approval → `14-ui-ux/kaygraph-human-in-the-loop/`
- Parallel tasks → `05-workflows/kaygraph-workflow-parallelization/`
- With error handling → `05-workflows/kaygraph-fault-tolerant-workflow/`
- Task routing/branching → `05-workflows/kaygraph-workflow-routing/`

#### **Production Features**
- API server → `13-production-monitoring/kaygraph-production-ready-api/`
- Real-time monitoring → `13-production-monitoring/kaygraph-realtime-monitoring/`
- Metrics dashboard → `13-production-monitoring/kaygraph-metrics-dashboard/`
- Background jobs → `13-production-monitoring/kaygraph-fastapi-background/`
- WebSocket support → `13-production-monitoring/kaygraph-fastapi-websocket/`

## 🟢 Start Here (Simplest)

1. **01-getting-started/kaygraph-hello-world/** - Absolute basics
2. **05-workflows/kaygraph-workflow/** - Simple pipeline
3. **07-chat-conversation/kaygraph-chat/** - Basic LLM interaction
4. **03-batch-processing/kaygraph-batch/** - Process multiple items

## 🟡 Common Combinations

| You Want | Combine These Examples |
|----------|----------------------|
| ChatGPT Clone | `chat-memory` + `streaming-llm` |
| Research Assistant | `agent` + `rag` + `tool-search` |
| Data Pipeline | `workflow` + `batch` + `validated-pipeline` |
| Multi-Agent System | `multi-agent` + `supervisor` + `agent-memory` |
| Production API | `production-ready-api` + `metrics-dashboard` + `fault-tolerant` |

## 🔴 Advanced Patterns

- **16-advanced-patterns/kaygraph-supervisor/** - Supervisor-worker pattern
- **13-production-monitoring/kaygraph-distributed-tracing/** - OpenTelemetry integration
- **06-ai-reasoning/kaygraph-think-act-reflect/** - Cognitive architecture
- **15-streaming-realtime/kaygraph-streaming-llm/** - Stream LLM responses
- **10-code-development/kaygraph-code-generator/** - Generate code with LLMs

## 🚀 Quick Start Path

```bash
# 1. Start with hello world
cd workbooks/01-getting-started/kaygraph-hello-world
python main.py

# 2. Try a simple workflow
cd ../05-workflows/kaygraph-workflow
python main.py

# 3. Add LLM capabilities
cd ../07-chat-conversation/kaygraph-chat
# Set up Ollama (see below)
python main.py

# 4. Build your custom solution
# Pick and combine patterns from above
```

## 🛠️ Setting Up Ollama (Free Local LLM)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model (3.8GB)
ollama pull llama3.2

# Start Ollama server
ollama serve

# Test it works
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Hello"
}'
```

Now all examples work with your local LLM!

## 📊 Complexity Levels

- 🟢 **Beginner**: hello-world, workflow, batch, chat
- 🟡 **Intermediate**: agent, rag, chat-memory, human-in-the-loop
- 🔴 **Advanced**: multi-agent, supervisor, distributed-*, streaming-*
- ⚫ **Production**: production-ready-api, realtime-monitoring, metrics-dashboard

## 💡 Tips

1. **Start simple** - Get a basic version working first
2. **Combine gradually** - Add one pattern at a time
3. **Use the same utils** - Copy `utils/call_llm.py` from any example
4. **Test locally** - Use Ollama to avoid API costs
5. **Check design.md** - Some workbooks have detailed design docs