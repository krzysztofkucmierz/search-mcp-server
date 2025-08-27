# MCP server requirements

Last upated: Aug, 27, 2025

## Functional requirements

1. Provide a Tool to search for existing MCP servers from the official GitHub repository.
2. Provide a Tool to get all available MCP server categories for filtering.
3. Return output as structured data.

## Web crawling requirements

1. List of MCP servers are stored on <https://github.com/modelcontextprotocol/servers> web page in `Third-Party Servers` section
2. Do NOT scrape any content of the web page outside of `Third-Party Servers` section
3. There are two categories of MCP servers: `Official Integrations` and `Community Servers`
4. Each MCP server entry on theis web page consists of a web link and its name following with short description of the MCP server. Example: `<a href="https://github.com/21st-dev/magic-mcp">21st.dev Magic</a> - Create crafted UI components inspired by the best 21st.dev design engineers.`
