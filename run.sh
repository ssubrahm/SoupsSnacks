#!/bin/bash

# Soups, Snacks & More - Quick Run Script (runs in current terminal)
# Use this if you prefer to manually manage backend/frontend in separate terminals

set -e

echo "🍲 Soups, Snacks & More - Quick Start"
echo "====================================="
echo ""

PROJECT_DIR="/Users/Srinath.Subrahmanyan/SoupsSnacks"
cd "$PROJECT_DIR"

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main
echo ""

echo "✅ Ready to run!"
echo ""
echo "Choose what to start:"
echo ""
echo "For Backend (in this terminal):"
echo "  cd $PROJECT_DIR"
echo "  source SSCo/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "For Frontend (in a NEW terminal):"
echo "  cd $PROJECT_DIR/frontend"
echo "  npm start"
echo ""
