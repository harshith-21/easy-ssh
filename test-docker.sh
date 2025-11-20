#!/bin/bash

echo "🔍 Checking Docker status..."

if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "📱 Starting Docker Desktop..."
    open -a Docker
    echo "⏳ Waiting for Docker to start (this may take 30-60 seconds)..."
    
    # Wait up to 60 seconds for Docker to start
    for i in {1..60}; do
        if docker info > /dev/null 2>&1; then
            echo "✅ Docker is now running!"
            break
        fi
        sleep 1
        echo -n "."
    done
    
    if ! docker info > /dev/null 2>&1; then
        echo ""
        echo "❌ Docker failed to start. Please:"
        echo "   1. Open Docker Desktop manually"
        echo "   2. Wait for it to fully start"
        echo "   3. Run this script again"
        exit 1
    fi
fi

echo "✅ Docker is running!"
echo ""
echo "🚀 Starting Easy SSH with docker-compose..."
cd /Users/harshithgandhe/Desktop/easy-ssh
docker-compose up --build

