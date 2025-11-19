"""
Tavily search provider implementation.

Implements web search using Tavily's AI-optimized search API.
Provides high-quality, structured results optimized for AI applications.
"""

import json
from typing import Any

import httpx
import structlog

from ..models import (
    APIError,
    AuthenticationError,
    NetworkError,
    QuotaExceededError,
    SearchResult,
    SearchType,
)
from .base import BaseSearchProvider

logger = structlog.get_logger(__name__)


class TavilyProvider(BaseSearchProvider):
    """
    Tavily search provider implementation.

    Uses Tavily's AI-optimized search API to perform searches.
    Requires API key and provides high-quality structured results.
    """

    BASE_URL = "https://api.tavily.com/search"

    async def _validate_config(self) -> None:
        """Validate Tavily configuration (API key required)."""
        if not self.config.api_key:
            raise AuthenticationError(
                "Tavily API key is required but not provided",
                provider=self.provider,
            )

        logger.debug("Tavily provider configuration validated")

    async def _perform_search(
        self,
        query: str,
        max_results: int,
        search_type: SearchType,
        **kwargs: Any,
    ) -> list[SearchResult]:
        """
        Perform Tavily search using their API.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            search_type: Type of search (web or news)
            **kwargs: Additional parameters

        Returns:
            List of SearchResult objects

        Raises:
            APIError: If the search fails or returns invalid data
            NetworkError: If there's a network connectivity issue
            AuthenticationError: If API key is invalid
            QuotaExceededError: If API quota is exceeded
        """
        if not self.client:
            raise APIError("HTTP client not initialized", provider=self.provider)

        try:
            # Build request payload
            payload = self._build_request_payload(
                query, max_results, search_type, **kwargs
            )

            logger.debug(
                "Making Tavily search request",
                query=query,
                max_results=max_results,
                search_type=search_type.value,
            )

            # Make the search request
            response = await self.client.post(
                self.BASE_URL,
                json=payload,
                headers=self._get_api_headers(),
            )

            # Handle different HTTP status codes with specific error extraction
            if response.status_code == 400:
                error_message = self._extract_error_message(response)
                raise APIError(
                    f"Invalid request parameters: {error_message}",
                    provider=self.provider,
                )
            elif response.status_code == 401:
                error_message = self._extract_error_message(response)
                raise AuthenticationError(
                    f"Invalid Tavily API key: {error_message}",
                    provider=self.provider,
                )
            elif response.status_code == 429:
                error_message = self._extract_error_message(response)
                raise QuotaExceededError(
                    f"Tavily API rate limit exceeded: {error_message}",
                    provider=self.provider,
                    retry_after=int(response.headers.get("Retry-After", 3600)),
                )
            elif response.status_code == 432:
                error_message = self._extract_error_message(response)
                raise QuotaExceededError(
                    f"Tavily monthly quota exceeded: {error_message}",
                    provider=self.provider,
                    retry_after=86400,  # Retry after 24 hours
                )
            elif response.status_code == 433:
                error_message = self._extract_error_message(response)
                raise QuotaExceededError(
                    f"Tavily daily quota exceeded: {error_message}",
                    provider=self.provider,
                    retry_after=86400,  # Retry after 24 hours
                )
            elif response.status_code >= 500:
                error_message = self._extract_error_message(response)
                raise APIError(
                    f"Tavily server error ({response.status_code}): {error_message}",
                    provider=self.provider,
                )
            elif response.status_code >= 400:
                error_message = self._extract_error_message(response)
                raise APIError(
                    f"Tavily API error ({response.status_code}): {error_message}",
                    provider=self.provider,
                )

            response.raise_for_status()

            # Parse the JSON response
            response_data = response.json()
            results = self._parse_search_results(response_data, max_results)

            logger.info(
                "Tavily search completed",
                query=query[:50] + "..." if len(query) > 50 else query,
                results_found=len(results),
                max_results=max_results,
                response_time=response_data.get("response_time", 0),
            )

            return results

        except httpx.HTTPStatusError as e:
            logger.error(
                "Tavily HTTP error",
                status_code=e.response.status_code,
                response_text=e.response.text[:500],
            )
            raise APIError(
                f"Tavily search failed with status {e.response.status_code}",
                provider=self.provider,
            ) from e

        except httpx.RequestError as e:
            logger.error("Tavily network error", error=str(e))
            raise NetworkError(
                f"Network error during Tavily search: {str(e)}",
                provider=self.provider,
            ) from e

        except json.JSONDecodeError as e:
            logger.error("Tavily JSON parsing error", error=str(e))
            raise APIError(
                f"Failed to parse Tavily JSON response: {str(e)}",
                provider=self.provider,
            ) from e

        except Exception as e:
            logger.error("Tavily unexpected error", error=str(e))
            raise APIError(
                f"Unexpected error during Tavily search: {str(e)}",
                provider=self.provider,
            ) from e

    def _build_request_payload(
        self,
        query: str,
        max_results: int,
        search_type: SearchType,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Build the request payload for Tavily API.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            search_type: Type of search (web or news)
            **kwargs: Additional parameters

        Returns:
            Dictionary containing the request payload
        """
        payload = {
            "api_key": self.config.api_key,
            "query": query,
            "max_results": min(max_results, 20),  # Tavily has a max limit
            "search_depth": "basic",  # Can be "basic" or "advanced"
            "include_answer": False,  # We focus on search results
            "include_images": False,  # We don't need images for now
            "include_raw_content": False,  # We use the processed content
        }

        # Add search type specific parameters
        if search_type == SearchType.NEWS:
            payload["topic"] = "news"
            payload["search_depth"] = "advanced"  # Better for news
        else:
            payload["topic"] = "general"

        # Add any additional parameters from kwargs
        if "search_depth" in kwargs:
            payload["search_depth"] = kwargs["search_depth"]

        if "include_answer" in kwargs:
            payload["include_answer"] = kwargs["include_answer"]

        return payload

    def _parse_search_results(
        self, response_data: dict[str, Any], max_results: int
    ) -> list[SearchResult]:
        """
        Parse Tavily API response into SearchResult objects.

        Args:
            response_data: Raw JSON response from Tavily API
            max_results: Maximum number of results to extract

        Returns:
            List of SearchResult objects

        Raises:
            APIError: If response parsing fails
        """
        try:
            results = []
            tavily_results = response_data.get("results", [])

            if not tavily_results:
                logger.warning("No results found in Tavily response")
                return []

            for position, result_data in enumerate(tavily_results[:max_results], 1):
                try:
                    result = self._extract_result_from_data(result_data, position)
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.warning(
                        "Failed to extract result from Tavily data",
                        position=position,
                        error=str(e),
                    )
                    continue

            return results

        except Exception as e:
            logger.error("Failed to parse Tavily response", error=str(e))
            raise APIError(
                f"Failed to parse Tavily search results: {str(e)}",
                provider=self.provider,
            ) from e

    def _extract_result_from_data(
        self, result_data: dict[str, Any], position: int
    ) -> SearchResult | None:
        """
        Extract a single search result from Tavily result data.

        Args:
            result_data: Individual result data from Tavily API
            position: Position of this result in the search results

        Returns:
            SearchResult object or None if extraction fails
        """
        try:
            # Extract required fields
            url = result_data.get("url")
            title = result_data.get("title")
            content = result_data.get("content")

            if not url or not title:
                logger.debug(
                    "Missing required fields in Tavily result", result_data=result_data
                )
                return None

            # Clean and validate URL
            url = self._clean_url(url)
            if not url:
                return None

            # Clean title and content
            title = self._clean_text(title)
            snippet = (
                self._clean_text(content) if content else "No description available"
            )

            # Truncate snippet if too long
            if len(snippet) > 300:
                snippet = snippet[:297] + "..."

            # Extract source domain
            source = self._extract_domain(url)

            # Extract score if available (Tavily provides relevance scores)
            score = result_data.get("score")

            # Build metadata
            metadata = {
                "provider": "tavily",
                "extracted_at": "2024-01-15T00:00:00Z",  # Could use actual timestamp
            }

            if score is not None:
                metadata["relevance_score"] = score

            # Check for raw content if available
            raw_content = result_data.get("raw_content")
            if raw_content:
                metadata["has_raw_content"] = True

            return SearchResult(
                title=title,
                url=url,
                snippet=snippet,
                position=position,
                date=None,  # Tavily doesn't typically provide dates
                source=source,
                metadata=metadata,
            )

        except Exception as e:
            logger.debug(
                "Failed to extract result from Tavily data",
                position=position,
                error=str(e),
            )
            return None

    def _extract_error_message(self, response: httpx.Response) -> str:
        """
        Extract error message from Tavily API response.

        Args:
            response: HTTP response from Tavily API

        Returns:
            Extracted error message or fallback text
        """
        try:
            error_data = response.json()
            # Handle Tavily's nested error format: {"detail": {"error": "message"}}
            if "detail" in error_data and isinstance(error_data["detail"], dict):
                return error_data["detail"].get("error", response.text)
            # Handle direct error format: {"error": "message"}
            elif "error" in error_data:
                return error_data["error"]
            # Fallback to response text
            else:
                return response.text
        except (json.JSONDecodeError, KeyError):
            return response.text or f"HTTP {response.status_code} error"

    def _get_api_headers(self) -> dict[str, str]:
        """Get Tavily-specific API headers."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": (
                "WebSearchMCP/1.0.0 (https://github.com/realtimex/web-search-mcp-server)"
            ),
        }
        return headers

    def _clean_url(self, url: str) -> str | None:
        """
        Clean and validate URL from Tavily results.

        Args:
            url: Raw URL from Tavily results

        Returns:
            Cleaned URL or None if invalid
        """
        if not url:
            return None

        # Tavily URLs are typically clean, but let's validate
        if not url.startswith(("http://", "https://")):
            if url.startswith("//"):
                url = "https:" + url
            else:
                url = "https://" + url

        # Basic URL validation
        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            if not parsed.netloc:
                return None
            return url
        except Exception:
            return None

    async def search(
        self,
        query: str,
        max_results: int = 10,
        search_type: SearchType = SearchType.SEARCH,
        **kwargs: Any,
    ):  # TODO: Add Type-hint
        """
        Override search method to add Tavily-specific enhancements.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            search_type: Type of search (web or news)
            **kwargs: Additional Tavily-specific parameters

        Returns:
            SearchResponse with results or error information
        """
        # Call parent search method
        result = await super().search(query, max_results, search_type, **kwargs)

        # Add Tavily-specific enhancements to successful results
        if result.success and result.results:
            # Sort results by relevance score if available
            results_with_scores = [
                r
                for r in result.results
                if r.metadata.get("relevance_score") is not None
            ]

            if results_with_scores:
                # Sort by relevance score (higher is better)
                result.results.sort(
                    key=lambda r: r.metadata.get("relevance_score", 0), reverse=True
                )

            # Add Tavily-specific metadata
            result.metadata.total_available = len(result.results)

            # Add related searches if available (Tavily sometimes provides follow-up questions)
            # This would be extracted from the API response if available

        return result
