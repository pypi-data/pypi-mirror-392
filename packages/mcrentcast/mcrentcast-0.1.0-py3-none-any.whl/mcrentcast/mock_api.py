"""Mock Rentcast API server for testing."""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal

from fastapi import FastAPI, HTTPException, Header, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import structlog

logger = structlog.get_logger()

# Create FastAPI app for mock server
mock_app = FastAPI(title="Mock Rentcast API", version="1.0.0")

# Static test API keys
TEST_API_KEYS = {
    "test_key_free_tier": {"tier": "free", "daily_limit": 50, "monthly_limit": 50},
    "test_key_basic": {"tier": "basic", "daily_limit": 100, "monthly_limit": 1000},
    "test_key_pro": {"tier": "pro", "daily_limit": 1000, "monthly_limit": 10000},
    "test_key_enterprise": {"tier": "enterprise", "daily_limit": 10000, "monthly_limit": 100000},
    "test_key_rate_limited": {"tier": "test", "daily_limit": 1, "monthly_limit": 1},
    "test_key_invalid": {"tier": "invalid", "daily_limit": 0, "monthly_limit": 0},
}

# Track API usage for rate limiting simulation
api_usage: Dict[str, Dict[str, int]] = {}

# Test data generators
def generate_property_record(index: int = 0, city: str = "Austin", state: str = "TX") -> Dict[str, Any]:
    """Generate a mock property record."""
    streets = ["Main St", "Oak Ave", "Park Blvd", "Elm Dr", "First St", "Second Ave", "Lake Rd", "Hill Dr"]
    property_types = ["Single Family", "Condo", "Townhouse", "Multi Family"]
    
    return {
        "id": f"prop_{index:06d}",
        "address": f"{100 + index} {random.choice(streets)}",
        "city": city,
        "state": state,
        "zipCode": f"{78700 + (index % 100):05d}",
        "county": f"{city} County",
        "propertyType": random.choice(property_types),
        "bedrooms": random.randint(1, 5),
        "bathrooms": random.choice([1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]),
        "squareFootage": random.randint(800, 4000),
        "lotSize": round(random.uniform(0.1, 2.0), 2),
        "yearBuilt": random.randint(1950, 2023),
        "lastSaleDate": f"{random.randint(2010, 2023)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
        "lastSalePrice": random.randint(150000, 1500000),
        "taxAssessments": [
            {
                "year": 2023,
                "land": random.randint(50000, 200000),
                "improvements": random.randint(100000, 800000),
                "total": random.randint(150000, 1000000)
            }
        ],
        "owner": {
            "name": f"Owner {index}",
            "mailingAddress": f"{200 + index} Business Park",
            "mailingCity": city,
            "mailingState": state,
            "mailingZipCode": f"{78700 + (index % 100):05d}"
        },
        "features": {
            "cooling": "Central Air",
            "heating": "Forced Air",
            "parking": f"{random.randint(1, 3)} Car Garage",
            "pool": random.choice([True, False]),
            "fireplace": random.choice([True, False])
        }
    }


def generate_value_estimate(address: str) -> Dict[str, Any]:
    """Generate a mock value estimate."""
    base_price = random.randint(200000, 1000000)
    return {
        "address": address,
        "price": base_price,
        "priceRangeLow": int(base_price * 0.9),
        "priceRangeHigh": int(base_price * 1.1),
        "confidence": random.choice(["High", "Medium", "Low"]),
        "lastSaleDate": f"{random.randint(2015, 2023)}-{random.randint(1, 12):02d}-15",
        "lastSalePrice": int(base_price * random.uniform(0.8, 0.95)),
        "comparables": [
            {
                "address": f"{100 + i} Nearby St",
                "price": base_price + random.randint(-50000, 50000),
                "distance": round(random.uniform(0.1, 1.0), 2)
            }
            for i in range(3)
        ]
    }


