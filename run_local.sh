#!/bin/bash
# AI Virtual Gym Trainer - Local Run Script
# Usage: ./run_local.sh [enhanced|original|dev]

set -e

APP_MODE="${1:-enhanced}"

echo "🏋️ AI Virtual Gym Trainer - Local Runner"
echo "========================================="
echo "Mode: $APP_MODE"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Python: $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the appropriate app
case "$APP_MODE" in
    enhanced)
        echo "Starting ENHANCED app on http://localhost:8501"
        streamlit run streamlit_app_enhanced.py --server.port=8501
        ;;
    original)
        echo "Starting ORIGINAL app on http://localhost:8501"
        streamlit run streamlit_app.py --server.port=8501
        ;;
    dev)
        echo "Starting DEVELOPMENT mode with hot reload on http://localhost:8502"
        STREAMLIT_SERVER_RUN_ON_SAVE=true streamlit run streamlit_app_enhanced.py --server.port=8502
        ;;
    *)
        echo "Unknown mode: $APP_MODE"
        echo "Usage: ./run_local.sh [enhanced|original|dev]"
        exit 1
        ;;
esac