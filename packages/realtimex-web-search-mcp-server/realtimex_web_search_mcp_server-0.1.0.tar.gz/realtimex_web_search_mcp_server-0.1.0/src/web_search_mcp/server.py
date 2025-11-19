"""
Main MCP server implementation for Web Search.

Provides MCP tools for performing web searches across multiple providers
with structured output and comprehensive error handling.
"""

from typing import Any

import mcp.types as types
import structlog
from mcp.server import Server
from mcp.server.stdio import stdio_server

from .config import WebSearchConfig
from .models import SearchProvider, SearchType
from .search_manager import SearchManager

logger = structlog.get_logger(__name__)


class WebSearchMCPServer:
    """
    MCP Server for Web Search operations.

    This server provides tools for performing web searches across multiple
    providers with structured output and automatic fallback capabilities.
    """

    def __init__(self, config: WebSearchConfig):
        self.config = config
        self.server = Server(
            name=config.server.server_name,
            version=config.server.server_version,
        )
        self.search_manager = SearchManager(config)
        self._initialized = False

        # Register MCP handlers
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register MCP protocol handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[types.Tool]:
            """Handle list_tools requests by returning available search tools."""
            try:
                logger.info("Received list_tools request")

                # Ensure server is initialized
                await self._ensure_initialized()

                # Build available tools
                tools = []

                # Main web search tool
                tools.append(self._build_web_search_tool())

                # Search with fallback tool
                if self.config.server.enable_fallbacks:
                    tools.append(self._build_search_with_fallback_tool())

                logger.info(
                    "Returning available tools",
                    tool_count=len(tools),
                    tool_names=[tool.name for tool in tools],
                )

                return tools

            except Exception as e:
                logger.error("Error in list_tools handler", error=str(e))
                # Return empty list on error to avoid breaking MCP protocol
                return []

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
            """Handle call_tool requests by executing the corresponding search."""
            logger.info(
                "Received call_tool request",
                tool_name=name,
                arguments=arguments,
            )

            try:
                # Ensure server is initialized
                await self._ensure_initialized()

                # Route to appropriate handler
                if name == "web_search":
                    return await self._handle_web_search(arguments)
                elif name == "search_with_fallback":
                    return await self._handle_search_with_fallback(arguments)
                else:
                    error_msg = f"Unknown tool '{name}'. Available tools: web_search, search_with_fallback"
                    logger.error("Unknown tool requested", tool_name=name)
                    raise ValueError(error_msg)

            except ValueError:
                # Re-raise ValueError for parameter validation errors
                raise
            except Exception as e:
                # Wrap unexpected errors
                error_msg = (
                    f"Internal server error while executing tool '{name}': {str(e)}"
                )
                logger.error(
                    "Unexpected error in call_tool handler",
                    tool_name=name,
                    error=str(e),
                    error_type=type(e).__name__,
                )
                raise RuntimeError(error_msg) from e

    async def _ensure_initialized(self) -> None:
        """Ensure the server is properly initialized."""
        if not self._initialized:
            await self.search_manager.initialize()
            self._initialized = True

    def _build_web_search_tool(self) -> types.Tool:
        """Build the main web search tool definition."""
        return types.Tool(
            name="web_search",
            description="Perform web searches using various search providers with structured results",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query string",
                    },
                    "provider": {
                        "type": "string",
                        "enum": [p.value for p in SearchProvider],
                        "description": f"Search provider to use (default: {self.config.server.default_provider.value})",
                        "default": self.config.server.default_provider.value,
                    },
                    "max_results": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "description": f"Maximum number of results to return (default: {self.config.server.default_max_results})",
                        "default": self.config.server.default_max_results,
                    },
                    "search_type": {
                        "type": "string",
                        "enum": [t.value for t in SearchType],
                        "description": "Type of search to perform (default: search)",
                        "default": "search",
                    },
                    "timeout": {
                        "type": "integer",
                        "minimum": 5,
                        "maximum": 120,
                        "description": f"Request timeout in seconds (default: {self.config.server.default_timeout})",
                        "default": self.config.server.default_timeout,
                    },
                },
                "required": ["query"],
                "additionalProperties": False,
            },
            outputSchema={
                "type": "object",
                "description": "Structured search results",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "description": "Whether the search was successful",
                    },
                    "provider": {
                        "type": "string",
                        "description": "Search provider used",
                    },
                    "query": {
                        "type": "string",
                        "description": "Original search query",
                    },
                    "results": {
                        "type": "array",
                        "description": "List of search results",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "url": {"type": "string"},
                                "snippet": {"type": "string"},
                                "position": {"type": "integer"},
                                "date": {"type": ["string", "null"]},
                                "source": {"type": ["string", "null"]},
                                "thumbnail": {"type": ["string", "null"]},
                                "metadata": {"type": "object"},
                            },
                            "required": ["title", "url", "snippet", "position"],
                        },
                    },
                    "results_returned": {
                        "type": "integer",
                        "description": "Number of results returned",
                    },
                    "search_time": {
                        "type": "number",
                        "description": "Search execution time in seconds",
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Search metadata",
                    },
                    "related_searches": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Related search suggestions",
                    },
                    "error": {
                        "type": ["string", "null"],
                        "description": "Error message if search failed",
                    },
                    "error_type": {
                        "type": ["string", "null"],
                        "description": "Error type classification",
                    },
                },
                "required": [
                    "success",
                    "provider",
                    "query",
                    "results",
                    "results_returned",
                    "search_time",
                    "metadata",
                ],
            },
        )

    def _build_search_with_fallback_tool(self) -> types.Tool:
        """Build the search with fallback tool definition."""
        enabled_providers = [p.value for p in self.config.get_enabled_providers()]

        return types.Tool(
            name="search_with_fallback",
            description="Perform web searches with automatic fallback to alternative providers on failure",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query string",
                    },
                    "primary_provider": {
                        "type": "string",
                        "enum": enabled_providers,
                        "description": f"Primary search provider (default: {self.config.server.default_provider.value})",
                        "default": self.config.server.default_provider.value,
                    },
                    "fallback_providers": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": enabled_providers,
                        },
                        "description": "List of fallback providers in priority order",
                        "default": [],
                    },
                    "max_results": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "description": f"Maximum number of results to return (default: {self.config.server.default_max_results})",
                        "default": self.config.server.default_max_results,
                    },
                    "search_type": {
                        "type": "string",
                        "enum": [t.value for t in SearchType],
                        "description": "Type of search to perform (default: search)",
                        "default": "search",
                    },
                },
                "required": ["query"],
                "additionalProperties": False,
            },
            outputSchema={
                "type": "object",
                "description": "Structured search results with fallback information",
                "properties": {
                    "success": {"type": "boolean"},
                    "provider": {"type": "string"},
                    "query": {"type": "string"},
                    "results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "url": {"type": "string"},
                                "snippet": {"type": "string"},
                                "position": {"type": "integer"},
                                "date": {"type": ["string", "null"]},
                                "source": {"type": ["string", "null"]},
                                "thumbnail": {"type": ["string", "null"]},
                                "metadata": {"type": "object"},
                            },
                            "required": ["title", "url", "snippet", "position"],
                        },
                    },
                    "results_returned": {"type": "integer"},
                    "search_time": {"type": "number"},
                    "metadata": {"type": "object"},
                    "fallback_used": {
                        "type": "boolean",
                        "description": "Whether fallback providers were used",
                    },
                    "providers_tried": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of providers attempted",
                    },
                    "error": {"type": ["string", "null"]},
                    "error_type": {"type": ["string", "null"]},
                },
                "required": [
                    "success",
                    "provider",
                    "query",
                    "results",
                    "results_returned",
                    "search_time",
                    "metadata",
                    "fallback_used",
                    "providers_tried",
                ],
            },
        )

    async def _handle_web_search(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Handle web_search tool execution."""
        # Extract and validate parameters
        query = arguments.get("query")
        if not query or not query.strip():
            raise ValueError("Query parameter is required and cannot be empty")

        provider_str = arguments.get(
            "provider", self.config.server.default_provider.value
        )
        max_results = arguments.get(
            "max_results", self.config.server.default_max_results
        )
        search_type_str = arguments.get("search_type", "search")
        timeout = arguments.get("timeout", self.config.server.default_timeout)

        # Validate provider
        try:
            provider = SearchProvider(provider_str.lower())
        except ValueError as e:
            raise ValueError(
                f"Invalid provider '{provider_str}'. Available providers: {[p.value for p in SearchProvider]}"
            ) from e

        # Validate search type
        try:
            search_type = SearchType(search_type_str.lower())
        except ValueError as e:
            raise ValueError(
                f"Invalid search type '{search_type_str}'. Available types: {[t.value for t in SearchType]}"
            ) from e

        # Validate max_results
        if not isinstance(max_results, int) or max_results < 1 or max_results > 100:
            raise ValueError("max_results must be an integer between 1 and 100")

        # Validate timeout
        if not isinstance(timeout, int) or timeout < 5 or timeout > 120:
            raise ValueError("timeout must be an integer between 5 and 120 seconds")

        # Perform search
        result = await self.search_manager.search(
            query=query.strip(),
            provider=provider,
            max_results=max_results,
            search_type=search_type,
            timeout=timeout,
        )

        # Convert to dict for MCP response
        return result.model_dump(mode="json")

    async def _handle_search_with_fallback(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle search_with_fallback tool execution."""
        # Extract and validate parameters
        query = arguments.get("query")
        if not query or not query.strip():
            raise ValueError("Query parameter is required and cannot be empty")

        primary_provider_str = arguments.get(
            "primary_provider", self.config.server.default_provider.value
        )
        fallback_providers_str = arguments.get("fallback_providers", [])
        max_results = arguments.get(
            "max_results", self.config.server.default_max_results
        )
        search_type_str = arguments.get("search_type", "search")

        # Validate primary provider
        try:
            primary_provider = SearchProvider(primary_provider_str.lower())
        except ValueError as e:
            raise ValueError(
                f"Invalid primary provider '{primary_provider_str}'"
            ) from e

        # Validate fallback providers
        fallback_providers = []
        for provider_str in fallback_providers_str:
            try:
                fallback_providers.append(SearchProvider(provider_str.lower()))
            except ValueError as e:
                raise ValueError(f"Invalid fallback provider '{provider_str}'") from e

        # Validate search type
        try:
            search_type = SearchType(search_type_str.lower())
        except ValueError as e:
            raise ValueError(f"Invalid search type '{search_type_str}'") from e

        # Validate max_results
        if not isinstance(max_results, int) or max_results < 1 or max_results > 100:
            raise ValueError("max_results must be an integer between 1 and 100")

        # Perform search with fallback
        result = await self.search_manager.search_with_fallback(
            query=query.strip(),
            primary_provider=primary_provider,
            fallback_providers=fallback_providers,
            max_results=max_results,
            search_type=search_type,
        )

        # Convert to dict for MCP response
        return result.model_dump(mode="json")

    async def start(self) -> None:
        """Start the MCP server."""
        try:
            logger.info(
                "Starting Web Search MCP Server",
                server_name=self.config.server.server_name,
                enabled_providers=[
                    p.value for p in self.config.get_enabled_providers()
                ],
                default_provider=self.config.server.default_provider.value,
            )

            # Initialize components
            await self._ensure_initialized()

            # Start STDIO server
            async with stdio_server() as (read_stream, write_stream):
                logger.info("MCP server started successfully")
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options(),
                )

        except Exception as e:
            logger.error("Failed to start MCP server", error=str(e))
            raise
        finally:
            await self.cleanup()

    async def cleanup(self) -> None:
        """Clean up server resources."""
        try:
            logger.info("Cleaning up MCP server resources")
            await self.search_manager.close()
            logger.info("MCP server cleanup completed")
        except Exception as e:
            logger.warning("Error during cleanup", error=str(e))
