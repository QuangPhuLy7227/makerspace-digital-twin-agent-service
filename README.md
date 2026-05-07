# makerspace-digital-twin-agent-service

A Python FastAPI service that hosts an LLM-powered agentic AI assistant for the MakerSpace Digital Twin. It uses a locally running Ollama model (`qwen2.5:7b-instruct`) with a LangGraph-style orchestration pipeline and Retrieval-Augmented Generation (RAG) over a static knowledge base. The agent can answer questions about printer status, task failures, print schedules, and general MakerSpace operations.

This is an optional component. The WebsiteWrapperFrontend AI assistant and the Unity Digital Twin AI Avatar both optionally connect to this service when it is running.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Runtime | Python, FastAPI |
| LLM | Ollama (`qwen2.5:7b-instruct`) — runs locally |
| Orchestration | LangGraph-style custom graph pipeline |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) |
| Vector Index | FAISS |
| Config | Pydantic Settings / `.env` |

---

## Agents

- **ExplanationAgent** — Explains printer states, task failures, and telemetry readings in plain language
- **ScheduleAgent** — Answers questions about the print job queue, scheduling decisions, and upcoming jobs

The routing pipeline selects the appropriate agent based on the incoming query.

---

## How to Run

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com) installed and running locally
- The `.NET` backend (`basic-makerspace-digital-twin-backend`) running and reachable

### 1. Pull the LLM

```bash
ollama pull qwen2.5:7b-instruct
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
BACKEND_API_BASE=http://localhost:5017
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b-instruct
```

### 3. Build the RAG Index

Run once to embed the static knowledge base:

```bash
python build_static_knowledge_index.py
```

### 4. Start the Service

```bash
uvicorn app.main:app --host 0.0.0.0 --port 9000
```

The service will be available at `http://localhost:9000`.

### Run via Docker

```bash
docker-compose up
```

---

## Key Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/chat` | Send a user message and receive an AI response |
| GET | `/health` | Health check — confirms the service and Ollama are reachable |

The `/chat` endpoint accepts the Convai conversational AI message format used by the Unity Digital Twin AI Avatar.

---

## System Context

This service sits at the AI layer of the broader Digital Twin ecosystem:

- Requires **basic-makerspace-digital-twin-backend** to be running to answer any real-time printer or schedule questions
- Optionally consumed by **WebsiteWrapperFrontend** for the web-based AI assistant chat panel
- Optionally consumed by **Digital-Twin-WebGL** (Unity) for the in-scene AI avatar voice/text interface

The service is fully optional — the rest of the system operates without it. Deploy it when AI query support is needed.
