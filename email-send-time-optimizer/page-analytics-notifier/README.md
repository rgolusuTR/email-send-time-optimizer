# Page Analytics Notification System

A comprehensive web application that analyzes Adobe Analytics page data and automatically sends email notifications to stakeholders about expired pages and low-engagement content.

## Features

- **Excel File Processing**: Upload and analyze Adobe Analytics reports in Excel format
- **Automated Page Analysis**: Identify expired pages (older than 2 years) and low-engagement pages
- **Stakeholder Mapping**: Intelligent URL-to-stakeholder mapping using exact matches, patterns, and department fallbacks
- **Email Notifications**: Send personalized HTML email alerts with actionable recommendations
- **Scheduled Processing**: Automated processing with configurable cron schedules
- **Web Dashboard**: Modern web interface for monitoring, configuration, and manual processing
- **Database Logging**: Track all alerts, processing runs, and system activity
- **Configurable Thresholds**: Customize alert criteria and notification settings

## System Architecture

```
page-analytics-notifier/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── config/                         # Configuration files
│   ├── settings.yaml              # Main system configuration
│   ├── stakeholders.yaml          # Stakeholder mapping rules
│   └── email_templates/           # HTML email templates
│       ├── expired_page.html
│       └── low_engagement.html
├── modules/                        # Core application modules
│   ├── database.py                # Database operations
│   ├── excel_processor.py         # Excel file processing
│   ├── email_service.py           # Email sending functionality
│   ├── stakeholder_mapper.py      # URL-to-stakeholder mapping
│   └── scheduler.py               # Automated scheduling
├── templates/                      # Web interface templates
│   ├── base.html
│   ├── dashboard.html
│   ├── upload.html
│   ├── process_results.html
│   └── configuration.html
├── uploads/                        # File upload directory
├── logs/                          # Application logs
└── data/                          # SQLite database storage
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone or download the project**:

   ```bash
   cd page-analytics-notifier
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the system**:

   - Edit `config/settings.yaml` for email and threshold settings
   - Edit `config/stakeholders.yaml` for stakeholder mapping rules
   - Update email templates in `config/email_templates/` if needed

4. **Run the application**:

   ```bash
   python app.py
   ```

5. **Access the web interface**:
   Open your browser and navigate to `http://localhost:5000`

## Configuration

### Email Configuration (`config/settings.yaml`)

Configure email settings for sending notifications:

```yaml
email:
  # SMTP Configuration
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  use_tls: true
  username: "your-email@gmail.com"
  password: "your-app-password"

  # OR SendGrid Configuration
  sendgrid_api_key: "your-sendgrid-api-key"

  # Email Details
  sender_email: "analytics@yourcompany.com"
  sender_name: "Analytics Team"
```

### Alert Thresholds

Customize when alerts are triggered:

```yaml
thresholds:
  expired_page_days: 730 # Pages older than 2 years
  low_engagement_days: 30 # Recently created pages
  low_engagement_views: 5 # Minimum views for new pages
  alert_cooldown_days: 7 # Days between duplicate alerts
```

### Scheduler Configuration

Set up automated processing:

```yaml
scheduler:
  enabled: true
  cron_schedule: "0 9 * * 1" # Every Monday at 9 AM
  timezone: "UTC"
  auto_start: true
```

### Stakeholder Mapping (`config/stakeholders.yaml`)

Define how pages are mapped to responsible stakeholders:

```yaml
stakeholders:
  # Exact URL matches
  exact_matches:
    "/about-us/": "marketing@company.com"
    "/contact/": "support@company.com"

  # Pattern-based matches (supports wildcards)
  pattern_matches:
    "/blog/*": "content@company.com"
    "/products/*": "product@company.com"
    "/support/*": "support@company.com"

  # Department fallbacks
  department_fallbacks:
    marketing: "marketing@company.com"
    support: "support@company.com"
    default: "webmaster@company.com"
```

## Usage

### Web Interface

1. **Dashboard**: View system statistics, recent alerts, and scheduler status
2. **Upload Report**: Upload Adobe Analytics Excel files for processing
3. **Configuration**: View and validate system configuration

### Excel File Requirements

Your Excel file must contain these columns (case-insensitive):

