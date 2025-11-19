"""
Unit tests for SearXNG Search provider.

Tests the SearXNG Search provider implementation to ensure
it follows the established patterns and handles all scenarios correctly.
"""

import json
from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from web_search_mcp.config import ProviderConfig
from web_search_mcp.models import (
    APIError,
    AuthenticationError,
    NetworkError,
    SearchProvider,
    SearchType,
    ValidationError,
)
from web_search_mcp.providers.searxng import SearXNGProvider


@pytest.fixture
def searxng_config():
    """Create a test configuration for SearXNG Search."""
    return ProviderConfig(
        enabled=True,
        base_url="https://searx.example.com",
        timeout=30,
        max_retries=3,
    )


@pytest.fixture
def searxng_provider(searxng_config):
    """Create a SearXNG Search provider instance."""
    return SearXNGProvider(SearchProvider.SEARXNG, searxng_config)


@pytest.fixture
def mock_web_response_success():
    """Mock successful SearXNG Web Search API response."""
    return {
        "results": [
            {
                "title": "Python Programming Tutorial",
                "url": "https://www.python.org/tutorial/",
                "content": "Learn Python programming with this comprehensive tutorial covering basics to advanced topics.",
                "pretty_url": "python.org",
                "engine": "google",
                "score": 0.95,
                "category": "general",
            },
            {
                "title": "Advanced Python Concepts",
                "url": "https://realpython.com/advanced-python/",
                "content": "Master advanced Python programming concepts including decorators, generators, and metaclasses.",
                "pretty_url": "realpython.com",
                "engine": "bing",
                "score": 0.87,
                "category": "general",
            },
        ],
        "infoboxes": [
            {
                "infobox": "Python Programming Language",
                "content": "Python is a high-level programming language.",
                "urls": [
                    {"url": "https://www.python.org", "title": "Official Website"}
                ],
            }
        ],
    }


@pytest.fixture
def mock_news_response_success():
    """Mock successful SearXNG News Search API response."""
    return {
        "results": [
            {
                "title": "AI Technology Breakthrough",
                "url": "https://techcrunch.com/ai-breakthrough/",
                "content": "Scientists announce major breakthrough in artificial intelligence research.",
                "pretty_url": "techcrunch.com",
                "publishedDate": "2024-01-15T08:00:00Z",
                "engine": "google_news",
                "category": "news",
                "thumbnail": "https://example.com/thumbnail.jpg",
            }
        ]
    }


