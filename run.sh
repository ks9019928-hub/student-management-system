#!/bin/bash
set -e

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "Setting up virtual environment..."
    python3 -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi

source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
