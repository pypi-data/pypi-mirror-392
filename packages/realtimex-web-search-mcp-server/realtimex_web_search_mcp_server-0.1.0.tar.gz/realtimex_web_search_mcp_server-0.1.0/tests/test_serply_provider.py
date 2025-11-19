"""
Unit tests for Serply Search provider.

Tests the Serply Search provider implementation to ensure
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
    QuotaExceededError,
    SearchProvider,
    SearchType,
    ValidationError,
)
from web_search_mcp.providers.serply import SerplyProvider


@pytest.fixture
def serply_config():
    """Create a test configuration for Serply Search."""
    return ProviderConfig(
        enabled=True,
        api_key="test-api-key",
        timeout=30,
        max_retries=3,
    )


@pytest.fixture
def serply_provider(serply_config):
    """Create a Serply Search provider instance."""
    return SerplyProvider(SearchProvider.SERPLY, serply_config)


@pytest.fixture
def mock_web_response_success():
    """Mock successful Serply Web Search API response."""
    return {
        "organic": [
            {
                "title": "Python Programming Tutorial",
                "link": "https://www.python.org/tutorial/",
                "snippet": "Learn Python programming with this comprehensive tutorial covering basics to advanced topics.",
                "displayLink": "python.org",
                "position": 1,
            },
            {
                "title": "Advanced Python Concepts",
                "link": "https://realpython.com/advanced-python/",
                "snippet": "Master advanced Python programming concepts including decorators, generators, and metaclasses.",
                "displayLink": "realpython.com",
                "position": 2,
            },
        ],
        "knowledgeGraph": {
            "title": "Python Programming Language",
            "description": "Python is a high-level programming language.",
            "website": "https://www.python.org",
        },
        "answerBox": {
            "title": "What is Python?",
            "answer": "Python is an interpreted, high-level programming language.",
            "link": "https://en.wikipedia.org/wiki/Python_(programming_language)",
        },
    }


@pytest.fixture
def mock_news_response_success():
    """Mock successful Serply News Search API response."""
    return {
        "news": [
            {
                "title": "AI Technology Breakthrough",
                "link": "https://techcrunch.com/ai-breakthrough/",
                "snippet": "Scientists announce major breakthrough in artificial intelligence research.",
                "date": "2024-01-15",
                "thumbnail": "https://example.com/thumbnail.jpg",
            }
        ]
    }


class TestSerplyProvider:
    """Test cases for Serply Search provider."""

    @pytest.mark.asyncio
    async def test_validate_config_success(self, serply_provider):
        """Test successful configuration validation."""
        # Should not raise any exception
        await serply_provider._validate_config()

    @pytest.mark.asyncio
    async def test_validate_config_missing_api_key(self):
        """Test configuration validation with missing API key."""
        config = ProviderConfig(enabled=True)
        provider = SerplyProvider(SearchProvider.SERPLY, config)

        with pytest.raises(AuthenticationError) as exc_info:
            await provider._validate_config()

        assert "API key is required" in str(exc_info.value)

    def test_get_endpoint_web_search(self, serply_provider):
        """Test getting endpoint for web search."""
        endpoint = serply_provider._get_endpoint(SearchType.SEARCH)
        assert endpoint == "https://api.serply.io/v1/search"

    def test_get_endpoint_news_search(self, serply_provider):
        """Test getting endpoint for news search."""
        endpoint = serply_provider._get_endpoint(SearchType.NEWS)
        assert endpoint == "https://api.serply.io/v1/news"

    @pytest.mark.asyncio
    async def test_build_request_params_web_search(self, serply_provider):
        """Test building request parameters for web search."""
        params = serply_provider._build_request_params(
            query="python tutorial",
            max_results=5,
            search_type=SearchType.SEARCH,
        )

        assert params["q"] == "python tutorial"
        assert params["num"] == 5
        assert params["hl"] == "en"
        assert params["gl"] == "us"
        assert params["safe"] == "medium"
        assert "tbm" not in params  # No news search parameter

    @pytest.mark.asyncio
    async def test_build_request_params_news_search(self, serply_provider):
        """Test building request parameters for news search."""
        params = serply_provider._build_request_params(
            query="tech news",
            max_results=3,
            search_type=SearchType.NEWS,
        )

        assert params["tbm"] == "nws"  # News search parameter
        assert params["tbs"] == "qdr:d"  # Recent news
        assert "safe" not in params  # No web-specific safe search

    @pytest.mark.asyncio
    async def test_build_request_params_with_kwargs(self, serply_provider):
        """Test building request parameters with additional kwargs."""
        params = serply_provider._build_request_params(
            query="test query",
            max_results=10,
            search_type=SearchType.SEARCH,
            language="fr",
            country="ca",
            safe_search="strict",
            site="example.com",
            filetype="pdf",
        )

        assert params["hl"] == "fr"
        assert params["gl"] == "ca"
        assert params["safe"] == "high"
        assert "filetype:pdf" in params["q"]
        assert "filetype:pdf" in params["q"]

    @pytest.mark.asyncio
    async def test_build_request_params_news_with_time_range(self, serply_provider):
        """Test building request parameters for news with time range."""
        params = serply_provider._build_request_params(
            query="tech news",
            max_results=5,
            search_type=SearchType.NEWS,
            time_range="week",
        )

        assert params["tbs"] == "qdr:w"  # Past week

    @pytest.mark.asyncio
    async def test_parse_search_results_success(
        self, serply_provider, mock_web_response_success
    ):
        """Test successful parsing of web search results."""
        results = serply_provider._parse_search_results(
            mock_web_response_success, 10, SearchType.SEARCH
        )

        assert len(results) == 4  # 2 organic + 1 knowledge graph + 1 answer box

        # Check knowledge graph result (should be first)
        kg_result = results[0]
        assert kg_result.title == "📚 Python Programming Language"
        assert kg_result.url == "https://www.python.org"
        assert kg_result.metadata["result_type"] == "knowledge_graph"

        # Check answer box result (should be second)
        ab_result = results[1]
        assert ab_result.title == "💡 What is Python?"
        assert (
            ab_result.snippet
            == "Python is an interpreted, high-level programming language."
        )
        assert ab_result.metadata["result_type"] == "answer_box"

        # Check organic results
        organic_result = results[2]
        assert organic_result.title == "Python Programming Tutorial"
        assert organic_result.url == "https://www.python.org/tutorial/"
        assert organic_result.source == "python.org"
        assert organic_result.metadata["provider"] == "serply"

    @pytest.mark.asyncio
    async def test_parse_news_search_results_success(
        self, serply_provider, mock_news_response_success
    ):
        """Test successful parsing of news search results."""
        results = serply_provider._parse_search_results(
            mock_news_response_success, 10, SearchType.NEWS
        )

        assert len(results) == 1

        # Check news result
        result = results[0]
        assert result.title == "AI Technology Breakthrough"
        assert result.url == "https://techcrunch.com/ai-breakthrough/"
        assert result.date == "2024-01-15"
        assert result.thumbnail == "https://example.com/thumbnail.jpg"
        assert result.metadata["provider"] == "serply"
        assert result.metadata["search_type"] == "news"

    @pytest.mark.asyncio
    async def test_parse_search_results_empty(self, serply_provider):
        """Test parsing empty search results."""
        empty_response = {"organic": []}
        results = serply_provider._parse_search_results(
            empty_response, 10, SearchType.SEARCH
        )
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_extract_knowledge_graph_result(self, serply_provider):
        """Test extracting knowledge graph result."""
        kg_data = {
            "title": "Python Programming",
            "description": "A high-level programming language",
            "website": "https://www.python.org",
        }

        result = serply_provider._extract_knowledge_graph_result(kg_data)

        assert result is not None
        assert result.title == "📚 Python Programming"
        assert result.url == "https://www.python.org"
        assert result.snippet == "A high-level programming language"
        assert result.metadata["result_type"] == "knowledge_graph"

    @pytest.mark.asyncio
    async def test_extract_answer_box_result(self, serply_provider):
        """Test extracting answer box result."""
        ab_data = {
            "title": "What is AI?",
            "answer": "Artificial Intelligence is machine intelligence",
            "link": "https://en.wikipedia.org/wiki/AI",
        }

        result = serply_provider._extract_answer_box_result(ab_data, 2)

        assert result is not None
        assert result.title == "💡 What is AI?"
        assert result.snippet == "Artificial Intelligence is machine intelligence"
        assert result.url == "https://en.wikipedia.org/wiki/AI"
        assert result.position == 2
        assert result.metadata["result_type"] == "answer_box"

    @pytest.mark.asyncio
    async def test_extract_error_message_serply_format(self, serply_provider):
        """Test extracting error message from Serply API error format."""
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Invalid API key"}
        mock_response.text = "Fallback text"

        error_message = serply_provider._extract_error_message(mock_response)
        assert error_message == "Invalid API key"

    @pytest.mark.asyncio
    async def test_extract_error_message_alternative_format(self, serply_provider):
        """Test extracting error message from alternative Serply error format."""
        mock_response = Mock()
        mock_response.json.return_value = {"message": "Quota exceeded"}
        mock_response.text = "Fallback text"

        error_message = serply_provider._extract_error_message(mock_response)
        assert error_message == "Quota exceeded"

    @pytest.mark.asyncio
    async def test_extract_error_message_fallback(self, serply_provider):
        """Test extracting error message with fallback to response text."""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "Error response text"

        error_message = serply_provider._extract_error_message(mock_response)
        assert error_message == "Error response text"

    @pytest.mark.asyncio
    async def test_perform_search_http_errors(self, serply_provider):
        """Test handling of various HTTP error codes."""
        serply_provider.client = AsyncMock()

        # Test 400 Bad Request
        mock_response_400 = Mock()
        mock_response_400.status_code = 400
        mock_response_400.json.return_value = {"error": "Bad request"}
        serply_provider.client.get.return_value = mock_response_400

        with pytest.raises(ValidationError):
            await serply_provider._perform_search("test", 5, SearchType.SEARCH)

        # Test 401 Unauthorized
        mock_response_401 = Mock()
        mock_response_401.status_code = 401
        mock_response_401.json.return_value = {"error": "Unauthorized"}
        serply_provider.client.get.return_value = mock_response_401

        with pytest.raises(AuthenticationError):
            await serply_provider._perform_search("test", 5, SearchType.SEARCH)

        # Test 403 Forbidden
        mock_response_403 = Mock()
        mock_response_403.status_code = 403
        mock_response_403.json.return_value = {"error": "Forbidden"}
        serply_provider.client.get.return_value = mock_response_403

        with pytest.raises(AuthenticationError):
            await serply_provider._perform_search("test", 5, SearchType.SEARCH)

        # Test 429 Rate Limited
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        mock_response_429.headers = {"Retry-After": "3600"}
        mock_response_429.json.return_value = {"error": "Rate limited"}
        serply_provider.client.get.return_value = mock_response_429

        with pytest.raises(QuotaExceededError) as exc_info:
            await serply_provider._perform_search("test", 5, SearchType.SEARCH)
        assert exc_info.value.retry_after == 3600

        # Test 402 Payment Required (Quota Exceeded)
        mock_response_402 = Mock()
        mock_response_402.status_code = 402
        mock_response_402.json.return_value = {"error": "Quota exceeded"}
        serply_provider.client.get.return_value = mock_response_402

        with pytest.raises(QuotaExceededError) as exc_info:
            await serply_provider._perform_search("test", 5, SearchType.SEARCH)
        assert exc_info.value.retry_after == 86400

        # Test 500 Server Error
        mock_response_500 = Mock()
        mock_response_500.status_code = 500
        mock_response_500.json.return_value = {"error": "Server error"}
        serply_provider.client.get.return_value = mock_response_500

        with pytest.raises(APIError):
            await serply_provider._perform_search("test", 5, SearchType.SEARCH)

    @pytest.mark.asyncio
    async def test_perform_search_network_error(self, serply_provider):
        """Test handling of network errors."""
        serply_provider.client = AsyncMock()
        serply_provider.client.get.side_effect = httpx.RequestError("Network error")

        with pytest.raises(NetworkError):
            await serply_provider._perform_search("test", 5, SearchType.SEARCH)

    @pytest.mark.asyncio
    async def test_perform_search_json_decode_error(self, serply_provider):
        """Test handling of JSON decode errors."""
        serply_provider.client = AsyncMock()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        serply_provider.client.get.return_value = mock_response

        with pytest.raises(APIError) as exc_info:
            await serply_provider._perform_search("test", 5, SearchType.SEARCH)
        assert "JSON response" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_extract_date_from_item(self, serply_provider):
        """Test extracting date from Serply item."""
        news_item = {
            "date": "2024-01-15",
            "title": "Test News Article",
        }

        date = serply_provider._extract_date_from_item(news_item, SearchType.NEWS)
        assert date == "2024-01-15"

        # Test item with published field
        item_with_published = {
            "published": "2024-01-16",
            "title": "Test Article",
        }

        date = serply_provider._extract_date_from_item(
            item_with_published, SearchType.SEARCH
        )
        assert date == "2024-01-16"

        # Test item without date
        item_without_date = {"title": "Test Page"}
        date = serply_provider._extract_date_from_item(
            item_without_date, SearchType.SEARCH
        )
        assert date is None

    @pytest.mark.asyncio
    async def test_extract_thumbnail(self, serply_provider):
        """Test extracting thumbnail from Serply item."""
        item_with_thumbnail = {
            "thumbnail": "https://example.com/thumbnail.jpg",
        }

        thumbnail = serply_provider._extract_thumbnail(item_with_thumbnail)
        assert thumbnail == "https://example.com/thumbnail.jpg"

        # Test alternative image format
        item_with_image = {
            "image": "https://example.com/image.jpg",
        }

        thumbnail = serply_provider._extract_thumbnail(item_with_image)
        assert thumbnail == "https://example.com/image.jpg"

        # Test item without thumbnail
        item_without_thumbnail = {"title": "Test Item"}
        thumbnail = serply_provider._extract_thumbnail(item_without_thumbnail)
        assert thumbnail is None

    def test_clean_url(self, serply_provider):
        """Test URL cleaning functionality."""
        # Test normal URL
        clean_url = serply_provider._clean_url("https://example.com")
        assert clean_url == "https://example.com"

        # Test URL without protocol
        clean_url = serply_provider._clean_url("example.com")
        assert clean_url == "https://example.com"

        # Test URL with // prefix
        clean_url = serply_provider._clean_url("//example.com")
        assert clean_url == "https://example.com"

        # Test invalid URL
        clean_url = serply_provider._clean_url("")
        assert clean_url is None

    def test_get_api_headers(self, serply_provider):
        """Test getting API headers."""
        headers = serply_provider._get_api_headers()

        assert "X-API-KEY" in headers
        assert "Accept" in headers
        assert "User-Agent" in headers
        assert headers["X-API-KEY"] == "test-api-key"
        assert headers["Accept"] == "application/json"
        assert "WebSearchMCP" in headers["User-Agent"]

    @pytest.mark.asyncio
    async def test_extract_result_from_data_missing_fields(self, serply_provider):
        """Test extracting result with missing required fields."""
        # Missing URL
        item_missing_url = {
            "title": "Test Title",
            "snippet": "Test snippet",
        }

        result = serply_provider._extract_result_from_data(
            item_missing_url, 1, SearchType.SEARCH
        )
        assert result is None

        # Missing title
        item_missing_title = {
            "link": "https://example.com",
            "snippet": "Test snippet",
        }

        result = serply_provider._extract_result_from_data(
            item_missing_title, 1, SearchType.SEARCH
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_search_method_enhancement(
        self, serply_provider, mock_web_response_success
    ):
        """Test the enhanced search method with result reordering."""
        await serply_provider.initialize()
        serply_provider.client = AsyncMock()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = mock_web_response_success
        serply_provider.client.get.return_value = mock_response

        result = await serply_provider.search(
            query="python tutorial", max_results=5, search_type=SearchType.SEARCH
        )

        assert result.success
        assert len(result.results) == 4

        # Check that results are properly ordered: KG, Answer Box, then Organic
        assert result.results[0].metadata.get("result_type") == "knowledge_graph"
        assert result.results[1].metadata.get("result_type") == "answer_box"
        assert result.results[2].metadata.get("result_type") is None  # Organic result
        assert result.results[3].metadata.get("result_type") is None  # Organic result

        # Check positions are updated correctly
        for i, search_result in enumerate(result.results, 1):
            assert search_result.position == i
