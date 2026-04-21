import pandas as pd
from datetime import datetime
import re
from typing import Dict, List, Optional

class SimpleSiteimproveParser:
    """Simplified parser for Siteimprove CSV files"""
    
    def parse_file(self, file_path: str, report_type: str) -> Dict:
        """Parse a Siteimprove CSV file"""
        try:
            # Try different encodings and separators for CSV files
            encodings = ['utf-8-sig', 'utf-8', 'utf-16', 'latin-1', 'cp1252', 'iso-8859-1']
            separators = ['\t', ',', ';']
            df = None
            successful_encoding = None
            successful_separator = None
            
            for encoding in encodings:
                for sep in separators:
                    try:
                        df = pd.read_csv(file_path, sep=sep, encoding=encoding, quotechar='"', on_bad_lines='skip')
                        if len(df.columns) > 1 and len(df) > 0:  # Valid data found
                            successful_encoding = encoding
                            successful_separator = sep
                            break
                    except (UnicodeDecodeError, pd.errors.EmptyDataError, pd.errors.ParserError, Exception):
                        continue
                if df is not None and len(df.columns) > 1:
                    break
            
            if df is None or len(df.columns) <= 1:
                raise Exception("Could not read file with any encoding/separator combination")
            
            print(f"Debug: Successfully read file with encoding={successful_encoding}, separator='{successful_separator}'")
            
            print(f"Debug: File shape: {df.shape}")
            print(f"Debug: Columns: {list(df.columns)}")
            print(f"Debug: First few rows:\n{df.head()}")
            
            # Extract metadata from first 2 rows
            metadata = {}
            if len(df) > 0:
                first_row = str(df.iloc[0, 0])
                if 'Created:' in first_row:
                    metadata['created_date'] = first_row.replace('Created: ', '')
            
            if len(df) > 1:
                second_row = str(df.iloc[1, 0])
                if 'Site:' in second_row:
                    metadata['site_name'] = second_row.replace('Site: ', '')
            
            # Find the header row (should be row with "Word", "Spelling suggestion", etc.)
            header_row_idx = None
            for i, row in df.iterrows():
                if 'Word' in str(row.iloc[0]):
                    header_row_idx = i
                    break
            
            if header_row_idx is None:
                raise Exception("Could not find header row")
            
            # Extract data starting from after the header row
            data_df = df.iloc[header_row_idx + 1:].reset_index(drop=True)
            
            # Set column names from header row
            headers = df.iloc[header_row_idx].tolist()
            data_df.columns = headers
            
            print(f"Debug: Data shape after processing: {data_df.shape}")
            print(f"Debug: Headers: {headers}")
            
            # Parse the data
            parsed_data = []
            for _, row in data_df.iterrows():
                try:
                    if report_type == 'misspellings':
                        record = {
                            'word': self._clean_value(row.get('Word')),
                            'spelling_suggestion': self._clean_value(row.get('Spelling suggestion')),
                            'language': self._clean_value(row.get('Language')),
                            'first_detected': self._parse_date(self._clean_value(row.get('First detected'))),
                            'pages_count': self._safe_int(self._clean_value(row.get('Pages')))
                        }
                        parsed_data.append(record)
                except Exception as e:
                    print(f"Warning: Skipping row due to error: {e}")
                    continue
            
            return {
                'metadata': metadata,
                'data': parsed_data,
                'row_count': len(parsed_data)
            }
            
        except Exception as e:
            raise Exception(f"Error parsing file: {str(e)}")
    
    def _clean_value(self, value) -> Optional[str]:
        """Clean and return string value"""
        if pd.isna(value) or value == '':
            return None
        return str(value).strip().replace('"', '')
    
    def _safe_int(self, value: str) -> Optional[int]:
        """Safely convert to integer"""
        if value is None:
            return None
        try:
            return int(float(value))
        except:
            return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_str:
            return None
        
        # Common date formats
        date_formats = [
            '%m/%d/%Y %I:%M:%S %p',  # "1/3/2025 8:51:10 AM"
            '%m/%d/%Y %H:%M:%S',
            '%m/%d/%Y',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except:
                continue
        
        print(f"Warning: Could not parse date: {date_str}")
        return None
    
    def detect_report_type(self, file_path: str) -> str:
        """Detect report type from file content"""
        try:
            # Try different encodings to read the file
            encodings = ['utf-8-sig', 'utf-8', 'utf-16', 'latin-1', 'cp1252', 'iso-8859-1']
            lines = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        lines = f.readlines()
                    break
                except (UnicodeDecodeError, Exception):
                    continue
            
            if lines is None:
                print("Could not read file with any encoding for detection")
                return 'misspellings'
            
            # Look for header line
            for line in lines:
                if 'Word' in line and 'Spelling suggestion' in line:
                    if 'Misspelling probability' in line:
                        return 'words_to_review'
                    elif 'Pages' in line:
                        return 'misspellings'
            
            return 'misspellings'  # Default
            
        except Exception as e:
            print(f"Error detecting report type: {e}")
            return 'misspellings'
