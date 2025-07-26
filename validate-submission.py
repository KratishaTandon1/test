#!/usr/bin/env python3
"""
Submission Checklist Validator
Validates all required submission components are present and correct
"""

import os
import json
from pathlib import Path

def validate_git_repository():
    """Check if this is a valid git repository"""
    git_dir = Path(".git")
    if git_dir.exists() and git_dir.is_dir():
        print("✅ Git repository initialized")
        return True
    else:
        print("❌ Git repository not found")
        return False

def validate_dockerfile():
    """Check if Dockerfile exists and is properly configured"""
    dockerfile = Path("Dockerfile")
    if not dockerfile.exists():
        print("❌ Dockerfile not found in root directory")
        return False
    
    content = dockerfile.read_text(encoding='utf-8')
    checks = {
        "AMD64 platform": "--platform=linux/amd64" in content,
        "Python base image": "python:" in content,
        "Working directory": "WORKDIR /app" in content,
        "Requirements copy": "COPY requirements.txt" in content,
        "Pip install": "pip install" in content,
        "Application copy": "COPY . ." in content,
        "CMD instruction": "CMD" in content,
        "Main script": "main_modular.py" in content
    }
    
    all_passed = True
    for check, passed in checks.items():
        icon = "✅" if passed else "❌"
        print(f"  {icon} {check}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("✅ Dockerfile is properly configured")
    else:
        print("❌ Dockerfile missing required components")
    
    return all_passed

def validate_dependencies():
    """Check if requirements.txt exists and contains necessary dependencies"""
    req_file = Path("requirements.txt")
    if not req_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    content = req_file.read_text(encoding='utf-8')
    required_deps = ["PyMuPDF", "scikit-learn", "numpy"]
    
    all_found = True
    for dep in required_deps:
        if dep.lower() in content.lower():
            print(f"  ✅ {dep} found in requirements")
        else:
            print(f"  ❌ {dep} missing from requirements")
            all_found = False
    
    # Check for GPU dependencies (should not be present)
    gpu_deps = ["torch", "tensorflow", "cuda"]
    gpu_found = False
    for dep in gpu_deps:
        if dep in content.lower() and "cpu" not in content.lower():
            print(f"  ⚠️  GPU dependency {dep} found - ensure CPU-only")
            gpu_found = True
    
    if not gpu_found:
        print("  ✅ No GPU dependencies detected")
    
    if all_found:
        print("✅ Dependencies properly specified")
    else:
        print("❌ Missing required dependencies")
    
    return all_found

def validate_readme():
    """Check if README.md exists and contains required sections"""
    readme = Path("README.md")
    if not readme.exists():
        print("❌ README.md not found")
        return False
    
    content = readme.read_text(encoding='utf-8').lower()
    
    required_sections = {
        "approach": ["approach", "architecture", "design", "strategy"],
        "models/libraries": ["models and libraries", "libraries used", "dependencies", "core libraries"],
        "build instructions": ["how to build", "building", "docker build", "build the solution"],
        "run instructions": ["how to run", "running", "docker run", "run the solution"]
    }
    
    all_found = True
    for section, keywords in required_sections.items():
        found = any(keyword in content for keyword in keywords)
        icon = "✅" if found else "❌"
        print(f"  {icon} {section.title()} section")
        if not found:
            all_found = False
    
    # Check for specific required content
    specific_checks = {
        "Docker commands": "docker build" in content and "docker run" in content,
        "AMD64 platform": "amd64" in content or "linux/amd64" in content,
        "Performance specs": any(x in content for x in ["10s", "200mb", "performance", "≤10", "≤200"]),
        "Network isolation": "--network none" in content or "offline" in content
    }
    
    for check, passed in specific_checks.items():
        icon = "✅" if passed else "❌"
        print(f"  {icon} {check}")
        if not passed:
            all_found = False
    
    if all_found:
        print("✅ README.md contains all required sections")
    else:
        print("❌ README.md missing required content")
    
    return all_found

def validate_main_script():
    """Check if main entry point exists"""
    main_script = Path("main_modular.py")
    if main_script.exists():
        print("✅ Main script (main_modular.py) found")
        return True
    else:
        print("❌ Main script (main_modular.py) not found")
        return False

def validate_docker_commands():
    """Validate the Docker commands match submission requirements"""
    print("🐳 Validating Docker commands...")
    
    # Check build scripts
    build_script = Path("docker-build-amd64.sh")
    if build_script.exists():
        content = build_script.read_text(encoding='utf-8')
        if "mysolutionname:somerandomidentifier" in content:
            print("  ✅ Build script uses correct image name")
        else:
            print("  ❌ Build script missing correct image name")
            return False
    
    # Check deployment scripts
    deploy_script = Path("deploy.sh")
    if deploy_script.exists():
        content = deploy_script.read_text(encoding='utf-8')
        if "mysolutionname:somerandomidentifier" in content and "--network none" in content:
            print("  ✅ Deploy script uses correct run command")
        else:
            print("  ❌ Deploy script missing correct configuration")
            return False
    
    print("✅ Docker commands properly configured")
    return True

def main():
    print("🔍 SUBMISSION CHECKLIST VALIDATION")
    print("=" * 50)
    
    checklist_items = [
        ("1. Git Repository", validate_git_repository),
        ("2. Working Dockerfile", validate_dockerfile),
        ("3. Dependencies", validate_dependencies),  
        ("4. README.md", validate_readme),
        ("5. Main Script", validate_main_script),
        ("6. Docker Commands", validate_docker_commands)
    ]
    
    results = []
    for item_name, validator in checklist_items:
        print(f"\n📋 Checking {item_name}...")
        result = validator()
        results.append((item_name, result))
    
    print("\n" + "=" * 50)
    print("📊 SUBMISSION CHECKLIST SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for item, passed in results:
        icon = "✅" if passed else "❌"
        status = "PASS" if passed else "FAIL"
        print(f"{icon} {item:<25} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("🎉 ALL SUBMISSION REQUIREMENTS MET!")
        print("\n✅ Ready for submission with:")
        print("   • Git project with working Dockerfile ✓")
        print("   • All dependencies in container ✓") 
        print("   • Complete README.md documentation ✓")
        print("   • Proper Docker build/run commands ✓")
        print("\n🚀 Build: docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier .")
        print("🚀 Run:   docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none mysolutionname:somerandomidentifier")
    else:
        print("⚠️  SUBMISSION REQUIREMENTS NOT FULLY MET")
        print("Please address the failed items above before submission.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
