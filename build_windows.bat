@echo off
REM Optimized Build script for Windows
REM Creates a standalone .exe application with reduced size

echo 🔨 Building Markdown Converter for Windows (Optimized)...

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

REM Build with PyInstaller (Optimized)
echo 🏗️  Building application with optimizations...
pyinstaller --onedir --windowed ^
    --name "MarkdownConverter" ^
    --add-data "app\locales;locales" ^
    --add-data "app\components;components" ^
    %ICON_OPTION% ^
    --noconfirm ^
    --clean ^
    --strip ^
    --exclude-module _testcapi ^
    --exclude-module _testbuffer ^
    --exclude-module _testinternalcapi ^
    --exclude-module _ctypes_test ^
    --exclude-module _testmultiphase ^
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
    --exclude-module tkinter.test ^
    --exclude-module lib2to3 ^
    --exclude-module pydoc ^
    --exclude-module doctest ^
    --exclude-module pdb ^
    --exclude-module profile ^
    --exclude-module cProfile ^
    --exclude-module trace ^
    --exclude-module curses ^
    --exclude-module multiprocessing.popen_spawn_posix ^
    app\main.py

echo.
echo ✅ Build complete!
echo 📁 Application location: dist\MarkdownConverter\MarkdownConverter.exe
echo.

REM Show size
echo 📊 Build size:
dir /s dist\MarkdownConverter | findstr /c:"File(s)"
echo.

echo To run the app, double-click:
echo   dist\MarkdownConverter\MarkdownConverter.exe
echo.

pause
