# mcrentcast Usage Guide

This guide provides comprehensive examples and best practices for using the mcrentcast MCP server with Claude.

## Table of Contents

- [Getting Started](#getting-started)
- [Tool Reference](#tool-reference)
- [Usage Examples](#usage-examples)
- [Cost Management](#cost-management)
- [Caching Best Practices](#caching-best-practices)
- [Rate Limiting](#rate-limiting)
- [Error Handling](#error-handling)
- [Advanced Usage](#advanced-usage)

## Getting Started

Once mcrentcast is installed and configured with Claude, you can start using it through natural language conversations. All 13 tools are available and will be automatically selected by Claude based on your requests.

### First Steps

1. **Verify Installation**
   ```
   User: What are my current API limits for Rentcast?
   
   Claude: I'll check your current API limits.
   [Uses get_api_limits tool]
   
   Shows: Daily: 0/100, Monthly: 0/1000, Rate limit: 3 requests/minute
   ```

2. **Set API Key (if needed)**
   ```
   User: Set my Rentcast API key to: sk_live_abcd1234...
   
   Claude: I'll set your Rentcast API key for this session.
   [Uses set_api_key tool]
   
   Response: API key updated successfully
   ```

## Tool Reference

The mcrentcast server provides 13 MCP tools organized into categories:

### Property Data Tools (4 tools)
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `search_properties` | Search for property records by location | `city`, `state`, `zipCode`, `limit`, `offset` |
| `get_property` | Get detailed property information by ID | `property_id` |
| `get_value_estimate` | Get property value estimate | `address` |
| `get_rent_estimate` | Get rental price estimate | `address`, `bedrooms`, `bathrooms`, `squareFootage` |

### Listing Tools (3 tools)
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `search_sale_listings` | Find properties currently for sale | `city`, `state`, `zipCode`, `limit` |
| `search_rental_listings` | Find rental properties | `city`, `state`, `zipCode`, `limit` |
| `get_market_statistics` | Get market trends and analytics | `city`, `state`, `zipCode` |

### Management Tools (6 tools)
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `set_api_key` | Configure Rentcast API key | `api_key` |
| `expire_cache` | Force refresh of cached data | `cache_key`, `endpoint`, `all` |
| `get_cache_stats` | View cache performance metrics | - |
| `get_usage_stats` | Track API usage and costs | `days` |
| `set_api_limits` | Configure rate limits | `daily_limit`, `monthly_limit`, `requests_per_minute` |
| `get_api_limits` | View current rate limits and usage | - |

## Usage Examples

### 1. Property Search

#### Basic Property Search
```
User: Find properties in Austin, Texas

Claude: I'll search for properties in Austin, Texas.
[Uses search_properties with city="Austin", state="TX"]

Results: Found 10 properties (fresh data)
- 123 Main St: $450,000, 3BR/2BA, 1,800 sq ft
- 456 Oak Ave: $520,000, 4BR/3BA, 2,200 sq ft
- ...
```

#### Advanced Property Search
```
User: Show me the first 5 properties in ZIP code 78701, then get the next 5

Claude: I'll search for properties in ZIP code 78701.
[Uses search_properties with zipCode="78701", limit=5, offset=0]

Then for the next batch:
[Uses search_properties with zipCode="78701", limit=5, offset=5]
```

#### Property Search with Force Refresh
```
User: Get fresh property data for downtown Seattle, ignore any cached results

Claude: I'll get fresh property data for downtown Seattle.
[Uses search_properties with city="Seattle", state="WA", force_refresh=true]

Note: This will consume API credits for fresh data
```

### 2. Property Details

#### Get Specific Property
```
User: Get details for property ID "prop_12345"

Claude: I'll get the detailed information for property ID prop_12345.
[Uses get_property with property_id="prop_12345"]

Results: Property found (from cache, age: 2.3 hours)
- Address: 789 Pine St, Denver, CO 80202
- Property Type: Single Family
- Bedrooms: 3, Bathrooms: 2.5
- Square Footage: 2,100
- Year Built: 1995
- Last Sale: $475,000 (2023-08-15)
```

### 3. Value Estimates

#### Property Value Estimate
```
User: What's the estimated value of 123 Main Street, Dallas, TX?

Claude: I'll get the value estimate for that property.
[Uses get_value_estimate with address="123 Main Street, Dallas, TX"]

Results: Value estimate: $385,000 (fresh data)
- Estimated range: $346,500 - $423,500
- Confidence: High
- Based on 3 comparable properties
- Date: 2024-01-15
```

#### Value Estimate with Property Details
```
User: I'm looking at a house at 456 Elm Ave, Portland, OR. What's it worth and what are similar properties selling for?

Claude: I'll get the value estimate and search for similar properties in Portland.
[Uses get_value_estimate and search_sale_listings]

Value Estimate: $625,000 (range: $562,500 - $687,500)
Similar properties for sale:
- 444 Elm Ave: $599,000, 3BR/2BA
- 468 Elm Ave: $649,000, 4BR/2.5BA
```

### 4. Rent Estimates

#### Basic Rent Estimate
```
User: How much could I rent out my property at 789 Broadway, San Francisco, CA?

Claude: I'll get a rental estimate for that property.
[Uses get_rent_estimate with address="789 Broadway, San Francisco, CA"]

Results: Rent estimate: $4,200/month (fresh data)
- Estimated range: $3,780 - $4,620
- Based on comparable rentals
- Long-term rental estimate
```

#### Detailed Rent Estimate
```
User: What's the rental potential for a 2-bedroom, 1.5-bathroom, 1200 sq ft condo at 555 Market St, San Francisco, CA?

Claude: I'll calculate the rental estimate with those specific details.
[Uses get_rent_estimate with address, bedrooms=2, bathrooms=1.5, squareFootage=1200]

Results: Rent estimate: $3,850/month
- Adjusted for: 2 bedrooms, 1.5 bathrooms, 1,200 sq ft
- Comparable rentals:
  - 2BR/1BA, 1,100 sq ft: $3,600/month
  - 2BR/2BA, 1,300 sq ft: $4,100/month
```

### 5. Sale Listings

#### Find Properties for Sale
```
User: What houses are currently for sale in Boulder, Colorado under $800,000?

Claude: I'll search for properties for sale in Boulder, Colorado.
[Uses search_sale_listings with city="Boulder", state="CO"]

Found 8 sale listings (from cache, age: 1.2 hours)
- 321 Mountain View Dr: $749,000, 3BR/2BA
- 654 Forest Ave: $695,000, 2BR/2BA
- 987 Creek Rd: $775,000, 4BR/3BA
```

### 6. Rental Listings

#### Find Rental Properties
```
User: Show me rental properties available in Miami Beach, FL

Claude: I'll search for rental properties in Miami Beach.
[Uses search_rental_listings with city="Miami Beach", state="FL"]

Found 12 rental listings (fresh data)
- 111 Ocean Dr: $3,200/month, 2BR/2BA, Ocean view
- 222 Collins Ave: $2,800/month, 1BR/1BA, Pool
- 333 Washington Ave: $4,500/month, 3BR/2BA, Luxury
```

### 7. Market Statistics

#### Market Analysis
```
User: What are the current market conditions in Nashville, Tennessee?

Claude: I'll get the market statistics for Nashville, Tennessee.
[Uses get_market_statistics with city="Nashville", state="TN"]

Market Statistics for Nashville, TN (fresh data):
- Median Sale Price: $425,000 (+8.2% YoY)
- Median Rent: $1,850/month (+12.1% YoY)
- Average Days on Market: 28 days
- Active Inventory: 2,847 properties
- Price per Square Foot: $185
```

#### Comparative Market Analysis
```
User: Compare the real estate markets in Austin, TX and Denver, CO

Claude: I'll get market statistics for both Austin and Denver.
[Uses get_market_statistics for both cities]

Austin, TX Market:
- Median Sale Price: $485,000 (+5.8% YoY)
- Median Rent: $2,100/month (+9.3% YoY)
- Days on Market: 32 days

Denver, CO Market:
- Median Sale Price: $525,000 (+3.2% YoY)
- Median Rent: $2,350/month (+7.8% YoY)  
- Days on Market: 29 days

Analysis: Denver has higher prices but slower appreciation
```

### 8. Cache Management

#### Check Cache Performance
```
User: How is the API cache performing?

Claude: I'll check the cache statistics.
[Uses get_cache_stats]

Cache Statistics:
- Total entries: 156
- Cache hits: 89 (57.1% hit rate)
- Cache misses: 67 (42.9% miss rate)
- Storage used: 12.3 MB / 100 MB
- Oldest entry: 18.2 hours ago
```

#### Force Cache Refresh
```
User: Clear the cache for Austin property searches and get fresh data

Claude: I'll expire the cache for Austin property searches.
[Uses expire_cache with endpoint="property-records" for Austin searches]

Cache entries expired: 8
Fresh data will be fetched on next request.
```

#### Clear All Cache
```
User: Clear all cached data

Claude: I'll clear all cached data.
[Uses expire_cache with all=true]

Expired 156 cache entries
All future requests will fetch fresh data from the API.
```

### 9. Usage Tracking

#### Check API Usage
```
User: How much have I used the Rentcast API this month?

Claude: I'll check your API usage statistics.
[Uses get_usage_stats with days=30]

Usage Statistics (Last 30 days):
- Total Requests: 47 / 1000 monthly limit
- Estimated Cost: $4.70
- Most Used Endpoint: search_properties (28 requests)
- Cache Hit Rate: 62%
- Average Response Time: 245ms
```

#### Weekly Usage Report
```
User: Show me my API usage for the past week

Claude: I'll get your usage statistics for the last 7 days.
[Uses get_usage_stats with days=7]

Weekly Usage Report:
- Total Requests: 12
- Property Searches: 7 requests
- Value Estimates: 3 requests  
- Rent Estimates: 2 requests
- Estimated Cost: $1.20
```

### 10. Rate Limit Management

#### Check Rate Limits
```
User: What are my current rate limits?

Claude: I'll check your current API limits and usage.
[Uses get_api_limits]

API Limits:
- Daily: 23/100 requests (23% used)
- Monthly: 67/1000 requests (6.7% used)
- Rate Limit: 3 requests per minute
- Current status: Within limits
```

#### Adjust Rate Limits
```
User: Increase my daily limit to 200 and monthly to 2000

Claude: I'll update your API limits.
[Uses set_api_limits with daily_limit=200, monthly_limit=2000]

API Limits Updated:
- Daily Limit: 100 → 200
- Monthly Limit: 1000 → 2000
- Rate Limit: 3 requests/minute (unchanged)
```

## Cost Management

### Understanding API Costs

The mcrentcast server provides cost estimates and tracking:

- **Property Records Search**: ~$0.05-0.10 per request
- **Value Estimates**: ~$0.15-0.25 per request  
- **Rent Estimates**: ~$0.15-0.25 per request
- **Sale/Rental Listings**: ~$0.10-0.15 per request
- **Market Statistics**: ~$0.20-0.30 per request

### Cost-Saving Strategies

1. **Use Caching Effectively**
   ```
   User: I want to analyze Austin properties but minimize API costs
   
   Claude: I'll help you minimize costs by using cached data where possible.
   
   Strategy:
   - First search will be fresh (costs credits)
   - Subsequent related searches use cache
   - Market data cached for 24 hours by default
   ```

2. **Batch Related Requests**
   ```
   User: Get comprehensive data for ZIP code 90210 - properties, listings, and market stats
   
   Claude: I'll get all the data for ZIP code 90210 in an efficient way.
   [Makes strategic API calls and leverages caching]
   ```

3. **Use Mock API for Testing**
   ```
   User: I want to test property searches without using API credits
   
   Claude: You can use the mock API mode for testing. 
   Configure with: USE_MOCK_API=true RENTCAST_API_KEY=test_key_basic
   ```

### Cost Monitoring
```
User: Alert me if I'm approaching my monthly API limit

Claude: I'll check your current usage against limits.
[Uses get_api_limits and get_usage_stats]

Current Usage: 850/1000 monthly requests (85% used)
Warning: You're approaching your monthly limit. Consider:
- Using cached data when possible
- Setting force_refresh=false (default)
- Monitoring with get_usage_stats regularly
```

## Caching Best Practices

### Understanding Cache Behavior

1. **Automatic Caching**: All responses are cached by default
2. **TTL (Time To Live)**: Default 24 hours, configurable
3. **Cache Keys**: Based on endpoint + parameters
4. **Force Refresh**: Use `force_refresh=true` to bypass cache

### Cache Strategy Examples

#### Smart Cache Usage
```
User: I'm doing market research on Austin. Get me property data efficiently.

Claude: I'll structure the requests to maximize cache efficiency.

1. Get market statistics (cached for 24h)
2. Search properties (results cached)
3. Get specific property details (uses cache if available)

This approach minimizes API calls while providing comprehensive data.
```

#### Cache Warming
```
User: Prepare cached data for a client presentation on Denver real estate tomorrow

Claude: I'll pre-load cache with relevant Denver data.
[Makes strategic API calls to cache:]
- Market statistics
- Property searches by key ZIP codes
- Recent sale listings
- Rental market data

Data will be cached and ready for your presentation.
```

### Cache Maintenance
```
User: My cache seems stale. Refresh data for Seattle properties.

Claude: I'll refresh the Seattle property cache.
[Uses expire_cache for Seattle-related entries, then searches with force_refresh]

Cache refreshed with fresh Seattle property data.
```

## Rate Limiting

### Understanding Rate Limits

The server implements multiple rate limiting layers:

1. **API-level**: Rentcast's limits (varies by plan)
2. **Per-minute**: Default 3 requests/minute (configurable)
3. **Daily/Monthly**: User-configurable quotas
4. **Exponential Backoff**: Automatic retry with delays

### Working with Rate Limits

#### Handling Rate Limit Messages
```
User: Get data for 20 different ZIP codes quickly

Claude: I'll get data for multiple ZIP codes, but I need to respect rate limits.
[Implements strategic delays between requests]

Note: Spacing requests to stay within 3 requests/minute limit.
Processing ZIP codes in batches...
```

#### Adjusting Rate Limits
```
User: I have a premium API plan. Increase my rate limits.

Claude: I'll update your rate limits for your premium plan.
[Uses set_api_limits]

Updated for premium plan:
- Daily: 500 requests  
- Monthly: 5000 requests
- Rate: 10 requests/minute
```

## Error Handling

### Common Error Scenarios

#### API Key Issues
```
User: Get properties in Chicago

Claude: I encountered an API key issue. Let me help resolve it.
[Error: API key not configured]

Solution: Please set your API key using:
"Set my Rentcast API key to: your_actual_key"
```

#### Rate Limit Exceeded
```
User: [After many requests] Get more property data

Claude: I've hit the rate limit. 
[Error: Rate limit exceeded - retry after X seconds]

I'll wait and retry, or you can:
- Use cached data with previous searches
- Increase rate limits if you have a higher plan
- Use mock API for testing
```

#### Invalid Parameters
```
User: Get property data for "fake city, ZZ"

Claude: I'll search for properties in that location.
[Error: Invalid location parameters]

The location "fake city, ZZ" wasn't found. Please try:
- Valid city and state combinations
- Existing ZIP codes
- Check spelling of location names
```

### Error Recovery Strategies

#### Automatic Retry with Cached Data
```
User: Get Austin property data

Claude: I'll try to get Austin property data.
[API call fails, falls back to cache]

Using cached Austin data (age: 8.5 hours) due to API error.
Would you like me to retry with fresh data?
```

#### Graceful Degradation
```
User: Get comprehensive market report for Phoenix

Claude: I'll gather comprehensive Phoenix market data.
[Some API calls succeed, others fail]

I was able to get:
✓ Property listings (fresh)  
✓ Market statistics (cached, 4h old)
✗ Value estimates (API error - using cached data)

The report is mostly complete with some cached data.
```

## Advanced Usage

### Complex Analysis Workflows

#### Investment Property Analysis
```
User: Analyze 123 Oak St, Portland, OR as a potential rental investment

Claude: I'll perform a comprehensive investment analysis.
[Uses multiple tools strategically:]

1. Property details and current value
2. Rental estimate and comparable rentals
3. Local market statistics and trends
4. Sale listings for comparable properties

Investment Analysis for 123 Oak St, Portland, OR:
- Current Value: $485,000 (±$25,000)
- Rental Potential: $2,400/month
- Gross Yield: 5.9% annually
- Market Appreciation: +6.2% YoY
- Days on Market: 34 days average
- Recommendation: Positive cash flow potential
```

#### Market Comparison Study
```
User: Compare investment opportunities between Austin, Nashville, and Raleigh

Claude: I'll compare real estate investment metrics across all three cities.
[Systematic market analysis using cached data where possible]

Market Comparison Study:

Austin, TX:
- Median Price: $485K, Rent: $2,100 (Yield: 5.2%)
- Appreciation: +5.8% YoY, DOM: 32 days

Nashville, TN:  
- Median Price: $425K, Rent: $1,850 (Yield: 5.2%)
- Appreciation: +8.2% YoY, DOM: 28 days

Raleigh, NC:
- Median Price: $365K, Rent: $1,650 (Yield: 5.4%)
- Appreciation: +7.1% YoY, DOM: 25 days

Best Value: Raleigh (lower entry cost, good yields)
Best Growth: Nashville (highest appreciation)
Most Liquid: Raleigh (fastest sales)
```

### Automated Monitoring

#### Market Watch Setup
```
User: Set up automated monitoring for Phoenix real estate market changes

Claude: I'll help you track Phoenix market changes efficiently.

Strategy:
1. Weekly market statistics checks
2. Cache management to minimize costs
3. Threshold alerts for significant changes
4. Usage tracking to stay within limits

I'll check Phoenix market stats weekly and alert you to:
- Price changes >5%
- Inventory changes >20%
- New rental/sale listings in target areas
```

#### Portfolio Monitoring
```
User: Track value estimates for my 3 rental properties monthly

Properties:
- 123 Main St, Austin, TX
- 456 Oak Ave, Denver, CO  
- 789 Pine St, Atlanta, GA

Claude: I'll set up monthly value tracking for your portfolio.

Monthly Portfolio Report Strategy:
- Value estimates for all 3 properties
- Market statistics for each city
- Rental market comparisons
- Performance trends over time

I'll use caching efficiently and track API usage to minimize costs.
```

### Integration Patterns

#### Real Estate CRM Integration
```
User: I have leads interested in Austin properties under $400K. Find suitable options and get market context.

Claude: I'll find suitable Austin properties and provide market context.
[Strategic search and analysis]

Austin Properties Under $400K:
- 5 properties found matching criteria
- Market context: Prices 15% below median
- Rental yields: 6.2-7.1% range
- Market trend: +5.8% appreciation
- Investment grade: Good entry opportunity

Ready for CRM integration with detailed property packets.
```

#### Reporting and Analytics
```
User: Generate a quarterly market report for my real estate clients covering Dallas-Fort Worth

Claude: I'll create a comprehensive DFW quarterly market report.
[Comprehensive data gathering using efficient API calls]

Q4 2024 Dallas-Fort Worth Market Report:

Executive Summary:
- Median home price: $425K (+4.2% QoQ)
- Average rent: $1,950/month (+8.1% QoQ)
- Inventory levels: 3.2 months supply
- Market velocity: 31 days average DOM

Detailed analysis with charts and comparable data ready for client presentation.
```

## Best Practices Summary

### Cost Optimization
1. **Leverage caching** - Don't force refresh unnecessarily
2. **Batch related requests** - Get comprehensive data efficiently  
3. **Monitor usage** - Track costs with `get_usage_stats`
4. **Use mock API** - For testing and development
5. **Set appropriate limits** - Match your Rentcast plan

### Performance Optimization
1. **Cache warming** - Pre-load frequently accessed data
2. **Strategic timing** - Respect rate limits
3. **Error handling** - Graceful fallbacks to cached data
4. **Batch operations** - Combine related searches

### Data Management
1. **Regular cache maintenance** - Clean expired entries
2. **Monitor cache hit rates** - Optimize for efficiency
3. **Track API patterns** - Understand usage trends
4. **Validate data freshness** - Balance cost vs. accuracy

### Security and Reliability
1. **Secure API key storage** - Use environment variables
2. **Rate limit compliance** - Avoid API suspensions
3. **Error monitoring** - Track and resolve issues
4. **Backup strategies** - Cache provides resilience

This comprehensive usage guide should help you maximize the value of the mcrentcast MCP server while minimizing costs and maintaining optimal performance.