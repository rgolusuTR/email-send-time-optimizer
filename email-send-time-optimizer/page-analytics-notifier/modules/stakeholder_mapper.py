"""
Stakeholder mapping module for Page Analytics Notification System
Maps page URLs to responsible stakeholder email addresses
"""

import yaml
import logging
import re
from typing import Dict, Optional, List
from urllib.parse import urlparse

class StakeholderMapper:
    def __init__(self, config_path: str = "config/stakeholders.yaml", 
                 settings_path: str = "config/settings.yaml"):
        """Initialize stakeholder mapper with configuration"""
        self.stakeholder_config = self._load_config(config_path)
        self.settings_config = self._load_config(settings_path)
        self.default_admin_email = self.settings_config.get('email', {}).get('default_admin_email', 'admin@company.com')
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logging.error(f"Error loading config {config_path}: {e}")
            return {}
    
    def get_stakeholder_email(self, page_url: str) -> str:
        """Get stakeholder email for a given page URL"""
        try:
            # Clean and normalize URL
            normalized_url = self._normalize_url(page_url)
            
            # Try exact matches first (highest priority)
            exact_email = self._check_exact_matches(normalized_url)
            if exact_email:
                logging.debug(f"Found exact match for {page_url}: {exact_email}")
                return exact_email
            
            # Try pattern matches
            pattern_email = self._check_pattern_matches(normalized_url)
            if pattern_email:
                logging.debug(f"Found pattern match for {page_url}: {pattern_email}")
                return pattern_email
            
            # Try department fallbacks based on URL structure
            department_email = self._check_department_fallbacks(normalized_url)
            if department_email:
                logging.debug(f"Found department fallback for {page_url}: {department_email}")
                return department_email
            
            # Return default admin email
            logging.debug(f"Using default admin email for {page_url}: {self.default_admin_email}")
            return self.default_admin_email
            
        except Exception as e:
            logging.error(f"Error getting stakeholder email for {page_url}: {e}")
            return self.default_admin_email
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for consistent matching"""
        try:
            # Remove protocol and domain, keep only path
            if url.startswith(('http://', 'https://')):
                parsed = urlparse(url)
                normalized = parsed.path
            else:
                normalized = url
            
            # Ensure it starts with /
            if not normalized.startswith('/'):
                normalized = '/' + normalized
            
            # Remove trailing slash for consistency (except for root)
            if len(normalized) > 1 and normalized.endswith('/'):
                normalized = normalized[:-1]
            
            return normalized
            
        except Exception as e:
            logging.error(f"Error normalizing URL {url}: {e}")
            return url
    
    def _check_exact_matches(self, url: str) -> Optional[str]:
        """Check for exact URL matches"""
        try:
            exact_matches = self.stakeholder_config.get('stakeholders', {}).get('exact_matches', {})
            
            # Check exact match
            if url in exact_matches:
                return exact_matches[url]
            
            # Check with trailing slash
            url_with_slash = url + '/' if not url.endswith('/') else url
            if url_with_slash in exact_matches:
                return exact_matches[url_with_slash]
            
            # Check without trailing slash
            url_without_slash = url[:-1] if url.endswith('/') and len(url) > 1 else url
            if url_without_slash in exact_matches:
                return exact_matches[url_without_slash]
            
            return None
            
        except Exception as e:
            logging.error(f"Error checking exact matches for {url}: {e}")
            return None
    
    def _check_pattern_matches(self, url: str) -> Optional[str]:
        """Check for regex pattern matches"""
        try:
            pattern_matches = self.stakeholder_config.get('stakeholders', {}).get('pattern_matches', {})
            
            for pattern, email in pattern_matches.items():
                try:
                    if re.match(pattern, url):
                        return email
                except re.error as regex_error:
                    logging.warning(f"Invalid regex pattern '{pattern}': {regex_error}")
                    continue
            
            return None
            
        except Exception as e:
            logging.error(f"Error checking pattern matches for {url}: {e}")
            return None
    
    def _check_department_fallbacks(self, url: str) -> Optional[str]:
        """Check department fallbacks based on URL structure"""
        try:
            department_fallbacks = self.stakeholder_config.get('stakeholders', {}).get('department_fallbacks', {})
            
            # Extract potential department from URL path
            url_parts = url.strip('/').split('/')
            if not url_parts or url_parts == ['']:
                return None
            
            # Check first part of URL path
            first_part = url_parts[0].lower()
            
            # Common department mappings
            department_keywords = {
                'about': 'marketing',
                'contact': 'support',
                'support': 'support',
                'help': 'support',
                'faq': 'support',
                'products': 'product',
                'product': 'product',
                'services': 'product',
                'blog': 'content',
                'news': 'marketing',
                'press': 'marketing',
                'careers': 'hr',
                'jobs': 'hr',
                'legal': 'legal',
                'privacy': 'legal',
                'terms': 'legal',
                'docs': 'tech',
                'documentation': 'tech',
                'api': 'tech',
                'developer': 'tech'
            }
            
            # Find matching department
            for keyword, department in department_keywords.items():
                if keyword in first_part or first_part in keyword:
                    if department in department_fallbacks:
                        return department_fallbacks[department]
            
            return None
            
        except Exception as e:
            logging.error(f"Error checking department fallbacks for {url}: {e}")
            return None
    
    def get_all_stakeholders(self) -> List[str]:
        """Get list of all configured stakeholder emails"""
        try:
            emails = set()
            
            # Add exact match emails
            exact_matches = self.stakeholder_config.get('stakeholders', {}).get('exact_matches', {})
            emails.update(exact_matches.values())
            
            # Add pattern match emails
            pattern_matches = self.stakeholder_config.get('stakeholders', {}).get('pattern_matches', {})
            emails.update(pattern_matches.values())
            
            # Add department fallback emails
            department_fallbacks = self.stakeholder_config.get('stakeholders', {}).get('department_fallbacks', {})
            emails.update(department_fallbacks.values())
            
            # Add default admin email
            emails.add(self.default_admin_email)
            
            return list(emails)
            
        except Exception as e:
            logging.error(f"Error getting all stakeholders: {e}")
            return [self.default_admin_email]
    
    def validate_stakeholder_config(self) -> Dict:
        """Validate stakeholder configuration and return validation results"""
        try:
            results = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'email_count': 0,
                'pattern_count': 0
            }
            
            stakeholders = self.stakeholder_config.get('stakeholders', {})
            
            # Validate exact matches
            exact_matches = stakeholders.get('exact_matches', {})
            for url, email in exact_matches.items():
                if not self._validate_email(email):
                    results['errors'].append(f"Invalid email in exact_matches: {email}")
                    results['valid'] = False
            
            # Validate pattern matches
            pattern_matches = stakeholders.get('pattern_matches', {})
            for pattern, email in pattern_matches.items():
                # Test regex pattern
                try:
                    re.compile(pattern)
                    results['pattern_count'] += 1
                except re.error:
                    results['errors'].append(f"Invalid regex pattern: {pattern}")
                    results['valid'] = False
                
                # Validate email
                if not self._validate_email(email):
                    results['errors'].append(f"Invalid email in pattern_matches: {email}")
                    results['valid'] = False
            
            # Validate department fallbacks
            department_fallbacks = stakeholders.get('department_fallbacks', {})
            for department, email in department_fallbacks.items():
                if not self._validate_email(email):
                    results['errors'].append(f"Invalid email in department_fallbacks: {email}")
                    results['valid'] = False
            
            # Count unique emails
            all_emails = self.get_all_stakeholders()
            results['email_count'] = len(set(all_emails))
            
            # Check for warnings
            if results['email_count'] == 1:
                results['warnings'].append("Only one unique email configured (default admin)")
            
            if not exact_matches and not pattern_matches:
                results['warnings'].append("No specific URL mappings configured")
            
            return results
            
        except Exception as e:
            logging.error(f"Error validating stakeholder config: {e}")
            return {
                'valid': False,
                'errors': [f"Configuration validation error: {e}"],
                'warnings': [],
                'email_count': 0,
                'pattern_count': 0
            }
    
    def _validate_email(self, email: str) -> bool:
        """Validate email address format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def add_stakeholder_mapping(self, url: str, email: str, mapping_type: str = 'exact') -> bool:
        """Add new stakeholder mapping (for dynamic configuration)"""
        try:
            if not self._validate_email(email):
                logging.error(f"Invalid email address: {email}")
                return False
            
            if mapping_type == 'exact':
                if 'stakeholders' not in self.stakeholder_config:
                    self.stakeholder_config['stakeholders'] = {}
                if 'exact_matches' not in self.stakeholder_config['stakeholders']:
                    self.stakeholder_config['stakeholders']['exact_matches'] = {}
                
                self.stakeholder_config['stakeholders']['exact_matches'][url] = email
                logging.info(f"Added exact mapping: {url} -> {email}")
                return True
            
            elif mapping_type == 'pattern':
                # Validate regex pattern
                try:
                    re.compile(url)
                except re.error:
                    logging.error(f"Invalid regex pattern: {url}")
                    return False
                
                if 'stakeholders' not in self.stakeholder_config:
                    self.stakeholder_config['stakeholders'] = {}
                if 'pattern_matches' not in self.stakeholder_config['stakeholders']:
                    self.stakeholder_config['stakeholders']['pattern_matches'] = {}
                
                self.stakeholder_config['stakeholders']['pattern_matches'][url] = email
                logging.info(f"Added pattern mapping: {url} -> {email}")
                return True
            
            else:
                logging.error(f"Invalid mapping type: {mapping_type}")
                return False
                
        except Exception as e:
            logging.error(f"Error adding stakeholder mapping: {e}")
            return False
