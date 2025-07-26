#!/usr/bin/env python3
"""
Docker Command Validation for Submission Requirements
Validates that Docker files use the exact submission commands
"""

import os
import re
from pathlib import Path

def main():
    print("🔍 Validating Docker commands for submission requirements...")
    print()
    
    # Expected commands from submission requirements
    expected_build = "docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier"
    expected_run = "docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none mysolutionname:somerandomidentifier"
    
    validation_results = []
    
    # Check build scripts
    print("📋 Checking build scripts...")
    
    # Linux/macOS build script
    bash_script = Path("docker-build-amd64.sh")
    if bash_script.exists():
        try:
            content = bash_script.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = bash_script.read_text(encoding='latin1')
        if "mysolutionname:somerandomidentifier" in content and "--platform linux/amd64" in content:
            print("✅ docker-build-amd64.sh - Updated with correct image name")
            validation_results.append(("Build Script (Linux)", "PASS"))
        else:
            print("❌ docker-build-amd64.sh - Missing correct image name")
            validation_results.append(("Build Script (Linux)", "FAIL"))
    
    # Windows build script
    bat_script = Path("docker-build-amd64.bat")
    if bat_script.exists():
        try:
            content = bat_script.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = bat_script.read_text(encoding='latin1')
        if "mysolutionname:somerandomidentifier" in content and "--platform linux/amd64" in content:
            print("✅ docker-build-amd64.bat - Updated with correct image name")
            validation_results.append(("Build Script (Windows)", "PASS"))
        else:
            print("❌ docker-build-amd64.bat - Missing correct image name")
            validation_results.append(("Build Script (Windows)", "FAIL"))
    
    print()
    print("🚀 Checking run scripts...")
    
    # Run script
    run_script = Path("docker-run.sh")
    if run_script.exists():
        try:
            content = run_script.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = run_script.read_text(encoding='latin1')
        if "mysolutionname:somerandomidentifier" in content and "--network none" in content:
            print("✅ docker-run.sh - Updated with correct image name and network isolation")
            validation_results.append(("Run Script", "PASS"))
        else:
            print("❌ docker-run.sh - Missing correct configuration")
            validation_results.append(("Run Script", "FAIL"))
    
    # Deployment scripts
    deploy_script = Path("deploy.sh")
    if deploy_script.exists():
        try:
            content = deploy_script.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = deploy_script.read_text(encoding='latin1')
        if "mysolutionname:somerandomidentifier" in content:
            print("✅ deploy.sh - Correct submission commands")
            validation_results.append(("Deploy Script (Linux)", "PASS"))
        else:
            print("❌ deploy.sh - Incorrect commands")
            validation_results.append(("Deploy Script (Linux)", "FAIL"))
    
    deploy_bat = Path("deploy.bat")
    if deploy_bat.exists():
        try:
            content = deploy_bat.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = deploy_bat.read_text(encoding='latin1')
        if "mysolutionname:somerandomidentifier" in content:
            print("✅ deploy.bat - Correct submission commands")
            validation_results.append(("Deploy Script (Windows)", "PASS"))
        else:
            print("❌ deploy.bat - Incorrect commands")
            validation_results.append(("Deploy Script (Windows)", "FAIL"))
    
    print()
    print("📖 Checking documentation...")
    
    # Documentation files
    docs = ["DOCKER_AMD64.md", "DOCKER_COMPLIANCE_SUMMARY.md"]
    for doc in docs:
        if Path(doc).exists():
            try:
                content = Path(doc).read_text(encoding='utf-8')
            except UnicodeDecodeError:
                content = Path(doc).read_text(encoding='latin1')
            if "mysolutionname:somerandomidentifier" in content:
                print(f"✅ {doc} - Updated with submission commands")
                validation_results.append((f"Documentation ({doc})", "PASS"))
            else:
                print(f"❌ {doc} - Still contains old commands")
                validation_results.append((f"Documentation ({doc})", "FAIL"))
    
    print()
    print("=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for component, status in validation_results:
        icon = "✅" if status == "PASS" else "❌"
        print(f"{icon} {component:<30} {status}")
        if status == "FAIL":
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("🎉 All Docker commands updated for submission requirements!")
        print()
        print("📋 Submission Commands:")
        print(f"   Build: {expected_build}")
        print(f"   Run:   {expected_run}")
        print()
        print("✅ Ready for submission!")
    else:
        print("⚠️  Some files still need updates")
        print("Please check the failed items above")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
