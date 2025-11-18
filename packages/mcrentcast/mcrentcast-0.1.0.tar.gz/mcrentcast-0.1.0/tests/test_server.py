"""Basic tests for mcrentcast MCP server.

NOTE: These tests use outdated testing patterns from before the FastMCP refactoring.
They are marked for skipping until they can be updated to use the FastMCP Client pattern.

See tests/test_smoke.py for working tests using the current FastMCP testing approach.
Reference: https://gofastmcp.com/patterns/testing
"""

import pytest

pytestmark = pytest.mark.skip(reason="Tests need updating for FastMCP Client pattern - see test_smoke.py")
from unittest.mock import AsyncMock, MagicMock, patch

from mcrentcast.server import (
    app,
    SetApiKeyRequest,
    PropertySearchRequest,
    ExpireCacheRequest,
)
from mcrentcast.models import PropertyRecord


@pytest.mark.asyncio
async def test_set_api_key():
    """Test setting API key."""
    request = SetApiKeyRequest(api_key="test_api_key_123")
    
    with patch("mcrentcast.server.db_manager") as mock_db:
        mock_db.set_config = AsyncMock()
        
        result = await app.tools["set_api_key"](request)
        
        assert result["success"] is True
        assert "successfully" in result["message"]
        mock_db.set_config.assert_called_once_with("rentcast_api_key", "test_api_key_123")


@pytest.mark.asyncio
async def test_search_properties_no_api_key():
    """Test searching properties without API key."""
    request = PropertySearchRequest(city="Austin", state="TX")
    
    with patch("mcrentcast.server.check_api_key", return_value=False):
        result = await app.tools["search_properties"](request)
        
        assert "error" in result
        assert "API key not configured" in result["error"]


@pytest.mark.asyncio
async def test_search_properties_cached():
    """Test searching properties with cached results."""
    request = PropertySearchRequest(city="Austin", state="TX")
    
    mock_property = PropertyRecord(
        id="123",
        address="123 Main St",
        city="Austin",
        state="TX",
        zipCode="78701"
    )
    
    with patch("mcrentcast.server.check_api_key", return_value=True), \
         patch("mcrentcast.server.get_rentcast_client") as mock_client_getter:
        
        mock_client = MagicMock()
        mock_client._create_cache_key.return_value = "test_cache_key"
        mock_client.get_property_records = AsyncMock(return_value=([mock_property], True, 12.5))
        mock_client_getter.return_value = mock_client
        
        with patch("mcrentcast.server.db_manager") as mock_db:
            mock_db.get_cache_entry = AsyncMock(return_value=MagicMock())
            
            result = await app.tools["search_properties"](request)
            
            assert result["success"] is True
            assert result["cached"] is True
            assert result["cache_age_hours"] == 12.5
            assert len(result["properties"]) == 1


@pytest.mark.asyncio
async def test_expire_cache():
    """Test expiring cache entries."""
    request = ExpireCacheRequest(cache_key="test_key")
    
    with patch("mcrentcast.server.db_manager") as mock_db:
        mock_db.expire_cache_entry = AsyncMock(return_value=True)
        
        result = await app.tools["expire_cache"](request)
        
        assert result["success"] is True
        assert "expired" in result["message"].lower()


@pytest.mark.asyncio
async def test_get_cache_stats():
    """Test getting cache statistics."""
    from mcrentcast.models import CacheStats
    
    mock_stats = CacheStats(
        total_entries=100,
        total_hits=80,
        total_misses=20,
        cache_size_mb=5.2,
        hit_rate=80.0
    )
    
    with patch("mcrentcast.server.db_manager") as mock_db:
        mock_db.get_cache_stats = AsyncMock(return_value=mock_stats)
        
        result = await app.tools["get_cache_stats"]()
        
        assert result["success"] is True
        assert result["stats"]["hit_rate"] == 80.0
        assert "80.0%" in result["message"]


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint."""
    from mcrentcast.server import health_check
    
    with patch("mcrentcast.server.settings") as mock_settings:
        mock_settings.validate_api_key.return_value = True
        mock_settings.mode = "development"
        
        result = await health_check()
        
        assert result["status"] == "healthy"
        assert result["api_key_configured"] is True
        assert result["mode"] == "development"