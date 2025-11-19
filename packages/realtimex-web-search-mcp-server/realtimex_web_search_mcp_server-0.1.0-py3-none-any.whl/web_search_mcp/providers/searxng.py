"""
SearXNG Search provider implementation.

Implements web search using SearXNG open-source metasearch engine
with proper result parsing and comprehensive error handling.
"""

import json
from typing import Any

import httpx
import structlog

from ..models import (
    APIError,
    AuthenticationError,
    NetworkError,
    SearchResult,
    SearchType,
    ValidationError,
)
from .base import BaseSearchProvider

logger = structlog.get_logger(__name__)


class SearXNGProvider(BaseSearchProvider):
    """
    SearXNG Search provider implementation.

    Uses SearXNG open-source metasearch engine to perform searches.
    Requires base URL of SearXNG instance (no API key needed).
    """

    def __init__(self, provider, config):
        super().__init__(provider, config)
        self.base_url = config.base_url
        if not self.base_url:
            raise ValueError("SearXNG base URL is required")

        # Ensure base URL doesn't end with slash
        self.base_url = self.base_url.rstrip("/")

    async def _validate_config(self) -> None:
        """Validate SearXNG configuration."""
        if not self.config.base_url:
            raise AuthenticationError(
                "SearXNG base URL is required but not provided",
                provider=self.provider,
            )

        # Test connectivity to SearXNG instance
        try:
            response = await self.client.get(f"{self.base_url}/config")
            if response.status_code != 200:
                raise AuthenticationError(
                    f"SearXNG instance not accessible at {self.base_url}",
                    provider=self.provider,
                )
        except httpx.RequestError as e:
            raise AuthenticationError(
                f"Cannot connect to SearXNG instance at {self.base_url}: {str(e)}",
                provider=self.provider,
            ) from e

        logger.debug("SearXNG provider configuration validated", base_url=self.base_url)

    async def _perform_search(
        self,
        query: str,
        max_results: int,
        search_type: SearchType,
        **kwargs: Any,
    ) -> list[SearchResult]:
        """
        Perform SearXNG Search using their API.

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
            ValidationError: If request parameters are invalid
        """
        if not self.client:
            raise APIError("HTTP client not initialized", provider=self.provider)

        try:
            # Build search URL and parameters
            search_url = f"{self.base_url}/search"
            params = self._build_request_params(
                query, max_results, search_type, **kwargs
            )

            logger.debug(
                "Making SearXNG search request",
                url=search_url,
                query=query,
                max_results=max_results,
                search_type=search_type.value,
            )

            # Make the search request
            response = await self.client.get(
                search_url,
                params=params,
                headers=self._get_api_headers(),
            )

            # Handle different HTTP status codes
            if response.status_code == 400:
                error_message = self._extract_error_message(response)
                raise ValidationError(
                    f"Invalid request parameters: {error_message}",
                    provider=self.provider,
                )
            elif response.status_code == 404:
                raise APIError(
                    "SearXNG search endpoint not found - check base URL",
                    provider=self.provider,
                )
            elif response.status_code == 429:
                raise APIError(
                    "SearXNG rate limit exceeded - too many requests",
                    provider=self.provider,
                )
            elif response.status_code >= 500:
                error_message = self._extract_error_message(response)
                raise APIError(
                    f"SearXNG server error ({response.status_code}): {error_message}",
                    provider=self.provider,
                )
            elif response.status_code >= 400:
                error_message = self._extract_error_message(response)
                raise APIError(
                    f"SearXNG error ({response.status_code}): {error_message}",
                    provider=self.provider,
                )

            response.raise_for_status()

            # Parse the JSON response
            response_data = response.json()
            results = self._parse_search_results(
                response_data, max_results, search_type
            )

            logger.info(
                "SearXNG search completed",
                query=query[:50] + "..." if len(query) > 50 else query,
                results_found=len(results),
                max_results=max_results,
                search_type=search_type.value,
            )

            return results

        except httpx.HTTPStatusError as e:
            logger.error(
                "SearXNG HTTP error",
                status_code=e.response.status_code,
                response_text=e.response.text[:500],
            )
            raise APIError(
                f"SearXNG search failed with status {e.response.status_code}",
                provider=self.provider,
            ) from e

        except httpx.RequestError as e:
            logger.error("SearXNG network error", error=str(e))
            raise NetworkError(
                f"Network error during SearXNG search: {str(e)}",
                provider=self.provider,
            ) from e

        except json.JSONDecodeError as e:
            logger.error("SearXNG JSON parsing error", error=str(e))
            raise APIError(
                f"Failed to parse SearXNG JSON response: {str(e)}",
                provider=self.provider,
            ) from e

        except (ValidationError, APIError, NetworkError):
            # Re-raise our custom exceptions without modification
            raise
        except Exception as e:
            logger.error("SearXNG unexpected error", error=str(e))
            raise APIError(
                f"Unexpected error during SearXNG search: {str(e)}",
                provider=self.provider,
            ) from e

    def _build_request_params(
        self,
        query: str,
        max_results: int,
        search_type: SearchType,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Build the request parameters for SearXNG API.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            search_type: Type of search (web or news)
            **kwargs: Additional parameters

        Returns:
            Dictionary containing the request parameters
        """
        params = {
            "q": query,
            "format": "json",
            "pageno": 1,  # Page number (SearXNG uses pagination)
        }

        # Add search type specific parameters
        if search_type == SearchType.NEWS:
            # News-specific engines
            params["categories"] = "news"
        else:
            # General web search
            params["categories"] = "general"

        # Add optional parameters from kwargs
        if "language" in kwargs:
            params["language"] = kwargs["language"]
        elif "lang" in kwargs:
            params["language"] = kwargs["lang"]
        else:
            params["language"] = "en"  # Default to English

        # Safe search
        if "safe_search" in kwargs:
            safe_search_map = {"off": "0", "moderate": "1", "strict": "2"}
            params["safesearch"] = safe_search_map.get(
                kwargs["safe_search"].lower(), "1"
            )
        else:
            params["safesearch"] = "1"  # Default to moderate

        # Time range for searches
        if "time_range" in kwargs:
            time_range_map = {
                "day": "day",
                "week": "week",
                "month": "month",
                "year": "year",
            }
            params["time_range"] = time_range_map.get(kwargs["time_range"].lower())

        # Search engines to use
        if "engines" in kwargs:
            if isinstance(kwargs["engines"], list):
                params["engines"] = ",".join(kwargs["engines"])
            else:
                params["engines"] = kwargs["engines"]

        # Image search
        if (
            search_type == SearchType.SEARCH
            and "image_search" in kwargs
            and kwargs["image_search"]
        ):
            params["categories"] = "images"

        return params

    def _parse_search_results(
        self, response_data: dict[str, Any], max_results: int, search_type: SearchType
    ) -> list[SearchResult]:
        """
        Parse SearXNG API response into SearchResult objects.

        Args:
            response_data: Raw JSON response from SearXNG API
            max_results: Maximum number of results to extract
            search_type: Type of search performed

        Returns:
            List of SearchResult objects

        Raises:
            APIError: If response parsing fails
        """
        try:
            results = []

            # Handle infobox results first (if available)
            infoboxes = response_data.get("infoboxes", [])
            for infobox in infoboxes:
                if len(results) >= max_results:
                    break

                infobox_result = self._extract_infobox_result(infobox, len(results) + 1)
                if infobox_result:
                    results.append(infobox_result)

            # Handle regular search results
            search_results = response_data.get("results", [])

            if not search_results and not infoboxes:
                logger.warning("No results found in SearXNG response")
                return []

            for result_data in search_results:
                if len(results) >= max_results:
                    break

                try:
                    result = self._extract_result_from_data(
                        result_data, len(results) + 1, search_type
                    )
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.warning(
                        "Failed to extract result from SearXNG data",
                        position=len(results) + 1,
                        error=str(e),
                    )
                    continue

            return results

        except Exception as e:
            logger.error("Failed to parse SearXNG response", error=str(e))
            raise APIError(
                f"Failed to parse SearXNG search results: {str(e)}",
                provider=self.provider,
            ) from e

    def _extract_infobox_result(
        self, infobox_data: dict[str, Any], position: int
    ) -> SearchResult | None:
        """
        Extract infobox result from SearXNG response.

        Args:
            infobox_data: Infobox data from SearXNG API
            position: Position for this result

        Returns:
            SearchResult object or None if extraction fails
        """
        try:
            title = infobox_data.get("infobox")
            content = infobox_data.get("content")
            urls = infobox_data.get("urls", [])

            if not title:
                return None

            # Get the first URL if available
            url = "https://searxng.org"  # Default fallback
            if urls and isinstance(urls, list) and urls:
                first_url = urls[0]
                if isinstance(first_url, dict) and "url" in first_url:
                    url = first_url["url"]
                elif isinstance(first_url, str):
                    url = first_url

            # Clean and validate URL
            url = self._clean_url(url)
            if not url:
                url = "https://searxng.org"

            # Create snippet from content
            snippet = "Infobox result"
            if content:
                if isinstance(content, str):
                    snippet = content
                elif isinstance(content, list):
                    snippet = " ".join(str(item) for item in content[:3])

            snippet = self._clean_text(snippet)
            source = self._extract_domain(url)

            return SearchResult(
                title=f"📋 {self._clean_text(title)}",  # Add emoji to distinguish infobox
                url=url,
                snippet=snippet,
                position=position,
                date=None,
                source=source,
                metadata={
                    "provider": "searxng",
                    "result_type": "infobox",
                    "extracted_at": "2024-01-15T00:00:00Z",
                },
            )

        except Exception as e:
            logger.debug("Failed to extract infobox result", error=str(e))
            return None

    def _extract_result_from_data(
        self, result_data: dict[str, Any], position: int, search_type: SearchType
    ) -> SearchResult | None:
        """
        Extract a single search result from SearXNG result data.

        Args:
            result_data: Individual result data from SearXNG API
            position: Position of this result in the search results
            search_type: Type of search performed

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
                    "Missing required fields in SearXNG result",
                    result_data=result_data,
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
            source = result_data.get("pretty_url") or self._extract_domain(url)

            # Extract date if available
            date = self._extract_date_from_item(result_data)

            # Extract thumbnail if available
            thumbnail = self._extract_thumbnail(result_data)

            # Build metadata
            metadata = {
                "provider": "searxng",
                "search_type": search_type.value,
                "extracted_at": "2024-01-15T00:00:00Z",
            }

            # Add SearXNG-specific metadata
            if "engine" in result_data:
                metadata["engine"] = result_data["engine"]

            if "score" in result_data:
                metadata["score"] = result_data["score"]

            if "category" in result_data:
                metadata["category"] = result_data["category"]

            return SearchResult(
                title=title,
                url=url,
                snippet=snippet,
                position=position,
                date=date,
                source=source,
                thumbnail=thumbnail,
                metadata=metadata,
            )

        except Exception as e:
            logger.debug(
                "Failed to extract result from SearXNG data",
                position=position,
                error=str(e),
            )
            return None

    def _extract_date_from_item(self, item_data: dict[str, Any]) -> str | None:
        """Extract publication date from SearXNG item if available."""
        try:
            # Check for publishedDate field
            if "publishedDate" in item_data:
                published_date = item_data["publishedDate"]
                if published_date:
                    # SearXNG sometimes returns datetime objects or timestamps
                    if isinstance(published_date, str):
                        return self._clean_text(published_date)
                    else:
                        return str(published_date)

            return None

        except Exception as e:
            logger.debug("Failed to extract date from SearXNG item", error=str(e))
            return None

    def _extract_thumbnail(self, item_data: dict[str, Any]) -> str | None:
        """Extract thumbnail URL from SearXNG item if available."""
        try:
            # Check for thumbnail field
            if "thumbnail" in item_data:
                return item_data["thumbnail"]

            # Check for img_src field (common in image results)
            if "img_src" in item_data:
                return item_data["img_src"]

            return None

        except Exception as e:
            logger.debug("Failed to extract thumbnail from SearXNG item", error=str(e))
            return None

    def _clean_url(self, url: str) -> str | None:
        """
        Clean and validate URL from SearXNG results.

        Args:
            url: Raw URL from SearXNG results

        Returns:
            Cleaned URL or None if invalid
        """
        if not url:
            return None

        # SearXNG URLs are typically clean, but let's validate
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

    def _extract_error_message(self, response: httpx.Response) -> str:
        """
        Extract error message from SearXNG API response.

        Args:
            response: HTTP response from SearXNG API

        Returns:
            Extracted error message or fallback text
        """
        try:
            # Try to parse as JSON first
            error_data = response.json()
            if "error" in error_data:
                return str(error_data["error"])
            elif "message" in error_data:
                return str(error_data["message"])
        except (json.JSONDecodeError, KeyError):
            pass

        # Fallback to response text
        return response.text or f"HTTP {response.status_code} error"

    def _get_api_headers(self) -> dict[str, str]:
        """Get SearXNG-specific API headers."""
        headers = {
            "Accept": "application/json",
            "User-Agent": (
                "WebSearchMCP/1.0.0 (https://github.com/realtimex/web-search-mcp-server)"
            ),
        }
        return headers

    async def search(
        self,
        query: str,
        max_results: int = 10,
        search_type: SearchType = SearchType.SEARCH,
        **kwargs: Any,
    ):
        """
        Override search method to add SearXNG-specific enhancements.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            search_type: Type of search (web or news)
            **kwargs: Additional SearXNG-specific parameters

        Returns:
            SearchResponse with results or error information
        """
        # Call parent search method
        result = await super().search(query, max_results, search_type, **kwargs)

        # Add SearXNG-specific enhancements to successful results
        if result.success and result.results:
            # Separate different result types for better organization
            infobox_results = [
                r for r in result.results if r.metadata.get("result_type") == "infobox"
            ]
            organic_results = [
                r for r in result.results if r.metadata.get("result_type") != "infobox"
            ]

            # Reorder results: Infobox first, then Organic
            reordered_results = infobox_results + organic_results

            # Update positions
            for i, search_result in enumerate(reordered_results, 1):
                search_result.position = i

            result.results = reordered_results

            # Add SearXNG-specific metadata
            if hasattr(result, "metadata") and result.metadata:
                result.metadata.total_available = len(result.results)

        return result
