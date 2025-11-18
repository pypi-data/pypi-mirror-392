-- Initialize mcrentcast database

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create cache table for API responses
CREATE TABLE IF NOT EXISTS api_cache (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    response_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    hit_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create rate limiting table
CREATE TABLE IF NOT EXISTS rate_limits (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    identifier VARCHAR(255) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    requests_count INTEGER DEFAULT 0,
    window_start TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(identifier, endpoint)
);

-- Create API usage tracking table
CREATE TABLE IF NOT EXISTS api_usage (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    endpoint VARCHAR(255) NOT NULL,
    request_data JSONB,
    response_status INTEGER,
    cost_estimate DECIMAL(10,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    cache_hit BOOLEAN DEFAULT FALSE
);

-- Create user confirmations table
CREATE TABLE IF NOT EXISTS user_confirmations (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    parameter_hash VARCHAR(255) UNIQUE NOT NULL,
    confirmed BOOLEAN DEFAULT FALSE,
    confirmed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create configuration table
CREATE TABLE IF NOT EXISTS configuration (
    key VARCHAR(255) PRIMARY KEY,
    value JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default configuration values
INSERT INTO configuration (key, value) VALUES
    ('daily_api_limit', '100'),
    ('monthly_api_limit', '1000'),
    ('requests_per_minute', '3'),
    ('cache_ttl_hours', '24'),
    ('max_cache_size_mb', '100')
ON CONFLICT (key) DO NOTHING;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_api_cache_cache_key ON api_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_api_cache_expires_at ON api_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_rate_limits_identifier_endpoint ON rate_limits(identifier, endpoint);
CREATE INDEX IF NOT EXISTS idx_rate_limits_window_start ON rate_limits(window_start);
CREATE INDEX IF NOT EXISTS idx_api_usage_endpoint ON api_usage(endpoint);
CREATE INDEX IF NOT EXISTS idx_api_usage_created_at ON api_usage(created_at);
CREATE INDEX IF NOT EXISTS idx_user_confirmations_parameter_hash ON user_confirmations(parameter_hash);
CREATE INDEX IF NOT EXISTS idx_user_confirmations_expires_at ON user_confirmations(expires_at);
CREATE INDEX IF NOT EXISTS idx_configuration_updated_at ON configuration(updated_at);