"""Database management for mcrentcast MCP server."""

import hashlib
import json
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

import structlog
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    create_engine,
    func,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from .config import settings
from .models import (
    ApiUsage,
    CacheEntry, 
    CacheStats,
    Configuration,
    RateLimit,
    UserConfirmation,
)

logger = structlog.get_logger()

Base = declarative_base()


class CacheEntryDB(Base):
    """Cache entry database model."""
    
    __tablename__ = "api_cache"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cache_key = Column(String(255), unique=True, nullable=False)
    response_data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    hit_count = Column(Integer, default=0)
    last_accessed = Column(DateTime(timezone=True), default=datetime.utcnow)


class RateLimitDB(Base):
    """Rate limit database model."""
    
    __tablename__ = "rate_limits"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    identifier = Column(String(255), nullable=False)
    endpoint = Column(String(255), nullable=False) 
    requests_count = Column(Integer, default=0)
    window_start = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class ApiUsageDB(Base):
    """API usage database model."""
    
    __tablename__ = "api_usage"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    endpoint = Column(String(255), nullable=False)
    request_data = Column(JSON)
    response_status = Column(Integer)
    cost_estimate = Column(Numeric(10, 4))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    cache_hit = Column(Boolean, default=False)


class UserConfirmationDB(Base):
    """User confirmation database model."""
    
    __tablename__ = "user_confirmations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    parameter_hash = Column(String(255), unique=True, nullable=False)
    confirmed = Column(Boolean, default=False)
    confirmed_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class ConfigurationDB(Base):
    """Configuration database model."""
    
    __tablename__ = "configuration"
    
    key = Column(String(255), primary_key=True)
    value = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class DatabaseManager:
    """Database manager for mcrentcast."""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or settings.database_url
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        """Create database tables."""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created")
        
    def get_session(self) -> Session:
        """Get database session."""
        return self.SessionLocal()
        
    def create_parameter_hash(self, endpoint: str, parameters: Dict[str, Any]) -> str:
        """Create hash for parameters to track confirmations."""
        data = json.dumps({"endpoint": endpoint, "parameters": parameters}, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()
        
    # Cache Management
    async def get_cache_entry(self, cache_key: str) -> Optional[CacheEntry]:
        """Get cache entry by key."""
        with self.get_session() as session:
            entry = session.query(CacheEntryDB).filter(
                CacheEntryDB.cache_key == cache_key,
                CacheEntryDB.expires_at > datetime.now(timezone.utc)
            ).first()
            
            if entry:
                # Update hit count and last accessed
                entry.hit_count += 1
                entry.last_accessed = datetime.now(timezone.utc)
                session.commit()
                
                return CacheEntry(
                    id=entry.id,
                    cache_key=entry.cache_key,
                    response_data=entry.response_data,
                    created_at=entry.created_at,
                    expires_at=entry.expires_at,
                    hit_count=entry.hit_count,
                    last_accessed=entry.last_accessed
                )
            return None
            
    async def set_cache_entry(self, cache_key: str, response_data: Dict[str, Any], ttl_hours: Optional[int] = None) -> CacheEntry:
        """Set cache entry."""
        ttl = ttl_hours or settings.cache_ttl_hours
        expires_at = datetime.now(timezone.utc) + timedelta(hours=ttl)
        
        with self.get_session() as session:
            # Remove existing entry if it exists
            session.query(CacheEntryDB).filter(CacheEntryDB.cache_key == cache_key).delete()
            
            entry = CacheEntryDB(
                cache_key=cache_key,
                response_data=response_data,
                expires_at=expires_at
            )
            session.add(entry)
            session.commit()
            session.refresh(entry)
            
            logger.info("Cache entry created", cache_key=cache_key, expires_at=expires_at)
            
            return CacheEntry(
                id=entry.id,
                cache_key=entry.cache_key,
                response_data=entry.response_data,
                created_at=entry.created_at,
                expires_at=entry.expires_at,
                hit_count=entry.hit_count,
                last_accessed=entry.last_accessed
            )
            
    async def expire_cache_entry(self, cache_key: str) -> bool:
        """Expire a specific cache entry."""
        with self.get_session() as session:
            deleted = session.query(CacheEntryDB).filter(CacheEntryDB.cache_key == cache_key).delete()
            session.commit()
            
            logger.info("Cache entry expired", cache_key=cache_key, deleted=bool(deleted))
            return bool(deleted)
            
    async def clean_expired_cache(self) -> int:
        """Clean expired cache entries."""
        with self.get_session() as session:
            count = session.query(CacheEntryDB).filter(
                CacheEntryDB.expires_at < datetime.now(timezone.utc)
            ).delete()
            session.commit()
            
            logger.info("Expired cache entries cleaned", count=count)
            return count
            
    async def get_cache_stats(self) -> CacheStats:
        """Get cache statistics."""
        with self.get_session() as session:
            total_entries = session.query(CacheEntryDB).count()
            total_hits = session.query(func.sum(CacheEntryDB.hit_count)).scalar() or 0
            total_misses = session.query(ApiUsageDB).filter(ApiUsageDB.cache_hit == False).count()
            
            # Calculate cache size (rough estimate based on JSON size)
            cache_size_mb = 0.0
            entries = session.query(CacheEntryDB).all()
            for entry in entries:
                cache_size_mb += len(json.dumps(entry.response_data).encode()) / (1024 * 1024)
                
            oldest_entry = session.query(func.min(CacheEntryDB.created_at)).scalar()
            newest_entry = session.query(func.max(CacheEntryDB.created_at)).scalar()
            
            hit_rate = (total_hits / (total_hits + total_misses) * 100) if (total_hits + total_misses) > 0 else 0.0
            
            return CacheStats(
                total_entries=total_entries,
                total_hits=total_hits,
                total_misses=total_misses,
                cache_size_mb=round(cache_size_mb, 2),
                oldest_entry=oldest_entry,
                newest_entry=newest_entry,
                hit_rate=round(hit_rate, 2)
            )
            
    # Rate Limiting
    async def check_rate_limit(self, identifier: str, endpoint: str, requests_per_minute: Optional[int] = None) -> Tuple[bool, int]:
        """Check if request is within rate limit."""
        limit = requests_per_minute or settings.requests_per_minute
        window_start = datetime.now(timezone.utc) - timedelta(minutes=1)
        
        with self.get_session() as session:
            # Clean old rate limit records
            session.query(RateLimitDB).filter(
                RateLimitDB.window_start < window_start
            ).delete()
            
            # Get current rate limit record
            rate_limit = session.query(RateLimitDB).filter(
                RateLimitDB.identifier == identifier,
                RateLimitDB.endpoint == endpoint
            ).first()
            
            if not rate_limit:
                rate_limit = RateLimitDB(
                    identifier=identifier,
                    endpoint=endpoint,
                    requests_count=1,
                    window_start=datetime.now(timezone.utc)
                )
                session.add(rate_limit)
            else:
                rate_limit.requests_count += 1
                
            session.commit()
            
            is_allowed = rate_limit.requests_count <= limit
            remaining = max(0, limit - rate_limit.requests_count)
            
            logger.info(
                "Rate limit check",
                identifier=identifier,
                endpoint=endpoint,
                count=rate_limit.requests_count,
                limit=limit,
                allowed=is_allowed
            )
            
            return is_allowed, remaining
            
    # API Usage Tracking
    async def track_api_usage(self, endpoint: str, request_data: Optional[Dict[str, Any]] = None, 
                            response_status: Optional[int] = None, cost_estimate: Optional[Decimal] = None,
                            cache_hit: bool = False) -> ApiUsage:
        """Track API usage."""
        with self.get_session() as session:
            usage = ApiUsageDB(
                endpoint=endpoint,
                request_data=request_data,
                response_status=response_status,
                cost_estimate=cost_estimate,
                cache_hit=cache_hit
            )
            session.add(usage)
            session.commit()
            session.refresh(usage)
            
            logger.info(
                "API usage tracked",
                endpoint=endpoint,
                status=response_status,
                cost=cost_estimate,
                cache_hit=cache_hit
            )
            
            return ApiUsage(
                id=usage.id,
                endpoint=usage.endpoint,
                request_data=usage.request_data,
                response_status=usage.response_status,
                cost_estimate=usage.cost_estimate,
                created_at=usage.created_at,
                cache_hit=usage.cache_hit
            )
            
    async def get_usage_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get API usage statistics."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        with self.get_session() as session:
            total_requests = session.query(ApiUsageDB).filter(
                ApiUsageDB.created_at >= cutoff_date
            ).count()
            
            cache_hits = session.query(ApiUsageDB).filter(
                ApiUsageDB.created_at >= cutoff_date,
                ApiUsageDB.cache_hit == True
            ).count()
            
            total_cost = session.query(func.sum(ApiUsageDB.cost_estimate)).filter(
                ApiUsageDB.created_at >= cutoff_date
            ).scalar() or Decimal('0.0')
            
            by_endpoint = session.query(
                ApiUsageDB.endpoint,
                func.count(ApiUsageDB.id).label('count')
            ).filter(
                ApiUsageDB.created_at >= cutoff_date
            ).group_by(ApiUsageDB.endpoint).all()
            
            return {
                "total_requests": total_requests,
                "cache_hits": cache_hits,
                "cache_misses": total_requests - cache_hits,
                "hit_rate": (cache_hits / total_requests * 100) if total_requests > 0 else 0.0,
                "total_cost": float(total_cost),
                "by_endpoint": {endpoint: count for endpoint, count in by_endpoint},
                "days": days
            }
            
    # User Confirmations
    async def create_confirmation(self, endpoint: str, parameters: Dict[str, Any]) -> str:
        """Create user confirmation request."""
        parameter_hash = self.create_parameter_hash(endpoint, parameters)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.confirmation_timeout_minutes)
        
        with self.get_session() as session:
            # Remove existing confirmation if it exists
            session.query(UserConfirmationDB).filter(
                UserConfirmationDB.parameter_hash == parameter_hash
            ).delete()
            
            confirmation = UserConfirmationDB(
                parameter_hash=parameter_hash,
                expires_at=expires_at
            )
            session.add(confirmation)
            session.commit()
            
            logger.info("User confirmation created", parameter_hash=parameter_hash, expires_at=expires_at)
            return parameter_hash
            
    async def check_confirmation(self, parameter_hash: str) -> Optional[bool]:
        """Check if user has confirmed the request."""
        with self.get_session() as session:
            confirmation = session.query(UserConfirmationDB).filter(
                UserConfirmationDB.parameter_hash == parameter_hash,
                UserConfirmationDB.expires_at > datetime.now(timezone.utc)
            ).first()
            
            if confirmation:
                return confirmation.confirmed
            return None
            
    async def confirm_request(self, parameter_hash: str) -> bool:
        """Confirm a user request."""
        with self.get_session() as session:
            confirmation = session.query(UserConfirmationDB).filter(
                UserConfirmationDB.parameter_hash == parameter_hash,
                UserConfirmationDB.expires_at > datetime.now(timezone.utc)
            ).first()
            
            if confirmation:
                confirmation.confirmed = True
                confirmation.confirmed_at = datetime.now(timezone.utc)
                session.commit()
                
                logger.info("User request confirmed", parameter_hash=parameter_hash)
                return True
            return False
            
    # Configuration Management
    async def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        with self.get_session() as session:
            config = session.query(ConfigurationDB).filter(ConfigurationDB.key == key).first()
            return config.value if config else default
            
    async def set_config(self, key: str, value: Any) -> None:
        """Set configuration value."""
        with self.get_session() as session:
            config = session.query(ConfigurationDB).filter(ConfigurationDB.key == key).first()
            if config:
                config.value = value
                config.updated_at = datetime.now(timezone.utc)
            else:
                config = ConfigurationDB(key=key, value=value)
                session.add(config)
            session.commit()
            
            logger.info("Configuration updated", key=key, value=value)


# Global database manager instance
db_manager = DatabaseManager()