"""
MCP Search Server - Search and discover existing MCP servers from the official repo.

This server provides search functionality for the comprehensive list of MCP servers
available at https://github.com/modelcontextprotocol/servers. It helps users discover
relevant MCP servers for their needs and provides detailed information about each
server.
"""

import argparse
import logging
import time
from typing import Any

import httpx
from bs4 import BeautifulSoup, Tag
from fastmcp import FastMCP

# Create the FastMCP server instance
mcp = FastMCP("MCP Search Server")

# Module logger
logger = logging.getLogger(__name__)


async def _find_section_header(readme_content: Tag, section_name: str) -> Tag | None:
    """Find a section header by name."""
    # Look for exact matches and partial matches
    for heading in readme_content.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        if isinstance(heading, Tag):
            heading_text = heading.get_text().lower()
            section_lower = section_name.lower()
            # More precise matching - look for the exact phrase in the heading
            if section_lower in heading_text and (
                (
                    section_lower == "community servers"
                    and "community servers" in heading_text
                )
                or (
                    section_lower == "official integrations"
                    and "official integrations" in heading_text
                )
            ):
                return heading
    return None


def _extract_server_info(li: Tag, category_type: str) -> dict[str, Any] | None:
    """Extract server information from a list item."""
    link = li.find("a", href=True)
    if not isinstance(link, Tag):
        return None

    href_val = link.get("href")
    if not href_val:
        return None

    href = str(href_val)
    name = link.get_text(strip=True)

    # Extract description from the text after the link
    # Format: "Name - Description"
    li_text = li.get_text(strip=True)
    description = ""
    if " - " in li_text:
        parts = li_text.split(" - ", 1)
        if len(parts) > 1:
            description = parts[1].strip()

    if not description:
        description = f"MCP server: {name}"

    # Build full URL if relative
    full_url = href
    if href.startswith("/"):
        full_url = f"https://github.com{href}"

    return {
        "name": name,
        "description": description,
        "url": full_url,
        "category": f"{category_type} Server",
    }


def _get_section_bounds(
    all_elements: list, section_header: Tag
) -> tuple[int, int | None]:
    """Get the start and end indices for a section."""
    try:
        section_index = all_elements.index(section_header)
    except ValueError:
        return -1, None

    # Find the next h2 header after our section
    next_h2_index = None
    for i, element in enumerate(all_elements[section_index + 1 :], section_index + 1):
        if isinstance(element, Tag) and element.name == "h2":
            next_h2_index = i
            break

    return section_index, next_h2_index


def _is_valid_github_link(href: str, text: str) -> bool:
    """Check if a link is a valid GitHub repository link."""
    return (
        "github.com" in href
        and not href.startswith("#")
        and bool(text)
        and len(text) > 2
    )


def _build_server_entry(text: str, href: str, category_type: str) -> dict[str, Any]:
    """Build a server entry dictionary."""
    # Build full URL if relative
    full_url = href if not href.startswith("/") else f"https://github.com{href}"

    return {
        "name": text,
        "description": f"MCP server: {text}",
        "url": full_url,
        "category": f"{category_type} Server",
    }


async def _parse_server_section(
    readme_content: Tag, section_name: str, category_type: str
) -> list[dict[str, Any]]:
    """Parse a specific server section (Official Integrations or Community Servers)."""
    servers: list[dict[str, Any]] = []

    section_header = await _find_section_header(readme_content, section_name)
    if not section_header:
        return servers

    # Get all elements in document order
    all_elements = list(readme_content.descendants)

    # Find the bounds of this section
    section_index, next_h2_index = _get_section_bounds(all_elements, section_header)
    if section_index == -1:
        return servers

    # Look for ul elements between our section and the next h2
    relevant_elements = all_elements[section_index + 1 : next_h2_index]

    # Extract GitHub links from ul elements in this range
    for element in relevant_elements:
        if not (isinstance(element, Tag) and element.name == "ul"):
            continue

        links = element.find_all("a", href=True)
        for link in links:
            if not isinstance(link, Tag):
                continue

            href_val = link.get("href")
            text = link.get_text(strip=True)

            if href_val:
                href = str(href_val)
                if _is_valid_github_link(href, text):
                    servers.append(_build_server_entry(text, href, category_type))

    return servers


