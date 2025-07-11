#!/bin/bash
# JARVYS_AI Linux/Mac Deployment Script

set -e

echo "🚀 Starting JARVYS_AI Deployment..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check for .env file
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.template .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file with your API keys before continuing."
    echo "Press Enter when you have updated the .env file..."
    read
fi

# Build JARVYS_AI image
echo "🏗️  Building JARVYS_AI Docker image..."
docker build -f Dockerfile.jarvys_ai -t jarvys_ai:latest .

# Start JARVYS_AI
echo "🎯 Starting JARVYS_AI..."
docker-compose -f docker-compose.windows.yml up -d

echo ""
echo "✅ JARVYS_AI deployed successfully!"
echo "🌐 Web interface: http://localhost:8000"
echo "📝 Check logs: docker-compose -f docker-compose.windows.yml logs -f"
echo "🛑 Stop JARVYS_AI: docker-compose -f docker-compose.windows.yml down"
