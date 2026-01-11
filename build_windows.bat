@echo off
REM Build script for Windows
REM Creates a standalone .exe application

echo 🔨 Building Markdown Converter for Windows...

REM Check if virtual environment exists
if not exist "venv" (
    echo ⚠️  No virtual environment detected. Creating one...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r app\requirements.txt
pip install pyinstaller

REM Check for icon
set ICON_OPTION=
if exist "app\assets\icon.ico" (
    set ICON_OPTION=--icon=app\assets\icon.ico
) else (
    echo ℹ️  No icon found. Building without custom icon...
)

REM Build with PyInstaller
echo 🏗️  Building application...
pyinstaller --onedir --windowed ^
    --name "MarkdownConverter" ^
    --add-data "app\locales;locales" ^
    %ICON_OPTION% ^
    --noconfirm ^
    --clean ^
    app\main.py

echo.
echo ✅ Build complete!
echo 📁 Application location: dist\MarkdownConverter\MarkdownConverter.exe
echo.
echo To run the app, double-click:
echo   dist\MarkdownConverter\MarkdownConverter.exe
echo.

pause
