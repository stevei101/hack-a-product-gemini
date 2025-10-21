# NVIDIA NIM Integration Guide - Agentic AI Unleashed AWS and NVIDIA Hackathon

This project is designed for the Agentic AI Unleashed AWS and NVIDIA Hackathon and supports both AWS Bedrock and NVIDIA NIM (NVIDIA Inference Microservices) as AI providers. The implementation includes:

- **Required Model**: `llama-3.1-nemotron-nano-8B-v1` for large language reasoning
- **Retrieval Embedding NIM**: Document search and RAG functionality
- **Agentic Application**: AI-powered ideation with document-based context

## NVIDIA NIM Setup

### Prerequisites

1. **NVIDIA GPU**: Compatible NVIDIA GPU with sufficient memory
2. **Docker**: Install Docker and NVIDIA Container Toolkit
3. **CUDA Drivers**: Install appropriate CUDA drivers
4. **NVIDIA AI Enterprise License**: Required for NIM access

### Option A: NVIDIA Hosted API (Recommended for Hackathon)

**No local deployment required!** Use NVIDIA's hosted API endpoint:

```bash
# Set environment variables
NIM_BASE_URL=https://integrate.api.nvidia.com/v1
NIM_API_KEY=your_nvidia_api_key
NIM_MODEL=nvidia/llama-3.1-nemotron-nano-8b-v1
```

**Benefits:**
- ✅ No infrastructure setup required
- ✅ No GPU resources needed
- ✅ Instant deployment
- ✅ Managed by NVIDIA
- ✅ Hackathon compliant

### Option B: Local Docker Deployment

1. **Pull Required NIM Containers**:
   ```bash
   # Hackathon-required reasoning model
   docker pull nvcr.io/nim/nvidia/llama-3.1-nemotron-nano-8b-v1
   
   # Retrieval embedding model
   docker pull nvcr.io/nim/nvidia/nemotron-embedding-3
   ```

2. **Run the NIM Containers**:
   ```bash
   # Reasoning model (port 8000)
   docker run --rm --gpus all -p 8000:8000 nvcr.io/nim/nvidia/llama-3.1-nemotron-nano-8b-v1
   
   # Embedding model (port 8001)
   docker run --rm --gpus all -p 8001:8000 nvcr.io/nim/nvidia/nemotron-embedding-3
   ```

3. **Verify Deployment**:
   ```bash
   # Test reasoning model
   curl -X POST http://localhost:8000/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{
       "model": "nvidia/llama-3.1-nemotron-nano-8b-v1",
       "messages": [{"role": "user", "content": "Hello!"}],
       "max_tokens": 50
     }'
   
   # Test embedding model
   curl -X POST http://localhost:8001/v1/embeddings \
     -H "Content-Type: application/json" \
     -d '{
       "model": "nvidia/nemotron-embedding-3",
       "input": "Test embedding"
     }'
   ```

### Option C: Test Hosted API
```bash
# Test NVIDIA hosted API directly
curl -X POST https://integrate.api.nvidia.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $YOUR_API_KEY" \
  -d '{
    "model": "nvidia/llama-3.1-nemotron-nano-8b-v1",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 50,
    "temperature": 0,
    "top_p": 0.95
  }'
```

### Available Models

**Hackathon Required Models:**
- **Llama 3.1 Nemotron Nano 8B v1**: Required reasoning model for agentic applications
- **Nemotron Embedding 3**: Required embedding model for retrieval functionality

**Additional Supported Models:**
- **Llama 3.1 8B Instruct**: Fast, efficient model for general tasks
- **Llama 3.1 70B Instruct**: High-quality model for complex reasoning
- **Code Llama 7B Instruct**: Specialized for code generation and analysis
- **Code Llama 13B Instruct**: Advanced code generation capabilities
- **Mistral 7B Instruct**: Balanced performance and efficiency
- **Mixtral 8x7B Instruct**: Mixture of experts for diverse capabilities

### Environment Variables

Set these environment variables in your Supabase Edge Function:

```bash
# NVIDIA Hosted API Configuration (Recommended)
NIM_BASE_URL=https://integrate.api.nvidia.com/v1
NIM_API_KEY=your_nvidia_api_key
NIM_MODEL=nvidia/llama-3.1-nemotron-nano-8b-v1
NIM_MAX_TOKENS=4096
NIM_TEMPERATURE=0
NIM_TOP_P=0.95
NIM_FREQUENCY_PENALTY=0
NIM_PRESENCE_PENALTY=0

# Local Docker Configuration (Alternative)
# NIM_BASE_URL=http://localhost:8000
# NIM_API_KEY=not_required_for_local

# NVIDIA Embedding NIM Configuration (Hackathon Required)
EMBEDDING_NIM_BASE_URL=http://localhost:8001
EMBEDDING_NIM_API_KEY=your_api_key_if_needed
EMBEDDING_NIM_MODEL=nvidia/nemotron-embedding-3

# AWS Bedrock Configuration (fallback)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
```

### Cloud Deployment Options

NVIDIA NIM can be deployed on various cloud platforms:

- **AWS EKS**: Deploy using Kubernetes with NIM Operator
- **Azure AKS**: Container-based deployment
- **Google GKE**: Managed Kubernetes service
- **Managed Services**: Through partners like Baseten, Fireworks AI, Together AI

### Usage

1. **Switch Providers**: Click the provider selector in the AI Companion panel
2. **Configure NIM**: Set base URL, model, and other parameters
3. **Start Chatting**: Messages will be routed to your selected provider

### Features

- **Multi-Provider Support**: Switch between AWS Bedrock and NVIDIA NIM
- **Streaming Support**: Real-time response streaming with NVIDIA NIM
- **Model Selection**: Choose from various NIM models
- **Configuration Management**: Persistent provider settings
- **Error Handling**: Graceful fallback and error reporting

### Troubleshooting

**Common Issues**:

1. **Connection Refused**: Ensure NIM container is running on the correct port
2. **GPU Not Found**: Verify NVIDIA Container Toolkit installation
3. **Model Not Available**: Check if the model is pulled and running
4. **Authentication Errors**: Verify API keys and permissions

**Debug Commands**:

```bash
# Check container status
docker ps | grep nim

# View container logs
docker logs <container_id>

# Test API endpoint
curl -X GET http://localhost:8000/health
```

### Performance Tips

1. **Model Selection**: Choose smaller models (8B) for faster responses
2. **Token Limits**: Adjust max_tokens based on your use case
3. **Temperature**: Lower values (0.1-0.3) for consistent responses
4. **GPU Memory**: Ensure sufficient VRAM for your chosen model

### Security Considerations

1. **Container Verification**: Use NVIDIA's signing key to verify containers
2. **Network Security**: Restrict access to NIM endpoints
3. **API Keys**: Store securely and rotate regularly
4. **SBOM Review**: Review Software Bill of Materials for security

For more information, visit the [NVIDIA NIM Documentation](https://docs.nvidia.com/nim/).