- **Page URL**: The URL of the page
- **Creation Date**: When the page was created (YYYY-MM-DD format)
- **Page Views**: Number of page views

Example:

```
Page URL          | Creation Date | Page Views
/about-us/        | 2022-01-15   | 1250
/products/laptop/ | 2023-06-20   | 3
/blog/new-post/   | 2024-12-01   | 45
```

### Processing Workflow

1. **Upload**: Upload an Excel file through the web interface
2. **Analysis**: System analyzes pages against configured thresholds
3. **Mapping**: Pages are mapped to stakeholders using the mapping rules
4. **Notifications**: Email alerts are sent to responsible stakeholders
5. **Logging**: All activities are logged to the database

### Email Notifications

The system sends two types of alerts:

#### Expired Page Alert

- Sent for pages older than the configured threshold (default: 2 years)
- Includes page details, age, and recommendations for review/removal
- Suggests content audit and potential archiving

#### Low Engagement Alert

- Sent for recently created pages with low traffic
- Includes engagement metrics and optimization suggestions
- Provides actionable recommendations for improvement

## API Endpoints

The system provides REST API endpoints for integration:

- `GET /api/stats` - Get alert statistics
- `GET /api/alerts` - Get recent alerts
- `POST /scheduler/start` - Start the scheduler
- `POST /scheduler/stop` - Stop the scheduler
- `POST /scheduler/trigger` - Trigger manual processing

## Database Schema

The system uses SQLite with the following tables:

- **alerts**: Stores all email alerts sent
- **processing_runs**: Logs each processing session
- **system_logs**: General system activity logs

## Troubleshooting

### Common Issues

1. **Email not sending**:

   - Check email configuration in `config/settings.yaml`
   - Verify SMTP credentials or SendGrid API key
   - Test email configuration using the web interface

2. **Excel file not processing**:

   - Ensure required columns are present
   - Check file format (.xlsx or .xls)
   - Verify file size is under 50MB

3. **Stakeholder mapping not working**:

   - Validate stakeholder configuration in the web interface
   - Check pattern syntax and email addresses
   - Ensure default fallback is configured

4. **Scheduler not running**:
   - Check scheduler configuration in `config/settings.yaml`
   - Verify cron schedule syntax
   - Check application logs for errors

### Logs

Application logs are stored in the `logs/` directory:

- `app.log`: Main application log
- Check logs for detailed error messages and debugging information

## Security Considerations

- **Email Credentials**: Store sensitive credentials securely
- **File Uploads**: System validates file types and sizes
- **Access Control**: Consider implementing authentication for production use
- **Data Privacy**: Ensure compliance with data protection regulations

## Customization

### Email Templates

Customize email templates in `config/email_templates/`:

- `expired_page.html`: Template for expired page alerts
- `low_engagement.html`: Template for low engagement alerts

Templates support Jinja2 syntax and receive page data as context.

### Thresholds

Adjust alert thresholds in `config/settings.yaml` based on your organization's needs:

- Modify `expired_page_days` for different expiration criteria
- Adjust `low_engagement_days` and `low_engagement_views` for engagement thresholds

### Stakeholder Mapping

Extend stakeholder mapping rules in `config/stakeholders.yaml`:

- Add more exact matches for specific pages
- Create pattern matches for URL structures
- Define department-based fallbacks

## Development

### Adding New Features

1. **New Alert Types**: Extend the analysis logic in `excel_processor.py`
2. **Additional Email Providers**: Add support in `email_service.py`
3. **Enhanced Mapping**: Improve stakeholder mapping in `stakeholder_mapper.py`
4. **Web Interface**: Add new pages and functionality in `templates/`

### Testing

Test the system with sample data:

1. Create a test Excel file with sample page data
2. Configure test email addresses in stakeholder mapping
3. Use the manual processing feature to test functionality
4. Monitor logs for any issues

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review application logs
3. Validate configuration files
4. Test with sample data

## License

This project is provided as-is for internal use. Modify and distribute according to your organization's policies.

## Version History

- **v1.0.0**: Initial release with core functionality
  - Excel file processing
  - Email notifications
  - Web interface
  - Automated scheduling
  - Stakeholder mapping
