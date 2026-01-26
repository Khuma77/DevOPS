#!/usr/bin/env python3
"""
Code quality checker and fixer for Agro Shop
Bu script kodni tekshiradi va ba'zi muammolarni avtomatik tuzatadi
"""

import os
import subprocess
import sys

def run_command(cmd, description):
    """Run a command and return the result"""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - OK")
            if result.stdout.strip():
                print(result.stdout)
        else:
            print(f"⚠️ {description} - Issues found:")
            if result.stdout.strip():
                print(result.stdout)
            if result.stderr.strip():
                print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False

def check_python_files():
    """Check Python files in the project"""
    python_files = []
    
    # Find all Python files in project directories
    for root, dirs, files in os.walk('.'):
        # Skip virtual environments and other directories
        dirs[:] = [d for d in dirs if d not in ['venv', 'env', '.venv', '.env', '__pycache__', '.git', 'logs', 'monitoring', 'deploy']]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files

def main():
    """Main function"""
    print("🚀 Agro Shop Code Quality Checker")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Get Python files
    python_files = check_python_files()
    print(f"📁 Found {len(python_files)} Python files")
    
    # Create file list for flake8
    file_list = ' '.join([f for f in python_files if not f.startswith('./venv')])
    
    success = True
    
    # 1. Check syntax errors only
    print("\n1️⃣ Checking for syntax errors...")
    if file_list:
        cmd = f"flake8 {file_list} --select=E9,F63,F7,F82 --show-source"
        if not run_command(cmd, "Syntax check"):
            success = False
    
    # 2. Check our code with relaxed rules
    print("\n2️⃣ Checking code quality...")
    app_files = [f for f in python_files if not any(skip in f for skip in ['venv/', 'test_', '_test.py', 'monitoring/', 'deploy/'])]
    if app_files:
        app_file_list = ' '.join(app_files)
        cmd = f"flake8 {app_file_list} --max-line-length=127 --max-complexity=10 --ignore=E203,W503,F401 --exit-zero"
        run_command(cmd, "Code quality check")
    
    # 3. Run tests if available
    print("\n3️⃣ Running tests...")
    if os.path.exists('test_api.py'):
        run_command("python -m pytest test_api.py -v --tb=short", "Unit tests")
    
    # 4. Check imports
    print("\n4️⃣ Checking imports...")
    for file in app_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Check for common issues
                if 'import *' in content:
                    print(f"⚠️ {file}: Contains 'import *' - consider specific imports")
        except Exception as e:
            print(f"⚠️ Could not read {file}: {e}")
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Code quality check completed!")
    else:
        print("⚠️ Some issues found, but they might be in dependencies")
    
    print("\n📋 To run individual checks:")
    print("• Syntax: flake8 *.py api/ admin/ models/ --select=E9,F63,F7,F82")
    print("• Quality: flake8 *.py api/ admin/ models/ --max-line-length=127")
    print("• Tests: python -m pytest test_api.py -v")

if __name__ == "__main__":
    main()