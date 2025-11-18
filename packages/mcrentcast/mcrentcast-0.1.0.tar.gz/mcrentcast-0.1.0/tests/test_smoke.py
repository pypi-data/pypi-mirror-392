"""Smoke tests for mcrentcast MCP server using FastMCP testing patterns.

These tests verify basic functionality using the recommended FastMCP Client approach.
Full test suite refactoring is tracked in GitHub issues.

Reference: https://gofastmcp.com/patterns/testing
"""

import pytest
import pytest_asyncio
from fastmcp import Client
from fastmcp.client.transports import FastMCPTransport

from mcrentcast.server import app


@pytest_asyncio.fixture
async def mcp_client():
    """Create FastMCP test client."""
    async with Client(app) as client:
        yield client


@pytest.mark.asyncio
async def test_server_ping(mcp_client: Client[FastMCPTransport]):
    """Test server responds to ping."""
    result = await mcp_client.ping()
    assert result is not None


@pytest.mark.asyncio
async def test_list_tools(mcp_client: Client[FastMCPTransport]):
    """Test server lists all available tools."""
    tools = await mcp_client.list_tools()

    # Verify expected tools exist
    tool_names = {tool.name for tool in tools}
    expected_tools = {
        "set_api_key",
        "search_properties",
        "get_property",
        "get_value_estimate",
        "get_rent_estimate",
        "search_sale_listings",
        "search_rental_listings",
        "get_market_statistics",
        "expire_cache",
        "set_api_limits",
    }

    assert expected_tools.issubset(tool_names), f"Missing tools: {expected_tools - tool_names}"
    assert len(tools) >= 10, f"Expected at least 10 tools, got {len(tools)}"


@pytest.mark.asyncio
async def test_set_api_key(mcp_client: Client[FastMCPTransport]):
    """Test setting API key."""
    result = await mcp_client.call_tool(
        name="set_api_key",
        arguments={"api_key": "test_key_12345"}
    )

    assert result.data is not None
    assert "success" in result.data
    assert result.data["success"] is True


@pytest.mark.asyncio
async def test_search_properties_requires_api_key(mcp_client: Client[FastMCPTransport]):
    """Test search_properties validates API key is set."""
    # This should fail gracefully without a valid API key
    result = await mcp_client.call_tool(
        name="search_properties",
        arguments={
            "address": "123 Test St",
            "city": "Testville",
            "state": "CA",
            "limit": 5
        }
    )

    # Even without API key, should return structured response
    assert result.data is not None


@pytest.mark.asyncio
async def test_expire_cache(mcp_client: Client[FastMCPTransport]):
    """Test cache expiration tool."""
    result = await mcp_client.call_tool(
        name="expire_cache",
        arguments={
            "all": True
        }
    )

    assert result.data is not None
    assert "success" in result.data


@pytest.mark.asyncio
async def test_set_api_limits(mcp_client: Client[FastMCPTransport]):
    """Test setting API rate limits."""
    result = await mcp_client.call_tool(
        name="set_api_limits",
        arguments={
            "daily_limit": 100,
            "monthly_limit": 500,
            "requests_per_minute": 5
        }
    )

    assert result.data is not None
    assert "success" in result.data
