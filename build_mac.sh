#!/bin/bash
# Optimized Build script for macOS
# Creates a standalone .app bundle with reduced size

set -e

echo "🔨 Building Markdown Converter for macOS (Optimized)..."

# Check if in virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  No virtual environment detected. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r app/requirements.txt
pip install pyinstaller

# Create icon if not exists (placeholder)
ICON_DIR="app/assets"
ICON_FILE="$ICON_DIR/icon.icns"

if [ ! -f "$ICON_FILE" ]; then
    echo "ℹ️  No icon found. Building without custom icon..."
    ICON_OPTION=""
else
    ICON_OPTION="--icon=$ICON_FILE"
fi

# Build with PyInstaller (Optimized)
echo "🏗️  Building application with optimizations..."
pyinstaller --onedir --windowed \
    --name "MarkdownConverter" \
    --add-data "app/locales:locales" \
    --add-data "app/components:components" \
    $ICON_OPTION \
    --noconfirm \
    --clean \
    --strip \
    --exclude-module _testcapi \
    --exclude-module _testbuffer \
    --exclude-module _testinternalcapi \
    --exclude-module _ctypes_test \
    --exclude-module _testmultiphase \
    --exclude-module test \
    --exclude-module tests \
    --exclude-module unittest \
    --exclude-module pytest \
    --exclude-module pip \
    --exclude-module setuptools \
    --exclude-module wheel \
    --exclude-module distutils \
    --exclude-module pkg_resources \
    --exclude-module numpy.testing \
    --exclude-module scipy \
    --exclude-module matplotlib \
    --exclude-module IPython \
    --exclude-module jupyter \
    --exclude-module notebook \
    --exclude-module tkinter.test \
    --exclude-module lib2to3 \
    --exclude-module pydoc \
    --exclude-module doctest \
    --exclude-module pdb \
    --exclude-module profile \
    --exclude-module cProfile \
    --exclude-module trace \
    --exclude-module curses \
    app/main.py

echo ""
echo "✅ Build complete!"
echo "📁 Application location: dist/MarkdownConverter.app"
echo ""

# Show size
echo "📊 Build size:"
du -sh dist/MarkdownConverter.app 2>/dev/null || du -sh dist/MarkdownConverter
echo ""

echo "To run the app:"
echo "  open dist/MarkdownConverter.app"
echo ""
echo "Or run directly:"
echo "  ./dist/MarkdownConverter/MarkdownConverter"
