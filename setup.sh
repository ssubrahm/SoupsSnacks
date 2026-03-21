#!/bin/bash

# Soups, Snacks & More - Local Setup Script for macOS
# This script pulls latest changes and starts both backend and frontend servers

set -e  # Exit on error

echo "🍲 Soups, Snacks & More - Setup & Run"
echo "======================================"
echo ""

# Navigate to project directory
PROJECT_DIR="/Users/Srinath.Subrahmanyan/SoupsSnacks"
cd "$PROJECT_DIR"

# Pull latest changes from GitHub
echo "📥 Pulling latest changes from GitHub..."
git pull origin main
echo "✓ Code updated"
echo ""

# Start backend in a new terminal
echo "🚀 Starting Django backend server..."
osascript -e 'tell application "Terminal" to do script "cd /Users/Srinath.Subrahmanyan/SoupsSnacks && source SSCo/bin/activate && python manage.py runserver"'
echo "✓ Backend starting in new terminal (http://localhost:8000)"
echo ""

# Wait a moment for backend to initialize
sleep 2

# Start frontend in a new terminal
echo "⚛️  Starting React frontend server..."
osascript -e 'tell application "Terminal" to do script "cd /Users/Srinath.Subrahmanyan/SoupsSnacks/frontend && npm start"'
echo "✓ Frontend starting in new terminal (http://localhost:3000)"
echo ""

echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   - Backend API: http://localhost:8000/api/health/"
echo "   - Frontend App: http://localhost:3000"
echo "   - Admin Panel: http://localhost:8000/admin/"
echo ""
echo "🛑 To stop servers: Close the terminal windows or press Ctrl+C in each"
