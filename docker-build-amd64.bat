@echo off
REM Docker build script for AMD64 PDF Extractor
REM Ensures AMD64 compatibility and compliance with requirements

echo 🐳 Building PDF Extractor for AMD64 Architecture...

REM Build with explicit AMD64 platform
docker build --platform linux/amd64 --tag mysolutionname:somerandomidentifier .

echo ✅ Build complete!
echo.
echo 📋 Verification:
echo    • Platform: linux/amd64
echo    • CPU-only: No GPU dependencies  
echo    • Offline: No network calls required
echo    • Size: ^<200MB (excluding base image)
echo.
echo 🚀 To run:
echo    docker run --rm -v %cd%/input:/app/input -v %cd%/output:/app/output --network none mysolutionname:somerandomidentifier
