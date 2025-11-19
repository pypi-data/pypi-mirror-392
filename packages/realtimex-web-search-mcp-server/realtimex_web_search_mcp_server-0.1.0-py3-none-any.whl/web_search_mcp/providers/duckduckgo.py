"""
DuckDuckGo search provider implementation.

Implements web search using DuckDuckGo's HTML interface with proper
parsing and result extraction. No API key required.
"""

import re
from typing import Any
from urllib.parse import quote_plus

import httpx
import structlog
from bs4 import BeautifulSoup

from ..models import APIError, NetworkError, SearchResult, SearchType
from .base import BaseSearchProvider

logger = structlog.get_logger(__name__)


class DuckDuckGoProvider(BaseSearchProvider):
    """
    DuckDuckGo search provider implementation.

    Uses DuckDuckGo's HTML search interface to perform searches.
    No API key required, but rate limiting applies.
    """

    BASE_URL = "https://html.duckduckgo.com/html"

    async def _validate_config(self) -> None:
        """Validate DuckDuckGo configuration (no API key required)."""
        # DuckDuckGo requires no configuration
        logger.debug("DuckDuckGo provider requires no configuration")

    async def _perform_search(
        self,
        query: str,
        max_results: int,
        search_type: SearchType,
        **kwargs: Any,
    ) -> list[SearchResult]:
        """
        Perform DuckDuckGo search using HTML interface.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            search_type: Type of search (web or news)
            **kwargs: Additional parameters (ignored for DuckDuckGo)

        Returns:
            List of SearchResult objects

        Raises:
            APIError: If the search fails or returns invalid data
            NetworkError: If there's a network connectivity issue
        """
        if not self.client:
            raise APIError("HTTP client not initialized", provider=self.provider)

        try:
            # Build search URL
            search_url = self._build_search_url(query, search_type)

            logger.debug(
                "Making DuckDuckGo search request",
                url=search_url,
                query=query,
                search_type=search_type.value,
            )

            # Make the search request
            response = await self.client.get(search_url)
            response.raise_for_status()

            # Parse the HTML response
            results = self._parse_search_results(response.text, max_results)

            logger.info(
                "DuckDuckGo search completed",
                query=query[:50] + "..." if len(query) > 50 else query,
                results_found=len(results),
                max_results=max_results,
            )

            return results

        except httpx.HTTPStatusError as e:
            logger.error(
                "DuckDuckGo HTTP error",
                status_code=e.response.status_code,
                response_text=e.response.text[:500],
            )
            raise APIError(
                f"DuckDuckGo search failed with status {e.response.status_code}",
                provider=self.provider,
            ) from e

        except httpx.RequestError as e:
            logger.error("DuckDuckGo network error", error=str(e))
            raise NetworkError(
                f"Network error during DuckDuckGo search: {str(e)}",
                provider=self.provider,
            ) from e

        except Exception as e:
            logger.error("DuckDuckGo parsing error", error=str(e))
            raise APIError(
                f"Failed to parse DuckDuckGo results: {str(e)}",
                provider=self.provider,
            ) from e

    def _build_search_url(self, query: str, search_type: SearchType) -> str:
        """
        Build the DuckDuckGo search URL.

        Args:
            query: Search query string
            search_type: Type of search (web or news)

        Returns:
            Complete search URL
        """
        # Encode the query for URL
        encoded_query = quote_plus(query)

        # Build base URL with query
        url = f"{self.BASE_URL}?q={encoded_query}"

        # Add search type parameters
        if search_type == SearchType.NEWS:
            # DuckDuckGo news search requires both parameters
            url += "&ia=news&iar=news"
        else:
            # Explicit web search intent
            url += "&ia=web"

        # Add essential parameters for better results
        url += "&kl=us-en"  # Language/region
        url += "&s=0"  # Start from first result
        url += "&kaf=-1"  # Full URLs (no redirect wrappers)
        url += "&kp=-1"  # Safe search: moderate
        url += "&dc=1"  # Disable auto-complete

        return url

    def _parse_search_results(
        self, html_content: str, max_results: int
    ) -> list[SearchResult]:
        """
        Parse DuckDuckGo HTML search results.

        Args:
            html_content: Raw HTML response from DuckDuckGo
            max_results: Maximum number of results to extract

        Returns:
            List of SearchResult objects

        Raises:
            APIError: If HTML parsing fails or no results found
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            results = []
            position = 1

            # Find all result containers
            # DuckDuckGo uses different CSS classes, we'll try multiple selectors
            result_selectors = [
                "div.result",
                "div.results_links",
                "div.web-result",
                ".result__body",
            ]

            result_elements = []
            for selector in result_selectors:
                elements = soup.select(selector)
                if elements:
                    result_elements = elements
                    logger.debug(f"Found results using selector: {selector}")
                    break

            if not result_elements:
                # Try a more specific generic approach
                result_elements = soup.find_all("div", class_=re.compile(r"result[_-]"))

            if not result_elements:
                logger.warning("No result elements found in DuckDuckGo response")
                return []

            for element in result_elements[:max_results]:
                try:
                    result = self._extract_result_from_element(element, position)
                    if result:
                        results.append(result)
                        position += 1
                except Exception as e:
                    logger.warning(
                        "Failed to extract result from element",
                        position=position,
                        error=str(e),
                    )
                    continue

            if not results:
                logger.warning("No valid results extracted from DuckDuckGo response")

            return results

        except Exception as e:
            logger.error("Failed to parse DuckDuckGo HTML", error=str(e))
            raise APIError(
                f"Failed to parse DuckDuckGo search results: {str(e)}",
                provider=self.provider,
            ) from e

    def _extract_result_from_element(
        self, element, position: int
    ) -> SearchResult | None:
        """
        Extract a single search result from an HTML element.

        Args:
            element: BeautifulSoup element containing result data
            position: Position of this result in the search results

        Returns:
            SearchResult object or None if extraction fails
        """
        try:
            # Try multiple approaches to find title and URL
            title_element = None
            url = None

            # Method 1: Look for result__a class (common in DuckDuckGo)
            title_link = element.find("a", class_=re.compile(r"result__a"))
            if title_link:
                title_element = title_link
                url = title_link.get("href")

            # Method 2: Look for any link with a title-like class
            if not title_element:
                title_link = element.find("a", class_=re.compile(r"title|heading"))
                if title_link:
                    title_element = title_link
                    url = title_link.get("href")

            # Method 3: Look for the first link in the result
            if not title_element:
                title_link = element.find("a", href=True)
                if title_link and title_link.get_text(strip=True):
                    title_element = title_link
                    url = title_link.get("href")

            if not title_element or not url:
                return None

            # Extract title
            title = self._clean_text(title_element.get_text())
            if not title:
                return None

            # Clean and validate URL
            url = self._clean_url(url)
            if not url:
                return None

            # Extract snippet/description
            snippet = self._extract_snippet(element)

            # Extract source domain
            source = self._extract_domain(url)

            # Extract date if available
            date = self._extract_date(element)

            return SearchResult(
                title=title,
                url=url,
                snippet=snippet,
                position=position,
                date=date,
                source=source,
                metadata={
                    "provider": "duckduckgo",
                    "extracted_at": "2024-01-15T00:00:00Z",  # Could use actual timestamp
                },
            )

        except Exception as e:
            logger.debug(
                "Failed to extract result from element",
                position=position,
                error=str(e),
            )
            return None

    def _extract_snippet(self, element) -> str:
        """Extract snippet/description from result element."""
        snippet = ""

        # Try multiple selectors for snippet
        snippet_selectors = [
            ".result__snippet",
            ".result-snippet",
            ".snippet",
            ".description",
            ".result__body",
        ]

        for selector in snippet_selectors:
            snippet_element = element.select_one(selector)
            if snippet_element:
                snippet = self._clean_text(snippet_element.get_text())
                break

        # If no snippet found with selectors, try to find any text content
        if not snippet:
            # Remove title and URL elements to avoid duplication
            temp_element = element.__copy__()
            for link in temp_element.find_all("a"):
                link.decompose()

            snippet = self._clean_text(temp_element.get_text())

        # Truncate snippet if too long
        if len(snippet) > 300:
            snippet = snippet[:297] + "..."

        return snippet or "No description available"

    def _extract_date(self, element) -> str | None:
        """Extract publication date from result element if available."""
        # DuckDuckGo doesn't typically provide dates in web search results
        # This could be enhanced for news results
        date_selectors = [
            ".result__timestamp",
            ".timestamp",
            ".date",
            ".published",
        ]

        for selector in date_selectors:
            date_element = element.select_one(selector)
            if date_element:
                date_text = self._clean_text(date_element.get_text())
                if date_text:
                    return date_text

        return None

    def _clean_url(self, url: str) -> str | None:
        """
        Clean and validate URL, removing tracking parameters and redirects.

        Args:
            url: Raw URL from search results

        Returns:
            Cleaned canonical URL or None if invalid
        """
        if not url:
            return None

        # With kaf=-1, DuckDuckGo should provide direct URLs, but handle legacy redirects
        if url.startswith("/l/?uddg="):
            # Extract the actual URL from DuckDuckGo's redirect wrapper
            try:
                import base64
                from urllib.parse import parse_qs, urlparse

                parsed = urlparse(url)
                if parsed.query:
                    query_params = parse_qs(parsed.query)
                    if "uddg" in query_params:
                        encoded_url = query_params["uddg"][0]
                        decoded_url = base64.b64decode(encoded_url).decode("utf-8")
                        url = decoded_url
            except Exception as e:
                logger.debug("Failed to decode DuckDuckGo redirect URL", error=str(e))
                return None

        # Handle DuckDuckGo redirect patterns FIRST (before protocol normalization)
        # Check for all possible DuckDuckGo redirect patterns
        is_ddg_redirect = (
            url.startswith("/l/?")
            or url.startswith("//duckduckgo.com/l/?")
            or url.startswith("//html.duckduckgo.com/l/?")
            or url.startswith("https://duckduckgo.com/l/?")
            or url.startswith("http://duckduckgo.com/l/?")
            or url.startswith("https://html.duckduckgo.com/l/?")
        )

        if is_ddg_redirect:
            try:
                from urllib.parse import parse_qs, unquote, urlparse

                # Normalize the URL for parsing
                if url.startswith("//"):
                    parse_url = "https:" + url
                elif url.startswith("/l/?"):
                    parse_url = "https://duckduckgo.com" + url
                else:
                    parse_url = url

                parsed = urlparse(parse_url)
                query_params = parse_qs(parsed.query)

                # Extract the actual URL from uddg parameter
                if "uddg" in query_params:
                    encoded_url = query_params["uddg"][0]
                    # The uddg parameter is URL-encoded, not base64-encoded
                    decoded_url = unquote(encoded_url)
                    logger.debug(
                        "Extracted URL from DuckDuckGo redirect",
                        original=url[:100],
                        extracted=decoded_url[:100],
                    )
                    url = decoded_url
                else:
                    # Try other possible redirect parameters
                    for param in ["kh", "u"]:
                        if param in query_params:
                            redirect_url = unquote(query_params[param][0])
                            url = redirect_url
                            break
                    else:
                        logger.warning(
                            "No redirect parameter found in DuckDuckGo URL",
                            url=url[:100],
                        )
                        return None
            except Exception as e:
                logger.debug(
                    "Failed to extract URL from DuckDuckGo redirect",
                    url=url[:100],
                    error=str(e),
                )
                return None

        # Ensure URL has protocol (after redirect extraction)
        if url.startswith("//"):
            url = "https:" + url
        elif not url.startswith(("http://", "https://")):
            if url.startswith("/"):
                # Relative URL - should not happen with kaf=-1, but handle gracefully
                logger.warning("Received relative URL from DuckDuckGo", url=url)
                return None
            else:
                url = "https://" + url

        # Remove common tracking parameters
        url = self._remove_tracking_params(url)

        # Basic URL validation
        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            if not parsed.netloc:
                return None
            return url
        except Exception:
            return None

    def _remove_tracking_params(self, url: str) -> str:
        """
        Remove common tracking parameters from URL.

        Args:
            url: URL to clean

        Returns:
            URL with tracking parameters removed
        """
        try:
            from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

            parsed = urlparse(url)
            if not parsed.query:
                return url

            # Common tracking parameters to remove
            tracking_params = {
                "utm_source",
                "utm_medium",
                "utm_campaign",
                "utm_term",
                "utm_content",
                "fbclid",
                "gclid",
                "msclkid",
                "twclid",
                "igshid",
                "ref",
                "referrer",
                "source",
                "campaign",
                "_ga",
                "_gl",
                "_hsenc",
                "_hsmi",
                "mc_cid",
                "mc_eid",
                "mkt_tok",
            }

            query_params = parse_qs(parsed.query, keep_blank_values=False)

            # Remove tracking parameters
            cleaned_params = {
                k: v
                for k, v in query_params.items()
                if k.lower() not in tracking_params
            }

            # Rebuild URL
            if cleaned_params:
                new_query = urlencode(cleaned_params, doseq=True)
                cleaned_parsed = parsed._replace(query=new_query)
            else:
                cleaned_parsed = parsed._replace(query="")

            return urlunparse(cleaned_parsed)

        except Exception as e:
            logger.debug("Failed to remove tracking parameters", url=url, error=str(e))
            return url

    def _get_default_headers(self) -> dict[str, str]:
        """Get DuckDuckGo-specific headers."""
        headers = super()._get_default_headers()
        headers.update(
            {
                "Referer": "https://duckduckgo.com/",
                "Origin": "https://duckduckgo.com",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
            }
        )
        return headers
