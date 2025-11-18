# mcrentcast Installation Guide

This guide provides detailed installation instructions for the mcrentcast MCP server for different use cases and environments.

## Prerequisites

Before installing mcrentcast, ensure you have:

- **Python 3.13+** - Required for running the server
- **Claude Desktop** - For MCP integration
- **uv package manager** - For Python dependency management
- **Rentcast API key** (optional for testing with mock API)

### Installing Prerequisites

#### Install uv (Python package manager)
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

#### Get a Rentcast API Key
1. Sign up at [Rentcast](https://rentcast.io/)
2. Navigate to your API dashboard
3. Generate an API key
4. Note the key for later configuration

## Installation Methods

### Method 1: Production Installation (Recommended)

This method installs the latest stable version directly from the git repository.

#### Step 1: Install with Claude MCP
```bash
claude mcp add mcrentcast -- uvx --from git+https://git.supported.systems/MCP/mcrentcast.git mcrentcast
```

#### Step 2: Configure API Key

Choose one of these methods to set your API key:

**Option A: Environment Variable**
```bash
export RENTCAST_API_KEY=your_actual_api_key
```

**Option B: .env File (Recommended)**
```bash
# Create .env file in your preferred directory
echo "RENTCAST_API_KEY=your_actual_api_key" > ~/.mcrentcast.env
```

**Option C: Set via Claude**
After installation, you can also set the API key through Claude:
```
User: Set my Rentcast API key to: your_actual_api_key

Claude: I'll set your Rentcast API key for this session.
[Uses set_api_key tool]
```

#### Step 3: Verify Installation

Test the installation by asking Claude to search for properties:
```
User: Search for properties in Austin, Texas

Claude: I'll search for properties in Austin, Texas using the Rentcast API.
[If successful, you'll see property results]
```

### Method 2: Development Installation

For development, testing, or customization:

#### Step 1: Clone Repository
```bash
git clone https://git.supported.systems/MCP/mcrentcast.git
cd mcrentcast
```

#### Step 2: Run Installation Script
```bash
# Make script executable
chmod +x install.sh

# Run installation
./install.sh
```

The installation script will:
- Install Python dependencies with uv
- Create data directory
- Initialize database
- Create example .env file

#### Step 3: Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit with your API key
nano .env
```

Set these essential variables in `.env`:
```env
RENTCAST_API_KEY=your_actual_api_key
USE_MOCK_API=false
CACHE_TTL_HOURS=24
DAILY_API_LIMIT=100
MONTHLY_API_LIMIT=1000
```

#### Step 4: Add to Claude
```bash
# Add development version to Claude
claude mcp add mcrentcast -- uvx --from . mcrentcast
```

### Method 3: Testing with Mock API

To test without consuming API credits:

#### Step 1: Install (Production or Development)
Follow either Method 1 or 2 above.

#### Step 2: Configure for Mock API
```bash
# Add to Claude with mock API configuration
claude mcp add mcrentcast-test -- uvx --from git+https://git.supported.systems/MCP/mcrentcast.git mcrentcast \
  -e USE_MOCK_API=true \
  -e RENTCAST_API_KEY=test_key_basic
```

#### Available Test Keys
| Key | Daily Limit | Use Case |
|-----|-------------|----------|
| `test_key_basic` | 100 | Standard testing |
| `test_key_free_tier` | 50 | Free tier simulation |
| `test_key_pro` | 1,000 | High-volume testing |
| `test_key_enterprise` | 10,000 | Unlimited testing |
| `test_key_rate_limited` | 1 | Rate limit testing |

### Method 4: Docker Installation

For containerized deployment:

#### Step 1: Clone and Configure
```bash
git clone https://git.supported.systems/MCP/mcrentcast.git
cd mcrentcast

# Configure environment
cp .env.example .env
nano .env  # Set your API key
```

#### Step 2: Start Services
```bash
# Development mode with hot-reload
make dev

# Production mode
make prod

# Mock API mode for testing
make test-mock
```

## Environment Configuration

### Essential Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `RENTCAST_API_KEY` | Yes* | - | Your Rentcast API key |
| `USE_MOCK_API` | No | `false` | Use mock API for testing |
| `CACHE_TTL_HOURS` | No | `24` | Cache expiration time |
| `DAILY_API_LIMIT` | No | `100` | Daily request limit |
| `MONTHLY_API_LIMIT` | No | `1000` | Monthly request limit |
| `REQUESTS_PER_MINUTE` | No | `3` | Rate limit per minute |

*Not required when using mock API (`USE_MOCK_API=true`)

### Advanced Configuration

```env
# Database settings
DATABASE_URL=sqlite:///./data/mcrentcast.db

# Logging
LOG_LEVEL=INFO
DEBUG=false

# Mock API settings (for testing)
USE_MOCK_API=false
MOCK_API_URL=http://localhost:8001/v1

# Cache settings
MAX_CACHE_SIZE_MB=100
CACHE_CLEANUP_INTERVAL_HOURS=6

# Rate limiting
EXPONENTIAL_BACKOFF_ENABLED=true
MAX_RETRY_ATTEMPTS=3
```

## Verification and Testing

### Verify Installation
```bash
# Check if server can start (development only)
cd /path/to/mcrentcast
uv run mcrentcast

# Test API connectivity
uv run python -c "
from src.mcrentcast.config import settings
print('API Key configured:', bool(settings.rentcast_api_key))
"
```

### Test with Claude

1. **Basic Test**
   ```
   User: What are the current API limits for mcrentcast?
   
   Claude: I'll check the current API limits.
   [Shows daily/monthly limits and current usage]
   ```

2. **Property Search Test**
   ```
   User: Find 3 properties in San Francisco, CA
   
   Claude: I'll search for properties in San Francisco.
   [Shows property listings with addresses, prices, details]
   ```

3. **Value Estimation Test**
   ```
   User: What's the estimated value of 123 Main St, Austin, TX?
   
   Claude: I'll get a value estimate for that property.
   [Shows estimated price range and comparables]
   ```

### Test Cache and Performance
```
User: Search for properties in Austin, TX (this should be cached on subsequent calls)

User: Get cache statistics to see hit/miss rates

User: Get usage statistics for the last 30 days
```

## Troubleshooting Installation Issues

### Common Installation Problems

#### 1. Python Version Issues
```bash
# Check Python version
python3 --version
python3.13 --version

# If Python 3.13 not available, install it
# Ubuntu/Debian:
sudo apt update
sudo apt install python3.13

# macOS with Homebrew:
brew install python@3.13
```

#### 2. uv Installation Issues
```bash
# Reinstall uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart shell or reload PATH
source ~/.bashrc  # or ~/.zshrc
```

#### 3. Permission Issues
```bash
# Fix directory permissions
chmod -R 755 /path/to/mcrentcast

# Create data directory with correct permissions
mkdir -p data
chmod 755 data
```

#### 4. Database Initialization Issues
```bash
# Remove existing database and recreate
rm -f data/mcrentcast.db

# Reinitialize
uv run python -c "
from src.mcrentcast.database import db_manager
db_manager.create_tables()
print('Database initialized successfully')
"
```

#### 5. Claude MCP Integration Issues

**Server Not Found:**
```bash
# Check if server is registered
claude mcp list

# Remove and re-add if needed
claude mcp remove mcrentcast
claude mcp add mcrentcast -- uvx --from git+https://git.supported.systems/MCP/mcrentcast.git mcrentcast
```

**API Key Not Working:**
```bash
# Test API key directly
curl -H "X-Api-Key: your_key" https://api.rentcast.io/v1/properties

# Use mock API for testing
claude mcp add mcrentcast-test -- uvx --from git+https://git.supported.systems/MCP/mcrentcast.git mcrentcast \
  -e USE_MOCK_API=true \
  -e RENTCAST_API_KEY=test_key_basic
```

### Debugging Steps

1. **Check Installation Status**
   ```bash
   # Verify uv installation
   uv --version
   
   # Check Python version
   uv run python --version
   
   # Verify dependencies
   uv run python -c "import mcrentcast; print('Import successful')"
   ```

2. **Test API Connectivity**
   ```bash
   # Test with mock API
   USE_MOCK_API=true uv run python scripts/test_mock_api.py
   
   # Test with real API (requires valid key)
   RENTCAST_API_KEY=your_key uv run python scripts/test_mock_api.py
   ```

3. **Check Logs**
   ```bash
   # Enable debug logging
   DEBUG=true LOG_LEVEL=DEBUG uv run mcrentcast
   ```

4. **Database Verification**
   ```bash
   # Check database file exists and is writable
   ls -la data/mcrentcast.db
   
   # Test database connection
   uv run python -c "
   from src.mcrentcast.database import db_manager
   import asyncio
   async def test_db():
       stats = await db_manager.get_cache_stats()
       print('Database connection successful')
   asyncio.run(test_db())
   "
   ```

## Environment-Specific Installation Notes

### Windows
```powershell
# Install uv for Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Use PowerShell for environment variables
$env:RENTCAST_API_KEY = "your_actual_api_key"
```

### macOS
```bash
# Install uv via Homebrew (alternative)
brew install uv

# Set environment variable permanently
echo 'export RENTCAST_API_KEY=your_actual_api_key' >> ~/.zshrc
source ~/.zshrc
```

### Linux
```bash
# Install Python 3.13 on older distributions
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.13 python3.13-venv

# Set environment variable permanently
echo 'export RENTCAST_API_KEY=your_actual_api_key' >> ~/.bashrc
source ~/.bashrc
```

## Upgrading

### Upgrade Production Installation
```bash
# Remove old version
claude mcp remove mcrentcast

# Install latest version
claude mcp add mcrentcast -- uvx --from git+https://git.supported.systems/MCP/mcrentcast.git mcrentcast
```

### Upgrade Development Installation
```bash
cd /path/to/mcrentcast

# Pull latest changes
git pull origin main

# Update dependencies
uv sync

# Reinitialize if needed
./install.sh
```

## Uninstallation

### Remove from Claude
```bash
# Remove MCP server
claude mcp remove mcrentcast

# Also remove test server if installed
claude mcp remove mcrentcast-test
```

### Clean Development Installation
```bash
# Remove cloned repository
rm -rf /path/to/mcrentcast

# Remove environment variables
# Edit ~/.bashrc or ~/.zshrc to remove RENTCAST_API_KEY export
```

## Getting Help

If you encounter issues during installation:

1. **Check the documentation**
   - [README.md](../README.md) - Overview and quick start
   - [USAGE.md](./USAGE.md) - Usage examples
   - [Mock API Guide](./mock-api.md) - Testing without credits

2. **Enable debug logging**
   ```bash
   DEBUG=true LOG_LEVEL=DEBUG uv run mcrentcast
   ```

3. **Test with mock API**
   ```bash
   USE_MOCK_API=true uv run python scripts/test_mock_api.py
   ```

4. **Create an issue**
   - Visit the [GitHub repository](https://git.supported.systems/MCP/mcrentcast)
   - Include error messages, environment details, and steps to reproduce

5. **Check system requirements**
   - Python 3.13+
   - Sufficient disk space (100MB minimum)
   - Internet connection for API calls
   - Write permissions for data directory