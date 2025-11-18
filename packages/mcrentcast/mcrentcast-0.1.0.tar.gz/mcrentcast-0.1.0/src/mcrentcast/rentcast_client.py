"""Rentcast API client with intelligent caching and rate limiting."""

import asyncio
import hashlib
import json
from decimal import Decimal
from typing import Any, Dict, List, Optional

import httpx
import structlog
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from .config import settings
from .database import db_manager
from .models import (
    MarketStatistics,
    PropertyRecord,
    RentEstimate,
    RentalListing,
    SaleListing,
    ValueEstimate,
)

logger = structlog.get_logger()


class RentcastAPIError(Exception):
    """Rentcast API error."""
    pass


class RateLimitExceeded(Exception):
    """Rate limit exceeded error."""
    pass


class RentcastClient:
    """Rentcast API client with caching and rate limiting."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or settings.rentcast_api_key
        
        # Use mock API if configured
        if settings.use_mock_api:
            self.base_url = settings.mock_api_url
            # Use a test key if no key provided and in mock mode
            if not self.api_key:
                self.api_key = "test_key_basic"
        else:
            self.base_url = base_url or settings.rentcast_base_url
        
        if not self.api_key:
            raise ValueError("Rentcast API key is required")
            
        self.client = httpx.AsyncClient(
            headers={
                "X-Api-Key": self.api_key,
                "Content-Type": "application/json",
                "User-Agent": "mcrentcast/0.1.0"
            },
            timeout=30.0
        )
        
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
        
    def _create_cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Create cache key for request."""
        data = json.dumps({"endpoint": endpoint, "params": params}, sort_keys=True)
        return hashlib.md5(data.encode()).hexdigest()
        
    def _estimate_cost(self, endpoint: str) -> Decimal:
        """Estimate cost for API request (placeholder logic)."""
        # This would be replaced with actual cost estimation based on Rentcast pricing
        cost_map = {
            "property-records": Decimal("0.10"),
            "property-record": Decimal("0.05"),
            "value-estimate": Decimal("0.15"),
            "rent-estimate-long-term": Decimal("0.15"),
            "sale-listings": Decimal("0.08"),
            "sale-listing": Decimal("0.05"),
            "rental-listings-long-term": Decimal("0.08"),
            "rental-listing-long-term": Decimal("0.05"),
            "market-statistics": Decimal("0.20"),
        }
        return cost_map.get(endpoint.replace("/", "").replace("-", ""), Decimal("0.10"))
        
    @retry(
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        wait=wait_exponential(
            multiplier=settings.exponential_backoff_base,
            max=settings.exponential_backoff_max_delay
        ),
        stop=stop_after_attempt(3),
        before_sleep=before_sleep_log(logger, "WARNING", exc_info=True)
    )
    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request to Rentcast API with retry logic."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        logger.info("Making Rentcast API request", endpoint=endpoint, params=params)
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            # Track successful API usage
            await db_manager.track_api_usage(
                endpoint=endpoint,
                request_data=params,
                response_status=response.status_code,
                cost_estimate=self._estimate_cost(endpoint),
                cache_hit=False
            )
            
            return response.json()
            
        except httpx.HTTPStatusError as e:
            # Track failed API usage
            await db_manager.track_api_usage(
                endpoint=endpoint,
                request_data=params,
                response_status=e.response.status_code,
                cost_estimate=self._estimate_cost(endpoint),
                cache_hit=False
            )
            
            if e.response.status_code == 429:
                raise RateLimitExceeded(f"Rentcast API rate limit exceeded: {e.response.text}")
            elif e.response.status_code == 401:
                raise RentcastAPIError(f"Invalid API key: {e.response.text}")
            elif e.response.status_code == 403:
                raise RentcastAPIError(f"Access forbidden: {e.response.text}")
            else:
                raise RentcastAPIError(f"API request failed: {e.response.status_code} {e.response.text}")
                
        except httpx.RequestError as e:
            logger.error("Network error during API request", error=str(e))
            raise RentcastAPIError(f"Network error: {str(e)}")
            
    async def _cached_request(self, endpoint: str, params: Dict[str, Any], 
                            force_refresh: bool = False) -> tuple[Dict[str, Any], bool, Optional[float]]:
        """Make cached request to Rentcast API."""
        cache_key = self._create_cache_key(endpoint, params)
        
        # Check cache first unless force refresh
        if not force_refresh:
            cached_entry = await db_manager.get_cache_entry(cache_key)
            if cached_entry:
                # Calculate cache age in hours
                cache_age = (cached_entry.last_accessed - cached_entry.created_at).total_seconds() / 3600
                
                # Track cache hit
                await db_manager.track_api_usage(
                    endpoint=endpoint,
                    request_data=params,
                    response_status=200,
                    cost_estimate=Decimal('0.0'),
                    cache_hit=True
                )
                
                logger.info("Cache hit", cache_key=cache_key, age_hours=cache_age)
                return cached_entry.response_data, True, cache_age
                
        # Check rate limits
        is_allowed, remaining = await db_manager.check_rate_limit("api", endpoint)
        if not is_allowed:
            logger.warning("Rate limit exceeded", endpoint=endpoint, remaining=remaining)
            raise RateLimitExceeded(f"Rate limit exceeded for {endpoint}. Try again later.")
            
        # Make API request
        response_data = await self._make_request(endpoint, params)
        
        # Cache the response
        await db_manager.set_cache_entry(cache_key, response_data)
        
        logger.info("API request completed and cached", endpoint=endpoint, cache_key=cache_key)
        return response_data, False, None
        
    # Property Records
    async def get_property_records(self, address: Optional[str] = None, city: Optional[str] = None,
                                 state: Optional[str] = None, zipCode: Optional[str] = None,
                                 limit: Optional[int] = None, offset: Optional[int] = None,
                                 force_refresh: bool = False) -> tuple[List[PropertyRecord], bool, Optional[float]]:
        """Get property records."""
        params = {}
        if address:
            params["address"] = address
        if city:
            params["city"] = city
        if state:
            params["state"] = state
        if zipCode:
            params["zipCode"] = zipCode
        if limit:
            params["limit"] = min(limit, 500)  # API max is 500
        if offset:
            params["offset"] = offset
            
        response_data, is_cached, cache_age = await self._cached_request(
            "property-records", params, force_refresh
        )
        
        properties = [PropertyRecord(**prop) for prop in response_data.get("properties", [])]
        return properties, is_cached, cache_age
        
    async def get_random_property_records(self, limit: Optional[int] = None,
                                        force_refresh: bool = False) -> tuple[List[PropertyRecord], bool, Optional[float]]:
        """Get random property records."""
        params = {}
        if limit:
            params["limit"] = min(limit, 500)
            
        response_data, is_cached, cache_age = await self._cached_request(
            "property-records/random", params, force_refresh
        )
        
        properties = [PropertyRecord(**prop) for prop in response_data.get("properties", [])]
        return properties, is_cached, cache_age
        
    async def get_property_record(self, property_id: str, 
                                force_refresh: bool = False) -> tuple[Optional[PropertyRecord], bool, Optional[float]]:
        """Get specific property record by ID."""
        response_data, is_cached, cache_age = await self._cached_request(
            f"property-record/{property_id}", {}, force_refresh
        )
        
        property_data = response_data.get("property")
        property_record = PropertyRecord(**property_data) if property_data else None
        return property_record, is_cached, cache_age
        
    # Value Estimates
    async def get_value_estimate(self, address: str, 
                               force_refresh: bool = False) -> tuple[Optional[ValueEstimate], bool, Optional[float]]:
        """Get property value estimate."""
        params = {"address": address}
        
        response_data, is_cached, cache_age = await self._cached_request(
            "value-estimate", params, force_refresh
        )
        
        estimate = ValueEstimate(**response_data) if response_data else None
        return estimate, is_cached, cache_age
        
    # Rent Estimates
    async def get_rent_estimate(self, address: str, propertyType: Optional[str] = None,
                              bedrooms: Optional[int] = None, bathrooms: Optional[float] = None,
                              squareFootage: Optional[int] = None,
                              force_refresh: bool = False) -> tuple[Optional[RentEstimate], bool, Optional[float]]:
        """Get rent estimate."""
        params = {"address": address}
        if propertyType:
            params["propertyType"] = propertyType
        if bedrooms:
            params["bedrooms"] = bedrooms
        if bathrooms:
            params["bathrooms"] = bathrooms
        if squareFootage:
            params["squareFootage"] = squareFootage
            
        response_data, is_cached, cache_age = await self._cached_request(
            "rent-estimate-long-term", params, force_refresh
        )
        
        estimate = RentEstimate(**response_data) if response_data else None
        return estimate, is_cached, cache_age
        
    # Sale Listings
    async def get_sale_listings(self, address: Optional[str] = None, city: Optional[str] = None,
                              state: Optional[str] = None, zipCode: Optional[str] = None,
                              limit: Optional[int] = None, offset: Optional[int] = None,
                              force_refresh: bool = False) -> tuple[List[SaleListing], bool, Optional[float]]:
        """Get sale listings."""
        params = {}
        if address:
            params["address"] = address
        if city:
            params["city"] = city
        if state:
            params["state"] = state
        if zipCode:
            params["zipCode"] = zipCode
        if limit:
            params["limit"] = min(limit, 500)
        if offset:
            params["offset"] = offset
            
        response_data, is_cached, cache_age = await self._cached_request(
            "sale-listings", params, force_refresh
        )
        
        listings = [SaleListing(**listing) for listing in response_data.get("listings", [])]
        return listings, is_cached, cache_age
        
    async def get_sale_listing(self, listing_id: str,
                             force_refresh: bool = False) -> tuple[Optional[SaleListing], bool, Optional[float]]:
        """Get specific sale listing by ID."""
        response_data, is_cached, cache_age = await self._cached_request(
            f"sale-listing/{listing_id}", {}, force_refresh
        )
        
        listing_data = response_data.get("listing")
        listing = SaleListing(**listing_data) if listing_data else None
        return listing, is_cached, cache_age
        
    # Rental Listings
    async def get_rental_listings(self, address: Optional[str] = None, city: Optional[str] = None,
                                state: Optional[str] = None, zipCode: Optional[str] = None,
                                limit: Optional[int] = None, offset: Optional[int] = None,
                                force_refresh: bool = False) -> tuple[List[RentalListing], bool, Optional[float]]:
        """Get rental listings."""
        params = {}
        if address:
            params["address"] = address
        if city:
            params["city"] = city
        if state:
            params["state"] = state
        if zipCode:
            params["zipCode"] = zipCode
        if limit:
            params["limit"] = min(limit, 500)
        if offset:
            params["offset"] = offset
            
        response_data, is_cached, cache_age = await self._cached_request(
            "rental-listings-long-term", params, force_refresh
        )
        
        listings = [RentalListing(**listing) for listing in response_data.get("listings", [])]
        return listings, is_cached, cache_age
        
    async def get_rental_listing(self, listing_id: str,
                               force_refresh: bool = False) -> tuple[Optional[RentalListing], bool, Optional[float]]:
        """Get specific rental listing by ID."""
        response_data, is_cached, cache_age = await self._cached_request(
            f"rental-listing-long-term/{listing_id}", {}, force_refresh
        )
        
        listing_data = response_data.get("listing")
        listing = RentalListing(**listing_data) if listing_data else None
        return listing, is_cached, cache_age
        
    # Market Statistics
    async def get_market_statistics(self, city: Optional[str] = None, state: Optional[str] = None,
                                  zipCode: Optional[str] = None,
                                  force_refresh: bool = False) -> tuple[Optional[MarketStatistics], bool, Optional[float]]:
        """Get market statistics."""
        params = {}
        if city:
            params["city"] = city
        if state:
            params["state"] = state
        if zipCode:
            params["zipCode"] = zipCode
            
        response_data, is_cached, cache_age = await self._cached_request(
            "market-statistics", params, force_refresh
        )
        
        stats = MarketStatistics(**response_data) if response_data else None
        return stats, is_cached, cache_age


# Global client instance (will be initialized in server)
rentcast_client: Optional[RentcastClient] = None


def get_rentcast_client() -> RentcastClient:
    """Get Rentcast client instance."""
    global rentcast_client
    if not rentcast_client:
        rentcast_client = RentcastClient()
    return rentcast_client