def generate_rent_estimate(address: str) -> Dict[str, Any]:
    """Generate a mock rent estimate."""
    base_rent = random.randint(1500, 5000)
    return {
        "address": address,
        "rent": base_rent,
        "rentRangeLow": int(base_rent * 0.9),
        "rentRangeHigh": int(base_rent * 1.1),
        "confidence": random.choice(["High", "Medium", "Low"]),
        "comparables": [
            {
                "address": f"{200 + i} Rental Ave",
                "rent": base_rent + random.randint(-300, 300),
                "distance": round(random.uniform(0.1, 1.0), 2)
            }
            for i in range(3)
        ]
    }


def generate_sale_listing(index: int = 0, city: str = "Austin", state: str = "TX") -> Dict[str, Any]:
    """Generate a mock sale listing."""
    return {
        "id": f"sale_{index:06d}",
        "address": f"{300 + index} Market St",
        "city": city,
        "state": state,
        "zipCode": f"{78700 + (index % 100):05d}",
        "price": random.randint(250000, 1500000),
        "bedrooms": random.randint(2, 5),
        "bathrooms": random.choice([2.0, 2.5, 3.0, 3.5, 4.0]),
        "squareFootage": random.randint(1200, 4000),
        "propertyType": random.choice(["Single Family", "Condo", "Townhouse"]),
        "listingDate": f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
        "daysOnMarket": random.randint(1, 120),
        "photos": [f"https://example.com/photo{i}.jpg" for i in range(5)],
        "description": f"Beautiful {random.choice(['modern', 'updated', 'spacious'])} home in {city}"
    }


def generate_rental_listing(index: int = 0, city: str = "Austin", state: str = "TX") -> Dict[str, Any]:
    """Generate a mock rental listing."""
    return {
        "id": f"rental_{index:06d}",
        "address": f"{400 + index} Rental Rd",
        "city": city,
        "state": state,
        "zipCode": f"{78700 + (index % 100):05d}",
        "rent": random.randint(1200, 4000),
        "bedrooms": random.randint(1, 4),
        "bathrooms": random.choice([1.0, 1.5, 2.0, 2.5, 3.0]),
        "squareFootage": random.randint(700, 2500),
        "propertyType": random.choice(["Apartment", "Single Family", "Condo", "Townhouse"]),
        "availableDate": f"2024-{random.randint(1, 12):02d}-01",
        "pets": random.choice(["Cats OK", "Dogs OK", "No Pets", "Cats and Dogs OK"]),
        "photos": [f"https://example.com/rental{i}.jpg" for i in range(3)],
        "description": f"Charming {random.choice(['cozy', 'spacious', 'modern'])} rental in {city}"
    }


def generate_market_statistics(city: Optional[str] = None, state: Optional[str] = None, 
                              zipCode: Optional[str] = None) -> Dict[str, Any]:
    """Generate mock market statistics."""
    return {
        "city": city or "Austin",
        "state": state or "TX",
        "zipCode": zipCode,
        "medianSalePrice": random.randint(300000, 800000),
        "medianRent": random.randint(1500, 3500),
        "averageDaysOnMarket": random.randint(15, 60),
        "inventoryCount": random.randint(100, 1000),
        "pricePerSquareFoot": round(random.uniform(150, 400), 2),
        "rentPerSquareFoot": round(random.uniform(1.0, 3.0), 2),
        "appreciation": round(random.uniform(-5.0, 15.0), 2)
    }


