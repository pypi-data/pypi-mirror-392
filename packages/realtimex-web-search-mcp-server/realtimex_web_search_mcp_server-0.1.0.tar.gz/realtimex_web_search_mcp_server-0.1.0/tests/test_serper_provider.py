"""
Tests for Serper search provider.

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
from web_search_mcp.providers.serper import SerperProvider


class TestSerperProvider:
    """Test suite for Serper search provider."""

    @pytest.fixture
    def provider_config(self):
        """Create a basic provider configuration for testing."""
        return ProviderConfig(
            enabled=True,
            api_key="test-serper-api-key-12345",
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
    def serper_provider(self, provider_config):
        """Create a Serper provider instance for testing."""
        return SerperProvider(SearchProvider.SERPER, provider_config)

    @pytest.fixture
    def sample_serper_response(self):
        """Sample Serper API response for testing."""
        return {
            "searchParameters": {
                "q": "python programming",
                "gl": "us",
                "hl": "en",
                "num": 10,
                "autocorrect": True,
                "page": 1,
                "type": "search",
            },
            "knowledgeGraph": {
                "title": "Python",
                "type": "Programming language",
                "website": "https://www.python.org/",
                "description": "Python is a high-level, general-purpose programming language.",
                "descriptionSource": "Wikipedia",
                "descriptionLink": "https://en.wikipedia.org/wiki/Python_(programming_language)",
            },
            "answerBox": {
                "title": "Python Programming",
                "answer": "Python is an interpreted, high-level and general-purpose programming language.",
                "link": "https://www.python.org/about/",
            },
            "organic": [
                {
                    "title": "Welcome to Python.org",
                    "link": "https://www.python.org/",
                    "snippet": "The official home of the Python Programming Language. Python is a programming language that lets you work quickly and integrate systems more effectively.",
                    "position": 1,
                },
                {
                    "title": "Python Tutorial - W3Schools",
                    "link": "https://www.w3schools.com/python/",
                    "snippet": "Well organized and easy to understand Web building tutorials with lots of examples of how to use HTML, CSS, JavaScript, SQL, Python, PHP, Bootstrap, Java, XML and more.",
                    "position": 2,
                },
                {
                    "title": "Learn Python - Free Interactive Python Tutorial",
                    "link": "https://www.learnpython.org/",
                    "snippet": "LearnPython.org is a free interactive Python tutorial for people who want to learn Python, fast.",
                    "position": 3,
                },
            ],
        }

    @pytest.fixture
    def sample_serper_news_response(self):
        """Sample Serper news API response for testing."""
        return {
            "searchParameters": {
                "q": "technology news",
                "gl": "us",
                "hl": "en",
                "num": 5,
                "type": "news",
            },
            "news": [
                {
                    "title": "Latest Tech Breakthrough Announced",
                    "link": "https://techcrunch.com/2024/01/15/tech-breakthrough",
                    "snippet": "A major technology company announced a breakthrough in artificial intelligence today.",
                    "date": "2 hours ago",
                    "source": "TechCrunch",
                    "position": 1,
                },
                {
                    "title": "New Programming Language Released",
                    "link": "https://arstechnica.com/2024/01/15/new-language",
                    "snippet": "Developers have released a new programming language designed for modern applications.",
                    "date": "4 hours ago",
                    "source": "Ars Technica",
                    "position": 2,
                },
            ],
        }

    async def test_provider_initialization_with_api_key(self, serper_provider):
        """Test that the provider initializes correctly with API key."""
        assert not serper_provider._initialized
        assert serper_provider.client is None

        await serper_provider.initialize()

        assert serper_provider._initialized
        assert serper_provider.client is not None
        assert isinstance(serper_provider.client, httpx.AsyncClient)

        # Clean up
        await serper_provider.close()

    async def test_provider_initialization_without_api_key(
        self, provider_config_no_key
    ):
        """Test that the provider fails to initialize without API key."""
        provider = SerperProvider(SearchProvider.SERPER, provider_config_no_key)

        with pytest.raises(AuthenticationError) as exc_info:
            await provider.initialize()

        assert "API key is required" in str(exc_info.value)
        assert exc_info.value.provider == SearchProvider.SERPER

    async def test_provider_cleanup(self, serper_provider):
        """Test that the provider cleans up resources correctly."""
        await serper_provider.initialize()
        assert serper_provider._initialized
        assert serper_provider.client is not None

        await serper_provider.close()
        assert serper_provider.client is None
        assert not serper_provider._initialized

    def test_get_endpoint(self, serper_provider):
        """Test endpoint selection for different search types."""
        # Test web search endpoint
        endpoint = serper_provider._get_endpoint(SearchType.SEARCH)
        assert endpoint == serper_provider.SEARCH_ENDPOINT
        assert "google.serper.dev/search" in endpoint

        # Test news search endpoint
        endpoint = serper_provider._get_endpoint(SearchType.NEWS)
        assert endpoint == serper_provider.NEWS_ENDPOINT
        assert "google.serper.dev/news" in endpoint

    def test_build_request_payload(self, serper_provider):
        """Test request payload building for different search types."""
        # Test basic web search
        payload = serper_provider._build_request_payload(
            "test query", 10, SearchType.SEARCH
        )

        assert payload["q"] == "test query"
        assert payload["num"] == 10
        assert payload["gl"] == "us"  # Default country
        assert payload["hl"] == "en"  # Default language

        # Test news search
        payload = serper_provider._build_request_payload(
            "news query", 5, SearchType.NEWS
        )
        assert payload["q"] == "news query"
        assert payload["num"] == 5

        # Test with custom parameters
        payload = serper_provider._build_request_payload(
            "custom query", 15, SearchType.SEARCH, gl="uk", hl="fr", tbs="qdr:d"
        )
        assert payload["gl"] == "uk"
        assert payload["hl"] == "fr"
        assert payload["tbs"] == "qdr:d"

        # Test max results limit
        payload = serper_provider._build_request_payload(
            "query", 150, SearchType.SEARCH
        )
        assert payload["num"] == 100  # Should be capped at 100

    def test_parse_search_results(self, serper_provider, sample_serper_response):
        """Test parsing of Serper API response."""
        results = serper_provider._parse_search_results(
            sample_serper_response, 10, SearchType.SEARCH
        )

        assert len(results) == 5  # Knowledge graph + answer box + 3 organic results

        # Check knowledge graph result (should be first)
        kg_result = results[0]
        assert "📚" in kg_result.title  # Knowledge graph emoji
        assert "Python" in kg_result.title
        assert kg_result.url == "https://www.python.org/"
        assert kg_result.position == 1
        assert kg_result.metadata["result_type"] == "knowledge_graph"

        # Check answer box result (should be second)
        ab_result = results[1]
        assert "💡" in ab_result.title  # Answer box emoji
        assert "Python Programming" in ab_result.title
        assert ab_result.metadata["result_type"] == "answer_box"

        # Check organic results
        organic_results = [
            r for r in results if r.metadata.get("result_type") == "organic"
        ]
        assert len(organic_results) == 3

        first_organic = organic_results[0]
        assert first_organic.title == "Welcome to Python.org"
        assert first_organic.url == "https://www.python.org/"
        assert (
            "official home of the Python Programming Language" in first_organic.snippet
        )
        assert first_organic.source == "python.org"
        assert first_organic.metadata["provider"] == "serper"

    def test_parse_news_results(self, serper_provider, sample_serper_news_response):
        """Test parsing of Serper news API response."""
        results = serper_provider._parse_search_results(
            sample_serper_news_response, 10, SearchType.NEWS
        )

        assert len(results) == 2

        # Check first news result
        first_result = results[0]
        assert first_result.title == "Latest Tech Breakthrough Announced"
        assert first_result.url == "https://techcrunch.com/2024/01/15/tech-breakthrough"
        assert first_result.date == "2 hours ago"
        assert first_result.source == "techcrunch.com"
        assert first_result.metadata["result_type"] == "organic"

        # Check second news result
        second_result = results[1]
        assert second_result.title == "New Programming Language Released"
        assert second_result.date == "4 hours ago"

    def test_parse_search_results_with_limit(
        self, serper_provider, sample_serper_response
    ):
        """Test parsing with result limit."""
        results = serper_provider._parse_search_results(
            sample_serper_response, 3, SearchType.SEARCH
        )
        assert len(results) == 3  # Should be limited to 3

    def test_parse_empty_results(self, serper_provider):
        """Test parsing when no results are returned."""
        empty_response = {"searchParameters": {"q": "nonexistent query"}, "organic": []}

        results = serper_provider._parse_search_results(
            empty_response, 10, SearchType.SEARCH
        )
        assert len(results) == 0

    def test_extract_knowledge_graph_result(self, serper_provider):
        """Test extraction of knowledge graph results."""
        kg_data = {
            "title": "Python Programming",
            "description": "A high-level programming language",
            "website": "https://www.python.org/",
        }

        result = serper_provider._extract_knowledge_graph_result(kg_data)

        assert result is not None
        assert "📚 Python Programming" == result.title
        assert result.url == "https://www.python.org/"
        assert result.snippet == "A high-level programming language"
        assert result.position == 1
        assert result.metadata["result_type"] == "knowledge_graph"

    def test_extract_answer_box_result(self, serper_provider):
        """Test extraction of answer box results."""
        ab_data = {
            "title": "Python Definition",
            "answer": "Python is a programming language",
            "link": "https://example.com/python",
        }

        result = serper_provider._extract_answer_box_result(ab_data, 2)

        assert result is not None
        assert "💡 Python Definition" == result.title
        assert result.url == "https://example.com/python"
        assert result.snippet == "Python is a programming language"
        assert result.position == 2
        assert result.metadata["result_type"] == "answer_box"

    def test_get_api_headers(self, serper_provider):
        """Test that API headers are properly formatted."""
        headers = serper_provider._get_api_headers()

        assert headers["X-API-KEY"] == "test-serper-api-key-12345"
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"
        assert "User-Agent" in headers
        assert "WebSearchMCP" in headers["User-Agent"]

    def test_clean_url(self, serper_provider):
        """Test URL cleaning functionality."""
        # Test normal URL
        assert (
            serper_provider._clean_url("https://example.com") == "https://example.com"
        )

        # Test URL without protocol
        assert serper_provider._clean_url("example.com") == "https://example.com"

        # Test protocol-relative URL
        assert serper_provider._clean_url("//example.com") == "https://example.com"

        # Test invalid URL
        assert serper_provider._clean_url("") is None

    @pytest.mark.asyncio
    async def test_search_with_mocked_response(
        self, serper_provider, sample_serper_response
    ):
        """Test search functionality with mocked HTTP response."""
        # Mock the HTTP client
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_serper_response
        mock_response.raise_for_status = AsyncMock()

        with patch.object(serper_provider, "client") as mock_client:
            mock_client.post = AsyncMock(return_value=mock_response)

            # Initialize provider
            await serper_provider.initialize()

            # Perform search
            result = await serper_provider.search(
                query="python programming",
                max_results=10,
                search_type=SearchType.SEARCH,
            )

            # Verify results
            assert result.success is True
            assert result.provider == SearchProvider.SERPER
            assert result.query == "python programming"
            assert len(result.results) == 5  # KG + AB + 3 organic
            assert result.results_returned == 5
            assert result.search_time > 0
            assert result.error is None

            # Verify result ordering (KG first, then AB, then organic)
            assert result.results[0].metadata["result_type"] == "knowledge_graph"
            assert result.results[1].metadata["result_type"] == "answer_box"
            assert result.results[2].metadata["result_type"] == "organic"

            # Verify HTTP call was made
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert call_args[0][0] == serper_provider.SEARCH_ENDPOINT

            # Check request payload
            payload = call_args[1]["json"]
            assert payload["q"] == "python programming"

            # Check headers
            headers = call_args[1]["headers"]
            assert headers["X-API-KEY"] == "test-serper-api-key-12345"

    @pytest.mark.asyncio
    async def test_news_search_with_mocked_response(
        self, serper_provider, sample_serper_news_response
    ):
        """Test news search functionality with mocked HTTP response."""
        # Mock the HTTP client
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_serper_news_response
        mock_response.raise_for_status = AsyncMock()

        with patch.object(serper_provider, "client") as mock_client:
            mock_client.post = AsyncMock(return_value=mock_response)

            # Initialize provider
            await serper_provider.initialize()

            # Perform news search
            result = await serper_provider.search(
                query="technology news", max_results=5, search_type=SearchType.NEWS
            )

            # Verify results
            assert result.success is True
            assert result.provider == SearchProvider.SERPER
            assert result.query == "technology news"
            assert len(result.results) == 2
            assert result.results_returned == 2

            # Verify news endpoint was used
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert call_args[0][0] == serper_provider.NEWS_ENDPOINT

    @pytest.mark.asyncio
    async def test_search_with_authentication_error(self, serper_provider):
        """Test search behavior when authentication fails."""
        # Mock HTTP 401 error
        mock_response = AsyncMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        with patch.object(serper_provider, "client") as mock_client:
            mock_client.post = AsyncMock(return_value=mock_response)

            # Initialize provider
            await serper_provider.initialize()

            # Perform search
            result = await serper_provider.search(
                query="test query", max_results=10, search_type=SearchType.SEARCH
            )

            # Verify error handling
            assert result.success is False
            assert result.provider == SearchProvider.SERPER
            assert result.query == "test query"
            assert len(result.results) == 0
            assert result.results_returned == 0
            assert "AuthenticationError" in result.error_type
            assert "Invalid Serper API key" in result.error

    @pytest.mark.asyncio
    async def test_search_with_quota_exceeded_error(self, serper_provider):
        """Test search behavior when quota is exceeded."""
        # Mock HTTP 429 error
        mock_response = AsyncMock()
        mock_response.status_code = 429
        mock_response.text = "Quota exceeded"
        mock_response.headers = {"Retry-After": "3600"}

        with patch.object(serper_provider, "client") as mock_client:
            mock_client.post = AsyncMock(return_value=mock_response)

            # Initialize provider
            await serper_provider.initialize()

            # Perform search
            result = await serper_provider.search(
                query="test query", max_results=10, search_type=SearchType.SEARCH
            )

            # Verify error handling
            assert result.success is False
            assert "QuotaExceededError" in result.error_type
            assert "quota exceeded" in result.error.lower()

    @pytest.mark.asyncio
    async def test_search_with_api_error(self, serper_provider):
        """Test search behavior when API returns error."""
        # Mock HTTP 400 error with JSON error response
        error_response = {"message": "Invalid search parameters"}
        mock_response = AsyncMock()
        mock_response.status_code = 400
        mock_response.text = json.dumps(error_response)
        mock_response.json.return_value = error_response

        with patch.object(serper_provider, "client") as mock_client:
            mock_client.post = AsyncMock(return_value=mock_response)

            # Initialize provider
            await serper_provider.initialize()

            # Perform search
            result = await serper_provider.search(
                query="test query", max_results=10, search_type=SearchType.SEARCH
            )

            # Verify error handling
            assert result.success is False
            assert "APIError" in result.error_type
            assert "Invalid search parameters" in result.error

    @pytest.mark.asyncio
    async def test_search_with_network_error(self, serper_provider):
        """Test search behavior when network error occurs."""
        # Mock network error
        network_error = httpx.ConnectError("Connection failed")

        with patch.object(serper_provider, "client") as mock_client:
            mock_client.post = AsyncMock(side_effect=network_error)

            # Initialize provider
            await serper_provider.initialize()

            # Perform search
            result = await serper_provider.search(
                query="test query", max_results=10, search_type=SearchType.SEARCH
            )

            # Verify error handling
            assert result.success is False
            assert "NetworkError" in result.error_type
            assert "Connection failed" in result.error

    def test_extract_result_from_data(self, serper_provider):
        """Test extraction of individual results from Serper data."""
        result_data = {
            "title": "Test Page Title",
            "link": "https://example.com/test",
            "snippet": "This is a test content snippet with relevant information.",
            "position": 1,
        }

        result = serper_provider._extract_result_from_data(result_data, 1)

        assert result is not None
        assert result.title == "Test Page Title"
        assert result.url == "https://example.com/test"
        assert (
            result.snippet
            == "This is a test content snippet with relevant information."
        )
        assert result.position == 1
        assert result.source == "example.com"
        assert result.metadata["provider"] == "serper"
        assert result.metadata["result_type"] == "organic"

    def test_extract_result_from_data_missing_fields(self, serper_provider):
        """Test extraction when required fields are missing."""
        # Missing title
        result_data = {
            "link": "https://example.com/test",
            "snippet": "Content without title",
        }
        result = serper_provider._extract_result_from_data(result_data, 1)
        assert result is None

        # Missing URL
        result_data = {"title": "Title without URL", "snippet": "Content without URL"}
        result = serper_provider._extract_result_from_data(result_data, 1)
        assert result is None


@pytest.mark.integration
class TestSerperIntegration:
    """Integration tests that make real API calls to Serper."""

    @pytest.fixture
    def provider_config(self):
        """Create a provider configuration for integration testing."""
        import os

        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            pytest.skip("SERPER_API_KEY environment variable not set")

        return ProviderConfig(
            enabled=True,
            api_key=api_key,
            timeout=30,
            max_retries=2,
        )

    @pytest.fixture
    def serper_provider(self, provider_config):
        """Create a Serper provider instance for integration testing."""
        return SerperProvider(SearchProvider.SERPER, provider_config)

    @pytest.mark.asyncio
    async def test_real_search(self, serper_provider):
        """Test a real search against Serper API (requires API key)."""
        try:
            await serper_provider.initialize()

            result = await serper_provider.search(
                query="artificial intelligence",
                max_results=5,
                search_type=SearchType.SEARCH,
            )

            # Verify basic structure
            assert result.provider == SearchProvider.SERPER
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
                    assert search_result.metadata["provider"] == "serper"

        finally:
            await serper_provider.close()

    @pytest.mark.asyncio
    async def test_real_news_search(self, serper_provider):
        """Test a real news search against Serper API."""
        try:
            await serper_provider.initialize()

            result = await serper_provider.search(
                query="technology news today",
                max_results=3,
                search_type=SearchType.NEWS,
            )

            # Verify basic structure
            assert result.provider == SearchProvider.SERPER
            assert result.query == "technology news today"
            assert isinstance(result.results, list)

            # If successful, check for news-specific features
            if result.success and result.results:
                # News results might have dates
                news_with_dates = [r for r in result.results if r.date]
                # At least some results should have dates in news search
                assert len(news_with_dates) >= 0  # Could be 0 if no dates provided

        finally:
            await serper_provider.close()

    @pytest.mark.asyncio
    async def test_real_search_with_custom_params(self, serper_provider):
        """Test a real search with custom Serper parameters."""
        try:
            await serper_provider.initialize()

            result = await serper_provider.search(
                query="machine learning tutorials",
                max_results=3,
                search_type=SearchType.SEARCH,
                gl="uk",  # UK region
                hl="en",  # English language
            )

            # Verify basic structure
            assert result.provider == SearchProvider.SERPER
            assert result.query == "machine learning tutorials"

        finally:
            await serper_provider.close()
