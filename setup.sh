#!/bin/bash

# Soups, Snacks & More - Local Setup Script for macOS
# Starts backend + frontend from THIS project folder (SoupsSnacks_v2)

set -e

echo "🍲 Soups, Snacks & More - Setup & Run"
echo "======================================"
echo ""

# Always use the directory where this script lives
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"
echo "📁 Project: $PROJECT_DIR"
echo ""

# Optional git pull — do not abort if local changes block it
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "📥 Checking for updates from GitHub..."
  if git pull origin main 2>/dev/null; then
    echo "✓ Code updated"
  else
    echo "⚠️  Skipped git pull (local changes or network). Running current code in this folder."
  fi
  echo ""
fi

# Run migrations (includes Ask chat history, etc.)
if [ -f "$PROJECT_DIR/SSCo/bin/activate" ]; then
  echo "🗄️  Running database migrations..."
  # shellcheck source=/dev/null
  source "$PROJECT_DIR/SSCo/bin/activate"
  python manage.py migrate --noinput
  echo "✓ Migrations complete"
  echo ""
else
  echo "⚠️  Virtual env not found at $PROJECT_DIR/SSCo"
  echo "   Run ./install.sh first, then ./setup.sh again"
  echo ""
fi

# Start backend in a new terminal
echo "🚀 Starting Django backend server..."
osascript -e "tell application \"Terminal\" to do script \"cd '$PROJECT_DIR' && source SSCo/bin/activate && python manage.py runserver\""
echo "✓ Backend starting in new terminal (http://localhost:8000)"
echo ""

sleep 2

# Start frontend in a new terminal
echo "⚛️  Starting React frontend server..."
osascript -e "tell application \"Terminal\" to do script \"cd '$PROJECT_DIR/frontend' && npm start\""
echo "✓ Frontend starting in new terminal (http://localhost:3000)"
echo ""

echo "✅ Setup complete!"
echo ""
echo "📝 Open: http://localhost:3000"
echo "   Ask page is at /ask-jeeves — look for Ask Jeeves in the sidebar (2nd item)"
echo ""
echo "🛑 Stop old servers first if you still see the old UI:"
echo "   Close other Terminal windows running runserver or npm start"
echo "   Or hard-refresh Chrome: Cmd+Shift+R"
echo ""
