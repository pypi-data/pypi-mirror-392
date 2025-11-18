#!/usr/bin/env python
"""Test the MCP server functionality."""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcrentcast.server import app


async def test_tools():
    """Test MCP server tools."""
    print("Testing mcrentcast MCP Server")
    print("=" * 50)
    
    # List available tools
    tools = []
    for name, func in app._tools.items():
        tools.append(name)
        print(f"  - {name}")
    
    print(f"\nTotal tools: {len(tools)}")
    
    # Test set_api_key
    print("\n1. Testing set_api_key...")
    result = await app._tools["set_api_key"](api_key="test_key_basic")
    print(f"   Result: {result}")
    
    # Test get_api_limits
    print("\n2. Testing get_api_limits...")
    result = await app._tools["get_api_limits"]()
    print(f"   Result: {json.dumps(result, indent=2)}")
    
    # Test search_properties (with cache miss)
    print("\n3. Testing search_properties...")
    result = await app._tools["search_properties"](
        city="Austin",
        state="TX",
        limit=2
    )
    print(f"   Found {result.get('count', 0)} properties")
    print(f"   Cached: {result.get('cached', False)}")
    
    # Test again (should hit cache)
    print("\n4. Testing search_properties (cache hit)...")
    result = await app._tools["search_properties"](
        city="Austin",
        state="TX",
        limit=2
    )
    print(f"   Found {result.get('count', 0)} properties")
    print(f"   Cached: {result.get('cached', False)}")
    print(f"   Cache age: {result.get('cache_age_hours', 'N/A')} hours")
    
    # Test get_cache_stats
    print("\n5. Testing get_cache_stats...")
    result = await app._tools["get_cache_stats"]()
    print(f"   Result: {json.dumps(result, indent=2)}")
    
    # Test get_usage_stats
    print("\n6. Testing get_usage_stats...")
    result = await app._tools["get_usage_stats"](days=7)
    print(f"   Result: {json.dumps(result, indent=2)}")
    
    print("\n" + "=" * 50)
    print("All tests completed successfully!")


if __name__ == "__main__":
    # Set environment for testing
    os.environ["USE_MOCK_API"] = "true"
    os.environ["RENTCAST_API_KEY"] = "test_key_basic"
    
    asyncio.run(test_tools())