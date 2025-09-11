# Siteimprove Misspellings Dashboard

A comprehensive web-based dashboard application for uploading, analyzing, and visualizing Siteimprove spelling reports across multiple websites. The dashboard provides insights into misspellings, words to review, and trends over time with powerful filtering and export capabilities.

## Features

### 📊 Dashboard Analytics

- **Summary Statistics**: Total reports, misspellings, words to review, and pages affected
- **Trend Analysis**: Line charts showing misspellings trends over time (daily, weekly, monthly, yearly)
- **Top Words**: Bar charts displaying most frequently misspelled words
- **Language Distribution**: Pie charts showing distribution of issues by language
- **Recent Issues**: Quick view of latest spelling problems

### 📁 File Upload & Processing

- **Multiple Formats**: Support for CSV and Excel files (.csv, .xlsx, .xls)
- **Auto-Detection**: Automatically detects report type from file content
- **Drag & Drop**: User-friendly file upload with drag and drop support
- **Progress Tracking**: Real-time upload and processing progress
- **Error Handling**: Comprehensive error reporting and validation

### 🔍 Advanced Filtering

- **Website Selection**: Filter by one or multiple websites
- **Report Types**: Filter by misspellings, words to review, pages with misspellings, or history
- **Date Range**: Custom date range selection with calendar picker
- **Time Periods**: Group data by daily, weekly, monthly, or yearly periods
- **Search**: Full-text search across words and suggestions

### 📈 Data Visualization

- **Interactive Charts**: Built with Chart.js for responsive, interactive visualizations
- **Drill-down Capability**: Click charts to explore underlying data
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Real-time Updates**: Charts update automatically when filters change

### 📤 Export Functionality

- **Excel Export**: Download complete dashboard data as Excel files
- **Filtered Exports**: Export respects current filter settings
- **Multiple Sheets**: Organized data across multiple Excel worksheets
- **Summary Reports**: Include charts and summary statistics in exports

## Supported Report Types

### 1. Misspellings Report

- **Columns**: Word, Spelling Suggestion, Language, First Detected, Pages
- **Purpose**: Track actual misspellings found on websites

### 2. Words to Review Report

- **Columns**: Word, Spelling Suggestion, Language, First Detected, Misspelling Probability, Pages
- **Purpose**: Monitor words flagged for potential spelling issues

### 3. Pages with Misspellings Report

- **Columns**: Title, URL, Page Report Link, CMS Link, Misspellings, Words to Review, Page Level
- **Purpose**: Identify specific pages containing spelling issues

### 4. Misspelling History Report

- **Columns**: Report Date, Misspellings, Words to Review
- **Purpose**: Track spelling issue trends over time

## Supported Websites

The dashboard supports the following Thomson Reuters websites:

- tax.thomsonreuters.com
- thomsonreuters.com
- legal.thomsonreuters.com
- thompsonwriters.co.ca
- Legal UK website

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone or download the project**

   ```bash
   cd siteimprove-misspellings-dashboard
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**

   ```bash
   python app.py
   ```

   The application will automatically create the SQLite database and default websites on first run.

4. **Access the application**
   Open your web browser and navigate to: `http://localhost:5000`

## Usage Guide

### 1. Uploading Reports

1. Navigate to the **Upload Reports** page
2. Select the target website from the dropdown
3. Choose the report type (or leave as "Auto-detect")
4. Upload your CSV or Excel file using:
   - File browser (click "Browse")
   - Drag and drop onto the upload area
5. Click "Upload and Process"
6. Monitor the progress bar and wait for completion
7. Review the results and navigate to the dashboard

### 2. Using the Dashboard

#### Applying Filters

1. Use the sidebar filters to customize your view:
   - **Websites**: Select one or multiple websites
   - **Report Types**: Choose specific report types
   - **Date Range**: Set custom date ranges
   - **Period**: Group data by time periods
2. Click "Apply Filters" to update the dashboard

#### Viewing Data

- **Summary Cards**: View high-level statistics at the top
- **Charts**: Analyze trends and distributions in the main area
- **Detailed Table**: Browse individual records at the bottom
- **Search**: Use the search box to find specific words

#### Exporting Data

1. Configure your desired filters
2. Click "Export to Excel" in the sidebar
3. Wait for the file to generate and download
4. Open the Excel file to view organized data and charts

### 3. File Format Requirements

#### File Structure

- **Row 1**: Report metadata (automatically skipped)
- **Row 2**: Website information (automatically skipped)
- **Row 3**: Empty row (automatically skipped)
- **Row 4**: Column headers
- **Row 5+**: Data rows

