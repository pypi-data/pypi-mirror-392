"""
Configuration management for Web Search MCP Server.

Handles environment-based configuration for search providers and server settings
with validation and secure credential management.
"""

import os
from typing import Any

import structlog
from pydantic import BaseModel, Field

from web_search_mcp.models import SearchProvider

logger = structlog.get_logger(__name__)


class ProviderConfig(BaseModel):
    """Configuration for a specific search provider."""

    enabled: bool = Field(default=True, description="Whether provider is enabled")
    api_key: str | None = Field(None, description="API key for the provider")
    base_url: str | None = Field(None, description="Base URL for the provider")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    rate_limit: int | None = Field(None, description="Rate limit per minute")
    additional_config: dict[str, Any] = Field(
        default_factory=dict, description="Provider-specific additional configuration"
    )


class ServerConfig(BaseModel):
    """MCP server configuration."""

    server_name: str = Field(default="web-search-mcp", description="MCP server name")
    server_version: str = Field(default="1.0.0", description="MCP server version")
    default_provider: SearchProvider = Field(
        default=SearchProvider.GOOGLE, description="Default search provider"
    )
    default_max_results: int = Field(
        default=10, description="Default maximum results per search"
    )
    default_timeout: int = Field(
        default=30, description="Default request timeout in seconds"
    )
    enable_fallbacks: bool = Field(
        default=True, description="Enable automatic provider fallbacks"
    )


class WebSearchConfig(BaseModel):
    """Complete configuration for Web Search MCP Server."""

    server: ServerConfig = Field(default_factory=ServerConfig)
    providers: dict[SearchProvider, ProviderConfig] = Field(
        default_factory=dict, description="Provider-specific configurations"
    )

    def get_provider_config(self, provider: SearchProvider) -> ProviderConfig:
        """Get configuration for a specific provider."""
        return self.providers.get(provider, ProviderConfig())

    def is_provider_enabled(self, provider: SearchProvider) -> bool:
        """Check if a provider is enabled and properly configured."""
        config = self.get_provider_config(provider)
        if not config.enabled:
            return False

        # Check provider-specific requirements
        if provider == SearchProvider.GOOGLE:
            return bool(config.api_key and config.additional_config.get("cse_id"))
        elif provider in [
            SearchProvider.BING,
            SearchProvider.SERPAPI,
            SearchProvider.SERPER,
            SearchProvider.SERPLY,
            SearchProvider.TAVILY,
        ]:
            return bool(config.api_key)
        elif provider == SearchProvider.SEARXNG:
            return bool(config.base_url)
        elif provider == SearchProvider.DUCKDUCKGO:
            return True  # No configuration required

        return False

    def get_enabled_providers(self) -> list[SearchProvider]:
        """Get list of enabled and properly configured providers."""
        return [
            provider
            for provider in SearchProvider
            if self.is_provider_enabled(provider)
        ]


