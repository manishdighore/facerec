#!/bin/bash

# Face Recognition Backend Setup Script
# This script sets up the new face_recognition library-based backend

set -e

echo "======================================"
echo "Face Recognition Backend Setup"
echo "======================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Detect OS
OS="unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS="windows"
fi

echo "Detected OS: $OS"
echo ""

# Install system dependencies based on OS
echo "Installing system dependencies..."
case $OS in
    macos)
        echo "Installing cmake via Homebrew..."
        if ! command -v brew &> /dev/null; then
            echo "Error: Homebrew not found. Please install Homebrew first:"
            echo "https://brew.sh/"
            exit 1
        fi
        brew install cmake || echo "cmake already installed"
        ;;
    linux)
        echo "Installing build tools and libraries..."
        sudo apt-get update
        sudo apt-get install -y build-essential cmake libopenblas-dev liblapack-dev
        ;;
    windows)
        echo "WARNING: On Windows, you need to manually install:"
        echo "1. Visual Studio Build Tools"
        echo "2. CMake"
        echo ""
        echo "Press Enter to continue if you have these installed..."
        read
        ;;
esac

echo ""
echo "Installing Python dependencies..."
cd backend

# Create virtual environment (optional but recommended)
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OS" == "windows" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dlib first (takes time to compile)
echo "Installing dlib (this may take a few minutes)..."
pip install --upgrade pip
pip install dlib

# Install other dependencies
echo "Installing other dependencies..."
pip install -r requirements.txt

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "To start the backend:"
echo "1. Activate virtual environment:"
if [[ "$OS" == "windows" ]]; then
    echo "   cd backend && venv\\Scripts\\activate"
else
    echo "   cd backend && source venv/bin/activate"
fi
echo "2. Run the server:"
echo "   python app.py"
echo ""
echo "The backend will be available at: http://localhost:5000"
echo ""
echo "For Docker deployment, run:"
echo "   docker-compose up --build"
echo ""
