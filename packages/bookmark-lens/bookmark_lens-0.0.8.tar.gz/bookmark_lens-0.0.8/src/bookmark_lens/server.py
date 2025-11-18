"""
MCP server for bookmark-lens.

Provides tools for saving, searching, and managing bookmarks with semantic search.
"""

import asyncio
import argparse
import logging
from typing import Optional

from fastmcp import FastMCP, Context
from fastmcp.server.middleware import Middleware, MiddlewareContext

from .config import load_config, Config
from .database.duckdb_client import DuckDBClient
from .database.lancedb_client import LanceDBClient
from .services.content_fetcher import ContentFetcher
from .services.embedding_service import EmbeddingService
from .services.bookmark_service import BookmarkService
from .services.search_service import SearchService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

mcp = FastMCP("bookmark-lens")


# Middleware to extract user context
class UserContextMiddleware(Middleware):
    """Extract user ID from HTTP headers or default to 'dev-user'."""

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        from fastmcp.server.dependencies import get_http_request
        
        user_id = "dev-user"
        try:
            request = get_http_request()
            user_id = request.headers.get("X-User-Id", "dev-user")
        except:
            pass
        
        context.fastmcp_context.set_state("user_id", user_id)
        logger.info(f"🔐 Middleware set user_id: {user_id}")
        
        return await call_next(context)


def extract_user_id(context: Context) -> str:
    """Extract user_id from context state."""
    user_id = context.get_state("user_id") or "dev-user"
    logger.info(f"🔍 Tool got user_id: {user_id}")
    return user_id


# Global service instances (initialized on startup)
config: Optional[Config] = None
duckdb_client: Optional[DuckDBClient] = None
lancedb_client: Optional[LanceDBClient] = None
bookmark_service: Optional[BookmarkService] = None
search_service: Optional[SearchService] = None
content_fetcher: Optional[ContentFetcher] = None


@mcp.prompt()
def bookmark_search_guide() -> str:
    """Guide for using bookmark-lens effectively, including natural language date parsing."""
    return """You are a bookmark management assistant with access to the bookmark-lens MCP server.

IMPORTANT: You HAVE the ability to manage bookmarks through the available tools. When users ask to save, search, or manage bookmarks, USE THE TOOLS.

Your capabilities:
1. Save bookmarks - Use save_bookmark when users say "save", "bookmark", "add to bookmarks", "remember this"
2. Search bookmarks - Use search_bookmarks when users say "find", "search", "show me bookmarks"
3. Get bookmark details - Use get_bookmark to retrieve full information
4. Update bookmarks - Use update_bookmark to modify notes or tags
5. Delete bookmarks - Use delete_bookmark to remove bookmarks
6. List tags - Use list_tags to show all available tags
7. Get statistics - Use get_bookmark_stats for analytics
8. Get content - Use get_bookmark_content to fetch and summarize articles

Common User Requests:
- "Save this URL" → Use save_bookmark
- "Bookmark this page" → Use save_bookmark
- "Add to my bookmarks" → Use save_bookmark
- "Find bookmarks about X" → Use search_bookmarks
- "Show me my bookmarks" → Use search_bookmarks with broad query
- "Summarize this bookmark" → Use get_bookmark_content then summarize

Date Conversion Rules:
- "today" → current date at 00:00:00Z
- "yesterday" → current date - 1 day at 00:00:00Z
- "last week" → current date - 7 days at 00:00:00Z
- "last month" → current date - 30 days at 00:00:00Z
- "this week" → 7 days ago to now
- Always use ISO 8601 format: "2024-11-14T00:00:00Z"
- For date ranges, set from_date to the start and to_date to now (or omit to_date)

Search Workflow:
1. Parse user query for filters (dates, domain, tags)
2. Extract semantic search text (the "what" they're looking for)
3. Convert any natural language dates to ISO format
4. Call search_bookmarks with proper parameters
5. Interpret similarity scores (>0.7 = highly relevant, >0.5 = relevant, <0.5 = weak match)
6. Present results clearly with titles and relevance

Filter Extraction Examples:
- "bookmarks from last week" → from_date = 7 days ago
- "find articles about AI from github.com" → query="articles about AI", domain="github.com"
- "show me bookmarks tagged as python" → query="python", tags=["python"]
- "bookmarks I saved yesterday about databases" → query="databases", from_date = yesterday

Rules:
- Always convert natural language dates to ISO format yourself (don't ask the user)
- Use semantic search for "find bookmarks about X" (the query parameter)
- Use domain filter for "from github.com" or "on example.com"
- Use tag filter for "tagged as X" or "with tag Y"
- Combine filters when appropriate
- If search returns no results, suggest a broader query or different filters
- When saving bookmarks, encourage users to add notes (improves search relevance)
- Similarity scores help gauge relevance - mention when results are highly relevant

Workflow Examples:

Example 1 - Save with context:
User: "Save https://example.com/article, this is about machine learning"
You: Call save_bookmark with url and note="this is about machine learning"

Example 2 - Search with date:
User: "Find bookmarks from last week about Python"
You: Calculate from_date (7 days ago), call search_bookmarks with query="Python", from_date="2024-11-07T00:00:00Z"

Example 3 - Search with domain:
User: "Show me GitHub bookmarks about React"
You: Call search_bookmarks with query="React", domain="github.com"

Example 4 - Update bookmark:
User: "Add tag 'tutorial' to bookmark abc123"
You: Call update_bookmark with id="abc123", tags=["tutorial"], tag_mode="append"
"""


