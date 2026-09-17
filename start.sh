#!/usr/bin/env bash
# RetailFlow Launch Script (Linux / macOS)

echo "==================================================="
echo "🚀 Launching RetailFlow Platform"
echo "==================================================="

# Try to activate conda ml environment if available
if command -v conda &> /dev/null; then
    eval "$(conda shell.bash hook 2> /dev/null)"
    conda activate ml 2> /dev/null || true
fi

# Detect Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "Error: Python 3 not found in PATH."
    exit 1
fi

$PYTHON_CMD start_retailflow.py
