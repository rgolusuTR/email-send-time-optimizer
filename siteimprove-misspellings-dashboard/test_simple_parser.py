#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.simple_parser import SimpleSiteimproveParser

def test_simple_parser():
    parser = SimpleSiteimproveParser()
    
    # Test file path
    test_file = "test_file.csv"
    
    print("Testing simple parser...")
    
    try:
        # Test detection
        report_type = parser.detect_report_type(test_file)
        print(f"✅ Detection successful: {report_type}")
        
        # Test parsing
        result = parser.parse_file(test_file, report_type)
        print(f"✅ Parsing successful!")
        print(f"   Metadata: {result['metadata']}")
        print(f"   Row count: {result['row_count']}")
        if result['data']:
            print(f"   First record: {result['data'][0]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_parser()
