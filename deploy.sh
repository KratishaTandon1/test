#!/bin/bash
# Deployment script matching the exact submission requirements

echo "🏗️ Building the Docker image..."
docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier .

if [ $? -eq 0 ]; then
    echo "✅ Image built successfully!"
    echo ""
    echo "📂 Setting up directories..."
    mkdir -p input output
    echo "✅ Directories ready!"
    echo ""
    echo "🚀 Ready to run with:"
    echo "   docker run --rm -v \$(pwd)/input:/app/input -v \$(pwd)/output:/app/output --network none mysolutionname:somerandomidentifier"
    echo ""
    echo "📋 Usage:"
    echo "   1. Place PDF files in ./input/ directory"
    echo "   2. Run the container command above"
    echo "   3. Find extracted data in ./output/ directory"
else
    echo "❌ Build failed!"
    exit 1
fi
