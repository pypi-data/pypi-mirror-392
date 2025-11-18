# MCRentCast MCP Server - Comprehensive Test Suite

This directory contains a comprehensive test suite for the mcrentcast MCP server, designed to thoroughly test all 13 MCP tools with various scenarios including caching, rate limiting, error handling, and both mock and real API modes.

## 📁 Test Structure

```
tests/
├── conftest.py              # pytest configuration and shared fixtures
├── test_mcp_server.py       # Main comprehensive test suite (1,400+ lines)
├── run_comprehensive_tests.py # Test runner script
├── test_integration.py      # Existing integration tests
├── test_server.py          # Basic server tests
└── README.md               # This file
```

## 🧪 Test Coverage

### 13 MCP Tools Tested
The test suite comprehensively tests all MCP tools defined in the server:

1. **`set_api_key`** - API key management and validation
2. **`get_api_limits`** - Current API limits and usage retrieval
3. **`set_api_limits`** - API rate limit configuration
4. **`search_properties`** - Property record search with caching
5. **`get_property`** - Individual property details retrieval
6. **`get_value_estimate`** - Property value estimation
7. **`get_rent_estimate`** - Property rent estimation  
8. **`search_sale_listings`** - Sale listing search
9. **`search_rental_listings`** - Rental listing search
10. **`get_market_statistics`** - Market statistics by location
11. **`expire_cache`** - Cache management and expiration
12. **`get_cache_stats`** - Cache performance statistics
13. **`get_usage_stats`** - API usage tracking and reporting

### Test Categories

#### 🟢 **Smoke Tests** (`@pytest.mark.smoke`)
- **`test_all_tools_exist`** - Verifies all 13 expected tools are registered
- **`test_basic_server_functionality`** - Basic server setup validation

#### 🔵 **Unit Tests** (`@pytest.mark.unit`) 
- **API Key Management** - Set/validation with success and error cases
- **Property Operations** - Individual tool functionality with mocking
- **Cache Management** - Cache operations and statistics
- **Usage & Limits** - API quota and rate limit management
- **Error Handling** - Comprehensive error scenario testing

#### 🟣 **Integration Tests** (`@pytest.mark.integration`)
- **Cache Hit/Miss Scenarios** - Full caching workflow testing
- **Rate Limiting Behavior** - Exponential backoff and limit enforcement
- **Mock API Integration** - Testing with mock Rentcast API
- **Confirmation Flow** - User confirmation and elicitation testing

#### 🟠 **Performance Tests** (`@pytest.mark.performance`)
- **Concurrent Request Handling** - Multiple simultaneous requests
- **Rate Limit Stress Testing** - High-frequency request scenarios
- **Cache Performance** - Cache efficiency under load

#### 🔴 **API Tests** (`@pytest.mark.api`)
- **Real API Integration** - Tests against actual Rentcast API (when configured)
- **Mock vs Real Comparison** - Behavior validation across modes

## 🚀 Enhanced Testing Framework

### TestReporter Class
Custom test reporting with syntax highlighting and quality metrics:

```python
reporter = TestReporter("test_name")
reporter.log_input("request_data", data, "Test input description")
reporter.log_processing_step("validation", "Validating API response", duration_ms=25.3)
reporter.log_output("result", response, quality_score=9.5)
reporter.log_quality_metric("accuracy", 0.95, threshold=0.90, passed=True)
result = reporter.complete()
```

### Beautiful HTML Reports
- **Professional styling** with Inter fonts and gradient headers
- **Quality scores** for each test with color-coded results
- **Test categorization** with automatic marker detection
- **Performance metrics** and timing information
- **Interactive filtering** by test result and category

### Advanced Mocking
- **Database manager mocking** for isolated testing
- **Rentcast client mocking** with configurable responses
- **Confirmation flow mocking** for user interaction testing
- **Rate limiting simulation** for error condition testing

## 🎯 Key Testing Scenarios

### Caching Functionality
```python
# Cache hit scenario
mock_db_manager.get_cache_entry.return_value = MagicMock()  # Cache exists
result = await app.tools["search_properties"](request)
assert result["cached"] is True
assert result["cache_age_hours"] > 0

# Cache miss with confirmation
mock_db_manager.get_cache_entry.return_value = None  # Cache miss
mock_confirmation.return_value = True  # User confirms
result = await app.tools["search_properties"](request)
assert result["cached"] is False
```

