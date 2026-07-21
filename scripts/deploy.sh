#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."

echo "🚀 Starting Veridex Production Deployment..."

echo "🛑 Tearing down existing development containers..."
docker-compose -f docker-compose.yml down || true

echo "📦 Building and starting the containers..."
docker-compose -f docker-compose.prod.yml up -d --build

echo "🔄 Waiting for databases to become healthy..."
sleep 10

# 2. Database Migrations
echo "📦 Running database migrations..."
docker exec veridex_backend uv run alembic upgrade head


echo "✅ Deployment successful!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
