# Mock Rentcast API Documentation

The mcrentcast project includes a complete mock implementation of the Rentcast API for testing and development purposes. This allows you to:

- Test without consuming real API credits
- Develop offline
- Test rate limiting and error scenarios
- Run integration tests reliably

## Available Test API Keys

The mock API provides several test keys with different rate limits:

| API Key | Tier | Daily Limit | Monthly Limit | Use Case |
|---------|------|-------------|---------------|----------|
| `test_key_free_tier` | Free | 50 | 50 | Testing free tier limits |
| `test_key_basic` | Basic | 100 | 1,000 | Standard testing |
| `test_key_pro` | Pro | 1,000 | 10,000 | High-volume testing |
| `test_key_enterprise` | Enterprise | 10,000 | 100,000 | Unlimited testing |
| `test_key_rate_limited` | Test | 1 | 1 | Testing rate limit errors |
| `test_key_invalid` | Invalid | 0 | 0 | Testing auth errors |

## Starting the Mock API

### Option 1: Full Stack with Mock API
```bash
make test-mock
```
This starts all services with the mock API enabled.

### Option 2: Mock API Only
```bash
make mock-api
```
This starts only the mock API server on port 8001.

### Option 3: Docker Compose
```bash
USE_MOCK_API=true docker compose --profile mock up -d
```

## Configuration

To use the mock API, set these environment variables in your `.env` file:

```env
USE_MOCK_API=true
MOCK_API_URL=http://mock-rentcast-api:8001/v1
RENTCAST_API_KEY=test_key_basic
```

## Endpoints

The mock API implements all Rentcast endpoints:

### Property Records
- `GET /v1/property-records` - Search properties
- `GET /v1/property-records/random` - Get random properties
- `GET /v1/property-record/{id}` - Get specific property

### Valuations
- `GET /v1/value-estimate` - Property value estimate
- `GET /v1/rent-estimate-long-term` - Rental price estimate

### Listings
- `GET /v1/sale-listings` - Properties for sale
- `GET /v1/sale-listing/{id}` - Specific sale listing
- `GET /v1/rental-listings-long-term` - Rental properties
- `GET /v1/rental-listing-long-term/{id}` - Specific rental

### Market Data
- `GET /v1/market-statistics` - Market statistics

### Utility Endpoints
- `GET /health` - Health check
- `GET /test-keys` - List available test keys

## Testing the Mock API

### Manual Testing
```bash
# Start the mock API
make mock-api

# Run the test script
python scripts/test_mock_api.py
```

### Integration Tests
```bash
# Run integration tests with mock API
USE_MOCK_API=true uv run pytest tests/test_integration.py -v
```

### Using curl
```bash
# Get test keys
curl http://localhost:8001/test-keys

# Search properties
curl -H "X-Api-Key: test_key_basic" \
  "http://localhost:8001/v1/property-records?city=Austin&state=TX&limit=5"

# Get value estimate
curl -H "X-Api-Key: test_key_basic" \
  "http://localhost:8001/v1/value-estimate?address=123+Main+St"
```

## Mock Data Characteristics

The mock API generates realistic but randomized data:

### Property Records
- Random addresses from predefined street names
- Property types: Single Family, Condo, Townhouse, Multi Family
- Bedrooms: 1-5
- Bathrooms: 1.0-4.0 (in 0.5 increments)
- Square footage: 800-4000
- Year built: 1950-2023
- Prices: $150,000-$1,500,000

### Value Estimates
- Base price: $200,000-$1,000,000
- Price range: ±10% of base price
- Confidence levels: High, Medium, Low
- Includes 3 comparable properties

### Rent Estimates
- Base rent: $1,500-$5,000/month
- Rent range: ±10% of base rent
- Adjusts based on bedrooms and square footage
- Includes 3 comparable rentals

### Market Statistics
- Median sale price: $300,000-$800,000
- Median rent: $1,500-$3,500
- Average days on market: 15-60
- Inventory count: 100-1,000 properties
- Price appreciation: -5% to +15%

## Rate Limiting Simulation

The mock API simulates Rentcast's rate limiting:

1. Each API key has daily and monthly limits
2. Requests are tracked per key
3. Returns 429 status when limits exceeded
4. Daily counters reset after 24 hours

### Testing Rate Limits
```python
# Use the rate-limited test key
client = RentcastClient(api_key="test_key_rate_limited")

# First request succeeds
response1 = await client.get_property_records(limit=1)  # ✅

# Second request fails with rate limit error
response2 = await client.get_property_records(limit=1)  # ❌ 429 Error
```

## Error Simulation

The mock API simulates various error conditions:

### Authentication Errors (401)
- Use an invalid API key
- Omit the X-Api-Key header

### Forbidden Access (403)
- Use `test_key_invalid` (suspended account)

### Rate Limiting (429)
- Exceed daily/monthly limits
- Use `test_key_rate_limited` for immediate limiting

### Bad Requests (400)
- Omit required parameters
- Use invalid parameter values

## Advantages of Mock API

1. **Cost-Free Testing**: No API credits consumed
2. **Predictable Data**: Consistent test results
3. **Offline Development**: No internet required
4. **Error Testing**: Simulate edge cases easily
5. **CI/CD Integration**: Reliable automated testing
6. **Performance Testing**: No rate limits for load testing

## Switching Between Real and Mock APIs

### Development (Mock API)
```bash
USE_MOCK_API=true make dev
```

### Production (Real API)
```bash
USE_MOCK_API=false RENTCAST_API_KEY=your_real_key make prod
```

### Toggle in Code
```python
from src.mcrentcast.config import settings

# Check current mode
if settings.use_mock_api:
    print("Using mock API")
else:
    print("Using real Rentcast API")
```

## Troubleshooting

### Mock API not responding
```bash
# Check if service is running
docker compose ps mock-rentcast-api

# View logs
docker compose logs mock-rentcast-api

# Restart service
docker compose restart mock-rentcast-api
```

### Rate limiting not working
- Ensure you're using the correct test key
- Check that daily counters haven't been reset
- Verify the API usage tracking in logs

### Data inconsistency
- Mock data is randomly generated
- Use fixed seeds for deterministic testing
- Cache responses for consistent results

## Best Practices

1. **Use appropriate test keys** for different scenarios
2. **Test error conditions** with special keys
3. **Verify caching** works with mock responses
4. **Run integration tests** before deploying
5. **Document test scenarios** using mock data
6. **Monitor mock API logs** for debugging