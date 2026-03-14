#!/bin/bash
cd "$(dirname "$0")" || exit

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install dependencies if requirements.txt has changed or first run
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the application
echo "Starting Simulador..."
streamlit run app.py
