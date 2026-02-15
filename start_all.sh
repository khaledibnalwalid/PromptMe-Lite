#!/bin/bash
# Start all PromptMe-Lite challenges at once
# Usage: ./start_all.sh [--no-dashboard]

set -e

echo "======================================================================"
echo " PromptMe-Lite - Starting All Challenges"
echo "======================================================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  WARNING: .env file not found"
    echo "   Copying .env.example to .env..."
    cp .env.example .env
    echo "   ✓ Please configure .env with your settings"
    echo ""
fi

# Create logs directory
mkdir -p logs

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check if requirements are installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo ""
    echo "⚠️  Dependencies not installed. Installing from requirements.txt..."
    pip3 install -r requirements.txt
    echo ""
fi

# Start all challenges
echo "Starting all 10 challenges..."
echo ""

if [ "$1" = "--no-dashboard" ]; then
    # Production mode: start all challenges without dashboard
    python3 main.py --no-dashboard
else
    # Development mode: start all challenges + dashboard
    python3 main.py --start-all
fi
