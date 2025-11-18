# mcrentcast - Rentcast MCP Server

<div align="center">
  <img src="https://app.rentcast.io/assets/svg/brand/logo.svg" alt="Rentcast Logo" width="200"/>
  
  <h3>MCP Server for Rentcast API</h3>
  <p>Intelligent property data access with advanced caching, rate limiting, and cost management</p>
  
  <p>
    <a href="https://www.rentcast.io/api">API Home</a> •
    <a href="https://developers.rentcast.io/reference/introduction">Documentation</a> •
    <a href="https://git.supported.systems/MCP/mcrentcast">Repository</a>
  </p>
</div>

---

> **The Rentcast real estate and property data API provides on-demand access to 140+ million property records, owner details, home value and rent estimates, comparable properties, active sale and rental listings, as well as aggregate real estate market data.**

A Model Context Protocol (MCP) server that provides intelligent access to the Rentcast API with advanced caching, rate limiting, and cost management features.

## 🌟 Features

- **🏠 Complete Rentcast API Integration**: Access all major Rentcast endpoints for property data, valuations, listings, and market statistics
- **💾 Intelligent Caching**: Automatic response caching with hit/miss tracking, 24-hour default TTL, and configurable cache management  
- **🛡️ Advanced Rate Limiting**: Multi-layer protection with daily/monthly/per-minute limits, exponential backoff, and automatic retry logic
- **💰 Smart Cost Management**: Real-time usage tracking, cost estimation, and user confirmation for expensive operations
- **🧪 Comprehensive Mock API**: Full-featured testing environment with multiple test keys and realistic data generation
- **✨ Seamless MCP Integration**: Native Claude Desktop integration with 13 specialized tools for real estate analysis
- **🐳 Production Ready**: Complete Docker setup with development/production modes and reverse proxy configuration
- **📊 Advanced Analytics**: Detailed usage statistics, cache performance metrics, and cost tracking with historical data
- **🔒 Security & Reliability**: Secure API key management, error handling, and graceful fallbacks to cached data

## 📋 Table of Contents

