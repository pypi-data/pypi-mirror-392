# Adding mcrentcast to Claude MCP

## Quick Setup with `claude mcp add`

The easiest way to add the mcrentcast MCP server to Claude:

```bash
# 1. Navigate to the mcrentcast directory
cd /path/to/mcrentcast

# 2. Install dependencies and initialize
./install.sh

# 3. Add to Claude
claude mcp add .
```

## Manual Configuration

If you prefer manual configuration, add this to your Claude MCP config file (usually `~/.config/claude/mcp.json` or similar):

```json
{
  "servers": {
    "mcrentcast": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcrentcast.server"],
      "cwd": "/home/rpm/claude/mcrentcast",
      "env": {
        "PYTHONPATH": "/home/rpm/claude/mcrentcast/src:${PYTHONPATH}",
        "RENTCAST_API_KEY": "your_api_key_here",
        "USE_MOCK_API": "false",
        "DATABASE_URL": "sqlite:////home/rpm/claude/mcrentcast/data/mcrentcast.db"
      }
    }
  }
}
```

## Configuration Options

### Environment Variables

You can configure the server behavior through environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `RENTCAST_API_KEY` | - | Your Rentcast API key (required for real API) |
| `USE_MOCK_API` | `false` | Use mock API for testing (no credits) |
| `MOCK_API_URL` | `http://mock-rentcast-api:8001/v1` | Mock API URL |
| `CACHE_TTL_HOURS` | `24` | Cache expiration time in hours |
| `DAILY_API_LIMIT` | `100` | Daily API request limit |
| `MONTHLY_API_LIMIT` | `1000` | Monthly API request limit |
| `REQUESTS_PER_MINUTE` | `3` | Rate limit per minute |
| `DATABASE_URL` | `sqlite:///./data/mcrentcast.db` | Database connection URL |

### Testing with Mock API

To test without consuming API credits:

```json
{
  "servers": {
    "mcrentcast-mock": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcrentcast.server"],
      "cwd": "/home/rpm/claude/mcrentcast",
      "env": {
        "USE_MOCK_API": "true",
        "RENTCAST_API_KEY": "test_key_basic"
      }
    }
  }
}
```

## Available Tools

Once added, you'll have access to these MCP tools in Claude:

- `set_api_key` - Configure your Rentcast API key
- `search_properties` - Search property records by location
- `get_property` - Get specific property details
- `get_value_estimate` - Property value estimates
- `get_rent_estimate` - Rental price estimates
- `search_sale_listings` - Properties for sale
- `search_rental_listings` - Rental properties
- `get_market_statistics` - Market analysis data
- `expire_cache` - Manage cache entries
- `get_cache_stats` - View cache performance
- `get_usage_stats` - Track API usage and costs
- `set_api_limits` - Configure rate limits
- `get_api_limits` - View current limits

## Usage Examples

After adding the server, you can use it in Claude like this:

```
User: Search for properties in Austin, Texas

Claude: I'll search for properties in Austin, Texas using the Rentcast API.
[Uses search_properties tool with city="Austin", state="TX"]
```

```
User: What's the estimated value of 123 Main St, Dallas, TX?

Claude: I'll get the value estimate for that property.
[Uses get_value_estimate tool with address="123 Main St, Dallas, TX"]
```

## Troubleshooting

### Server won't start
- Ensure `uv` is installed: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Check Python version: Requires Python 3.13+
- Verify dependencies: Run `uv sync` in the project directory

### API key issues
- For production: Set `RENTCAST_API_KEY` with your actual key
- For testing: Set `USE_MOCK_API=true` to use test keys

### Database errors
- Delete `data/mcrentcast.db` and restart to recreate
- Ensure write permissions in the data directory

### Rate limiting
- Adjust limits in environment variables
- Use mock API for unlimited testing

## Support

- Documentation: `/docs` directory
- Mock API guide: `/docs/mock-api.md`
- GitHub issues: Create an issue in the repository