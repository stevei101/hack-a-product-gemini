# Agentic Application Backend

FastAPI backend application with NVIDIA NIM integration for AI-powered task management and agent orchestration.

## Features

- RESTful API with FastAPI
- NVIDIA NIM integration for AI capabilities
- Vector database with ChromaDB for RAG
- PostgreSQL database with AsyncPG
- Task management and agent orchestration
- WebSocket support for real-time updates

## Installation

```bash
pip install -e .
```

## Development

```bash
pip install -e ".[dev]"
```

## Running

```bash
uvicorn agentic_app.main:app --reload
```

