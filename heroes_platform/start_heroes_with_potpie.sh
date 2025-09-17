#!/bin/bash
set -e

echo "🚀 Starting Heroes Platform with Potpie Integration..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if virtual environment is active
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  No virtual environment is active. Creating one..."
    python3.11 -m venv venv
    source venv/bin/activate
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -e ".[dev,production,mcp]"

# Copy Potpie configuration if it doesn't exist
if [ ! -f "potpie/.env" ]; then
    echo "📋 Creating Potpie configuration..."
    cp config/potpie.env.example potpie/.env
    echo "⚠️  Please edit potpie/.env and configure your AI provider API keys"
fi

# Start Docker services
echo "🐳 Starting Docker services..."
docker compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."

# Wait for Heroes PostgreSQL
echo "Waiting for Heroes PostgreSQL..."
until docker exec heroes_postgres pg_isready -U heroes_user -d heroes_platform; do
    echo "Heroes PostgreSQL is unavailable - sleeping"
    sleep 2
done

# Wait for Potpie PostgreSQL
echo "Waiting for Potpie PostgreSQL..."
until docker exec potpie_postgres pg_isready -U postgres; do
    echo "Potpie PostgreSQL is unavailable - sleeping"
    sleep 2
done

# Wait for Neo4j
echo "Waiting for Neo4j..."
until curl -f http://localhost:7474 > /dev/null 2>&1; do
    echo "Neo4j is unavailable - sleeping"
    sleep 2
done

# Wait for Redis
echo "Waiting for Redis..."
until docker exec heroes_redis redis-cli ping > /dev/null 2>&1; do
    echo "Redis is unavailable - sleeping"
    sleep 2
done

echo "✅ All services are ready!"

# Apply Potpie database migrations
echo "🗄️  Applying Potpie database migrations..."
cd potpie
alembic upgrade heads
cd ..

echo "🎉 Heroes Platform with Potpie is ready!"
echo ""
echo "📊 Services:"
echo "  - Heroes Platform API: http://localhost:8000"
echo "  - Potpie API: http://localhost:8001"
echo "  - Neo4j Browser: http://localhost:7474"
echo "  - Redis: localhost:6379"
echo ""
echo "🔧 Next steps:"
echo "  1. Configure AI provider API keys in potpie/.env"
echo "  2. Test the integration with: python scripts/test_potpie_integration.py"
echo ""
echo "🛑 To stop all services: ./stop_heroes_with_potpie.sh"
