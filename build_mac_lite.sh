#!/bin/bash
# Lightweight Build script for macOS (No AI features)
# Creates a smaller standalone .app (~40-50MB instead of 100MB+)

set -e

echo "🔨 Building Markdown Converter for macOS (LITE - No AI)..."

# Create lightweight venv
if [ ! -d "venv-lite" ]; then
    echo "⚠️  Creating lightweight virtual environment..."
    python3 -m venv venv-lite
fi

source venv-lite/bin/activate

# Install minimal dependencies
echo "📦 Installing minimal dependencies..."
pip install -r app/requirements-build.txt
pip install pyinstaller

# Icon
ICON_FILE="app/assets/icon.icns"
ICON_OPTION=""
if [ -f "$ICON_FILE" ]; then
    ICON_OPTION="--icon=$ICON_FILE"
fi

# Build with PyInstaller (Lite version)
echo "🏗️  Building lite application..."
pyinstaller --onedir --windowed \
    --name "MarkdownConverter-Lite" \
    --add-data "app/locales:locales" \
    --add-data "app/components:components" \
    $ICON_OPTION \
    --noconfirm \
    --clean \
    --strip \
    --exclude-module openai \
    --exclude-module google \
    --exclude-module google.generativeai \
    --exclude-module httpx \
    --exclude-module h11 \
    --exclude-module httpcore \
    --exclude-module _testcapi \
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
    --exclude-module lib2to3 \
    --exclude-module pydoc \
    --exclude-module doctest \
    --exclude-module pdb \
    app/main.py

echo ""
echo "✅ LITE Build complete!"
echo "📁 Application: dist/MarkdownConverter-Lite.app"
echo ""
echo "ℹ️  Note: This version does NOT include AI image description."
echo "   To use AI features, install openai/google-generativeai separately."
echo ""

# Show size
echo "📊 Build size:"
du -sh dist/MarkdownConverter-Lite.app 2>/dev/null || du -sh dist/MarkdownConverter-Lite
