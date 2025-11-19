"""
Base search provider interface.

Defines the abstract base class that all search providers must implement
to ensure consistent behavior and extensibility.
"""

import time
from abc import ABC, abstractmethod
from typing import Any
from urllib.parse import urlparse

import httpx
import structlog

from ..config import ProviderConfig
from ..models import (
    APIError,
    NetworkError,
    SearchMetadata,
    SearchProvider,
    SearchResponse,
    SearchResult,
    SearchType,
)

logger = structlog.get_logger(__name__)


class BaseSearchProvider(ABC):
    """
    Abstract base class for search providers.

    All search providers must inherit from this class and implement
    the required abstract methods.
    """

    def __init__(self, provider: SearchProvider, config: ProviderConfig):
        self.provider = provider
        self.config = config
        self.client: httpx.AsyncClient | None = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the provider (create HTTP client, validate config, etc.)."""
        if self._initialized:
            return

        try:
            # Create HTTP client with appropriate settings
            timeout = httpx.Timeout(
                connect=10.0,
                read=self.config.timeout,
                write=10.0,
                pool=10.0,
            )

            self.client = httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=True,
                headers=self._get_default_headers(),
            )

            # Validate provider-specific configuration
            await self._validate_config()

            self._initialized = True
            logger.info(
                "Search provider initialized",
                provider=self.provider.value,
                timeout=self.config.timeout,
            )

        except Exception as e:
            logger.error(
                "Failed to initialize search provider",
                provider=self.provider.value,
                error=str(e),
            )
            raise

    async def close(self) -> None:
        """Clean up provider resources."""
        if self.client:
            await self.client.aclose()
            self.client = None
        self._initialized = False

    @abstractmethod
    async def _validate_config(self) -> None:
        """Validate provider-specific configuration."""
        pass

    @abstractmethod
    async def _perform_search(
        self,
        query: str,
        max_results: int,
        search_type: SearchType,
        **kwargs: Any,
    ) -> list[SearchResult]:
        """
        Perform the actual search operation.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            search_type: Type of search (web or news)
            **kwargs: Additional provider-specific parameters

        Returns:
            List of SearchResult objects

        Raises:
            APIError: If the search API returns an error
            NetworkError: If there's a network connectivity issue
        """
        pass

    async def search(
        self,
        query: str,
        max_results: int = 10,
        search_type: SearchType = SearchType.SEARCH,
        **kwargs: Any,
    ) -> SearchResponse:
        """
        Perform a search and return structured results.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            search_type: Type of search (web or news)
            **kwargs: Additional provider-specific parameters

        Returns:
            SearchResponse with results or error information
        """
        if not self._initialized:
            await self.initialize()

        start_time = time.time()

        try:
            logger.info(
                "Performing search",
                provider=self.provider.value,
                query=query[:100] + "..." if len(query) > 100 else query,
                max_results=max_results,
                search_type=search_type.value,
            )

            # Perform the search with retry logic
            results = await self._search_with_retry(
                query=query,
                max_results=max_results,
                search_type=search_type,
                **kwargs,
            )

            search_time = time.time() - start_time

            # Create metadata
            metadata = SearchMetadata(
                language="en",
                region="us",
                search_type=search_type.value,
                safe_search="moderate",
                total_available=len(results) if results else None,
            )

            logger.info(
                "Search completed successfully",
                provider=self.provider.value,
                results_count=len(results),
                search_time=search_time,
            )

            return SearchResponse(
                success=True,
                provider=self.provider,
                query=query,
                results=results,
                results_returned=len(results),
                search_time=search_time,
                metadata=metadata,
                related_searches=[],  # Can be overridden by specific providers
            )

        except Exception as e:
            search_time = time.time() - start_time
            error_msg = str(e)
            error_type = type(e).__name__

            logger.error(
                "Search failed",
                provider=self.provider.value,
                query=query[:100] + "..." if len(query) > 100 else query,
                error=error_msg,
                error_type=error_type,
                search_time=search_time,
            )

            return SearchResponse(
                success=False,
                provider=self.provider,
                query=query,
                results=[],
                results_returned=0,
                search_time=search_time,
                metadata=SearchMetadata(
                    language="en",
                    region="us",
                    search_type=search_type.value,
                    safe_search="moderate",
                ),
                error=error_msg,
                error_type=error_type,
            )

    async def _search_with_retry(
        self,
        query: str,
        max_results: int,
        search_type: SearchType,
        **kwargs: Any,
    ) -> list[SearchResult]:
        """
        Perform search with retry logic.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            search_type: Type of search (web or news)
            **kwargs: Additional provider-specific parameters

        Returns:
            List of SearchResult objects

        Raises:
            APIError: If all retry attempts fail
            NetworkError: If there's a persistent network issue
        """
        last_exception = None

        for attempt in range(self.config.max_retries + 1):
            try:
                if attempt > 0:
                    # Exponential backoff: 1s, 2s, 4s, etc.
                    delay = 2 ** (attempt - 1)
                    logger.info(
                        "Retrying search after delay",
                        provider=self.provider.value,
                        attempt=attempt + 1,
                        max_attempts=self.config.max_retries + 1,
                        delay=delay,
                    )
                    await self._sleep(delay)

                return await self._perform_search(
                    query=query,
                    max_results=max_results,
                    search_type=search_type,
                    **kwargs,
                )

            except (httpx.TimeoutException, httpx.ConnectError) as e:
                last_exception = NetworkError(
                    f"Network error during search: {str(e)}",
                    provider=self.provider,
                )
                logger.warning(
                    "Network error, will retry",
                    provider=self.provider.value,
                    attempt=attempt + 1,
                    error=str(e),
                )
                continue

            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500:
                    # Server error, retry
                    last_exception = APIError(
                        f"Server error: {e.response.status_code}",
                        provider=self.provider,
                    )
                    logger.warning(
                        "Server error, will retry",
                        provider=self.provider.value,
                        attempt=attempt + 1,
                        status_code=e.response.status_code,
                    )
                    continue
                else:
                    # Client error, don't retry
                    raise APIError(
                        f"API error: {e.response.status_code} - {e.response.text}",
                        provider=self.provider,
                    ) from e

            except Exception as e:
                # Unexpected error, don't retry
                raise APIError(
                    f"Unexpected error during search: {str(e)}",
                    provider=self.provider,
                ) from e

        # All retries exhausted
        if last_exception:
            raise last_exception
        else:
            raise APIError(
                f"Search failed after {self.config.max_retries + 1} attempts",
                provider=self.provider,
            )

    def _get_default_headers(self) -> dict[str, str]:
        """Get default HTTP headers for requests."""
        return {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;"
                "q=0.9,image/webp,*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL for source field."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            # Remove 'www.' prefix if present
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except Exception:
            return "unknown"

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""

        # Remove extra whitespace and normalize
        text = " ".join(text.split())

        # Remove common HTML entities that might slip through
        text = text.replace("&amp;", "&")
        text = text.replace("&lt;", "<")
        text = text.replace("&gt;", ">")
        text = text.replace("&quot;", '"')
        text = text.replace("&#39;", "'")

        return text.strip()

    async def _sleep(self, seconds: float) -> None:
        """Sleep for the specified number of seconds (async)."""
        import asyncio

        await asyncio.sleep(seconds)
