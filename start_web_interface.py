#!/usr/bin/env python3
"""
Launcher for the Code Conversion Web Interface
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        print("✅ Flask is installed")
        return True
    except ImportError:
        print("❌ Flask is not installed")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_web.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def create_sample_zip():
    """Create a sample project ZIP for testing"""
    import zipfile
    
    sample_dir = Path("sample_projects/c_project")
    zip_path = Path("sample_c_project.zip")
    
    if not zip_path.exists() and sample_dir.exists():
        print("Creating sample project ZIP...")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in sample_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(sample_dir)
                    zipf.write(file_path, arcname)
        print(f"✅ Sample ZIP created: {zip_path}")
        return str(zip_path)
    return None

def main():
    """Main launcher function"""
    print("🚀 Code Conversion Web Interface Launcher")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\nInstalling missing dependencies...")
        if not install_dependencies():
            print("❌ Failed to install dependencies. Please install manually:")
            print("   pip install -r requirements_web.txt")
            return
    
    # Create sample ZIP
    sample_zip = create_sample_zip()
    
    # Start the web server
    print("\n🌐 Starting web interface...")
    print("   The interface will be available at: http://localhost:5000")
    print("   Press Ctrl+C to stop the server")
    
    if sample_zip:
        print(f"\n📁 Sample project available: {sample_zip}")
        print("   You can use this ZIP file to test the conversion")
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(2)
        webbrowser.open('http://localhost:5000')
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start Flask app
    try:
        from web_interface import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Web interface stopped")
    except Exception as e:
        print(f"\n❌ Error starting web interface: {e}")

if __name__ == "__main__":
    main() 