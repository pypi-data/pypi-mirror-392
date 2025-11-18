"""Pytest configuration and fixtures for mcrentcast MCP server tests.

Provides shared fixtures, test configuration, and enhanced HTML report styling
following the project's testing framework requirements.
"""

import asyncio
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import pytest
import structlog
from unittest.mock import AsyncMock, MagicMock

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Configure test logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def clean_test_environment():
    """Ensure clean test environment for each test."""
    # Reset any global state
    yield
    # Cleanup after test


@pytest.fixture
def mock_settings():
    """Mock application settings for testing."""
    from unittest.mock import patch
    
    with patch("mcrentcast.server.settings") as mock_settings:
        # Configure default mock settings
        mock_settings.rentcast_api_key = "test_api_key_123"
        mock_settings.use_mock_api = False
        mock_settings.daily_api_limit = 100
        mock_settings.monthly_api_limit = 1000
        mock_settings.requests_per_minute = 3
        mock_settings.cache_ttl_hours = 24
        mock_settings.mode = "test"
        mock_settings.validate_api_key.return_value = True
        
        yield mock_settings


@pytest.fixture
async def test_database():
    """Provide test database instance."""
    # For testing, we'll use in-memory SQLite
    from mcrentcast.database import DatabaseManager
    
    test_db = DatabaseManager(database_url="sqlite:///:memory:")
    test_db.create_tables()
    
    yield test_db
    
    # Cleanup
    if hasattr(test_db, 'close'):
        await test_db.close()


@pytest.fixture
def sample_test_data():
    """Provide sample test data for various test scenarios."""
    from mcrentcast.models import (
        PropertyRecord,
        ValueEstimate,
        RentEstimate,
        SaleListing,
        RentalListing,
        MarketStatistics
    )
    
    return {
        "property_record": PropertyRecord(
            id="test_prop_001",
            address="123 Test Street",
            city="Test City",
            state="TX",
            zipCode="12345",
            propertyType="Single Family",
            bedrooms=3,
            bathrooms=2.0,
            squareFootage=1800,
            yearBuilt=2015,
            lastSalePrice=350000,
            zestimate=375000,
            rentestimate=2200
        ),
        
        "value_estimate": ValueEstimate(
            address="123 Test Street",
            price=375000,
            priceRangeLow=350000,
            priceRangeHigh=400000,
            confidence="High",
            lastSaleDate="2023-06-15",
            lastSalePrice=350000
        ),
        
        "rent_estimate": RentEstimate(
            address="123 Test Street",
            rent=2200,
            rentRangeLow=2000,
            rentRangeHigh=2400,
            confidence="Medium"
        ),
        
        "sale_listing": SaleListing(
            id="sale_test_001",
            address="456 Sale Avenue",
            city="Sale City",
            state="CA",
            zipCode="54321",
            price=525000,
            bedrooms=4,
            bathrooms=3.0,
            squareFootage=2400,
            propertyType="Single Family",
            listingDate="2024-08-01",
            daysOnMarket=30
        ),
        
        "rental_listing": RentalListing(
            id="rent_test_001", 
            address="789 Rental Road",
            city="Rental City",
            state="NY",
            zipCode="67890",
            rent=3200,
            bedrooms=2,
            bathrooms=2.0,
            squareFootage=1400,
            propertyType="Condo",
            availableDate="2024-10-01",
            pets="Dogs allowed"
        ),
        
        "market_statistics": MarketStatistics(
            city="Test City",
            state="TX",
            medianSalePrice=425000,
            medianRent=2100,
            averageDaysOnMarket=32,
            inventoryCount=850,
            pricePerSquareFoot=245.50,
            rentPerSquareFoot=1.65,
            appreciation=6.8
        )
    }


def pytest_html_report_title(report):
    """Customize HTML report title."""
    report.title = "🏠 MCRentCast MCP Server - Comprehensive Test Results"


def pytest_html_results_table_header(cells):
    """Customize HTML report table headers."""
    cells.insert(2, '<th class="sortable" data-column-type="text">Test Category</th>')
    cells.insert(3, '<th class="sortable" data-column-type="text">Quality Score</th>')


def pytest_html_results_table_row(report, cells):
    """Customize HTML report table rows with enhanced information."""
    # Extract test category from markers
    test_categories = []
    if hasattr(report, 'keywords'):
        for marker in ['unit', 'integration', 'smoke', 'performance', 'api']:
            if marker in report.keywords:
                test_categories.append(marker.title())
    
    category = ", ".join(test_categories) if test_categories else "General"
    
    # Calculate quality score based on test outcome and performance
    if report.passed:
        quality_score = "9.5/10" if report.duration < 1.0 else "8.5/10"
        quality_color = "color: #28a745;"
    elif report.failed:
        quality_score = "3.0/10"
        quality_color = "color: #dc3545;"
    elif report.skipped:
        quality_score = "N/A"
        quality_color = "color: #6c757d;"
    else:
        quality_score = "Unknown"
        quality_color = "color: #17a2b8;"
    
    # Insert custom columns
    cells.insert(2, f'<td>{category}</td>')
    cells.insert(3, f'<td style="{quality_color}"><strong>{quality_score}</strong></td>')


