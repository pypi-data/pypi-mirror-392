#!/bin/bash
# Publish script for dailystories-generator package

set -e

# Check if PYPI_API_TOKEN or PYPI_TOKEN is set
if [ -z "$PYPI_API_TOKEN" ] && [ -z "$PYPI_TOKEN" ]; then
    echo "❌ Error: PYPI_API_TOKEN or PYPI_TOKEN environment variable not set"
    echo "Set it with: export PYPI_API_TOKEN='your-token-here'"
    echo ""
    echo "To get a token:"
    echo "1. Go to https://pypi.org/manage/account/token/"
    echo "2. Create a new API token"
    echo "3. Export it: export PYPI_API_TOKEN='pypi-...'"
    exit 1
fi

# Use PYPI_API_TOKEN if available, otherwise fall back to PYPI_TOKEN
TOKEN="${PYPI_API_TOKEN:-$PYPI_TOKEN}"

# Build first
echo "🔨 Building package..."
./build.sh

# Publish to PyPI
echo ""
echo "📦 Publishing to PyPI..."
uv publish --token "$TOKEN"

echo ""
echo "✅ Published successfully to PyPI!"
echo "View at: https://pypi.org/project/storygenerator/"

