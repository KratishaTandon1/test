#!/usr/bin/env python3
"""
Docker AMD64 Compliance Validator
Validates that the Docker setup meets all AMD64 requirements
"""

import os
import re
import subprocess
import sys

def check_dockerfile():
    """Check Dockerfile for AMD64 compliance"""
    print("🔍 Checking Dockerfile...")
    
    with open('Dockerfile', 'r') as f:
        content = f.read()
    
    checks = {
        'AMD64 Platform': 'FROM --platform=linux/amd64' in content,
        'CPU Environment': 'TORCH_DEVICE=cpu' in content,
        'No CUDA': 'NO_CUDA=1' in content,
        'Modular Entry': 'main_modular.py' in content
    }
    
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")
    
    return all(checks.values())

def check_requirements():
    """Check requirements.txt for GPU dependencies"""
    print("\n🔍 Checking requirements.txt...")
    
    with open('requirements.txt', 'r') as f:
        content = f.read().lower()
    
    gpu_keywords = ['cuda', 'gpu', 'tensorrt', 'nvidia']
    gpu_deps = [keyword for keyword in gpu_keywords if keyword in content]
    
    if gpu_deps:
        print(f"  ❌ Found GPU dependencies: {gpu_deps}")
        return False
    else:
        print("  ✅ No GPU dependencies found")
        return True

def check_file_sizes():
    """Check key file sizes for container efficiency"""
    print("\n🔍 Checking file sizes...")
    
    files_to_check = [
        'main_modular.py',
        'requirements.txt', 
        'Dockerfile',
        '.dockerignore'
    ]
    
    total_size = 0
    for file in files_to_check:
        if os.path.exists(file):
            size = os.path.getsize(file)
            total_size += size
            print(f"  📄 {file}: {size:,} bytes")
        else:
            print(f"  ❌ Missing: {file}")
            return False
    
    print(f"  📊 Total core files: {total_size:,} bytes")
    return True

def check_main_script():
    """Check that main script exists and is executable"""
    print("\n🔍 Checking main script...")
    
    if not os.path.exists('main_modular.py'):
        print("  ❌ main_modular.py not found")
        return False
    
    try:
        # Try different encodings
        for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
            try:
                with open('main_modular.py', 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue
        else:
            print("  ❌ Could not decode main script with any encoding")
            return False
        
        if 'ModularPDFExtractor' in content:
            print("  ✅ Uses modular architecture")
        else:
            print("  ⚠️  May not use modular architecture")
        
        return True
    except Exception as e:
        print(f"  ❌ Error reading main script: {e}")
        return False

def main():
    """Main validation function"""
    print("🐳 Docker AMD64 Compliance Validator")
    print("=" * 50)
    
    checks = [
        ("Dockerfile", check_dockerfile),
        ("Requirements", check_requirements), 
        ("File Sizes", check_file_sizes),
        ("Main Script", check_main_script)
    ]
    
    results = []
    for name, check_func in checks:
        result = check_func()
        results.append((name, result))
    
    print("\n" + "=" * 50)
    print("📋 Validation Summary:")
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All checks passed! Docker setup is AMD64 compliant.")
        print("\n🚀 Ready to build:")
        print("   docker build --platform linux/amd64 -t pdf-extractor:amd64 .")
    else:
        print("⚠️  Some checks failed. Please review and fix issues.")
        sys.exit(1)

if __name__ == "__main__":
    main()
