"""
Analytics and Reporting Module
Phase 2 Implementation - Code Project Converter

This module provides conversion success rate tracking, performance metrics dashboard,
user activity analytics, and quality metrics and trends.
"""

import os
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import pandas as pd
from dataclasses import dataclass, asdict

@dataclass
class ConversionMetrics:
    """Data class for conversion metrics."""
    conversion_id: str
    user_id: str
    source_language: str
    target_language: str
    file_count: int
    total_lines: int
    conversion_time: float
    success: bool
    error_message: Optional[str]
    ai_model_used: str
    quality_score: float
    timestamp: datetime

@dataclass
class UserActivity:
    """Data class for user activity metrics."""
    user_id: str
    session_id: str
    action: str
    resource: str
    duration: float
    success: bool
    timestamp: datetime

@dataclass
class PerformanceMetrics:
    """Data class for performance metrics."""
    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    context: Dict[str, Any]

class AnalyticsManager:
    """Manages analytics data collection and storage."""
    
    def __init__(self, db_path: str = "instance/analytics.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize analytics database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create conversions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversions (
                    conversion_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    source_language TEXT,
                    target_language TEXT,
                    file_count INTEGER,
                    total_lines INTEGER,
                    conversion_time REAL,
                    success BOOLEAN,
                    error_message TEXT,
                    ai_model_used TEXT,
                    quality_score REAL,
                    timestamp DATETIME
                )
            ''')
            
            # Create user_activity table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    session_id TEXT,
                    action TEXT,
                    resource TEXT,
                    duration REAL,
                    success BOOLEAN,
                    timestamp DATETIME
                )
            ''')
            
            # Create performance_metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT,
                    value REAL,
                    unit TEXT,
                    timestamp DATETIME,
                    context TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Error initializing analytics database: {e}")
    
    def record_conversion(self, metrics: ConversionMetrics):
        """Record conversion metrics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO conversions 
                (conversion_id, user_id, source_language, target_language, 
                 file_count, total_lines, conversion_time, success, 
                 error_message, ai_model_used, quality_score, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.conversion_id,
                metrics.user_id,
                metrics.source_language,
                metrics.target_language,
                metrics.file_count,
                metrics.total_lines,
                metrics.conversion_time,
                metrics.success,
                metrics.error_message,
                metrics.ai_model_used,
                metrics.quality_score,
                metrics.timestamp.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Error recording conversion metrics: {e}")
    
    def record_user_activity(self, activity: UserActivity):
        """Record user activity metrics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_activity 
                (user_id, session_id, action, resource, duration, success, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                activity.user_id,
                activity.session_id,
                activity.action,
                activity.resource,
                activity.duration,
                activity.success,
                activity.timestamp.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Error recording user activity: {e}")
    
    def record_performance_metric(self, metric: PerformanceMetrics):
        """Record performance metrics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_metrics 
                (metric_name, value, unit, timestamp, context)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                metric.metric_name,
                metric.value,
                metric.unit,
                metric.timestamp.isoformat(),
                json.dumps(metric.context)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Error recording performance metric: {e}")

class ConversionAnalytics:
    """Analyzes conversion success rates and quality metrics."""
    
    def __init__(self, analytics_manager: AnalyticsManager):
        self.analytics_manager = analytics_manager
    
    def get_conversion_success_rate(self, start_date: datetime = None, 
                                   end_date: datetime = None) -> Dict[str, Any]:
        """Calculate conversion success rate."""
        try:
            conn = sqlite3.connect(self.analytics_manager.db_path)
            
            query = "SELECT success, COUNT(*) FROM conversions"
            params = []
            
            if start_date or end_date:
                query += " WHERE 1=1"
                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date.isoformat())
                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date.isoformat())
            
            query += " GROUP BY success"
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            total_conversions = 0
            successful_conversions = 0
            
            for success, count in results:
                total_conversions += count
                if success:
                    successful_conversions += count
            
            success_rate = (successful_conversions / total_conversions * 100) if total_conversions > 0 else 0
            
            conn.close()
            
            return {
                'total_conversions': total_conversions,
                'successful_conversions': successful_conversions,
                'failed_conversions': total_conversions - successful_conversions,
                'success_rate': round(success_rate, 2),
                'period': {
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None
                }
            }
            
        except Exception as e:
            logging.error(f"Error calculating success rate: {e}")
            return {}
    
    def get_language_pair_metrics(self, start_date: datetime = None, 
                                 end_date: datetime = None) -> Dict[str, Any]:
        """Get metrics by language pair."""
        try:
            conn = sqlite3.connect(self.analytics_manager.db_path)
            
            query = '''
                SELECT source_language, target_language, 
                       COUNT(*) as total,
                       SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful,
                       AVG(conversion_time) as avg_time,
                       AVG(quality_score) as avg_quality
                FROM conversions
            '''
            params = []
            
            if start_date or end_date:
                query += " WHERE 1=1"
                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date.isoformat())
                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date.isoformat())
            
            query += " GROUP BY source_language, target_language"
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            language_metrics = {}
            for row in results:
                source_lang, target_lang, total, successful, avg_time, avg_quality = row
                pair_key = f"{source_lang}_to_{target_lang}"
                
                language_metrics[pair_key] = {
                    'source_language': source_lang,
                    'target_language': target_lang,
                    'total_conversions': total,
                    'successful_conversions': successful,
                    'success_rate': round((successful / total * 100), 2) if total > 0 else 0,
                    'average_conversion_time': round(avg_time, 2) if avg_time else 0,
                    'average_quality_score': round(avg_quality, 2) if avg_quality else 0
                }
            
            conn.close()
            return language_metrics
            
        except Exception as e:
            logging.error(f"Error getting language pair metrics: {e}")
            return {}
    
    def get_ai_model_performance(self, start_date: datetime = None, 
                                end_date: datetime = None) -> Dict[str, Any]:
        """Get performance metrics by AI model."""
        try:
            conn = sqlite3.connect(self.analytics_manager.db_path)
            
            query = '''
                SELECT ai_model_used,
                       COUNT(*) as total,
                       SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful,
                       AVG(conversion_time) as avg_time,
                       AVG(quality_score) as avg_quality
                FROM conversions
            '''
            params = []
            
            if start_date or end_date:
                query += " WHERE 1=1"
                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date.isoformat())
                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date.isoformat())
            
            query += " GROUP BY ai_model_used"
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            model_metrics = {}
            for row in results:
                model, total, successful, avg_time, avg_quality = row
                
                model_metrics[model] = {
                    'total_conversions': total,
                    'successful_conversions': successful,
                    'success_rate': round((successful / total * 100), 2) if total > 0 else 0,
                    'average_conversion_time': round(avg_time, 2) if avg_time else 0,
                    'average_quality_score': round(avg_quality, 2) if avg_quality else 0
                }
            
            conn.close()
            return model_metrics
            
        except Exception as e:
            logging.error(f"Error getting AI model performance: {e}")
            return {}

class UserActivityAnalytics:
    """Analyzes user activity patterns and engagement."""
    
    def __init__(self, analytics_manager: AnalyticsManager):
        self.analytics_manager = analytics_manager
    
    def get_user_engagement_metrics(self, start_date: datetime = None, 
                                   end_date: datetime = None) -> Dict[str, Any]:
        """Get user engagement metrics."""
        try:
            conn = sqlite3.connect(self.analytics_manager.db_path)
            
            query = '''
                SELECT 
                    COUNT(DISTINCT user_id) as unique_users,
                    COUNT(*) as total_actions,
                    AVG(duration) as avg_session_duration,
                    COUNT(DISTINCT session_id) as total_sessions
                FROM user_activity
            '''
            params = []
            
            if start_date or end_date:
                query += " WHERE 1=1"
                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date.isoformat())
                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date.isoformat())
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            
            if result:
                unique_users, total_actions, avg_duration, total_sessions = result
                
                engagement_metrics = {
                    'unique_users': unique_users,
                    'total_actions': total_actions,
                    'average_session_duration': round(avg_duration, 2) if avg_duration else 0,
                    'total_sessions': total_sessions,
                    'actions_per_user': round(total_actions / unique_users, 2) if unique_users > 0 else 0,
                    'sessions_per_user': round(total_sessions / unique_users, 2) if unique_users > 0 else 0
                }
            else:
                engagement_metrics = {}
            
            conn.close()
            return engagement_metrics
            
        except Exception as e:
            logging.error(f"Error getting user engagement metrics: {e}")
            return {}
    
    def get_popular_actions(self, start_date: datetime = None, 
                           end_date: datetime = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular user actions."""
        try:
            conn = sqlite3.connect(self.analytics_manager.db_path)
            
            query = '''
                SELECT action, COUNT(*) as count, AVG(duration) as avg_duration
                FROM user_activity
            '''
            params = []
            
            if start_date or end_date:
                query += " WHERE 1=1"
                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date.isoformat())
                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date.isoformat())
            
            query += " GROUP BY action ORDER BY count DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            popular_actions = []
            for action, count, avg_duration in results:
                popular_actions.append({
                    'action': action,
                    'count': count,
                    'average_duration': round(avg_duration, 2) if avg_duration else 0
                })
            
            conn.close()
            return popular_actions
            
        except Exception as e:
            logging.error(f"Error getting popular actions: {e}")
            return []
    
    def get_user_retention_data(self, days: int = 30) -> Dict[str, Any]:
        """Get user retention data."""
        try:
            conn = sqlite3.connect(self.analytics_manager.db_path)
            
            # Get first-time users
            query = '''
                SELECT user_id, MIN(timestamp) as first_visit
                FROM user_activity
                GROUP BY user_id
            '''
            
            cursor = conn.cursor()
            cursor.execute(query)
            first_visits = cursor.fetchall()
            
            retention_data = {
                'day_1': 0,
                'day_7': 0,
                'day_30': 0
            }
            
            total_users = len(first_visits)
            if total_users == 0:
                conn.close()
                return retention_data
            
            for user_id, first_visit in first_visits:
                first_visit_date = datetime.fromisoformat(first_visit)
                
                # Check if user returned within 1 day
                day_1_cutoff = first_visit_date + timedelta(days=1)
                cursor.execute('''
                    SELECT COUNT(*) FROM user_activity 
                    WHERE user_id = ? AND timestamp > ? AND timestamp <= ?
                ''', (user_id, first_visit, day_1_cutoff.isoformat()))
                if cursor.fetchone()[0] > 0:
                    retention_data['day_1'] += 1
                
                # Check if user returned within 7 days
                day_7_cutoff = first_visit_date + timedelta(days=7)
                cursor.execute('''
                    SELECT COUNT(*) FROM user_activity 
                    WHERE user_id = ? AND timestamp > ? AND timestamp <= ?
                ''', (user_id, first_visit, day_7_cutoff.isoformat()))
                if cursor.fetchone()[0] > 0:
                    retention_data['day_7'] += 1
                
                # Check if user returned within 30 days
                day_30_cutoff = first_visit_date + timedelta(days=30)
                cursor.execute('''
                    SELECT COUNT(*) FROM user_activity 
                    WHERE user_id = ? AND timestamp > ? AND timestamp <= ?
                ''', (user_id, first_visit, day_30_cutoff.isoformat()))
                if cursor.fetchone()[0] > 0:
                    retention_data['day_30'] += 1
            
            # Convert to percentages
            retention_data = {
                'day_1': round((retention_data['day_1'] / total_users) * 100, 2),
                'day_7': round((retention_data['day_7'] / total_users) * 100, 2),
                'day_30': round((retention_data['day_30'] / total_users) * 100, 2),
                'total_users': total_users
            }
            
            conn.close()
            return retention_data
            
        except Exception as e:
            logging.error(f"Error getting user retention data: {e}")
            return {}

