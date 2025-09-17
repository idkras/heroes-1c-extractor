# 🚀 Potpie Integration with Heroes Platform

## Overview

This document describes the integration of [Potpie](https://github.com/potpie-ai/potpie) with Heroes Platform, enabling AI-powered codebase analysis and custom engineering agents.

## 🏗️ Architecture

### Services Integration

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Heroes        │    │     Potpie      │    │   Shared        │
│   Platform      │    │     API         │    │   Services      │
│                 │    │                 │    │                 │
│ • MCP Servers   │◄──►│ • AI Agents     │    │ • PostgreSQL    │
│ • Workflows     │    │ • Knowledge     │    │ • Neo4j         │
│ • Standards     │    │   Graph         │    │ • Redis         │
│ • CLI Tools     │    │ • Code Analysis │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Port Configuration

- **Heroes Platform API**: `8000`
- **Potpie API**: `8001`
- **Neo4j Browser**: `7474`
- **Neo4j Bolt**: `7687`
- **PostgreSQL (Heroes)**: `5432`
- **PostgreSQL (Potpie)**: `5433`
- **Redis**: `6379`

## 🚀 Quick Start

### 1. Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Git

### 2. Installation

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd heroes-template/heroes_platform

# Start the integrated system
./start_heroes_with_potpie.sh
```

### 3. Configuration

Edit `potpie/.env` to configure your AI provider:

```bash
# Copy example configuration
cp config/potpie.env.example potpie/.env

# Edit the configuration
nano potpie/.env
```

Required configuration:
```env
# AI Provider Configuration
PROVIDER_API_KEY=sk-proj-your-key
INFERENCE_MODEL=ollama_chat/qwen2.5-coder:7b
CHAT_MODEL=ollama_chat/qwen2.5-coder:7b
```

### 4. Testing

```bash
# Run integration tests
python scripts/test_potpie_integration.py
```

## 🔧 Usage

### Heroes Platform + Potpie Workflow

1. **Parse Repository**:
   ```bash
   curl -X POST 'http://localhost:8001/api/v1/parse' \
     -H 'Content-Type: application/json' \
     -d '{
       "repo_path": "/path/to/your/repo",
       "branch_name": "main"
     }'
   ```

2. **Create Conversation**:
   ```bash
   curl -X POST 'http://localhost:8001/api/v1/conversations/' \
     -H 'Content-Type: application/json' \
     -d '{
       "user_id": "heroes_user",
       "title": "Code Analysis",
       "status": "active",
       "project_ids": ["your-project-id"],
       "agent_ids": ["chosen-agent-id"]
     }'
   ```

3. **Interact with Agent**:
   ```bash
   curl -X POST 'http://localhost:8001/api/v1/conversations/your-conversation-id/message/' \
     -H 'Content-Type: application/json' \
     -d '{
       "content": "Analyze the codebase architecture",
       "node_ids": []
     }'
   ```

### Heroes Platform MCP Integration

Use Heroes Platform MCP tools with Potpie analysis:

```python
from heroes_platform.heroes_mcp import MCPClient

# Initialize MCP client
client = MCPClient()

# Use Heroes Platform tools
result = client.call_tool("standards_workflow_command", {
    "command": "analyze",
    "kwargs": "{}"
})

# Integrate with Potpie analysis
potpie_result = client.call_tool("potpie_analyze_codebase", {
    "repo_path": "/path/to/repo",
    "analysis_type": "architecture"
})
```

## 🛠️ Development

### Adding Custom Agents

1. **Create Agent via API**:
   ```bash
   curl -X POST "http://localhost:8001/api/v1/custom-agents/agents/auto" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "An agent that analyzes code quality and suggests improvements"
     }'
   ```

2. **Integrate with Heroes Platform**:
   ```python
   # In your Heroes Platform workflow
   def analyze_code_quality(repo_path):
       # Use Potpie agent
       potpie_analysis = call_potpie_agent("code_quality_agent", repo_path)
       
       # Use Heroes Platform standards
       standards_check = call_heroes_standards(repo_path)
       
       # Combine results
       return combine_analysis(potpie_analysis, standards_check)
   ```

### Custom Tools Integration

Add custom tools to Potpie in `potpie/app/modules/intelligence/tools/`:

```python
# heroes_platform_tool.py
from heroes_platform.heroes_mcp import MCPClient

class HeroesPlatformTool:
    def __init__(self):
        self.mcp_client = MCPClient()
    
    def call_heroes_workflow(self, command, kwargs):
        return self.mcp_client.call_tool("standards_workflow_command", {
            "command": command,
            "kwargs": kwargs
        })
```

## 📊 Monitoring

### Health Checks

- **Heroes Platform**: `http://localhost:8000/health`
- **Potpie**: `http://localhost:8001/health`
- **Neo4j**: `http://localhost:7474`

### Logs

```bash
# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f heroes_api
docker compose logs -f potpie_api
docker compose logs -f potpie_celery
```

## 🔒 Security

### API Keys

- Store AI provider API keys in `potpie/.env`
- Use environment variables for production
- Never commit API keys to version control

### Network Security

- Services communicate through Docker network
- External access only through defined ports
- Use reverse proxy for production deployment

## 🐛 Troubleshooting

### Common Issues

1. **Port Conflicts**:
   ```bash
   # Check port usage
   lsof -i :8000
   lsof -i :8001
   ```

2. **Database Connection Issues**:
   ```bash
   # Check database status
   docker compose ps
   docker compose logs postgres
   ```

3. **Neo4j Connection Issues**:
   ```bash
   # Check Neo4j status
   curl http://localhost:7474
   docker compose logs neo4j
   ```

### Reset Everything

```bash
# Stop and clean all services
./stop_heroes_with_potpie.sh
docker system prune -f
docker volume prune -f

# Start fresh
./start_heroes_with_potpie.sh
```

## 📚 Additional Resources

- [Potpie Documentation](https://docs.potpie.ai/)
- [Heroes Platform Documentation](./README.md)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the integration
5. Submit a pull request

## 📄 License

This integration follows the same license as Heroes Platform and Potpie.

---

**Version**: 1.0.0  
**Last Updated**: December 2024  
**Status**: Active Development