@mcp.tool()
async def save_bookmark(url: str, note: Optional[str] = None, tags: Optional[list[str]] = None, context: Context = None) -> str:
    """Save a bookmark to the user's bookmark collection.

IMPORTANT: Use this tool whenever the user asks to:
- "Save this URL"
- "Bookmark this"
- "Add to bookmarks"
- "Remember this page"
- Or any similar request to save a URL

After saving, consider helping the user by:
1. Calling get_bookmark_content(id) to fetch the article
2. Summarizing the content for them
3. Calling update_bookmark(id, note=summary) to save the summary

This provides a helpful summary without requiring an API key.

Args:
    url: The URL to bookmark
    note: Optional note explaining why you saved this or context
    tags: Optional tags to categorize this bookmark

Returns:
    Success message with bookmark ID
    """
    from .handlers import handle_save_bookmark

    # Extract user_id from context
    user_id = extract_user_id(context)

    arguments = {"url": url}
    if note is not None:
        arguments["note"] = note
    if tags is not None:
        arguments["tags"] = tags

    result = await handle_save_bookmark(arguments, bookmark_service, user_id)
    return result[0].text


@mcp.tool()
async def search_bookmarks(
    query: str,
    domain: Optional[str] = None,
    tags: Optional[list[str]] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = 10,
    context: Context = None
) -> str:
    """Search the user's bookmark collection using semantic search.

IMPORTANT: Use this tool whenever the user asks to:
- "Find bookmarks about..."
- "Search my bookmarks for..."
- "Show me bookmarks..."
- "Do I have any bookmarks about..."
- Or any similar request to find saved bookmarks

Supports semantic search (meaning-based) with optional filters for domain, tags, and dates.

Args:
    query: What to search for (semantic search)
    domain: Filter by domain (e.g., 'github.com')
    tags: Filter by tags
    from_date: Filter bookmarks after this date (ISO 8601 format: '2024-11-14T00:00:00Z')
    to_date: Filter bookmarks before this date (ISO 8601 format: '2024-11-14T23:59:59Z')
    limit: Max results to return (1-100)

Returns:
    Search results with bookmark details
    """
    from .handlers import handle_search_bookmarks

    # Extract user_id from context
    user_id = extract_user_id(context)

    arguments = {"query": query, "limit": limit}
    if domain is not None:
        arguments["domain"] = domain
    if tags is not None:
        arguments["tags"] = tags
    if from_date is not None:
        arguments["from_date"] = from_date
    if to_date is not None:
        arguments["to_date"] = to_date

    result = await handle_search_bookmarks(arguments, search_service, user_id)
    return result[0].text


@mcp.tool()
async def get_bookmark(id: str, context: Context = None) -> str:
    """Get full details about a specific bookmark by ID.

Args:
    id: The bookmark ID

Returns:
    Full bookmark details
    """
    from .handlers import handle_get_bookmark

    # Extract user_id from context
    user_id = extract_user_id(context)

    result = await handle_get_bookmark({"id": id}, bookmark_service, user_id)
    return result[0].text


@mcp.tool()
async def update_bookmark(
    id: str,
    note: Optional[str] = None,
    tags: Optional[list[str]] = None,
    tag_mode: str = "replace",
    context: Context = None
) -> str:
    """Update note and/or tags for an existing bookmark.

Args:
    id: The bookmark ID
    note: New note (replaces existing)
    tags: Tags to add or replace
    tag_mode: Whether to 'replace' or 'append' tags

Returns:
    Success message
    """
    from .handlers import handle_update_bookmark

    # Extract user_id from context
    user_id = extract_user_id(context)

    arguments = {"id": id, "tag_mode": tag_mode}
    if note is not None:
        arguments["note"] = note
    if tags is not None:
        arguments["tags"] = tags

    result = await handle_update_bookmark(arguments, bookmark_service, user_id)
    return result[0].text


