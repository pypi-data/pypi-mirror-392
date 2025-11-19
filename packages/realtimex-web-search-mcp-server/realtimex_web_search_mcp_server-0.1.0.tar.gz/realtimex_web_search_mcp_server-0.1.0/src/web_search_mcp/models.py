"""
Data models for Web Search MCP Server.

Defines the core data structures for search requests, responses, and errors
with comprehensive type safety and validation.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class SearchProvider(str, Enum):
    """Supported web search providers."""

    GOOGLE = "google"
    BING = "bing"
    DUCKDUCKGO = "duckduckgo"
    SERPAPI = "serpapi"
    SERPER = "serper"
    SERPLY = "serply"
    SEARXNG = "searxng"
    TAVILY = "tavily"


class SearchType(str, Enum):
    """Supported search types."""

    SEARCH = "search"
    NEWS = "news"


class SearchResult(BaseModel):
    """Individual search result."""

    title: str = Field(description="Page title")
    url: str = Field(description="Page URL")
    snippet: str = Field(description="Page description or excerpt")
    position: int = Field(description="Result position in search results")
    date: str | None = Field(None, description="Publication date if available")
    source: str | None = Field(None, description="Source name or domain")
    thumbnail: str | None = Field(None, description="Thumbnail image URL")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional result metadata"
    )


class SearchMetadata(BaseModel):
    """Search metadata and context information."""

    language: str = Field(default="en", description="Search language")
    region: str = Field(default="us", description="Search region")
    search_type: str = Field(default="search", description="Type of search performed")
    safe_search: str = Field(default="moderate", description="Safe search level")
    total_available: int | None = Field(None, description="Total results available")


class SearchResponse(BaseModel):
    """Complete search response structure."""

    success: bool = Field(description="Whether the search was successful")
    provider: SearchProvider = Field(description="Search provider used")
    query: str = Field(description="Original search query")
    results: list[SearchResult] = Field(description="List of search results")
    results_returned: int = Field(description="Number of results returned")
    search_time: float = Field(description="Search execution time in seconds")
    metadata: SearchMetadata = Field(description="Search metadata")
    related_searches: list[str] = Field(
        default_factory=list, description="Related search suggestions"
    )
    error: str | None = Field(None, description="Error message if search failed")
    error_type: str | None = Field(None, description="Error type classification")

    @field_validator("results_returned")
    @classmethod
    def validate_results_count(cls, v: int, info) -> int:
        """Ensure results_returned matches actual results length."""
        if hasattr(info, "data") and "results" in info.data:
            actual_count = len(info.data["results"])
            if v != actual_count:
                return actual_count
        return v


class SearchError(Exception):
    """Base exception for search-related errors."""

    def __init__(
        self,
        message: str,
        provider: SearchProvider | None = None,
        error_type: str | None = None,
        retry_after: int | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.error_type = error_type or self.__class__.__name__
        self.retry_after = retry_after
        self.timestamp = datetime.now()


class ConfigurationError(SearchError):
    """Error in search provider configuration."""

    pass


class APIError(SearchError):
    """Error from search provider API."""

    pass


class QuotaExceededError(APIError):
    """Search provider quota exceeded."""

    pass


class AuthenticationError(APIError):
    """Authentication failure with search provider."""

    pass


class NetworkError(SearchError):
    """Network-related error during search."""

    pass


class ValidationError(SearchError):
    """Parameter validation error."""

    pass
