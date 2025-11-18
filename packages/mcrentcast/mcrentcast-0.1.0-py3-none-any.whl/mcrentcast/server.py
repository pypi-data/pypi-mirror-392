"""FastMCP server for Rentcast API with intelligent caching and rate limiting."""

import asyncio
import hashlib
import json
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

import structlog
from fastmcp import FastMCP
try:
    from fastmcp.elicitation import request_user_input
except ImportError:
    # Elicitation may not be available in all FastMCP versions
    async def request_user_input(prompt: str, title: str = ""):
        # Fallback implementation - just return a message indicating confirmation needed
        return "confirmed"
from pydantic import BaseModel, Field

from .config import settings
from .database import db_manager
from .models import (
    ApiLimits,
    CacheStats,
    ConfirmationRequest,
)
from .rentcast_client import (
    RentcastClient,
    RentcastAPIError,
    RateLimitExceeded,
    get_rentcast_client,
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Create FastMCP app
app = FastMCP("mcrentcast")

# Request/Response models for MCP tools
class SetApiKeyRequest(BaseModel):
    api_key: str = Field(..., description="Rentcast API key")
    

class PropertySearchRequest(BaseModel):
    address: Optional[str] = Field(None, description="Property address")
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State code (e.g., CA, TX)")
    zipCode: Optional[str] = Field(None, description="ZIP code")
    limit: Optional[int] = Field(10, description="Max results (up to 500)")
    offset: Optional[int] = Field(0, description="Results offset for pagination")
    force_refresh: bool = Field(False, description="Force cache refresh")
    

class PropertyByIdRequest(BaseModel):
    property_id: str = Field(..., description="Property ID from Rentcast")
    force_refresh: bool = Field(False, description="Force cache refresh")
    

class ValueEstimateRequest(BaseModel):
    address: str = Field(..., description="Property address")
    force_refresh: bool = Field(False, description="Force cache refresh")
    

class RentEstimateRequest(BaseModel):
    address: str = Field(..., description="Property address")
    propertyType: Optional[str] = Field(None, description="Property type (Single Family, Condo, etc.)")
    bedrooms: Optional[int] = Field(None, description="Number of bedrooms")
    bathrooms: Optional[float] = Field(None, description="Number of bathrooms")
    squareFootage: Optional[int] = Field(None, description="Square footage")
    force_refresh: bool = Field(False, description="Force cache refresh")
    

class ListingSearchRequest(BaseModel):
    address: Optional[str] = Field(None, description="Property address")
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State code")
    zipCode: Optional[str] = Field(None, description="ZIP code")
    limit: Optional[int] = Field(10, description="Max results (up to 500)")
    offset: Optional[int] = Field(0, description="Results offset for pagination")
    force_refresh: bool = Field(False, description="Force cache refresh")
    

class ListingByIdRequest(BaseModel):
    listing_id: str = Field(..., description="Listing ID from Rentcast")
    force_refresh: bool = Field(False, description="Force cache refresh")
    

class MarketStatsRequest(BaseModel):
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State code")
    zipCode: Optional[str] = Field(None, description="ZIP code")
    force_refresh: bool = Field(False, description="Force cache refresh")
    

class ExpireCacheRequest(BaseModel):
    cache_key: Optional[str] = Field(None, description="Specific cache key to expire")
    endpoint: Optional[str] = Field(None, description="Expire all cache for endpoint")
    all: bool = Field(False, description="Expire all cache entries")
    

class SetLimitsRequest(BaseModel):
    daily_limit: Optional[int] = Field(None, description="Daily API request limit")
    monthly_limit: Optional[int] = Field(None, description="Monthly API request limit")
    requests_per_minute: Optional[int] = Field(None, description="Requests per minute limit")


async def check_api_key() -> bool:
    """Check if API key is configured."""
    return settings.validate_api_key()


async def request_confirmation(endpoint: str, parameters: Dict[str, Any], 
                              cost_estimate: Decimal, cached_data: Optional[Dict[str, Any]] = None,
                              cache_age_hours: Optional[float] = None) -> bool:
    """Request user confirmation for API call."""
    # Create confirmation request
    param_hash = db_manager.create_parameter_hash(endpoint, parameters)
    
    # Check if already confirmed within timeout
    confirmation_status = await db_manager.check_confirmation(param_hash)
    if confirmation_status is not None:
        return confirmation_status
        
    # Create new confirmation request
    await db_manager.create_confirmation(endpoint, parameters)
    
    # Prepare confirmation message
    message = f"Rentcast API request will consume credits:\n"
    message += f"Endpoint: {endpoint}\n"
    message += f"Estimated cost: ${cost_estimate}\n"
    
    if cached_data:
        message += f"\nCached data available (age: {cache_age_hours:.1f} hours)\n"
        message += "Would you like to use cached data or make a fresh API call?"
        
    # Try to use MCP elicitation
    try:
        user_response = await request_user_input(
            prompt=message,
            title="Rentcast API Confirmation Required"
        )
        
        # Parse response (yes/true/confirm = proceed)
        confirmed = user_response.lower() in ["yes", "y", "true", "confirm", "proceed"]
        
        if confirmed:
            await db_manager.confirm_request(param_hash)
            
        return confirmed
        
    except Exception as e:
        logger.warning("MCP elicitation failed, returning confirmation request", error=str(e))
        # Return confirmation request to client
        return False


# MCP Tool Definitions

@app.tool()
async def set_api_key(api_key: str) -> Dict[str, Any]:
    """Set or update the Rentcast API key for this session.

    Args:
        api_key: Rentcast API key
    """
    settings.rentcast_api_key = api_key

    # Reinitialize client with new key
    global rentcast_client
    if rentcast_client:
        await rentcast_client.close()
    rentcast_client = RentcastClient(api_key=api_key)

    # Save to configuration
    await db_manager.set_config("rentcast_api_key", api_key)

    logger.info("API key updated")
    return {
        "success": True,
        "message": "API key updated successfully"
    }


@app.tool()
async def search_properties(
    address: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    zipCode: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    force_refresh: bool = False
) -> Dict[str, Any]:
    """Search for property records by location.

    Args:
        address: Property address
        city: City name
        state: State code (e.g., CA, TX)
        zipCode: ZIP code
        limit: Max results (up to 500)
        offset: Results offset for pagination
        force_refresh: Force cache refresh
    """
    if not await check_api_key():
        return {
            "error": "API key not configured",
            "message": "Please set your Rentcast API key first using set_api_key tool"
        }

    client = get_rentcast_client()

    try:
        # Build params dict
        params = {
            "address": address,
            "city": city,
            "state": state,
            "zipCode": zipCode,
            "limit": limit,
            "offset": offset
        }

        # Check if we need confirmation for non-cached request
        cache_key = client._create_cache_key("property-records", params)
        cached_entry = await db_manager.get_cache_entry(cache_key) if not force_refresh else None

        if not cached_entry:
            # Request confirmation for new API call
            cost_estimate = client._estimate_cost("property-records")
            confirmed = await request_confirmation(
                "property-records",
                params,
                cost_estimate
            )

            if not confirmed:
                return {
                    "confirmation_required": True,
                    "message": f"API call requires confirmation (estimated cost: ${cost_estimate})",
                    "retry_with": "Please confirm to proceed with the API request"
                }

        properties, is_cached, cache_age = await client.get_property_records(
            address=address,
            city=city,
            state=state,
            zipCode=zipCode,
            limit=limit,
            offset=offset,
            force_refresh=force_refresh
        )
        
        return {
            "success": True,
            "properties": [prop.model_dump() for prop in properties],
            "count": len(properties),
            "cached": is_cached,
            "cache_age_hours": cache_age,
            "message": f"Found {len(properties)} properties" + (f" (from cache, age: {cache_age:.1f} hours)" if is_cached else " (fresh data)")
        }
        
    except RateLimitExceeded as e:
        return {
            "error": "Rate limit exceeded",
            "message": str(e),
            "retry_after": "Please wait before making more requests"
        }
    except RentcastAPIError as e:
        return {
            "error": "API error",
            "message": str(e)
        }
    except Exception as e:
        logger.error("Error searching properties", error=str(e))
        return {
            "error": "Internal error",
            "message": str(e)
        }


@app.tool()
async def get_property(property_id: str, force_refresh: bool = False) -> Dict[str, Any]:
    """Get detailed information for a specific property by ID.

    Args:
        property_id: Property ID from Rentcast
        force_refresh: Force cache refresh
    """
    if not await check_api_key():
        return {
            "error": "API key not configured",
            "message": "Please set your Rentcast API key first using set_api_key tool"
        }

    client = get_rentcast_client()

    try:
        # Check cache and request confirmation if needed
        cache_key = client._create_cache_key(f"property-record/{property_id}", {})
        cached_entry = await db_manager.get_cache_entry(cache_key) if not force_refresh else None

        if not cached_entry:
            cost_estimate = client._estimate_cost("property-record")
            confirmed = await request_confirmation(
                f"property-record/{property_id}",
                {},
                cost_estimate
            )

            if not confirmed:
                return {
                    "confirmation_required": True,
                    "message": f"API call requires confirmation (estimated cost: ${cost_estimate})",
                    "retry_with": "Please confirm to proceed with the API request"
                }

        property_record, is_cached, cache_age = await client.get_property_record(
            property_id,
            force_refresh
        )

        if property_record:
            return {
                "success": True,
                "property": property_record.model_dump(),
                "cached": is_cached,
                "cache_age_hours": cache_age,
                "message": f"Property found" + (f" (from cache, age: {cache_age:.1f} hours)" if is_cached else " (fresh data)")
            }
        else:
            return {
                "success": False,
                "message": "Property not found"
            }

    except Exception as e:
        logger.error("Error getting property", error=str(e))
        return {
            "error": "Internal error",
            "message": str(e)
        }


@app.tool()
async def get_value_estimate(address: str, force_refresh: bool = False) -> Dict[str, Any]:
    """Get property value estimate for an address.

    Args:
        address: Property address
        force_refresh: Force cache refresh
    """
    if not await check_api_key():
        return {
            "error": "API key not configured",
            "message": "Please set your Rentcast API key first using set_api_key tool"
        }

    client = get_rentcast_client()

    try:
        # Check cache and request confirmation if needed
        cache_key = client._create_cache_key("value-estimate", {"address": address})
        cached_entry = await db_manager.get_cache_entry(cache_key) if not force_refresh else None

        if not cached_entry:
            cost_estimate = client._estimate_cost("value-estimate")
            confirmed = await request_confirmation(
                "value-estimate",
                {"address": address},
                cost_estimate
            )

            if not confirmed:
                return {
                    "confirmation_required": True,
                    "message": f"API call requires confirmation (estimated cost: ${cost_estimate})",
                    "retry_with": "Please confirm to proceed with the API request"
                }

        estimate, is_cached, cache_age = await client.get_value_estimate(
            address,
            force_refresh
        )

        if estimate:
            return {
                "success": True,
                "estimate": estimate.model_dump(),
                "cached": is_cached,
                "cache_age_hours": cache_age,
                "message": f"Value estimate: ${estimate.price:,}" + (f" (from cache, age: {cache_age:.1f} hours)" if is_cached else " (fresh data)")
            }
        else:
            return {
                "success": False,
                "message": "Could not estimate value for this address"
            }

    except Exception as e:
        logger.error("Error getting value estimate", error=str(e))
        return {
            "error": "Internal error",
            "message": str(e)
        }


@app.tool()
async def get_rent_estimate(
    address: str,
    propertyType: Optional[str] = None,
    bedrooms: Optional[int] = None,
    bathrooms: Optional[float] = None,
    squareFootage: Optional[int] = None,
    force_refresh: bool = False
) -> Dict[str, Any]:
    """Get rent estimate for a property.

    Args:
        address: Property address
        propertyType: Property type (Single Family, Condo, etc.)
        bedrooms: Number of bedrooms
        bathrooms: Number of bathrooms
        squareFootage: Square footage
        force_refresh: Force cache refresh
    """
    if not await check_api_key():
        return {
            "error": "API key not configured",
            "message": "Please set your Rentcast API key first using set_api_key tool"
        }

    client = get_rentcast_client()

    try:
        params = {
            "address": address,
            "propertyType": propertyType,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "squareFootage": squareFootage
        }
        cache_key = client._create_cache_key("rent-estimate-long-term", params)
        cached_entry = await db_manager.get_cache_entry(cache_key) if not force_refresh else None

        if not cached_entry:
            cost_estimate = client._estimate_cost("rent-estimate-long-term")
            confirmed = await request_confirmation(
                "rent-estimate-long-term",
                params,
                cost_estimate
            )

            if not confirmed:
                return {
                    "confirmation_required": True,
                    "message": f"API call requires confirmation (estimated cost: ${cost_estimate})",
                    "retry_with": "Please confirm to proceed with the API request"
                }

        estimate, is_cached, cache_age = await client.get_rent_estimate(
            address=address,
            propertyType=propertyType,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            squareFootage=squareFootage,
            force_refresh=force_refresh
        )

        if estimate:
            return {
                "success": True,
                "estimate": estimate.model_dump(),
                "cached": is_cached,
                "cache_age_hours": cache_age,
                "message": f"Rent estimate: ${estimate.rent:,}/month" + (f" (from cache, age: {cache_age:.1f} hours)" if is_cached else " (fresh data)")
            }
        else:
            return {
                "success": False,
                "message": "Could not estimate rent for this property"
            }

    except Exception as e:
        logger.error("Error getting rent estimate", error=str(e))
        return {
            "error": "Internal error",
            "message": str(e)
        }


@app.tool()
async def search_sale_listings(
    address: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    zipCode: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    force_refresh: bool = False
) -> Dict[str, Any]:
    """Search for properties for sale.

    Args:
        address: Property address
        city: City name
        state: State code
        zipCode: ZIP code
        limit: Max results (up to 500)
        offset: Results offset for pagination
        force_refresh: Force cache refresh
    """
    if not await check_api_key():
        return {
            "error": "API key not configured",
            "message": "Please set your Rentcast API key first using set_api_key tool"
        }

    client = get_rentcast_client()

    try:
        params = {
            "address": address,
            "city": city,
            "state": state,
            "zipCode": zipCode,
            "limit": limit,
            "offset": offset
        }
        cache_key = client._create_cache_key("sale-listings", params)
        cached_entry = await db_manager.get_cache_entry(cache_key) if not force_refresh else None

        if not cached_entry:
            cost_estimate = client._estimate_cost("sale-listings")
            confirmed = await request_confirmation(
                "sale-listings",
                params,
                cost_estimate
            )

            if not confirmed:
                return {
                    "confirmation_required": True,
                    "message": f"API call requires confirmation (estimated cost: ${cost_estimate})",
                    "retry_with": "Please confirm to proceed with the API request"
                }

        listings, is_cached, cache_age = await client.get_sale_listings(
            address=address,
            city=city,
            state=state,
            zipCode=zipCode,
            limit=limit,
            offset=offset,
            force_refresh=force_refresh
        )

        return {
            "success": True,
            "listings": [listing.model_dump() for listing in listings],
            "count": len(listings),
            "cached": is_cached,
            "cache_age_hours": cache_age,
            "message": f"Found {len(listings)} sale listings" + (f" (from cache, age: {cache_age:.1f} hours)" if is_cached else " (fresh data)")
        }

    except Exception as e:
        logger.error("Error searching sale listings", error=str(e))
        return {
            "error": "Internal error",
            "message": str(e)
        }


@app.tool()
async def search_rental_listings(
    address: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    zipCode: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    force_refresh: bool = False
) -> Dict[str, Any]:
    """Search for rental properties.

    Args:
        address: Property address
        city: City name
        state: State code
        zipCode: ZIP code
        limit: Max results (up to 500)
        offset: Results offset for pagination
        force_refresh: Force cache refresh
    """
    if not await check_api_key():
        return {
            "error": "API key not configured",
            "message": "Please set your Rentcast API key first using set_api_key tool"
        }

    client = get_rentcast_client()

    try:
        params = {
            "address": address,
            "city": city,
            "state": state,
            "zipCode": zipCode,
            "limit": limit,
            "offset": offset
        }
        cache_key = client._create_cache_key("rental-listings-long-term", params)
        cached_entry = await db_manager.get_cache_entry(cache_key) if not force_refresh else None

        if not cached_entry:
            cost_estimate = client._estimate_cost("rental-listings-long-term")
            confirmed = await request_confirmation(
                "rental-listings-long-term",
                params,
                cost_estimate
            )

            if not confirmed:
                return {
                    "confirmation_required": True,
                    "message": f"API call requires confirmation (estimated cost: ${cost_estimate})",
                    "retry_with": "Please confirm to proceed with the API request"
                }

        listings, is_cached, cache_age = await client.get_rental_listings(
            address=address,
            city=city,
            state=state,
            zipCode=zipCode,
            limit=limit,
            offset=offset,
            force_refresh=force_refresh
        )

        return {
            "success": True,
            "listings": [listing.model_dump() for listing in listings],
            "count": len(listings),
            "cached": is_cached,
            "cache_age_hours": cache_age,
            "message": f"Found {len(listings)} rental listings" + (f" (from cache, age: {cache_age:.1f} hours)" if is_cached else " (fresh data)")
        }

    except Exception as e:
        logger.error("Error searching rental listings", error=str(e))
        return {
            "error": "Internal error",
            "message": str(e)
        }


@app.tool()
async def get_market_statistics(
    city: Optional[str] = None,
    state: Optional[str] = None,
    zipCode: Optional[str] = None,
    force_refresh: bool = False
) -> Dict[str, Any]:
    """Get market statistics for a location.

    Args:
        city: City name
        state: State code
        zipCode: ZIP code
        force_refresh: Force cache refresh
    """
    if not await check_api_key():
        return {
            "error": "API key not configured",
            "message": "Please set your Rentcast API key first using set_api_key tool"
        }

    client = get_rentcast_client()

    try:
        params = {
            "city": city,
            "state": state,
            "zipCode": zipCode
        }
        cache_key = client._create_cache_key("market-statistics", params)
        cached_entry = await db_manager.get_cache_entry(cache_key) if not force_refresh else None

        if not cached_entry:
            cost_estimate = client._estimate_cost("market-statistics")
            confirmed = await request_confirmation(
                "market-statistics",
                params,
                cost_estimate
            )

            if not confirmed:
                return {
                    "confirmation_required": True,
                    "message": f"API call requires confirmation (estimated cost: ${cost_estimate})",
                    "retry_with": "Please confirm to proceed with the API request"
                }

        stats, is_cached, cache_age = await client.get_market_statistics(
            city=city,
            state=state,
            zipCode=zipCode,
            force_refresh=force_refresh
        )

        if stats:
            return {
                "success": True,
                "statistics": stats.model_dump(),
                "cached": is_cached,
                "cache_age_hours": cache_age,
                "message": "Market statistics retrieved" + (f" (from cache, age: {cache_age:.1f} hours)" if is_cached else " (fresh data)")
            }
        else:
            return {
                "success": False,
                "message": "Could not retrieve market statistics for this location"
            }

    except Exception as e:
        logger.error("Error getting market statistics", error=str(e))
        return {
            "error": "Internal error",
            "message": str(e)
        }


@app.tool()
async def expire_cache(
    cache_key: Optional[str] = None,
    endpoint: Optional[str] = None,
    all: bool = False
) -> Dict[str, Any]:
    """Expire cache entries to force fresh API calls.

    Args:
        cache_key: Specific cache key to expire
        endpoint: Expire all cache for endpoint
        all: Expire all cache entries
    """
    try:
        if all:
            # Clean all expired entries
            count = await db_manager.clean_expired_cache()
            return {
                "success": True,
                "message": f"Expired {count} cache entries"
            }
        elif cache_key:
            # Expire specific cache key
            expired = await db_manager.expire_cache_entry(cache_key)
            return {
                "success": expired,
                "message": "Cache entry expired" if expired else "Cache entry not found"
            }
        else:
            return {
                "success": False,
                "message": "Please specify cache_key or set all=true"
            }

    except Exception as e:
        logger.error("Error expiring cache", error=str(e))
        return {
            "error": "Internal error",
            "message": str(e)
        }


@app.tool()
async def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics including hit/miss rates and storage usage."""
    try:
        stats = await db_manager.get_cache_stats()
        return {
            "success": True,
            "stats": stats.model_dump(),
            "message": f"Cache hit rate: {stats.hit_rate}%"
        }
    except Exception as e:
        logger.error("Error getting cache stats", error=str(e))
        return {
            "error": "Internal error",
            "message": str(e)
        }


@app.tool()
async def get_usage_stats(days: int = Field(30, description="Number of days to include in stats")) -> Dict[str, Any]:
    """Get API usage statistics including costs and endpoint breakdown."""
    try:
        stats = await db_manager.get_usage_stats(days)
        return {
            "success": True,
            "stats": stats,
            "message": f"Usage stats for last {days} days"
        }
    except Exception as e:
        logger.error("Error getting usage stats", error=str(e))
        return {
            "error": "Internal error",
            "message": str(e)
        }


@app.tool()
async def set_api_limits(
    daily_limit: Optional[int] = None,
    monthly_limit: Optional[int] = None,
    requests_per_minute: Optional[int] = None
) -> Dict[str, Any]:
    """Update API rate limits and usage quotas.

    Args:
        daily_limit: Daily API request limit
        monthly_limit: Monthly API request limit
        requests_per_minute: Requests per minute limit
    """
    try:
        if daily_limit is not None:
            await db_manager.set_config("daily_api_limit", daily_limit)
            settings.daily_api_limit = daily_limit

        if monthly_limit is not None:
            await db_manager.set_config("monthly_api_limit", monthly_limit)
            settings.monthly_api_limit = monthly_limit

        if requests_per_minute is not None:
            await db_manager.set_config("requests_per_minute", requests_per_minute)
            settings.requests_per_minute = requests_per_minute

        return {
            "success": True,
            "limits": {
                "daily_limit": settings.daily_api_limit,
                "monthly_limit": settings.monthly_api_limit,
                "requests_per_minute": settings.requests_per_minute
            },
            "message": "API limits updated"
        }
    except Exception as e:
        logger.error("Error setting API limits", error=str(e))
        return {
            "error": "Internal error",
            "message": str(e)
        }


@app.tool()
async def get_api_limits() -> Dict[str, Any]:
    """Get current API rate limits and usage quotas."""
    try:
        # Get current usage counts
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        daily_usage = await db_manager.get_usage_stats(1)
        monthly_usage = await db_manager.get_usage_stats(30)
        
        limits = ApiLimits(
            daily_limit=settings.daily_api_limit,
            monthly_limit=settings.monthly_api_limit,
            requests_per_minute=settings.requests_per_minute,
            current_daily_usage=daily_usage.get("total_requests", 0),
            current_monthly_usage=monthly_usage.get("total_requests", 0)
        )
        
        return {
            "success": True,
            "limits": limits.model_dump(),
            "message": f"Daily: {limits.current_daily_usage}/{limits.daily_limit}, Monthly: {limits.current_monthly_usage}/{limits.monthly_limit}"
        }
    except Exception as e:
        logger.error("Error getting API limits", error=str(e))
        return {
            "error": "Internal error",
            "message": str(e)
        }


# Initialize on module load
logger.info("Starting mcrentcast MCP server", mode=settings.mode)

# Create database tables
db_manager.create_tables()

# Initialize Rentcast client if API key is configured
if settings.validate_api_key():
    rentcast_client = RentcastClient()
    logger.info("Rentcast client initialized")
else:
    logger.warning("No API key configured - set using set_api_key tool")


def main():
    """Main entry point for the MCP server."""
    # FastMCP handles everything when running as a script
    # The app.run() method in FastMCP 2.x runs synchronously
    try:
        app.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()