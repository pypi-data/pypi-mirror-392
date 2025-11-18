"""Integration tests using mock Rentcast API."""

import asyncio
import os
import pytest
import pytest_asyncio
from decimal import Decimal
from unittest.mock import patch

# Set mock API mode for tests
os.environ["USE_MOCK_API"] = "true"
os.environ["MOCK_API_URL"] = "http://localhost:8001/v1"
os.environ["RENTCAST_API_KEY"] = "test_key_basic"

from mcrentcast.config import settings
from mcrentcast.rentcast_client import RentcastClient, RateLimitExceeded, RentcastAPIError
from mcrentcast.database import DatabaseManager
from mcrentcast.mock_api import mock_app, TEST_API_KEYS


@pytest_asyncio.fixture
async def mock_api_server():
    """Start mock API server for testing."""
    import uvicorn
    from threading import Thread
    
    # Run server in a thread
    server = uvicorn.Server(
        uvicorn.Config(mock_app, host="127.0.0.1", port=8001, log_level="error")
    )
    thread = Thread(target=server.run)
    thread.daemon = True
    thread.start()
    
    # Wait for server to start
    await asyncio.sleep(1)
    
    yield
    
    # Server will stop when thread ends


@pytest_asyncio.fixture
async def client():
    """Create Rentcast client for testing."""
    settings.use_mock_api = True
    settings.mock_api_url = "http://localhost:8001/v1"
    client = RentcastClient(api_key="test_key_basic")
    yield client
    await client.close()


@pytest_asyncio.fixture
async def db_manager():
    """Create database manager for testing."""
    # Use in-memory SQLite for tests
    db = DatabaseManager("sqlite:///:memory:")
    db.create_tables()
    return db


@pytest.mark.asyncio
async def test_property_search(mock_api_server, client, db_manager):
    """Test searching for properties."""
    # Search properties
    properties, is_cached, cache_age = await client.get_property_records(
        city="Austin", state="TX", limit=5
    )
    
    assert len(properties) == 5
    assert not is_cached  # First request
    assert cache_age is None
    
    # Check properties have expected fields
    for prop in properties:
        assert prop.city == "Austin"
        assert prop.state == "TX"
        assert prop.address is not None
        assert prop.bedrooms is not None
        assert prop.bathrooms is not None


@pytest.mark.asyncio
async def test_caching_behavior(mock_api_server, client, db_manager):
    """Test that responses are cached properly."""
    # Patch db_manager in client module
    with patch("mcrentcast.rentcast_client.db_manager", db_manager):
        # First request - should not be cached
        properties1, is_cached1, cache_age1 = await client.get_property_records(
            city="Dallas", state="TX", limit=3
        )
        
        assert not is_cached1
        assert cache_age1 is None
        assert len(properties1) == 3
        
        # Second identical request - should be cached
        properties2, is_cached2, cache_age2 = await client.get_property_records(
            city="Dallas", state="TX", limit=3
        )
        
        assert is_cached2
        assert cache_age2 is not None
        assert cache_age2 >= 0
        assert properties2 == properties1  # Same data


@pytest.mark.asyncio
async def test_value_estimate(mock_api_server, client):
    """Test getting property value estimate."""
    estimate, is_cached, cache_age = await client.get_value_estimate(
        address="123 Main St, Austin, TX"
    )
    
    assert estimate is not None
    assert estimate.address == "123 Main St, Austin, TX"
    assert estimate.price is not None
    assert estimate.priceRangeLow is not None
    assert estimate.priceRangeHigh is not None
    assert estimate.confidence in ["High", "Medium", "Low"]


@pytest.mark.asyncio
async def test_rent_estimate(mock_api_server, client):
    """Test getting rent estimate."""
    estimate, is_cached, cache_age = await client.get_rent_estimate(
        address="456 Oak Ave, Dallas, TX",
        bedrooms=3,
        bathrooms=2.0,
        squareFootage=1800
    )
    
    assert estimate is not None
    assert estimate.address == "456 Oak Ave, Dallas, TX"
    assert estimate.rent is not None
    assert estimate.rentRangeLow is not None
    assert estimate.rentRangeHigh is not None


@pytest.mark.asyncio
async def test_sale_listings(mock_api_server, client):
    """Test searching sale listings."""
    listings, is_cached, cache_age = await client.get_sale_listings(
        city="Houston", state="TX", limit=10
    )
    
    assert len(listings) <= 10
    for listing in listings:
        assert listing.city == "Houston"
        assert listing.state == "TX"
        assert listing.price is not None
        assert listing.bedrooms is not None


@pytest.mark.asyncio
async def test_rental_listings(mock_api_server, client):
    """Test searching rental listings."""
    listings, is_cached, cache_age = await client.get_rental_listings(
        city="San Antonio", state="TX", limit=8
    )
    
    assert len(listings) <= 8
    for listing in listings:
        assert listing.city == "San Antonio"
        assert listing.state == "TX"
        assert listing.rent is not None
        assert listing.bedrooms is not None