class PerformanceAnalytics:
    """Analyzes system performance metrics."""
    
    def __init__(self, analytics_manager: AnalyticsManager):
        self.analytics_manager = analytics_manager
    
    def get_system_performance_metrics(self, start_date: datetime = None, 
                                      end_date: datetime = None) -> Dict[str, Any]:
        """Get system performance metrics."""
        try:
            conn = sqlite3.connect(self.analytics_manager.db_path)
            
            query = '''
                SELECT metric_name, AVG(value) as avg_value, 
                       MIN(value) as min_value, MAX(value) as max_value,
                       COUNT(*) as data_points
                FROM performance_metrics
            '''
            params = []
            
            if start_date or end_date:
                query += " WHERE 1=1"
                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date.isoformat())
                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date.isoformat())
            
            query += " GROUP BY metric_name"
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            performance_metrics = {}
            for row in results:
                metric_name, avg_value, min_value, max_value, data_points = row
                
                performance_metrics[metric_name] = {
                    'average_value': round(avg_value, 2) if avg_value else 0,
                    'minimum_value': round(min_value, 2) if min_value else 0,
                    'maximum_value': round(max_value, 2) if max_value else 0,
                    'data_points': data_points
                }
            
            conn.close()
            return performance_metrics
            
        except Exception as e:
            logging.error(f"Error getting system performance metrics: {e}")
            return {}
    
    def get_response_time_trends(self, start_date: datetime = None, 
                                end_date: datetime = None) -> List[Dict[str, Any]]:
        """Get response time trends over time."""
        try:
            conn = sqlite3.connect(self.analytics_manager.db_path)
            
            query = '''
                SELECT DATE(timestamp) as date, AVG(value) as avg_response_time
                FROM performance_metrics
                WHERE metric_name = 'response_time'
            '''
            params = []
            
            if start_date or end_date:
                query += " AND 1=1"
                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date.isoformat())
                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date.isoformat())
            
            query += " GROUP BY DATE(timestamp) ORDER BY date"
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            trends = []
            for date, avg_response_time in results:
                trends.append({
                    'date': date,
                    'average_response_time': round(avg_response_time, 2) if avg_response_time else 0
                })
            
            conn.close()
            return trends
            
        except Exception as e:
            logging.error(f"Error getting response time trends: {e}")
            return []

