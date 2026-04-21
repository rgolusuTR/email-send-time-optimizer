import pandas as pd
from datetime import datetime
import re
from typing import Dict, List, Tuple, Optional

class SiteimproveParser:
    """Parser for Siteimprove report files (Excel/CSV)"""
    
    def __init__(self):
        self.supported_formats = ['.csv', '.xlsx', '.xls']
    
    def parse_file(self, file_path: str, report_type: str) -> Dict:
        """
        Parse a Siteimprove report file
        
        Args:
            file_path: Path to the file
            report_type: Type of report (misspellings, words_to_review, pages_with_misspellings, misspelling_history)
        
        Returns:
            Dictionary containing parsed data and metadata
        """
        try:
            # Read the file
            if file_path.endswith('.csv'):
                # Try different encodings and separators for CSV files
                encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
                separators = ['\t', ',']  # Try tab first, then comma
                df = None
                successful_encoding = None
                successful_separator = None
                
                for encoding in encodings:
                    for sep in separators:
                        try:
                            df = pd.read_csv(file_path, header=None, encoding=encoding, sep=sep, quotechar='"', quoting=1, on_bad_lines='skip')
                            if len(df.columns) > 1:  # If we got multiple columns, we found the right separator
                                successful_encoding = encoding
                                successful_separator = sep
                                break
                        except (UnicodeDecodeError, pd.errors.EmptyDataError, pd.errors.ParserError):
                            continue
                    if df is not None and len(df.columns) > 1:
                        break
                
                if df is None or len(df.columns) <= 1:
                    raise Exception("Could not read CSV file with any encoding/separator combination")
                
                print(f"Debug: Successfully read CSV with encoding={successful_encoding}, separator='{successful_separator}'")
            else:
                df = pd.read_excel(file_path, header=None)
            
            # Extract metadata from first 3 rows
            metadata = self._extract_metadata(df)
            
            # Parse data starting from row 4 (index 3)
            if len(df) <= 3:
                raise Exception("File does not have enough rows (needs at least 4 rows)")
            
            data_df = df.iloc[3:].reset_index(drop=True)
            
            # Set proper headers
            if len(data_df) == 0:
                raise Exception("No data rows found after headers")
            
            data_df.columns = data_df.iloc[0]
            data_df = data_df.drop(data_df.index[0]).reset_index(drop=True)
            
            print(f"Debug: Data shape after processing: {data_df.shape}")
            print(f"Debug: Columns: {list(data_df.columns)}")
            
            # Parse based on report type
            parsed_data = self._parse_by_type(data_df, report_type)
            
            return {
                'metadata': metadata,
                'data': parsed_data,
                'row_count': len(parsed_data)
            }
            
        except Exception as e:
            raise Exception(f"Error parsing file: {str(e)}")
    
    def _extract_metadata(self, df: pd.DataFrame) -> Dict:
        """Extract metadata from first 3 rows"""
        metadata = {}
        
        try:
            # Row 1: Created date and time
            if len(df) > 0:
                created_text = str(df.iloc[0, 0])
                if 'Created:' in created_text:
                    date_match = re.search(r'Created:\s*(.+)', created_text)
                    if date_match:
                        try:
                            metadata['created_date'] = datetime.strptime(
                                date_match.group(1).strip(), 
                                '%m/%d/%Y %I:%M:%S %p'
                            )
                        except:
                            metadata['created_date'] = None
            
            # Row 2: Site name
            if len(df) > 1:
                site_text = str(df.iloc[1, 0])
                if 'Site:' in site_text:
                    site_match = re.search(r'Site:\s*(.+)', site_text)
                    if site_match:
                        metadata['site_name'] = site_match.group(1).strip()
                else:
                    metadata['site_name'] = site_text.strip()
            
        except Exception as e:
            print(f"Warning: Could not extract metadata: {e}")
        
        return metadata
    
    def _parse_by_type(self, df: pd.DataFrame, report_type: str) -> List[Dict]:
        """Parse data based on report type"""
        
        if report_type == 'misspellings':
            return self._parse_misspellings(df)
        elif report_type == 'words_to_review':
            return self._parse_words_to_review(df)
        elif report_type == 'pages_with_misspellings':
            return self._parse_pages_with_misspellings(df)
        elif report_type == 'misspelling_history':
            return self._parse_misspelling_history(df)
        else:
            raise ValueError(f"Unsupported report type: {report_type}")
    
    def _parse_misspellings(self, df: pd.DataFrame) -> List[Dict]:
        """Parse misspellings report"""
        data = []
        
        for _, row in df.iterrows():
            try:
                record = {
                    'word': self._safe_get(row, 'Word'),
                    'spelling_suggestion': self._safe_get(row, 'Spelling suggestion'),
                    'language': self._safe_get(row, 'Language'),
                    'first_detected': self._parse_date(self._safe_get(row, 'First detected')),
                    'pages_count': self._safe_int(self._safe_get(row, 'Pages'))
                }
                data.append(record)
            except Exception as e:
                print(f"Warning: Skipping row due to error: {e}")
                continue
        
        return data
    
    def _parse_words_to_review(self, df: pd.DataFrame) -> List[Dict]:
        """Parse words to review report"""
        data = []
        
        for _, row in df.iterrows():
            try:
                record = {
                    'word': self._safe_get(row, 'Word'),
                    'spelling_suggestion': self._safe_get(row, 'Spelling suggestion'),
                    'language': self._safe_get(row, 'Language'),
                    'first_detected': self._parse_date(self._safe_get(row, 'First detected')),
                    'misspelling_probability': self._safe_get(row, 'Misspelling probability'),
                    'pages_count': self._safe_int(self._safe_get(row, 'Pages'))
                }
                data.append(record)
            except Exception as e:
                print(f"Warning: Skipping row due to error: {e}")
                continue
        
        return data
    
    def _parse_pages_with_misspellings(self, df: pd.DataFrame) -> List[Dict]:
        """Parse pages with misspellings report"""
        data = []
        
        for _, row in df.iterrows():
            try:
                record = {
                    'title': self._safe_get(row, 'Title'),
                    'url': self._safe_get(row, 'URL'),
                    'page_report_link': self._safe_get(row, 'Page Report'),
                    'cms_link': self._safe_get(row, 'CMS'),
                    'misspellings_count': self._safe_int(self._safe_get(row, 'Misspellings')),
                    'words_to_review_count': self._safe_int(self._safe_get(row, 'Words to review')),
                    'page_level': self._safe_int(self._safe_get(row, 'Page level'))
                }
                data.append(record)
            except Exception as e:
                print(f"Warning: Skipping row due to error: {e}")
                continue
        
        return data
    
    def _parse_misspelling_history(self, df: pd.DataFrame) -> List[Dict]:
        """Parse misspelling history report"""
        data = []
        
        for _, row in df.iterrows():
            try:
                record = {
                    'report_date': self._parse_date(self._safe_get(row, 'Report date')),
                    'misspellings_count': self._safe_int(self._safe_get(row, 'Misspellings')),
                    'words_to_review_count': self._safe_int(self._safe_get(row, 'Words to review'))
                    # Note: Ignoring 'Total words' column as per requirements
                }
                data.append(record)
            except Exception as e:
                print(f"Warning: Skipping row due to error: {e}")
                continue
        
        return data
    
    def _safe_get(self, row, column_name: str) -> Optional[str]:
        """Safely get a value from a row"""
        try:
            value = row.get(column_name)
            if pd.isna(value) or value == '':
                return None
            return str(value).strip()
        except:
            return None
    
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
        
        # Remove quotes if present
        date_str = date_str.strip().replace('"', '')
        
        # Common date formats in Siteimprove reports
        date_formats = [
            '%m/%d/%Y %I:%M:%S %p',  # Format from the CSV: "1/3/2025 8:51:10 AM"
            '%m/%d/%Y %H:%M:%S',
            '%m/%d/%Y %H:%M',
            '%m/%d/%Y %I:%M %p',
            '%m/%d/%Y %I:%M',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%m/%d/%Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except:
                continue
        
        print(f"Warning: Could not parse date: {date_str}")
        return None
    
    def detect_report_type(self, file_path: str) -> str:
        """
        Attempt to detect report type based on column headers
        """
        try:
            if file_path.endswith('.csv'):
                # Try different encodings and separators for CSV files
                encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
                separators = ['\t', ',']  # Try tab first, then comma
                df = None
                
                for encoding in encodings:
                    for sep in separators:
                        try:
                            # Skip first 3 rows (2 metadata + 1 empty), read headers from row 4
                            df = pd.read_csv(file_path, skiprows=3, nrows=1, encoding=encoding, sep=sep, quotechar='"')
                            if len(df.columns) > 1:  # If we got multiple columns, we found the right separator
                                break
                        except (UnicodeDecodeError, pd.errors.EmptyDataError, pd.errors.ParserError):
                            continue
                    if df is not None and len(df.columns) > 1:
                        break
                
                if df is None or len(df.columns) <= 1:
                    print("Could not read CSV file with any encoding/separator combination")
                    return 'unknown'
            else:
                df = pd.read_excel(file_path, header=None)
                # Get headers from row 4 (index 3) for Excel files
                if len(df) > 3:
                    headers = df.iloc[3].tolist()
                    df = pd.DataFrame(columns=headers)
            
            # Get column names and convert to lowercase for comparison
            columns = [str(col).lower().strip().replace('"', '') for col in df.columns if pd.notna(col)]
            headers_str = ' '.join(columns)
            
            print(f"Debug: Detected columns: {columns}")  # Debug output
            
            # Check for different report types based on column patterns
            if 'misspelling probability' in headers_str:
                return 'words_to_review'
            elif 'page report' in headers_str and 'cms' in headers_str:
                return 'pages_with_misspellings'
            elif 'report date' in headers_str:
                return 'misspelling_history'
            elif 'word' in headers_str and 'spelling suggestion' in headers_str and 'pages' in headers_str:
                return 'misspellings'
            
            return 'unknown'
            
        except Exception as e:
            print(f"Error detecting report type: {e}")
            return 'unknown'