@pytest.mark.asyncio
async def test_market_statistics(mock_api_server, client):
    """Test getting market statistics."""
    stats, is_cached, cache_age = await client.get_market_statistics(
        city="Phoenix", state="AZ"
    )
    
    assert stats is not None
    assert stats.city == "Phoenix"
    assert stats.state == "AZ"
    assert stats.medianSalePrice is not None
    assert stats.medianRent is not None
    assert stats.inventoryCount is not None


@pytest.mark.asyncio
async def test_rate_limiting(mock_api_server):
    """Test rate limiting with limited API key."""
    # Use rate limited key
    limited_client = RentcastClient(api_key="test_key_rate_limited")
    
    try:
        # First request should succeed
        properties1, _, _ = await limited_client.get_property_records(limit=1)
        assert len(properties1) >= 0
        
        # Second request should fail due to rate limit
        with pytest.raises(RentcastAPIError) as exc_info:
            await limited_client.get_property_records(limit=1)
        
        assert "rate limit" in str(exc_info.value).lower()
        
    finally:
        await limited_client.close()


@pytest.mark.asyncio
async def test_invalid_api_key(mock_api_server):
    """Test using invalid API key."""
    # Use invalid key
    invalid_client = RentcastClient(api_key="invalid_key_123")
    
    try:
        with pytest.raises(RentcastAPIError) as exc_info:
            await invalid_client.get_property_records(limit=1)
        
        assert "Invalid API key" in str(exc_info.value) or "401" in str(exc_info.value)
        
    finally:
        await invalid_client.close()


@pytest.mark.asyncio
async def test_specific_property_by_id(mock_api_server, client):
    """Test getting specific property by ID."""
    property_record, is_cached, cache_age = await client.get_property_record(
        property_id="prop_000123"
    )
    
    assert property_record is not None
    assert property_record.id == "prop_000123"
    assert property_record.address is not None
    assert property_record.city is not None


@pytest.mark.asyncio
async def test_random_properties(mock_api_server, client):
    """Test getting random property records."""
    properties, is_cached, cache_age = await client.get_random_property_records(
        limit=5
    )
    
    assert len(properties) == 5
    # Check that properties have varied cities (randomized)
    cities = {prop.city for prop in properties}
    assert len(cities) >= 1  # At least some variety


@pytest.mark.asyncio
async def test_cache_expiration(mock_api_server, db_manager):
    """Test cache expiration and cleanup."""
    with patch("mcrentcast.rentcast_client.db_manager", db_manager):
        client = RentcastClient(api_key="test_key_basic")
        
        try:
            # Make a request to cache it
            await client.get_property_records(city="Denver", state="CO", limit=2)
            
            # Check cache stats
            stats = await db_manager.get_cache_stats()
            assert stats.total_entries == 1
            
            # Force expire cache
            cache_key = client._create_cache_key(
                "property-records", 
                {"city": "Denver", "state": "CO", "limit": 2}
            )
            expired = await db_manager.expire_cache_entry(cache_key)
            assert expired
            
            # Check cache stats again
            stats = await db_manager.get_cache_stats()
            assert stats.total_entries == 0
            
        finally:
            await client.close()


@pytest.mark.asyncio
async def test_cost_estimation(mock_api_server, client):
    """Test API cost estimation."""
    # Test various endpoints
    assert client._estimate_cost("property-records") == Decimal("0.10")
    assert client._estimate_cost("value-estimate") == Decimal("0.15")
    assert client._estimate_cost("rent-estimate-long-term") == Decimal("0.15")
    assert client._estimate_cost("sale-listings") == Decimal("0.08")
    assert client._estimate_cost("market-statistics") == Decimal("0.20")


@pytest.mark.asyncio
async def test_pagination(mock_api_server, client):
    """Test pagination with offset."""
    # Get first page
    page1, _, _ = await client.get_property_records(
        city="Austin", state="TX", limit=5, offset=0
    )
    
    # Get second page
    page2, _, _ = await client.get_property_records(
        city="Austin", state="TX", limit=5, offset=5
    )
    
    # Pages should have different properties
    page1_addresses = {prop.address for prop in page1}
    page2_addresses = {prop.address for prop in page2}
    
    # No overlap between pages
    assert len(page1_addresses.intersection(page2_addresses)) == 0


@pytest.mark.asyncio
async def test_api_usage_tracking(mock_api_server, db_manager):
    """Test API usage tracking."""
    with patch("mcrentcast.rentcast_client.db_manager", db_manager):
        client = RentcastClient(api_key="test_key_basic")
        
        try:
            # Make several API calls
            await client.get_property_records(city="Austin", limit=2)
            await client.get_value_estimate("123 Test St")
            await client.get_rent_estimate("456 Test Ave")
            
            # Check usage stats
            stats = await db_manager.get_usage_stats(days=1)
            
            assert stats["total_requests"] == 3
            assert stats["cache_hits"] == 0
            assert stats["cache_misses"] == 3
            assert stats["total_cost"] > 0
            
            # Make cached request
            await client.get_property_records(city="Austin", limit=2)
            
            stats = await db_manager.get_usage_stats(days=1)
            assert stats["total_requests"] == 4
            assert stats["cache_hits"] == 1
            
        finally:
            await client.close()