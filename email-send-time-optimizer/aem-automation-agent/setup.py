#!/usr/bin/env python3
"""
Setup script for AEM Automation Agent
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version {sys.version.split()[0]} is compatible")
    return True

def install_dependencies():
    """Install Python dependencies"""
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python dependencies"
    )

def install_playwright():
    """Install Playwright browsers"""
    return run_command(
        f"{sys.executable} -m playwright install chromium",
        "Installing Playwright browsers"
    )

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example.exists():
        print("❌ .env.example file not found")
        return False
    
    try:
        # Copy .env.example to .env
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file with your AEM credentials")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def test_installation():
    """Test if the installation works"""
    print("🧪 Testing installation...")
    try:
        # Try importing main modules
        import playwright
        import loguru
        import pydantic
        from dotenv import load_dotenv
        
        print("✅ All dependencies imported successfully")
        
        # Test if Playwright browser is available
        result = subprocess.run(
            f"{sys.executable} -c 'from playwright.sync_api import sync_playwright; p = sync_playwright().start(); p.chromium.launch(); p.stop()'",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Playwright browser test passed")
            return True
        else:
            print("❌ Playwright browser test failed")
            print(f"   Error: {result.stderr}")
            return False
            
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        return False

def show_next_steps():
    """Show next steps to the user"""
    print("\n" + "="*50)
    print("🎉 Setup completed successfully!")
    print("="*50)
    print("\nNext steps:")
    print("1. Edit the .env file with your AEM credentials:")
    print("   - AEM_USERNAME=your_username")
    print("   - AEM_PASSWORD=your_password")
    print("\n2. Run the agent:")
    print("   python cli.py                    # Interactive mode")
    print("   python cli.py -c \"Create a page\"  # Single command")
    print("\n3. Get help:")
    print("   python cli.py --help")
    print("\n4. Test with demo:")
    print("   python aem_agent.py")
    print("\nFor more information, see README.md")

def main():
    """Main setup function"""
    print("🚀 AEM Automation Agent Setup")
    print("="*40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies. Please check your internet connection and try again.")
        sys.exit(1)
    
    # Install Playwright
    if not install_playwright():
        print("❌ Failed to install Playwright browsers. Please try running 'playwright install chromium' manually.")
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        print("❌ Failed to create .env file. Please create it manually from .env.example")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("❌ Installation test failed. Please check the error messages above.")
        sys.exit(1)
    
    # Show next steps
    show_next_steps()

if __name__ == "__main__":
    main()
