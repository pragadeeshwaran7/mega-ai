# Mega AI: Real-Time Multi-Agent LLM Orchestration & Evaluation

A production-grade, containerized multi-agent system featuring dynamic routing, self-improving prompt loops, and real-time observability.

## 🚀 Architecture Overview

The system is composed of five major layers:

```
┌─────────────────────────────────────────────┐
│                 FastAPI Server               │
│           (SSE Streaming + REST)             │
├─────────────────────────────────────────────┤
│              ORCHESTRATOR AGENT              │
│         (Dynamic Routing Engine)             │
├────────┬──────────┬──────────┬──────────────┤
│ DECOMP │   RAG    │ CRITIQUE │  SYNTHESIS   │
│ Agent  │  Agent   │  Agent   │   Agent      │
├────────┴──────────┴──────────┴──────────────┤
│              TOOL LAYER                      │
│  Web Search │ Code Exec │ SQL │ Reflection   │
├─────────────────────────────────────────────┤
│          EVALUATION HARNESS                  │
│  15 Test Cases │ Multi-Dim Scoring │ Meta    │
├─────────────────────────────────────────────┤
│        DATABASE & LOGGING LAYER              │
│    SQLite/PostgreSQL │ Structured Logger      │
└─────────────────────────────────────────────┘
```

## 📂 Project Structure

```
mega-ai/
├── main.py                    # FastAPI entry point with SSE streaming
├── worker.py                  # Background job processor
├── database.py                # SQLAlchemy ORM models
├── context.py                 # Shared context schema (Pydantic)
├── budget.py                  # Token budget management & compression
├── llm.py                     # LLM client (Anthropic/OpenAI)
├── logger.py                  # Structured execution logger
├── prompts.py                 # Dynamic prompt store with DB fallback
├── agents/
│   ├── base.py                # Abstract base agent
│   ├── orchestrator.py        # Master routing agent
│   ├── decomposition.py       # Query decomposition into sub-tasks
│   ├── rag.py                 # Multi-hop retrieval agent
│   ├── critique.py            # Adversarial critique agent
│   ├── synthesis.py           # Final answer synthesis
│   ├── compression.py         # Context compression agent
│   └── meta_agent.py          # Self-improving prompt optimizer
├── tools/
│   ├── base.py                # Abstract tool interface
│   ├── web_search.py          # Web search with fallback
│   ├── code_execution.py      # Sandboxed Python execution
│   ├── sql_lookup.py          # SQL query tool
│   └── reflection.py          # Self-reflection tool
├── eval/
│   ├── test_cases.py          # 15 adversarial test cases
│   ├── scoring.py             # Multi-dimensional scoring
│   └── harness.py             # Evaluation runner with DB storage
├── log_ui/
│   └── index.html             # Real-time execution trace dashboard
├── docker-compose.yml         # Full containerized deployment
├── Dockerfile.api             # API server container
├── Dockerfile.worker          # Background worker container
├── Dockerfile.logui           # Log UI container
├── nginx.conf                 # Reverse proxy config
├── init.sql                   # Database schema initialization
├── vercel.json                # Vercel serverless deployment config
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variable template
└── README.md
```

## 🛠️ Quick Start

### Option 1: Local Development

```bash
# Clone the repository
git clone https://github.com/pragadeeshwaran7/mega-ai.git
cd mega-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the server
uvicorn main:app --reload --port 8000
```

### Option 2: Docker Compose (Full Stack)

```bash
cp .env.example .env
# Edit .env with your API keys and PostgreSQL credentials

docker-compose up --build
```

Services:
- **API**: http://localhost:8000
- **Log UI**: http://localhost:3000
- **PostgreSQL**: localhost:5432

### Option 3: Vercel Deployment

This project is configured for one-click Vercel deployment:

1. Push to GitHub
2. Import the repository in [Vercel](https://vercel.com)
3. Add environment variables (`ANTHROPIC_API_KEY` or `OPENAI_API_KEY`)
4. Deploy!

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Real-time execution trace dashboard |
| `POST` | `/submit?query=...` | Submit a new query for processing |
| `GET` | `/stream/{job_id}` | SSE stream of real-time execution logs |
| `GET` | `/trace/{job_id}` | Full execution trace for a job |
| `GET` | `/eval/latest` | Latest evaluation run results |
| `POST` | `/eval/re-run` | Trigger a full evaluation pass |
| `POST` | `/prompt/approve/{id}` | Approve a prompt version from meta-agent |
| `GET` | `/health` | System health check |

## 🧠 Key Features

### Dynamic Agent Orchestration
The Orchestrator Agent uses LLM-driven routing (not hardcoded chains) to decide which sub-agent to invoke next based on query complexity, context, and budget.

### Context Budget Management
Token-aware budget tracking with automatic context compression when limits are approached. Uses lossless compression for structured data (tool outputs, citations) and lossy for filler.

### Self-Improving Evaluation Loop
- **15 test cases** across 3 categories: straightforward, ambiguous, adversarial
- **Multi-dimensional scoring**: correctness, citation accuracy, tool efficiency, budget compliance, critique agreement
- **Meta-Agent**: Automatically proposes prompt rewrites for worst-performing agents
- **Human-in-the-loop**: Prompt changes require explicit approval

### Tool Orchestration with Failure Handling
Each tool returns structured `ToolResult` objects with status codes (`success`, `timeout`, `error`, `empty`), latency tracking, and retry logic.

### Real-Time Observability
SSE-powered live dashboard showing every agent thought, tool call, and decision in real time with a premium dark-mode UI.

## 🔑 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Anthropic API key | Yes (if using Claude) |
| `OPENAI_API_KEY` | OpenAI API key | Yes (if using GPT) |
| `DEFAULT_MODEL` | Default LLM model | No (defaults to claude-3-opus) |
| `DATABASE_URL` | Database connection string | No (defaults to SQLite) |

## 📜 License

MIT License
