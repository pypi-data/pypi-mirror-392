# WebQuest MCP

WebQuest MCP is a Model Context Protocol (MCP) server that exposes powerful web search and scraping tools to AI agents and MCP-compatible clients.

**Scrapers**

- **Any Article:** Extracts readable content from arbitrary web articles.
- **DuckDuckGo Search:** General web search using DuckDuckGo.
- **Google News Search:** News-focused search via Google News.
- **YouTube Search:** Search YouTube videos, channels, posts, and shorts.
- **YouTube Transcript:** Fetch transcripts for YouTube videos.

**Runners**

- **Hyperbrowser:** Executes scraping tasks using Hyperbrowser.

## Installation

Installing using pip:

```bash
pip install webquest-mcp
```

Installing using uv:

```bash
uv add webquest-mcp
```

## Usage

Start the WebQuest MCP server:

```bash
webquest-mcp
```

This will launch the MCP server using the streamable-http transport. Configure your MCP-compatible client (e.g., an MCP-aware IDE or agent) to connect to the webquest-mcp server to use the tools listed above.

> To use the Hyperbrowser runner, you need to set the `HYPERBROWSER_API_KEY` environment variable.

> To use the Any Article scraper, you need to set the `OPENAI_API_KEY` environment variable.
