#!/bin/bash
# ==============================================================================
# Student Management System - Startup Runner
# ==============================================================================

set -e

cd "$(dirname "$0")"

echo "=========================================================="
echo "🎓 Starting Student Management System Backend"
echo "=========================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    ./venv/bin/pip install --upgrade pip
    ./venv/bin/pip install -r requirements.txt
fi

# Activate venv
source venv/bin/activate

# Launch Uvicorn server
echo "Starting FastAPI server on http://127.0.0.1:8000"
echo "• Swagger Docs: http://127.0.0.1:8000/docs"
echo "• Health Check: http://127.0.0.1:8000/health"
echo "• Press Ctrl+C to stop the server"
echo "----------------------------------------------------------"

exec uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
