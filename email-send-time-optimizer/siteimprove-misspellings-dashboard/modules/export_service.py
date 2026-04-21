import pandas as pd
import xlsxwriter
from io import BytesIO
import base64
from datetime import datetime
from typing import Dict, List
import json

class ExportService:
    """Handle Excel export functionality with charts and data"""
    
    def __init__(self):
        pass
    
    def export_dashboard_to_excel(self, data: Dict, filters: Dict) -> BytesIO:
        """
        Export dashboard data to Excel with multiple sheets and embedded charts
        
        Args:
            data: Dictionary containing all dashboard data
            filters: Applied filters for context
        
        Returns:
            BytesIO object containing the Excel file
        """
        
        output = BytesIO()
        
        # Create workbook and add formats
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1
        })
        
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'bg_color': '#D9E1F2',
            'border': 1
        })
        
        data_format = workbook.add_format({
            'border': 1,
            'align': 'left'
        })
        
        number_format = workbook.add_format({
            'border': 1,
            'num_format': '#,##0'
        })
        
        date_format = workbook.add_format({
            'border': 1,
            'num_format': 'mm/dd/yyyy'
        })
        
        # Create summary sheet
        self._create_summary_sheet(workbook, data, filters, title_format, header_format, data_format, number_format)
        
        # Create detailed data sheets
        if 'detailed_data' in data:
            self._create_detailed_data_sheet(workbook, data['detailed_data'], header_format, data_format, date_format)
        
        # Create trend data sheet
        if 'trend_data' in data:
            self._create_trend_sheet(workbook, data['trend_data'], header_format, data_format)
        
        # Create top words sheet
        if 'top_words' in data:
            self._create_top_words_sheet(workbook, data['top_words'], header_format, data_format, number_format)
        
        # Create language distribution sheet
        if 'language_distribution' in data:
            self._create_language_sheet(workbook, data['language_distribution'], header_format, data_format, number_format)
        
        workbook.close()
        output.seek(0)
        
        return output
    
    def _create_summary_sheet(self, workbook, data: Dict, filters: Dict, title_format, header_format, data_format, number_format):
        """Create summary sheet with key statistics and filters"""
        
        worksheet = workbook.add_worksheet('Summary')
        
        row = 0
        
        # Title
        worksheet.write(row, 0, 'Siteimprove Dashboard Export Summary', title_format)
        worksheet.write(row, 1, '', title_format)
        worksheet.write(row, 2, '', title_format)
        row += 2
        
        # Export info
        worksheet.write(row, 0, 'Export Date:', header_format)
        worksheet.write(row, 1, datetime.now().strftime('%m/%d/%Y %H:%M'), data_format)
        row += 1
        
        # Applied filters
        worksheet.write(row, 0, 'Applied Filters', title_format)
        worksheet.write(row, 1, '', title_format)
        row += 1
        
        if 'websites' in filters:
            worksheet.write(row, 0, 'Websites:', header_format)
            worksheet.write(row, 1, ', '.join(filters['websites']), data_format)
            row += 1
        
        if 'report_types' in filters:
            worksheet.write(row, 0, 'Report Types:', header_format)
            worksheet.write(row, 1, ', '.join(filters['report_types']), data_format)
            row += 1
        
        if 'date_range' in filters:
            worksheet.write(row, 0, 'Date Range:', header_format)
            worksheet.write(row, 1, f"{filters['date_range']['start']} to {filters['date_range']['end']}", data_format)
            row += 1
        
        row += 1
        
        # Summary statistics
        if 'summary_stats' in data:
            worksheet.write(row, 0, 'Summary Statistics', title_format)
            worksheet.write(row, 1, '', title_format)
            row += 1
            
            stats = data['summary_stats']
            
            worksheet.write(row, 0, 'Total Reports:', header_format)
            worksheet.write(row, 1, stats.get('total_reports', 0), number_format)
            row += 1
            
            worksheet.write(row, 0, 'Total Misspellings:', header_format)
            worksheet.write(row, 1, stats.get('total_misspellings', 0), number_format)
            row += 1
            
            worksheet.write(row, 0, 'Total Words to Review:', header_format)
            worksheet.write(row, 1, stats.get('total_words_to_review', 0), number_format)
            row += 1
            
            worksheet.write(row, 0, 'Total Pages Affected:', header_format)
            worksheet.write(row, 1, stats.get('total_pages_affected', 0), number_format)
            row += 1
        
        # Set column widths
        worksheet.set_column(0, 0, 20)
        worksheet.set_column(1, 1, 30)
    
    def _create_detailed_data_sheet(self, workbook, detailed_data: Dict, header_format, data_format, date_format):
        """Create detailed data sheet"""
        
        worksheet = workbook.add_worksheet('Detailed Data')
        
        if not detailed_data.get('data'):
            worksheet.write(0, 0, 'No detailed data available', data_format)
            return
        
        # Headers
        headers = ['Type', 'Word', 'Suggestion', 'Language', 'First Detected', 'Pages', 'Website', 'Report Date']
        
        # Check if we have probability data
        has_probability = any('probability' in item for item in detailed_data['data'])
        if has_probability:
            headers.insert(6, 'Probability')
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Data rows
        for row, item in enumerate(detailed_data['data'], 1):
            col = 0
            worksheet.write(row, col, item.get('type', ''), data_format)
            col += 1
            worksheet.write(row, col, item.get('word', ''), data_format)
            col += 1
            worksheet.write(row, col, item.get('suggestion', ''), data_format)
            col += 1
            worksheet.write(row, col, item.get('language', ''), data_format)
            col += 1
            
            # First detected date
            first_detected = item.get('first_detected')
            if first_detected:
                if isinstance(first_detected, str):
                    worksheet.write(row, col, first_detected, data_format)
                else:
                    worksheet.write(row, col, first_detected, date_format)
            else:
                worksheet.write(row, col, '', data_format)
            col += 1
            
            worksheet.write(row, col, item.get('pages', ''), data_format)
            col += 1
            
            if has_probability:
                worksheet.write(row, col, item.get('probability', ''), data_format)
                col += 1
            
            worksheet.write(row, col, item.get('website', ''), data_format)
            col += 1
            
            # Report date
            report_date = item.get('report_date')
            if report_date:
                if isinstance(report_date, str):
                    worksheet.write(row, col, report_date, data_format)
                else:
                    worksheet.write(row, col, report_date, date_format)
            else:
                worksheet.write(row, col, '', data_format)
        
        # Set column widths
        worksheet.set_column(0, 0, 15)  # Type
        worksheet.set_column(1, 1, 20)  # Word
        worksheet.set_column(2, 2, 20)  # Suggestion
        worksheet.set_column(3, 3, 15)  # Language
        worksheet.set_column(4, 4, 15)  # First Detected
        worksheet.set_column(5, 5, 10)  # Pages
        if has_probability:
            worksheet.set_column(6, 6, 12)  # Probability
            worksheet.set_column(7, 7, 25)  # Website
            worksheet.set_column(8, 8, 15)  # Report Date
        else:
            worksheet.set_column(6, 6, 25)  # Website
            worksheet.set_column(7, 7, 15)  # Report Date
    
    def _create_trend_sheet(self, workbook, trend_data: Dict, header_format, data_format):
        """Create trend data sheet with chart"""
        
        worksheet = workbook.add_worksheet('Trends')
        
        if not trend_data.get('labels') or not trend_data.get('datasets'):
            worksheet.write(0, 0, 'No trend data available', data_format)
            return
        
        # Headers
        headers = ['Date'] + [dataset['label'] for dataset in trend_data['datasets']]
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Data
        labels = trend_data['labels']
        datasets = trend_data['datasets']
        
        for row, label in enumerate(labels, 1):
            worksheet.write(row, 0, label, data_format)
            for col, dataset in enumerate(datasets, 1):
                value = dataset['data'][row-1] if row-1 < len(dataset['data']) else 0
                worksheet.write(row, col, value, data_format)
        
        # Create chart
        if len(labels) > 0 and len(datasets) > 0:
            chart = workbook.add_chart({'type': 'line'})
            
            for col, dataset in enumerate(datasets, 1):
                chart.add_series({
                    'name': dataset['label'],
                    'categories': ['Trends', 1, 0, len(labels), 0],
                    'values': ['Trends', 1, col, len(labels), col],
                    'line': {'color': dataset.get('borderColor', '#000000').replace('rgb(', '').replace(')', '').replace(' ', '')}
                })
            
            chart.set_title({'name': 'Misspellings Trend Over Time'})
            chart.set_x_axis({'name': 'Date'})
            chart.set_y_axis({'name': 'Count'})
            chart.set_size({'width': 720, 'height': 480})
            
            worksheet.insert_chart('E2', chart)
        
        # Set column widths
        worksheet.set_column(0, 0, 15)
        for i in range(1, len(headers)):
            worksheet.set_column(i, i, 12)
    
    def _create_top_words_sheet(self, workbook, top_words_data: Dict, header_format, data_format, number_format):
        """Create top words sheet with chart"""
        
        worksheet = workbook.add_worksheet('Top Words')
        
        if not top_words_data.get('labels') or not top_words_data.get('datasets'):
            worksheet.write(0, 0, 'No top words data available', data_format)
            return
        
        # Headers
        worksheet.write(0, 0, 'Word', header_format)
        worksheet.write(0, 1, 'Pages Affected', header_format)
        
        # Data
        labels = top_words_data['labels']
        data_values = top_words_data['datasets'][0]['data'] if top_words_data['datasets'] else []
        
        for row, (label, value) in enumerate(zip(labels, data_values), 1):
            worksheet.write(row, 0, label, data_format)
            worksheet.write(row, 1, value, number_format)
        
        # Create chart
        if len(labels) > 0:
            chart = workbook.add_chart({'type': 'column'})
            
            chart.add_series({
                'name': 'Pages Affected',
                'categories': ['Top Words', 1, 0, len(labels), 0],
                'values': ['Top Words', 1, 1, len(labels), 1],
            })
            
            chart.set_title({'name': 'Top Misspelled Words by Pages Affected'})
            chart.set_x_axis({'name': 'Words'})
            chart.set_y_axis({'name': 'Pages Affected'})
            chart.set_size({'width': 720, 'height': 480})
            
            worksheet.insert_chart('D2', chart)
        
        # Set column widths
        worksheet.set_column(0, 0, 25)
        worksheet.set_column(1, 1, 15)
    
    def _create_language_sheet(self, workbook, language_data: Dict, header_format, data_format, number_format):
        """Create language distribution sheet with chart"""
        
        worksheet = workbook.add_worksheet('Language Distribution')
        
        if not language_data.get('labels') or not language_data.get('datasets'):
            worksheet.write(0, 0, 'No language data available', data_format)
            return
        
        # Headers
        worksheet.write(0, 0, 'Language', header_format)
        worksheet.write(0, 1, 'Count', header_format)
        
        # Data
        labels = language_data['labels']
        data_values = language_data['datasets'][0]['data'] if language_data['datasets'] else []
        
        for row, (label, value) in enumerate(zip(labels, data_values), 1):
            worksheet.write(row, 0, label, data_format)
            worksheet.write(row, 1, value, number_format)
        
        # Create chart
        if len(labels) > 0:
            chart = workbook.add_chart({'type': 'pie'})
            
            chart.add_series({
                'name': 'Language Distribution',
                'categories': ['Language Distribution', 1, 0, len(labels), 0],
                'values': ['Language Distribution', 1, 1, len(labels), 1],
            })
            
            chart.set_title({'name': 'Language Distribution'})
            chart.set_size({'width': 480, 'height': 480})
            
            worksheet.insert_chart('D2', chart)
        
        # Set column widths
        worksheet.set_column(0, 0, 20)
        worksheet.set_column(1, 1, 15)
