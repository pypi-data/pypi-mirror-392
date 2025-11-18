# API Reference - mcrentcast MCP Server

## Overview

The mcrentcast MCP server provides 13 tools for interacting with the Rentcast API. All tools support intelligent caching, rate limiting, and cost management.

## Authentication

### set_api_key

Configure or update the Rentcast API key for the session.

**Parameters:**
- `api_key` (string, required): Your Rentcast API key

**Example:**
```json
{
  "tool": "set_api_key",
  "parameters": {
    "api_key": "your_rentcast_api_key_here"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "API key updated successfully"
}
```

## Property Data Tools

### search_properties

Search for property records by location.

**Parameters:**
- `address` (string, optional): Property address
- `city` (string, optional): City name
- `state` (string, optional): State code (e.g., "TX", "CA")
- `zipCode` (string, optional): ZIP code
- `limit` (integer, optional): Maximum results (1-500, default: 10)
- `offset` (integer, optional): Results offset for pagination (default: 0)
- `force_refresh` (boolean, optional): Force cache refresh (default: false)

**Example:**
```json
{
  "tool": "search_properties",
  "parameters": {
    "city": "Austin",
    "state": "TX",
    "limit": 5
  }
}
```

**Response:**
```json
{
  "success": true,
  "properties": [
    {
      "id": "prop_000001",
      "address": "123 Main St",
      "city": "Austin",
      "state": "TX",
      "zipCode": "78701",
      "propertyType": "Single Family",
      "bedrooms": 3,
      "bathrooms": 2.0,
      "squareFootage": 1800,
      "yearBuilt": 2010,
      "lastSalePrice": 350000
    }
  ],
  "count": 5,
  "cached": false,
  "cache_age_hours": null,
  "message": "Found 5 properties (fresh data)"
}
```

### get_property

Get detailed information for a specific property by ID.

**Parameters:**
- `property_id` (string, required): Property ID from Rentcast
- `force_refresh` (boolean, optional): Force cache refresh (default: false)

**Example:**
```json
{
  "tool": "get_property",
  "parameters": {
    "property_id": "prop_000123"
  }
}
```

**Response:**
```json
{
  "success": true,
  "property": {
    "id": "prop_000123",
    "address": "456 Oak Ave",
    "city": "Dallas",
    "state": "TX",
    "owner": {
      "name": "John Doe",
      "mailingAddress": "789 Business Park"
    },
    "taxAssessments": [
      {
        "year": 2023,
        "total": 450000
      }
    ],
    "features": {
      "cooling": "Central Air",
      "heating": "Forced Air",
      "pool": true
    }
  },
  "cached": true,
  "cache_age_hours": 2.5,
  "message": "Property found (from cache, age: 2.5 hours)"
}
```

## Valuation Tools

### get_value_estimate

Get property value estimate for an address.

**Parameters:**
- `address` (string, required): Full property address
- `force_refresh` (boolean, optional): Force cache refresh (default: false)

**Example:**
```json
{
  "tool": "get_value_estimate",
  "parameters": {
    "address": "123 Main St, Austin, TX 78701"
  }
}
```

**Response:**
```json
{
  "success": true,
  "estimate": {
    "address": "123 Main St, Austin, TX 78701",
    "price": 425000,
    "priceRangeLow": 382500,
    "priceRangeHigh": 467500,
    "confidence": "High",
    "lastSaleDate": "2020-05-15",
    "lastSalePrice": 380000,
    "comparables": [
      {
        "address": "125 Main St",
        "price": 430000,
        "distance": 0.1
      }
    ]
  },
  "cached": false,
  "cache_age_hours": null,
  "message": "Value estimate: $425,000 (fresh data)"
}
```

### get_rent_estimate

Get rent estimate for a property.

**Parameters:**
- `address` (string, required): Full property address
- `propertyType` (string, optional): Property type (e.g., "Single Family", "Condo")
- `bedrooms` (integer, optional): Number of bedrooms
- `bathrooms` (float, optional): Number of bathrooms
- `squareFootage` (integer, optional): Square footage
- `force_refresh` (boolean, optional): Force cache refresh (default: false)

**Example:**
```json
{
  "tool": "get_rent_estimate",
  "parameters": {
    "address": "456 Oak Ave, Dallas, TX",
    "bedrooms": 3,
    "bathrooms": 2.0,
    "squareFootage": 1500
  }
}
```

**Response:**
```json
{
  "success": true,
  "estimate": {
    "address": "456 Oak Ave, Dallas, TX",
    "rent": 2500,
    "rentRangeLow": 2250,
    "rentRangeHigh": 2750,
    "confidence": "Medium",
    "comparables": [
      {
        "address": "458 Oak Ave",
        "rent": 2450,
        "distance": 0.05
      }
    ]
  },
  "cached": true,
  "cache_age_hours": 1.2,
  "message": "Rent estimate: $2,500/month (from cache, age: 1.2 hours)"
}
```

