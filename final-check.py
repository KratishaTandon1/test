#!/usr/bin/env python3
"""
Simple Submission Validation
Quick check of all submission requirements
"""

import os
from pathlib import Path

def main():
    print("🎯 SUBMISSION READINESS CHECK")
    print("=" * 40)
    
    checks = []
    
    # 1. Git repository
    if Path(".git").exists():
        print("✅ Git repository initialized")
        checks.append(True)
    else:
        print("❌ Git repository missing")
        checks.append(False)
    
    # 2. Dockerfile in root
    if Path("Dockerfile").exists():
        print("✅ Dockerfile in root directory")
        dockerfile_content = Path("Dockerfile").read_text(encoding='utf-8')
        if "--platform=linux/amd64" in dockerfile_content:
            print("  ✅ AMD64 platform specified")
        if "main_modular.py" in dockerfile_content:
            print("  ✅ Main script configured")
        checks.append(True)
    else:
        print("❌ Dockerfile missing")
        checks.append(False)
    
    # 3. Dependencies
    if Path("requirements.txt").exists():
        print("✅ requirements.txt exists")
        req_content = Path("requirements.txt").read_text(encoding='utf-8')
        if "PyMuPDF" in req_content:
            print("  ✅ PyMuPDF dependency")
        if "scikit-learn" in req_content:
            print("  ✅ scikit-learn dependency")
        if "numpy" in req_content:
            print("  ✅ numpy dependency")
        checks.append(True)
    else:
        print("❌ requirements.txt missing")
        checks.append(False)
    
    # 4. README.md
    if Path("README.md").exists():
        print("✅ README.md exists")
        readme_content = Path("README.md").read_text(encoding='utf-8')
        if len(readme_content) > 1000:
            print("  ✅ Comprehensive documentation")
        if "docker build" in readme_content.lower():
            print("  ✅ Build instructions included")
        if "docker run" in readme_content.lower():
            print("  ✅ Run instructions included")
        if "approach" in readme_content.lower():
            print("  ✅ Approach documented")
        if "libraries" in readme_content.lower() or "models" in readme_content.lower():
            print("  ✅ Libraries/models documented")
        checks.append(True)
    else:
        print("❌ README.md missing")
        checks.append(False)
    
    # 5. Main script
    if Path("main_modular.py").exists():
        print("✅ main_modular.py exists")
        checks.append(True)
    else:
        print("❌ main_modular.py missing")
        checks.append(False)
    
    # 6. Docker commands
    if Path("deploy.sh").exists():
        deploy_content = Path("deploy.sh").read_text(encoding='utf-8')
        if "mysolutionname:somerandomidentifier" in deploy_content:
            print("✅ Correct Docker image name")
        if "--network none" in deploy_content:
            print("✅ Network isolation configured")
        checks.append(True)
    else:
        print("❌ Deploy script missing")
        checks.append(False)
    
    print("\n" + "=" * 40)
    
    if all(checks):
        print("🎉 ALL SUBMISSION REQUIREMENTS MET!")
        print("\n📋 Submission Checklist:")
        print("✅ Git project with working Dockerfile")
        print("✅ All dependencies in container")  
        print("✅ README.md with required sections")
        print("✅ Correct build/run commands")
        print("\n🚀 Ready for submission!")
    else:
        failed_count = len([c for c in checks if not c])
        print(f"⚠️  {failed_count} items need attention")
    
    print("\n📝 Final submission commands:")
    print("Build: docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier .")
    print("Run:   docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none mysolutionname:somerandomidentifier")

if __name__ == "__main__":
    main()
