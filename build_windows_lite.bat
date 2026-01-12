@echo off
REM Lightweight Build script for Windows (No AI features)
REM Creates a smaller standalone .exe (~40-50MB instead of 114MB)

echo 🔨 Building Markdown Converter for Windows (LITE - No AI)...

REM Check if virtual environment exists
if not exist "venv-lite" (
    echo ⚠️  Creating lightweight virtual environment...
    python -m venv venv-lite
)

REM Activate virtual environment
call venv-lite\Scripts\activate.bat

REM Install minimal dependencies
echo 📦 Installing minimal dependencies...
pip install -r app\requirements-build.txt
pip install pyinstaller

REM Check for icon
set ICON_OPTION=
if exist "app\assets\icon.ico" (
    set ICON_OPTION=--icon=app\assets\icon.ico
)

REM Build with PyInstaller (Lite version)
echo 🏗️  Building lite application...
pyinstaller --onedir --windowed ^
    --name "MarkdownConverter-Lite" ^
    --add-data "app\locales;locales" ^
    --add-data "app\components;components" ^
    %ICON_OPTION% ^
    --noconfirm ^
    --clean ^
    --strip ^
    --exclude-module openai ^
    --exclude-module google ^
    --exclude-module google.generativeai ^
    --exclude-module httpx ^
    --exclude-module h11 ^
    --exclude-module httpcore ^
    --exclude-module _testcapi ^
    --exclude-module test ^
    --exclude-module tests ^
    --exclude-module unittest ^
    --exclude-module pytest ^
    --exclude-module pip ^
    --exclude-module setuptools ^
    --exclude-module wheel ^
    --exclude-module distutils ^
    --exclude-module pkg_resources ^
    --exclude-module numpy.testing ^
    --exclude-module scipy ^
    --exclude-module matplotlib ^
    --exclude-module IPython ^
    --exclude-module jupyter ^
    --exclude-module notebook ^
    --exclude-module lib2to3 ^
    --exclude-module pydoc ^
    --exclude-module doctest ^
    --exclude-module pdb ^
    app\main.py

echo.
echo ✅ LITE Build complete!
echo 📁 Application: dist\MarkdownConverter-Lite\MarkdownConverter-Lite.exe
echo.
echo ℹ️  Note: This version does NOT include AI image description.
echo     To use AI features, install openai/google-generativeai separately.
echo.

REM Show size
echo 📊 Build size:
dir /s dist\MarkdownConverter-Lite | findstr /c:"File(s)"
echo.

pause
