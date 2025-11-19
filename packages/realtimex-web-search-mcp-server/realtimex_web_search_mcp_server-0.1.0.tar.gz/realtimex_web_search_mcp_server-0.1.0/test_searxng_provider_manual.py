#!/usr/bin/env python3
"""
Manual test script for SearXNG Search provider.

This script tests the SearXNG Search provider implementation
to ensure it works correctly with a SearXNG instance.

Usage:
    export SEARXNG_BASE_URL="https://your-searxng-instance.com"
    python test_searxng_provider_manual.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from web_search_mcp.config import ProviderConfig
from web_search_mcp.models import SearchProvider, SearchType
from web_search_mcp.providers.searxng import SearXNGProvider


async def test_searxng_provider():
    """Test the SearXNG Search provider."""

    # Check for required environment variables
    base_url = os.getenv("SEARXNG_BASE_URL")

    if not base_url:
        print("❌ SEARXNG_BASE_URL environment variable not set")
        print("Please set your SearXNG instance URL:")
        print("export SEARXNG_BASE_URL='https://your-searxng-instance.com'")
        print("\nYou can use public instances like:")
        print("- https://searx.be")
        print("- https://search.sapti.me")
        print("- https://searx.tiekoetter.com")
        return False

    print("🔍 Testing SearXNG Search Provider")
    print(f"Base URL: {base_url}")
    print()

    # Create provider configuration
    config = ProviderConfig(enabled=True, base_url=base_url)

    # Initialize provider
    try:
        provider = SearXNGProvider(SearchProvider.SEARXNG, config)
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return False

    try:
        await provider.initialize()
        print("✅ Provider initialized successfully")

        # Test web search
        print("\n📝 Testing web search...")
        query = "python programming tutorial"
        results = await provider.search(
            query=query, max_results=5, search_type=SearchType.SEARCH
        )

        if results.success:
            print(f"✅ Web search successful: {results.results_returned} results")
            print(f"⏱️  Search time: {results.search_time:.2f}s")

            for i, result in enumerate(results.results[:3], 1):
                print(f"\n{i}. {result.title}")
                print(f"   URL: {result.url}")
                print(f"   Source: {result.source}")
                print(f"   Date: {result.date or 'N/A'}")
                print(f"   Snippet: {result.snippet[:100]}...")
                if result.metadata.get("result_type"):
                    print(f"   Type: {result.metadata['result_type']}")
                if result.metadata.get("engine"):
                    print(f"   Engine: {result.metadata['engine']}")
                if result.metadata.get("score"):
                    print(f"   Score: {result.metadata['score']}")
        else:
            print(f"❌ Web search failed: {results.error}")
            return False

        # Test news search
        print("\n📰 Testing news search...")
        news_query = "artificial intelligence news"
        news_results = await provider.search(
            query=news_query, max_results=3, search_type=SearchType.NEWS
        )

        if news_results.success:
            print(f"✅ News search successful: {news_results.results_returned} results")
            print(f"⏱️  Search time: {news_results.search_time:.2f}s")

            for i, result in enumerate(news_results.results[:2], 1):
                print(f"\n{i}. {result.title}")
                print(f"   URL: {result.url}")
                print(f"   Source: {result.source}")
                print(f"   Date: {result.date or 'N/A'}")
                print(f"   Snippet: {result.snippet[:100]}...")
                if result.metadata.get("engine"):
                    print(f"   Engine: {result.metadata['engine']}")
                if result.thumbnail:
                    print(f"   Thumbnail: {result.thumbnail}")
        else:
            print(f"❌ News search failed: {news_results.error}")
            return False

        # Test search with additional parameters
        print("\n🔧 Testing search with additional parameters...")
        advanced_results = await provider.search(
            query="machine learning",
            max_results=3,
            search_type=SearchType.SEARCH,
            language="en",
            safe_search="moderate",
            engines=["google", "bing"],
        )

        if advanced_results.success:
            print(
                f"✅ Advanced search successful: {advanced_results.results_returned} results"
            )
            print(f"⏱️  Search time: {advanced_results.search_time:.2f}s")

            for i, result in enumerate(advanced_results.results[:2], 1):
                print(f"\n{i}. {result.title}")
                print(f"   URL: {result.url}")
                print(f"   Source: {result.source}")
                if result.metadata.get("result_type"):
                    print(f"   Type: {result.metadata['result_type']}")
                if result.metadata.get("engine"):
                    print(f"   Engine: {result.metadata['engine']}")
        else:
            print(f"❌ Advanced search failed: {advanced_results.error}")
            return False

        # Test search with time range
        print("\n⏰ Testing search with time range...")
        time_range_results = await provider.search(
            query="technology news",
            max_results=2,
            search_type=SearchType.NEWS,
            time_range="week",
        )

        if time_range_results.success:
            print(
                f"✅ Time range search successful: {time_range_results.results_returned} results"
            )
            print(f"⏱️  Search time: {time_range_results.search_time:.2f}s")

            for i, result in enumerate(time_range_results.results, 1):
                print(f"\n{i}. {result.title}")
                print(f"   URL: {result.url}")
                print(f"   Date: {result.date or 'N/A'}")
                if result.metadata.get("engine"):
                    print(f"   Engine: {result.metadata['engine']}")
        else:
            print(f"❌ Time range search failed: {time_range_results.error}")
            return False

        # Test image search
        print("\n🖼️  Testing image search...")
        image_results = await provider.search(
            query="python logo",
            max_results=2,
            search_type=SearchType.SEARCH,
            image_search=True,
        )

        if image_results.success:
            print(
                f"✅ Image search successful: {image_results.results_returned} results"
            )
            print(f"⏱️  Search time: {image_results.search_time:.2f}s")

            for i, result in enumerate(image_results.results, 1):
                print(f"\n{i}. {result.title}")
                print(f"   URL: {result.url}")
                if result.thumbnail:
                    print(f"   Thumbnail: {result.thumbnail}")
                if result.metadata.get("engine"):
                    print(f"   Engine: {result.metadata['engine']}")
        else:
            print(f"❌ Image search failed: {image_results.error}")
            return False

        print("\n🎉 All tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

    finally:
        await provider.close()
        print("🔒 Provider closed")


if __name__ == "__main__":
    success = asyncio.run(test_searxng_provider())
    sys.exit(0 if success else 1)
