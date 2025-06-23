#!/usr/bin/env python3
"""
CropMate Startup Script
A simple script to check dependencies and start the CropMate application
"""

import sys
import subprocess
import importlib.util
import os

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'flask',
        'numpy', 
        'pandas',
        'sklearn',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        spec = importlib.util.find_spec(package)
        if spec is None:
            missing_packages.append(package)
        else:
            print(f"✅ {package} - OK")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install missing packages with:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def check_model_files():
    """Check if required model files exist"""
    required_files = [
        'model.pkl',
        'standscaler.pkl', 
        'minmaxscaler.pkl'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} - OK")
        else:
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Missing model files: {', '.join(missing_files)}")
        print("Please ensure all model files are present in the project directory")
        return False
    
    return True

def start_application():
    """Start the Flask application"""
    print("\n🚀 Starting CropMate...")
    print("=" * 50)
    print("🌱 CropMate - Your Farming Companion")
    print("=" * 50)
    print("📱 Access the application at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Import and run the Flask app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 CropMate stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🌱 CropMate Startup Check")
    print("=" * 30)
    
    # Check Python version
    if not check_python_version():
        return False
    
    print("\n📦 Checking dependencies...")
    if not check_dependencies():
        return False
    
    print("\n🤖 Checking model files...")
    if not check_model_files():
        return False
    
    print("\n✅ All checks passed!")
    
    # Start the application
    return start_application()

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 