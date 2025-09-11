from database.models import db, Website, Report, Misspelling, WordToReview, PageWithMisspelling, MisspellingHistory
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd

class DataProcessor:
    """Handle data analysis and aggregation for dashboard visualizations"""
    
    def __init__(self):
        pass
    
    def get_websites(self) -> List[Dict]:
        """Get all websites"""
        websites = Website.query.all()
        return [{'id': w.id, 'name': w.name, 'url': w.url} for w in websites]
    
    def get_report_types(self, website_ids: List[int] = None) -> List[str]:
        """Get available report types, optionally filtered by websites"""
        query = db.session.query(Report.report_type).distinct()
        if website_ids:
            query = query.filter(Report.website_id.in_(website_ids))
        
        return [r[0] for r in query.all()]
    
    def get_date_range(self, website_ids: List[int] = None, report_types: List[str] = None) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Get the date range of available data"""
        query = db.session.query(
            func.min(Report.created_date),
            func.max(Report.created_date)
        )
        
        if website_ids:
            query = query.filter(Report.website_id.in_(website_ids))
        if report_types:
            query = query.filter(Report.report_type.in_(report_types))
        
        result = query.first()
        return result[0], result[1]
    
    def get_trend_data(self, website_ids: List[int], report_types: List[str], 
                      start_date: datetime, end_date: datetime, 
                      period: str = 'daily') -> Dict:
        """
        Get trend data for line charts
        
        Args:
            website_ids: List of website IDs to include
            report_types: List of report types to include
            start_date: Start date for filtering
            end_date: End date for filtering
            period: Aggregation period ('daily', 'weekly', 'monthly', 'yearly')
        """
        
        # Get misspelling history data for trends
        if 'misspelling_history' in report_types:
            return self._get_history_trends(website_ids, start_date, end_date, period)
        else:
            return self._get_calculated_trends(website_ids, report_types, start_date, end_date, period)
    
    def _get_history_trends(self, website_ids: List[int], start_date: datetime, 
                           end_date: datetime, period: str) -> Dict:
        """Get trends from misspelling history data"""
        
        query = db.session.query(
            MisspellingHistory.report_date,
            MisspellingHistory.misspellings_count,
            MisspellingHistory.words_to_review_count,
            Website.name
        ).join(Report).join(Website).filter(
            Report.website_id.in_(website_ids),
            MisspellingHistory.report_date.between(start_date, end_date)
        ).order_by(MisspellingHistory.report_date)
        
        results = query.all()
        
        # Group by period
        grouped_data = self._group_by_period(results, period)
        
        return {
            'labels': list(grouped_data.keys()),
            'datasets': [
                {
                    'label': 'Misspellings',
                    'data': [sum(d['misspellings'] for d in data) for data in grouped_data.values()],
                    'borderColor': 'rgb(255, 99, 132)',
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)'
                },
                {
                    'label': 'Words to Review',
                    'data': [sum(d['words_to_review'] for d in data) for data in grouped_data.values()],
                    'borderColor': 'rgb(54, 162, 235)',
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)'
                }
            ]
        }
    
    def _get_calculated_trends(self, website_ids: List[int], report_types: List[str],
                              start_date: datetime, end_date: datetime, period: str) -> Dict:
        """Calculate trends from individual reports"""
        
        # This would aggregate data from individual misspelling/word reports
        # For now, return empty structure
        return {
            'labels': [],
            'datasets': [
                {
                    'label': 'Misspellings',
                    'data': [],
                    'borderColor': 'rgb(255, 99, 132)',
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)'
                },
                {
                    'label': 'Words to Review',
                    'data': [],
                    'borderColor': 'rgb(54, 162, 235)',
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)'
                }
            ]
        }
    
    def get_top_misspelled_words(self, website_ids: List[int], report_types: List[str],
                                start_date: datetime, end_date: datetime, limit: int = 10) -> Dict:
        """Get top misspelled words for bar chart"""
        
        data = []
        
        if 'misspellings' in report_types:
            query = db.session.query(
                Misspelling.word,
                func.sum(Misspelling.pages_count).label('total_pages')
            ).join(Report).filter(
                Report.website_id.in_(website_ids),
                Report.created_date.between(start_date, end_date)
            ).group_by(Misspelling.word).order_by(
                func.sum(Misspelling.pages_count).desc()
            ).limit(limit)
            
            results = query.all()
            data.extend([(r.word, r.total_pages or 0) for r in results])
        
        if 'words_to_review' in report_types:
            query = db.session.query(
                WordToReview.word,
                func.sum(WordToReview.pages_count).label('total_pages')
            ).join(Report).filter(
                Report.website_id.in_(website_ids),
                Report.created_date.between(start_date, end_date)
            ).group_by(WordToReview.word).order_by(
                func.sum(WordToReview.pages_count).desc()
            ).limit(limit)
            
            results = query.all()
            data.extend([(r.word, r.total_pages or 0) for r in results])
        
        # Sort and limit
        data.sort(key=lambda x: x[1], reverse=True)
        data = data[:limit]
        
        return {
            'labels': [item[0] for item in data],
            'datasets': [{
                'label': 'Pages Affected',
                'data': [item[1] for item in data],
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 205, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(153, 102, 255, 0.8)',
                    'rgba(255, 159, 64, 0.8)',
                    'rgba(199, 199, 199, 0.8)',
                    'rgba(83, 102, 255, 0.8)',
                    'rgba(255, 99, 255, 0.8)',
                    'rgba(99, 255, 132, 0.8)'
                ]
            }]
        }
    
    def get_language_distribution(self, website_ids: List[int], report_types: List[str],
                                 start_date: datetime, end_date: datetime) -> Dict:
        """Get language distribution for pie chart"""
        
        data = {}
        
        if 'misspellings' in report_types:
            query = db.session.query(
                Misspelling.language,
                func.count(Misspelling.id).label('count')
            ).join(Report).filter(
                Report.website_id.in_(website_ids),
                Report.created_date.between(start_date, end_date),
                Misspelling.language.isnot(None)
            ).group_by(Misspelling.language)
            
            for result in query.all():
                lang = result.language or 'Unknown'
                data[lang] = data.get(lang, 0) + result.count
        
        if 'words_to_review' in report_types:
            query = db.session.query(
                WordToReview.language,
                func.count(WordToReview.id).label('count')
            ).join(Report).filter(
                Report.website_id.in_(website_ids),
                Report.created_date.between(start_date, end_date),
                WordToReview.language.isnot(None)
            ).group_by(WordToReview.language)
            
            for result in query.all():
                lang = result.language or 'Unknown'
                data[lang] = data.get(lang, 0) + result.count
        
        return {
            'labels': list(data.keys()),
            'datasets': [{
                'data': list(data.values()),
                'backgroundColor': [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF',
                    '#FF9F40'
                ]
            }]
        }
    
    def get_detailed_data(self, website_ids: List[int], report_types: List[str],
                         start_date: datetime, end_date: datetime, 
                         search_term: str = None, page: int = 1, per_page: int = 50) -> Dict:
        """Get detailed data for tables with pagination"""
        
        results = []
        total_count = 0
        
        offset = (page - 1) * per_page
        
        if 'misspellings' in report_types:
            query = db.session.query(Misspelling, Website.name, Report.created_date).join(Report).join(Website).filter(
                Report.website_id.in_(website_ids),
                Report.created_date.between(start_date, end_date)
            )
            
            if search_term:
                query = query.filter(
                    or_(
                        Misspelling.word.ilike(f'%{search_term}%'),
                        Misspelling.spelling_suggestion.ilike(f'%{search_term}%')
                    )
                )
            
            total_count += query.count()
            
            for item, website_name, created_date in query.offset(offset).limit(per_page).all():
                results.append({
                    'type': 'Misspelling',
                    'word': item.word,
                    'suggestion': item.spelling_suggestion,
                    'language': item.language,
                    'first_detected': item.first_detected,
                    'pages': item.pages_count,
                    'website': website_name,
                    'report_date': created_date
                })
        
        if 'words_to_review' in report_types and len(results) < per_page:
            remaining = per_page - len(results)
            query = db.session.query(WordToReview, Website.name, Report.created_date).join(Report).join(Website).filter(
                Report.website_id.in_(website_ids),
                Report.created_date.between(start_date, end_date)
            )
            
            if search_term:
                query = query.filter(
                    or_(
                        WordToReview.word.ilike(f'%{search_term}%'),
                        WordToReview.spelling_suggestion.ilike(f'%{search_term}%')
                    )
                )
            
            total_count += query.count()
            
            for item, website_name, created_date in query.offset(max(0, offset - len(results))).limit(remaining).all():
                results.append({
                    'type': 'Word to Review',
                    'word': item.word,
                    'suggestion': item.spelling_suggestion,
                    'language': item.language,
                    'first_detected': item.first_detected,
                    'pages': item.pages_count,
                    'probability': item.misspelling_probability,
                    'website': website_name,
                    'report_date': created_date
                })
        
        return {
            'data': results,
            'total': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page
        }
    
    def _group_by_period(self, data: List, period: str) -> Dict:
        """Group data by time period"""
        grouped = {}
        
        for item in data:
            date = item[0]  # report_date
            misspellings = item[1] or 0
            words_to_review = item[2] or 0
            
            if period == 'daily':
                key = date.strftime('%Y-%m-%d')
            elif period == 'weekly':
                # Get Monday of the week
                monday = date - timedelta(days=date.weekday())
                key = monday.strftime('%Y-%m-%d')
            elif period == 'monthly':
                key = date.strftime('%Y-%m')
            elif period == 'yearly':
                key = date.strftime('%Y')
            else:
                key = date.strftime('%Y-%m-%d')
            
            if key not in grouped:
                grouped[key] = []
            
            grouped[key].append({
                'misspellings': misspellings,
                'words_to_review': words_to_review
            })
        
        return grouped
    
    def get_summary_stats(self, website_ids: List[int], report_types: List[str],
                         start_date: datetime, end_date: datetime) -> Dict:
        """Get summary statistics for the dashboard"""
        
        stats = {
            'total_misspellings': 0,
            'total_words_to_review': 0,
            'total_pages_affected': 0,
            'total_reports': 0
        }
        
        # Count reports
        report_count = db.session.query(Report).filter(
            Report.website_id.in_(website_ids),
            Report.report_type.in_(report_types),
            Report.created_date.between(start_date, end_date)
        ).count()
        stats['total_reports'] = report_count
        
        # Count misspellings
        if 'misspellings' in report_types:
            misspelling_count = db.session.query(func.count(Misspelling.id)).join(Report).filter(
                Report.website_id.in_(website_ids),
                Report.created_date.between(start_date, end_date)
            ).scalar()
            stats['total_misspellings'] = misspelling_count or 0
        
        # Count words to review
        if 'words_to_review' in report_types:
            words_count = db.session.query(func.count(WordToReview.id)).join(Report).filter(
                Report.website_id.in_(website_ids),
                Report.created_date.between(start_date, end_date)
            ).scalar()
            stats['total_words_to_review'] = words_count or 0
        
        # Count affected pages
        if 'pages_with_misspellings' in report_types:
            pages_count = db.session.query(func.count(PageWithMisspelling.id)).join(Report).filter(
                Report.website_id.in_(website_ids),
                Report.created_date.between(start_date, end_date)
            ).scalar()
            stats['total_pages_affected'] = pages_count or 0
        
        return stats
