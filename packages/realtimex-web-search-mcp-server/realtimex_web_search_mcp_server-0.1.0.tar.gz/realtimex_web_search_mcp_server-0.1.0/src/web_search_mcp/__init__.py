"""
Web Search MCP Server

A Model Context Protocol (MCP) server that provides utility tools for performing
web searches via APIs. Supports multiple search providers including Google, Bing,
DuckDuckGo, SerpAPI, Serply, SearXNG, and Tavily.

This package provides a production-ready MCP server with comprehensive search
capabilities, structured output, and robust error handling.
"""

__version__ = "1.0.0"
__author__ = "RealTimeX"
__email__ = "support@realtimex.com"

from .models import SearchError, SearchResponse, SearchResult
from .server import WebSearchMCPServer

__all__ = [
    "WebSearchMCPServer",
    "SearchResult",
    "SearchResponse",
    "SearchError",
]
