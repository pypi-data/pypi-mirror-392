#!/usr/bin/env python3
"""
Manual test script for Google Custom Search provider.

This script tests the Google Custom Search provider implementation
to ensure it works correctly with the Google Custom Search API.

Usage:
    export GOOGLE_SEARCH_API_KEY="your-api-key"
    export GOOGLE_CSE_ID="your-cse-id"
    python test_google_provider_manual.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv

from web_search_mcp.config import ProviderConfig
from web_search_mcp.models import SearchProvider, SearchType
from web_search_mcp.providers.google import GoogleProvider

load_dotenv()


async def test_google_provider():
    """Test the Google Custom Search provider."""

    # Check for required environment variables
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")

    if not api_key:
        print("❌ GOOGLE_SEARCH_API_KEY environment variable not set")
        print("Please set your Google Custom Search API key:")
        print("export GOOGLE_SEARCH_API_KEY='your-api-key'")
        return False

    if not cse_id:
        print("❌ GOOGLE_CSE_ID environment variable not set")
        print("Please set your Google Custom Search Engine ID:")
        print("export GOOGLE_CSE_ID='your-cse-id'")
        return False

    print("🔍 Testing Google Custom Search Provider")
    print(f"API Key: {api_key[:10]}..." if len(api_key) > 10 else api_key)
    print(f"CSE ID: {cse_id}")
    print()

    # Create provider configuration
    config = ProviderConfig(
        enabled=True, api_key=api_key, additional_config={"cse_id": cse_id}
    )

    # Initialize provider
    provider = GoogleProvider(SearchProvider.GOOGLE, config)

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
                print(f"   Snippet: {result.snippet[:100]}...")
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
        else:
            print(f"❌ News search failed: {news_results.error}")
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
    success = asyncio.run(test_google_provider())
    sys.exit(0 if success else 1)
