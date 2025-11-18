#!/bin/bash

# mcrentcast MCP Server Installation Script

set -e

echo "🚀 Installing mcrentcast MCP Server..."
echo "======================================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Install dependencies
echo "📦 Installing Python dependencies..."
cd "$SCRIPT_DIR"
uv sync

# Create data directory
echo "📁 Creating data directory..."
mkdir -p data

# Initialize database
echo "🗄️ Initializing database..."
uv run python -c "
from mcrentcast.database import db_manager
db_manager.create_tables()
print('✅ Database initialized')
"

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📋 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your Rentcast API key"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "📌 Next steps:"
echo "1. Edit .env and set your RENTCAST_API_KEY"
echo "2. Add to Claude using: claude mcp add $SCRIPT_DIR"
echo "3. Or add manually to your Claude MCP configuration"
echo ""
echo "🧪 To test with mock API (no credits required):"
echo "   make test-mock"
echo ""
echo "📚 Documentation: $SCRIPT_DIR/docs/mock-api.md"