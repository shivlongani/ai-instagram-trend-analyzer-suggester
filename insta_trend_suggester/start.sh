#!/bin/bash

# Instagram Trend Suggester Startup Script

echo "Starting Instagram Trend Suggester..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Please copy .env.example to .env and configure your API keys."
    echo "cp .env.example .env"
    exit 1
fi

# Start the application
echo "Starting FastAPI server..."
python main.py