## Listing Tools

### search_sale_listings

Search for properties for sale.

**Parameters:**
- `address` (string, optional): Property address
- `city` (string, optional): City name
- `state` (string, optional): State code
- `zipCode` (string, optional): ZIP code
- `limit` (integer, optional): Maximum results (1-500, default: 10)
- `offset` (integer, optional): Results offset for pagination
- `force_refresh` (boolean, optional): Force cache refresh (default: false)

**Example:**
```json
{
  "tool": "search_sale_listings",
  "parameters": {
    "city": "Houston",
    "state": "TX",
    "limit": 10
  }
}
```

**Response:**
```json
{
  "success": true,
  "listings": [
    {
      "id": "sale_000001",
      "address": "789 Park Blvd",
      "city": "Houston",
      "state": "TX",
      "price": 550000,
      "bedrooms": 4,
      "bathrooms": 3.0,
      "squareFootage": 2400,
      "listingDate": "2024-01-15",
      "daysOnMarket": 45,
      "photos": ["url1", "url2"],
      "description": "Beautiful modern home"
    }
  ],
  "count": 10,
  "cached": false,
  "cache_age_hours": null,
  "message": "Found 10 sale listings (fresh data)"
}
```

### search_rental_listings

Search for rental properties.

**Parameters:**
- `address` (string, optional): Property address
- `city` (string, optional): City name
- `state` (string, optional): State code
- `zipCode` (string, optional): ZIP code
- `limit` (integer, optional): Maximum results (1-500, default: 10)
- `offset` (integer, optional): Results offset for pagination
- `force_refresh` (boolean, optional): Force cache refresh (default: false)

**Example:**
```json
{
  "tool": "search_rental_listings",
  "parameters": {
    "city": "San Antonio",
    "state": "TX",
    "limit": 5
  }
}
```

**Response:**
```json
{
  "success": true,
  "listings": [
    {
      "id": "rental_000001",
      "address": "321 Rental Rd",
      "city": "San Antonio",
      "state": "TX",
      "rent": 1800,
      "bedrooms": 2,
      "bathrooms": 2.0,
      "squareFootage": 1100,
      "availableDate": "2024-02-01",
      "pets": "Cats OK",
      "photos": ["url1", "url2"],
      "description": "Cozy apartment"
    }
  ],
  "count": 5,
  "cached": true,
  "cache_age_hours": 3.5,
  "message": "Found 5 rental listings (from cache, age: 3.5 hours)"
}
```

### get_market_statistics

Get market statistics for a location.

**Parameters:**
- `city` (string, optional): City name
- `state` (string, optional): State code
- `zipCode` (string, optional): ZIP code
- `force_refresh` (boolean, optional): Force cache refresh (default: false)

**Note:** At least one location parameter is required.

**Example:**
```json
{
  "tool": "get_market_statistics",
  "parameters": {
    "city": "Phoenix",
    "state": "AZ"
  }
}
```

**Response:**
```json
{
  "success": true,
  "statistics": {
    "city": "Phoenix",
    "state": "AZ",
    "medianSalePrice": 485000,
    "medianRent": 2200,
    "averageDaysOnMarket": 32,
    "inventoryCount": 1250,
    "pricePerSquareFoot": 285.50,
    "rentPerSquareFoot": 1.85,
    "appreciation": 6.5
  },
  "cached": false,
  "cache_age_hours": null,
  "message": "Market statistics retrieved (fresh data)"
}
```

## Cache Management Tools

### expire_cache

Expire cache entries to force fresh API calls.

**Parameters:**
- `cache_key` (string, optional): Specific cache key to expire
- `endpoint` (string, optional): Expire all cache for endpoint
- `all` (boolean, optional): Expire all cache entries (default: false)

**Example:**
```json
{
  "tool": "expire_cache",
  "parameters": {
    "all": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Expired 42 cache entries"
}
```

### get_cache_stats

Get cache statistics including hit/miss rates and storage usage.

**Parameters:** None

**Example:**
```json
{
  "tool": "get_cache_stats",
  "parameters": {}
}
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_entries": 156,
    "total_hits": 1247,
    "total_misses": 312,
    "cache_size_mb": 8.4,
    "oldest_entry": "2024-01-01T10:00:00Z",
    "newest_entry": "2024-01-15T14:30:00Z",
    "hit_rate": 80.0
  },
  "message": "Cache hit rate: 80.0%"
}
```

## Usage Analytics Tools

### get_usage_stats

Get API usage statistics including costs and endpoint breakdown.

**Parameters:**
- `days` (integer, optional): Number of days to include (default: 30)

