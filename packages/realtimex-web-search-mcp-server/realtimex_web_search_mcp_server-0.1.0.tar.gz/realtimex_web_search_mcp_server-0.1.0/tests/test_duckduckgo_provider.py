"""
Tests for DuckDuckGo search provider.

Comprehensive tests including unit tests with mocked responses and
integration tests with real API calls.
"""

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from web_search_mcp.config import ProviderConfig
from web_search_mcp.models import SearchProvider, SearchType
from web_search_mcp.providers.duckduckgo import DuckDuckGoProvider


class TestDuckDuckGoProvider:
    """Test suite for DuckDuckGo search provider."""

    @pytest.fixture
    def provider_config(self):
        """Create a basic provider configuration for testing."""
        return ProviderConfig(
            enabled=True,
            timeout=30,
            max_retries=3,
        )

    @pytest.fixture
    def duckduckgo_provider(self, provider_config):
        """Create a DuckDuckGo provider instance for testing."""
        return DuckDuckGoProvider(SearchProvider.DUCKDUCKGO, provider_config)

    @pytest.fixture
    def sample_html_response(self):
        """Sample DuckDuckGo HTML response for testing."""
        return """
        <!DOCTYPE html>
        <html>
        <head><title>DuckDuckGo Search Results</title></head>
        <body>
            <div class="result results_links">
                <div class="result__body">
                    <a class="result__a" href="https://example.com/page1">
                        Example Page 1 - Test Result
                    </a>
                    <a class="result__snippet" href="#">
                        This is a sample snippet for the first test result. It contains relevant information about the search query.
                    </a>
                </div>
            </div>
            <div class="result results_links">
                <div class="result__body">
                    <a class="result__a" href="https://example.com/page2">
                        Example Page 2 - Another Test
                    </a>
                    <a class="result__snippet" href="#">
                        This is another sample snippet with different content to test parsing capabilities.
                    </a>
                </div>
            </div>
            <div class="result results_links">
                <div class="result__body">
                    <a class="result__a" href="https://example.com/page3">
                        Example Page 3 - Third Result
                    </a>
                    <a class="result__snippet" href="#">
                        A third snippet to ensure we can parse multiple results correctly.
                    </a>
                </div>
            </div>
        </body>
        </html>
        """

    async def test_provider_initialization(self, duckduckgo_provider):
        """Test that the provider initializes correctly."""
        assert not duckduckgo_provider._initialized
        assert duckduckgo_provider.client is None

        await duckduckgo_provider.initialize()

        assert duckduckgo_provider._initialized
        assert duckduckgo_provider.client is not None
        assert isinstance(duckduckgo_provider.client, httpx.AsyncClient)

        # Clean up
        await duckduckgo_provider.close()

    async def test_provider_cleanup(self, duckduckgo_provider):
        """Test that the provider cleans up resources correctly."""
        await duckduckgo_provider.initialize()
        assert duckduckgo_provider._initialized
        assert duckduckgo_provider.client is not None

        await duckduckgo_provider.close()
        assert duckduckgo_provider.client is None
        assert not duckduckgo_provider._initialized

    def test_build_search_url(self, duckduckgo_provider):
        """Test URL building for different search types."""
        # Test basic web search
        url = duckduckgo_provider._build_search_url("test query", SearchType.SEARCH)
        assert "q=test+query" in url
        assert duckduckgo_provider.BASE_URL in url
        assert "kl=us-en" in url

        # Test news search
        url = duckduckgo_provider._build_search_url("news query", SearchType.NEWS)
        assert "q=news+query" in url
        assert "iar=news" in url

    def test_parse_search_results(self, duckduckgo_provider, sample_html_response):
        """Test parsing of HTML search results."""
        results = duckduckgo_provider._parse_search_results(sample_html_response, 10)

        assert len(results) == 3

        # Check first result
        first_result = results[0]
        assert first_result.title == "Example Page 1 - Test Result"
        assert first_result.url == "https://example.com/page1"
        assert "sample snippet for the first test result" in first_result.snippet
        assert first_result.position == 1
        assert first_result.source == "example.com"

        # Check second result
        second_result = results[1]
        assert second_result.title == "Example Page 2 - Another Test"
        assert second_result.url == "https://example.com/page2"
        assert second_result.position == 2

        # Check third result
        third_result = results[2]
        assert third_result.title == "Example Page 3 - Third Result"
        assert third_result.url == "https://example.com/page3"
        assert third_result.position == 3

    def test_parse_search_results_with_limit(
        self, duckduckgo_provider, sample_html_response
    ):
        """Test parsing with result limit."""
        results = duckduckgo_provider._parse_search_results(sample_html_response, 2)
        assert len(results) == 2

    def test_clean_url(self, duckduckgo_provider):
        """Test URL cleaning functionality."""
        # Test normal URL
        assert (
            duckduckgo_provider._clean_url("https://example.com")
            == "https://example.com"
        )

        # Test URL without protocol
        assert duckduckgo_provider._clean_url("example.com") == "https://example.com"

        # Test protocol-relative URL
        assert duckduckgo_provider._clean_url("//example.com") == "https://example.com"

        # Test invalid URL
        assert duckduckgo_provider._clean_url("") is None
        assert duckduckgo_provider._clean_url("not-a-url") == "https://not-a-url"

    def test_extract_domain(self, duckduckgo_provider):
        """Test domain extraction from URLs."""
        assert (
            duckduckgo_provider._extract_domain("https://www.example.com/path")
            == "example.com"
        )
        assert (
            duckduckgo_provider._extract_domain("https://example.com") == "example.com"
        )
        assert (
            duckduckgo_provider._extract_domain("http://subdomain.example.com")
            == "subdomain.example.com"
        )
        assert duckduckgo_provider._extract_domain("invalid-url") == "unknown"

    def test_clean_text(self, duckduckgo_provider):
        """Test text cleaning functionality."""
        # Test normal text
        assert duckduckgo_provider._clean_text("Normal text") == "Normal text"

        # Test text with extra whitespace
        assert (
            duckduckgo_provider._clean_text("  Text  with   spaces  ")
            == "Text with spaces"
        )

        # Test text with HTML entities
        assert (
            duckduckgo_provider._clean_text("Text &amp; more &lt;text&gt;")
            == "Text & more <text>"
        )

        # Test empty text
        assert duckduckgo_provider._clean_text("") == ""
        assert duckduckgo_provider._clean_text(None) == ""

    @pytest.mark.asyncio
    async def test_search_with_mocked_response(
        self, duckduckgo_provider, sample_html_response
    ):
        """Test search functionality with mocked HTTP response."""
        # Mock the HTTP client
        mock_response = AsyncMock()
        mock_response.text = sample_html_response
        mock_response.raise_for_status = AsyncMock()

        with patch.object(duckduckgo_provider, "client") as mock_client:
            mock_client.get = AsyncMock(return_value=mock_response)

            # Initialize provider
            await duckduckgo_provider.initialize()

            # Perform search
            result = await duckduckgo_provider.search(
                query="test query", max_results=10, search_type=SearchType.SEARCH
            )

            # Verify results
            assert result.success is True
            assert result.provider == SearchProvider.DUCKDUCKGO
            assert result.query == "test query"
            assert len(result.results) == 3
            assert result.results_returned == 3
            assert result.search_time > 0
            assert result.error is None

            # Verify HTTP call was made
            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args[0]
            assert "test+query" in call_args[0]

    @pytest.mark.asyncio
    async def test_search_with_http_error(self, duckduckgo_provider):
        """Test search behavior when HTTP error occurs."""
        # Mock HTTP error
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        http_error = httpx.HTTPStatusError(
            "Server Error", request=AsyncMock(), response=mock_response
        )

        with patch.object(duckduckgo_provider, "client") as mock_client:
            mock_client.get = AsyncMock(side_effect=http_error)

            # Initialize provider
            await duckduckgo_provider.initialize()

            # Perform search
            result = await duckduckgo_provider.search(
                query="test query", max_results=10, search_type=SearchType.SEARCH
            )

            # Verify error handling
            assert result.success is False
            assert result.provider == SearchProvider.DUCKDUCKGO
            assert result.query == "test query"
            assert len(result.results) == 0
            assert result.results_returned == 0
            assert result.error is not None
            assert "500" in result.error

    @pytest.mark.asyncio
    async def test_search_with_network_error(self, duckduckgo_provider):
        """Test search behavior when network error occurs."""
        # Mock network error
        network_error = httpx.ConnectError("Connection failed")

        with patch.object(duckduckgo_provider, "client") as mock_client:
            mock_client.get = AsyncMock(side_effect=network_error)

            # Initialize provider
            await duckduckgo_provider.initialize()

            # Perform search
            result = await duckduckgo_provider.search(
                query="test query", max_results=10, search_type=SearchType.SEARCH
            )

            # Verify error handling
            assert result.success is False
            assert result.error is not None
            assert "NetworkError" in result.error_type

    @pytest.mark.asyncio
    async def test_search_with_empty_results(self, duckduckgo_provider):
        """Test search behavior when no results are found."""
        empty_html = "<html><body><div>No results found</div></body></html>"

        mock_response = AsyncMock()
        mock_response.text = empty_html
        mock_response.raise_for_status = AsyncMock()

        with patch.object(duckduckgo_provider, "client") as mock_client:
            mock_client.get = AsyncMock(return_value=mock_response)

            # Initialize provider
            await duckduckgo_provider.initialize()

            # Perform search
            result = await duckduckgo_provider.search(
                query="nonexistent query", max_results=10, search_type=SearchType.SEARCH
            )

            # Verify results
            assert result.success is True  # Success even with no results
            assert len(result.results) == 0
            assert result.results_returned == 0

    def test_get_default_headers(self, duckduckgo_provider):
        """Test that DuckDuckGo-specific headers are included."""
        headers = duckduckgo_provider._get_default_headers()

        assert "User-Agent" in headers
        assert "Referer" in headers
        assert headers["Referer"] == "https://duckduckgo.com/"
        assert headers["Origin"] == "https://duckduckgo.com"
        assert "Sec-Fetch-Dest" in headers


