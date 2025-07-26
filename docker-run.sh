#!/bin/bash
# Docker run script for PDF Extractor
# Ensures proper volume mounting and network isolation

echo "🚀 Running PDF Extractor..."

# Create input/output directories if they don't exist
mkdir -p input output

# Run the container with network isolation
docker run --rm 
    -v $(pwd)/input:/app/input 
    -v $(pwd)/output:/app/output 
    --network none 
    mysolutionname:somerandomidentifier

echo "✅ Processing complete! Check output/ directory for results."
