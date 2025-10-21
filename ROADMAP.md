# Project Roadmap: The Product Mindset

This document outlines the development roadmap for "The Product Mindset" agentic application. It tracks our progress from foundational infrastructure to a feature-rich, AI-powered creative workspace.

---

## Phase 1: Foundational Infrastructure & Core AI

*Focus: Establishing a scalable, production-ready environment for the application and its AI microservices.*

- [x] **Setup Initial Project Structure:** Basic frontend, backend, and CI/CD.
- [x] **Containerize Frontend & Backend:** Create Dockerfiles for both services.
- [x] **Establish CI/CD Pipeline:** Configure GitHub Actions for automated builds and tests.
- [x] **Define EKS Infrastructure in Terraform:**
    - [x] Create VPC, EKS Cluster, and IAM Roles.
    - [x] Define a CPU node group for general workloads.
    - [x] Define a GPU node group for NVIDIA NIMs.
- [x] **Setup ECR & Deploy Workflow:** Configure Terraform for ECR and update the GitHub Actions workflow to push images and deploy to EKS.
- [x] **Update Project Documentation:** Rewrite the main `README.md` to reflect the current architecture.
- [ ] **Deploy NVIDIA GPU Operator:** Install the operator on the EKS cluster to manage GPU resources.
- [ ] **Deploy Vector Database:** Add a vector store (e.g., ChromaDB) to the Kubernetes cluster for the agent's memory.
- [ ] **Deploy NVIDIA NIMs:**
    - [ ] Deploy the Nemotron-Nano-8B-v1 (Reasoning) NIM via Helm.
    - [ ] Deploy the Embedding NIM (Retrieval) via Helm.

---

## Phase 2: Minimum Viable Product (MVP) - The Ideation Workspace

*Focus: Building the core user experience, allowing users to interact with the AI agent in a meaningful way.*

- [ ] **Build the Ideation UI (Frontend):**
    - [ ] **(In Progress)** Replace the placeholder UI with a chat-style interface.
    - [ ] Implement state management for conversations.
    - [ ] Create components for displaying the agent's structured responses (e.g., "Idea Block Cards").
- [ ] **Implement the Core Agentic Loop (Backend):**
    - [ ] Create the API endpoint to receive user prompts.
    - [ ] Write the orchestration logic to call the Nemotron NIM.
    - [ ] Write the logic to call the Embedding NIM and interact with the vector database.
    - [ ] Develop the data structures for returning plans, ideas, and context to the frontend.
- [ ] **End-to-End Integration:** Connect the UI to the backend and ensure the full conversational flow is working.

---

## Phase 3: Advanced Features & Polish

*Focus: Expanding on the MVP to build a multi-faceted creative tool and enhance the agent's intelligence.*

- [ ] **Develop the Planning View:**
    - [ ] Create a UI to convert the agent's plans into task lists or Kanban boards.
    - [ ] Implement backend logic for managing task state.
- [ ] **Develop the Design Canvas:**
    - [ ] Build a lightweight visual canvas for brainstorming and wireframing.
    - [ ] Integrate the AI to provide contextual design feedback.
- [ ] **Enhance Agent Memory & Insights:**
    - [ ] Implement long-term memory for projects.
    - [ ] Develop the "Insights" feature to identify user patterns and provide helpful suggestions.
- [ ] **Improve Developer & Designer Experience:**
    - [ ] Create a `docker-compose.yml` for a one-command local setup.
    - [ ] Introduce a component library like Storybook for the frontend.
- [ ] **User Experience Polish:**
    - [ ] Add proactive AI prompts and "context bubbles."
    - [ ] Refine the visual style and add microinteractions.
