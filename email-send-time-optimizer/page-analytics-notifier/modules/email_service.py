"""
Email service module for Page Analytics Notification System
Handles email sending via SMTP and SendGrid
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional
import yaml
import re
from datetime import datetime
import os

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    logging.warning("SendGrid not available. Install sendgrid package for SendGrid support.")

class EmailService:
    def __init__(self, config_path: str = "config/settings.yaml"):
        """Initialize email service with configuration"""
        self.config = self._load_config(config_path)
        self.email_config = self.config.get('email', {})
        self.template_cache = {}
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            return {}
    
    def _load_template(self, template_name: str) -> str:
        """Load email template from file"""
        if template_name in self.template_cache:
            return self.template_cache[template_name]
        
        template_path = f"config/email_templates/{template_name}.html"
        try:
            with open(template_path, 'r', encoding='utf-8') as file:
                template_content = file.read()
                self.template_cache[template_name] = template_content
                return template_content
        except Exception as e:
            logging.error(f"Error loading template {template_name}: {e}")
            return ""
    
    def _render_template(self, template_content: str, variables: Dict) -> str:
        """Render template with variables"""
        try:
            # Simple template rendering using string replacement
            rendered = template_content
            for key, value in variables.items():
                placeholder = f"{{{{{key}}}}}"
                rendered = rendered.replace(placeholder, str(value))
            
            return rendered
        except Exception as e:
            logging.error(f"Error rendering template: {e}")
            return template_content
    
    def _validate_email(self, email: str) -> bool:
        """Validate email address format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def send_expired_page_alert(self, page_data: Dict, recipient_email: str) -> bool:
        """Send expired page alert email"""
        try:
            if not self._validate_email(recipient_email):
                logging.error(f"Invalid email address: {recipient_email}")
                return False
            
            # Prepare template variables
            variables = {
                'page_url': page_data['page_url'],
                'creation_date': page_data['creation_date'],
                'page_views': page_data['page_views'],
                'page_age_days': page_data['page_age_days'],
                'page_age_years': page_data['page_age_years'],
                'alert_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'threshold_days': self.config.get('thresholds', {}).get('expired_page_days', 730),
                'company_name': 'Your Company',
                'aem_edit_url': f"https://author.aem.company.com{page_data['page_url']}",
                'analytics_url': f"https://analytics.adobe.com/workspace/project/page-analysis?url={page_data['page_url']}"
            }
            
            # Load and render template
            template_content = self._load_template('expired_page')
            if not template_content:
                logging.error("Failed to load expired page template")
                return False
            
            html_content = self._render_template(template_content, variables)
            
            # Send email
            subject = f"🚨 Page Review Required - Expired Content: {page_data['page_url']}"
            return self._send_email(recipient_email, subject, html_content)
            
        except Exception as e:
            logging.error(f"Error sending expired page alert: {e}")
            return False
    
    def send_low_engagement_alert(self, page_data: Dict, recipient_email: str) -> bool:
        """Send low engagement alert email"""
        try:
            if not self._validate_email(recipient_email):
                logging.error(f"Invalid email address: {recipient_email}")
                return False
            
            # Prepare template variables
            variables = {
                'page_url': page_data['page_url'],
                'creation_date': page_data['creation_date'],
                'page_views': page_data['page_views'],
                'days_since_creation': page_data['days_since_creation'],
                'expected_views': page_data['expected_views'],
                'alert_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'threshold_days': self.config.get('thresholds', {}).get('low_engagement_days', 30),
                'min_views': self.config.get('thresholds', {}).get('low_engagement_views', 5),
                'company_name': 'Your Company',
                'aem_edit_url': f"https://author.aem.company.com{page_data['page_url']}",
                'analytics_url': f"https://analytics.adobe.com/workspace/project/page-analysis?url={page_data['page_url']}"
            }
            
            # Load and render template
            template_content = self._load_template('low_engagement')
            if not template_content:
                logging.error("Failed to load low engagement template")
                return False
            
            html_content = self._render_template(template_content, variables)
            
            # Send email
            subject = f"📊 Low Engagement Alert - New Page Performance: {page_data['page_url']}"
            return self._send_email(recipient_email, subject, html_content)
            
        except Exception as e:
            logging.error(f"Error sending low engagement alert: {e}")
            return False
    
    def _send_email(self, recipient_email: str, subject: str, html_content: str) -> bool:
        """Send email using configured method"""
        # Try SendGrid first if available and configured
        if SENDGRID_AVAILABLE and self.email_config.get('sendgrid_api_key'):
            return self._send_via_sendgrid(recipient_email, subject, html_content)
        
        # Fallback to SMTP
        return self._send_via_smtp(recipient_email, subject, html_content)
    
    def _send_via_smtp(self, recipient_email: str, subject: str, html_content: str) -> bool:
        """Send email via SMTP"""
        try:
            sender_email = self.email_config.get('sender_email')
            sender_password = self.email_config.get('sender_password')
            sender_name = self.email_config.get('sender_name', 'Page Analytics System')
            
            if not sender_email or not sender_password:
                logging.error("SMTP credentials not configured")
                return False
            
            # Check for placeholder values
            if sender_email in ['your.email@gmail.com', 'your-email@gmail.com', 'raju.golusu@thomsonreuters.com'] or sender_password in ['your-app-password-here', 'your-app-password', 'your-password-here']:
                logging.error("Email credentials contain placeholder values. Please configure with actual credentials.")
                logging.error("For Thomson Reuters: Replace 'your-password-here' with your actual password or app password.")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{sender_name} <{sender_email}>"
            msg['To'] = recipient_email
            
            # Add Reply-To if configured
            reply_to = self.email_config.get('reply_to')
            if reply_to:
                msg['Reply-To'] = reply_to
            
            # Add CC emails if configured
            cc_emails = self.email_config.get('cc_emails', [])
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            
            # Add BCC emails if configured
            bcc_emails = self.email_config.get('bcc_emails', [])
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Prepare recipient list (including CC and BCC)
            all_recipients = [recipient_email] + cc_emails + bcc_emails
            
            # Send email
            smtp_server = self.email_config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = self.email_config.get('smtp_port', 587)
            use_tls = self.email_config.get('use_tls', True)
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                if use_tls:
                    server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg, to_addrs=all_recipients)
            
            logging.info(f"Email sent successfully via SMTP to {recipient_email} (CC: {cc_emails}, BCC: {bcc_emails})")
            return True
            
        except Exception as e:
            logging.error(f"Error sending email via SMTP: {e}")
            return False
    
    def _send_via_sendgrid(self, recipient_email: str, subject: str, html_content: str) -> bool:
        """Send email via SendGrid"""
        try:
            api_key = self.email_config.get('sendgrid_api_key')
            sender_email = self.email_config.get('sender_email')
            sender_name = self.email_config.get('sender_name', 'Page Analytics System')
            
            if not api_key or not sender_email:
                logging.error("SendGrid credentials not configured")
                return False
            
            message = Mail(
                from_email=(sender_email, sender_name),
                to_emails=recipient_email,
                subject=subject,
                html_content=html_content
            )
            
            sg = SendGridAPIClient(api_key=api_key)
            response = sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                logging.info(f"Email sent successfully via SendGrid to {recipient_email}")
                return True
            else:
                logging.error(f"SendGrid error: {response.status_code}")
                return False
                
        except Exception as e:
            logging.error(f"Error sending email via SendGrid: {e}")
            return False
    
    def send_test_email(self, recipient_email: str) -> bool:
        """Send a test email to verify configuration"""
        try:
            subject = "Test Email - Page Analytics Notification System"
            html_content = """
            <html>
            <body>
                <h2>Test Email</h2>
                <p>This is a test email from the Page Analytics Notification System.</p>
                <p>If you received this email, your email configuration is working correctly.</p>
                <p><em>Sent at: {}</em></p>
            </body>
            </html>
            """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            return self._send_email(recipient_email, subject, html_content)
            
        except Exception as e:
            logging.error(f"Error sending test email: {e}")
            return False
    
    def send_summary_report(self, recipient_emails: List[str], summary_data: Dict) -> bool:
        """Send summary report to administrators"""
        try:
            subject = f"Page Analytics Summary Report - {datetime.now().strftime('%Y-%m-%d')}"
            
            html_content = f"""
            <html>
            <body>
                <h2>Page Analytics Summary Report</h2>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <h3>Processing Summary</h3>
                <ul>
                    <li>Total Pages Processed: {summary_data.get('total_pages', 0)}</li>
                    <li>Expired Page Alerts: {summary_data.get('expired_alerts', 0)}</li>
                    <li>Low Engagement Alerts: {summary_data.get('low_engagement_alerts', 0)}</li>
                    <li>Emails Sent: {summary_data.get('emails_sent', 0)}</li>
                    <li>Processing Time: {summary_data.get('processing_time', 0):.2f} seconds</li>
                </ul>
                
                <p><em>Page Analytics Notification System</em></p>
            </body>
            </html>
            """
            
            success_count = 0
            for email in recipient_emails:
                if self._send_email(email, subject, html_content):
                    success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            logging.error(f"Error sending summary report: {e}")
            return False
