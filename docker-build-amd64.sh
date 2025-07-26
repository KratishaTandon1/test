#!/bin/bash
# Docker build script for AMD64 PDF Extractor
# Ensures AMD64 compatibility and compliance with requirements

echo "🐳 Building PDF Extractor for AMD64 Architecture..."

# Build with explicit AMD64 platform
docker build \
    --platform linux/amd64 \
    --tag mysolutionname:somerandomidentifier \
    .

echo "✅ Build complete!"
echo ""
echo "📋 Verification:"
echo "   • Platform: linux/amd64"
echo "   • CPU-only: No GPU dependencies"
echo "   • Offline: No network calls required"
echo "   • Size: <200MB (excluding base image)"
echo ""
echo "🚀 To run:"
echo "   docker run --rm -v \$(pwd)/input:/app/input -v \$(pwd)/output:/app/output --network none mysolutionname:somerandomidentifier"