async def fetch_mcp_servers_from_github() -> list[dict[str, Any]]:
    """Fetch MCP servers data from GitHub repository."""
    url = "https://github.com/modelcontextprotocol/servers"

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            servers = []

            # Find the README content
            readme_content = soup.find("article", class_="markdown-body")
            if not readme_content:
                # Fallback to looking for any article tag
                readme_content = soup.find("article")

            if readme_content and isinstance(readme_content, Tag):
                # Parse both "Official Integrations" and "Community Servers" categories
                servers.extend(
                    await _parse_server_section(
                        readme_content, "Official Integrations", "Official"
                    )
                )
                servers.extend(
                    await _parse_server_section(
                        readme_content, "Community Servers", "Community"
                    )
                )

        except Exception:
            logger.exception("Error fetching servers from GitHub")
            # Return fallback servers if scraping fails
            return []
        else:
            return servers  # Return all servers for comprehensive search


# Server cache manager
class ServerCache:
    def __init__(self, cache_timeout: int = 21600) -> None:  # Default 6 hours
        self.cache: list[dict[str, Any]] | None = None
        self.timestamp: float | None = None
        self.duration = cache_timeout  # Configurable cache timeout

    async def get_data(self) -> list[dict[str, Any]]:
        """Get servers data with caching."""
        current_time = time.time()

        # Check if cache is valid
        if (
            self.cache is not None
            and self.timestamp is not None
            and current_time - self.timestamp < self.duration
        ):
            return self.cache

        # Fetch fresh data
        try:
            servers = await fetch_mcp_servers_from_github()
            self.cache = servers
            self.timestamp = current_time
        except Exception:
            logger.exception("Failed to fetch servers")
            # Return cached data if available, otherwise empty list
            return self.cache if self.cache is not None else []
        else:
            return servers


class CacheManager:
    """Singleton cache manager to avoid global variables."""

    _instance: "CacheManager | None" = None
    _cache: ServerCache | None = None

    def __new__(cls) -> "CacheManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def set_timeout(self, timeout: int) -> None:
        """Set the cache timeout."""
        self._cache = ServerCache(cache_timeout=timeout)

    def get_cache(self) -> ServerCache:
        """Get the cache instance."""
        if self._cache is None:
            self._cache = ServerCache()  # Default timeout
        return self._cache


# Global cache manager instance
cache_manager = CacheManager()


async def get_servers_data() -> list[dict[str, Any]]:
    """Get servers data with caching."""
    return await cache_manager.get_cache().get_data()


@mcp.tool()
async def search_mcp_servers(query: str, category: str = "all") -> dict[str, Any]:
    """Search for existing MCP servers from the official GitHub repository.

    Args:
        query: Search query to find relevant MCP servers (searches name,
               description, and category)
        category: Filter by category (all, development, database,
                  productivity, automation, cloud, security, etc.)    Returns:
        Search results with matching MCP servers and their details
    """
    servers_data = await get_servers_data()

    # Convert query to lowercase for case-insensitive search
    query_lower = query.lower()
    category_lower = category.lower()

    # Filter servers based on query and category
    matching_servers = []

    for server in servers_data:
        # Check if query matches name, description, or category
        matches_query = (
            query_lower in server["name"].lower()
            or query_lower in server["description"].lower()
            or query_lower in server["category"].lower()
        )

        # Check category filter
        matches_category = (
            category_lower == "all" or category_lower in server["category"].lower()
        )

        if matches_query and matches_category:
            matching_servers.append(server)

    return {
        "query": query,
        "category_filter": category,
        "total_results": len(matching_servers),
        "servers": matching_servers,
        "search_suggestions": (
            _get_search_suggestions(query) if len(matching_servers) == 0 else None
        ),
    }


async def _get_server_categories_data() -> dict[str, Any]:
    """Internal function to get server categories data."""
    servers_data = await get_servers_data()
    categories: dict[str, list] = {}

    for server in servers_data:
        category = server["category"]
        if category not in categories:
            categories[category] = []
        categories[category].append({"name": server["name"]})

    return {
        "categories": categories,
        "total_categories": len(categories),
        "total_servers": len(servers_data),
        "category_counts": {cat: len(servers) for cat, servers in categories.items()},
    }


