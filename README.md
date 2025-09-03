# Search MCP Server

A Model Context Protocol (MCP) server that enables searching and discovering existing MCP servers from the official GitHub repository.

**Author:** Krzysztof Kućmierz  
**Email:** <krzysztof.kucmierz@artificiuminformatica.pl>

## Features

- **Search MCP Servers**: Find relevant MCP servers by name, description, or category
- **Dynamic Data**: Live scraping from <https://github.com/modelcontextprotocol/servers>
- **Fast & Cached**: Configurable caching (default: 6 hours) for optimal performance

## Installation

### Prerequisites

Install [uv](https://docs.astral.sh/uv/) (fast Python package manager):

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

### Setup Project

```bash
git clone https://github.com/krzysztofkucmierz/search-mcp-server.git
cd search-mcp-server
uv sync
```

## Usage

### Start the MCP Server

Note: the server script `mcp_server.py` lives in the repo root — run it directly as shown below. If you install the package, the `mcp-search-server` entry point (configured in `pyproject.toml`) will also be available.

```bash
# SSE mode (recommended) — exposes an HTTP/SSE endpoint
uv run python mcp_server.py --sse

# Custom port and cache timeout
uv run python mcp_server.py --sse --port 8001 --cache-timeout 3600

# Stdio mode (for MCP clients that spawn the process)
uv run python mcp_server.py
```

Small note: use `--sse` when you want other apps to connect over HTTP; omit it to run in stdio mode where the client must start the process.

### To add this MCP server to VSCode

If you run the server with `--sse`, point your client (or VSCode MCP extension) to the SSE URL (example: `http://127.0.0.1:8000/sse`). The following minimal JSON shows the URL form (only valid when using `--sse`):

```json
{
    "servers": {
        "Search MCP server": { "url": "http://127.0.0.1:8000/sse", "type": "http" }
    },
    "inputs": []
}
```

#### Command Line Options

- `--sse`: Start in SSE mode instead of stdio mode
- `--port PORT`: Port for SSE mode (default: 8000)
- `--cache-timeout SECONDS`: Cache timeout in seconds (default: 21600 = 6 hours)

### Tools & Resources

- Tools: `search_mcp_servers(query, category)`, `get_mcp_server_categories()`
- Resources: `mcp://servers/list`, `mcp://servers/categories`

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
