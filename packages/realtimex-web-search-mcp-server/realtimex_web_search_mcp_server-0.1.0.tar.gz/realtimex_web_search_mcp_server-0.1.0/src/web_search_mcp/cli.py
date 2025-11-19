"""
CLI interface for Web Search MCP Server.

Handles command-line argument parsing and server startup logic.
"""

import asyncio
import sys

import click
import structlog

from web_search_mcp.config import load_config
from web_search_mcp.server import WebSearchMCPServer

logger = structlog.get_logger(__name__)


@click.command()
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
    help="Logging level",
)
@click.option(
    "--provider",
    type=click.Choice(
        ["google", "bing", "duckduckgo", "serpapi", "serply", "searxng", "tavily"],
        case_sensitive=False,
    ),
    help="Override default search provider",
)
def main(log_level: str, provider: str | None) -> None:
    """Start the Web Search MCP Server."""
    try:
        # Configure logging
        _configure_logging(log_level)

        # Run the server
        asyncio.run(run_server(provider))

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error("Server failed to start", error=str(e))
        sys.exit(1)


async def run_server(override_provider: str | None = None) -> None:
    """Run the MCP server with the given configuration."""
    # Load configuration
    config = load_config()

    # Override default provider if specified
    if override_provider:
        from .models import SearchProvider

        try:
            config.server.default_provider = SearchProvider(override_provider.lower())
            logger.info("Default provider overridden", provider=override_provider)
        except ValueError:
            logger.warning(
                "Invalid provider specified, using configured default",
                invalid_provider=override_provider,
                default_provider=config.server.default_provider.value,
            )

    # Create and start server
    server = WebSearchMCPServer(config)
    await server.start()


def _configure_logging(log_level: str) -> None:
    """Pure JSON logging with stable key order."""
    import json
    import logging
    import sys
    from collections import OrderedDict
    from functools import partial

    import structlog

    level = getattr(logging, log_level.upper(), logging.INFO)

    # JSON serializer that accepts extra kwargs (e.g., default=)
    json_dumps = partial(
        json.dumps,
        ensure_ascii=False,
        separators=(", ", ": "),  # compact
        sort_keys=False,  # change to True if you prefer pure alphabetical
    )

    PRIORITY_KEYS = ("timestamp", "level", "logger", "event")

    def reorder_keys(_, __, event_dict):
        # Put important keys first; sort the rest for stability
        out = OrderedDict()
        for k in PRIORITY_KEYS:
            if k in event_dict:
                out[k] = event_dict.pop(k)
        for k in sorted(event_dict):
            out[k] = event_dict[k]
        return out

    # stdlib handler -> ProcessorFormatter -> JSON
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=[
                structlog.contextvars.merge_contextvars,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.processors.TimeStamper(key="timestamp", fmt="iso", utc=True),
                reorder_keys,
            ],
            processor=structlog.processors.JSONRenderer(serializer=json_dumps),
        )
    )
    logging.basicConfig(level=level, handlers=[handler], force=True)

    # structlog -> wrap_for_formatter -> ProcessorFormatter above
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(key="timestamp", fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            reorder_keys,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


if __name__ == "__main__":
    main()
