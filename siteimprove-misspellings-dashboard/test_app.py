#!/usr/bin/env python3
"""
Simple test script to check if the Flask app can start
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing Flask app startup...")
    
    # Test imports
    print("1. Testing imports...")
    from flask import Flask
    print("   ✓ Flask imported")
    
    from flask_sqlalchemy import SQLAlchemy
    print("   ✓ Flask-SQLAlchemy imported")
    
    import pandas as pd
    print("   ✓ Pandas imported")
    
    # Test our modules
    print("2. Testing custom modules...")
    from database.models import db, Website
    print("   ✓ Database models imported")
    
    from modules.file_parser import SiteimproveParser
    print("   ✓ File parser imported")
    
    from modules.data_processor import DataProcessor
    print("   ✓ Data processor imported")
    
    from modules.export_service import ExportService
    print("   ✓ Export service imported")
    
    # Test Flask app creation
    print("3. Testing Flask app creation...")
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    print("   ✓ Flask app created and configured")
    
    # Test database creation
    print("4. Testing database creation...")
    with app.app_context():
        db.create_all()
        print("   ✓ Database tables created")
    
    print("\n✅ All tests passed! The Flask app should work correctly.")
    print("🚀 Starting Flask app on port 5001...")
    
    # Import and run the actual app
    import app as main_app
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    print("Please install missing dependencies with: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
