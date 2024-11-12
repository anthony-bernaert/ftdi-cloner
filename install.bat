echo Removing existing virtual environment...
@RMDIR /S /Q .\.venv
echo Creating Python virtual environment...
python -m venv .venv
echo Activating environment...
CALL .\.venv\Scripts\activate.bat
echo Creating editable install of packages in this project
pip install -e .
echo "Creating executable..."
pyinstaller ftdi-cloner.py --noconfirm
