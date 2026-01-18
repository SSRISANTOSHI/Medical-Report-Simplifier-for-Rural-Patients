#!/bin/bash

# Streamlit App Launcher

echo "🏥 Starting Medical Report Simplifier (Streamlit UI)..."

# Ensure venv exists
if [ ! -d "backend/venv" ]; then
    echo "⚠️  Virtual environment not found. Please run start.sh first to set it up."
    exit 1
fi

cd backend
source venv/bin/activate

# Run the app
echo "🚀 Launching Streamlit..."
echo "🌐 App will run at: http://localhost:8501"
streamlit run streamlit_app.py
