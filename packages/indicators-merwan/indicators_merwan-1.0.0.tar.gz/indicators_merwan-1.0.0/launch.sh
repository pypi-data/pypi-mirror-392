#!/bin/bash
# Composite Indicator Builder Launcher
# Author: Dr. Merwan Roudane

echo "===================================="
echo "Composite Indicator Builder"
echo "by Dr. Merwan Roudane"
echo "===================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check if package is installed
python3 -c "import indicator" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Package not found. Installing..."
    pip3 install -e .
    if [ $? -ne 0 ]; then
        echo "Installation failed!"
        exit 1
    fi
fi

# Launch the application
echo "Launching application..."
echo
python3 -m indicator.gui
