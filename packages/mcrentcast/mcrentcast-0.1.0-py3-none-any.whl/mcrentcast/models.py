"""Data models for mcrentcast MCP server."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class CacheEntry(BaseModel):
    """Cache entry model."""
    
    id: UUID = Field(default_factory=uuid4)
    cache_key: str
    response_data: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    hit_count: int = 0
    last_accessed: datetime = Field(default_factory=datetime.utcnow)


class RateLimit(BaseModel):
    """Rate limit tracking model."""
    
    id: UUID = Field(default_factory=uuid4)
    identifier: str
    endpoint: str
    requests_count: int = 0
    window_start: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ApiUsage(BaseModel):
    """API usage tracking model."""
    
    id: UUID = Field(default_factory=uuid4)
    endpoint: str
    request_data: Optional[Dict[str, Any]] = None
    response_status: Optional[int] = None
    cost_estimate: Optional[Decimal] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    cache_hit: bool = False


class UserConfirmation(BaseModel):
    """User confirmation tracking model."""
    
    id: UUID = Field(default_factory=uuid4)
    parameter_hash: str
    confirmed: bool = False
    confirmed_at: Optional[datetime] = None
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Configuration(BaseModel):
    """Configuration model."""
    
    key: str
    value: Union[str, int, float, bool, Dict[str, Any]]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PropertyRecord(BaseModel):
    """Property record from Rentcast API."""
    
    id: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipCode: Optional[str] = None
    county: Optional[str] = None
    propertyType: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    squareFootage: Optional[int] = None
    lotSize: Optional[float] = None
    yearBuilt: Optional[int] = None
    lastSaleDate: Optional[str] = None
    lastSalePrice: Optional[int] = None
    zestimate: Optional[int] = None
    rentestimate: Optional[int] = None
    owner: Optional[Dict[str, Any]] = None
    taxAssessments: Optional[List[Dict[str, Any]]] = None
    features: Optional[Dict[str, Any]] = None


class ValueEstimate(BaseModel):
    """Value estimate from Rentcast API."""
    
    address: str
    price: Optional[int] = None
    priceRangeLow: Optional[int] = None
    priceRangeHigh: Optional[int] = None
    confidence: Optional[str] = None
    lastSaleDate: Optional[str] = None
    lastSalePrice: Optional[int] = None
    comparables: Optional[List[Dict[str, Any]]] = None


class RentEstimate(BaseModel):
    """Rent estimate from Rentcast API."""
    
    address: str
    rent: Optional[int] = None
    rentRangeLow: Optional[int] = None
    rentRangeHigh: Optional[int] = None
    confidence: Optional[str] = None
    comparables: Optional[List[Dict[str, Any]]] = None


class SaleListing(BaseModel):
    """Sale listing from Rentcast API."""
    
    id: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipCode: Optional[str] = None
    price: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    squareFootage: Optional[int] = None
    propertyType: Optional[str] = None
    listingDate: Optional[str] = None
    daysOnMarket: Optional[int] = None
    photos: Optional[List[str]] = None
    description: Optional[str] = None


class RentalListing(BaseModel):
    """Rental listing from Rentcast API."""
    
    id: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipCode: Optional[str] = None
    rent: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    squareFootage: Optional[int] = None
    propertyType: Optional[str] = None
    availableDate: Optional[str] = None
    pets: Optional[str] = None
    photos: Optional[List[str]] = None
    description: Optional[str] = None


class MarketStatistics(BaseModel):
    """Market statistics from Rentcast API."""
    
    city: Optional[str] = None
    state: Optional[str] = None
    zipCode: Optional[str] = None
    medianSalePrice: Optional[int] = None
    medianRent: Optional[int] = None
    averageDaysOnMarket: Optional[int] = None
    inventoryCount: Optional[int] = None
    pricePerSquareFoot: Optional[float] = None
    rentPerSquareFoot: Optional[float] = None
    appreciation: Optional[float] = None


class CacheStats(BaseModel):
    """Cache statistics response."""
    
    total_entries: int
    total_hits: int
    total_misses: int
    cache_size_mb: float
    oldest_entry: Optional[datetime] = None
    newest_entry: Optional[datetime] = None
    hit_rate: float = Field(description="Cache hit rate as percentage")


class ApiLimits(BaseModel):
    """API limits configuration."""
    
    daily_limit: int
    monthly_limit: int
    requests_per_minute: int
    current_daily_usage: int = 0
    current_monthly_usage: int = 0
    current_minute_usage: int = 0
    
    
class ConfirmationRequest(BaseModel):
    """Request requiring user confirmation."""
    
    endpoint: str
    parameters: Dict[str, Any]
    estimated_cost: Optional[Decimal] = None
    cached_data: Optional[Dict[str, Any]] = None
    cache_age_hours: Optional[float] = None
    reason: str = "API request will consume credits"