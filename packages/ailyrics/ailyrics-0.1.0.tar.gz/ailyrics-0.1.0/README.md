# Lyrics - Super connection middleware about multi-agent and skills

Lyrics is a bash command proxy server designed for AI Agents to securely execute Agent Skills commands in containerized environments.

## 🎯 Why Lyrics?

Agent Skills need a secure bash environment to:
- Execute document processing (PDF, Excel, etc.)
- Run Python scripts and utilities
- Manage file system operations
- Maintain persistent shell sessions

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│        FastAPI Server               │
│  • REST API (/api/v1/*)             │
│  • Health checks                    │
├─────────────────────────────────────┤
│       Service Layer                 │
│  • Business logic                   │
│  • Thread pool management           │
├─────────────────────────────────────┤
│  Command Processing  │ File System  │
│  • Security validation│ Path resolve │
│  • Shell sessions     │ Access control│
├─────────────────────────────────────┤
│        Agent Skills (/skills)        │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│  │   pdf   │ │  xlsx   │ │ Custom  │ │
│  └─────────┘ └─────────┘ └─────────┘ │
└─────────────────────────────────────┘
```

### Key Components
- **CommandParser**: Validates bash commands with security checks
- **CommandExecutor**: Executes commands using persistent shell sessions
- **PathResolver**: Resolves skill/workspace paths
- **PathValidator**: Enforces security policies

## 🚀 Quick Start

### Installation

#### Option 1: Install from PyPI (Recommended)

```bash
pip install ailyrics
```

#### Option 2: Install from Source (Development)
```bash
# Clone project
git clone https://github.com/your-org/lyrics.git
cd lyrics

# Install dependencies
uv sync
```

### Start Server
```bash
# PyPI installation
python -m lyrics.server --host 0.0.0.0 --port 8870

# Source development
uv run python -m lyrics.server --host 0.0.0.0 --port 8870

# Docker mode (source only)
make docker-up
```

### Verify Installation
```bash
curl http://localhost:8870/api/v1/health
# Returns: {"status": "healthy", "service": "lyrics", "api_version": "v1"}
```

## 📡 Core API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | Health check |
| `POST` | `/api/v1/bash/execute` | Execute bash commands |
| `GET` | `/api/v1/skills` | List all skills |
| `GET` | `/api/v1/skills/{name}` | Get specific skill |

### Execute Commands
```bash
curl -X POST http://localhost:8870/api/v1/bash/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "ls -la /skills/public"}'
```

## 🔧 Agent Skills

### Skill Structure
```
skill-name/
├── SKILL.md          # YAML metadata + instructions (required)
├── scripts/          # Utility scripts (optional)
├── reference/        # Reference docs (optional)
└── data/            # Data files (optional)
```

### YAML Frontmatter Format
```yaml
---
name: pdf-processing
description: PDF toolkit for text extraction, form filling, etc.
license: MIT
---

# PDF Processing Guide
...detailed content...
```

### Available Skills
- **pdf**: PDF document processing (text extraction, form filling)
- **xlsx**: Excel spreadsheet processing (formulas, data analysis)

## ⚠️ Security Constraints

The system blocks dangerous patterns for security:
- Shell operators: `;`, `&&`, `||`, `|`, `$`, `` ` ``, `>`, `<`, `&` ❌
- Path traversal: `../../../etc/passwd` ❌
- Command injection attempts ❌

**Alternative: Use Python**
```bash
# ✅ Correct way
python3 -c "with open('file.txt', 'w') as f: f.write('content')"
```

## 🐍 Python Client Example

```python
import asyncio
import httpx

async def main():
    async with httpx.Client() as client:
        # Health check
        health = await client.get("http://localhost:8870/api/v1/health")
        print(f"Service status: {health.json()['status']}")

        # Execute command
        result = await client.post(
            "http://localhost:8870/api/v1/bash/execute",
            json={"command": "echo 'Hello Lyrics!'"}
        )
        print(f"Output: {result.json()['stdout']}")

asyncio.run(main())
```

## 🛠️ Development

### Project Structure
```
src/lyrics/
├── server.py          # FastAPI main server
├── bash/              # Bash command processing
├── filesystem/        # File system operations
└── commands/          # Command handlers
```

### Running Tests
```bash
# Full integration tests (recommended)
make docker-test

# Unit tests
make test
```

### Code Quality
```bash
make fmt          # Format code
make check        # Check code quality
```

## 📊 Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SKILLS_PATH` | `/skills` | Skills directory |
| `WORKSPACE_PATH` | `/workspace` | Working directory |
| `LOG_LEVEL` | `INFO` | Log level |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8870` | Server port |

## 🤝 Contributing

1. Fork the project
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Create Pull Request

## 📄 License

MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built for the Agent Skills ecosystem** 🚀