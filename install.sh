#!/bin/bash
echo "Removing existing virtual environment..."
rm -r ./.venv
echo Creating Python virtual environment...
python -m venv .venv
echo "Activating environment..."
source ./.venv/bin/activate
echo "Creating editable install of packages in this project"
pip install -e .
echo "Creating executable..."
pyinstaller ftdi-cloner.py --noconfirm
deactivate