#### Supported Formats

- **CSV**: Comma-separated values (.csv)
- **Excel**: Microsoft Excel files (.xlsx, .xls)
- **Size Limit**: Maximum 16MB per file

## Technical Architecture

### Backend (Python/Flask)

- **Framework**: Flask web framework
- **Database**: SQLite with SQLAlchemy ORM
- **File Processing**: pandas for CSV/Excel parsing
- **Export**: openpyxl for Excel generation

### Frontend (HTML/CSS/JavaScript)

- **UI Framework**: Bootstrap 5
- **Charts**: Chart.js for data visualization
- **Date Picker**: Flatpickr for date range selection
- **Icons**: Font Awesome for UI icons

### Database Schema

- **Websites**: Store website information
- **Reports**: Track uploaded report metadata
- **Misspellings**: Store misspelling data
- **WordsToReview**: Store words flagged for review
- **PagesWithMisspellings**: Store page-level spelling issues
- **MisspellingHistory**: Store historical trend data

## API Endpoints

### Data Endpoints

- `GET /api/websites` - Get all websites
- `GET /api/dashboard-data` - Get dashboard data with filters
- `GET /api/detailed-data` - Get paginated detailed data
- `GET /api/export` - Export dashboard data to Excel

### Upload Endpoints

- `POST /api/upload` - Upload and process report files

### Filter Endpoints

- `GET /api/report-types` - Get available report types
- `GET /api/date-range` - Get available date ranges

## Configuration

### Environment Variables

- `FLASK_ENV`: Set to 'development' for debug mode
- `SECRET_KEY`: Change the default secret key for production

### Database Configuration

- Default: SQLite database (`siteimprove_dashboard.db`)
- Configurable via `SQLALCHEMY_DATABASE_URI` in app.py

### File Upload Configuration

- **Upload Directory**: `static/uploads`
- **Max File Size**: 16MB
- **Allowed Extensions**: .csv, .xlsx, .xls

## Troubleshooting

### Common Issues

#### Upload Failures

- **File too large**: Ensure file is under 16MB
- **Invalid format**: Use only CSV or Excel files
- **Corrupted data**: Check that data starts from row 4
- **Missing columns**: Verify all required columns are present

#### Dashboard Loading Issues

- **No data**: Upload reports first or check filter settings
- **Slow performance**: Reduce date range or limit websites
- **Chart errors**: Refresh the page or clear browser cache

#### Export Problems

- **Download fails**: Check browser download settings
- **Empty file**: Verify filters return data
- **Excel errors**: Ensure Excel is installed to open files

### Performance Optimization

- **Large datasets**: Use smaller date ranges for better performance
- **Multiple websites**: Filter to specific websites when possible
- **Regular cleanup**: Remove old uploaded files periodically

## Development

### Project Structure

```
siteimprove-misspellings-dashboard/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This documentation
├── database/
│   └── models.py         # Database models
├── modules/
│   ├── file_parser.py    # File parsing logic
│   ├── data_processor.py # Data processing and queries
│   └── export_service.py # Excel export functionality
├── templates/
│   ├── base.html         # Base template
│   ├── dashboard.html    # Dashboard page
│   └── upload.html       # Upload page
└── static/
    ├── css/
    │   └── dashboard.css # Custom styles
    └── js/
        └── dashboard.js  # Dashboard JavaScript
```

### Adding New Features

1. **New Report Types**: Update `file_parser.py` and add database models
2. **Additional Charts**: Extend `dashboard.js` and add Chart.js configurations
3. **New Filters**: Update both frontend filters and backend API endpoints
4. **Export Formats**: Extend `export_service.py` for new export types

### Database Migrations

When modifying database models:

1. Delete the existing database file
2. Restart the application to recreate tables
3. Re-upload your data

## Security Considerations

### File Upload Security

- File type validation
- File size limits
- Secure filename handling
- Temporary file cleanup

### Data Protection

- Input sanitization
- SQL injection prevention via SQLAlchemy
- XSS protection in templates

### Production Deployment

- Change default secret key
- Use environment variables for configuration
- Implement proper logging
- Set up HTTPS
- Configure proper file permissions

## Support

For issues, questions, or feature requests:

1. Check the troubleshooting section above
2. Review the file format requirements
3. Verify your data follows the expected structure
4. Test with a smaller dataset first

## License

This project is developed for Thomson Reuters internal use for analyzing Siteimprove spelling reports and improving website content quality.
