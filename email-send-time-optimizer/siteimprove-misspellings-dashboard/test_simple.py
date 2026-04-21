#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.file_parser import SiteimproveParser

def test_parser():
    parser = SiteimproveParser()
    
    # Test file path
    test_file = "test_file.csv"
    
    print("Testing parser...")
    
    try:
        # Test detection
        report_type = parser.detect_report_type(test_file)
        print(f"✅ Detection successful: {report_type}")
        
        # Test parsing
        result = parser.parse_file(test_file, report_type)
        print(f"✅ Parsing successful!")
        print(f"   Metadata: {result['metadata']}")
        print(f"   Row count: {result['row_count']}")
        print(f"   First few records: {result['data'][:3]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_parser()
