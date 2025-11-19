"""
Bing Search provider implementation.

Implements web search using Microsoft Bing Search API with proper
result parsing and comprehensive error handling.
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
    ValidationError,
)
from .base import BaseSearchProvider

logger = structlog.get_logger(__name__)


class BingProvider(BaseSearchProvider):
    """
    Bing Search provider implementation.

    Uses Microsoft Bing Search API to perform searches.
    Requires API key (Ocp-Apim-Subscription-Key).
    """

    BASE_URL = "https://api.bing.microsoft.com/v7.0/search"
    NEWS_URL = "https://api.bing.microsoft.com/v7.0/news/search"

    async def _validate_config(self) -> None:
        """Validate Bing Search configuration."""
        if not self.config.api_key:
            raise AuthenticationError(
                "Bing Search API key is required but not provided",
                provider=self.provider,
            )

        logger.debug("Bing Search provider configuration validated")

    async def _perform_search(
        self,
        query: str,
        max_results: int,
        search_type: SearchType,
        **kwargs: Any,
    ) -> list[SearchResult]:
        """
        Perform Bing Search using their API.

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
            # Select endpoint and build parameters
            endpoint = self._get_endpoint(search_type)
            params = self._build_request_params(
                query, max_results, search_type, **kwargs
            )

            logger.debug(
                "Making Bing Search request",
                endpoint=endpoint,
                query=query,
                max_results=max_results,
                search_type=search_type.value,
            )

            # Make the search request
            response = await self.client.get(
                endpoint,
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
            elif response.status_code == 401:
                error_message = self._extract_error_message(response)
                raise AuthenticationError(
                    f"Invalid Bing API key: {error_message}",
                    provider=self.provider,
                )
            elif response.status_code == 403:
                error_message = self._extract_error_message(response)
                raise AuthenticationError(
                    f"Bing API access forbidden: {error_message}",
                    provider=self.provider,
                )
            elif response.status_code == 429:
                error_message = self._extract_error_message(response)
                raise QuotaExceededError(
                    f"Bing API rate limit exceeded: {error_message}",
                    provider=self.provider,
                    retry_after=int(response.headers.get("Retry-After", 3600)),
                )
            elif response.status_code == 503:
                error_message = self._extract_error_message(response)
                raise QuotaExceededError(
                    f"Bing API quota exceeded: {error_message}",
                    provider=self.provider,
                    retry_after=86400,  # Daily quota, retry after 24 hours
                )
            elif response.status_code >= 500:
                error_message = self._extract_error_message(response)
                raise APIError(
                    f"Bing API server error ({response.status_code}): {error_message}",
                    provider=self.provider,
                )
            elif response.status_code >= 400:
                error_message = self._extract_error_message(response)
                raise APIError(
                    f"Bing API error ({response.status_code}): {error_message}",
                    provider=self.provider,
                )

            response.raise_for_status()

            # Parse the JSON response
            response_data = response.json()
            results = self._parse_search_results(
                response_data, max_results, search_type
            )

            logger.info(
                "Bing Search completed",
                query=query[:50] + "..." if len(query) > 50 else query,
                results_found=len(results),
                max_results=max_results,
                search_type=search_type.value,
            )

            return results

        except httpx.HTTPStatusError as e:
            logger.error(
                "Bing Search HTTP error",
                status_code=e.response.status_code,
                response_text=e.response.text[:500],
            )
            raise APIError(
                f"Bing Search failed with status {e.response.status_code}",
                provider=self.provider,
            ) from e

        except httpx.RequestError as e:
            logger.error("Bing Search network error", error=str(e))
            raise NetworkError(
                f"Network error during Bing Search: {str(e)}",
                provider=self.provider,
            ) from e

        except json.JSONDecodeError as e:
            logger.error("Bing Search JSON parsing error", error=str(e))
            raise APIError(
                f"Failed to parse Bing Search JSON response: {str(e)}",
                provider=self.provider,
            ) from e

        except (
            ValidationError,
            AuthenticationError,
            QuotaExceededError,
            APIError,
            NetworkError,
        ):
            # Re-raise our custom exceptions without modification
            raise

        except Exception as e:
            logger.error("Bing Search unexpected error", error=str(e))
            raise APIError(
                f"Unexpected error during Bing Search: {str(e)}",
                provider=self.provider,
            ) from e

    def _get_endpoint(self, search_type: SearchType) -> str:
        """
        Get the appropriate Bing endpoint based on search type.

        Args:
            search_type: Type of search (web or news)

        Returns:
            API endpoint URL
        """
        if search_type == SearchType.NEWS:
            return self.NEWS_URL
        else:
            return self.BASE_URL

    def _build_request_params(
        self,
        query: str,
        max_results: int,
        search_type: SearchType,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Build the request parameters for Bing Search API.

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
            "count": min(max_results, 50),  # Bing supports up to 50 per request
            "offset": 0,
            "mkt": "en-US",  # Market/locale
            "safeSearch": "Moderate",  # Safe search level
        }

        # Add search type specific parameters
        if search_type == SearchType.NEWS:
            # News-specific parameters
            params["sortBy"] = "Date"  # Sort news by date
            params["freshness"] = "Day"  # Recent news
        else:
            # Web search specific parameters
            params["responseFilter"] = "Webpages"
            params["textDecorations"] = False  # No text highlighting
            params["textFormat"] = "Raw"  # Raw text format

        # Add optional parameters from kwargs
        if "market" in kwargs:
            params["mkt"] = kwargs["market"]
        elif "mkt" in kwargs:
            params["mkt"] = kwargs["mkt"]

        if "country" in kwargs:
            params["cc"] = kwargs["country"]
        elif "cc" in kwargs:
            params["cc"] = kwargs["cc"]

        if "language" in kwargs:
            params["setLang"] = kwargs["language"]
        elif "setLang" in kwargs:
            params["setLang"] = kwargs["setLang"]

        # Safe search level
        if "safe_search" in kwargs:
            safe_search_map = {
                "off": "Off",
                "moderate": "Moderate",
                "strict": "Strict",
            }
            params["safeSearch"] = safe_search_map.get(
                kwargs["safe_search"].lower(), "Moderate"
            )

        # Freshness for news searches
        if search_type == SearchType.NEWS and "freshness" in kwargs:
            freshness_map = {
                "day": "Day",
                "week": "Week",
                "month": "Month",
            }
            params["freshness"] = freshness_map.get(kwargs["freshness"].lower(), "Day")

        # Site restriction
        if "site" in kwargs:
            params["q"] = f"site:{kwargs['site']} {query}"

        return params

    def _parse_search_results(
        self, response_data: dict[str, Any], max_results: int, search_type: SearchType
    ) -> list[SearchResult]:
        """
        Parse Bing Search API response into SearchResult objects.

        Args:
            response_data: Raw JSON response from Bing Search API
            max_results: Maximum number of results to extract
            search_type: Type of search performed

        Returns:
            List of SearchResult objects

        Raises:
            APIError: If response parsing fails
        """
        try:
            results = []

            # Get results based on search type
            if search_type == SearchType.NEWS:
                items = response_data.get("value", [])
            else:
                # Web search results are in webPages.value
                web_pages = response_data.get("webPages", {})
                items = web_pages.get("value", [])

            if not items:
                logger.warning("No results found in Bing Search response")
                return []

            for position, item_data in enumerate(items[:max_results], 1):
                try:
                    result = self._extract_result_from_data(
                        item_data, position, search_type
                    )
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.warning(
                        "Failed to extract result from Bing Search data",
                        position=position,
                        error=str(e),
                    )
                    continue

            return results

        except Exception as e:
            logger.error("Failed to parse Bing Search response", error=str(e))
            raise APIError(
                f"Failed to parse Bing Search results: {str(e)}",
                provider=self.provider,
            ) from e

    def _extract_result_from_data(
        self, item_data: dict[str, Any], position: int, search_type: SearchType
    ) -> SearchResult | None:
        """
        Extract a single search result from Bing Search item data.

        Args:
            item_data: Individual result data from Bing Search API
            position: Position of this result in the search results
            search_type: Type of search performed

        Returns:
            SearchResult object or None if extraction fails
        """
        try:
            # Extract required fields
            url = item_data.get("url")
            title = item_data.get("name")  # Bing uses 'name' for title
            snippet = item_data.get("snippet")

            if not url or not title:
                logger.debug(
                    "Missing required fields in Bing Search result",
                    result_data=item_data,
                )
                return None

            # Clean title and snippet
            title = self._clean_text(title)
            snippet = (
                self._clean_text(snippet) if snippet else "No description available"
            )

            # Truncate snippet if too long
            if len(snippet) > 300:
                snippet = snippet[:297] + "..."

            # Extract source domain
            source = item_data.get("displayUrl") or self._extract_domain(url)

            # Extract date if available (common in news results)
            date = self._extract_date_from_item(item_data, search_type)

            # Extract thumbnail if available
            thumbnail = self._extract_thumbnail(item_data)

            # Build metadata
            metadata = {
                "provider": "bing",
                "extracted_at": "2024-01-15T00:00:00Z",
                "search_type": search_type.value,
            }

            # Add Bing-specific metadata
            if "id" in item_data:
                metadata["bing_id"] = item_data["id"]

            if "displayUrl" in item_data:
                metadata["display_url"] = item_data["displayUrl"]

            # Add news-specific metadata
            if search_type == SearchType.NEWS:
                if "provider" in item_data:
                    providers = item_data["provider"]
                    if isinstance(providers, list) and providers:
                        metadata["news_provider"] = providers[0].get("name")

                if "category" in item_data:
                    metadata["news_category"] = item_data["category"]

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
                "Failed to extract result from Bing Search data",
                position=position,
                error=str(e),
            )
            return None

    def _extract_date_from_item(
        self, item_data: dict[str, Any], search_type: SearchType
    ) -> str | None:
        """Extract publication date from Bing Search item if available."""
        try:
            # News results have datePublished field
            if search_type == SearchType.NEWS and "datePublished" in item_data:
                return self._clean_text(item_data["datePublished"])

            # Web results might have dateLastCrawled
            if "dateLastCrawled" in item_data:
                return self._clean_text(item_data["dateLastCrawled"])

            return None

        except Exception as e:
            logger.debug("Failed to extract date from Bing Search item", error=str(e))
            return None

    def _extract_thumbnail(self, item_data: dict[str, Any]) -> str | None:
        """Extract thumbnail URL from Bing Search item if available."""
        try:
            # Check for image thumbnail
            if "image" in item_data:
                image_data = item_data["image"]
                if isinstance(image_data, dict) and "thumbnail" in image_data:
                    thumbnail_data = image_data["thumbnail"]
                    if (
                        isinstance(thumbnail_data, dict)
                        and "contentUrl" in thumbnail_data
                    ):
                        return thumbnail_data["contentUrl"]

            # Check for direct thumbnail field
            if "thumbnail" in item_data:
                thumbnail_data = item_data["thumbnail"]
                if isinstance(thumbnail_data, dict) and "contentUrl" in thumbnail_data:
                    return thumbnail_data["contentUrl"]

            return None

        except Exception as e:
            logger.debug(
                "Failed to extract thumbnail from Bing Search item", error=str(e)
            )
            return None

    def _extract_error_message(self, response: httpx.Response) -> str:
        """
        Extract error message from Bing Search API response.

        Args:
            response: HTTP response from Bing Search API

        Returns:
            Extracted error message or fallback text
        """
        try:
            error_data = response.json()
            # Handle Bing's error format: {"errors": [{"message": "...", "code": "..."}]}
            if "errors" in error_data:
                errors = error_data["errors"]
                if isinstance(errors, list) and errors:
                    error = errors[0]
                    if isinstance(error, dict):
                        message = error.get("message", "")
                        code = error.get("code", "")
                        if message:
                            return f"{message} (Code: {code})" if code else message

            # Handle direct error format: {"error": {"message": "...", "code": "..."}}
            elif "error" in error_data:
                error_info = error_data["error"]
                if isinstance(error_info, dict):
                    message = error_info.get("message", "")
                    code = error_info.get("code", "")
                    if message:
                        return f"{message} (Code: {code})" if code else message

            # Fallback to response text
            return response.text
        except (json.JSONDecodeError, KeyError):
            return response.text or f"HTTP {response.status_code} error"

    def _get_api_headers(self) -> dict[str, str]:
        """Get Bing Search-specific API headers."""
        headers = {
            "Ocp-Apim-Subscription-Key": self.config.api_key,
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
        Override search method to add Bing Search-specific enhancements.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            search_type: Type of search (web or news)
            **kwargs: Additional Bing Search-specific parameters

        Returns:
            SearchResponse with results or error information
        """
        # Call parent search method
        result = await super().search(query, max_results, search_type, **kwargs)

        # Add Bing Search-specific enhancements to successful results
        if result.success and result.results:
            # Sort results by position (should already be sorted, but ensure consistency)
            result.results.sort(key=lambda r: r.position)

            # Add Bing-specific metadata
            if hasattr(result, "metadata") and result.metadata:
                result.metadata.total_available = len(result.results)

        return result