- [Quick Start](#quick-start)  
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [MCP Tools](#mcp-tools)
- [Documentation](#documentation)
- [Development](#development)
- [Testing](#testing)
- [Support](#support)

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager
- Rentcast API key (or use mock mode for testing)

### Production Installation

The easiest way to install and use mcrentcast with Claude:

```bash
# Install directly from git (recommended for production)
claude mcp add mcrentcast -- uvx --from git+https://git.supported.systems/MCP/mcrentcast.git mcrentcast
```

**Important**: After installation, you need to set your Rentcast API key in your environment or `.env` file:

```bash
# Set your API key in your environment
export RENTCAST_API_KEY=your_actual_api_key

# OR create a .env file in your current directory
echo "RENTCAST_API_KEY=your_actual_api_key" > .env
```

### Development Installation

For development or local installation:

```bash
# Clone the repository
git clone https://git.supported.systems/MCP/mcrentcast.git
cd mcrentcast

# Run the installation script
./install.sh

# Set your API key in the .env file
echo "RENTCAST_API_KEY=your_actual_api_key" >> .env

# Add to Claude for development
claude mcp add mcrentcast -- uvx --from . mcrentcast
```

## 📦 Installation

### Method 1: Automated Installation

```bash
./install.sh
```

This script will:
- Install Python dependencies with uv
- Create necessary directories
- Initialize the database
- Set up configuration files

### Method 2: Manual Installation

```bash
# Install dependencies
uv sync

# Create data directory
mkdir -p data

# Initialize database
uv run python -c "from mcrentcast.database import db_manager; db_manager.create_tables()"

# Copy environment configuration
cp .env.example .env

# Edit .env with your API key
nano .env
```

### Using the Installed Scripts

After installation, you can use the provided command-line scripts:

```bash
# Run the MCP server (for Claude integration)
uv run mcrentcast

# Run the mock API server (for testing)
uv run mcrentcast-mock-api
```

### Method 3: Docker

```bash
# Start with Docker Compose
make dev  # Development mode
make prod # Production mode
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with your configuration:

```env
# Rentcast API Configuration
RENTCAST_API_KEY=your_api_key_here
RENTCAST_BASE_URL=https://api.rentcast.io/v1

# Mock API Settings (for testing)
USE_MOCK_API=false  # Set to true for testing without credits
MOCK_API_URL=http://localhost:8001/v1

# Rate Limiting
DAILY_API_LIMIT=100
MONTHLY_API_LIMIT=1000
REQUESTS_PER_MINUTE=3

# Cache Settings
CACHE_TTL_HOURS=24
MAX_CACHE_SIZE_MB=100

# Database
DATABASE_URL=sqlite:///./data/mcrentcast.db
```

### Claude Desktop Configuration

#### Option 1: Using `claude mcp add` with uvx (Recommended)

```bash
# Navigate to the project directory
cd /path/to/mcrentcast

# Make sure your API key is set in .env file
# Edit .env and set RENTCAST_API_KEY=your_actual_key

# For production (install directly from git)
claude mcp add mcrentcast -- uvx --from git+https://git.supported.systems/MCP/mcrentcast.git mcrentcast

# For development (from cloned repository)
claude mcp add mcrentcast -- uvx --from . mcrentcast

# Alternative: use the mcp.json configuration (development only)
claude mcp add mcrentcast .

# For testing with mock API (no real API key needed)
claude mcp add mcrentcast-test -- uvx --from git+https://git.supported.systems/MCP/mcrentcast.git mcrentcast \
  -e USE_MOCK_API=true \
  -e RENTCAST_API_KEY=test_key_basic

# To use different scopes
claude mcp add --scope user mcrentcast -- uvx --from . mcrentcast  # Available to all projects
claude mcp add --scope local mcrentcast .  # Only for current project (default)
```

#### Option 2: Manual Configuration

Add to your Claude MCP configuration file (usually `~/.config/claude/mcp.json` or similar):

```json
{
  "servers": {
    "mcrentcast": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcrentcast.server"],
      "cwd": "/path/to/mcrentcast",
      "env": {
        "PYTHONPATH": "/path/to/mcrentcast/src:${PYTHONPATH}",
        "RENTCAST_API_KEY": "your_api_key_here",
        "USE_MOCK_API": "false"
      }
    }
  }
}
```

Note: The server uses the `mcp.json` file in the project root for configuration when using `claude mcp add`.

## 🔧 Usage

### Natural Language Interface with Claude

Once installed, interact with the Rentcast API through natural language:

```
User: Find 5 properties for sale in Austin, Texas under $500,000

Claude: I'll search for properties for sale in Austin, Texas.
[Uses search_sale_listings tool]

Found 8 sale listings (fresh data):
- 123 Oak St: $450,000, 3BR/2BA, 1,800 sq ft
- 456 Pine Ave: $485,000, 4BR/2.5BA, 2,100 sq ft
- 789 Elm Dr: $425,000, 3BR/2BA, 1,650 sq ft
...
```

```  
User: What's the estimated rental income for 123 Main St, Denver, CO?

Claude: I'll get the rental estimate for that property.
[Uses get_rent_estimate tool]

Rent estimate: $2,850/month (fresh data)
- Estimated range: $2,565 - $3,135
- Market comparison: 8% above area median
- Based on 3 comparable rentals nearby
```

```
User: Show me the current real estate market statistics for Miami, FL

Claude: I'll get the current market statistics for Miami.
[Uses get_market_statistics tool]

Miami, FL Market Statistics (from cache, age: 3.2 hours):
- Median Sale Price: $485,000 (+7.2% YoY)
- Median Rent: $2,650/month (+11.8% YoY)
- Average Days on Market: 45 days
- Active Inventory: 3,247 properties
- Price per Square Foot: $285
```

### Advanced Analysis Examples

```
User: I'm considering an investment property in Nashville. Analyze the market and find potential deals.

Claude: I'll perform a comprehensive Nashville investment analysis.
[Uses multiple tools: get_market_statistics, search_sale_listings, search_rental_listings]

Nashville Investment Analysis:
✓ Market Growth: +8.2% annual appreciation 
✓ Rental Demand: Strong (+12.1% rent growth)
✓ Investment Properties Found: 12 properties with 6%+ yield potential
✓ Market Liquidity: Good (28 days average DOM)

Top Investment Opportunities:
1. 234 Music Row: $385K, potential $2,400/month (7.5% yield)
2. 567 Broadway St: $420K, potential $2,650/month (7.6% yield)
...
```

## 🛠️ MCP Tools

The server provides 13 MCP tools:

### Property Data Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `search_properties` | Search for property records | `city`, `state`, `zipCode`, `limit`, `offset` |
| `get_property` | Get specific property details | `property_id` |
| `get_value_estimate` | Get property value estimate | `address` |
| `get_rent_estimate` | Get rental price estimate | `address`, `bedrooms`, `bathrooms`, `squareFootage` |

### Listing Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `search_sale_listings` | Find properties for sale | `city`, `state`, `zipCode`, `limit` |
| `search_rental_listings` | Find rental properties | `city`, `state`, `zipCode`, `limit` |
| `get_market_statistics` | Get market analysis data | `city`, `state`, `zipCode` |

### Management Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `set_api_key` | Configure Rentcast API key | `api_key` |
| `expire_cache` | Expire cache entries | `cache_key`, `all` |
| `get_cache_stats` | View cache performance | - |
| `get_usage_stats` | Track API usage and costs | `days` |
| `set_api_limits` | Configure rate limits | `daily_limit`, `monthly_limit`, `requests_per_minute` |
| `get_api_limits` | View current limits | - |

## 🧪 Mock API

The project includes a complete mock of the Rentcast API for testing without consuming API credits:

### Starting Mock API

#### Using the Script Command

```bash
# Start mock API server (runs on port 8001)
uv run mcrentcast-mock-api
```

#### Using Make Commands

```bash
# Start mock API only
make mock-api

# Start full stack with mock API
make test-mock
```

### Test API Keys

The mock API includes predefined test keys with different rate limits:

| Key | Daily Limit | Use Case |
|-----|-------------|----------|
| `test_key_free_tier` | 50 | Testing free tier |
| `test_key_basic` | 100 | Standard testing |
| `test_key_pro` | 1,000 | High-volume testing |
| `test_key_enterprise` | 10,000 | Unlimited testing |
| `test_key_rate_limited` | 1 | Rate limit testing |

### Using Mock Mode

To use the mock API instead of the real Rentcast API, set in `.env`:

```env
USE_MOCK_API=true
RENTCAST_API_KEY=test_key_basic
MOCK_API_URL=http://localhost:8001/v1
```

Then run the MCP server normally:

```bash
uv run mcrentcast
```

## 🔬 Development

### Project Structure

```
mcrentcast/
├── src/mcrentcast/       # Core MCP server code
│   ├── server.py         # FastMCP server implementation
│   ├── rentcast_client.py # Rentcast API client
│   ├── database.py       # Database management
│   ├── models.py         # Data models
│   ├── config.py         # Configuration
│   └── mock_api.py       # Mock API server
├── tests/                # Test suite
├── docs/                 # Documentation
├── scripts/              # Utility scripts
├── docker-compose.yml    # Docker configuration
├── Makefile             # Build automation
└── pyproject.toml       # Python dependencies
```

### Running Locally

```bash
# Install development dependencies
uv sync --dev

# Run tests
uv run pytest

# Run with mock API
USE_MOCK_API=true uv run python -m mcrentcast.server

# Run linting
uv run ruff check src/

# Format code
uv run black src/ tests/
```

### Docker Development

```bash
# Build images
make build

# Start development environment
make dev

# View logs
make logs

# Run tests in container
make test

# Access shell
make shell
```

## 🧪 Testing

### Unit Tests

```bash
uv run pytest tests/ -v
```

### Integration Tests

```bash
# Start mock API
make mock-api

# Run integration tests
uv run pytest tests/test_integration.py -v
```

### Test Coverage

```bash
uv run pytest --cov=src --cov-report=html
# View report at htmlcov/index.html
```

## 📚 Documentation

### Comprehensive Guides

| Document | Description |
|----------|-------------|
| **[Installation Guide](docs/INSTALLATION.md)** | Detailed installation instructions for all scenarios |
| **[Usage Guide](docs/USAGE.md)** | Complete examples for all 13 tools with best practices |
| **[Mock API Guide](docs/mock-api.md)** | Testing without API credits using realistic mock data |
| **[Claude Setup](docs/claude-setup.md)** | MCP integration and configuration |
| **[API Reference](docs/api-reference.md)** | Technical API documentation |

### Quick Reference

#### Essential Commands
```bash
# Production installation
claude mcp add mcrentcast -- uvx --from git+https://git.supported.systems/MCP/mcrentcast.git mcrentcast

# Test with mock API (no credits required)
claude mcp add mcrentcast-test -- uvx --from git+https://git.supported.systems/MCP/mcrentcast.git mcrentcast \
  -e USE_MOCK_API=true -e RENTCAST_API_KEY=test_key_basic

# Check installation
claude mcp list | grep mcrentcast
```

#### Key Features
- **13 MCP Tools**: Complete Rentcast API coverage
- **Smart Caching**: 24-hour default TTL with intelligent cache management
- **Cost Control**: Usage tracking, rate limiting, and user confirmations
- **Testing Support**: Full mock API with realistic data
- **Production Ready**: Docker support, security, and reliability features

### API Coverage

The server provides complete access to Rentcast API endpoints:

| Category | Endpoints | Tools |
|----------|-----------|-------|
| **Property Data** | Property records, specific properties | `search_properties`, `get_property` |
| **Valuations** | Value and rent estimates | `get_value_estimate`, `get_rent_estimate` |
| **Listings** | Sale and rental listings | `search_sale_listings`, `search_rental_listings` |
| **Market Data** | Statistics and trends | `get_market_statistics` |
| **Management** | Configuration and monitoring | 6 management tools |

### 💰 API Pricing & Cost Management

#### Rentcast API Pricing
Rentcast offers several pricing tiers for API access. See [official pricing](https://www.rentcast.io/api#api-pricing) for current rates:
- **Free Tier**: Limited requests for testing
- **Basic**: $99/month for 1,000 requests
- **Professional**: Higher volumes with bulk pricing
- **Enterprise**: Custom pricing for large-scale usage

> **Why We Cache**: Each API request costs money! Our [intelligent caching system](#-features) stores responses for 24 hours (configurable), dramatically reducing costs by serving repeated requests from cache instead of making new API calls. This can reduce API costs by 70-90% in typical usage patterns.

#### Cost Management Features
- **Automatic Cost Estimation**: Know before you spend
- **User Confirmations**: Approve expensive operations
- **Usage Tracking**: Monitor daily/monthly consumption
- **Smart Caching**: Minimize redundant API calls
- **Rate Limiting**: Prevent accidental overuse
- **Cache Analytics**: Track hit rates and savings
- **Mock API**: Unlimited testing without credits

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## 🙏 Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp) for MCP support
- Uses [Rentcast API](https://developers.rentcast.io/) for property data
- Powered by [uv](https://github.com/astral-sh/uv) for Python management

## 📞 Support

### Project Documentation
- **[Installation Guide](docs/INSTALLATION.md)**: Complete setup instructions
- **[Usage Examples](docs/USAGE.md)**: All 13 tools with real-world examples  
- **[Mock API Testing](docs/mock-api.md)**: Test without consuming credits
- **[Claude Integration](docs/claude-setup.md)**: MCP configuration help

### Rentcast API Resources
- **[API Documentation](https://developers.rentcast.io/reference/introduction)**: Official API reference
- **[API Pricing](https://www.rentcast.io/api#api-pricing)**: Current pricing tiers
- **[API Dashboard](https://app.rentcast.io)**: Manage your API keys
- **[Rentcast Support](https://www.rentcast.io/contact)**: Official support channel

### Getting Help
- **Issues**: [Create an issue](https://git.supported.systems/MCP/mcrentcast/issues) on the repository
- **Discussions**: Use GitHub discussions for questions and community support
- **Documentation**: All guides available in the `/docs` directory

### Quick Troubleshooting
```bash
# Verify installation
claude mcp list | grep mcrentcast

# Test with mock API (no API key needed)
claude mcp add mcrentcast-test -- uvx --from git+https://git.supported.systems/MCP/mcrentcast.git mcrentcast \
  -e USE_MOCK_API=true -e RENTCAST_API_KEY=test_key_basic

# Enable debug logging
DEBUG=true LOG_LEVEL=DEBUG
```

---

**Important**: This is an unofficial integration with the Rentcast API. Please ensure you comply with [Rentcast's terms of service](https://rentcast.io/terms) and API usage guidelines. The mcrentcast server provides caching and rate limiting to help you stay within usage limits and manage costs effectively.