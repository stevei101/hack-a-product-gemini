# The Product Mindset - Agentic Application

**The Product Mindset** is an AI-powered agentic workspace that acts as a thinking companion for creators and developers. It leverages large language models and retrieval-augmented generation to help users brainstorm, plan, and develop product ideas.

This project is built for the AWS & NVIDIA Hackathon, demonstrating a modern, scalable architecture for deploying AI microservices on Kubernetes.

##  Architektur

The application is designed as a containerized system deployed on Amazon EKS, with a clear separation between the user-facing frontend, the backend orchestration layer, and the GPU-intensive AI services.

### System Overview & Agentic Flow

```
[ Frontend (React + Bun) ]
        ↓
[ Backend Agent (FastAPI on EKS CPU Nodes) ]
        ↙︎                        ↘︎
[ Reasoning NIM (Nemotron on EKS GPU Nodes) ]   [ Embedding NIM (on EKS GPU Nodes) ]
```

1.  **User Input:** A user enters a product idea or prompt into the React-based frontend.
2.  **Orchestration:** The request is sent to the backend agent, a FastAPI application running on a standard CPU node group in EKS.
3.  **Reasoning & Retrieval:** The backend orchestrates the agentic workflow:
    *   It calls the **Nemotron NIM** (running on a dedicated GPU node) for reasoning, planning, and generating text.
    *   It calls the **Embedding NIM** (also on a GPU node) to convert text to vectors for storage or to retrieve relevant context from a vector store.
4.  **Response:** The backend synthesizes the information from the NIMs and sends the final, structured response back to the frontend.

### Technology Stack

| Category          | Technology                                                              |
| ----------------- | ----------------------------------------------------------------------- |
| **Frontend**      | React, TypeScript, Bun, Tailwind CSS                                    |
| **Backend**       | Python, FastAPI                                                         |
| **AI Services**   | NVIDIA NIMs (Nemotron-Nano-8B-v1, Retrieval Embedding Model)            |
| **Infrastructure**| AWS, Amazon EKS, Amazon ECR, Terraform                                  |
| **CI/CD**         | GitHub Actions, Docker, Helm                                            |

## Project Structure

```
.
├── .github/workflows/  # CI/CD pipelines for deployment
├── backend/            # FastAPI backend application (the "agent")
├── charts/             # Helm charts for deploying to Kubernetes
├── kubernetes/         # Manifests for GPU operator and NIMs
├── src/                # React frontend application
├── terraform/          # Terraform code for all AWS infrastructure (VPC, EKS, etc.)
└── ...
```

## 🚀 Getting Started

### Prerequisites

- **Bun**: For frontend development.
- **Python 3.11+**: For the backend API.
- **Docker**: For containerization and local development.
- **Terraform**: For provisioning cloud infrastructure.
- **AWS CLI**: For interacting with AWS.
- **kubectl**: For interacting with the Kubernetes cluster.
- **Helm**: For deploying applications on Kubernetes.

### Local Development

A `docker-compose.yml` file will be added to streamline local development. For now, you can run each service manually:

1.  **Set Environment Variables**:
    *   Copy `backend/env.example` to `backend/.env` and add your NVIDIA API key and other secrets.

2.  **Run the Backend**:
    ```bash
    make backend-dev
    ```

3.  **Run the Frontend**:
    ```bash
    make dev
    ```

## 🌐 Deployment

The entire application is deployed via a unified GitHub Actions workflow (`.github/workflows/deploy.yml`) triggered on pushes to the `develop` branch.

The workflow performs the following steps:
1.  **Provision Infrastructure**: Runs `terraform apply` to create or update the AWS resources (VPC, EKS cluster, node groups, ECR repos).
2.  **Build & Test**: Builds the frontend and runs tests for the backend.
3.  **Push to ECR**: Builds Docker images for the frontend and backend and pushes them to Amazon ECR.
4.  **Deploy to EKS**: Uses Helm to deploy the frontend and backend applications to the EKS cluster.

The NVIDIA NIMs and GPU Operator must be installed on the cluster separately, as described in `kubernetes/README.md`.

## 🛠️ Makefile Commands

This project includes a comprehensive `Makefile` with convenient shortcuts for common tasks. Run `make help` for a full list of available commands.