# MCP Search Server

A Model Context Protocol (MCP) server that enables searching and discovering existing MCP servers from the official GitHub repository.

**Author:** Krzysztof Kućmierz  
**Email:** <krzysztof.kucmierz@artificiuminformatica.pl>

## Features

- **🔍 Search MCP Servers**: Find relevant MCP servers by name, description, or category
- **🌐 Dynamic Data**: Live scraping from <https://github.com/modelcontextprotocol/servers>
- **⚡ Fast & Cached**: Configurable caching (default: 6 hours) for optimal performance

## Installation

### Prerequisites

Install [uv](https://docs.astral.sh/uv/) (fast Python package manager):

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

### Setup Project

```bash
git clone <repository-url>
cd <repository-name>
uv sync
```

## Usage

### Start the MCP Server

```bash
# SSE mode (recommended)
uv run python mcp_server.py --sse

# Custom port and cache timeout
uv run python mcp_server.py --sse --port 8001 --cache-timeout 3600

# Stdio mode (for MCP clients)
uv run python mcp_server.py
```

### To add this MCP server to VSCode

Create mcp.json file containing:

```json
{
"servers": {
    "Search MCP server": {
        "url": "http://127.0.0.1:8000/sse",
        "type": "http"
    }
},
"inputs": []
}
```

#### Command Line Options

- `--sse`: Start in SSE mode instead of stdio mode
- `--port PORT`: Port for SSE mode (default: 8000)
- `--cache-timeout SECONDS`: Cache timeout in seconds (default: 21600 = 6 hours)

### Available Tools

- **`search_mcp_servers(query, category)`** - Search for MCP servers
- **`get_mcp_server_categories()`** - List all available categories

### Available Resources

- **`mcp://servers/list`** - Formatted list of all MCP servers
- **`mcp://servers/categories`** - Information about server categories

## Development

```bash
# Code quality
uv run ruff check --fix .
uv run mypy mcp_server.py

# Run server
uv run python mcp_server.py --sse
```

### Debugging with MCP Inspector

```bash
npx @modelcontextprotocol/inspector uv run python mcp_server.py --sse
```

## Links

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Servers Repository](https://github.com/modelcontextprotocol/servers)
- [FastMCP Framework](https://gofastmcp.com/)
