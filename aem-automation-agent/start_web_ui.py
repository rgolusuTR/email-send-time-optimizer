#!/usr/bin/env python3
"""
Simple startup script for the AEM Automation Agent Web UI
"""

import os
import sys
import subprocess

def main():
    print("🚀 Starting AEM Automation Agent Web UI...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('web_ui.py'):
        print("❌ Error: web_ui.py not found. Please run this script from the aem-automation-agent directory.")
        sys.exit(1)
    
    # Check if templates directory exists
    if not os.path.exists('templates'):
        print("📁 Creating templates directory...")
        os.makedirs('templates', exist_ok=True)
    
    if not os.path.exists('static'):
        print("📁 Creating static directory...")
        os.makedirs('static', exist_ok=True)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found. Please create one with your AEM credentials.")
        print("   You can copy .env.example to .env and fill in your details.")
    
    print("\n🌐 Web UI will be available at: http://localhost:5000")
    print("🔧 Make sure to configure your .env file with AEM credentials")
    print("📖 Check the README.md for detailed setup instructions")
    print("\n" + "=" * 50)
    
    try:
        # Start the web UI
        subprocess.run([sys.executable, 'web_ui.py'], check=True)
    except KeyboardInterrupt:
        print("\n\n👋 Web UI stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting web UI: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
