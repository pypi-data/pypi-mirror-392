"""
Unit tests for Google Custom Search provider.

Tests the Google Custom Search provider implementation to ensure
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
from web_search_mcp.providers.google import GoogleProvider


@pytest.fixture
def google_config():
    """Create a test configuration for Google Custom Search."""
    return ProviderConfig(
        enabled=True,
        api_key="test-api-key",
        additional_config={"cse_id": "test-cse-id"},
        timeout=30,
        max_retries=3,
    )


@pytest.fixture
def google_provider(google_config):
    """Create a Google Custom Search provider instance."""
    return GoogleProvider(SearchProvider.GOOGLE, google_config)


@pytest.fixture
def mock_response_success():
    """Mock successful Google Custom Search API response."""
    return {
        "items": [
            {
                "title": "Python Programming Tutorial",
                "link": "https://www.python.org/tutorial/",
                "snippet": "Learn Python programming with this comprehensive tutorial.",
                "displayLink": "python.org",
                "formattedUrl": "https://www.python.org/tutorial/",
                "pagemap": {
                    "metatags": [
                        {
                            "og:title": "Python Programming Tutorial",
                            "og:description": "Learn Python programming",
                            "datepublished": "2024-01-15",
                        }
                    ]
                },
            },
            {
                "title": "Advanced Python Concepts",
                "link": "https://realpython.com/advanced-python/",
                "snippet": "Master advanced Python programming concepts and techniques.",
                "displayLink": "realpython.com",
                "formattedUrl": "https://realpython.com/advanced-python/",
            },
        ],
        "searchInformation": {
            "totalResults": "1000000",
            "searchTime": 0.45,
        },
    }


class TestGoogleProvider:
    """Test cases for Google Custom Search provider."""

    @pytest.mark.asyncio
    async def test_validate_config_success(self, google_provider):
        """Test successful configuration validation."""
        # Should not raise any exception
        await google_provider._validate_config()

    @pytest.mark.asyncio
    async def test_validate_config_missing_api_key(self):
        """Test configuration validation with missing API key."""
        config = ProviderConfig(
            enabled=True,
            additional_config={"cse_id": "test-cse-id"},
        )
        provider = GoogleProvider(SearchProvider.GOOGLE, config)

        with pytest.raises(AuthenticationError) as exc_info:
            await provider._validate_config()

        assert "API key is required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_config_missing_cse_id(self):
        """Test configuration validation with missing CSE ID."""
        config = ProviderConfig(
            enabled=True,
            api_key="test-api-key",
        )
        provider = GoogleProvider(SearchProvider.GOOGLE, config)

        with pytest.raises(AuthenticationError) as exc_info:
            await provider._validate_config()

        assert "Custom Search Engine ID" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_build_request_params_web_search(self, google_provider):
        """Test building request parameters for web search."""
        params = google_provider._build_request_params(
            query="python tutorial",
            max_results=5,
            search_type=SearchType.SEARCH,
        )

        assert params["key"] == "test-api-key"
        assert params["cx"] == "test-cse-id"
        assert params["q"] == "python tutorial"
        assert params["num"] == 5
        assert params["safe"] == "medium"
        assert "tbm" not in params  # No news search parameter

    @pytest.mark.asyncio
    async def test_build_request_params_news_search(self, google_provider):
        """Test building request parameters for news search."""
        params = google_provider._build_request_params(
            query="tech news",
            max_results=3,
            search_type=SearchType.NEWS,
        )

        assert params["tbm"] == "nws"  # News search parameter
        assert params["sort"] == "date"  # Sort by date for news

    @pytest.mark.asyncio
    async def test_build_request_params_with_kwargs(self, google_provider):
        """Test building request parameters with additional kwargs."""
        params = google_provider._build_request_params(
            query="test query",
            max_results=10,
            search_type=SearchType.SEARCH,
            language="fr",
            country="ca",
            site="example.com",
            filetype="pdf",
        )

        assert params["lr"] == "lang_fr"
        assert params["gl"] == "ca"
        assert params["siteSearch"] == "example.com"
        assert params["fileType"] == "pdf"

    @pytest.mark.asyncio
    async def test_parse_search_results_success(
        self, google_provider, mock_response_success
    ):
        """Test successful parsing of search results."""
        results = google_provider._parse_search_results(mock_response_success, 10)

        assert len(results) == 2

        # Check first result
        result1 = results[0]
        assert result1.title == "Python Programming Tutorial"
        assert result1.url == "https://www.python.org/tutorial/"
        assert (
            result1.snippet
            == "Learn Python programming with this comprehensive tutorial."
        )
        assert result1.source == "python.org"
        assert result1.position == 1
        assert result1.date == "2024-01-15"
        assert result1.metadata["provider"] == "google"

        # Check second result
        result2 = results[1]
        assert result2.title == "Advanced Python Concepts"
        assert result2.url == "https://realpython.com/advanced-python/"
        assert result2.position == 2

    @pytest.mark.asyncio
    async def test_parse_search_results_empty(self, google_provider):
        """Test parsing empty search results."""
        empty_response = {"items": []}
        results = google_provider._parse_search_results(empty_response, 10)
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_extract_error_message_google_format(self, google_provider):
        """Test extracting error message from Google API error format."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "error": {
                "message": "Invalid API key",
                "code": 401,
            }
        }
        mock_response.text = "Fallback text"

        error_message = google_provider._extract_error_message(mock_response)
        assert error_message == "Invalid API key (Code: 401)"

    @pytest.mark.asyncio
    async def test_extract_error_message_fallback(self, google_provider):
        """Test extracting error message with fallback to response text."""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "Error response text"

        error_message = google_provider._extract_error_message(mock_response)
        assert error_message == "Error response text"

    @pytest.mark.asyncio
    async def test_perform_search_http_errors(self, google_provider):
        """Test handling of various HTTP error codes."""
        google_provider.client = AsyncMock()

        # Test 400 Bad Request
        mock_response_400 = Mock()
        mock_response_400.status_code = 400
        mock_response_400.json.return_value = {"error": {"message": "Bad request"}}
        google_provider.client.get.return_value = mock_response_400

        with pytest.raises(ValidationError):
            await google_provider._perform_search("test", 5, SearchType.SEARCH)

        # Test 401 Unauthorized
        mock_response_401 = Mock()
        mock_response_401.status_code = 401
        mock_response_401.json.return_value = {"error": {"message": "Unauthorized"}}
        google_provider.client.get.return_value = mock_response_401

        with pytest.raises(AuthenticationError):
            await google_provider._perform_search("test", 5, SearchType.SEARCH)

        # Test 403 Quota Exceeded
        mock_response_403 = Mock()
        mock_response_403.status_code = 403
        mock_response_403.json.return_value = {"error": {"message": "Quota exceeded"}}
        google_provider.client.get.return_value = mock_response_403

        with pytest.raises(QuotaExceededError):
            await google_provider._perform_search("test", 5, SearchType.SEARCH)

        # Test 429 Rate Limited
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        mock_response_429.headers = {"Retry-After": "3600"}
        mock_response_429.json.return_value = {"error": {"message": "Rate limited"}}
        google_provider.client.get.return_value = mock_response_429

        with pytest.raises(QuotaExceededError) as exc_info:
            await google_provider._perform_search("test", 5, SearchType.SEARCH)
        assert exc_info.value.retry_after == 3600

        # Test 500 Server Error
        mock_response_500 = Mock()
        mock_response_500.status_code = 500
        mock_response_500.json.return_value = {"error": {"message": "Server error"}}
        google_provider.client.get.return_value = mock_response_500

        with pytest.raises(APIError):
            await google_provider._perform_search("test", 5, SearchType.SEARCH)

    @pytest.mark.asyncio
    async def test_perform_search_network_error(self, google_provider):
        """Test handling of network errors."""
        google_provider.client = AsyncMock()
        google_provider.client.get.side_effect = httpx.RequestError("Network error")

        with pytest.raises(NetworkError):
            await google_provider._perform_search("test", 5, SearchType.SEARCH)

    @pytest.mark.asyncio
    async def test_perform_search_json_decode_error(self, google_provider):
        """Test handling of JSON decode errors."""
        google_provider.client = AsyncMock()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        google_provider.client.get.return_value = mock_response

        with pytest.raises(APIError) as exc_info:
            await google_provider._perform_search("test", 5, SearchType.SEARCH)
        assert "JSON response" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_extract_date_from_item(self, google_provider):
        """Test extracting date from Google Custom Search item."""
        item_with_date = {
            "pagemap": {
                "metatags": [
                    {
                        "datepublished": "2024-01-15",
                        "og:title": "Test Article",
                    }
                ]
            }
        }

        date = google_provider._extract_date_from_item(item_with_date)
        assert date == "2024-01-15"

        # Test item without date
        item_without_date = {"pagemap": {}}
        date = google_provider._extract_date_from_item(item_without_date)
        assert date is None

    @pytest.mark.asyncio
    async def test_extract_thumbnail(self, google_provider):
        """Test extracting thumbnail from Google Custom Search item."""
        item_with_thumbnail = {
            "pagemap": {
                "cse_thumbnail": [
                    {
                        "src": "https://example.com/thumbnail.jpg",
                    }
                ]
            }
        }

        thumbnail = google_provider._extract_thumbnail(item_with_thumbnail)
        assert thumbnail == "https://example.com/thumbnail.jpg"

        # Test item without thumbnail
        item_without_thumbnail = {"pagemap": {}}
        thumbnail = google_provider._extract_thumbnail(item_without_thumbnail)
        assert thumbnail is None

    def test_get_api_headers(self, google_provider):
        """Test getting API headers."""
        headers = google_provider._get_api_headers()

        assert "Accept" in headers
        assert "User-Agent" in headers
        assert headers["Accept"] == "application/json"
        assert "WebSearchMCP" in headers["User-Agent"]