def load_config() -> WebSearchConfig:
    """
    Load configuration from environment variables.

    Returns:
        WebSearchConfig with all settings loaded from environment

    Raises:
        ValueError: If required configuration is missing
    """
    logger.info("Loading Web Search MCP server configuration")

    try:
        # Load server configuration
        server_config = ServerConfig(
            server_name=os.getenv("WEB_SEARCH_SERVER_NAME", "web-search-mcp"),
            server_version=os.getenv("WEB_SEARCH_SERVER_VERSION", "1.0.0"),
            default_provider=SearchProvider(
                os.getenv("WEB_SEARCH_DEFAULT_PROVIDER", "google")
            ),
            default_max_results=int(os.getenv("WEB_SEARCH_DEFAULT_MAX_RESULTS", "10")),
            default_timeout=int(os.getenv("WEB_SEARCH_DEFAULT_TIMEOUT", "30")),
            enable_fallbacks=os.getenv("WEB_SEARCH_ENABLE_FALLBACKS", "true").lower()
            == "true",
        )

        # Load provider configurations
        providers = {}

        # Google Custom Search
        google_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        google_cse_id = os.getenv("GOOGLE_CSE_ID")
        if google_api_key and google_cse_id:
            providers[SearchProvider.GOOGLE] = ProviderConfig(
                enabled=True,
                api_key=google_api_key,
                timeout=int(os.getenv("GOOGLE_SEARCH_TIMEOUT", "30")),
                max_retries=int(os.getenv("GOOGLE_SEARCH_MAX_RETRIES", "3")),
                additional_config={"cse_id": google_cse_id},
            )

        # Bing Search
        bing_api_key = os.getenv("BING_SEARCH_API_KEY")
        if bing_api_key:
            providers[SearchProvider.BING] = ProviderConfig(
                enabled=True,
                api_key=bing_api_key,
                timeout=int(os.getenv("BING_SEARCH_TIMEOUT", "30")),
                max_retries=int(os.getenv("BING_SEARCH_MAX_RETRIES", "3")),
            )

        # SerpAPI
        serpapi_key = os.getenv("SERPAPI_API_KEY")
        if serpapi_key:
            providers[SearchProvider.SERPAPI] = ProviderConfig(
                enabled=True,
                api_key=serpapi_key,
                timeout=int(os.getenv("SERPAPI_TIMEOUT", "30")),
                max_retries=int(os.getenv("SERPAPI_MAX_RETRIES", "3")),
            )

        # Serply
        serply_key = os.getenv("SERPLY_API_KEY")
        if serply_key:
            providers[SearchProvider.SERPLY] = ProviderConfig(
                enabled=True,
                api_key=serply_key,
                timeout=int(os.getenv("SERPLY_TIMEOUT", "30")),
                max_retries=int(os.getenv("SERPLY_MAX_RETRIES", "3")),
            )

        # SearXNG
        searxng_url = os.getenv("SEARXNG_BASE_URL")
        if searxng_url:
            providers[SearchProvider.SEARXNG] = ProviderConfig(
                enabled=True,
                base_url=searxng_url,
                timeout=int(os.getenv("SEARXNG_TIMEOUT", "30")),
                max_retries=int(os.getenv("SEARXNG_MAX_RETRIES", "3")),
            )

        # Serper
        serper_key = os.getenv("SERPER_API_KEY")
        if serper_key:
            providers[SearchProvider.SERPER] = ProviderConfig(
                enabled=True,
                api_key=serper_key,
                timeout=int(os.getenv("SERPER_TIMEOUT", "30")),
                max_retries=int(os.getenv("SERPER_MAX_RETRIES", "3")),
            )

        # Tavily
        tavily_key = os.getenv("TAVILY_API_KEY")
        if tavily_key:
            providers[SearchProvider.TAVILY] = ProviderConfig(
                enabled=True,
                api_key=tavily_key,
                timeout=int(os.getenv("TAVILY_TIMEOUT", "30")),
                max_retries=int(os.getenv("TAVILY_MAX_RETRIES", "3")),
            )

        # DuckDuckGo (always available)
        providers[SearchProvider.DUCKDUCKGO] = ProviderConfig(
            enabled=True,
            timeout=int(os.getenv("DUCKDUCKGO_TIMEOUT", "30")),
            max_retries=int(os.getenv("DUCKDUCKGO_MAX_RETRIES", "3")),
        )

        config = WebSearchConfig(server=server_config, providers=providers)

        # Validate at least one provider is available
        enabled_providers = config.get_enabled_providers()
        if not enabled_providers:
            raise ValueError(
                "No search providers are properly configured. "
                "Please set up at least one provider with required credentials."
            )

        logger.info(
            "Configuration loaded successfully",
            enabled_providers=[p.value for p in enabled_providers],
            default_provider=config.server.default_provider.value,
        )

        return config

    except Exception as e:
        logger.error("Failed to load configuration", error=str(e))
        raise


def get_environment_info() -> dict[str, Any]:
    """
    Get information about the current environment configuration.

    Returns:
        Dictionary with environment information (without sensitive data)
    """
    return {
        "server_name": os.getenv("WEB_SEARCH_SERVER_NAME", "web-search-mcp"),
        "default_provider": os.getenv("WEB_SEARCH_DEFAULT_PROVIDER", "google"),
        "google_configured": bool(
            os.getenv("GOOGLE_SEARCH_API_KEY") and os.getenv("GOOGLE_CSE_ID")
        ),
        "bing_configured": bool(os.getenv("BING_SEARCH_API_KEY")),
        "serpapi_configured": bool(os.getenv("SERPAPI_API_KEY")),
        "serper_configured": bool(os.getenv("SERPER_API_KEY")),
        "serply_configured": bool(os.getenv("SERPLY_API_KEY")),
        "searxng_configured": bool(os.getenv("SEARXNG_BASE_URL")),
        "tavily_configured": bool(os.getenv("TAVILY_API_KEY")),
        "duckduckgo_configured": True,  # Always available
    }
