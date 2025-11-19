"""
Google Custom Search provider implementation.

Implements web search using Google Custom Search API with proper
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


class GoogleProvider(BaseSearchProvider):
    """
    Google Custom Search provider implementation.

    Uses Google Custom Search API to perform searches.
    Requires API key and Custom Search Engine ID.
    """

    BASE_URL = "https://www.googleapis.com/customsearch/v1"

    async def _validate_config(self) -> None:
        """Validate Google Custom Search configuration."""
        if not self.config.api_key:
            raise AuthenticationError(
                "Google Custom Search API key is required but not provided",
                provider=self.provider,
            )

        cse_id = self.config.additional_config.get("cse_id")
        if not cse_id:
            raise AuthenticationError(
                "Google Custom Search Engine ID (cse_id) is required but not provided",
                provider=self.provider,
            )

        logger.debug("Google Custom Search provider configuration validated")

    async def _perform_search(
        self,
        query: str,
        max_results: int,
        search_type: SearchType,
        **kwargs: Any,
    ) -> list[SearchResult]:
        """
        Perform Google Custom Search using their API.

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
            AuthenticationError: If API key or CSE ID is invalid
            QuotaExceededError: If API quota is exceeded
        """
        if not self.client:
            raise APIError("HTTP client not initialized", provider=self.provider)

        try:
            # Build request parameters
            params = self._build_request_params(
                query, max_results, search_type, **kwargs
            )

            logger.debug(
                "Making Google Custom Search request",
                query=query,
                max_results=max_results,
                search_type=search_type.value,
            )

            # Make the search request
            response = await self.client.get(
                self.BASE_URL,
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
                    f"Invalid Google API key: {error_message}",
                    provider=self.provider,
                )
            elif response.status_code == 403:
                error_message = self._extract_error_message(response)
                # Check if it's a quota issue or permission issue
                if "quota" in error_message.lower() or "limit" in error_message.lower():
                    raise QuotaExceededError(
                        f"Google API quota exceeded: {error_message}",
                        provider=self.provider,
                        retry_after=86400,  # Daily quota, retry after 24 hours
                    )
                else:
                    raise AuthenticationError(
                        f"Google API access forbidden: {error_message}",
                        provider=self.provider,
                    )
            elif response.status_code == 429:
                error_message = self._extract_error_message(response)
                raise QuotaExceededError(
                    f"Google API rate limit exceeded: {error_message}",
                    provider=self.provider,
                    retry_after=int(response.headers.get("Retry-After", 3600)),
                )
            elif response.status_code >= 500:
                error_message = self._extract_error_message(response)
                raise APIError(
                    f"Google API server error ({response.status_code}): {error_message}",
                    provider=self.provider,
                )
            elif response.status_code >= 400:
                error_message = self._extract_error_message(response)
                raise APIError(
                    f"Google API error ({response.status_code}): {error_message}",
                    provider=self.provider,
                )

            response.raise_for_status()

            # Parse the JSON response
            response_data = response.json()
            results = self._parse_search_results(response_data, max_results)

            logger.info(
                "Google Custom Search completed",
                query=query[:50] + "..." if len(query) > 50 else query,
                results_found=len(results),
                max_results=max_results,
                total_results=response_data.get("searchInformation", {}).get(
                    "totalResults", 0
                ),
            )

            return results

        except httpx.HTTPStatusError as e:
            logger.error(
                "Google Custom Search HTTP error",
                status_code=e.response.status_code,
                response_text=e.response.text[:500],
            )
            raise APIError(
                f"Google Custom Search failed with status {e.response.status_code}",
                provider=self.provider,
            ) from e

        except httpx.RequestError as e:
            logger.error("Google Custom Search network error", error=str(e))
            raise NetworkError(
                f"Network error during Google Custom Search: {str(e)}",
                provider=self.provider,
            ) from e

        except json.JSONDecodeError as e:
            logger.error("Google Custom Search JSON parsing error", error=str(e))
            raise APIError(
                f"Failed to parse Google Custom Search JSON response: {str(e)}",
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
            logger.error("Google Custom Search unexpected error", error=str(e))
            raise APIError(
                f"Unexpected error during Google Custom Search: {str(e)}",
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
        Build the request parameters for Google Custom Search API.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            search_type: Type of search (web or news)
            **kwargs: Additional parameters

        Returns:
            Dictionary containing the request parameters
        """
        cse_id = self.config.additional_config.get("cse_id")

        params = {
            "key": self.config.api_key,
            "cx": cse_id,
            "q": query,
            "num": min(max_results, 10),  # Google CSE supports max 10 per request
            "safe": "medium",  # Safe search level
            "fields": "items(title,link,snippet,displayLink,formattedUrl,pagemap),searchInformation(totalResults,searchTime)",
        }

        # Add search type specific parameters
        if search_type == SearchType.NEWS:
            # Use news-specific search parameters
            params["tbm"] = "nws"  # News search
            params["sort"] = "date"  # Sort by date for news

        # Add optional parameters from kwargs
        if "language" in kwargs:
            params["lr"] = f"lang_{kwargs['language']}"
        elif "hl" in kwargs:
            params["hl"] = kwargs["hl"]
        else:
            params["hl"] = "en"  # Default to English

        if "country" in kwargs:
            params["gl"] = kwargs["country"]
        elif "gl" in kwargs:
            params["gl"] = kwargs["gl"]
        else:
            params["gl"] = "us"  # Default to US

        # Date range for news searches
        if search_type == SearchType.NEWS and "dateRestrict" in kwargs:
            params["dateRestrict"] = kwargs["dateRestrict"]

        # Site restriction
        if "site" in kwargs:
            params["siteSearch"] = kwargs["site"]

        # File type restriction
        if "filetype" in kwargs:
            params["fileType"] = kwargs["filetype"]

        return params

    def _parse_search_results(
        self, response_data: dict[str, Any], max_results: int
    ) -> list[SearchResult]:
        """
        Parse Google Custom Search API response into SearchResult objects.

        Args:
            response_data: Raw JSON response from Google Custom Search API
            max_results: Maximum number of results to extract

        Returns:
            List of SearchResult objects

        Raises:
            APIError: If response parsing fails
        """
        try:
            results = []
            items = response_data.get("items", [])

            if not items:
                logger.warning("No results found in Google Custom Search response")
                return []

            for position, item_data in enumerate(items[:max_results], 1):
                try:
                    result = self._extract_result_from_data(item_data, position)
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.warning(
                        "Failed to extract result from Google Custom Search data",
                        position=position,
                        error=str(e),
                    )
                    continue

            return results

        except Exception as e:
            logger.error("Failed to parse Google Custom Search response", error=str(e))
            raise APIError(
                f"Failed to parse Google Custom Search results: {str(e)}",
                provider=self.provider,
            ) from e

    def _extract_result_from_data(
        self, item_data: dict[str, Any], position: int
    ) -> SearchResult | None:
        """
        Extract a single search result from Google Custom Search item data.

        Args:
            item_data: Individual result data from Google Custom Search API
            position: Position of this result in the search results

        Returns:
            SearchResult object or None if extraction fails
        """
        try:
            # Extract required fields
            url = item_data.get("link")
            title = item_data.get("title")
            snippet = item_data.get("snippet")

            if not url or not title:
                logger.debug(
                    "Missing required fields in Google Custom Search result",
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
            source = item_data.get("displayLink") or self._extract_domain(url)

            # Extract date if available (common in news results)
            date = self._extract_date_from_item(item_data)

            # Extract thumbnail if available
            thumbnail = self._extract_thumbnail(item_data)

            # Build metadata
            metadata = {
                "provider": "google",
                "extracted_at": "2024-01-15T00:00:00Z",
                "formatted_url": item_data.get("formattedUrl"),
            }

            # Add pagemap data if available
            pagemap = item_data.get("pagemap", {})
            if pagemap:
                metadata["pagemap"] = pagemap

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
                "Failed to extract result from Google Custom Search data",
                position=position,
                error=str(e),
            )
            return None

    def _extract_date_from_item(self, item_data: dict[str, Any]) -> str | None:
        """Extract publication date from Google Custom Search item if available."""
        try:
            # Check pagemap for structured data
            pagemap = item_data.get("pagemap", {})

            # Try different structured data sources
            for source in ["newsarticle", "article", "webpage", "metatags"]:
                if source in pagemap:
                    items = pagemap[source]
                    if isinstance(items, list) and items:
                        item = items[0]
                        # Try different date fields
                        for date_field in [
                            "datepublished",
                            "publishdate",
                            "date",
                            "pubdate",
                        ]:
                            if date_field in item:
                                return self._clean_text(item[date_field])

            return None

        except Exception as e:
            logger.debug(
                "Failed to extract date from Google Custom Search item", error=str(e)
            )
            return None

    def _extract_thumbnail(self, item_data: dict[str, Any]) -> str | None:
        """Extract thumbnail URL from Google Custom Search item if available."""
        try:
            pagemap = item_data.get("pagemap", {})

            # Try different image sources
            for source in ["cse_thumbnail", "cse_image", "imageobject", "metatags"]:
                if source in pagemap:
                    items = pagemap[source]
                    if isinstance(items, list) and items:
                        item = items[0]
                        # Try different image fields
                        for img_field in ["src", "url", "image", "og:image"]:
                            if img_field in item:
                                return item[img_field]

            return None

        except Exception as e:
            logger.debug(
                "Failed to extract thumbnail from Google Custom Search item",
                error=str(e),
            )
            return None

    def _extract_error_message(self, response: httpx.Response) -> str:
        """
        Extract error message from Google Custom Search API response.

        Args:
            response: HTTP response from Google Custom Search API

        Returns:
            Extracted error message or fallback text
        """
        try:
            error_data = response.json()
            # Handle Google's error format: {"error": {"message": "...", "code": 400}}
            if "error" in error_data:
                error_info = error_data["error"]
                if isinstance(error_info, dict):
                    message = error_info.get("message", "")
                    code = error_info.get("code", "")
                    if message:
                        return f"{message} (Code: {code})" if code else message
                elif isinstance(error_info, str):
                    return error_info
            # Fallback to response text
            return response.text
        except (json.JSONDecodeError, KeyError):
            return response.text or f"HTTP {response.status_code} error"

    def _get_api_headers(self) -> dict[str, str]:
        """Get Google Custom Search-specific API headers."""
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
        Override search method to add Google Custom Search-specific enhancements.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            search_type: Type of search (web or news)
            **kwargs: Additional Google Custom Search-specific parameters

        Returns:
            SearchResponse with results or error information
        """
        # Call parent search method
        result = await super().search(query, max_results, search_type, **kwargs)

        # Add Google Custom Search-specific enhancements to successful results
        if result.success and result.results:
            # Sort results by position (should already be sorted, but ensure consistency)
            result.results.sort(key=lambda r: r.position)

            # Add Google-specific metadata
            if hasattr(result, "metadata") and result.metadata:
                result.metadata.total_available = len(result.results)

        return result