@mcp.tool()
async def delete_bookmark(id: str, context: Context = None) -> str:
    """Delete a bookmark and all its associated data.

Args:
    id: The bookmark ID to delete

Returns:
    Success message
    """
    from .handlers import handle_delete_bookmark

    # Extract user_id from context
    user_id = extract_user_id(context)

    result = await handle_delete_bookmark({"id": id}, bookmark_service, user_id)
    return result[0].text


@mcp.tool()
async def list_tags(context: Context = None) -> str:
    """List all tags with their usage counts.

Returns:
    List of tags with counts
    """
    from .handlers import handle_list_tags

    # Extract user_id from context
    user_id = extract_user_id(context)

    result = await handle_list_tags({}, duckdb_client, user_id)
    return result[0].text


@mcp.tool()
async def get_bookmark_stats(
    stat_type: str = "total",
    domain: Optional[str] = None,
    topic: Optional[str] = None,
    tags: Optional[list[str]] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = 10,
    context: Context = None
) -> str:
    """Get statistics about your bookmark collection with optional filters.

Args:
    stat_type: Type of statistics: 'total' (count), 'by_domain' (top domains),
               'by_topic' (topic breakdown), 'by_tag' (tag distribution),
               'by_date' (activity over time)
    domain: Filter by domain (e.g., 'github.com')
    topic: Filter by topic
    tags: Filter by tags
    from_date: Filter bookmarks after this date (ISO 8601 format)
    to_date: Filter bookmarks before this date (ISO 8601 format)
    limit: For 'by_*' stats, limit to top N results (default: 10)

Returns:
    Statistics data
    """
    from .handlers import handle_get_bookmark_stats

    # Extract user_id from context
    user_id = extract_user_id(context)

    arguments = {"stat_type": stat_type, "limit": limit}
    if domain is not None:
        arguments["domain"] = domain
    if topic is not None:
        arguments["topic"] = topic
    if tags is not None:
        arguments["tags"] = tags
    if from_date is not None:
        arguments["from_date"] = from_date
    if to_date is not None:
        arguments["to_date"] = to_date

    result = await handle_get_bookmark_stats(arguments, duckdb_client, user_id)
    return result[0].text


@mcp.tool()
async def get_bookmark_content(id: str, context: Context = None) -> str:
    """Get the full content of a bookmark in Markdown format.

Use this tool when the user wants to:
- Read the full article content
- Get a summary of the bookmark (you will summarize the returned content)
- Analyze or discuss the bookmark content in detail
- Quote specific parts of the article
- Get fresh content from the URL

After calling this tool, YOU should summarize or analyze the content based on what the user asked.

Args:
    id: The bookmark ID

Returns:
    Bookmark content in Markdown format
    """
    from .handlers import handle_get_bookmark_content

    logger.info(f"🔧 TOOL CALLED: get_bookmark_content(id={id})")
    
    # Extract user_id from context
    user_id = extract_user_id(context)

    result = await handle_get_bookmark_content({"id": id}, bookmark_service, content_fetcher, user_id)
    
    response_text = result[0].text
    logger.info(f"📤 TOOL RESPONSE: {len(response_text)} characters")
    logger.info(f"📄 Content preview: {response_text[:200]}")
    
    return response_text


def initialize_services():
    """Initialize database and services."""
    global config, duckdb_client, lancedb_client, bookmark_service, search_service, content_fetcher

    logger.info("Initializing bookmark-lens MCP server...")

    config = load_config()
    logger.info(f"Config loaded - DB: {config.db_path}")

    duckdb_client = DuckDBClient(config.db_path)
    duckdb_client.initialize_schema()
    logger.info("DuckDB initialized")

    lancedb_client = LanceDBClient(config.lance_path, config.embedding_dimension)
    lancedb_client.initialize_table()
    logger.info("LanceDB initialized")

    content_fetcher = ContentFetcher(config)
    embedding_service = EmbeddingService(config)
    logger.info("Services initialized")

    bookmark_service = BookmarkService(
        config,
        duckdb_client,
        lancedb_client,
        content_fetcher,
        embedding_service
    )

    search_service = SearchService(
        config,
        duckdb_client,
        lancedb_client,
        embedding_service
    )
    logger.info("Bookmark and search services initialized")


def run():
    """Entry point for console script (stdio mode by default)."""
    parser = argparse.ArgumentParser(description="Bookmark Lens MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport mode: stdio (default) or http"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP server (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for HTTP server (default: 127.0.0.1)"
    )

    args = parser.parse_args()

    # Initialize services before starting server
    initialize_services()
    
    # Add user context middleware for multi-user support
    mcp.add_middleware(UserContextMiddleware())

    if args.transport == "stdio":
        logger.info("Starting MCP server in stdio mode...")
        mcp.run(transport="stdio")
    else:
        logger.info(f"Starting MCP server in HTTP mode on {args.host}:{args.port}...")
        mcp.run(transport="http", host=args.host, port=args.port)


if __name__ == "__main__":
    run()
