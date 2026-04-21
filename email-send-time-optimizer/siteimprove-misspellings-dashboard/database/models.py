from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Website(db.Model):
    __tablename__ = 'websites'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reports = db.relationship('Report', backref='website', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Website {self.name}>'

class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    website_id = db.Column(db.Integer, db.ForeignKey('websites.id'), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)  # misspellings, words_to_review, pages_with_misspellings, misspelling_history
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    filename = db.Column(db.String(255), nullable=False)
    processed_at = db.Column(db.DateTime, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True)  # From report metadata
    
    # Relationships
    misspellings = db.relationship('Misspelling', backref='report', lazy=True, cascade='all, delete-orphan')
    words_to_review = db.relationship('WordToReview', backref='report', lazy=True, cascade='all, delete-orphan')
    pages_with_misspellings = db.relationship('PageWithMisspelling', backref='report', lazy=True, cascade='all, delete-orphan')
    misspelling_history = db.relationship('MisspellingHistory', backref='report', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Report {self.report_type} for {self.website.name}>'

class Misspelling(db.Model):
    __tablename__ = 'misspellings'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    word = db.Column(db.String(255), nullable=False)
    spelling_suggestion = db.Column(db.String(255), nullable=True)
    language = db.Column(db.String(100), nullable=True)
    first_detected = db.Column(db.DateTime, nullable=True)
    pages_count = db.Column(db.Integer, nullable=True)
    
    def __repr__(self):
        return f'<Misspelling {self.word}>'

class WordToReview(db.Model):
    __tablename__ = 'words_to_review'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    word = db.Column(db.String(255), nullable=False)
    spelling_suggestion = db.Column(db.String(255), nullable=True)
    language = db.Column(db.String(100), nullable=True)
    first_detected = db.Column(db.DateTime, nullable=True)
    misspelling_probability = db.Column(db.String(50), nullable=True)  # High, Medium, Low
    pages_count = db.Column(db.Integer, nullable=True)
    
    def __repr__(self):
        return f'<WordToReview {self.word}>'

class PageWithMisspelling(db.Model):
    __tablename__ = 'pages_with_misspellings'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    title = db.Column(db.Text, nullable=True)
    url = db.Column(db.Text, nullable=True)
    page_report_link = db.Column(db.Text, nullable=True)
    cms_link = db.Column(db.Text, nullable=True)
    misspellings_count = db.Column(db.Integer, nullable=True)
    words_to_review_count = db.Column(db.Integer, nullable=True)
    page_level = db.Column(db.Integer, nullable=True)
    
    def __repr__(self):
        return f'<PageWithMisspelling {self.title[:50]}>'

class MisspellingHistory(db.Model):
    __tablename__ = 'misspelling_history'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    report_date = db.Column(db.DateTime, nullable=False)
    misspellings_count = db.Column(db.Integer, nullable=True)
    words_to_review_count = db.Column(db.Integer, nullable=True)
    # Note: total_words column ignored as per requirements
    
    def __repr__(self):
        return f'<MisspellingHistory {self.report_date}>'
