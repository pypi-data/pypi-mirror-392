# chora-orchestration

[![PyPI version](https://badge.fury.io/py/chora-orchestration.svg)](https://pypi.org/project/chora-orchestration/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MCP server orchestration CLI and HTTP server for managing Docker-based MCP services.

## Features

- **Dual Mode Operation**: CLI commands + MCP HTTP server + stdio bridge
- **Docker Integration**: Manages containers via Docker SDK
- **Smart Path Resolution**: Auto-discovers registry.yaml with 5-tier fallback hierarchy
- **Cross-Platform**: Consistent behavior on Windows, Linux, and macOS
- **Auto-Discovery**: Reads registry.yaml for server definitions
- **Health Monitoring**: Tracks container and endpoint health
- **Log Access**: View container logs for debugging
- **Gateway Proxying**: Unified MCP endpoint exposing both orchestration and gateway tools

## Installation

### From PyPI (Recommended)

```bash
pip install chora-orchestration
```

**Latest version**: [0.3.1](https://pypi.org/project/chora-orchestration/) (published on PyPI)

**What's new in 0.3.1**:
- Fixed startup initialization bug in DockerOrchestrator
- Improved async/sync compatibility in startup sequencing
- All 74 tests passing with 65% coverage
- SAP-047 template compliance verified at 100% (22/22 requirements)
- CLI fully functional across Windows, Linux, and macOS

### From Source (Development)

```bash
git clone https://github.com/liminalcommons/chora-orchestration.git
cd chora-orchestration
poetry install
```

## Usage

### CLI Mode

```bash
# Initialize ecosystem
chora-orch init

# Deploy server
chora-orch deploy n8n

# List servers
chora-orch list

# Check health
chora-orch health manifest

# View logs
chora-orch logs n8n --tail 50

# Stop server
chora-orch stop n8n

# Get status
chora-orch status
```

### MCP Server Mode

```bash
# Start MCP HTTP server
chora-orch-serve --port 8090
```

Then access tools via HTTP:
- `POST /tools/init`
- `POST /tools/deploy`
- `POST /tools/list`
- `POST /tools/health`
- `POST /tools/logs`
- `POST /tools/stop`
- `POST /tools/status`

## Development

```bash
# Run tests
poetry run pytest -v

# Run with coverage
poetry run pytest --cov=chora_mcp_orchestration --cov-report=term-missing

# Type check (if mypy added)
poetry run mypy src/
```

## Documentation

- [Requirements](docs/ORCHESTRATION-REQUIREMENTS.md) - Full specification
- [Bootstrap Guide](docs/user-docs/how-to/01-bootstrap-ecosystem-stdio.md) - Quick start with stdio bridge
- [PyPI Publishing Guide](docs/dev-docs/pypi-publishing-guide.md) - Publishing workflow
- [CLI Scenarios](tests/features/orchestration_cli.feature) - BDD scenarios
- [MCP Server Scenarios](tests/features/orchestration_mcp_server.feature) - HTTP tool scenarios
- [CHANGELOG](CHANGELOG.md) - Version history

## License

MIT
