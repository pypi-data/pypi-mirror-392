#!/usr/bin/env python3
"""
Manual test script for Serply Search provider.

This script tests the Serply Search provider implementation
to ensure it works correctly with the Serply API.

Usage:
    export SERPLY_API_KEY="your-api-key"
    python test_serply_provider_manual.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from web_search_mcp.config import ProviderConfig
from web_search_mcp.models import SearchProvider, SearchType
from web_search_mcp.providers.serply import SerplyProvider


async def test_serply_provider():
    """Test the Serply Search provider."""

    # Check for required environment variables
    api_key = os.getenv("SERPLY_API_KEY")

    if not api_key:
        print("❌ SERPLY_API_KEY environment variable not set")
        print("Please set your Serply API key:")
        print("export SERPLY_API_KEY='your-api-key'")
        return False

    print("🔍 Testing Serply Search Provider")
    print(f"API Key: {api_key[:10]}..." if len(api_key) > 10 else api_key)
    print()

    # Create provider configuration
    config = ProviderConfig(enabled=True, api_key=api_key)

    # Initialize provider
    provider = SerplyProvider(SearchProvider.SERPLY, config)

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
                if result.metadata.get("serply_position"):
                    print(f"   Serply Position: {result.metadata['serply_position']}")
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
            country="us",
            safe_search="moderate",
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
        else:
            print(f"❌ Advanced search failed: {advanced_results.error}")
            return False

        # Test news search with time range
        print("\n⏰ Testing news search with time range...")
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
        else:
            print(f"❌ Time range search failed: {time_range_results.error}")
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
    success = asyncio.run(test_serply_provider())
    sys.exit(0 if success else 1)
