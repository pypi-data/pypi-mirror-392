"""
Tests for Tavily search provider.

Comprehensive tests including unit tests with mocked responses and
integration tests with real API calls.
"""

import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from web_search_mcp.config import ProviderConfig
from web_search_mcp.models import (
    AuthenticationError,
    SearchProvider,
    SearchType,
)
from web_search_mcp.providers.tavily import TavilyProvider


class TestTavilyProvider:
    """Test suite for Tavily search provider."""

    @pytest.fixture
    def provider_config(self):
        """Create a basic provider configuration for testing."""
        return ProviderConfig(
            enabled=True,
            api_key="test-api-key-12345",
            timeout=30,
            max_retries=3,
        )

    @pytest.fixture
    def provider_config_no_key(self):
        """Create a provider configuration without API key."""
        return ProviderConfig(
            enabled=True,
            timeout=30,
            max_retries=3,
        )

    @pytest.fixture
    def tavily_provider(self, provider_config):
        """Create a Tavily provider instance for testing."""
        return TavilyProvider(SearchProvider.TAVILY, provider_config)

    @pytest.fixture
    def sample_tavily_response(self):
        """Sample Tavily API response for testing."""
        return {
            "query": "python programming",
            "follow_up_questions": None,
            "answer": None,
            "images": [],
            "results": [
                {
                    "url": "https://www.python.org/",
                    "title": "Welcome to Python.org",
                    "content": "The official home of the Python Programming Language. Python is a programming language that lets you work quickly and integrate systems more effectively.",
                    "score": 0.89234,
                    "raw_content": None,
                },
                {
                    "url": "https://docs.python.org/3/tutorial/",
                    "title": "The Python Tutorial — Python 3.12.1 documentation",
                    "content": "Python is an easy to learn, powerful programming language. It has efficient high-level data structures and a simple but effective approach to object-oriented programming.",
                    "score": 0.85671,
                    "raw_content": None,
                },
                {
                    "url": "https://realpython.com/",
                    "title": "Real Python - Python Tutorials",
                    "content": "Learn Python online: Python tutorials for developers of all skill levels, Python books and courses, Python news, code examples, articles, and more.",
                    "score": 0.82145,
                    "raw_content": None,
                },
            ],
            "response_time": 1.23,
        }

    async def test_provider_initialization_with_api_key(self, tavily_provider):
        """Test that the provider initializes correctly with API key."""
        assert not tavily_provider._initialized
        assert tavily_provider.client is None

        await tavily_provider.initialize()

        assert tavily_provider._initialized
        assert tavily_provider.client is not None
        assert isinstance(tavily_provider.client, httpx.AsyncClient)

        # Clean up
        await tavily_provider.close()

    async def test_provider_initialization_without_api_key(
        self, provider_config_no_key
    ):
        """Test that the provider fails to initialize without API key."""
        provider = TavilyProvider(SearchProvider.TAVILY, provider_config_no_key)

        with pytest.raises(AuthenticationError) as exc_info:
            await provider.initialize()

        assert "API key is required" in str(exc_info.value)
        assert exc_info.value.provider == SearchProvider.TAVILY

    async def test_provider_cleanup(self, tavily_provider):
        """Test that the provider cleans up resources correctly."""
        await tavily_provider.initialize()
        assert tavily_provider._initialized
        assert tavily_provider.client is not None

        await tavily_provider.close()
        assert tavily_provider.client is None
        assert not tavily_provider._initialized

    def test_build_request_payload(self, tavily_provider):
        """Test request payload building for different search types."""
        # Test basic web search
        payload = tavily_provider._build_request_payload(
            "test query", 10, SearchType.SEARCH
        )

        assert payload["api_key"] == "test-api-key-12345"
        assert payload["query"] == "test query"
        assert payload["max_results"] == 10
        assert payload["search_depth"] == "basic"
        assert payload["format"] == "json"
        assert payload["include_answer"] is False

        # Test news search (should use advanced depth)
        payload = tavily_provider._build_request_payload(
            "news query", 5, SearchType.NEWS
        )
        assert payload["query"] == "news query"
        assert payload["max_results"] == 5
        assert payload["search_depth"] == "advanced"

        # Test with custom parameters
        payload = tavily_provider._build_request_payload(
            "custom query",
            15,
            SearchType.SEARCH,
            search_depth="advanced",
            include_answer=True,
        )
        assert payload["search_depth"] == "advanced"
        assert payload["include_answer"] is True

    def test_parse_search_results(self, tavily_provider, sample_tavily_response):
        """Test parsing of Tavily API response."""
        results = tavily_provider._parse_search_results(sample_tavily_response, 10)

        assert len(results) == 3

        # Check first result
        first_result = results[0]
        assert first_result.title == "Welcome to Python.org"
        assert first_result.url == "https://www.python.org/"
        assert (
            "official home of the Python Programming Language" in first_result.snippet
        )
        assert first_result.position == 1
        assert first_result.source == "python.org"
        assert first_result.metadata["relevance_score"] == 0.89234
        assert first_result.metadata["provider"] == "tavily"

        # Check second result
        second_result = results[1]
        assert (
            second_result.title == "The Python Tutorial — Python 3.12.1 documentation"
        )
        assert second_result.url == "https://docs.python.org/3/tutorial/"
        assert second_result.position == 2
        assert second_result.metadata["relevance_score"] == 0.85671

        # Check third result
        third_result = results[2]
        assert third_result.title == "Real Python - Python Tutorials"
        assert third_result.url == "https://realpython.com/"
        assert third_result.position == 3

    def test_parse_search_results_with_limit(
        self, tavily_provider, sample_tavily_response
    ):
        """Test parsing with result limit."""
        results = tavily_provider._parse_search_results(sample_tavily_response, 2)
        assert len(results) == 2

    def test_parse_empty_results(self, tavily_provider):
        """Test parsing when no results are returned."""
        empty_response = {
            "query": "nonexistent query",
            "results": [],
            "response_time": 0.5,
        }

        results = tavily_provider._parse_search_results(empty_response, 10)
        assert len(results) == 0

    def test_clean_url(self, tavily_provider):
        """Test URL cleaning functionality."""
        # Test normal URL
        assert (
            tavily_provider._clean_url("https://example.com") == "https://example.com"
        )

        # Test URL without protocol
        assert tavily_provider._clean_url("example.com") == "https://example.com"

        # Test protocol-relative URL
        assert tavily_provider._clean_url("//example.com") == "https://example.com"

        # Test invalid URL
        assert tavily_provider._clean_url("") is None
        assert tavily_provider._clean_url("not-a-url") == "https://not-a-url"

    def test_get_api_headers(self, tavily_provider):
        """Test that API headers are properly formatted."""
        headers = tavily_provider._get_api_headers()

        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"
        assert "User-Agent" in headers
        assert "WebSearchMCP" in headers["User-Agent"]

    @pytest.mark.asyncio
    async def test_search_with_mocked_response(
        self, tavily_provider, sample_tavily_response
    ):
        """Test search functionality with mocked HTTP response."""
        # Mock the HTTP client
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_tavily_response
        mock_response.raise_for_status = AsyncMock()

        with patch.object(tavily_provider, "client") as mock_client:
            mock_client.post = AsyncMock(return_value=mock_response)

            # Initialize provider
            await tavily_provider.initialize()

            # Perform search
            result = await tavily_provider.search(
                query="python programming",
                max_results=10,
                search_type=SearchType.SEARCH,
            )

            # Verify results
            assert result.success is True
            assert result.provider == SearchProvider.TAVILY
            assert result.query == "python programming"
            assert len(result.results) == 3
            assert result.results_returned == 3
            assert result.search_time > 0
            assert result.error is None

            # Verify results are sorted by relevance score
            scores = [r.metadata.get("relevance_score", 0) for r in result.results]
            assert scores == sorted(scores, reverse=True)

            # Verify HTTP call was made
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert call_args[0][0] == tavily_provider.BASE_URL

            # Check request payload
            payload = call_args[1]["json"]
            assert payload["query"] == "python programming"
            assert payload["api_key"] == "test-api-key-12345"

    @pytest.mark.asyncio
    async def test_search_with_authentication_error(self, tavily_provider):
        """Test search behavior when authentication fails."""
        # Mock HTTP 401 error
        mock_response = AsyncMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        with patch.object(tavily_provider, "client") as mock_client:
            mock_client.post = AsyncMock(return_value=mock_response)

            # Initialize provider
            await tavily_provider.initialize()

            # Perform search
            result = await tavily_provider.search(
                query="test query", max_results=10, search_type=SearchType.SEARCH
            )

            # Verify error handling
            assert result.success is False
            assert result.provider == SearchProvider.TAVILY
            assert result.query == "test query"
            assert len(result.results) == 0
            assert result.results_returned == 0
            assert "AuthenticationError" in result.error_type
            assert "Invalid Tavily API key" in result.error

    @pytest.mark.asyncio
    async def test_search_with_quota_exceeded_error(self, tavily_provider):
        """Test search behavior when quota is exceeded."""
        # Mock HTTP 429 error
        mock_response = AsyncMock()
        mock_response.status_code = 429
        mock_response.text = "Quota exceeded"
        mock_response.headers = {"Retry-After": "3600"}

        with patch.object(tavily_provider, "client") as mock_client:
            mock_client.post = AsyncMock(return_value=mock_response)

            # Initialize provider
            await tavily_provider.initialize()

            # Perform search
            result = await tavily_provider.search(
                query="test query", max_results=10, search_type=SearchType.SEARCH
            )

            # Verify error handling
            assert result.success is False
            assert "QuotaExceededError" in result.error_type
            assert "quota exceeded" in result.error.lower()

    @pytest.mark.asyncio
    async def test_search_with_api_error(self, tavily_provider):
        """Test search behavior when API returns error."""
        # Mock HTTP 400 error with JSON error response
        error_response = {"error": "Invalid query parameter"}
        mock_response = AsyncMock()
        mock_response.status_code = 400
        mock_response.text = json.dumps(error_response)
        mock_response.json.return_value = error_response

        with patch.object(tavily_provider, "client") as mock_client:
            mock_client.post = AsyncMock(return_value=mock_response)

            # Initialize provider
            await tavily_provider.initialize()

            # Perform search
            result = await tavily_provider.search(
                query="test query", max_results=10, search_type=SearchType.SEARCH
            )

            # Verify error handling
            assert result.success is False
            assert "APIError" in result.error_type
            assert "Invalid query parameter" in result.error

    @pytest.mark.asyncio
    async def test_search_with_network_error(self, tavily_provider):
        """Test search behavior when network error occurs."""
        # Mock network error
        network_error = httpx.ConnectError("Connection failed")

        with patch.object(tavily_provider, "client") as mock_client:
            mock_client.post = AsyncMock(side_effect=network_error)

            # Initialize provider
            await tavily_provider.initialize()

            # Perform search
            result = await tavily_provider.search(
                query="test query", max_results=10, search_type=SearchType.SEARCH
            )

            # Verify error handling
            assert result.success is False
            assert "NetworkError" in result.error_type
            assert "Connection failed" in result.error

    @pytest.mark.asyncio
    async def test_search_with_json_decode_error(self, tavily_provider):
        """Test search behavior when JSON parsing fails."""
        # Mock response with invalid JSON
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.raise_for_status = AsyncMock()

        with patch.object(tavily_provider, "client") as mock_client:
            mock_client.post = AsyncMock(return_value=mock_response)

            # Initialize provider
            await tavily_provider.initialize()

            # Perform search
            result = await tavily_provider.search(
                query="test query", max_results=10, search_type=SearchType.SEARCH
            )

            # Verify error handling
            assert result.success is False
            assert "APIError" in result.error_type
            assert "Failed to parse Tavily JSON response" in result.error

    def test_extract_result_from_data(self, tavily_provider):
        """Test extraction of individual results from Tavily data."""
        result_data = {
            "url": "https://example.com/test",
            "title": "Test Page Title",
            "content": "This is a test content snippet with relevant information.",
            "score": 0.75,
        }

        result = tavily_provider._extract_result_from_data(result_data, 1)

        assert result is not None
        assert result.title == "Test Page Title"
        assert result.url == "https://example.com/test"
        assert (
            result.snippet
            == "This is a test content snippet with relevant information."
        )
        assert result.position == 1
        assert result.source == "example.com"
        assert result.metadata["relevance_score"] == 0.75
        assert result.metadata["provider"] == "tavily"

    def test_extract_result_from_data_missing_fields(self, tavily_provider):
        """Test extraction when required fields are missing."""
        # Missing title
        result_data = {
            "url": "https://example.com/test",
            "content": "Content without title",
            "score": 0.5,
        }
        result = tavily_provider._extract_result_from_data(result_data, 1)
        assert result is None

        # Missing URL
        result_data = {
            "title": "Title without URL",
            "content": "Content without URL",
            "score": 0.5,
        }
        result = tavily_provider._extract_result_from_data(result_data, 1)
        assert result is None

    def test_extract_result_with_long_snippet(self, tavily_provider):
        """Test snippet truncation for long content."""
        result_data = {
            "url": "https://example.com/test",
            "title": "Test Page",
            "content": "A" * 400,  # Very long content
            "score": 0.5,
        }

        result = tavily_provider._extract_result_from_data(result_data, 1)

        assert result is not None
        assert len(result.snippet) <= 300
        assert result.snippet.endswith("...")


