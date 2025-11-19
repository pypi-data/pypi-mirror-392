#!/usr/bin/env python3
"""
Manual test script for DuckDuckGo search provider.

This script allows you to test the DuckDuckGo implementation manually
without running the full MCP server.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv

from web_search_mcp.config import ProviderConfig
from web_search_mcp.models import SearchProvider, SearchType
from web_search_mcp.providers.duckduckgo import DuckDuckGoProvider

load_dotenv()


async def test_duckduckgo_search():
    """Test DuckDuckGo search functionality."""
    print("🦆 Testing DuckDuckGo Search Provider")
    print("=" * 50)

    # Create provider configuration
    config = ProviderConfig(
        enabled=True,
        timeout=30,
        max_retries=3,
    )

    # Create provider instance
    provider = DuckDuckGoProvider(SearchProvider.DUCKDUCKGO, config)

    try:
        # Initialize provider
        print("Initializing DuckDuckGo provider...")
        await provider.initialize()
        print("✅ Provider initialized successfully")

        # Test queries
        test_queries = [
            ("python programming", SearchType.SEARCH, 5),
            ("artificial intelligence", SearchType.SEARCH, 3),
            ("latest tech news", SearchType.NEWS, 3),
        ]

        for query, search_type, max_results in test_queries:
            print(
                f"\n🔍 Searching for: '{query}' (type: {search_type.value}, max: {max_results})"
            )
            print("-" * 40)

            # Perform search
            result = await provider.search(
                query=query,
                max_results=max_results,
                search_type=search_type,
            )

            # Display results
            print(f"Success: {result.success}")
            print(f"Provider: {result.provider.value}")
            print(f"Results returned: {result.results_returned}")
            print(f"Search time: {result.search_time:.2f}s")

            if result.success and result.results:
                print("\nResults:")
                for i, search_result in enumerate(result.results, 1):
                    print(f"  {i}. {search_result.title}")
                    print(f"     URL: {search_result.url}")
                    print(f"     Source: {search_result.source}")
                    print(f"     Snippet: {search_result.snippet[:100]}...")
                    print()
            elif result.error:
                print(f"❌ Error: {result.error}")
                print(f"Error type: {result.error_type}")

            # Add delay between searches to be respectful
            await asyncio.sleep(2)

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Clean up
        print("\nCleaning up...")
        await provider.close()
        print("✅ Provider closed successfully")


async def test_tavily_search():
    """Test Tavily search functionality."""
    print("\n🔍 Testing Tavily Search Provider")
    print("=" * 50)

    import os

    from web_search_mcp.providers.tavily import TavilyProvider

    # Check if API key is available
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        print("⚠️  TAVILY_API_KEY environment variable not set. Skipping Tavily tests.")
        return

    # Create provider configuration
    config = ProviderConfig(
        enabled=True,
        api_key=api_key,
        timeout=30,
        max_retries=3,
    )

    # Create provider instance
    provider = TavilyProvider(SearchProvider.TAVILY, config)

    try:
        # Initialize provider
        print("Initializing Tavily provider...")
        await provider.initialize()
        print("✅ Tavily provider initialized successfully")

        # Test queries
        test_queries = [
            ("artificial intelligence", SearchType.SEARCH, 3),
            # ("machine learning tutorials", SearchType.SEARCH, 5),
            # ("latest tech news", SearchType.NEWS, 3),
        ]

        for query, search_type, max_results in test_queries:
            print(
                f"\n🔍 Searching for: '{query}' (type: {search_type.value}, max: {max_results})"
            )
            print("-" * 40)

            # Perform search
            result = await provider.search(
                query=query,
                max_results=max_results,
                search_type=search_type,
            )

            # Display results
            print(f"Success: {result.success}")
            print(f"Provider: {result.provider.value}")
            print(f"Results returned: {result.results_returned}")
            print(f"Search time: {result.search_time:.2f}s")

            if result.success and result.results:
                print("\nResults (sorted by relevance):")
                for i, search_result in enumerate(result.results, 1):
                    score = search_result.metadata.get("relevance_score", "N/A")
                    print(f"  {i}. {search_result.title} (Score: {score})")
                    print(f"     URL: {search_result.url}")
                    print(f"     Source: {search_result.source}")
                    print(f"     Snippet: {search_result.snippet[:100]}...")
                    print()
            elif result.error:
                print(f"❌ Error: {result.error}")
                print(f"Error type: {result.error_type}")

            # Add delay between searches to be respectful
            await asyncio.sleep(2)

    except Exception as e:
        print(f"❌ Tavily test failed with error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Clean up
        print("\nCleaning up Tavily provider...")
        await provider.close()
        print("✅ Tavily provider closed successfully")


async def test_serper_search():
    """Test Serper search functionality."""
    print("\n🔍 Testing Serper Search Provider")
    print("=" * 50)

    import os

    from web_search_mcp.providers.serper import SerperProvider

    # Check if API key is available
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        print("⚠️  SERPER_API_KEY environment variable not set. Skipping Serper tests.")
        return

    # Create provider configuration
    config = ProviderConfig(
        enabled=True,
        api_key=api_key,
        timeout=30,
        max_retries=3,
    )

    # Create provider instance
    provider = SerperProvider(SearchProvider.SERPER, config)

    try:
        # Initialize provider
        print("Initializing Serper provider...")
        await provider.initialize()
        print("✅ Serper provider initialized successfully")

        # Test queries
        test_queries = [
            ("python programming", SearchType.SEARCH, 5),
            ("artificial intelligence trends", SearchType.SEARCH, 3),
            ("technology news today", SearchType.NEWS, 4),
        ]

        for query, search_type, max_results in test_queries:
            print(
                f"\n🔍 Searching for: '{query}' (type: {search_type.value}, max: {max_results})"
            )
            print("-" * 40)

            # Perform search
            result = await provider.search(
                query=query,
                max_results=max_results,
                search_type=search_type,
            )

            # Display results
            print(f"Success: {result.success}")
            print(f"Provider: {result.provider.value}")
            print(f"Results returned: {result.results_returned}")
            print(f"Search time: {result.search_time:.2f}s")

            if result.success and result.results:
                print("\nResults (with special result types):")
                for i, search_result in enumerate(result.results, 1):
                    result_type = search_result.metadata.get("result_type", "organic")
                    type_indicator = ""
                    if result_type == "knowledge_graph":
                        type_indicator = " [Knowledge Graph]"
                    elif result_type == "answer_box":
                        type_indicator = " [Answer Box]"

                    print(f"  {i}. {search_result.title}{type_indicator}")
                    print(f"     URL: {search_result.url}")
                    print(f"     Source: {search_result.source}")
                    if search_result.date:
                        print(f"     Date: {search_result.date}")
                    print(f"     Snippet: {search_result.snippet[:100]}...")
                    print()
            elif result.error:
                print(f"❌ Error: {result.error}")
                print(f"Error type: {result.error_type}")

            # Add delay between searches to be respectful
            await asyncio.sleep(2)

    except Exception as e:
        print(f"❌ Serper test failed with error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Clean up
        print("\nCleaning up Serper provider...")
        await provider.close()
        print("✅ Serper provider closed successfully")


async def test_search_manager():
    """Test the SearchManager with multiple providers."""
    print("\n🔧 Testing SearchManager Integration")
    print("=" * 50)

    import os

    from web_search_mcp.config import ProviderConfig, ServerConfig, WebSearchConfig
    from web_search_mcp.search_manager import SearchManager

    # Create configuration
    server_config = ServerConfig(
        default_provider=SearchProvider.DUCKDUCKGO,
        default_max_results=3,
    )

    providers = {
        SearchProvider.DUCKDUCKGO: ProviderConfig(
            enabled=True,
            timeout=30,
            max_retries=3,
        )
    }

    # Add Tavily if API key is available
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if tavily_api_key:
        providers[SearchProvider.TAVILY] = ProviderConfig(
            enabled=True,
            api_key=tavily_api_key,
            timeout=30,
            max_retries=3,
        )
        print("✅ Tavily API key found, will test Tavily provider")
    else:
        print("⚠️  No Tavily API key found")

    # Add Serper if API key is available
    serper_api_key = os.getenv("SERPER_API_KEY")
    if serper_api_key:
        providers[SearchProvider.SERPER] = ProviderConfig(
            enabled=True,
            api_key=serper_api_key,
            timeout=30,
            max_retries=3,
        )
        print("✅ Serper API key found, will test Serper provider")
    else:
        print("⚠️  No Serper API key found")

    if len(providers) == 1:
        print("⚠️  Only DuckDuckGo will be tested (no API keys found)")

    config = WebSearchConfig(server=server_config, providers=providers)

    # Create search manager
    search_manager = SearchManager(config)

    try:
        # Initialize search manager
        print("Initializing SearchManager...")
        await search_manager.initialize()
        print("✅ SearchManager initialized successfully")

        # Test available providers
        available_providers = list(search_manager.providers.keys())
        print(f"Available providers: {[p.value for p in available_providers]}")

        # Test each available provider
        for provider in available_providers:
            query = f"machine learning {provider.value}"
            print(f"\n🔍 Testing {provider.value} with query: '{query}'")
            print("-" * 40)

            result = await search_manager.search(
                query=query,
                provider=provider,
                max_results=3,
                search_type=SearchType.SEARCH,
            )

            # Display results
            print(f"Success: {result.success}")
            print(f"Provider: {result.provider.value}")
            print(f"Results returned: {result.results_returned}")
            print(f"Search time: {result.search_time:.2f}s")

            if result.success and result.results:
                print("\nResults:")
                for i, search_result in enumerate(result.results, 1):
                    score = search_result.metadata.get("relevance_score")
                    score_text = f" (Score: {score})" if score else ""
                    print(f"  {i}. {search_result.title}{score_text}")
                    print(f"     URL: {search_result.url}")
                    print(f"     Snippet: {search_result.snippet[:80]}...")
            elif result.error:
                print(f"❌ Error: {result.error}")

            # Add delay between provider tests
            await asyncio.sleep(1)

        # Test fallback functionality if multiple providers available
        if len(available_providers) > 1:
            print("\n🔄 Testing fallback functionality")
            print("-" * 40)

            fallback_result = await search_manager.search_with_fallback(
                query="artificial intelligence",
                primary_provider=available_providers[0],
                fallback_providers=available_providers[1:],
                max_results=3,
            )

            print(f"Fallback test - Success: {fallback_result['success']}")
            print(f"Provider used: {fallback_result['provider']}")
            print(f"Fallback used: {fallback_result['fallback_used']}")
            print(f"Providers tried: {fallback_result['providers_tried']}")

    except Exception as e:
        print(f"❌ SearchManager test failed: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Clean up
        print("\nCleaning up SearchManager...")
        await search_manager.close()
        print("✅ SearchManager closed successfully")


async def main():
    """Run all tests."""
    print("🚀 Starting Web Search Provider Tests")
    print("=" * 60)

    try:
        # Test DuckDuckGo provider directly
        # await test_duckduckgo_search()

        # Test Tavily provider directly (if API key available)
        await test_tavily_search()

        exit(0)

        # Test Serper provider directly (if API key available)
        await test_serper_search()

        # Test through SearchManager with all available providers
        await test_search_manager()

        print("\n🎉 All tests completed!")

    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Tests failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Configure basic logging
    import logging

    logging.basicConfig(level=logging.INFO)

    # Run tests
    asyncio.run(main())
