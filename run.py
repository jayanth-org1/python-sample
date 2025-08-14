#!/usr/bin/env python3
"""
Startup script for the Python Flask Sample Application.
This script provides a user-friendly way to start the application.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required!")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import flask
        import requests
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False

def start_application():
    """Start the Flask application."""
    print("\n🚀 Starting Flask Application...")
    print("=" * 50)
    
    # Check if app.py exists
    if not Path("app.py").exists():
        print("❌ Error: app.py not found!")
        print("   Make sure you're in the correct directory.")
        return False
    
    try:
        # Start the Flask application
        print("📡 Starting server on http://localhost:5000")
        print("🔄 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Run the Flask app
        subprocess.run([sys.executable, "app.py"])
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        return False
    
    return True

def main():
    """Main function."""
    print("🎉 Welcome to Python Flask Sample Application!")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    # Start the application
    start_application()

if __name__ == "__main__":
    main()
