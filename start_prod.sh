#!/bin/bash
echo "🚀 Starting CarbonSight in production mode..."

# Build frontend
echo "🏗️ Building frontend..."
npm run build

# Start backend
echo "📡 Starting backend server..."
python run.py
