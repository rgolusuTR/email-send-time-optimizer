"""
Scheduler module for Page Analytics Notification System
Handles automated processing and scheduling
"""

import logging
import yaml
from datetime import datetime
from typing import Dict, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import time
import os

class NotificationScheduler:
    def __init__(self, config_path: str = "config/settings.yaml"):
        """Initialize scheduler with configuration"""
        self.config = self._load_config(config_path)
        self.scheduler_config = self.config.get('scheduler', {})
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            return {}
    
    def start_scheduler(self) -> bool:
        """Start the background scheduler"""
        try:
            if self.is_running:
                logging.warning("Scheduler is already running")
                return True
            
            if not self.scheduler_config.get('enabled', False):
                logging.info("Scheduler is disabled in configuration")
                return False
            
            # Add the main processing job
            cron_schedule = self.scheduler_config.get('cron_schedule', '0 9 * * 1')  # Default: Monday 9 AM
            timezone = self.scheduler_config.get('timezone', 'UTC')
            
            # Parse cron schedule (minute hour day month day_of_week)
            cron_parts = cron_schedule.split()
            if len(cron_parts) != 5:
                logging.error(f"Invalid cron schedule format: {cron_schedule}")
                return False
            
            trigger = CronTrigger(
                minute=cron_parts[0],
                hour=cron_parts[1],
                day=cron_parts[2],
                month=cron_parts[3],
                day_of_week=cron_parts[4],
                timezone=timezone
            )
            
            self.scheduler.add_job(
                func=self._scheduled_processing,
                trigger=trigger,
                id='analytics_processing',
                name='Page Analytics Processing',
                replace_existing=True
            )
            
            # Add cleanup job (weekly)
            self.scheduler.add_job(
                func=self._cleanup_old_data,
                trigger=CronTrigger(hour=2, minute=0, day_of_week=0),  # Sunday 2 AM
                id='cleanup_job',
                name='Database Cleanup',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.is_running = True
            
            logging.info(f"Scheduler started with cron schedule: {cron_schedule}")
            return True
            
        except Exception as e:
            logging.error(f"Error starting scheduler: {e}")
            return False
    
    def stop_scheduler(self) -> bool:
        """Stop the background scheduler"""
        try:
            if not self.is_running:
                logging.warning("Scheduler is not running")
                return True
            
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            
            logging.info("Scheduler stopped successfully")
            return True
            
        except Exception as e:
            logging.error(f"Error stopping scheduler: {e}")
            return False
    
    def _scheduled_processing(self):
        """Main scheduled processing function"""
        try:
            logging.info("Starting scheduled analytics processing")
            
            # Import here to avoid circular imports
            from .excel_processor import ExcelProcessor
            from .email_service import EmailService
            from .stakeholder_mapper import StakeholderMapper
            from .database import DatabaseManager
            
            # Look for Excel files in uploads directory
            uploads_dir = "uploads"
            if not os.path.exists(uploads_dir):
                logging.warning("Uploads directory not found, skipping scheduled processing")
                return
            
            excel_files = [f for f in os.listdir(uploads_dir) if f.lower().endswith(('.xlsx', '.xls'))]
            
            if not excel_files:
                logging.info("No Excel files found for processing")
                return
            
            # Process the most recent file
            latest_file = max(excel_files, key=lambda f: os.path.getctime(os.path.join(uploads_dir, f)))
            file_path = os.path.join(uploads_dir, latest_file)
            
            # Process the file
            success = self._process_file(file_path)
            
            if success:
                logging.info(f"Scheduled processing completed successfully for {latest_file}")
            else:
                logging.error(f"Scheduled processing failed for {latest_file}")
                
        except Exception as e:
            logging.error(f"Error in scheduled processing: {e}")
    
    def _process_file(self, file_path: str) -> bool:
        """Process a single Excel file"""
        try:
            start_time = time.time()
            
            # Import modules
            from .excel_processor import ExcelProcessor
            from .email_service import EmailService
            from .stakeholder_mapper import StakeholderMapper
            from .database import DatabaseManager
            
            # Initialize components
            processor = ExcelProcessor()
            email_service = EmailService()
            mapper = StakeholderMapper()
            db = DatabaseManager()
            
            # Process Excel file
            if not processor.read_excel_file(file_path):
                logging.error(f"Failed to read Excel file: {file_path}")
                return False
            
            # Get thresholds from config
            thresholds = self.config.get('thresholds', {})
            expired_days = thresholds.get('expired_page_days', 730)
            low_engagement_days = thresholds.get('low_engagement_days', 30)
            low_engagement_views = thresholds.get('low_engagement_views', 5)
            
            # Analyze pages
            expired_pages, low_engagement_pages = processor.analyze_pages(
                expired_days, low_engagement_days, low_engagement_views
            )
            
            total_pages = len(processor.data) if processor.data is not None else 0
            alerts_generated = 0
            emails_sent = 0
            errors = 0
            
            # Process expired pages
            for page in expired_pages:
                try:
                    recipient = mapper.get_stakeholder_email(page['page_url'])
                    
                    # Check if alert was sent recently
                    if db.check_recent_alert(page['page_url'], 'expired', 7):
                        logging.debug(f"Skipping recent alert for {page['page_url']}")
                        continue
                    
                    # Send email
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
                    logging.error(f"Error processing expired page {page['page_url']}: {e}")
                    errors += 1
            
            # Process low engagement pages
            for page in low_engagement_pages:
                try:
                    recipient = mapper.get_stakeholder_email(page['page_url'])
                    
                    # Check if alert was sent recently
                    if db.check_recent_alert(page['page_url'], 'low_engagement', 7):
                        logging.debug(f"Skipping recent alert for {page['page_url']}")
                        continue
                    
                    # Send email
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
                    logging.error(f"Error processing low engagement page {page['page_url']}: {e}")
                    errors += 1
            
            # Log processing run
            processing_time = time.time() - start_time
            db.log_processing_run(
                os.path.basename(file_path), total_pages, alerts_generated,
                emails_sent, errors, processing_time
            )
            
            logging.info(f"Processing complete: {total_pages} pages, {alerts_generated} alerts, {emails_sent} emails sent")
            return True
            
        except Exception as e:
            logging.error(f"Error processing file {file_path}: {e}")
            return False
    
    def _cleanup_old_data(self):
        """Clean up old database entries"""
        try:
            logging.info("Starting database cleanup")
            
            from .database import DatabaseManager
            db = DatabaseManager()
            db.cleanup_old_logs(90)  # Keep 90 days of logs
            
            logging.info("Database cleanup completed")
            
        except Exception as e:
            logging.error(f"Error in database cleanup: {e}")
    
    def get_scheduler_status(self) -> Dict:
        """Get current scheduler status"""
        try:
            if not self.is_running:
                return {
                    'running': False,
                    'enabled': self.scheduler_config.get('enabled', False),
                    'jobs': []
                }
            
            jobs = []
            for job in self.scheduler.get_jobs():
                jobs.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger)
                })
            
            return {
                'running': True,
                'enabled': self.scheduler_config.get('enabled', False),
                'jobs': jobs,
                'cron_schedule': self.scheduler_config.get('cron_schedule', '0 9 * * 1'),
                'timezone': self.scheduler_config.get('timezone', 'UTC')
            }
            
        except Exception as e:
            logging.error(f"Error getting scheduler status: {e}")
            return {'running': False, 'enabled': False, 'jobs': [], 'error': str(e)}
    
    def trigger_manual_run(self) -> bool:
        """Trigger a manual processing run"""
        try:
            logging.info("Triggering manual processing run")
            self._scheduled_processing()
            return True
            
        except Exception as e:
            logging.error(f"Error in manual processing run: {e}")
            return False
