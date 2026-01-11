#!/bin/bash
# Build script for macOS
# Creates a standalone .app bundle

set -e

echo "🔨 Building Markdown Converter for macOS..."

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

# Build with PyInstaller
echo "🏗️  Building application..."
pyinstaller --onedir --windowed \
    --name "MarkdownConverter" \
    --add-data "app/locales:locales" \
    $ICON_OPTION \
    --noconfirm \
    --clean \
    app/main.py

echo ""
echo "✅ Build complete!"
echo "📁 Application location: dist/MarkdownConverter.app"
echo ""
echo "To run the app:"
echo "  open dist/MarkdownConverter.app"
echo ""
echo "Or run directly:"
echo "  ./dist/MarkdownConverter/MarkdownConverter"
