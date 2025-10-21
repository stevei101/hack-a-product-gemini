# The Product Mindset - AWS & NVIDIA Hackathon Submission

## Overview

**The Product Mindset** is an agentic AI workspace that acts as a thinking companion for creators and developers. Built specifically for the AWS and NVIDIA hackathon, it demonstrates cutting-edge AI integration with a focus on agentic workflows and retrieval-augmented generation.

## Hackathon Requirements ✅

### ✅ Official NVIDIA API Format
The implementation follows the official NVIDIA NIM API format from [build.nvidia.com](https://build.nvidia.com/nvidia/llama-3_1-nemotron-nano-8b-v1):
- Correct model naming: `nvidia/llama-3_1-nemotron-nano-8b-v1` (underscores, not dashes)
- System parameter: `"detailed thinking off"` for Nemotron-specific behavior
- Full parameter support: temperature, top_p, max_tokens, frequency_penalty, presence_penalty
- Compatible with OpenAI client format

### ✅ Agentic Application
The application functions as an intelligent agent that assists users through the entire product development lifecycle:
- **Ideation**: Brainstorming and capturing creative ideas
- **Planning**: Organizing thoughts into actionable goals
- **Design**: Structuring features and tasks
- **Execution**: Contextual guidance through implementation

### ✅ NVIDIA NIM - Llama 3.1 Nemotron Nano 8B
- **Model**: `nvidia/llama-3_1-nemotron-nano-8b-v1`
- **Purpose**: Large language reasoning and intelligent conversation
- **Implementation**: `/supabase/functions/server/index.tsx` line 265
- **Special Feature**: Uses "detailed thinking off" system parameter for concise responses
- **Features**:
  - Context-aware responses
  - Remembers project history
  - Provides creative suggestions
  - Assists with planning and ideation

### ✅ Retrieval Embedding NIM
- **Model**: `nvidia/nv-embedqa-e5-v5`
- **Purpose**: Semantic search and context retrieval
- **Implementation**: `/supabase/functions/server/index.tsx` line 4-19
- **Features**:
  - Generates embeddings for all project ideas
  - Performs cosine similarity search
  - Retrieves semantically relevant context
  - Enhances AI responses with RAG (Retrieval-Augmented Generation)

## Architecture

### Three-Tier System
```
Frontend (React + TypeScript)
    ↓
Server (Supabase Edge Functions + Hono)
    ↓
Database (Supabase KV Store)
```

### AI Provider Integration

#### NVIDIA NIM Stack
1. **Reasoning Engine**: Nemotron Nano 8B for intelligent responses
   - Model: `nvidia/llama-3_1-nemotron-nano-8b-v1`
   - System setting: "detailed thinking off" for concise, actionable responses
   - Parameters: temperature=0.7, top_p=0.95, max_tokens=4096
2. **Embedding Engine**: NV-EmbedQA-E5-v5 for semantic search
   - Model: `nvidia/nv-embedqa-e5-v5`
   - Generates 1024-dimension vectors for semantic similarity
3. **RAG Pipeline**:
   - User asks question → Generate query embedding
   - Compare with stored idea embeddings (cosine similarity)
   - Retrieve top 3 most relevant ideas (threshold > 0.3)
   - Enhance AI prompt with retrieved context
   - Generate context-aware response

#### AWS Bedrock (Alternative Provider)
- **Model**: Claude 3 Sonnet
- **Purpose**: Enterprise-grade conversational AI
- **Features**: Advanced reasoning, Bedrock Guardrails ready

### RAG (Retrieval-Augmented Generation) Implementation

The system implements a complete RAG pipeline:

1. **Embedding Generation** (`/supabase/functions/server/index.tsx:4-19`)
   ```typescript
   async function generateEmbedding(text: string, apiKey: string): Promise<number[]>
   ```
   - Calls NVIDIA Embedding API
   - Returns vector representation of text

2. **Similarity Search** (`/supabase/functions/server/index.tsx:21-29`)
   ```typescript
   function cosineSimilarity(a: number[], b: number[]): number
   ```
   - Computes similarity between query and stored embeddings
   - Ranks ideas by relevance

3. **Context Enhancement** (`/supabase/functions/server/index.tsx:131-175`)
   - Automatically generates embeddings for new ideas
   - Retrieves relevant context on every query
   - Augments AI prompt with semantic context

4. **Visualization** (`/components/RAGStatusPanel.tsx`)
   - Shows embedding status for all ideas
   - Displays vector dimensions
   - Demonstrates RAG system in action

## Key Features

### 🤖 Dual AI Providers
- Switch between NVIDIA NIM and AWS Bedrock
- Real-time provider indicators
- Optimized for different use cases

### 🎨 Ideation Canvas
- Visual board for organizing ideas
- Four-column workflow: Brainstorm → Planning → In Progress → Completed
- Support for Ideas, Goals, Features, and Tasks

### 🔍 RAG-Powered Context
- Semantic search across project history
- Automatic embedding generation
- Intelligent context retrieval
- Visual status panel for embeddings

### 💬 Context-Aware AI Chat
- Remembers project history
- References past conversations
- Provides actionable suggestions
- Adapts to user's workflow

### 💾 Persistent Storage
- All data stored in Supabase
- Cross-device synchronization
- Conversation history retention
- Embedding cache for performance

## Technology Stack

### Frontend
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Icons**: Lucide React

### Backend
- **Runtime**: Deno (Supabase Edge Functions)
- **Framework**: Hono (lightweight web framework)
- **Database**: Supabase KV Store
- **API**: RESTful endpoints

### AI Integration
- **NVIDIA NIM**: Llama 3.1 Nemotron Nano 8B + NV-EmbedQA-E5-v5
- **AWS Bedrock**: Claude 3 Sonnet
- **SDK**: AWS SDK for JavaScript, NVIDIA API

## Demo Flow

### For Hackathon Judges

1. **Launch Application**
   - Welcome screen highlights AWS + NVIDIA integration
   - Shows agentic architecture

2. **Create a Project**
   - Click "New Project" in sidebar
   - Enter project details

3. **Add Ideas**
   - Use "Add Idea" button on Ideation Canvas
   - Add multiple ideas with descriptions
   - Ideas are automatically embedded when using NVIDIA NIM

4. **View RAG Status**
   - Click "Show RAG Status" button
   - See real-time embedding generation
   - View vector dimensions and embedded ideas

5. **Chat with AI (NVIDIA NIM)**
   - Switch to NVIDIA provider in Settings
   - Note "RAG Active" badge appears
   - Ask questions about your project
   - AI retrieves semantically similar ideas
   - Responses are context-aware

6. **Compare Providers**
   - Switch to AWS Bedrock in Settings
   - Compare response styles
   - Both maintain conversation history

## API Endpoints

### Projects
- `GET /projects` - List all projects
- `POST /projects` - Create new project
- `GET /projects/:id` - Get project details
- `PUT /projects/:id` - Update project
- `DELETE /projects/:id` - Delete project

### AI Chat
- `POST /chat` - Send message to AI (multi-provider)
  - Supports: `provider: 'nvidia' | 'bedrock'`
  - Includes RAG when using NVIDIA

### Embeddings (Demo)
- `GET /projects/:id/embeddings` - Get embedding status
  - Shows which ideas have embeddings
  - Displays vector dimensions
  - Useful for hackathon demonstration

## Environment Variables Required

```bash
# NVIDIA NIM
NVIDIA_API_KEY=your_nvidia_api_key

# AWS Bedrock
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1

###THIS IS TO BE REPLACED!
# Supabase (pre-configured)
SUPABASE_URL=auto_configured
SUPABASE_ANON_KEY=auto_configured
SUPABASE_SERVICE_ROLE_KEY=auto_configured
###
```

## Code Highlights

### RAG Implementation
Location: `/supabase/functions/server/index.tsx`

The RAG system:
1. Generates embeddings on-demand for ideas
2. Caches embeddings in KV store (key: `embedding:{projectId}:{ideaId}`)
3. Computes cosine similarity for each query
4. Retrieves top 3 most relevant ideas
5. Enhances AI prompt with retrieved context

### Agentic Behavior
The AI agent:
- **Perceives**: Understands project context through embeddings
- **Reasons**: Uses Nemotron Nano for intelligent responses
- **Acts**: Provides actionable suggestions and next steps
- **Learns**: Remembers conversation history and project evolution

## Performance Optimizations

1. **Embedding Caching**: Embeddings stored in KV store, generated once
2. **Lazy Loading**: Embeddings generated on first query
3. **Efficient Retrieval**: Only compares embeddings when RAG is active
4. **Provider Switching**: Instant switching between AI providers

## Future Enhancements

- **Bedrock Guardrails**: Add content filtering and safety
- **Multi-modal**: Support image and document uploads
- **Collaboration**: Real-time multi-user editing
- **NeMo Integration**: Advanced model customization
- **Agent Workflows**: Multi-step autonomous task execution

## Conclusion

The Product Mindset demonstrates a complete agentic AI application using:
- ✅ **NVIDIA NIM** for reasoning (Nemotron Nano 8B)
- ✅ **Retrieval Embedding NIM** for semantic search (NV-EmbedQA-E5-v5)
- ✅ **RAG Pipeline** for context-aware responses
- ✅ **AWS Bedrock** as alternative provider
- ✅ **Agentic Workflow** from ideation to execution

This application showcases the power of combining state-of-the-art LLMs with intelligent retrieval systems to create a truly helpful AI companion for creators and developers.