def check_api_key(api_key: str) -> Dict[str, Any]:
    """Check if API key is valid and not rate limited."""
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    if api_key not in TEST_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    key_info = TEST_API_KEYS[api_key]
    
    # Check if this is the invalid test key
    if key_info["tier"] == "invalid":
        raise HTTPException(status_code=403, detail="API key has been suspended")
    
    # Track usage
    if api_key not in api_usage:
        api_usage[api_key] = {"daily": 0, "monthly": 0, "last_reset": datetime.now()}
    
    usage = api_usage[api_key]
    
    # Reset daily counter if needed
    if datetime.now() - usage["last_reset"] > timedelta(days=1):
        usage["daily"] = 0
        usage["last_reset"] = datetime.now()
    
    # Check rate limits
    if usage["daily"] >= key_info["daily_limit"]:
        raise HTTPException(
            status_code=429, 
            detail=f"Daily rate limit exceeded ({key_info['daily_limit']} requests)"
        )
    
    if usage["monthly"] >= key_info["monthly_limit"]:
        raise HTTPException(
            status_code=429,
            detail=f"Monthly rate limit exceeded ({key_info['monthly_limit']} requests)"
        )
    
    # Increment usage
    usage["daily"] += 1
    usage["monthly"] += 1
    
    return key_info


# API Endpoints

@mock_app.get("/v1/property-records")
async def get_property_records(
    x_api_key: str = Header(None, alias="X-Api-Key"),
    address: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    zipCode: Optional[str] = None,
    limit: int = Query(10, le=500),
    offset: int = Query(0, ge=0)
):
    """Get property records."""
    check_api_key(x_api_key)
    
    # Generate mock properties based on search criteria
    properties = []
    for i in range(offset, min(offset + limit, 500)):
        prop = generate_property_record(i, city or "Austin", state or "TX")
        
        # Filter by search criteria
        if address and address.lower() not in prop["address"].lower():
            continue
        if city and city.lower() != prop["city"].lower():
            continue
        if state and state.upper() != prop["state"].upper():
            continue
        if zipCode and zipCode != prop["zipCode"]:
            continue
            
        properties.append(prop)
        
        if len(properties) >= limit:
            break
    
    return {"properties": properties, "total": len(properties)}


@mock_app.get("/v1/property-records/random")
async def get_random_property_records(
    x_api_key: str = Header(None, alias="X-Api-Key"),
    limit: int = Query(10, le=500)
):
    """Get random property records."""
    check_api_key(x_api_key)
    
    properties = []
    for _ in range(limit):
        index = random.randint(0, 10000)
        city = random.choice(["Austin", "Dallas", "Houston", "San Antonio", "Phoenix", "Denver"])
        state = random.choice(["TX", "AZ", "CO", "CA", "FL"])
        properties.append(generate_property_record(index, city, state))
    
    return {"properties": properties}


@mock_app.get("/v1/property-record/{property_id}")
async def get_property_record(
    property_id: str,
    x_api_key: str = Header(None, alias="X-Api-Key")
):
    """Get specific property record."""
    check_api_key(x_api_key)
    
    # Extract index from property_id or use random
    try:
        index = int(property_id.split("_")[1])
    except:
        index = random.randint(0, 10000)
    
    property_data = generate_property_record(index)
    property_data["id"] = property_id
    
    return {"property": property_data}


@mock_app.get("/v1/value-estimate")
async def get_value_estimate(
    address: str,
    x_api_key: str = Header(None, alias="X-Api-Key")
):
    """Get property value estimate."""
    check_api_key(x_api_key)
    
    if not address:
        raise HTTPException(status_code=400, detail="Address is required")
    
    return generate_value_estimate(address)


@mock_app.get("/v1/rent-estimate-long-term")
async def get_rent_estimate(
    address: str,
    x_api_key: str = Header(None, alias="X-Api-Key"),
    propertyType: Optional[str] = None,
    bedrooms: Optional[int] = None,
    bathrooms: Optional[float] = None,
    squareFootage: Optional[int] = None
):
    """Get rent estimate."""
    check_api_key(x_api_key)
    
    if not address:
        raise HTTPException(status_code=400, detail="Address is required")
    
    estimate = generate_rent_estimate(address)
    
    # Adjust estimate based on provided details
    if bedrooms:
        estimate["rent"] += (bedrooms - 2) * 200
    if squareFootage:
        estimate["rent"] = int(estimate["rent"] * (squareFootage / 1500))
    
    return estimate


