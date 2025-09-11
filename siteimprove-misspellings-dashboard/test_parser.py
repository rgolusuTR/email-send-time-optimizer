#!/usr/bin/env python3
"""
Test script for the file parser
"""

from modules.file_parser import SiteimproveParser

def test_parser():
    parser = SiteimproveParser()
    
    # Test detection
    report_type = parser.detect_report_type('test_file.csv')
    print(f"Detected report type: {report_type}")
    
    if report_type != 'unknown':
        # Test parsing
        try:
            result = parser.parse_file('test_file.csv', report_type)
            print(f"Successfully parsed {result['row_count']} records")
            
            if result['data']:
                print("Sample record:")
                sample = result['data'][0]
                for key, value in sample.items():
                    print(f"  {key}: {value}")
            
            print(f"Metadata: {result['metadata']}")
            
        except Exception as e:
            print(f"Error parsing file: {e}")
    else:
        print("Could not detect report type")

if __name__ == "__main__":
    test_parser()
