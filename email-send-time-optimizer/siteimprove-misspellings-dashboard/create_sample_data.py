#!/usr/bin/env python3
"""
Create sample data for Siteimprove Dashboard
This script generates realistic sample data for all report types across Thomson Reuters websites
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
import random
from app import app, db
from database.models import Website, Report, Misspelling, WordToReview, PageWithMisspelling, MisspellingHistory

def create_sample_data():
    """Create comprehensive sample data for the dashboard"""
    
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        # Create websites
        print("Creating websites...")
        websites = [
            Website(name='tax.thomsonreuters.com'),
            Website(name='thomsonreuters.com'),
            Website(name='legal.thomsonreuters.com'),
            Website(name='thompsonwriters.co.ca'),
            Website(name='Legal UK website')
        ]
        
        for website in websites:
            db.session.add(website)
        db.session.commit()
        
        # Sample data for different report types
        sample_misspellings = [
            ('recieve', 'receive', 'English', 45),
            ('seperate', 'separate', 'English', 32),
            ('occured', 'occurred', 'English', 28),
            ('accomodate', 'accommodate', 'English', 23),
            ('definately', 'definitely', 'English', 19),
            ('neccessary', 'necessary', 'English', 17),
            ('begining', 'beginning', 'English', 15),
            ('existance', 'existence', 'English', 12),
            ('maintainance', 'maintenance', 'English', 11),
            ('independant', 'independent', 'English', 9),
            ('priviledge', 'privilege', 'English', 8),
            ('embarass', 'embarrass', 'English', 7),
            ('persistant', 'persistent', 'English', 6),
            ('recomend', 'recommend', 'English', 5),
            ('goverment', 'government', 'English', 4)
        ]
        
        sample_words_to_review = [
            ('colour', 'color', 'English', 0.75, 12),
            ('centre', 'center', 'English', 0.65, 8),
            ('realise', 'realize', 'English', 0.55, 6),
            ('analyse', 'analyze', 'English', 0.45, 4),
            ('organisation', 'organization', 'English', 0.35, 3),
            ('specialise', 'specialize', 'English', 0.25, 2)
        ]
        
        sample_pages = [
            ('Tax Planning Guide 2025', '/tax/planning-guide-2025', 'High', 8, 3),
            ('Legal Research Methods', '/legal/research-methods', 'Medium', 5, 2),
            ('Corporate Tax Updates', '/tax/corporate-updates', 'High', 12, 4),
            ('Employment Law Changes', '/legal/employment-law', 'Medium', 7, 1),
            ('International Tax Treaties', '/tax/international-treaties', 'Low', 3, 1),
            ('Litigation Best Practices', '/legal/litigation-practices', 'High', 9, 2),
            ('Small Business Tax Guide', '/tax/small-business', 'Medium', 6, 2),
            ('Contract Law Essentials', '/legal/contract-law', 'Low', 4, 1)
        ]
        
        # Generate data for the last 90 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        print("Creating sample reports and data...")
        
        for website in websites:
            print(f"  Processing {website.name}...")
            
            # Create reports for different time periods
            for days_ago in range(0, 90, 7):  # Weekly reports
                report_date = end_date - timedelta(days=days_ago)
                
                # Create Misspellings Report
                misspellings_report = Report(
                    website_id=website.id,
                    report_type='misspellings',
                    filename=f'misspellings_{website.name}_{report_date.strftime("%Y%m%d")}.csv',
                    created_date=report_date,
                    processed_at=report_date
                )
                db.session.add(misspellings_report)
                db.session.flush()
                
                # Add misspellings data
                for word, suggestion, language, base_pages in sample_misspellings:
                    # Add some randomness to make data realistic
                    pages_count = max(1, base_pages + random.randint(-5, 10))
                    first_detected = report_date - timedelta(days=random.randint(1, 30))
                    
                    misspelling = Misspelling(
                        report_id=misspellings_report.id,
                        word=word,
                        spelling_suggestion=suggestion,
                        language=language,
                        first_detected=first_detected,
                        pages_count=pages_count
                    )
                    db.session.add(misspelling)
                
                # Create Words to Review Report
                words_report = Report(
                    website_id=website.id,
                    report_type='words_to_review',
                    filename=f'words_to_review_{website.name}_{report_date.strftime("%Y%m%d")}.csv',
                    created_date=report_date,
                    processed_at=report_date
                )
                db.session.add(words_report)
                db.session.flush()
                
                # Add words to review data
                for word, suggestion, language, probability, base_pages in sample_words_to_review:
                    pages_count = max(1, base_pages + random.randint(-1, 3))
                    first_detected = report_date - timedelta(days=random.randint(1, 20))
                    
                    word_to_review = WordToReview(
                        report_id=words_report.id,
                        word=word,
                        spelling_suggestion=suggestion,
                        language=language,
                        first_detected=first_detected,
                        misspelling_probability=probability,
                        pages_count=pages_count
                    )
                    db.session.add(word_to_review)
                
                # Create Pages with Misspellings Report
                pages_report = Report(
                    website_id=website.id,
                    report_type='pages_with_misspellings',
                    filename=f'pages_misspellings_{website.name}_{report_date.strftime("%Y%m%d")}.csv',
                    created_date=report_date,
                    processed_at=report_date
                )
                db.session.add(pages_report)
                db.session.flush()
                
                # Add pages data
                for title, url, level, misspellings, words_to_review in sample_pages:
                    page_url = f"https://{website.name}{url}"
                    page_report_link = f"https://my2.siteimprove.com/page/{random.randint(100000, 999999)}"
                    cms_link = f"https://cms.{website.name}/edit{url}"
                    
                    page = PageWithMisspelling(
                        report_id=pages_report.id,
                        title=title,
                        url=page_url,
                        page_report_link=page_report_link,
                        cms_link=cms_link,
                        misspellings_count=misspellings + random.randint(-2, 5),
                        words_to_review_count=words_to_review + random.randint(-1, 2),
                        page_level=level
                    )
                    db.session.add(page)
                
                # Create Misspelling History Report
                history_report = Report(
                    website_id=website.id,
                    report_type='misspelling_history',
                    filename=f'history_{website.name}_{report_date.strftime("%Y%m%d")}.csv',
                    created_date=report_date,
                    processed_at=report_date
                )
                db.session.add(history_report)
                db.session.flush()
                
                # Add history data
                total_misspellings = sum(m.pages_count for m in db.session.query(Misspelling).filter_by(report_id=misspellings_report.id).all())
                total_words_to_review = sum(w.pages_count for w in db.session.query(WordToReview).filter_by(report_id=words_report.id).all())
                
                history = MisspellingHistory(
                    report_id=history_report.id,
                    report_date=report_date,
                    misspellings_count=total_misspellings,
                    words_to_review_count=total_words_to_review
                )
                db.session.add(history)
        
        # Commit all data
        db.session.commit()
        
        # Print summary
        print("\n" + "="*50)
        print("SAMPLE DATA CREATION COMPLETE!")
        print("="*50)
        
        websites_count = db.session.query(Website).count()
        reports_count = db.session.query(Report).count()
        misspellings_count = db.session.query(Misspelling).count()
        words_count = db.session.query(WordToReview).count()
        pages_count = db.session.query(PageWithMisspelling).count()
        history_count = db.session.query(MisspellingHistory).count()
        
        print(f"✅ Websites: {websites_count}")
        print(f"✅ Reports: {reports_count}")
        print(f"✅ Misspellings: {misspellings_count}")
        print(f"✅ Words to Review: {words_count}")
        print(f"✅ Pages with Misspellings: {pages_count}")
        print(f"✅ History Records: {history_count}")
        print("\n🎉 Your dashboard is now ready with realistic sample data!")
        print("🌐 Access it at: http://localhost:5001")
        print("\n📊 You can now test:")
        print("   • Interactive charts and visualizations")
        print("   • Filtering by website, date range, and report type")
        print("   • Detailed data tables with search and pagination")
        print("   • Excel export functionality")
        print("   • Trend analysis across time periods")

if __name__ == '__main__':
    create_sample_data()
