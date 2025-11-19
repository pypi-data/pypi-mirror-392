"""
Serper search provider implementation.

Implements web search using Serper.dev API which provides Google search results
through a clean JSON API with separate endpoints for web search and news.
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


class SerperProvider(BaseSearchProvider):
    """
    Serper search provider implementation.

    Uses Serper.dev API to provide Google search results through a clean JSON API.
    Requires API key and supports both web search and news search.
    """

    SEARCH_ENDPOINT = "https://google.serper.dev/search"
    NEWS_ENDPOINT = "https://google.serper.dev/news"

    async def _validate_config(self) -> None:
        """Validate Serper configuration (API key required)."""
        if not self.config.api_key:
            raise AuthenticationError(
                "Serper API key is required but not provided",
                provider=self.provider,
            )

        logger.debug("Serper provider configuration validated")

    async def _perform_search(
        self,
        query: str,
        max_results: int,
        search_type: SearchType,
        **kwargs: Any,
    ) -> list[SearchResult]:
        """
        Perform Serper search using their API.

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
            # Select endpoint based on search type
            endpoint = self._get_endpoint(search_type)

            # Build request payload
            payload = self._build_request_payload(
                query, max_results, search_type, **kwargs
            )

            logger.debug(
                "Making Serper search request",
                endpoint=endpoint,
                query=query,
                max_results=max_results,
                search_type=search_type.value,
            )

            # Make the search request
            response = await self.client.post(
                endpoint,
                json=payload,
                headers=self._get_api_headers(),
            )

            # Handle different HTTP status codes
            if response.status_code == 401:
                raise AuthenticationError(
                    "Invalid Serper API key",
                    provider=self.provider,
                )
            elif response.status_code == 429:
                raise QuotaExceededError(
                    "Serper API quota exceeded",
                    provider=self.provider,
                    retry_after=int(response.headers.get("Retry-After", 3600)),
                )
            elif response.status_code >= 400:
                error_text = response.text
                try:
                    error_data = response.json()
                    error_message = error_data.get("message", error_text)
                except:  # noqa: E722
                    error_message = error_text

                raise APIError(
                    f"Serper API error ({response.status_code}): {error_message}",
                    provider=self.provider,
                )

            response.raise_for_status()

            # Parse the JSON response
            response_data = response.json()
            results = self._parse_search_results(
                response_data, max_results, search_type
            )

            logger.info(
                "Serper search completed",
                query=query[:50] + "..." if len(query) > 50 else query,
                results_found=len(results),
                max_results=max_results,
                search_type=search_type.value,
            )

            return results

        except httpx.HTTPStatusError as e:
            logger.error(
                "Serper HTTP error",
                status_code=e.response.status_code,
                response_text=e.response.text[:500],
            )
            raise APIError(
                f"Serper search failed with status {e.response.status_code}",
                provider=self.provider,
            ) from e

        except httpx.RequestError as e:
            logger.error("Serper network error", error=str(e))
            raise NetworkError(
                f"Network error during Serper search: {str(e)}",
                provider=self.provider,
            ) from e

        except json.JSONDecodeError as e:
            logger.error("Serper JSON parsing error", error=str(e))
            raise APIError(
                f"Failed to parse Serper JSON response: {str(e)}",
                provider=self.provider,
            ) from e

        except Exception as e:
            logger.error("Serper unexpected error", error=str(e))
            raise APIError(
                f"Unexpected error during Serper search: {str(e)}",
                provider=self.provider,
            ) from e

    def _get_endpoint(self, search_type: SearchType) -> str:
        """
        Get the appropriate Serper endpoint based on search type.

        Args:
            search_type: Type of search (web or news)

        Returns:
            API endpoint URL
        """
        if search_type == SearchType.NEWS:
            return self.NEWS_ENDPOINT
        else:
            return self.SEARCH_ENDPOINT

    def _build_request_payload(
        self,
        query: str,
        max_results: int,
        search_type: SearchType,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Build the request payload for Serper API.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            search_type: Type of search (web or news)
            **kwargs: Additional parameters

        Returns:
            Dictionary containing the request payload
        """
        payload = {
            "q": query,
            "num": min(max_results, 100),  # Serper supports up to 100 results
        }

        # Add optional parameters
        if "gl" in kwargs:  # Country/region
            payload["gl"] = kwargs["gl"]
        elif "country" in kwargs:
            payload["gl"] = kwargs["country"]
        else:
            payload["gl"] = "us"  # Default to US

        if "hl" in kwargs:  # Language
            payload["hl"] = kwargs["hl"]
        elif "language" in kwargs:
            payload["hl"] = kwargs["language"]
        else:
            payload["hl"] = "en"  # Default to English

        # Add search type specific parameters
        if search_type == SearchType.NEWS:
            # News-specific parameters
            if "tbs" in kwargs:  # Time-based search (e.g., "qdr:d" for past day)
                payload["tbs"] = kwargs["tbs"]

        # Add any additional parameters from kwargs
        for key in ["autocorrect", "page", "type", "engine"]:
            if key in kwargs:
                payload[key] = kwargs[key]

        return payload

    def _parse_search_results(
        self, response_data: dict[str, Any], max_results: int, search_type: SearchType
    ) -> list[SearchResult]:
        """
        Parse Serper API response into SearchResult objects.

        Args:
            response_data: Raw JSON response from Serper API
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
                        result_data, len(results) + 1
                    )
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.warning(
                        "Failed to extract result from Serper data",
                        position=len(results) + 1,
                        error=str(e),
                    )
                    continue

            return results

        except Exception as e:
            logger.error("Failed to parse Serper response", error=str(e))
            raise APIError(
                f"Failed to parse Serper search results: {str(e)}",
                provider=self.provider,
            ) from e

    def _extract_knowledge_graph_result(
        self, kg_data: dict[str, Any]
    ) -> SearchResult | None:
        """
        Extract knowledge graph result from Serper response.

        Args:
            kg_data: Knowledge graph data from Serper API

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
                    "provider": "serper",
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
        Extract answer box result from Serper response.

        Args:
            ab_data: Answer box data from Serper API
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
                    "provider": "serper",
                    "result_type": "answer_box",
                    "extracted_at": "2024-01-15T00:00:00Z",
                },
            )

        except Exception as e:
            logger.debug("Failed to extract answer box result", error=str(e))
            return None

    def _extract_result_from_data(
        self, result_data: dict[str, Any], position: int
    ) -> SearchResult | None:
        """
        Extract a single search result from Serper result data.

        Args:
            result_data: Individual result data from Serper API
            position: Position of this result in the search results

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
                    "Missing required fields in Serper result", result_data=result_data
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
            source = self._extract_domain(url)

            # Extract date if available (common in news results)
            date = result_data.get("date")
            if date:
                date = self._clean_text(date)

            # Build metadata
            metadata = {
                "provider": "serper",
                "result_type": "organic",
                "extracted_at": "2024-01-15T00:00:00Z",
            }

            # Add additional metadata if available
            if "position" in result_data:
                metadata["serper_position"] = result_data["position"]

            return SearchResult(
                title=title,
                url=url,
                snippet=snippet,
                position=position,
                date=date,
                source=source,
                metadata=metadata,
            )

        except Exception as e:
            logger.debug(
                "Failed to extract result from Serper data",
                position=position,
                error=str(e),
            )
            return None

    def _get_api_headers(self) -> dict[str, str]:
        """Get Serper-specific API headers."""
        return {
            "X-API-KEY": self.config.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": (
                "WebSearchMCP/1.0.0 (https://github.com/realtimex/web-search-mcp-server)"
            ),
        }

    def _clean_url(self, url: str) -> str | None:
        """
        Clean and validate URL from Serper results.

        Args:
            url: Raw URL from Serper results

        Returns:
            Cleaned URL or None if invalid
        """
        if not url:
            return None

        # Serper URLs are typically clean, but let's validate
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
    ):  # TODO: Add Typehint SearchResponse
        """
        Override search method to add Serper-specific enhancements.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            search_type: Type of search (web or news)
            **kwargs: Additional Serper-specific parameters

        Returns:
            SearchResponse with results or error information
        """
        # Call parent search method
        result = await super().search(query, max_results, search_type, **kwargs)

        # Add Serper-specific enhancements to successful results
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
                r for r in result.results if r.metadata.get("result_type") == "organic"
            ]

            # Reorder results: Knowledge Graph, Answer Box, then Organic
            reordered_results = (
                knowledge_graph_results + answer_box_results + organic_results
            )

            # Update positions
            for i, search_result in enumerate(reordered_results, 1):
                search_result.position = i

            result.results = reordered_results

            # Add Serper-specific metadata
            result.metadata.total_available = len(result.results)

        return result
