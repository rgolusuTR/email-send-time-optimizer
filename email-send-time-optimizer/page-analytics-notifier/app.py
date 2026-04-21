"""
Main Flask application for Page Analytics Notification System
Web interface for managing and monitoring the notification system
"""

import os
import logging
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
import yaml

# Import our modules
from modules.excel_processor import ExcelProcessor
from modules.email_service import EmailService
from modules.stakeholder_mapper import StakeholderMapper
from modules.database import DatabaseManager
from modules.scheduler import NotificationScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

# Create Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # Change this in production

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('logs', exist_ok=True)
os.makedirs('data', exist_ok=True)

# Initialize components
db = DatabaseManager()
scheduler = NotificationScheduler()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_config():
    """Load configuration from YAML file"""
    try:
        with open('config/settings.yaml', 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        return {}

@app.route('/')
def index():
    """Main dashboard page"""
    try:
        # Get recent statistics
        stats = db.get_alert_statistics(30)
        recent_alerts = db.get_recent_alerts(10)
        scheduler_status = scheduler.get_scheduler_status()
        
        return render_template('dashboard.html', 
                             stats=stats, 
                             recent_alerts=recent_alerts,
                             scheduler_status=scheduler_status)
    except Exception as e:
        logging.error(f"Error loading dashboard: {e}")
        flash(f"Error loading dashboard: {e}", 'error')
        return render_template('dashboard.html', stats={}, recent_alerts=[], scheduler_status={})

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """File upload page"""
    if request.method == 'POST':
        try:
            # Check if file was uploaded
            if 'file' not in request.files:
                flash('No file selected', 'error')
                return redirect(request.url)
            
            file = request.files['file']
            if file.filename == '':
                flash('No file selected', 'error')
                return redirect(request.url)
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to filename to avoid conflicts
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                flash(f'File uploaded successfully: {filename}', 'success')
                return redirect(url_for('process_file', filename=filename))
            else:
                flash('Invalid file type. Please upload .xlsx or .xls files only.', 'error')
                
        except Exception as e:
            logging.error(f"Error uploading file: {e}")
            flash(f'Error uploading file: {e}', 'error')
    
    return render_template('upload.html')

@app.route('/process/<filename>')
def process_file(filename):
    """Process uploaded file"""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            flash('File not found', 'error')
            return redirect(url_for('upload_file'))
        
        # Initialize processor
        processor = ExcelProcessor()
        
        # Read and validate file
        if not processor.read_excel_file(filepath):
            flash('Error reading Excel file. Please check the file format and required columns.', 'error')
            return redirect(url_for('upload_file'))
        
        # Get data summary
        summary = processor.get_data_summary()
        
        # Get configuration for analysis
        config = load_config()
        thresholds = config.get('thresholds', {})
        
        # Analyze pages
        expired_pages, low_engagement_pages = processor.analyze_pages(
            thresholds.get('expired_page_days', 730),
            thresholds.get('low_engagement_days', 30),
            thresholds.get('low_engagement_views', 5)
        )
        
        return render_template('process_results.html',
                             filename=filename,
                             summary=summary,
                             expired_pages=expired_pages,
                             low_engagement_pages=low_engagement_pages,
                             thresholds=thresholds)
        
    except Exception as e:
        logging.error(f"Error processing file {filename}: {e}")
        flash(f'Error processing file: {e}', 'error')
        return redirect(url_for('upload_file'))

@app.route('/send_alerts/<filename>', methods=['POST'])
def send_alerts(filename):
    """Send email alerts for processed file"""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'File not found'})
        
        start_time = time.time()
        
        # Initialize components
        processor = ExcelProcessor()
        email_service = EmailService()
        mapper = StakeholderMapper()
        
        # Process file
        if not processor.read_excel_file(filepath):
            return jsonify({'success': False, 'error': 'Error reading Excel file'})
        
        # Get configuration
        config = load_config()
        thresholds = config.get('thresholds', {})
        
        # Analyze pages
        expired_pages, low_engagement_pages = processor.analyze_pages(
            thresholds.get('expired_page_days', 730),
            thresholds.get('low_engagement_days', 30),
            thresholds.get('low_engagement_views', 5)
        )
        
        total_pages = len(processor.data) if processor.data is not None else 0
        alerts_generated = 0
        emails_sent = 0
        errors = 0
        
        # Send expired page alerts
        for page in expired_pages:
            try:
                recipient = mapper.get_stakeholder_email(page['page_url'])
                
                # Check if alert was sent recently
                if db.check_recent_alert(page['page_url'], 'expired', 7):
                    continue
                
                if email_service.send_expired_page_alert(page, recipient):
                    db.log_alert(
                        page['page_url'], 'expired', recipient,
                        page['creation_date'], page['page_views'],
                        page['page_age_days'], 'sent'
                    )
                    emails_sent += 1
                else:
                    db.log_alert(
                        page['page_url'], 'expired', recipient,
                        page['creation_date'], page['page_views'],
                        page['page_age_days'], 'failed', 'Email sending failed'
                    )
                    errors += 1
                
                alerts_generated += 1
                
            except Exception as e:
                logging.error(f"Error sending alert for {page['page_url']}: {e}")
                errors += 1
        
        # Send low engagement alerts
        for page in low_engagement_pages:
            try:
                recipient = mapper.get_stakeholder_email(page['page_url'])
                
                # Check if alert was sent recently
                if db.check_recent_alert(page['page_url'], 'low_engagement', 7):
                    continue
                
                if email_service.send_low_engagement_alert(page, recipient):
                    db.log_alert(
                        page['page_url'], 'low_engagement', recipient,
                        page['creation_date'], page['page_views'],
                        page['days_since_creation'], 'sent'
                    )
                    emails_sent += 1
                else:
                    db.log_alert(
                        page['page_url'], 'low_engagement', recipient,
                        page['creation_date'], page['page_views'],
                        page['days_since_creation'], 'failed', 'Email sending failed'
                    )
                    errors += 1
                
                alerts_generated += 1
                
            except Exception as e:
                logging.error(f"Error sending alert for {page['page_url']}: {e}")
                errors += 1
        
        # Log processing run
        processing_time = time.time() - start_time
        db.log_processing_run(filename, total_pages, alerts_generated, emails_sent, errors, processing_time)
        
        return jsonify({
            'success': True,
            'total_pages': total_pages,
            'alerts_generated': alerts_generated,
            'emails_sent': emails_sent,
            'errors': errors,
            'processing_time': round(processing_time, 2)
        })
        
    except Exception as e:
        logging.error(f"Error sending alerts: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/configuration')
def configuration():
    """Configuration management page"""
    try:
        config = load_config()
        
        # Load stakeholder configuration
        with open('config/stakeholders.yaml', 'r') as file:
            stakeholder_config = yaml.safe_load(file)
        
        # Validate stakeholder configuration
        mapper = StakeholderMapper()
        validation_results = mapper.validate_stakeholder_config()
        
        return render_template('configuration.html',
                             config=config,
                             stakeholder_config=stakeholder_config,
                             validation_results=validation_results)
        
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        flash(f'Error loading configuration: {e}', 'error')
        return render_template('configuration.html', config={}, stakeholder_config={}, validation_results={})

@app.route('/test_email', methods=['POST'])
def test_email():
    """Test email configuration"""
    try:
        email = request.form.get('email')
        if not email:
            return jsonify({'success': False, 'error': 'Email address required'})
        
        email_service = EmailService()
        success = email_service.send_test_email(email)
        
        if success:
            return jsonify({'success': True, 'message': 'Test email sent successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to send test email'})
            
    except Exception as e:
        logging.error(f"Error sending test email: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/scheduler/start', methods=['POST'])
def start_scheduler():
    """Start the scheduler"""
    try:
        success = scheduler.start_scheduler()
        if success:
            return jsonify({'success': True, 'message': 'Scheduler started successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to start scheduler'})
    except Exception as e:
        logging.error(f"Error starting scheduler: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/scheduler/stop', methods=['POST'])
def stop_scheduler():
    """Stop the scheduler"""
    try:
        success = scheduler.stop_scheduler()
        if success:
            return jsonify({'success': True, 'message': 'Scheduler stopped successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to stop scheduler'})
    except Exception as e:
        logging.error(f"Error stopping scheduler: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/scheduler/trigger', methods=['POST'])
def trigger_manual_run():
    """Trigger manual processing run"""
    try:
        success = scheduler.trigger_manual_run()
        if success:
            return jsonify({'success': True, 'message': 'Manual processing triggered successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to trigger manual processing'})
    except Exception as e:
        logging.error(f"Error triggering manual run: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    try:
        stats = db.get_alert_statistics(30)
        return jsonify(stats)
    except Exception as e:
        logging.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts')
def api_alerts():
    """API endpoint for recent alerts"""
    try:
        limit = request.args.get('limit', 50, type=int)
        alerts = db.get_recent_alerts(limit)
        return jsonify(alerts)
    except Exception as e:
        logging.error(f"Error getting alerts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-email', methods=['POST'])
def api_test_email():
    """API endpoint for testing email configuration"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'success': False, 'error': 'Email address required'})
        
        email_service = EmailService()
        success = email_service.send_test_email(email)
        
        if success:
            return jsonify({'success': True, 'message': 'Test email sent successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to send test email'})
            
    except Exception as e:
        logging.error(f"Error sending test email: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/validate-stakeholders')
def api_validate_stakeholders():
    """API endpoint for validating stakeholder configuration"""
    try:
        mapper = StakeholderMapper()
        validation_results = mapper.validate_stakeholder_config()
        return jsonify(validation_results)
    except Exception as e:
        logging.error(f"Error validating stakeholders: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    flash('File is too large. Maximum size is 50MB.', 'error')
    return redirect(url_for('upload_file'))

if __name__ == '__main__':
    # Start scheduler if enabled
    config = load_config()
    if config.get('scheduler', {}).get('enabled', False):
        scheduler.start_scheduler()
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