@pytest.mark.integration
class TestTavilyIntegration:
    """Integration tests that make real API calls to Tavily."""

    @pytest.fixture
    def provider_config(self):
        """Create a provider configuration for integration testing."""
        import os

        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            pytest.skip("TAVILY_API_KEY environment variable not set")

        return ProviderConfig(
            enabled=True,
            api_key=api_key,
            timeout=30,
            max_retries=2,
        )

    @pytest.fixture
    def tavily_provider(self, provider_config):
        """Create a Tavily provider instance for integration testing."""
        return TavilyProvider(SearchProvider.TAVILY, provider_config)

    @pytest.mark.asyncio
    async def test_real_search(self, tavily_provider):
        """Test a real search against Tavily API (requires API key)."""
        try:
            await tavily_provider.initialize()

            result = await tavily_provider.search(
                query="artificial intelligence",
                max_results=5,
                search_type=SearchType.SEARCH,
            )

            # Verify basic structure
            assert result.provider == SearchProvider.TAVILY
            assert result.query == "artificial intelligence"
            assert isinstance(result.results, list)
            assert isinstance(result.search_time, float)
            assert result.search_time > 0

            # If successful, verify result structure
            if result.success:
                assert result.results_returned > 0
                for search_result in result.results:
                    assert search_result.title
                    assert search_result.url.startswith(("http://", "https://"))
                    assert search_result.snippet
                    assert search_result.position > 0
                    assert search_result.source
                    assert "relevance_score" in search_result.metadata

                # Verify results are sorted by relevance
                scores = [r.metadata.get("relevance_score", 0) for r in result.results]
                assert scores == sorted(scores, reverse=True)

        finally:
            await tavily_provider.close()

    @pytest.mark.asyncio
    async def test_real_news_search(self, tavily_provider):
        """Test a real news search against Tavily API."""
        try:
            await tavily_provider.initialize()

            result = await tavily_provider.search(
                query="technology news today",
                max_results=3,
                search_type=SearchType.NEWS,
            )

            # Verify basic structure
            assert result.provider == SearchProvider.TAVILY
            assert result.query == "technology news today"
            assert isinstance(result.results, list)

        finally:
            await tavily_provider.close()

    @pytest.mark.asyncio
    async def test_real_search_with_custom_params(self, tavily_provider):
        """Test a real search with custom Tavily parameters."""
        try:
            await tavily_provider.initialize()

            result = await tavily_provider.search(
                query="machine learning tutorials",
                max_results=3,
                search_type=SearchType.SEARCH,
                search_depth="advanced",
                include_answer=True,
            )

            # Verify basic structure
            assert result.provider == SearchProvider.TAVILY
            assert result.query == "machine learning tutorials"

        finally:
            await tavily_provider.close()
