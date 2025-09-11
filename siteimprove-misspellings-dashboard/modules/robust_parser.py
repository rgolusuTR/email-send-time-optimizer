import pandas as pd
from datetime import datetime
import re
from typing import Dict, List, Optional
import chardet

class RobustSiteimproveParser:
    """Robust parser for Siteimprove CSV files with comprehensive error handling"""
    
    def parse_file(self, file_path: str, report_type: str) -> Dict:
        """Parse a Siteimprove CSV file with robust error handling"""
        try:
            print(f"Debug: Attempting to parse file: {file_path}")
            
            # First, detect the file encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                encoding_result = chardet.detect(raw_data)
                detected_encoding = encoding_result['encoding']
                confidence = encoding_result['confidence']
                print(f"Debug: Detected encoding: {detected_encoding} (confidence: {confidence})")
            
            # Try multiple approaches to read the file
            df = None
            successful_method = None
            
            # Method 1: Use detected encoding
            if detected_encoding and confidence > 0.7:
                try:
                    df = self._try_read_csv(file_path, detected_encoding)
                    if df is not None:
                        successful_method = f"detected encoding ({detected_encoding})"
                except Exception as e:
                    print(f"Debug: Failed with detected encoding: {e}")
            
            # Method 2: Try common encodings
            if df is None:
                encodings = ['utf-8-sig', 'utf-8', 'utf-16', 'utf-16le', 'utf-16be', 'latin-1', 'cp1252', 'iso-8859-1']
                for encoding in encodings:
                    try:
                        df = self._try_read_csv(file_path, encoding)
                        if df is not None:
                            successful_method = f"fallback encoding ({encoding})"
                            break
                    except Exception as e:
                        print(f"Debug: Failed with {encoding}: {e}")
                        continue
            
            # Method 3: Try reading as binary and converting
            if df is None:
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    
                    # Try to decode with different encodings
                    for encoding in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']:
                        try:
                            text_content = content.decode(encoding)
                            # Write to temporary file and read with pandas
                            import tempfile
                            import os
                            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as temp_file:
                                temp_file.write(text_content)
                                temp_path = temp_file.name
                            
                            df = self._try_read_csv(temp_path, 'utf-8')
                            os.unlink(temp_path)  # Clean up temp file
                            
                            if df is not None:
                                successful_method = f"binary conversion ({encoding})"
                                break
                        except Exception as e:
                            print(f"Debug: Binary conversion failed with {encoding}: {e}")
                            continue
                except Exception as e:
                    print(f"Debug: Binary method failed: {e}")
            
            if df is None:
                raise Exception("Could not read file with any method")
            
            print(f"Debug: Successfully read file using {successful_method}")
            print(f"Debug: File shape: {df.shape}")
            print(f"Debug: Columns: {list(df.columns)}")
            print(f"Debug: First few rows:\n{df.head()}")
            
            # Process the dataframe
            return self._process_dataframe(df, report_type)
            
        except Exception as e:
            print(f"Debug: Full error details: {str(e)}")
            raise Exception(f"Error parsing file: {str(e)}")
    
    def _try_read_csv(self, file_path: str, encoding: str) -> Optional[pd.DataFrame]:
        """Try to read CSV with different separators"""
        separators = ['\t', ',', ';', '|']
        
        for sep in separators:
            try:
                df = pd.read_csv(
                    file_path, 
                    sep=sep, 
                    encoding=encoding, 
                    quotechar='"', 
                    on_bad_lines='skip',
                    engine='python'  # More flexible parser
                )
                
                # Check if we got meaningful data
                if len(df.columns) > 1 and len(df) > 0:
                    print(f"Debug: Success with separator '{sep}' and encoding '{encoding}'")
                    return df
                    
            except Exception as e:
                print(f"Debug: Failed with sep='{sep}', encoding='{encoding}': {e}")
                continue
        
        return None
    
    def _process_dataframe(self, df: pd.DataFrame, report_type: str) -> Dict:
        """Process the successfully read dataframe"""
        # Extract metadata from first few rows
        metadata = {}
        
        # Look for metadata in first few rows
        for i in range(min(5, len(df))):
            row_text = str(df.iloc[i, 0])
            if 'Created:' in row_text or 'created:' in row_text.lower():
                metadata['created_date'] = row_text
            elif 'Site:' in row_text or 'site:' in row_text.lower():
                metadata['site_name'] = row_text
        
        # Find the header row
        header_row_idx = None
        for i, row in df.iterrows():
            row_text = str(row.iloc[0]).lower()
            if 'word' in row_text and ('spelling' in row_text or 'suggestion' in row_text):
                header_row_idx = i
                break
        
        if header_row_idx is None:
            # If no clear header found, assume row 3 (after metadata)
            header_row_idx = min(3, len(df) - 1)
            print(f"Debug: No clear header found, using row {header_row_idx}")
        
        print(f"Debug: Using header row {header_row_idx}")
        
        # Extract data starting from after the header row
        if header_row_idx + 1 >= len(df):
            raise Exception("No data rows found after header")
        
        data_df = df.iloc[header_row_idx + 1:].reset_index(drop=True)
        
        # Set column names from header row
        headers = df.iloc[header_row_idx].tolist()
        data_df.columns = headers
        
        print(f"Debug: Data shape after processing: {data_df.shape}")
        print(f"Debug: Headers: {headers}")
        
        # Parse the data based on report type
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
                    # Only add if we have at least a word
                    if record['word']:
                        parsed_data.append(record)
                        
            except Exception as e:
                print(f"Warning: Skipping row due to error: {e}")
                continue
        
        print(f"Debug: Successfully parsed {len(parsed_data)} records")
        
        return {
            'metadata': metadata,
            'data': parsed_data,
            'row_count': len(parsed_data)
        }
    
    def _clean_value(self, value) -> Optional[str]:
        """Clean and return string value"""
        if pd.isna(value) or value == '' or str(value).lower() == 'nan':
            return None
        return str(value).strip().replace('"', '')
    
    def _safe_int(self, value: str) -> Optional[int]:
        """Safely convert to integer"""
        if value is None:
            return None
        try:
            # Remove any non-numeric characters except decimal point
            clean_value = re.sub(r'[^\d.]', '', str(value))
            if clean_value:
                return int(float(clean_value))
        except:
            pass
        return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_str:
            return None
        
        # Clean the date string
        date_str = str(date_str).strip().replace('"', '')
        
        # Common date formats
        date_formats = [
            '%m/%d/%Y %I:%M:%S %p',  # "1/3/2025 8:51:10 AM"
            '%m/%d/%Y %H:%M:%S',
            '%m/%d/%Y %H:%M',
            '%m/%d/%Y %I:%M %p',
            '%m/%d/%Y',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d',
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        
        print(f"Warning: Could not parse date: {date_str}")
        return None
    
    def detect_report_type(self, file_path: str) -> str:
        """Detect report type from file content"""
        try:
            # Use the same robust reading approach
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                encoding_result = chardet.detect(raw_data)
                detected_encoding = encoding_result['encoding']
            
            # Try to read with detected encoding first
            content = None
            if detected_encoding:
                try:
                    content = raw_data.decode(detected_encoding)
                except:
                    pass
            
            # Fallback to other encodings
            if content is None:
                for encoding in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']:
                    try:
                        content = raw_data.decode(encoding)
                        break
                    except:
                        continue
            
            if content is None:
                return 'misspellings'  # Default
            
            # Look for header patterns
            content_lower = content.lower()
            if 'misspelling probability' in content_lower:
                return 'words_to_review'
            elif 'page report' in content_lower and 'cms' in content_lower:
                return 'pages_with_misspellings'
            elif 'report date' in content_lower:
                return 'misspelling_history'
            elif 'word' in content_lower and 'spelling' in content_lower:
                return 'misspellings'
            
            return 'misspellings'  # Default
            
        except Exception as e:
            print(f"Error detecting report type: {e}")
            return 'misspellings'
