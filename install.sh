#!/bin/bash
#
# Soups, Snacks & More - Installation Script
# 
# This script sets up the application on a new Mac/Linux machine.
# Prerequisites: Python 3.10+, Node.js 18+
#

set -e

echo ""
echo "======================================"
echo "  Soups, Snacks & More - Installer"
echo "======================================"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "   Install from: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✓ Python $PYTHON_VERSION found"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    echo "   Install from: https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node -v)
echo "✓ Node.js $NODE_VERSION found"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed."
    exit 1
fi

NPM_VERSION=$(npm -v)
echo "✓ npm $NPM_VERSION found"

echo ""
echo "Creating Python virtual environment..."
python3 -m venv SSCo

echo "Activating virtual environment..."
source SSCo/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip > /dev/null
pip install -r requirements.txt

echo ""
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo ""
echo "Setting up database..."
python manage.py migrate

echo ""
echo "======================================"
echo "  Installation Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Seed demo data (optional):"
echo "   python seed_demo_data.py"
echo ""
echo "2. Or create your own admin user:"
echo "   python manage.py createsuperuser"
echo ""
echo "3. Start the application:"
echo "   ./setup.sh"
echo ""
echo "4. Open in browser:"
echo "   http://localhost:3000"
echo ""
echo "Demo credentials (if seeded):"
echo "   admin / admin123"
echo "   operator / operator123"
echo "   cook / cook123"
echo ""
