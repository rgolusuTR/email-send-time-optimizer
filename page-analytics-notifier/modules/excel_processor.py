"""
Excel processing module for Page Analytics Notification System
Handles reading and analyzing Adobe Analytics Excel reports
"""

import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import os
import re

class ExcelProcessor:
    def __init__(self):
        """Initialize Excel processor"""
        self.required_columns = ['Page URL', 'Creation Date', 'Page Views']
        self.data = None
        self.processed_data = []
        
    def validate_file(self, file_path: str) -> bool:
        """Validate if the file exists and has correct extension"""
        if not os.path.exists(file_path):
            logging.error(f"File not found: {file_path}")
            return False
            
        if not file_path.lower().endswith(('.xlsx', '.xls')):
            logging.error(f"Invalid file format: {file_path}")
            return False
            
        return True
    
    def read_excel_file(self, file_path: str) -> bool:
        """Read Excel file and validate structure"""
        try:
            # Try reading the Excel file
            self.data = pd.read_excel(file_path)
            logging.info(f"Successfully read Excel file: {file_path}")
            
            # Validate required columns
            missing_columns = []
            for col in self.required_columns:
                # Check for exact match or similar column names
                if col not in self.data.columns:
                    # Try to find similar column names (case insensitive)
                    similar_cols = [c for c in self.data.columns if col.lower() in c.lower()]
                    if similar_cols:
                        # Use the first similar column found
                        self.data.rename(columns={similar_cols[0]: col}, inplace=True)
                        logging.info(f"Mapped column '{similar_cols[0]}' to '{col}'")
                    else:
                        missing_columns.append(col)
            
            if missing_columns:
                logging.error(f"Missing required columns: {missing_columns}")
                return False
            
            # Clean and validate data
            self._clean_data()
            
            logging.info(f"Excel file processed successfully. Found {len(self.data)} rows")
            return True
            
        except Exception as e:
            logging.error(f"Error reading Excel file: {e}")
            return False
    
    def _clean_data(self):
        """Clean and validate the data"""
        try:
            # Remove rows with missing essential data
            initial_count = len(self.data)
            self.data = self.data.dropna(subset=['Page URL', 'Creation Date'])
            
            # Clean Page URLs
            self.data['Page URL'] = self.data['Page URL'].astype(str).str.strip()
            
            # Convert Creation Date to datetime
            self.data['Creation Date'] = pd.to_datetime(self.data['Creation Date'], errors='coerce')
            
            # Convert Page Views to numeric, fill NaN with 0
            self.data['Page Views'] = pd.to_numeric(self.data['Page Views'], errors='coerce').fillna(0)
            
            # Remove rows where date conversion failed
            self.data = self.data.dropna(subset=['Creation Date'])
            
            # Remove duplicate URLs (keep the latest entry)
            self.data = self.data.sort_values('Creation Date').drop_duplicates(subset=['Page URL'], keep='last')
            
            final_count = len(self.data)
            logging.info(f"Data cleaned: {initial_count} -> {final_count} rows")
            
        except Exception as e:
            logging.error(f"Error cleaning data: {e}")
            raise
    
    def analyze_pages(self, expired_threshold_days: int = 730, 
                     low_engagement_days: int = 30, 
                     low_engagement_views: int = 5) -> Tuple[List[Dict], List[Dict]]:
        """Analyze pages and identify those needing alerts"""
        if self.data is None:
            logging.error("No data loaded. Please read Excel file first.")
            return [], []
        
        current_date = datetime.now()
        expired_pages = []
        low_engagement_pages = []
        
        try:
            for _, row in self.data.iterrows():
                page_url = row['Page URL']
                creation_date = row['Creation Date']
                page_views = int(row['Page Views'])
                
                # Calculate page age
                page_age = (current_date - creation_date).days
                
                # Check for expired pages
                if page_age > expired_threshold_days:
                    expired_pages.append({
                        'page_url': page_url,
                        'creation_date': creation_date.strftime('%Y-%m-%d'),
                        'page_views': page_views,
                        'page_age_days': page_age,
                        'page_age_years': round(page_age / 365.25, 1),
                        'alert_type': 'expired'
                    })
                
                # Check for low engagement pages (recently created)
                elif page_age <= low_engagement_days and page_views < low_engagement_views:
                    low_engagement_pages.append({
                        'page_url': page_url,
                        'creation_date': creation_date.strftime('%Y-%m-%d'),
                        'page_views': page_views,
                        'days_since_creation': page_age,
                        'expected_views': low_engagement_views,
                        'alert_type': 'low_engagement'
                    })
            
            logging.info(f"Analysis complete: {len(expired_pages)} expired pages, {len(low_engagement_pages)} low engagement pages")
            return expired_pages, low_engagement_pages
            
        except Exception as e:
            logging.error(f"Error analyzing pages: {e}")
            return [], []
    
    def get_data_summary(self) -> Dict:
        """Get summary statistics of the loaded data"""
        if self.data is None:
            return {}
        
        try:
            current_date = datetime.now()
            
            # Calculate age statistics
            self.data['age_days'] = (current_date - self.data['Creation Date']).dt.days
            
            summary = {
                'total_pages': len(self.data),
                'date_range': {
                    'earliest': self.data['Creation Date'].min().strftime('%Y-%m-%d'),
                    'latest': self.data['Creation Date'].max().strftime('%Y-%m-%d')
                },
                'page_views': {
                    'total': int(self.data['Page Views'].sum()),
                    'average': round(self.data['Page Views'].mean(), 2),
                    'median': int(self.data['Page Views'].median())
                },
                'age_distribution': {
                    'average_age_days': round(self.data['age_days'].mean(), 1),
                    'pages_over_2_years': len(self.data[self.data['age_days'] > 730]),
                    'pages_under_30_days': len(self.data[self.data['age_days'] <= 30])
                }
            }
            
            return summary
            
        except Exception as e:
            logging.error(f"Error generating data summary: {e}")
            return {}
    
    def export_analysis_results(self, expired_pages: List[Dict], 
                               low_engagement_pages: List[Dict], 
                               output_path: str) -> bool:
        """Export analysis results to Excel file"""
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Export expired pages
                if expired_pages:
                    expired_df = pd.DataFrame(expired_pages)
                    expired_df.to_excel(writer, sheet_name='Expired Pages', index=False)
                
                # Export low engagement pages
                if low_engagement_pages:
                    low_engagement_df = pd.DataFrame(low_engagement_pages)
                    low_engagement_df.to_excel(writer, sheet_name='Low Engagement', index=False)
                
                # Export summary
                summary = self.get_data_summary()
                if summary:
                    summary_df = pd.DataFrame([summary])
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            logging.info(f"Analysis results exported to: {output_path}")
            return True
            
        except Exception as e:
            logging.error(f"Error exporting analysis results: {e}")
            return False
    
    def validate_urls(self, urls: List[str]) -> List[Dict]:
        """Validate URL formats and return validation results"""
        results = []
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        for url in urls:
            is_valid = bool(url_pattern.match(url)) if url.startswith(('http://', 'https://')) else True
            results.append({
                'url': url,
                'is_valid': is_valid,
                'issue': None if is_valid else 'Invalid URL format'
            })
        
        return results
