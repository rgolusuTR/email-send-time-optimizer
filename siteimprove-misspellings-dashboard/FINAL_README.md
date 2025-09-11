# Siteimprove Misspellings Dashboard

A comprehensive web-based dashboard application for uploading, analyzing, and visualizing Siteimprove spelling reports across multiple Thomson Reuters websites.

## 🚀 Features

### ✅ Completed Features

1. **Report Upload & Processing**

   - Upload CSV and Excel files from Siteimprove
   - Auto-detection of report types (Misspellings, Words to Review, Pages with Misspellings, Misspelling History)
   - Automatic parsing starting from row 4 (skipping metadata)
   - Support for multiple websites: tax.thomsonreuters.com, thomsonreuters.com, legal.thomsonreuters.com, thompsonwriters.co.ca, Legal UK website

2. **Data Visualization**

   - Interactive dashboard with summary statistics
   - Line charts for trends over time (daily, weekly, monthly, yearly)
   - Bar charts for top misspelled words
   - Pie charts for language distribution
   - Detailed data tables with sorting and filtering

3. **Advanced Filtering**

   - Filter by website(s)
   - Filter by report type
   - Date range picker
   - Search functionality for words, pages, etc.

4. **Export Functionality**

   - Export dashboard views to Excel
   - Include all charts, tables, and summary data
   - Customizable export based on current filters

5. **Responsive Design**
   - Mobile-friendly interface
   - Bootstrap-based UI
   - Intuitive navigation

## 📁 Project Structure

```
siteimprove-misspellings-dashboard/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── database/
│   └── models.py                   # SQLAlchemy database models
├── modules/
│   ├── simple_parser.py            # CSV/Excel file parser
│   ├── data_processor.py           # Data processing and aggregation
│   └── export_service.py           # Excel export functionality
├── templates/
│   ├── base.html                   # Base template
│   ├── dashboard.html              # Main dashboard
│   └── upload.html                 # File upload page
├── static/
│   ├── css/dashboard.css           # Custom styles
│   └── js/dashboard.js             # Frontend JavaScript
└── test_files/                     # Test files and utilities
```

## 🛠 Installation & Setup

### Prerequisites

- Python 3.8+
- pip package manager

### Installation Steps

1. **Clone/Navigate to the project directory:**

   ```bash
   cd siteimprove-misspellings-dashboard
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**

   ```bash
   python app.py
   ```

4. **Access the dashboard:**
   Open your browser and navigate to: `http://localhost:5001`

## 📊 Data Models

### Supported Report Types

1. **Misspellings Report**

   - Word, Spelling Suggestion, Language, First Detected, Pages

2. **Words to Review Report**

   - Word, Spelling Suggestion, Language, First Detected, Misspelling Probability, Pages

3. **Pages with Misspellings Report**

   - Title, URL, Page Report Link, CMS Link, Misspellings, Words to Review, Page Level

4. **Misspelling History Report**
   - Report Date, Misspellings, Words to Review (Total Words column ignored)

## 🎯 Usage Guide

### Uploading Reports

1. Navigate to the Upload page
2. Select the target website from the dropdown
3. Choose "Auto-detect from file content" or manually select report type
4. Upload your CSV or Excel file
5. The system will automatically parse and store the data

### Using the Dashboard

1. **Filters Panel (Left Side):**

   - Select one or more websites
   - Choose report types to analyze
   - Set date range for analysis

2. **Main Dashboard:**

   - View summary statistics (Total Reports, Misspellings, Words to Review, Pages Affected)
   - Analyze trends over time with interactive charts
   - Explore top misspelled words and language distributions
   - Browse detailed data with search and pagination

3. **Export Data:**
   - Click the "Export to Excel" button
   - Downloads include all current dashboard data based on active filters

### File Format Requirements

- **Supported formats:** CSV, Excel (.xlsx, .xls)
- **File structure:**
  - Row 1: Created date and time
  - Row 2: Site name
  - Row 3: Empty row
  - Row 4+: Column headers and data
- **Maximum file size:** 16MB

## 🔧 Technical Details

### Backend Technologies

- **Flask:** Web framework
- **SQLAlchemy:** Database ORM
- **Pandas:** Data processing
- **OpenPyXL:** Excel file handling

### Frontend Technologies

- **Bootstrap 5:** UI framework
- **Chart.js:** Data visualization
- **jQuery:** DOM manipulation
- **DataTables:** Advanced table features

### Database

- **SQLite:** Default database (easily configurable for PostgreSQL/MySQL)
- **Models:** Website, Report, Misspelling, WordToReview, PageWithMisspelling, MisspellingHistory

## 🧪 Testing

The project includes several test files:

```bash
# Test the file parser
python test_simple_parser.py

# Test the complete application
python test_app.py
```

## 🚀 Deployment

### Production Considerations

1. **Database:** Configure PostgreSQL or MySQL for production
2. **Security:** Update the SECRET_KEY in app.py
3. **File Storage:** Consider cloud storage for uploaded files
4. **Performance:** Add caching for frequently accessed data

### Environment Variables

```bash
export FLASK_ENV=production
export DATABASE_URL=postgresql://user:pass@localhost/dbname
export SECRET_KEY=your-production-secret-key
```

## 📈 Performance Features

- **Pagination:** Large datasets are paginated for better performance
- **Lazy Loading:** Charts and data load on demand
- **Efficient Queries:** Optimized database queries with proper indexing
- **File Cleanup:** Uploaded files are automatically cleaned after processing

## 🔒 Security Features

- **File Validation:** Strict file type and size validation
- **Secure Filenames:** Automatic filename sanitization
- **SQL Injection Protection:** SQLAlchemy ORM prevents SQL injection
- **XSS Protection:** Template escaping prevents cross-site scripting

## 🐛 Troubleshooting

### Common Issues

1. **File Upload Fails:**

   - Check file format (CSV/Excel only)
   - Ensure file size is under 16MB
   - Verify file structure (metadata in first 3 rows)

2. **Charts Not Loading:**

   - Check browser console for JavaScript errors
   - Ensure all static files are accessible
   - Verify data is available for selected filters

3. **Database Errors:**
   - Check if database file has write permissions
   - Ensure all required tables are created
   - Restart the application to reinitialize database

## 📞 Support

For technical support or feature requests, please refer to the project documentation or contact the development team.

## 🎉 Success Metrics

The dashboard successfully addresses all requirements:

✅ **File Upload:** Supports CSV/Excel with automatic parsing  
✅ **Multi-Website Support:** All Thomson Reuters websites configured  
✅ **Report Types:** All 4 report types supported  
✅ **Visualizations:** Line, bar, pie charts and tables  
✅ **Filtering:** Website, report type, date range, search  
✅ **Export:** Excel export with current dashboard view  
✅ **Responsive Design:** Mobile and desktop friendly  
✅ **User Experience:** Intuitive navigation and tooltips

The application is production-ready and provides a comprehensive solution for Siteimprove report analysis and visualization.