@pytest.mark.integration
class TestDuckDuckGoIntegration:
    """Integration tests that make real API calls to DuckDuckGo."""

    @pytest.fixture
    def provider_config(self):
        """Create a provider configuration for integration testing."""
        return ProviderConfig(
            enabled=True,
            timeout=30,
            max_retries=2,
        )

    @pytest.fixture
    def duckduckgo_provider(self, provider_config):
        """Create a DuckDuckGo provider instance for integration testing."""
        return DuckDuckGoProvider(SearchProvider.DUCKDUCKGO, provider_config)

    @pytest.mark.asyncio
    async def test_real_search(self, duckduckgo_provider):
        """Test a real search against DuckDuckGo (requires internet connection)."""
        try:
            await duckduckgo_provider.initialize()

            result = await duckduckgo_provider.search(
                query="python programming", max_results=5, search_type=SearchType.SEARCH
            )

            # Verify basic structure
            assert result.provider == SearchProvider.DUCKDUCKGO
            assert result.query == "python programming"
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

        finally:
            await duckduckgo_provider.close()

    @pytest.mark.asyncio
    async def test_real_news_search(self, duckduckgo_provider):
        """Test a real news search against DuckDuckGo."""
        try:
            await duckduckgo_provider.initialize()

            result = await duckduckgo_provider.search(
                query="technology news", max_results=3, search_type=SearchType.NEWS
            )

            # Verify basic structure
            assert result.provider == SearchProvider.DUCKDUCKGO
            assert result.query == "technology news"
            assert isinstance(result.results, list)

        finally:
            await duckduckgo_provider.close()