@mock_app.get("/v1/sale-listings")
async def get_sale_listings(
    x_api_key: str = Header(None, alias="X-Api-Key"),
    address: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    zipCode: Optional[str] = None,
    limit: int = Query(10, le=500),
    offset: int = Query(0, ge=0)
):
    """Get sale listings."""
    check_api_key(x_api_key)
    
    listings = []
    for i in range(offset, min(offset + limit, 500)):
        listing = generate_sale_listing(i, city or "Austin", state or "TX")
        
        # Filter by search criteria
        if city and city.lower() != listing["city"].lower():
            continue
        if state and state.upper() != listing["state"].upper():
            continue
        if zipCode and zipCode != listing["zipCode"]:
            continue
            
        listings.append(listing)
        
        if len(listings) >= limit:
            break
    
    return {"listings": listings, "total": len(listings)}


@mock_app.get("/v1/sale-listing/{listing_id}")
async def get_sale_listing(
    listing_id: str,
    x_api_key: str = Header(None, alias="X-Api-Key")
):
    """Get specific sale listing."""
    check_api_key(x_api_key)
    
    try:
        index = int(listing_id.split("_")[1])
    except:
        index = random.randint(0, 10000)
    
    listing = generate_sale_listing(index)
    listing["id"] = listing_id
    
    return {"listing": listing}


@mock_app.get("/v1/rental-listings-long-term")
async def get_rental_listings(
    x_api_key: str = Header(None, alias="X-Api-Key"),
    address: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    zipCode: Optional[str] = None,
    limit: int = Query(10, le=500),
    offset: int = Query(0, ge=0)
):
    """Get rental listings."""
    check_api_key(x_api_key)
    
    listings = []
    for i in range(offset, min(offset + limit, 500)):
        listing = generate_rental_listing(i, city or "Austin", state or "TX")
        
        # Filter by search criteria
        if city and city.lower() != listing["city"].lower():
            continue
        if state and state.upper() != listing["state"].upper():
            continue
        if zipCode and zipCode != listing["zipCode"]:
            continue
            
        listings.append(listing)
        
        if len(listings) >= limit:
            break
    
    return {"listings": listings, "total": len(listings)}


@mock_app.get("/v1/rental-listing-long-term/{listing_id}")
async def get_rental_listing(
    listing_id: str,
    x_api_key: str = Header(None, alias="X-Api-Key")
):
    """Get specific rental listing."""
    check_api_key(x_api_key)
    
    try:
        index = int(listing_id.split("_")[1])
    except:
        index = random.randint(0, 10000)
    
    listing = generate_rental_listing(index)
    listing["id"] = listing_id
    
    return {"listing": listing}


@mock_app.get("/v1/market-statistics")
async def get_market_statistics(
    x_api_key: str = Header(None, alias="X-Api-Key"),
    city: Optional[str] = None,
    state: Optional[str] = None,
    zipCode: Optional[str] = None
):
    """Get market statistics."""
    check_api_key(x_api_key)
    
    if not any([city, state, zipCode]):
        raise HTTPException(status_code=400, detail="At least one location parameter required")
    
    return generate_market_statistics(city, state, zipCode)


@mock_app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "mock-rentcast-api",
        "timestamp": datetime.now().isoformat()
    }


@mock_app.get("/test-keys")
async def get_test_keys():
    """Get list of available test API keys."""
    return {
        "test_keys": [
            {
                "key": key,
                "tier": info["tier"],
                "daily_limit": info["daily_limit"],
                "monthly_limit": info["monthly_limit"],
                "description": f"Test key for {info['tier']} tier"
            }
            for key, info in TEST_API_KEYS.items()
        ]
    }


def run_mock_server():
    """Run the mock Rentcast API server."""
    import uvicorn
    uvicorn.run(
        "mcrentcast.mock_api:mock_app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    run_mock_server()