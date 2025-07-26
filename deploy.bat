@echo off
REM Deployment script matching the exact submission requirements

echo 🏗️ Building the Docker image...
docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier .

if %ERRORLEVEL% equ 0 (
    echo ✅ Image built successfully!
    echo.
    echo 📂 Setting up directories...
    if not exist "input" mkdir input
    if not exist "output" mkdir output
    echo ✅ Directories ready!
    echo.
    echo 🚀 Ready to run with:
    echo    docker run --rm -v %cd%/input:/app/input -v %cd%/output:/app/output --network none mysolutionname:somerandomidentifier
    echo.
    echo 📋 Usage:
    echo    1. Place PDF files in .\input\ directory
    echo    2. Run the container command above
    echo    3. Find extracted data in .\output\ directory
) else (
    echo ❌ Build failed!
    exit /b 1
)
