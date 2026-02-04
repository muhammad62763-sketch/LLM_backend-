#!/bin/bash

echo "🚀 Setting up Multi-API Backend..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.11+ is required"
    exit 1
fi

# Install Poetry if not installed
if ! command -v poetry &> /dev/null; then
    echo "📦 Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
fi

# Install dependencies
echo "📦 Installing dependencies..."
poetry install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update .env with your actual API keys and database URL"
fi

# Initialize database migrations
echo "🗄️  Initializing database..."
poetry run alembic upgrade head

echo "✅ Setup complete!"
echo ""
echo "To start the server:"
echo "  poetry run uvicorn app.main:app --reload"
echo ""
echo "Or with Docker:"
echo "  docker-compose up -d"
