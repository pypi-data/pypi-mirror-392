"""
Search Manager for Web Search MCP Server.

Manages search operations across multiple providers with fallback capabilities,
rate limiting, and comprehensive error handling.
"""

import time
from typing import Any

import structlog

from .config import WebSearchConfig
from .models import SearchProvider, SearchResponse, SearchType
from .providers import (
    BaseSearchProvider,
    BingProvider,
    DuckDuckGoProvider,
    GoogleProvider,
    SearXNGProvider,
    SerperProvider,
    SerplyProvider,
    TavilyProvider,
)

logger = structlog.get_logger(__name__)


class SearchManager:
    """
    Manages search operations across multiple providers.

    This class handles provider selection, fallback logic, rate limiting,
    and result normalization across different search providers.
    """

    def __init__(self, config: WebSearchConfig):
        self.config = config
        self.providers: dict[SearchProvider, BaseSearchProvider] = {}
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the search manager and available providers."""
        if self._initialized:
            return

        try:
            logger.info("Initializing SearchManager")

            # Initialize available providers
            await self._initialize_providers()

            self._initialized = True
            logger.info(
                "SearchManager initialized successfully",
                available_providers=[p.value for p in self.providers.keys()],
            )

        except Exception as e:
            logger.error("Failed to initialize SearchManager", error=str(e))
            raise

    async def _initialize_providers(self) -> None:
        """Initialize all configured and available search providers."""
        # DuckDuckGo Provider (always available)
        if self.config.is_provider_enabled(SearchProvider.DUCKDUCKGO):
            duckduckgo_config = self.config.get_provider_config(
                SearchProvider.DUCKDUCKGO
            )
            duckduckgo_provider = DuckDuckGoProvider(
                SearchProvider.DUCKDUCKGO, duckduckgo_config
            )

            try:
                await duckduckgo_provider.initialize()
                self.providers[SearchProvider.DUCKDUCKGO] = duckduckgo_provider
                logger.info("DuckDuckGo provider initialized successfully")
            except Exception as e:
                logger.error("Failed to initialize DuckDuckGo provider", error=str(e))

        # Tavily Provider (requires API key)
        if self.config.is_provider_enabled(SearchProvider.TAVILY):
            tavily_config = self.config.get_provider_config(SearchProvider.TAVILY)
            tavily_provider = TavilyProvider(SearchProvider.TAVILY, tavily_config)

            try:
                await tavily_provider.initialize()
                self.providers[SearchProvider.TAVILY] = tavily_provider
                logger.info("Tavily provider initialized successfully")
            except Exception as e:
                logger.error("Failed to initialize Tavily provider", error=str(e))

        # Serper Provider (requires API key)
        if self.config.is_provider_enabled(SearchProvider.SERPER):
            serper_config = self.config.get_provider_config(SearchProvider.SERPER)
            serper_provider = SerperProvider(SearchProvider.SERPER, serper_config)

            try:
                await serper_provider.initialize()
                self.providers[SearchProvider.SERPER] = serper_provider
                logger.info("Serper provider initialized successfully")
            except Exception as e:
                logger.error("Failed to initialize Serper provider", error=str(e))

        # Google Custom Search Provider (requires API key and CSE ID)
        if self.config.is_provider_enabled(SearchProvider.GOOGLE):
            google_config = self.config.get_provider_config(SearchProvider.GOOGLE)
            google_provider = GoogleProvider(SearchProvider.GOOGLE, google_config)

            try:
                await google_provider.initialize()
                self.providers[SearchProvider.GOOGLE] = google_provider
                logger.info("Google Custom Search provider initialized successfully")
            except Exception as e:
                logger.error(
                    "Failed to initialize Google Custom Search provider", error=str(e)
                )

        # Bing Search Provider (requires API key)
        if self.config.is_provider_enabled(SearchProvider.BING):
            bing_config = self.config.get_provider_config(SearchProvider.BING)
            bing_provider = BingProvider(SearchProvider.BING, bing_config)

            try:
                await bing_provider.initialize()
                self.providers[SearchProvider.BING] = bing_provider
                logger.info("Bing Search provider initialized successfully")
            except Exception as e:
                logger.error("Failed to initialize Bing Search provider", error=str(e))

        # Serply Provider (requires API key)
        if self.config.is_provider_enabled(SearchProvider.SERPLY):
            serply_config = self.config.get_provider_config(SearchProvider.SERPLY)
            serply_provider = SerplyProvider(SearchProvider.SERPLY, serply_config)

            try:
                await serply_provider.initialize()
                self.providers[SearchProvider.SERPLY] = serply_provider
                logger.info("Serply provider initialized successfully")
            except Exception as e:
                logger.error("Failed to initialize Serply provider", error=str(e))

        # SearXNG Provider (requires base URL)
        if self.config.is_provider_enabled(SearchProvider.SEARXNG):
            searxng_config = self.config.get_provider_config(SearchProvider.SEARXNG)
            searxng_provider = SearXNGProvider(SearchProvider.SEARXNG, searxng_config)

            try:
                await searxng_provider.initialize()
                self.providers[SearchProvider.SEARXNG] = searxng_provider
                logger.info("SearXNG provider initialized successfully")
            except Exception as e:
                logger.error("Failed to initialize SearXNG provider", error=str(e))

        # TODO: Add other providers here as they are implemented
        # SerpAPI, etc.

        if not self.providers:
            raise RuntimeError("No search providers could be initialized")

    async def close(self) -> None:
        """Clean up resources."""
        try:
            logger.info("Closing SearchManager")

            # Close all provider connections
            for provider_name, provider in self.providers.items():
                try:
                    await provider.close()
                    logger.debug("Closed provider", provider=provider_name.value)
                except Exception as e:
                    logger.warning(
                        "Error closing provider",
                        provider=provider_name.value,
                        error=str(e),
                    )

            self.providers.clear()
            self._initialized = False
            logger.info("SearchManager closed successfully")
        except Exception as e:
            logger.warning("Error closing SearchManager", error=str(e))

    async def search(
        self,
        query: str,
        provider: SearchProvider,
        max_results: int = 10,
        search_type: SearchType = SearchType.SEARCH,
        timeout: int = 30,
    ) -> SearchResponse:
        """
        Perform a search using the specified provider.

        Args:
            query: Search query string
            provider: Search provider to use
            max_results: Maximum number of results to return
            search_type: Type of search (web or news)
            timeout: Request timeout in seconds

        Returns:
            SearchResponse with results or error information
        """
        if not self._initialized:
            await self.initialize()

        try:
            logger.info(
                "Performing search",
                query=query[:50] + "..." if len(query) > 50 else query,
                provider=provider.value,
                max_results=max_results,
                search_type=search_type.value,
            )

            # Check if provider is available
            if provider not in self.providers:
                available_providers = [p.value for p in self.providers.keys()]
                raise ValueError(
                    f"Provider '{provider.value}' is not available. "
                    f"Available providers: {available_providers}"
                )

            # Get the provider instance
            provider_instance = self.providers[provider]

            # Perform the search using the provider
            result = await provider_instance.search(
                query=query,
                max_results=max_results,
                search_type=search_type,
                timeout=timeout,
            )

            logger.info(
                "Search completed",
                provider=provider.value,
                success=result.success,
                results_count=result.results_returned,
                search_time=result.search_time,
            )

            return result

        except Exception as e:
            logger.error(
                "Search failed",
                query=query[:50] + "..." if len(query) > 50 else query,
                provider=provider.value,
                error=str(e),
                error_type=type(e).__name__,
            )

            # Return error response
            from .models import SearchMetadata

            return SearchResponse(
                success=False,
                provider=provider,
                query=query,
                results=[],
                results_returned=0,
                search_time=0.0,
                metadata=SearchMetadata(
                    language="en",
                    region="us",
                    search_type=search_type.value,
                    safe_search="moderate",
                ),
                error=str(e),
                error_type=type(e).__name__,
            )

    async def search_with_fallback(
        self,
        query: str,
        primary_provider: SearchProvider,
        fallback_providers: list[SearchProvider] | None = None,
        max_results: int = 10,
        search_type: SearchType = SearchType.SEARCH,
    ) -> dict[str, Any]:
        """
        Perform a search with automatic fallback to alternative providers.

        Args:
            query: Search query string
            primary_provider: Primary search provider
            fallback_providers: List of fallback providers
            max_results: Maximum number of results to return
            search_type: Type of search (web or news)

        Returns:
            Extended SearchResponse with fallback information
        """
        if not self._initialized:
            await self.initialize()

        start_time = time.time()
        providers_tried = []
        fallback_used = False

        # Build provider list
        providers_to_try = [primary_provider]
        if fallback_providers:
            providers_to_try.extend(fallback_providers)

        # Try each provider in order
        for i, provider in enumerate(providers_to_try):
            providers_tried.append(provider.value)

            try:
                result = await self.search(
                    query=query,
                    provider=provider,
                    max_results=max_results,
                    search_type=search_type,
                )

                if result.success:
                    # Success - add fallback information
                    result_dict = result.model_dump(mode="json")
                    result_dict["fallback_used"] = i > 0
                    result_dict["providers_tried"] = providers_tried
                    return result_dict

                # Provider failed, try next one
                if i > 0:
                    fallback_used = True

                logger.warning(
                    "Provider failed, trying next",
                    provider=provider.value,
                    error=result.error,
                    remaining_providers=len(providers_to_try) - i - 1,
                )

            except Exception as e:
                logger.error(
                    "Provider error during fallback search",
                    provider=provider.value,
                    error=str(e),
                )
                continue

        # All providers failed
        search_time = time.time() - start_time

        return {
            "success": False,
            "provider": primary_provider.value,
            "query": query,
            "results": [],
            "results_returned": 0,
            "search_time": search_time,
            "metadata": {
                "language": "en",
                "region": "us",
                "search_type": search_type.value,
                "safe_search": "moderate",
            },
            "fallback_used": fallback_used,
            "providers_tried": providers_tried,
            "error": f"All providers failed. Tried: {', '.join(providers_tried)}",
            "error_type": "AllProvidersFailed",
        }
