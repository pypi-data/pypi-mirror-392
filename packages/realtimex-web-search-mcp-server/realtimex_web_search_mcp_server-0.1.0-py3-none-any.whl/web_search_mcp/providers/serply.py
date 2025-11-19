"""
Serply Search provider implementation.

Implements web search using Serply API with proper
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


class SerplyProvider(BaseSearchProvider):
    """
    Serply Search provider implementation.

    Uses Serply API to perform searches with Google-like results.
    Requires API key for authentication.
    """

    BASE_URL = "https://api.serply.io/v1/search"
    NEWS_URL = "https://api.serply.io/v1/news"

    async def _validate_config(self) -> None:
        """Validate Serply Search configuration."""
        if not self.config.api_key:
            raise AuthenticationError(
                "Serply API key is required but not provided",
                provider=self.provider,
            )

        logger.debug("Serply Search provider configuration validated")

    async def _perform_search(
        self,
        query: str,
        max_results: int,
        search_type: SearchType,
        **kwargs: Any,
    ) -> list[SearchResult]:
        """
        Perform Serply Search using their API.

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
                "Making Serply Search request",
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
                    f"Invalid Serply API key: {error_message}",
                    provider=self.provider,
                )
            elif response.status_code == 403:
                error_message = self._extract_error_message(response)
                raise AuthenticationError(
                    f"Serply API access forbidden: {error_message}",
                    provider=self.provider,
                )
            elif response.status_code == 429:
                error_message = self._extract_error_message(response)
                raise QuotaExceededError(
                    f"Serply API rate limit exceeded: {error_message}",
                    provider=self.provider,
                    retry_after=int(response.headers.get("Retry-After", 3600)),
                )
            elif response.status_code == 402:
                error_message = self._extract_error_message(response)
                raise QuotaExceededError(
                    f"Serply API quota exceeded: {error_message}",
                    provider=self.provider,
                    retry_after=86400,  # Daily quota, retry after 24 hours
                )
            elif response.status_code >= 500:
                error_message = self._extract_error_message(response)
                raise APIError(
                    f"Serply API server error ({response.status_code}): {error_message}",
                    provider=self.provider,
                )
            elif response.status_code >= 400:
                error_message = self._extract_error_message(response)
                raise APIError(
                    f"Serply API error ({response.status_code}): {error_message}",
                    provider=self.provider,
                )

            response.raise_for_status()

            # Parse the JSON response
            response_data = response.json()
            results = self._parse_search_results(
                response_data, max_results, search_type
            )

            logger.info(
                "Serply Search completed",
                query=query[:50] + "..." if len(query) > 50 else query,
                results_found=len(results),
                max_results=max_results,
                search_type=search_type.value,
            )

            return results

        except httpx.HTTPStatusError as e:
            logger.error(
                "Serply Search HTTP error",
                status_code=e.response.status_code,
                response_text=e.response.text[:500],
            )
            raise APIError(
                f"Serply Search failed with status {e.response.status_code}",
                provider=self.provider,
            ) from e

        except httpx.RequestError as e:
            logger.error("Serply Search network error", error=str(e))
            raise NetworkError(
                f"Network error during Serply Search: {str(e)}",
                provider=self.provider,
            ) from e

        except json.JSONDecodeError as e:
            logger.error("Serply Search JSON parsing error", error=str(e))
            raise APIError(
                f"Failed to parse Serply Search JSON response: {str(e)}",
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
            logger.error("Serply Search unexpected error", error=str(e))
            raise APIError(
                f"Unexpected error during Serply Search: {str(e)}",
                provider=self.provider,
            ) from e

    def _get_endpoint(self, search_type: SearchType) -> str:
        """
        Get the appropriate Serply endpoint based on search type.

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
        Build the request parameters for Serply API.

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
            "num": min(max_results, 100),  # Serply supports up to 100 per request
            "hl": "en",  # Language
            "gl": "us",  # Country/region
        }

        # Add search type specific parameters
        if search_type == SearchType.NEWS:
            # News-specific parameters
            params["tbm"] = "nws"  # News search mode
            params["tbs"] = "qdr:d"  # Recent news (past day)
        else:
            # Web search specific parameters
            params["safe"] = "medium"  # Safe search level

        # Add optional parameters from kwargs
        if "language" in kwargs:
            params["hl"] = kwargs["language"]
        elif "hl" in kwargs:
            params["hl"] = kwargs["hl"]

        if "country" in kwargs:
            params["gl"] = kwargs["country"]
        elif "gl" in kwargs:
            params["gl"] = kwargs["gl"]

        # Safe search level for web searches
        if search_type == SearchType.SEARCH and "safe_search" in kwargs:
            safe_search_map = {"off": "off", "moderate": "medium", "strict": "high"}
            params["safe"] = safe_search_map.get(
                kwargs["safe_search"].lower(), "medium"
            )

        # Time-based search for news
        if search_type == SearchType.NEWS and "time_range" in kwargs:
            time_range_map = {
                "hour": "qdr:h",
                "day": "qdr:d",
                "week": "qdr:w",
                "month": "qdr:m",
                "year": "qdr:y",
            }
            params["tbs"] = time_range_map.get(kwargs["time_range"].lower(), "qdr:d")

        # Site restriction
        if "site" in kwargs:
            params["q"] = f"site:{kwargs['site']} {query}"

        # File type restriction
        if "filetype" in kwargs:
            params["q"] = f"filetype:{kwargs['filetype']} {query}"

        return params

    def _parse_search_results(
        self, response_data: dict[str, Any], max_results: int, search_type: SearchType
    ) -> list[SearchResult]:
        """
        Parse Serply API response into SearchResult objects.

        Args:
            response_data: Raw JSON response from Serply API
            max_results: Maximum number of results to extract
            search_type: Type of search performed

        Returns:
            List of SearchResult objects

        Raises:
            APIError: If response parsing fails
        """
        try:
            results = []

            # Handle knowledge graph results first (if available)
            knowledge_graph = response_data.get("knowledgeGraph")
            if knowledge_graph and len(results) < max_results:
                kg_result = self._extract_knowledge_graph_result(knowledge_graph)
                if kg_result:
                    results.append(kg_result)

            # Handle answer box results (if available)
            answer_box = response_data.get("answerBox")
            if answer_box and len(results) < max_results:
                ab_result = self._extract_answer_box_result(
                    answer_box, len(results) + 1
                )
                if ab_result:
                    results.append(ab_result)

            # Handle organic results
            organic_results = response_data.get("organic", [])
            if search_type == SearchType.NEWS:
                # For news, also check the 'news' field
                news_results = response_data.get("news", [])
                organic_results.extend(news_results)

            for result_data in organic_results:
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
                        "Failed to extract result from Serply data",
                        position=len(results) + 1,
                        error=str(e),
                    )
                    continue

            return results

        except Exception as e:
            logger.error("Failed to parse Serply response", error=str(e))
            raise APIError(
                f"Failed to parse Serply search results: {str(e)}",
                provider=self.provider,
            ) from e

    def _extract_knowledge_graph_result(
        self, kg_data: dict[str, Any]
    ) -> SearchResult | None:
        """
        Extract knowledge graph result from Serply response.

        Args:
            kg_data: Knowledge graph data from Serply API

        Returns:
            SearchResult object or None if extraction fails
        """
        try:
            title = kg_data.get("title")
            description = kg_data.get("description")
            url = kg_data.get("descriptionLink") or kg_data.get("website")

            if not title or not url:
                return None

            # Clean and validate URL
            url = self._clean_url(url)
            if not url:
                return None

            snippet = (
                self._clean_text(description)
                if description
                else "Knowledge Graph result"
            )
            source = self._extract_domain(url)

            return SearchResult(
                title=f"📚 {self._clean_text(title)}",  # Add emoji to distinguish KG results
                url=url,
                snippet=snippet,
                position=1,  # Knowledge graph typically appears first
                date=None,
                source=source,
                metadata={
                    "provider": "serply",
                    "result_type": "knowledge_graph",
                    "extracted_at": "2024-01-15T00:00:00Z",
                },
            )

        except Exception as e:
            logger.debug("Failed to extract knowledge graph result", error=str(e))
            return None

    def _extract_answer_box_result(
        self, ab_data: dict[str, Any], position: int
    ) -> SearchResult | None:
        """
        Extract answer box result from Serply response.

        Args:
            ab_data: Answer box data from Serply API
            position: Position for this result

        Returns:
            SearchResult object or None if extraction fails
        """
        try:
            title = ab_data.get("title")
            answer = ab_data.get("answer")
            snippet = ab_data.get("snippet")
            url = ab_data.get("link")

            if not answer and not snippet:
                return None

            # Use answer or snippet as content
            content = answer or snippet
            if not content:
                return None

            # Create a title if not provided
            if not title:
                title = "Answer Box Result"

            # Use a default URL if not provided
            if not url:
                url = "https://www.google.com"
            else:
                url = self._clean_url(url)
                if not url:
                    url = "https://www.google.com"

            snippet_text = self._clean_text(content)
            source = self._extract_domain(url)

            return SearchResult(
                title=f"💡 {self._clean_text(title)}",  # Add emoji to distinguish answer box
                url=url,
                snippet=snippet_text,
                position=position,
                date=None,
                source=source,
                metadata={
                    "provider": "serply",
                    "result_type": "answer_box",
                    "extracted_at": "2024-01-15T00:00:00Z",
                },
            )

        except Exception as e:
            logger.debug("Failed to extract answer box result", error=str(e))
            return None

    def _extract_result_from_data(
        self, result_data: dict[str, Any], position: int, search_type: SearchType
    ) -> SearchResult | None:
        """
        Extract a single search result from Serply result data.

        Args:
            result_data: Individual result data from Serply API
            position: Position of this result in the search results
            search_type: Type of search performed

        Returns:
            SearchResult object or None if extraction fails
        """
        try:
            # Extract required fields
            url = result_data.get("link")
            title = result_data.get("title")
            snippet = result_data.get("snippet")

            if not url or not title:
                logger.debug(
                    "Missing required fields in Serply result",
                    result_data=result_data,
                )
                return None

            # Clean and validate URL
            url = self._clean_url(url)
            if not url:
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
            source = result_data.get("displayLink") or self._extract_domain(url)

            # Extract date if available (common in news results)
            date = self._extract_date_from_item(result_data, search_type)

            # Extract thumbnail if available
            thumbnail = self._extract_thumbnail(result_data)

            # Build metadata
            metadata = {
                "provider": "serply",
                "search_type": search_type.value,
                "extracted_at": "2024-01-15T00:00:00Z",
            }

            # Add additional metadata if available
            if "position" in result_data:
                metadata["serply_position"] = result_data["position"]

            if "sitelinks" in result_data:
                metadata["has_sitelinks"] = True

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
                "Failed to extract result from Serply data",
                position=position,
                error=str(e),
            )
            return None

    def _extract_date_from_item(
        self, item_data: dict[str, Any], search_type: SearchType
    ) -> str | None:
        """Extract publication date from Serply item if available."""
        try:
            # News results might have date field
            if search_type == SearchType.NEWS and "date" in item_data:
                return self._clean_text(item_data["date"])

            # Check for other date fields
            for date_field in ["published", "datePublished", "timestamp"]:
                if date_field in item_data:
                    return self._clean_text(item_data[date_field])

            return None

        except Exception as e:
            logger.debug("Failed to extract date from Serply item", error=str(e))
            return None

    def _extract_thumbnail(self, item_data: dict[str, Any]) -> str | None:
        """Extract thumbnail URL from Serply item if available."""
        try:
            # Check for thumbnail field
            if "thumbnail" in item_data:
                return item_data["thumbnail"]

            # Check for image field
            if "image" in item_data:
                return item_data["image"]

            return None

        except Exception as e:
            logger.debug("Failed to extract thumbnail from Serply item", error=str(e))
            return None

    def _clean_url(self, url: str) -> str | None:
        """
        Clean and validate URL from Serply results.

        Args:
            url: Raw URL from Serply results

        Returns:
            Cleaned URL or None if invalid
        """
        if not url:
            return None

        # Serply URLs are typically clean, but let's validate
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
        Extract error message from Serply API response.

        Args:
            response: HTTP response from Serply API

        Returns:
            Extracted error message or fallback text
        """
        try:
            error_data = response.json()
            # Handle Serply's error format: {"error": "message"} or {"message": "error"}
            if "error" in error_data:
                return str(error_data["error"])
            elif "message" in error_data:
                return str(error_data["message"])
            # Fallback to response text
            return response.text
        except (json.JSONDecodeError, KeyError):
            return response.text or f"HTTP {response.status_code} error"

    def _get_api_headers(self) -> dict[str, str]:
        """Get Serply-specific API headers."""
        headers = {
            "X-API-KEY": self.config.api_key,
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
        Override search method to add Serply-specific enhancements.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            search_type: Type of search (web or news)
            **kwargs: Additional Serply-specific parameters

        Returns:
            SearchResponse with results or error information
        """
        # Call parent search method
        result = await super().search(query, max_results, search_type, **kwargs)

        # Add Serply-specific enhancements to successful results
        if result.success and result.results:
            # Separate different result types for better organization
            knowledge_graph_results = [
                r
                for r in result.results
                if r.metadata.get("result_type") == "knowledge_graph"
            ]
            answer_box_results = [
                r
                for r in result.results
                if r.metadata.get("result_type") == "answer_box"
            ]
            organic_results = [
                r
                for r in result.results
                if r.metadata.get("result_type")
                not in ["knowledge_graph", "answer_box"]
            ]

            # Reorder results: Knowledge Graph, Answer Box, then Organic
            reordered_results = (
                knowledge_graph_results + answer_box_results + organic_results
            )

            # Update positions
            for i, search_result in enumerate(reordered_results, 1):
                search_result.position = i

            result.results = reordered_results

            # Add Serply-specific metadata
            if hasattr(result, "metadata") and result.metadata:
                result.metadata.total_available = len(result.results)

        return result
