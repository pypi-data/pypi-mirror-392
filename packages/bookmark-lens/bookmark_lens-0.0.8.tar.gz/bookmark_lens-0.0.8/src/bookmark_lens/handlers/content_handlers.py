"""Handlers for bookmark content operations."""

import json
import logging
from typing import TYPE_CHECKING

from mcp.types import TextContent

if TYPE_CHECKING:
    from ..services.bookmark_service import BookmarkService
    from ..services.content_fetcher import ContentFetcher

logger = logging.getLogger(__name__)


async def handle_get_bookmark_content(
    arguments: dict,
    bookmark_service: "BookmarkService",
    content_fetcher: "ContentFetcher",
    user_id: str = "dev-user"
) -> list[TextContent]:
    """Handle get_bookmark_content tool call."""
    bookmark_id = arguments.get("id")
    if not bookmark_id:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": "Missing required argument 'id'"
            }, indent=2)
        )]

    try:
        bookmark = bookmark_service.get_bookmark(bookmark_id, user_id)
        
        if not bookmark:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "message": f"Bookmark not found: {bookmark_id}"
                }, indent=2)
            )]
        
        # Check if stored content is valid (not an error message)
        error_messages = [
            "You can't perform that action at this time",
            "Access denied",
            "403 Forbidden",
            "404 Not Found"
        ]
        
        has_valid_content = (
            bookmark.content_text and 
            len(bookmark.content_text) > 100 and
            not any(err in bookmark.content_text for err in error_messages)
        )
        
        if has_valid_content:
            logger.info(f"✅ Using stored content_text: {len(bookmark.content_text)} characters")
            logger.info(f"📝 Content preview: {bookmark.content_text[:200]}")
            content = bookmark.content_text
        elif bookmark.url:
            logger.info(f"⚠️ No valid stored content, fetching fresh content for: {bookmark.url}")
            content_result = content_fetcher.fetch(bookmark.url)
            content = content_result.content_text or ""
            logger.info(f"✅ Fetched content: {len(content)} characters")
            if content:
                logger.info(f"📝 Fetched preview: {content[:200]}")
            else:
                logger.warning("⚠️ Fetched content is empty")
        else:
            logger.warning("❌ No content_text and no URL available")
            content = ""
        
        if not content:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": "No content available for this bookmark. The content could not be fetched or is empty."
                    }, indent=2)
                )
            ]
        
        logger.info(f"📦 Final content length being returned: {len(content)} characters")
        
        response = {
            "success": True,
            "bookmark": {
                "id": bookmark.id,
                "url": bookmark.url,
                "title": bookmark.title,
                "description": bookmark.description,
                "content": content
            },
            "message": "Content retrieved successfully"
        }
        
        logger.info(f"Retrieved content for bookmark: {bookmark_id}")
        return [TextContent(type="text", text=json.dumps(response, indent=2))]
        
    except Exception as e:
        logger.error(f"Failed to get bookmark content {bookmark_id}: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
        )]
