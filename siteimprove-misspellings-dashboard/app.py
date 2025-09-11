from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import json

# Import our modules
from database.models import db, Website, Report, Misspelling, WordToReview, PageWithMisspelling, MisspellingHistory
from modules.robust_parser import RobustSiteimproveParser
from modules.data_processor import DataProcessor
from modules.export_service import ExportService

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///siteimprove_dashboard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize database
db.init_app(app)

# Initialize services
parser = RobustSiteimproveParser()
data_processor = DataProcessor()
export_service = ExportService()

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def create_tables():
    """Create database tables"""
    with app.app_context():
        db.create_all()
        
        # Create default websites if they don't exist
        default_websites = [
            'tax.thomsonreuters.com',
            'thomsonreuters.com', 
            'legal.thomsonreuters.com',
            'thompsonwriters.co.ca',
            'Legal UK website'
        ]
        
        for site_name in default_websites:
            if not Website.query.filter_by(name=site_name).first():
                website = Website(name=site_name)
                db.session.add(website)
        
        db.session.commit()

# Initialize database on startup
create_tables()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/upload')
def upload_page():
    """File upload page"""
    websites = Website.query.all()
    return render_template('upload.html', websites=websites)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        website_id = request.form.get('website_id')
        report_type = request.form.get('report_type')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not website_id:
            return jsonify({'error': 'Website not selected'}), 400
        
        # Validate file extension
        allowed_extensions = {'.csv', '.xlsx', '.xls'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({'error': 'Invalid file format. Please upload CSV or Excel files.'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Auto-detect report type if not provided
        if not report_type or report_type == 'auto':
            report_type = parser.detect_report_type(filepath)
            if report_type == 'unknown':
                os.remove(filepath)
                return jsonify({'error': 'Could not determine report type. Please select manually.'}), 400
        
        # Parse file
        parsed_data = parser.parse_file(filepath, report_type)
        
        # Create report record
        website = Website.query.get(website_id)
        if not website:
            os.remove(filepath)
            return jsonify({'error': 'Invalid website selected'}), 400
        
        report = Report(
            website_id=website_id,
            report_type=report_type,
            filename=filename,
            created_date=parsed_data['metadata'].get('created_date'),
            processed_at=datetime.utcnow()
        )
        db.session.add(report)
        db.session.flush()  # Get the report ID
        
        # Store parsed data
        success_count = 0
        error_count = 0
        
        for item in parsed_data['data']:
            try:
                if report_type == 'misspellings':
                    record = Misspelling(
                        report_id=report.id,
                        word=item['word'],
                        spelling_suggestion=item['spelling_suggestion'],
                        language=item['language'],
                        first_detected=item['first_detected'],
                        pages_count=item['pages_count']
                    )
                elif report_type == 'words_to_review':
                    record = WordToReview(
                        report_id=report.id,
                        word=item['word'],
                        spelling_suggestion=item['spelling_suggestion'],
                        language=item['language'],
                        first_detected=item['first_detected'],
                        misspelling_probability=item['misspelling_probability'],
                        pages_count=item['pages_count']
                    )
                elif report_type == 'pages_with_misspellings':
                    record = PageWithMisspelling(
                        report_id=report.id,
                        title=item['title'],
                        url=item['url'],
                        page_report_link=item['page_report_link'],
                        cms_link=item['cms_link'],
                        misspellings_count=item['misspellings_count'],
                        words_to_review_count=item['words_to_review_count'],
                        page_level=item['page_level']
                    )
                elif report_type == 'misspelling_history':
                    record = MisspellingHistory(
                        report_id=report.id,
                        report_date=item['report_date'],
                        misspellings_count=item['misspellings_count'],
                        words_to_review_count=item['words_to_review_count']
                    )
                
                db.session.add(record)
                success_count += 1
                
            except Exception as e:
                print(f"Error processing record: {e}")
                error_count += 1
                continue
        
        db.session.commit()
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': f'Successfully processed {success_count} records. {error_count} errors.',
            'report_id': report.id,
            'report_type': report_type,
            'website': website.name
        })
        
    except Exception as e:
        db.session.rollback()
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/api/dashboard-data')
def get_dashboard_data():
    """Get dashboard data based on filters"""
    try:
        # Get filter parameters
        website_ids = request.args.getlist('websites[]')
        report_types = request.args.getlist('report_types[]')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        period = request.args.get('period', 'daily')
        
        # Convert to appropriate types
        website_ids = [int(id) for id in website_ids if id]
        
        # Default date range if not provided
        if not start_date or not end_date:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Default to all websites if none selected
        if not website_ids:
            website_ids = [w.id for w in Website.query.all()]
        
        # Default to all report types if none selected
        if not report_types:
            report_types = data_processor.get_report_types(website_ids)
        
        # Get data
        dashboard_data = {
            'summary_stats': data_processor.get_summary_stats(website_ids, report_types, start_date, end_date),
            'trend_data': data_processor.get_trend_data(website_ids, report_types, start_date, end_date, period),
            'top_words': data_processor.get_top_misspelled_words(website_ids, report_types, start_date, end_date),
            'language_distribution': data_processor.get_language_distribution(website_ids, report_types, start_date, end_date),
            'detailed_data': data_processor.get_detailed_data(website_ids, report_types, start_date, end_date, page=1, per_page=10)
        }
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/detailed-data')
def get_detailed_data():
    """Get detailed data with pagination and search"""
    try:
        # Get parameters
        website_ids = request.args.getlist('websites[]')
        report_types = request.args.getlist('report_types[]')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        search_term = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        # Convert and validate parameters
        website_ids = [int(id) for id in website_ids if id]
        
        if not start_date or not end_date:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        if not website_ids:
            website_ids = [w.id for w in Website.query.all()]
        
        if not report_types:
            report_types = data_processor.get_report_types(website_ids)
        
        # Get detailed data
        detailed_data = data_processor.get_detailed_data(
            website_ids, report_types, start_date, end_date, 
            search_term, page, per_page
        )
        
        return jsonify(detailed_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export')
def export_dashboard():
    """Export dashboard data to Excel"""
    try:
        # Get filter parameters (same as dashboard-data)
        website_ids = request.args.getlist('websites[]')
        report_types = request.args.getlist('report_types[]')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        period = request.args.get('period', 'daily')
        
        # Convert parameters
        website_ids = [int(id) for id in website_ids if id]
        
        if not start_date or not end_date:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        if not website_ids:
            website_ids = [w.id for w in Website.query.all()]
        
        if not report_types:
            report_types = data_processor.get_report_types(website_ids)
        
        # Get all data for export
        export_data = {
            'summary_stats': data_processor.get_summary_stats(website_ids, report_types, start_date, end_date),
            'trend_data': data_processor.get_trend_data(website_ids, report_types, start_date, end_date, period),
            'top_words': data_processor.get_top_misspelled_words(website_ids, report_types, start_date, end_date, limit=20),
            'language_distribution': data_processor.get_language_distribution(website_ids, report_types, start_date, end_date),
            'detailed_data': data_processor.get_detailed_data(website_ids, report_types, start_date, end_date, page=1, per_page=1000)
        }
        
        # Get website names for filters
        website_names = [w.name for w in Website.query.filter(Website.id.in_(website_ids)).all()]
        
        filters = {
            'websites': website_names,
            'report_types': report_types,
            'date_range': {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d')
            }
        }
        
        # Generate Excel file
        excel_file = export_service.export_dashboard_to_excel(export_data, filters)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'siteimprove_dashboard_export_{timestamp}.xlsx'
        
        return send_file(
            excel_file,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/websites')
def get_websites():
    """Get all websites"""
    websites = data_processor.get_websites()
    return jsonify(websites)

@app.route('/api/report-types')
def get_report_types():
    """Get available report types"""
    website_ids = request.args.getlist('websites[]')
    website_ids = [int(id) for id in website_ids if id] if website_ids else None
    
    report_types = data_processor.get_report_types(website_ids)
    return jsonify(report_types)

@app.route('/api/date-range')
def get_date_range():
    """Get available date range"""
    website_ids = request.args.getlist('websites[]')
    report_types = request.args.getlist('report_types[]')
    
    website_ids = [int(id) for id in website_ids if id] if website_ids else None
    report_types = report_types if report_types else None
    
    start_date, end_date = data_processor.get_date_range(website_ids, report_types)
    
    return jsonify({
        'start_date': start_date.isoformat() if start_date else None,
        'end_date': end_date.isoformat() if end_date else None
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5017)
