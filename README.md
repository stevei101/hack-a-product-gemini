# The Product Mindset - Agentic Application

AKA hack-a-product

**The Product Mindset** is an AI-powered agentic workspace that acts as a thinking companion for creators and developers. Built for the AWS & NVIDIA Hackathon, it demonstrates cutting-edge AI integration with a focus on agentic workflows and retrieval-augmented generation.

![Screenshot of the application UI](./preview.png)

## 🧠 Updated Architecture — NIM-Compliant Edition

This revised architecture matches the new NVIDIA NIM and retrieval embedding requirements while keeping AWS Bedrock integration optional but compatible.

### 🔧 Core Hackathon Requirements
- ✅ Use **Llama-3.1-Nemotron-Nano-8B-v1** as your reasoning model.
- ✅ Deploy it as an **NVIDIA NIM** Inference Microservice.
- ✅ Include at least one **Retrieval Embedding NIM** for memory or context search.
- ✅ Show **agentic behavior** (reasoning + planning + multi-step action).
- ✅ (Optional) Integrate AWS Bedrock for orchestration, guardrails, or data ops.

### 🧩 System Overview & Agentic Flow
```
[ Frontend (Next.js + React) ]
        ↓
[ API Gateway / Lambda ]
        ↓
[ Agentic Orchestrator Layer ]
        ↙︎                        ↘︎
[NVIDIA NIM (Nemotron-Nano-8B-v1)]   [Retrieval Embedding NIM]
        ↓                               ↓
[ Vector Memory Store (FAISS / DynamoDB) ]
```

1.  **User Input:** A user enters a prompt or idea in the Next.js frontend.
2.  **Orchestration:** API Gateway sends the request to the Agentic Orchestrator (Lambda or Bedrock).
3.  **Reasoning:** The Orchestrator routes the request to the NIM reasoning model (Nemotron-Nano-8B-v1).
4.  **Enrichment:** The response is enriched by the Retrieval Embedding NIM, which fetches context or prior session data from the Vector Memory Store.
5.  **Output:** The merged, context-aware output is sent back to the frontend as a structured plan or design insight.

### 🧱 Component Breakdown

#### 🪟 Frontend
- **Stack:** Next.js + Tailwind CSS
- **Features:**
    - **Chat Canvas:** For ideation and planning.
    - **Knowledge Sidebar:** For context retrieved via the Embedding NIM.
    - **Task Board:** Auto-generated from agentic reasoning.

#### ⚙️ API Gateway + Agent Orchestrator
- **Implementation:** AWS Lambda (Node.js or Python).
- **Responsibilities:** Handles routing between the reasoning and retrieval NIMs. Can optionally use Bedrock Guardrails for safety.
- **Pseudocode:**
  ```python
  response = call_nim_reasoner(prompt)
  context = retrieve_context_with_nim_embeddings(project_id)
  final_output = merge_agentic_output(response, context)
  return final_output
  ```

#### 🧩 NVIDIA NIM Microservices
- **Reasoning NIM:** `Nemotron-Nano-8B-v1` hosted on NGC or locally. Performs reasoning, planning, and synthesis.
- **Retrieval Embedding NIM:** Generates embeddings for user data and supports `/embed` and `/query` endpoints for vector search.
- **Example Deployment:**
  ```bash
  docker run -p 8000:8000 nvcr.io/nim/llama-3-nemotron-nano-8b-v1:latest
  ```

#### 💾 Vector Memory Layer
- **Technology:** FAISS (local) or Amazon DynamoDB + Bedrock Embeddings.
- **Function:** Stores each new idea or interaction as an embedding vector for future retrieval.

### 🌐 Deployment Flow
1.  **NIM Services:** Deploy both NIM containers on an NVIDIA GPU instance (G6, DGX Cloud, or on-prem).
2.  **Frontend:** Deploy the Next.js frontend via AWS Amplify.
3.  **Backend:** Deploy the Lambda backend to bridge the AWS and NIM APIs.
4.  **Security:** Use AWS Secrets Manager for NIM API credentials.

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**: For the backend API
- **Bun**: For frontend development and package management
- **Docker**: For containerization (optional for local development)
- **NVIDIA API Key**: For AI functionality (get from [NVIDIA NIM](https://build.nvidia.com))

### 🏃‍♂️ Get Started in 3 Steps

1. **Quick Setup**:
   ```bash
   make quick-start
   ```

2. **Set Your API Key**:
   ```bash
   # Edit backend/.env and add your NVIDIA API key
   NIM_API_KEY=your_actual_nvidia_api_key_here
   ```

3. **Start the Application**:
   ```bash
   # Terminal 1: Start backend
   make backend-dev
   
   # Terminal 2: Start frontend
   make dev
   ```

## 🛠️ Makefile Commands

This project includes a comprehensive `Makefile` with convenient shortcuts for all tasks. (See `make help` for a full list).

## 📄 Documentation

All project documentation has been moved to the `/docs` directory.
