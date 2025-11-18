#!/usr/bin/env python3
"""Test script to verify mock API is working correctly."""

import asyncio
import httpx
import json
from typing import Dict, Any


async def test_mock_api(base_url: str = "http://localhost:8001"):
    """Test the mock Rentcast API endpoints."""
    
    print("🧪 Testing Mock Rentcast API")
    print("=" * 50)
    
    # Test API keys
    test_keys = {
        "valid": "test_key_basic",
        "rate_limited": "test_key_rate_limited",
        "invalid": "invalid_key_123"
    }
    
    async with httpx.AsyncClient() as client:
        # Test 1: Health check
        print("\n1. Testing health check...")
        response = await client.get(f"{base_url}/health")
        assert response.status_code == 200
        print("   ✅ Health check passed")
        
        # Test 2: Get test keys
        print("\n2. Getting available test keys...")
        response = await client.get(f"{base_url}/test-keys")
        assert response.status_code == 200
        keys_data = response.json()
        print(f"   ✅ Found {len(keys_data['test_keys'])} test keys:")
        for key_info in keys_data['test_keys']:
            print(f"      - {key_info['key']}: {key_info['description']}")
        
        # Test 3: Valid API request
        print("\n3. Testing valid API request...")
        headers = {"X-Api-Key": test_keys["valid"]}
        response = await client.get(
            f"{base_url}/v1/property-records",
            headers=headers,
            params={"city": "Austin", "state": "TX", "limit": 3}
        )
        assert response.status_code == 200
        data = response.json()
        print(f"   ✅ Retrieved {len(data['properties'])} properties")
        
        # Test 4: Value estimate
        print("\n4. Testing value estimate...")
        response = await client.get(
            f"{base_url}/v1/value-estimate",
            headers=headers,
            params={"address": "123 Test St, Austin, TX"}
        )
        assert response.status_code == 200
        estimate = response.json()
        print(f"   ✅ Value estimate: ${estimate['price']:,}")
        
        # Test 5: Rent estimate
        print("\n5. Testing rent estimate...")
        response = await client.get(
            f"{base_url}/v1/rent-estimate-long-term",
            headers=headers,
            params={
                "address": "456 Test Ave, Dallas, TX",
                "bedrooms": 3,
                "bathrooms": 2.0
            }
        )
        assert response.status_code == 200
        estimate = response.json()
        print(f"   ✅ Rent estimate: ${estimate['rent']:,}/month")
        
        # Test 6: Market statistics
        print("\n6. Testing market statistics...")
        response = await client.get(
            f"{base_url}/v1/market-statistics",
            headers=headers,
            params={"city": "Phoenix", "state": "AZ"}
        )
        assert response.status_code == 200
        stats = response.json()
        print(f"   ✅ Median sale price: ${stats['medianSalePrice']:,}")
        print(f"   ✅ Median rent: ${stats['medianRent']:,}")
        
        # Test 7: Invalid API key
        print("\n7. Testing invalid API key...")
        headers = {"X-Api-Key": test_keys["invalid"]}
        response = await client.get(
            f"{base_url}/v1/property-records",
            headers=headers,
            params={"limit": 1}
        )
        assert response.status_code == 401
        print("   ✅ Invalid key correctly rejected")
        
        # Test 8: Rate limiting
        print("\n8. Testing rate limiting...")
        headers = {"X-Api-Key": test_keys["rate_limited"]}
        
        # First request should succeed
        response = await client.get(
            f"{base_url}/v1/property-records",
            headers=headers,
            params={"limit": 1}
        )
        assert response.status_code == 200
        print("   ✅ First request succeeded")
        
        # Second request should be rate limited
        response = await client.get(
            f"{base_url}/v1/property-records",
            headers=headers,
            params={"limit": 1}
        )
        assert response.status_code == 429
        print("   ✅ Rate limiting working correctly")
        
        # Test 9: Specific property by ID
        print("\n9. Testing get property by ID...")
        headers = {"X-Api-Key": test_keys["valid"]}
        response = await client.get(
            f"{base_url}/v1/property-record/prop_000123",
            headers=headers
        )
        assert response.status_code == 200
        property_data = response.json()
        assert property_data["property"]["id"] == "prop_000123"
        print(f"   ✅ Retrieved property: {property_data['property']['address']}")
        
        # Test 10: Random properties
        print("\n10. Testing random properties...")
        response = await client.get(
            f"{base_url}/v1/property-records/random",
            headers=headers,
            params={"limit": 5}
        )
        assert response.status_code == 200
        data = response.json()
        cities = {prop["city"] for prop in data["properties"]}
        print(f"   ✅ Retrieved {len(data['properties'])} random properties")
        print(f"   ✅ Cities: {', '.join(cities)}")
    
    print("\n" + "=" * 50)
    print("✅ All tests passed successfully!")
    print("\n📝 Mock API is ready for use with these test keys:")
    print("   - test_key_free_tier (50 daily limit)")
    print("   - test_key_basic (100 daily limit)")
    print("   - test_key_pro (1000 daily limit)")
    print("   - test_key_enterprise (10000 daily limit)")
    print("   - test_key_rate_limited (1 daily limit - for testing)")


if __name__ == "__main__":
    try:
        asyncio.run(test_mock_api())
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
    except httpx.ConnectError:
        print("\n❌ Could not connect to mock API server")
        print("   Please ensure the mock API is running:")
        print("   make mock-api")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)