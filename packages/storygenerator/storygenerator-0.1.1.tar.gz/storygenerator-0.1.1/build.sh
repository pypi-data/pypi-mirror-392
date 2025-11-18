#!/bin/bash
# Build script for dailystories-generator package

set -e

echo "🔨 Building dailystories-generator package..."

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info

# Build the package
echo "Building wheel and source distribution..."
uv build

echo "✅ Build complete! Distributions are in dist/"
ls -lh dist/

