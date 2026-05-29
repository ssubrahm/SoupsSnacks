#!/bin/bash

# Quick reference — run backend and frontend manually from THIS folder

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🍲 Soups, Snacks & More - Quick Start"
echo "====================================="
echo ""
echo "Project: $PROJECT_DIR"
echo ""

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "📥 Checking for updates..."
  git pull origin main 2>/dev/null || echo "⚠️  Skipped git pull (local changes or network)"
  echo ""
fi

echo "✅ Ready to run!"
echo ""
echo "Terminal 1 — Backend:"
echo "  cd $PROJECT_DIR"
echo "  source SSCo/bin/activate"
echo "  python manage.py migrate"
echo "  python manage.py runserver"
echo ""
echo "Terminal 2 — Frontend:"
echo "  cd $PROJECT_DIR/frontend"
echo "  npm start"
echo ""
echo "Then open http://localhost:3000 — 💬 Ask is the landing page"
echo ""
