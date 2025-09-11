#!/usr/bin/env python3
"""
Quick start script for Siteimprove AI Agent
Starts both backend and frontend servers
"""
import subprocess
import sys
import os
import time
import threading
from pathlib import Path

def run_backend():
    """Start the backend server"""
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    print("🚀 Starting Backend Server...")
    try:
        subprocess.run([sys.executable, "start_server.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")
    except Exception as e:
        print(f"❌ Backend server error: {e}")

def run_frontend():
    """Start the frontend development server"""
    frontend_dir = Path(__file__).parent / "frontend"
    os.chdir(frontend_dir)
    
    print("🎨 Starting Frontend Server...")
    time.sleep(3)  # Give backend time to start
    
    try:
        subprocess.run(["npm", "start"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped")
    except Exception as e:
        print(f"❌ Frontend server error: {e}")

def main():
    """Main function to start both servers"""
    print("🌟 Siteimprove AI Agent - Quick Start")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not (Path.cwd() / "backend").exists() or not (Path.cwd() / "frontend").exists():
        print("❌ Please run this script from the siteimprove-ai-agent directory")
        sys.exit(1)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Start frontend in main thread
    try:
        run_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        sys.exit(0)

if __name__ == "__main__":
    main()
