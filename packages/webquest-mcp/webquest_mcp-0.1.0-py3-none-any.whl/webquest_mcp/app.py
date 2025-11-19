from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession
from webquest.base import BaseRunner
from webquest.runners import Hyperbrowser
from webquest.scrapers.any_article import (
    AnyArticle,
    AnyArticleRequest,
    AnyArticleResponse,
)
from webquest.scrapers.duckduckgo_search import (
    DuckDuckGoSearch,
    DuckDuckGoSearchRequest,
    DuckDuckGoSearchResponse,
)
from webquest.scrapers.google_news_search import (
    GoogleNewsSearch,
    GoogleNewsSearchRequest,
    GoogleNewsSearchResponse,
)
from webquest.scrapers.youtube_search import (
    YouTubeSearch,
    YouTubeSearchRequest,
    YouTubeSearchResponse,
)
from webquest.scrapers.youtube_transcript import (
    YouTubeTranscript,
    YouTubeTranscriptRequest,
    YouTubeTranscriptResponse,
)


@dataclass
class AppContext:
    runner: BaseRunner


@asynccontextmanager
async def app_lifespan(_: FastMCP) -> AsyncIterator[AppContext]:
    runner = Hyperbrowser()
    try:
        yield AppContext(runner=runner)
    finally:
        pass


mcp = FastMCP("WebQuest MCP", lifespan=app_lifespan)


@mcp.tool()
async def any_article(
    request: AnyArticleRequest,
    ctx: Context[ServerSession, AppContext],
) -> AnyArticleResponse:
    """Get the content of an article given its URL."""
    runner = ctx.request_context.lifespan_context.runner
    scraper = AnyArticle()
    response = await runner.run(scraper, request)
    return response


@mcp.tool()
async def duckduckgo_search(
    request: DuckDuckGoSearchRequest,
    ctx: Context[ServerSession, AppContext],
) -> DuckDuckGoSearchResponse:
    """Search the web using DuckDuckGo given a query."""
    runner = ctx.request_context.lifespan_context.runner
    scraper = DuckDuckGoSearch()
    response = await runner.run(scraper, request)
    return response


@mcp.tool()
async def google_news_search(
    request: GoogleNewsSearchRequest,
    ctx: Context[ServerSession, AppContext],
) -> GoogleNewsSearchResponse:
    """Search for news articles using Google News given a query."""
    runner = ctx.request_context.lifespan_context.runner
    scraper = GoogleNewsSearch()
    response = await runner.run(scraper, request)
    return response


@mcp.tool()
async def youtube_search(
    request: YouTubeSearchRequest,
    ctx: Context[ServerSession, AppContext],
) -> YouTubeSearchResponse:
    """Search for YouTube videos, channels, posts, and shorts given a query."""
    runner = ctx.request_context.lifespan_context.runner
    scraper = YouTubeSearch()
    response = await runner.run(scraper, request)
    return response


@mcp.tool()
async def youtube_transcript(
    request: YouTubeTranscriptRequest,
    ctx: Context[ServerSession, AppContext],
) -> YouTubeTranscriptResponse:
    """Get the transcript of a YouTube video given its ID."""
    runner = ctx.request_context.lifespan_context.runner
    scraper = YouTubeTranscript()
    response = await runner.run(scraper, request)
    return response