class TestSearXNGProvider:
    """Test cases for SearXNG Search provider."""

    def test_init_with_base_url(self):
        """Test initialization with base URL."""
        config = ProviderConfig(enabled=True, base_url="https://searx.example.com/")
        provider = SearXNGProvider(SearchProvider.SEARXNG, config)

        # Should strip trailing slash
        assert provider.base_url == "https://searx.example.com"

    def test_init_without_base_url(self):
        """Test initialization without base URL raises error."""
        config = ProviderConfig(enabled=True)

        with pytest.raises(ValueError) as exc_info:
            SearXNGProvider(SearchProvider.SEARXNG, config)

        assert "base URL is required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_config_success(self, searxng_provider):
        """Test successful configuration validation."""
        searxng_provider.client = AsyncMock()

        # Mock successful config endpoint response
        mock_response = Mock()
        mock_response.status_code = 200
        searxng_provider.client.get.return_value = mock_response

        # Should not raise any exception
        await searxng_provider._validate_config()

    @pytest.mark.asyncio
    async def test_validate_config_missing_base_url(self):
        """Test configuration validation with missing base URL."""
        config = ProviderConfig(enabled=True)

        with pytest.raises(ValueError):
            SearXNGProvider(SearchProvider.SEARXNG, config)

    @pytest.mark.asyncio
    async def test_validate_config_unreachable_instance(self, searxng_provider):
        """Test configuration validation with unreachable SearXNG instance."""
        searxng_provider.client = AsyncMock()

        # Mock failed config endpoint response
        mock_response = Mock()
        mock_response.status_code = 404
        searxng_provider.client.get.return_value = mock_response

        with pytest.raises(AuthenticationError) as exc_info:
            await searxng_provider._validate_config()

        assert "not accessible" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_config_network_error(self, searxng_provider):
        """Test configuration validation with network error."""
        searxng_provider.client = AsyncMock()
        searxng_provider.client.get.side_effect = httpx.RequestError(
            "Connection failed"
        )

        with pytest.raises(AuthenticationError) as exc_info:
            await searxng_provider._validate_config()

        assert "Cannot connect" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_build_request_params_web_search(self, searxng_provider):
        """Test building request parameters for web search."""
        params = searxng_provider._build_request_params(
            query="python tutorial",
            max_results=5,
            search_type=SearchType.SEARCH,
        )

        assert params["q"] == "python tutorial"
        assert params["format"] == "json"
        assert params["pageno"] == 1
        assert params["categories"] == "general"
        assert params["language"] == "en"
        assert params["safesearch"] == "1"

    @pytest.mark.asyncio
    async def test_build_request_params_news_search(self, searxng_provider):
        """Test building request parameters for news search."""
        params = searxng_provider._build_request_params(
            query="tech news",
            max_results=3,
            search_type=SearchType.NEWS,
        )

        assert params["categories"] == "news"

    @pytest.mark.asyncio
    async def test_build_request_params_with_kwargs(self, searxng_provider):
        """Test building request parameters with additional kwargs."""
        params = searxng_provider._build_request_params(
            query="test query",
            max_results=10,
            search_type=SearchType.SEARCH,
            language="fr",
            safe_search="strict",
            time_range="week",
            engines=["google", "bing"],
        )

        assert params["language"] == "fr"
        assert params["safesearch"] == "2"
        assert params["time_range"] == "week"
        assert params["engines"] == "google,bing"

    @pytest.mark.asyncio
    async def test_build_request_params_image_search(self, searxng_provider):
        """Test building request parameters for image search."""
        params = searxng_provider._build_request_params(
            query="python logo",
            max_results=5,
            search_type=SearchType.SEARCH,
            image_search=True,
        )

        assert params["categories"] == "images"

    @pytest.mark.asyncio
    async def test_parse_search_results_success(
        self, searxng_provider, mock_web_response_success
    ):
        """Test successful parsing of web search results."""
        results = searxng_provider._parse_search_results(
            mock_web_response_success, 10, SearchType.SEARCH
        )

        assert len(results) == 3  # 2 regular + 1 infobox

        # Check infobox result (should be first)
        infobox_result = results[0]
        assert infobox_result.title == "📋 Python Programming Language"
        assert infobox_result.url == "https://www.python.org"
        assert infobox_result.metadata["result_type"] == "infobox"

        # Check regular results
        regular_result = results[1]
        assert regular_result.title == "Python Programming Tutorial"
        assert regular_result.url == "https://www.python.org/tutorial/"
        assert regular_result.source == "python.org"
        assert regular_result.metadata["provider"] == "searxng"
        assert regular_result.metadata["engine"] == "google"
        assert regular_result.metadata["score"] == 0.95

    @pytest.mark.asyncio
    async def test_parse_news_search_results_success(
        self, searxng_provider, mock_news_response_success
    ):
        """Test successful parsing of news search results."""
        results = searxng_provider._parse_search_results(
            mock_news_response_success, 10, SearchType.NEWS
        )

        assert len(results) == 1

        # Check news result
        result = results[0]
        assert result.title == "AI Technology Breakthrough"
        assert result.url == "https://techcrunch.com/ai-breakthrough/"
        assert result.date == "2024-01-15T08:00:00Z"
        assert result.thumbnail == "https://example.com/thumbnail.jpg"
        assert result.metadata["provider"] == "searxng"
        assert result.metadata["search_type"] == "news"
        assert result.metadata["engine"] == "google_news"
        assert result.metadata["category"] == "news"

    @pytest.mark.asyncio
    async def test_parse_search_results_empty(self, searxng_provider):
        """Test parsing empty search results."""
        empty_response = {"results": [], "infoboxes": []}
        results = searxng_provider._parse_search_results(
            empty_response, 10, SearchType.SEARCH
        )
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_extract_infobox_result(self, searxng_provider):
        """Test extracting infobox result."""
        infobox_data = {
            "infobox": "Python Programming",
            "content": "A high-level programming language",
            "urls": [{"url": "https://www.python.org", "title": "Official Site"}],
        }

        result = searxng_provider._extract_infobox_result(infobox_data, 1)

        assert result is not None
        assert result.title == "📋 Python Programming"
        assert result.url == "https://www.python.org"
        assert result.snippet == "A high-level programming language"
        assert result.metadata["result_type"] == "infobox"

    @pytest.mark.asyncio
    async def test_extract_infobox_result_with_string_urls(self, searxng_provider):
        """Test extracting infobox result with string URLs."""
        infobox_data = {
            "infobox": "Test Topic",
            "content": "Test content",
            "urls": ["https://example.com"],
        }

        result = searxng_provider._extract_infobox_result(infobox_data, 1)

        assert result is not None
        assert result.url == "https://example.com"

    @pytest.mark.asyncio
    async def test_extract_infobox_result_with_list_content(self, searxng_provider):
        """Test extracting infobox result with list content."""
        infobox_data = {
            "infobox": "Test Topic",
            "content": ["First item", "Second item", "Third item"],
            "urls": [{"url": "https://example.com"}],
        }

        result = searxng_provider._extract_infobox_result(infobox_data, 1)

        assert result is not None
        assert result.snippet == "First item Second item Third item"

    @pytest.mark.asyncio
    async def test_extract_error_message_json_format(self, searxng_provider):
        """Test extracting error message from JSON format."""
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Invalid query"}
        mock_response.text = "Fallback text"

        error_message = searxng_provider._extract_error_message(mock_response)
        assert error_message == "Invalid query"

    @pytest.mark.asyncio
    async def test_extract_error_message_message_format(self, searxng_provider):
        """Test extracting error message from message format."""
        mock_response = Mock()
        mock_response.json.return_value = {"message": "Server error"}
        mock_response.text = "Fallback text"

        error_message = searxng_provider._extract_error_message(mock_response)
        assert error_message == "Server error"

    @pytest.mark.asyncio
    async def test_extract_error_message_fallback(self, searxng_provider):
        """Test extracting error message with fallback to response text."""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "Error response text"

        error_message = searxng_provider._extract_error_message(mock_response)
        assert error_message == "Error response text"

    @pytest.mark.asyncio
    async def test_perform_search_http_errors(self, searxng_provider):
        """Test handling of various HTTP error codes."""
        searxng_provider.client = AsyncMock()

        # Test 400 Bad Request
        mock_response_400 = Mock()
        mock_response_400.status_code = 400
        mock_response_400.json.return_value = {"error": "Bad request"}
        searxng_provider.client.get.return_value = mock_response_400

        with pytest.raises(ValidationError):
            await searxng_provider._perform_search("test", 5, SearchType.SEARCH)

        # Test 404 Not Found
        mock_response_404 = Mock()
        mock_response_404.status_code = 404
        mock_response_404.json.return_value = {"error": "Not found"}
        searxng_provider.client.get.return_value = mock_response_404

        with pytest.raises(APIError) as exc_info:
            await searxng_provider._perform_search("test", 5, SearchType.SEARCH)
        assert "endpoint not found" in str(exc_info.value)

        # Test 429 Rate Limited
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        mock_response_429.json.return_value = {"error": "Rate limited"}
        searxng_provider.client.get.return_value = mock_response_429

        with pytest.raises(APIError) as exc_info:
            await searxng_provider._perform_search("test", 5, SearchType.SEARCH)
        assert "rate limit exceeded" in str(exc_info.value)

        # Test 500 Server Error
        mock_response_500 = Mock()
        mock_response_500.status_code = 500
        mock_response_500.json.return_value = {"error": "Server error"}
        searxng_provider.client.get.return_value = mock_response_500

        with pytest.raises(APIError):
            await searxng_provider._perform_search("test", 5, SearchType.SEARCH)

    @pytest.mark.asyncio
    async def test_perform_search_network_error(self, searxng_provider):
        """Test handling of network errors."""
        searxng_provider.client = AsyncMock()
        searxng_provider.client.get.side_effect = httpx.RequestError("Network error")

        with pytest.raises(NetworkError):
            await searxng_provider._perform_search("test", 5, SearchType.SEARCH)

    @pytest.mark.asyncio
    async def test_perform_search_json_decode_error(self, searxng_provider):
        """Test handling of JSON decode errors."""
        searxng_provider.client = AsyncMock()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        searxng_provider.client.get.return_value = mock_response

        with pytest.raises(APIError) as exc_info:
            await searxng_provider._perform_search("test", 5, SearchType.SEARCH)
        assert "JSON response" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_extract_date_from_item(self, searxng_provider):
        """Test extracting date from SearXNG item."""
        item_with_date = {
            "publishedDate": "2024-01-15T08:00:00Z",
            "title": "Test Article",
        }

        date = searxng_provider._extract_date_from_item(item_with_date)
        assert date == "2024-01-15T08:00:00Z"

        # Test item with non-string date
        item_with_timestamp = {
            "publishedDate": 1705305600,  # Timestamp
            "title": "Test Article",
        }

        date = searxng_provider._extract_date_from_item(item_with_timestamp)
        assert date == "1705305600"

        # Test item without date
        item_without_date = {"title": "Test Page"}
        date = searxng_provider._extract_date_from_item(item_without_date)
        assert date is None

    @pytest.mark.asyncio
    async def test_extract_thumbnail(self, searxng_provider):
        """Test extracting thumbnail from SearXNG item."""
        item_with_thumbnail = {
            "thumbnail": "https://example.com/thumbnail.jpg",
        }

        thumbnail = searxng_provider._extract_thumbnail(item_with_thumbnail)
        assert thumbnail == "https://example.com/thumbnail.jpg"

        # Test alternative img_src format
        item_with_img_src = {
            "img_src": "https://example.com/image.jpg",
        }

        thumbnail = searxng_provider._extract_thumbnail(item_with_img_src)
        assert thumbnail == "https://example.com/image.jpg"

        # Test item without thumbnail
        item_without_thumbnail = {"title": "Test Item"}
        thumbnail = searxng_provider._extract_thumbnail(item_without_thumbnail)
        assert thumbnail is None

    def test_clean_url(self, searxng_provider):
        """Test URL cleaning functionality."""
        # Test normal URL
        clean_url = searxng_provider._clean_url("https://example.com")
        assert clean_url == "https://example.com"

        # Test URL without protocol
        clean_url = searxng_provider._clean_url("example.com")
        assert clean_url == "https://example.com"

        # Test URL with // prefix
        clean_url = searxng_provider._clean_url("//example.com")
        assert clean_url == "https://example.com"

        # Test invalid URL
        clean_url = searxng_provider._clean_url("")
        assert clean_url is None

    def test_get_api_headers(self, searxng_provider):
        """Test getting API headers."""
        headers = searxng_provider._get_api_headers()

        assert "Accept" in headers
        assert "User-Agent" in headers
        assert headers["Accept"] == "application/json"
        assert "WebSearchMCP" in headers["User-Agent"]

    @pytest.mark.asyncio
    async def test_extract_result_from_data_missing_fields(self, searxng_provider):
        """Test extracting result with missing required fields."""
        # Missing URL
        item_missing_url = {
            "title": "Test Title",
            "content": "Test content",
        }

        result = searxng_provider._extract_result_from_data(
            item_missing_url, 1, SearchType.SEARCH
        )
        assert result is None

        # Missing title
        item_missing_title = {
            "url": "https://example.com",
            "content": "Test content",
        }

        result = searxng_provider._extract_result_from_data(
            item_missing_title, 1, SearchType.SEARCH
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_search_method_enhancement(
        self, searxng_provider, mock_web_response_success
    ):
        """Test the enhanced search method with result reordering."""
        searxng_provider._validate_config = AsyncMock()
        await searxng_provider.initialize()
        searxng_provider.client = AsyncMock()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = mock_web_response_success
        searxng_provider.client.get.return_value = mock_response

        result = await searxng_provider.search(
            query="python tutorial", max_results=5, search_type=SearchType.SEARCH
        )

        assert result.success
        assert len(result.results) == 3

        # Check that results are properly ordered: Infobox first, then Organic
        assert result.results[0].metadata.get("result_type") == "infobox"
        assert result.results[1].metadata.get("result_type") != "infobox"
        assert result.results[2].metadata.get("result_type") != "infobox"

        # Check positions are updated correctly
        for i, search_result in enumerate(result.results, 1):
            assert search_result.position == i