class ReportGenerator:
    """Generates comprehensive analytics reports."""
    
    def __init__(self, analytics_manager: AnalyticsManager):
        self.analytics_manager = analytics_manager
        self.conversion_analytics = ConversionAnalytics(analytics_manager)
        self.user_analytics = UserActivityAnalytics(analytics_manager)
        self.performance_analytics = PerformanceAnalytics(analytics_manager)
    
    def generate_comprehensive_report(self, start_date: datetime = None, 
                                    end_date: datetime = None) -> Dict[str, Any]:
        """Generate a comprehensive analytics report."""
        try:
            report = {
                'report_generated_at': datetime.now().isoformat(),
                'period': {
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None
                },
                'conversion_metrics': self.conversion_analytics.get_conversion_success_rate(start_date, end_date),
                'language_pair_metrics': self.conversion_analytics.get_language_pair_metrics(start_date, end_date),
                'ai_model_performance': self.conversion_analytics.get_ai_model_performance(start_date, end_date),
                'user_engagement': self.user_analytics.get_user_engagement_metrics(start_date, end_date),
                'popular_actions': self.user_analytics.get_popular_actions(start_date, end_date),
                'user_retention': self.user_analytics.get_user_retention_data(),
                'system_performance': self.performance_analytics.get_system_performance_metrics(start_date, end_date),
                'response_time_trends': self.performance_analytics.get_response_time_trends(start_date, end_date)
            }
            
            return report
            
        except Exception as e:
            logging.error(f"Error generating comprehensive report: {e}")
            return {'error': str(e)}
    
    def save_report(self, report: Dict[str, Any], filename: str = None) -> str:
        """Save report to file."""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"analytics_report_{timestamp}.json"
            
            filepath = os.path.join("instance", "reports", filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
            
            return filepath
            
        except Exception as e:
            logging.error(f"Error saving report: {e}")
            return ""

# Global instances
analytics_manager = AnalyticsManager()
conversion_analytics = ConversionAnalytics(analytics_manager)
user_activity_analytics = UserActivityAnalytics(analytics_manager)
performance_analytics = PerformanceAnalytics(analytics_manager)
report_generator = ReportGenerator(analytics_manager)

def get_analytics_manager():
    """Get the global analytics manager instance."""
    return analytics_manager

def get_conversion_analytics():
    """Get the global conversion analytics instance."""
    return conversion_analytics

def get_user_activity_analytics():
    """Get the global user activity analytics instance."""
    return user_activity_analytics

def get_performance_analytics():
    """Get the global performance analytics instance."""
    return performance_analytics

def get_report_generator():
    """Get the global report generator instance."""
    return report_generator 