### Rate Limiting
```python
# Rate limit exceeded
mock_client.get_property_records.side_effect = RateLimitExceeded("Rate limit exceeded")
result = await app.tools["search_properties"](request)
assert result["error"] == "Rate limit exceeded"
assert "retry_after" in result
```

### Error Handling
```python
# API error handling
mock_client.get_property_records.side_effect = RentcastAPIError("Invalid API key")
result = await app.tools["search_properties"](request)
assert result["error"] == "API error"
assert "Invalid API key" in result["message"]
```

## 📊 Running Tests

### Quick Start
```bash
# Run all smoke tests
PYTHONPATH=src uv run pytest tests/test_mcp_server.py::TestSmokeTests -v

# Run comprehensive test suite
python tests/run_comprehensive_tests.py

# Run specific test categories
PYTHONPATH=src uv run pytest tests/test_mcp_server.py -m unit -v
PYTHONPATH=src uv run pytest tests/test_mcp_server.py -m integration -v
PYTHONPATH=src uv run pytest tests/test_mcp_server.py -m performance -v
```

### Advanced Usage
```bash
# Generate HTML report
PYTHONPATH=src uv run pytest tests/test_mcp_server.py --html=reports/test_report.html --self-contained-html

# Run with coverage
PYTHONPATH=src uv run pytest tests/test_mcp_server.py --cov=src --cov-report=html --cov-report=term

# Run specific tests
PYTHONPATH=src uv run pytest tests/test_mcp_server.py::TestPropertySearch::test_search_properties_cached_hit -v

# Collect tests without running
PYTHONPATH=src uv run pytest tests/test_mcp_server.py --collect-only
```

## 🔧 Test Configuration

### Fixtures Available
- **`mock_db_manager`** - Mocked database operations
- **`mock_rentcast_client`** - Mocked Rentcast API client
- **`sample_property`** - Sample property record data
- **`sample_cache_stats`** - Sample cache statistics
- **`test_data_factory`** - Factory for creating test objects

### Environment Variables
- **`PYTHONPATH=src`** - Required for imports
- **`PYTEST_CURRENT_TEST`** - Auto-set by pytest
- **`RENTCAST_API_KEY`** - For real API testing (optional)

## 📈 Test Metrics

### Coverage Targets
- **Unit Tests**: 70-80% code coverage
- **Critical Paths**: 90%+ coverage  
- **Integration Tests**: End-to-end workflow coverage
- **Error Paths**: All error conditions tested

### Quality Metrics
- **Response Time**: < 1000ms for mocked tests
- **Accuracy**: 95%+ for data validation tests
- **Reliability**: 0% flaky tests tolerance
- **Maintainability**: Clear, descriptive test names and structure

## 🛠 Extending Tests

### Adding New Tests
```python
class TestNewFeature:
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_new_functionality(self, mock_db_manager):
        """Test new feature functionality."""
        reporter = TestReporter("new_functionality")
        
        # Test implementation
        result = await app.tools["new_tool"](request)
        
        # Assertions
        assert result["success"] is True
        
        reporter.complete()
```

### Custom Fixtures
```python
@pytest.fixture
def custom_test_data():
    """Provide custom test data."""
    return {"custom": "data"}
```

## 📋 Test Checklist

- [x] All 13 MCP tools have comprehensive tests
- [x] Cache hit and miss scenarios covered
- [x] Rate limiting behavior tested
- [x] Error handling for all failure modes
- [x] Mock API mode testing
- [x] User confirmation flow testing
- [x] Performance and concurrency testing
- [x] Beautiful HTML reporting with quality metrics
- [x] Professional test structure with fixtures
- [x] Documentation and usage examples

## 🎨 Report Examples

The test suite generates beautiful HTML reports with:
- **Custom styling** with professional gradients and typography
- **Test categorization** (Unit, Integration, Smoke, Performance, API)
- **Quality scores** (9.5/10 for passing tests, 3.0/10 for failures)
- **Performance timing** for each test
- **Interactive filtering** by result type and category

## 🚀 Next Steps

1. **Run the comprehensive test suite** to validate all functionality
2. **Review HTML reports** for detailed test results and coverage
3. **Add real API tests** when Rentcast API key is available
4. **Extend performance tests** for production load scenarios
5. **Integrate with CI/CD** pipeline for automated testing

This test suite follows FastMCP testing guidelines and provides comprehensive coverage of the mcrentcast MCP server functionality, ensuring reliability and maintainability of the codebase.