def pytest_html_results_summary(prefix, session, postfix):
    """Add custom summary information to the HTML report.""" 
    test_summary = f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center;">
        <h2 style="margin: 0 0 10px 0; font-size: 24px;">🏠 MCRentCast MCP Server Test Suite</h2>
        <p style="margin: 5px 0; opacity: 0.9;">Comprehensive testing of 13 MCP tools with caching, rate limiting, and error handling</p>
        <p style="margin: 5px 0; opacity: 0.9;">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
        <p style="margin: 5px 0; opacity: 0.9;">Testing Framework: pytest + FastMCP + Enhanced Reporting</p>
    </div>
    """
    prefix.extend([test_summary])


@pytest.fixture(autouse=True)
async def test_setup_and_teardown():
    """Automatic setup and teardown for each test."""
    # Setup
    test_start_time = datetime.now(timezone.utc)
    
    # Test execution happens here
    yield
    
    # Teardown
    test_duration = (datetime.now(timezone.utc) - test_start_time).total_seconds()
    
    # Log test completion (optional)
    if test_duration > 5.0:  # Log slow tests
        logging.warning(f"Slow test detected: {test_duration:.2f}s")


@pytest.fixture
def test_performance_tracker():
    """Track test performance metrics."""
    class PerformanceTracker:
        def __init__(self):
            self.metrics = {}
            self.start_time = None
            
        def start_tracking(self, operation: str):
            self.start_time = datetime.now(timezone.utc)
            
        def end_tracking(self, operation: str):
            if self.start_time:
                duration = (datetime.now(timezone.utc) - self.start_time).total_seconds() * 1000
                self.metrics[operation] = duration
                self.start_time = None
                
        def get_metrics(self) -> Dict[str, float]:
            return self.metrics.copy()
    
    return PerformanceTracker()


# Custom pytest markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests that test individual functions")
    config.addinivalue_line("markers", "integration: Integration tests that test component interactions")
    config.addinivalue_line("markers", "smoke: Smoke tests for basic functionality verification")
    config.addinivalue_line("markers", "performance: Performance and benchmarking tests")
    config.addinivalue_line("markers", "api: Rentcast API integration tests")
    config.addinivalue_line("markers", "slow: Tests that are expected to take longer than usual")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add automatic markers."""
    for item in items:
        # Add slow marker to tests that might be slow
        if "integration" in item.keywords or "performance" in item.keywords:
            item.add_marker(pytest.mark.slow)
        
        # Add markers based on test class names
        if "TestApiKeyManagement" in str(item.parent):
            item.add_marker(pytest.mark.unit)
        elif "TestPropertySearch" in str(item.parent):
            item.add_marker(pytest.mark.integration)
        elif "TestSmokeTests" in str(item.parent):
            item.add_marker(pytest.mark.smoke)
        elif "TestRateLimiting" in str(item.parent):
            item.add_marker(pytest.mark.performance)


@pytest.fixture
def mock_logger():
    """Provide mock logger for testing."""
    return MagicMock(spec=structlog.BoundLogger)


# Test data factories
class TestDataFactory:
    """Factory for creating test data objects."""
    
    @staticmethod
    def create_property_record(**kwargs):
        """Create a property record with default values."""
        from mcrentcast.models import PropertyRecord
        
        defaults = {
            "id": "factory_prop_001",
            "address": "Factory Test Address",
            "city": "Factory City",
            "state": "TX",
            "zipCode": "00000",
            "propertyType": "Single Family",
            "bedrooms": 3,
            "bathrooms": 2.0,
            "squareFootage": 1500
        }
        defaults.update(kwargs)
        return PropertyRecord(**defaults)
    
    @staticmethod
    def create_cache_stats(**kwargs):
        """Create cache stats with default values."""
        from mcrentcast.models import CacheStats
        
        defaults = {
            "total_entries": 100,
            "total_hits": 80,
            "total_misses": 20,
            "cache_size_mb": 5.0,
            "hit_rate": 80.0
        }
        defaults.update(kwargs)
        return CacheStats(**defaults)


@pytest.fixture
def test_data_factory():
    """Provide test data factory."""
    return TestDataFactory()


# Async test utilities
@pytest.fixture
def async_test_utils():
    """Provide utilities for async testing."""
    class AsyncTestUtils:
        @staticmethod
        async def wait_for_condition(condition_func, timeout=5.0, interval=0.1):
            """Wait for a condition to become true."""
            import asyncio
            
            end_time = asyncio.get_event_loop().time() + timeout
            while asyncio.get_event_loop().time() < end_time:
                if await condition_func():
                    return True
                await asyncio.sleep(interval)
            return False
        
        @staticmethod
        async def run_with_timeout(coro, timeout=10.0):
            """Run coroutine with timeout."""
            return await asyncio.wait_for(coro, timeout=timeout)
    
    return AsyncTestUtils()


# Environment setup for different test modes
@pytest.fixture(params=["mock_api", "real_api"])
def api_mode(request):
    """Parameterized fixture for testing both mock and real API modes."""
    return request.param


@pytest.fixture
def configure_test_mode(api_mode):
    """Configure test environment based on API mode."""
    from unittest.mock import patch
    
    use_mock = api_mode == "mock_api"
    
    with patch("mcrentcast.server.settings") as mock_settings:
        mock_settings.use_mock_api = use_mock
        mock_settings.mock_api_url = "http://localhost:8001/v1" if use_mock else None
        yield api_mode