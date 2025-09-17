#!/bin/bash
set -e

echo "🛑 Stopping Heroes Platform with Potpie Integration..."

# Stop Docker services
echo "🐳 Stopping Docker services..."
docker compose down

# Remove containers and networks
echo "🧹 Cleaning up containers and networks..."
docker compose down --volumes --remove-orphans

echo "✅ Heroes Platform with Potpie has been stopped!"
echo ""
echo "💡 To start again: ./start_heroes_with_potpie.sh"