**Example:**
```json
{
  "tool": "get_usage_stats",
  "parameters": {
    "days": 7
  }
}
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_requests": 234,
    "cache_hits": 187,
    "cache_misses": 47,
    "hit_rate": 79.9,
    "total_cost": 4.70,
    "by_endpoint": {
      "property-records": 89,
      "value-estimate": 45,
      "rent-estimate-long-term": 38,
      "market-statistics": 62
    },
    "days": 7
  },
  "message": "Usage stats for last 7 days"
}
```

## Configuration Tools

### set_api_limits

Update API rate limits and usage quotas.

**Parameters:**
- `daily_limit` (integer, optional): Daily API request limit
- `monthly_limit` (integer, optional): Monthly API request limit
- `requests_per_minute` (integer, optional): Requests per minute limit

**Example:**
```json
{
  "tool": "set_api_limits",
  "parameters": {
    "daily_limit": 200,
    "monthly_limit": 2000,
    "requests_per_minute": 5
  }
}
```

**Response:**
```json
{
  "success": true,
  "limits": {
    "daily_limit": 200,
    "monthly_limit": 2000,
    "requests_per_minute": 5
  },
  "message": "API limits updated"
}
```

### get_api_limits

Get current API rate limits and usage quotas.

**Parameters:** None

**Example:**
```json
{
  "tool": "get_api_limits",
  "parameters": {}
}
```

**Response:**
```json
{
  "success": true,
  "limits": {
    "daily_limit": 100,
    "monthly_limit": 1000,
    "requests_per_minute": 3,
    "current_daily_usage": 42,
    "current_monthly_usage": 567,
    "current_minute_usage": 1
  },
  "message": "Daily: 42/100, Monthly: 567/1000"
}
```

## Error Responses

All tools return consistent error responses:

### API Key Not Configured
```json
{
  "error": "API key not configured",
  "message": "Please set your Rentcast API key first using set_api_key tool"
}
```

### Rate Limit Exceeded
```json
{
  "error": "Rate limit exceeded",
  "message": "Daily rate limit exceeded (100 requests). Try again tomorrow.",
  "retry_after": "Please wait before making more requests"
}
```

### Confirmation Required
```json
{
  "confirmation_required": true,
  "message": "API call requires confirmation (estimated cost: $0.15)",
  "retry_with": "Please confirm to proceed with the API request"
}
```

### Invalid Parameters
```json
{
  "error": "Invalid parameters",
  "message": "At least one location parameter required"
}
```

### Internal Error
```json
{
  "error": "Internal error",
  "message": "An unexpected error occurred: [details]"
}
```

## Caching Behavior

### Cache Keys

Cache keys are generated based on:
- Endpoint name
- Request parameters (sorted)
- MD5 hash of the combination

### Cache Expiration

- Default TTL: 24 hours (configurable via `CACHE_TTL_HOURS`)
- Manual expiration available via `expire_cache` tool
- Automatic cleanup of expired entries

### Cache Indicators

All data-fetching tools return cache information:
- `cached`: Boolean indicating if response was from cache
- `cache_age_hours`: Age of cached data in hours (null if fresh)
- Message includes cache status

## Rate Limiting

### Limits

Configurable via environment variables or `set_api_limits` tool:
- Daily limit (default: 100)
- Monthly limit (default: 1000)
- Per-minute limit (default: 3)

### Enforcement

- Checked before each API call
- Returns 429-style error when exceeded
- Counters reset automatically

### Exponential Backoff

Failed requests automatically retry with exponential backoff:
- Base: 2.0 seconds
- Maximum: 300 seconds (5 minutes)
- Maximum attempts: 3

## Cost Management

### Cost Estimation

Approximate costs per endpoint:
- Property records: $0.10
- Property record (by ID): $0.05
- Value estimate: $0.15
- Rent estimate: $0.15
- Sale listings: $0.08
- Rental listings: $0.08
- Market statistics: $0.20

### Confirmation System

For non-cached requests:
1. Cost is estimated
2. User confirmation requested (if supported)
3. Request proceeds only after confirmation
4. Confirmations cached for 15 minutes

### Cost Tracking

- All API calls logged with cost estimates
- View total costs via `get_usage_stats`
- Cache hits have zero cost

## Best Practices

1. **Use Caching**: Let the cache work for you - avoid `force_refresh` unless necessary
2. **Batch Requests**: Group related searches to maximize cache efficiency
3. **Monitor Usage**: Regularly check `get_usage_stats` and `get_api_limits`
4. **Test with Mock**: Use mock API (`USE_MOCK_API=true`) for development
5. **Set Appropriate Limits**: Configure rate limits based on your API plan
6. **Handle Errors**: Implement proper error handling for rate limits and confirmations
7. **Optimize Searches**: Use specific parameters to improve cache hit rates