@mcp.tool()
async def get_mcp_server_categories() -> dict[str, Any]:
    """Get all available MCP server categories for filtering.

    Returns:
        List of available categories
    """
    return await _get_server_categories_data()


def _get_search_suggestions(query: str) -> list[str]:
    """Generate search suggestions when no results are found."""

    common_terms = [
        "github",
        "database",
        "postgres",
        "mongodb",
        "redis",
        "docker",
        "kubernetes",
        "aws",
        "google",
        "slack",
        "notion",
        "jupyter",
        "browser",
        "automation",
        "api",
        "productivity",
        "development",
    ]

    # Find similar terms
    suggestions = []
    query_lower = query.lower()

    for term in common_terms:
        if query_lower in term or term in query_lower:
            suggestions.append(term)

    # Add category suggestions
    categories = [
        "development",
        "database",
        "productivity",
        "automation",
        "cloud",
        "security",
    ]
    suggestions.extend([cat for cat in categories if cat not in suggestions])

    return suggestions[:5]


@mcp.resource("mcp://servers/list")
async def get_all_mcp_servers() -> str:
    """Get a formatted list of all available MCP servers.

    Returns:
        Formatted text listing all MCP servers with categories
    """
    servers_data = await get_servers_data()

    # Group servers by category
    servers_by_category: dict[str, list] = {}
    for server in servers_data:
        category = server["category"]
        if category not in servers_by_category:
            servers_by_category[category] = []
        servers_by_category[category].append(server)

    # Format output
    output = "# Available MCP Servers\n\n"
    output += f"Total servers: {len(servers_data)}\n"
    output += f"Categories: {len(servers_by_category)}\n\n"

    for category, servers in sorted(servers_by_category.items()):
        output += f"## {category} ({len(servers)} servers)\n\n"

        for server in servers:
            output += f"**{server['name']}** ({server['category']})\n"
            output += f"- Description: {server['description']}\n"
            output += f"- URL: {server['url']}\n\n"

    output += "\n---\n"
    output += (
        "For more servers, visit: https://github.com/modelcontextprotocol/servers\n"
    )
    output += "To contribute your own server, submit a PR to the official repository."

    return output


@mcp.resource("mcp://servers/categories")
async def get_categories_resource() -> str:
    """Get information about MCP server categories.

    Returns:
        Formatted information about available categories
    """

    categories_info = await _get_server_categories_data()

    output = "# MCP Server Categories\n\n"

    for category, servers in categories_info["categories"].items():
        output += f"## {category}\n"
        output += f"Servers in this category: {len(servers)}\n\n"

        for server in servers[:3]:  # Show first 3 servers
            output += f"- {server['name']}\n"

        if len(servers) > 3:
            output += f"- ... and {len(servers) - 3} more\n"

        output += "\n"

    return output


def main() -> None:
    """Main entry point for the MCP server."""
    parser = argparse.ArgumentParser(description="MCP Search Server")
    parser.add_argument(
        "--sse", action="store_true", help="Start in SSE mode instead of stdio mode"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port for SSE mode (default: 8000)"
    )
    parser.add_argument(
        "--cache-timeout",
        type=int,
        default=21600,  # 6 hours in seconds
        help="Cache timeout in seconds (default: 21600 = 6 hours)",
    )

    args = parser.parse_args()

    # Initialize server cache with configured timeout
    cache_manager.set_timeout(args.cache_timeout)

    timeout_hours = args.cache_timeout / 3600
    cache_msg = (
        f"Cache timeout: {args.cache_timeout} seconds " f"({timeout_hours:.1f} hours)"
    )

    if args.sse:
        # Start in SSE mode on specified port
        print(f"Starting MCP server in SSE mode on port {args.port}")
        print(cache_msg)
        mcp.run(transport="sse", port=args.port)
    else:
        # Default stdio mode for MCP clients
        print("Starting MCP server in stdio mode")
        print(cache_msg)
        mcp.run()


if __name__ == "__main__":
    main()
