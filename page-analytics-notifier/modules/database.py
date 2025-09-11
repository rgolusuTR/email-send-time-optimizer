"""
Database module for Page Analytics Notification System
Handles SQLite operations for logging and tracking alerts
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os

class DatabaseManager:
    def __init__(self, db_path: str = "data/analytics_notifications.db"):
        """Initialize database manager with SQLite database"""
        self.db_path = db_path
        self.ensure_directory_exists()
        self.init_database()
        
    def ensure_directory_exists(self):
        """Create directory for database if it doesn't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
    def init_database(self):
        """Initialize database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create alerts table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        page_url TEXT NOT NULL,
                        alert_type TEXT NOT NULL,
                        recipient_email TEXT NOT NULL,
                        creation_date TEXT NOT NULL,
                        page_views INTEGER NOT NULL,
                        page_age_days INTEGER,
                        alert_sent_date TEXT NOT NULL,
                        email_status TEXT NOT NULL,
                        error_message TEXT
                    )
                ''')
                
                # Create processing_log table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS processing_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT NOT NULL,
                        processed_date TEXT NOT NULL,
                        total_pages INTEGER NOT NULL,
                        alerts_generated INTEGER NOT NULL,
                        emails_sent INTEGER NOT NULL,
                        errors INTEGER NOT NULL,
                        processing_time_seconds REAL NOT NULL
                    )
                ''')
                
                # Create configuration_log table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS configuration_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        config_type TEXT NOT NULL,
                        old_value TEXT,
                        new_value TEXT NOT NULL,
                        changed_by TEXT,
                        changed_date TEXT NOT NULL
                    )
                ''')
                
                conn.commit()
                logging.info("Database initialized successfully")
                
        except Exception as e:
            logging.error(f"Error initializing database: {e}")
            raise
    
    def log_alert(self, page_url: str, alert_type: str, recipient_email: str, 
                  creation_date: str, page_views: int, page_age_days: Optional[int],
                  email_status: str, error_message: Optional[str] = None) -> int:
        """Log an alert to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO alerts (page_url, alert_type, recipient_email, 
                                      creation_date, page_views, page_age_days,
                                      alert_sent_date, email_status, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (page_url, alert_type, recipient_email, creation_date, 
                      page_views, page_age_days, datetime.now().isoformat(),
                      email_status, error_message))
                
                alert_id = cursor.lastrowid
                conn.commit()
                logging.info(f"Alert logged with ID: {alert_id}")
                return alert_id
                
        except Exception as e:
            logging.error(f"Error logging alert: {e}")
            raise
    
    def check_recent_alert(self, page_url: str, alert_type: str, days: int = 7) -> bool:
        """Check if an alert was sent for this page recently"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM alerts 
                    WHERE page_url = ? AND alert_type = ? 
                    AND alert_sent_date > ? AND email_status = 'sent'
                ''', (page_url, alert_type, cutoff_date.isoformat()))
                
                count = cursor.fetchone()[0]
                return count > 0
                
        except Exception as e:
            logging.error(f"Error checking recent alerts: {e}")
            return False
    
    def log_processing_run(self, filename: str, total_pages: int, alerts_generated: int,
                          emails_sent: int, errors: int, processing_time: float) -> int:
        """Log a processing run to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO processing_log (filename, processed_date, total_pages,
                                              alerts_generated, emails_sent, errors,
                                              processing_time_seconds)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (filename, datetime.now().isoformat(), total_pages,
                      alerts_generated, emails_sent, errors, processing_time))
                
                log_id = cursor.lastrowid
                conn.commit()
                logging.info(f"Processing run logged with ID: {log_id}")
                return log_id
                
        except Exception as e:
            logging.error(f"Error logging processing run: {e}")
            raise
    
    def get_alert_statistics(self, days: int = 30) -> Dict:
        """Get alert statistics for the last N days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total alerts
                cursor.execute('''
                    SELECT COUNT(*) FROM alerts 
                    WHERE alert_sent_date > ?
                ''', (cutoff_date.isoformat(),))
                total_alerts = cursor.fetchone()[0]
                
                # Alerts by type
                cursor.execute('''
                    SELECT alert_type, COUNT(*) FROM alerts 
                    WHERE alert_sent_date > ?
                    GROUP BY alert_type
                ''', (cutoff_date.isoformat(),))
                alerts_by_type = dict(cursor.fetchall())
                
                # Success rate
                cursor.execute('''
                    SELECT email_status, COUNT(*) FROM alerts 
                    WHERE alert_sent_date > ?
                    GROUP BY email_status
                ''', (cutoff_date.isoformat(),))
                status_counts = dict(cursor.fetchall())
                
                return {
                    'total_alerts': total_alerts,
                    'alerts_by_type': alerts_by_type,
                    'status_counts': status_counts,
                    'period_days': days
                }
                
        except Exception as e:
            logging.error(f"Error getting alert statistics: {e}")
            return {}
    
    def get_recent_alerts(self, limit: int = 50) -> List[Dict]:
        """Get recent alerts for display"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT page_url, alert_type, recipient_email, alert_sent_date,
                           email_status, page_views, page_age_days
                    FROM alerts 
                    ORDER BY alert_sent_date DESC 
                    LIMIT ?
                ''', (limit,))
                
                columns = ['page_url', 'alert_type', 'recipient_email', 
                          'alert_sent_date', 'email_status', 'page_views', 'page_age_days']
                
                alerts = []
                for row in cursor.fetchall():
                    alert_dict = dict(zip(columns, row))
                    alerts.append(alert_dict)
                
                return alerts
                
        except Exception as e:
            logging.error(f"Error getting recent alerts: {e}")
            return []
    
    def cleanup_old_logs(self, days: int = 90):
        """Clean up old log entries"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Clean up old alerts
                cursor.execute('''
                    DELETE FROM alerts 
                    WHERE alert_sent_date < ?
                ''', (cutoff_date.isoformat(),))
                alerts_deleted = cursor.rowcount
                
                # Clean up old processing logs
                cursor.execute('''
                    DELETE FROM processing_log 
                    WHERE processed_date < ?
                ''', (cutoff_date.isoformat(),))
                logs_deleted = cursor.rowcount
                
                conn.commit()
                logging.info(f"Cleaned up {alerts_deleted} old alerts and {logs_deleted} old processing logs")
                
        except Exception as e:
            logging.error(f"Error cleaning up old logs: {e}")
