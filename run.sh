#!/bin/bash

# Get project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate virtual environment (INSIDE project)
source "$SCRIPT_DIR/llm-agent-env/bin/activate"

# Use python3 explicitly (safer)
python3 "$SCRIPT_DIR/gui.py"
