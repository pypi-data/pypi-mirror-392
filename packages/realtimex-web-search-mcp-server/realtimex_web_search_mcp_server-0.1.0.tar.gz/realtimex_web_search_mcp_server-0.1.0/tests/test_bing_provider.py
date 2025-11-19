"""
Unit tests for Bing Search provider.

Tests the Bing Search provider implementation to ensure
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
from web_search_mcp.providers.bing import BingProvider


@pytest.fixture
def bing_config():
    """Create a test configuration for Bing Search."""
    return ProviderConfig(
        enabled=True,
        api_key="test-api-key",
        timeout=30,
        max_retries=3,
    )


@pytest.fixture
def bing_provider(bing_config):
    """Create a Bing Search provider instance."""
    return BingProvider(SearchProvider.BING, bing_config)


@pytest.fixture
def mock_web_response_success():
    """Mock successful Bing Web Search API response."""
    return {
        "webPages": {
            "value": [
                {
                    "id": "https://api.bing.microsoft.com/api/v7/#WebPages.0",
                    "name": "Python Programming Tutorial",
                    "url": "https://www.python.org/tutorial/",
                    "snippet": "Learn Python programming with this comprehensive tutorial covering basics to advanced topics.",
                    "displayUrl": "python.org",
                    "dateLastCrawled": "2024-01-15T10:30:00.0000000Z",
                },
                {
                    "id": "https://api.bing.microsoft.com/api/v7/#WebPages.1",
                    "name": "Advanced Python Concepts",
                    "url": "https://realpython.com/advanced-python/",
                    "snippet": "Master advanced Python programming concepts including decorators, generators, and metaclasses.",
                    "displayUrl": "realpython.com",
                },
            ]
        }
    }


@pytest.fixture
def mock_news_response_success():
    """Mock successful Bing News Search API response."""
    return {
        "value": [
            {
                "id": "https://api.bing.microsoft.com/api/v7/#News.0",
                "name": "AI Technology Breakthrough",
                "url": "https://techcrunch.com/ai-breakthrough/",
                "snippet": "Scientists announce major breakthrough in artificial intelligence research.",
                "datePublished": "2024-01-15T08:00:00.0000000Z",
                "provider": [{"name": "TechCrunch"}],
                "category": "Technology",
                "image": {
                    "thumbnail": {"contentUrl": "https://example.com/thumbnail.jpg"}
                },
            }
        ]
    }


class TestBingProvider:
    """Test cases for Bing Search provider."""

    @pytest.mark.asyncio
    async def test_validate_config_success(self, bing_provider):
        """Test successful configuration validation."""
        # Should not raise any exception
        await bing_provider._validate_config()

    @pytest.mark.asyncio
    async def test_validate_config_missing_api_key(self):
        """Test configuration validation with missing API key."""
        config = ProviderConfig(enabled=True)
        provider = BingProvider(SearchProvider.BING, config)

        with pytest.raises(AuthenticationError) as exc_info:
            await provider._validate_config()

        assert "API key is required" in str(exc_info.value)

    def test_get_endpoint_web_search(self, bing_provider):
        """Test getting endpoint for web search."""
        endpoint = bing_provider._get_endpoint(SearchType.SEARCH)
        assert endpoint == "https://api.bing.microsoft.com/v7.0/search"

    def test_get_endpoint_news_search(self, bing_provider):
        """Test getting endpoint for news search."""
        endpoint = bing_provider._get_endpoint(SearchType.NEWS)
        assert endpoint == "https://api.bing.microsoft.com/v7.0/news/search"

    @pytest.mark.asyncio
    async def test_build_request_params_web_search(self, bing_provider):
        """Test building request parameters for web search."""
        params = bing_provider._build_request_params(
            query="python tutorial",
            max_results=5,
            search_type=SearchType.SEARCH,
        )

        assert params["q"] == "python tutorial"
        assert params["count"] == 5
        assert params["offset"] == 0
        assert params["mkt"] == "en-US"
        assert params["safeSearch"] == "Moderate"
        assert params["responseFilter"] == "Webpages"
        assert "sortBy" not in params  # No news-specific parameters

    @pytest.mark.asyncio
    async def test_build_request_params_news_search(self, bing_provider):
        """Test building request parameters for news search."""
        params = bing_provider._build_request_params(
            query="tech news",
            max_results=3,
            search_type=SearchType.NEWS,
        )

        assert params["sortBy"] == "Date"  # News-specific parameter
        assert params["freshness"] == "Day"  # News freshness
        assert "responseFilter" not in params  # No web-specific parameters

    @pytest.mark.asyncio
    async def test_build_request_params_with_kwargs(self, bing_provider):
        """Test building request parameters with additional kwargs."""
        params = bing_provider._build_request_params(
            query="test query",
            max_results=10,
            search_type=SearchType.SEARCH,
            market="fr-FR",
            country="FR",
            language="fr",
            safe_search="strict",
            site="example.com",
        )

        assert params["mkt"] == "fr-FR"
        assert params["cc"] == "FR"
        assert params["setLang"] == "fr"
        assert params["safeSearch"] == "Strict"
        assert "site:example.com" in params["q"]

    @pytest.mark.asyncio
    async def test_parse_web_search_results_success(
        self, bing_provider, mock_web_response_success
    ):
        """Test successful parsing of web search results."""
        results = bing_provider._parse_search_results(
            mock_web_response_success, 10, SearchType.SEARCH
        )

        assert len(results) == 2

        # Check first result
        result1 = results[0]
        assert result1.title == "Python Programming Tutorial"
        assert result1.url == "https://www.python.org/tutorial/"
        assert (
            result1.snippet
            == "Learn Python programming with this comprehensive tutorial covering basics to advanced topics."
        )
        assert result1.source == "python.org"
        assert result1.position == 1
        assert result1.date == "2024-01-15T10:30:00.0000000Z"
        assert result1.metadata["provider"] == "bing"
        assert result1.metadata["search_type"] == "search"

        # Check second result
        result2 = results[1]
        assert result2.title == "Advanced Python Concepts"
        assert result2.url == "https://realpython.com/advanced-python/"
        assert result2.position == 2

    @pytest.mark.asyncio
    async def test_parse_news_search_results_success(
        self, bing_provider, mock_news_response_success
    ):
        """Test successful parsing of news search results."""
        results = bing_provider._parse_search_results(
            mock_news_response_success, 10, SearchType.NEWS
        )

        assert len(results) == 1

        # Check news result
        result = results[0]
        assert result.title == "AI Technology Breakthrough"
        assert result.url == "https://techcrunch.com/ai-breakthrough/"
        assert (
            result.snippet
            == "Scientists announce major breakthrough in artificial intelligence research."
        )
        assert result.position == 1
        assert result.date == "2024-01-15T08:00:00.0000000Z"
        assert result.thumbnail == "https://example.com/thumbnail.jpg"
        assert result.metadata["provider"] == "bing"
        assert result.metadata["search_type"] == "news"
        assert result.metadata["news_provider"] == "TechCrunch"
        assert result.metadata["news_category"] == "Technology"

    @pytest.mark.asyncio
    async def test_parse_search_results_empty(self, bing_provider):
        """Test parsing empty search results."""
        empty_web_response = {"webPages": {"value": []}}
        results = bing_provider._parse_search_results(
            empty_web_response, 10, SearchType.SEARCH
        )
        assert len(results) == 0

        empty_news_response = {"value": []}
        results = bing_provider._parse_search_results(
            empty_news_response, 10, SearchType.NEWS
        )
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_extract_error_message_bing_format(self, bing_provider):
        """Test extracting error message from Bing API error format."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "errors": [
                {
                    "message": "Invalid API key",
                    "code": "InvalidApiKey",
                }
            ]
        }
        mock_response.text = "Fallback text"

        error_message = bing_provider._extract_error_message(mock_response)
        assert error_message == "Invalid API key (Code: InvalidApiKey)"

    @pytest.mark.asyncio
    async def test_extract_error_message_alternative_format(self, bing_provider):
        """Test extracting error message from alternative Bing error format."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "error": {
                "message": "Quota exceeded",
                "code": "QuotaExceeded",
            }
        }
        mock_response.text = "Fallback text"

        error_message = bing_provider._extract_error_message(mock_response)
        assert error_message == "Quota exceeded (Code: QuotaExceeded)"

    @pytest.mark.asyncio
    async def test_extract_error_message_fallback(self, bing_provider):
        """Test extracting error message with fallback to response text."""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "Error response text"

        error_message = bing_provider._extract_error_message(mock_response)
        assert error_message == "Error response text"

    @pytest.mark.asyncio
    async def test_perform_search_http_errors(self, bing_provider):
        """Test handling of various HTTP error codes."""
        bing_provider.client = AsyncMock()

        # Test 400 Bad Request
        mock_response_400 = Mock()
        mock_response_400.status_code = 400
        mock_response_400.json.return_value = {"errors": [{"message": "Bad request"}]}
        bing_provider.client.get.return_value = mock_response_400

        with pytest.raises(ValidationError):
            await bing_provider._perform_search("test", 5, SearchType.SEARCH)

        # Test 401 Unauthorized
        mock_response_401 = Mock()
        mock_response_401.status_code = 401
        mock_response_401.json.return_value = {"errors": [{"message": "Unauthorized"}]}
        bing_provider.client.get.return_value = mock_response_401

        with pytest.raises(AuthenticationError):
            await bing_provider._perform_search("test", 5, SearchType.SEARCH)

        # Test 403 Forbidden
        mock_response_403 = Mock()
        mock_response_403.status_code = 403
        mock_response_403.json.return_value = {"errors": [{"message": "Forbidden"}]}
        bing_provider.client.get.return_value = mock_response_403

        with pytest.raises(AuthenticationError):
            await bing_provider._perform_search("test", 5, SearchType.SEARCH)

        # Test 429 Rate Limited
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        mock_response_429.headers = {"Retry-After": "3600"}
        mock_response_429.json.return_value = {"errors": [{"message": "Rate limited"}]}
        bing_provider.client.get.return_value = mock_response_429

        with pytest.raises(QuotaExceededError) as exc_info:
            await bing_provider._perform_search("test", 5, SearchType.SEARCH)
        assert exc_info.value.retry_after == 3600

        # Test 503 Quota Exceeded
        mock_response_503 = Mock()
        mock_response_503.status_code = 503
        mock_response_503.json.return_value = {
            "errors": [{"message": "Quota exceeded"}]
        }
        bing_provider.client.get.return_value = mock_response_503

        with pytest.raises(QuotaExceededError) as exc_info:
            await bing_provider._perform_search("test", 5, SearchType.SEARCH)
        assert exc_info.value.retry_after == 86400

        # Test 500 Server Error
        mock_response_500 = Mock()
        mock_response_500.status_code = 500
        mock_response_500.json.return_value = {"errors": [{"message": "Server error"}]}
        bing_provider.client.get.return_value = mock_response_500

        with pytest.raises(APIError):
            await bing_provider._perform_search("test", 5, SearchType.SEARCH)

    @pytest.mark.asyncio
    async def test_perform_search_network_error(self, bing_provider):
        """Test handling of network errors."""
        bing_provider.client = AsyncMock()
        bing_provider.client.get.side_effect = httpx.RequestError("Network error")

        with pytest.raises(NetworkError):
            await bing_provider._perform_search("test", 5, SearchType.SEARCH)

    @pytest.mark.asyncio
    async def test_perform_search_json_decode_error(self, bing_provider):
        """Test handling of JSON decode errors."""
        bing_provider.client = AsyncMock()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        bing_provider.client.get.return_value = mock_response

        with pytest.raises(APIError) as exc_info:
            await bing_provider._perform_search("test", 5, SearchType.SEARCH)
        assert "JSON response" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_extract_date_from_item_news(self, bing_provider):
        """Test extracting date from Bing news item."""
        news_item = {
            "datePublished": "2024-01-15T08:00:00.0000000Z",
            "name": "Test News Article",
        }

        date = bing_provider._extract_date_from_item(news_item, SearchType.NEWS)
        assert date == "2024-01-15T08:00:00.0000000Z"

    @pytest.mark.asyncio
    async def test_extract_date_from_item_web(self, bing_provider):
        """Test extracting date from Bing web item."""
        web_item = {
            "dateLastCrawled": "2024-01-15T10:30:00.0000000Z",
            "name": "Test Web Page",
        }

        date = bing_provider._extract_date_from_item(web_item, SearchType.SEARCH)
        assert date == "2024-01-15T10:30:00.0000000Z"

        # Test item without date
        item_without_date = {"name": "Test Page"}
        date = bing_provider._extract_date_from_item(
            item_without_date, SearchType.SEARCH
        )
        assert date is None

    @pytest.mark.asyncio
    async def test_extract_thumbnail(self, bing_provider):
        """Test extracting thumbnail from Bing item."""
        item_with_thumbnail = {
            "image": {
                "thumbnail": {
                    "contentUrl": "https://example.com/thumbnail.jpg",
                }
            }
        }

        thumbnail = bing_provider._extract_thumbnail(item_with_thumbnail)
        assert thumbnail == "https://example.com/thumbnail.jpg"

        # Test alternative thumbnail format
        item_with_direct_thumbnail = {
            "thumbnail": {
                "contentUrl": "https://example.com/thumb2.jpg",
            }
        }

        thumbnail = bing_provider._extract_thumbnail(item_with_direct_thumbnail)
        assert thumbnail == "https://example.com/thumb2.jpg"

        # Test item without thumbnail
        item_without_thumbnail = {"name": "Test Item"}
        thumbnail = bing_provider._extract_thumbnail(item_without_thumbnail)
        assert thumbnail is None

    def test_get_api_headers(self, bing_provider):
        """Test getting API headers."""
        headers = bing_provider._get_api_headers()

        assert "Ocp-Apim-Subscription-Key" in headers
        assert "Accept" in headers
        assert "User-Agent" in headers
        assert headers["Ocp-Apim-Subscription-Key"] == "test-api-key"
        assert headers["Accept"] == "application/json"
        assert "WebSearchMCP" in headers["User-Agent"]

    @pytest.mark.asyncio
    async def test_extract_result_from_data_missing_fields(self, bing_provider):
        """Test extracting result with missing required fields."""
        # Missing URL
        item_missing_url = {
            "name": "Test Title",
            "snippet": "Test snippet",
        }

        result = bing_provider._extract_result_from_data(
            item_missing_url, 1, SearchType.SEARCH
        )
        assert result is None

        # Missing title
        item_missing_title = {
            "url": "https://example.com",
            "snippet": "Test snippet",
        }

        result = bing_provider._extract_result_from_data(
            item_missing_title, 1, SearchType.SEARCH
        )
        assert result is None
