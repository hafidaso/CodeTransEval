#!/usr/bin/env python3
"""
Simple launcher for Code Project Converter
"""

import os
import sys
import webbrowser
import time
import threading
from pathlib import Path

def main():
    """Launch the Code Project Converter"""
    
    print("🚀 Code Project Converter")
    print("=" * 40)
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Virtual environment not detected")
        print("   Run: source .venv/bin/activate")
        return
    
    # Check if required files exist
    required_files = [
        'enhanced_code_converter.py',
        'web_interface.py',
        'gemma3n_integration.py'
    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Missing required file: {file}")
            return
    
    print("✅ All required files found")
    
    # Create necessary directories
    os.makedirs('converted', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    
    print("🌐 Starting web interface...")
    print("   URL: http://localhost:5000")
    print("   Press Ctrl+C to stop")
    
    # Open browser after delay
    def open_browser():
        time.sleep(2)
        webbrowser.open('http://localhost:5000')
    
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start the web interface
    try:
        from start_web_interface import main as start_web
        start_web()
    except KeyboardInterrupt:
        print("\n👋 Code Project Converter stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main() 