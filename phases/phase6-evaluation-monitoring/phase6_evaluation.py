"""
Phase 6: Evaluation, Monitoring, and Improvement
Goal: Measure recommendation quality and continuously improve system performance.
"""

import json
import time
import sqlite3
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import pandas as pd
import numpy as np

@dataclass
class UserFeedback:
    """Data structure for user feedback on recommendations."""
    recommendation_id: str
    user_id: str
    restaurant_id: str
    rating: int  # 1-5 stars
    helpful: bool  # Was the recommendation helpful?
    booked: bool  # Did user book the restaurant?
    feedback_text: Optional[str] = None
    timestamp: datetime
    improvement_suggestions: Optional[List[str]] = None

@dataclass
class PerformanceMetrics:
    """Performance metrics for the recommendation system."""
    total_recommendations: int
    click_through_rate: float
    booking_rate: float
    user_satisfaction_score: float
    avg_response_time: float
    error_rate: float
    token_usage: int
    cost_per_recommendation: float

class MetricsCollector:
    """Collects and stores system performance metrics."""
    
    def __init__(self, db_path: str = "metrics.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for metrics storage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recommendation_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                restaurant_id TEXT NOT NULL,
                rating INTEGER NOT NULL,
                helpful BOOLEAN NOT NULL,
                booked BOOLEAN NOT NULL,
                feedback_text TEXT,
                improvement_suggestions TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                total_recommendations INTEGER NOT NULL,
                total_clicks INTEGER NOT NULL,
                total_bookings INTEGER NOT NULL,
                avg_satisfaction REAL NOT NULL,
                avg_response_time REAL NOT NULL,
                errors INTEGER NOT NULL,
                token_usage INTEGER NOT NULL,
                api_cost REAL NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommendation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                preferences TEXT NOT NULL,
                recommendations TEXT NOT NULL,
                response_time REAL NOT NULL,
                success BOOLEAN NOT NULL,
                error_message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def log_recommendation_request(self, user_id: str, preferences: Dict, 
                              recommendations: List[Dict], response_time: float, 
                              success: bool, error_message: Optional[str] = None):
        """Log recommendation request for performance tracking."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO recommendation_logs 
            (user_id, preferences, recommendations, response_time, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id, 
            json.dumps(preferences), 
            json.dumps(recommendations), 
            response_time, 
            success, 
            error_message
        ))
        
        conn.commit()
        conn.close()
    
    def store_user_feedback(self, feedback: UserFeedback):
        """Store user feedback for analysis."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_feedback 
            (recommendation_id, user_id, restaurant_id, rating, helpful, booked, 
             feedback_text, improvement_suggestions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            feedback.recommendation_id,
            feedback.user_id,
            feedback.restaurant_id,
            feedback.rating,
            feedback.helpful,
            feedback.booked,
            feedback.feedback_text,
            json.dumps(feedback.improvement_suggestions) if feedback.improvement_suggestions else None
        ))
        
        conn.commit()
        conn.close()
    
    def get_performance_metrics(self, days: int = 30) -> PerformanceMetrics:
        """Calculate performance metrics for the specified period."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent performance data
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute("""
            SELECT * FROM performance_metrics 
            WHERE date >= ?
            ORDER BY date DESC
        """, (cutoff_date.date(),))
        
        metrics_data = cursor.fetchall()
        conn.close()
        
        if not metrics_data:
            return PerformanceMetrics(0, 0, 0, 0, 0, 0, 0, 0)
        
        # Calculate aggregate metrics
        total_recs = sum(row[2] for row in metrics_data)
        total_clicks = sum(row[3] for row in metrics_data)
        total_bookings = sum(row[4] for row in metrics_data)
        total_satisfaction = sum(row[5] for row in metrics_data)
        total_response_time = sum(row[6] for row in metrics_data)
        total_errors = sum(row[7] for row in metrics_data)
        total_tokens = sum(row[8] for row in metrics_data)
        total_cost = sum(row[9] for row in metrics_data)
        
        return PerformanceMetrics(
            total_recommendations=total_recs,
            click_through_rate=(total_clicks / total_recs * 100) if total_recs > 0 else 0,
            booking_rate=(total_bookings / total_recs * 100) if total_recs > 0 else 0,
            user_satisfaction_score=(total_satisfaction / len(metrics_data)) if metrics_data else 0,
            avg_response_time=(total_response_time / len(metrics_data)) if metrics_data else 0,
            error_rate=(total_errors / total_recs * 100) if total_recs > 0 else 0,
            token_usage=total_tokens,
            cost_per_recommendation=(total_cost / total_recs) if total_recs > 0 else 0
        )
    
    def get_feedback_analysis(self, days: int = 30) -> Dict:
        """Analyze user feedback patterns."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute("""
            SELECT restaurant_id, rating, helpful, booked, feedback_text, improvement_suggestions
            FROM user_feedback 
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        """, (cutoff_date,))
        
        feedback_data = cursor.fetchall()
        conn.close()
        
        if not feedback_data:
            return {}
        
        # Analyze feedback patterns
        ratings = [row[1] for row in feedback_data]
        helpful_count = sum(1 for row in feedback_data if row[2])
        booking_count = sum(1 for row in feedback_data if row[3])
        
        # Extract improvement suggestions
        all_suggestions = []
        for row in feedback_data:
            if row[5]:  # improvement_suggestions
                suggestions = json.loads(row[5]) if row[5] else []
                all_suggestions.extend(suggestions)
        
        # Count restaurant frequency in feedback
        restaurant_feedback_count = {}
        for row in feedback_data:
            restaurant_id = row[0]
            restaurant_feedback_count[restaurant_id] = restaurant_feedback_count.get(restaurant_id, 0) + 1
        
        return {
            'total_feedback': len(feedback_data),
            'avg_rating': sum(ratings) / len(ratings) if ratings else 0,
            'helpful_rate': (helpful_count / len(feedback_data) * 100) if feedback_data else 0,
            'booking_rate': (booking_count / len(feedback_data) * 100) if feedback_data else 0,
            'common_suggestions': list(set(all_suggestions)),
            'most_mentioned_restaurants': sorted(restaurant_feedback_count.items(), 
                                            key=lambda x: x[1], reverse=True)[:5],
            'rating_distribution': {
                '5_star': ratings.count(5),
                '4_star': ratings.count(4),
                '3_star': ratings.count(3),
                '2_star': ratings.count(2),
                '1_star': ratings.count(1)
            }
        }

class SystemMonitor:
    """Monitors system health and performance in real-time."""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
    
    def log_request(self, response_time: float, success: bool = True):
        """Log a request for monitoring."""
        self.request_count += 1
        self.response_times.append(response_time)
        
        if not success:
            self.error_count += 1
    
    def get_system_status(self) -> Dict:
        """Get current system status."""
        uptime = time.time() - self.start_time
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        error_rate = (self.error_count / self.request_count * 100) if self.request_count > 0 else 0
        
        return {
            'uptime_seconds': uptime,
            'uptime_formatted': str(timedelta(seconds=int(uptime))),
            'total_requests': self.request_count,
            'error_count': self.error_count,
            'error_rate': error_rate,
            'avg_response_time': avg_response_time,
            'requests_per_minute': (self.request_count / (uptime / 60)) if uptime > 0 else 0,
            'status': 'healthy' if error_rate < 5 and avg_response_time < 2.0 else 'degraded'
        }

class FeedbackAnalyzer:
    """Analyzes user feedback for improvement insights."""
    
    def __init__(self):
        pass
    
    def analyze_feedback_patterns(self, feedback_data: List[UserFeedback]) -> Dict:
        """Analyze patterns in user feedback."""
        if not feedback_data:
            return {}
        
        # Analyze rating patterns
        ratings = [f.rating for f in feedback_data]
        avg_rating = sum(ratings) / len(ratings)
        
        # Analyze helpfulness
        helpful_count = sum(1 for f in feedback_data if f.helpful)
        helpful_rate = (helpful_count / len(feedback_data) * 100) if feedback_data else 0
        
        # Analyze booking conversion
        booking_count = sum(1 for f in feedback_data if f.booked)
        booking_rate = (booking_count / len(feedback_data) * 100) if feedback_data else 0
        
        # Extract common improvement suggestions
        all_suggestions = []
        for f in feedback_data:
            if f.improvement_suggestions:
                all_suggestions.extend(f.improvement_suggestions)
        
        suggestion_frequency = {}
        for suggestion in all_suggestions:
            suggestion_frequency[suggestion] = suggestion_frequency.get(suggestion, 0) + 1
        
        # Analyze feedback text sentiment (simple keyword approach)
        positive_keywords = ['good', 'great', 'excellent', 'amazing', 'perfect', 'love', 'best']
        negative_keywords = ['bad', 'terrible', 'awful', 'hate', 'worst', 'disappointing']
        
        positive_count = 0
        negative_count = 0
        
        for f in feedback_data:
            if f.feedback_text:
                text_lower = f.feedback_text.lower()
                positive_count += sum(1 for keyword in positive_keywords if keyword in text_lower)
                negative_count += sum(1 for keyword in negative_keywords if keyword in text_lower)
        
        return {
            'total_feedback': len(feedback_data),
            'avg_rating': avg_rating,
            'helpful_rate': helpful_rate,
            'booking_rate': booking_rate,
            'top_improvement_suggestions': sorted(suggestion_frequency.items(), 
                                              key=lambda x: x[1], reverse=True)[:5],
            'sentiment_analysis': {
                'positive_mentions': positive_count,
                'negative_mentions': negative_count,
                'sentiment_score': (positive_count - negative_count) / len(feedback_data) if feedback_data else 0
            },
            'rating_distribution': {
                'excellent': ratings.count(5),
                'good': ratings.count(4),
                'average': ratings.count(3),
                'poor': ratings.count(2),
                'terrible': ratings.count(1)
            }
        }
    
    def generate_improvement_recommendations(self, analysis: Dict) -> List[str]:
        """Generate actionable improvement recommendations."""
        recommendations = []
        
        # Based on ratings
        if analysis.get('avg_rating', 0) < 3.5:
            recommendations.append("Improve recommendation accuracy - ratings are below average")
        
        # Based on helpfulness
        if analysis.get('helpful_rate', 0) < 70:
            recommendations.append("Refine matching algorithm - users don't find recommendations helpful")
        
        # Based on booking rate
        if analysis.get('booking_rate', 0) < 15:
            recommendations.append("Enhance restaurant information to increase booking conversion")
        
        # Based on sentiment
        sentiment = analysis.get('sentiment_analysis', {})
        if sentiment.get('sentiment_score', 0) < -0.5:
            recommendations.append("Address negative feedback patterns in recommendations")
        
        # Based on common suggestions
        top_suggestions = analysis.get('top_improvement_suggestions', [])
        if top_suggestions:
            most_common = top_suggestions[0][0] if top_suggestions else ""
            if "location" in most_common.lower():
                recommendations.append("Improve location-based filtering and matching")
            if "price" in most_common.lower() or "cost" in most_common.lower():
                recommendations.append("Refine price filtering and budget matching")
            if "cuisine" in most_common.lower():
                recommendations.append("Enhance cuisine preference matching algorithm")
        
        return list(set(recommendations))  # Remove duplicates

class ModelTuner:
    """Tunes and optimizes recommendation models based on feedback."""
    
    def __init__(self):
        self.tuning_history = []
    
    def calculate_rating_adjustment(self, restaurant_id: str, feedback_history: List[UserFeedback]) -> float:
        """Calculate rating adjustment based on user feedback."""
        if not feedback_history:
            return 0.0
        
        # Calculate average feedback for this restaurant
        relevant_feedback = [f for f in feedback_history if f.restaurant_id == restaurant_id]
        
        if not relevant_feedback:
            return 0.0
        
        avg_rating = sum(f.rating for f in relevant_feedback) / len(relevant_feedback)
        helpful_rate = sum(1 for f in relevant_feedback if f.helpful) / len(relevant_feedback)
        
        # Calculate adjustment factor
        if avg_rating >= 4.0 and helpful_rate >= 0.8:
            return 0.1  # Boost highly rated, helpful restaurants
        elif avg_rating <= 2.0:
            return -0.2  # Penalize poorly rated restaurants
        else:
            return 0.0  # No adjustment
    
    def update_scoring_weights(self, performance_metrics: PerformanceMetrics) -> Dict:
        """Update scoring weights based on performance metrics."""
        current_weights = {
            'rating_weight': 0.3,
            'cost_weight': 0.2,
            'location_weight': 0.15,
            'cuisine_weight': 0.2,
            'variety_weight': 0.15
        }
        
        new_weights = current_weights.copy()
        
        # Adjust based on performance
        if performance_metrics.user_satisfaction_score < 3.5:
            # Increase rating weight if satisfaction is low
            new_weights['rating_weight'] = min(0.5, current_weights['rating_weight'] + 0.1)
            new_weights['cost_weight'] = max(0.1, current_weights['cost_weight'] - 0.05)
        
        if performance_metrics.click_through_rate < 20:
            # Increase variety weight if CTR is low
            new_weights['variety_weight'] = min(0.25, current_weights['variety_weight'] + 0.05)
        
        if performance_metrics.booking_rate < 10:
            # Increase location weight if booking rate is low
            new_weights['location_weight'] = min(0.25, current_weights['location_weight'] + 0.05)
        
        # Normalize weights to sum to 1.0
        total_weight = sum(new_weights.values())
        if total_weight > 0:
            new_weights = {k: v/total_weight for k, v in new_weights.items()}
        
        return new_weights
    
    def log_tuning_change(self, change_type: str, old_value: float, new_value: float, reason: str):
        """Log tuning changes for tracking."""
        change_record = {
            'timestamp': datetime.now(),
            'change_type': change_type,
            'old_value': old_value,
            'new_value': new_value,
            'reason': reason,
            'improvement': new_value - old_value
        }
        
        self.tuning_history.append(change_record)
        
        print(f"Tuning Change: {change_type}")
        print(f"  Reason: {reason}")
        print(f"  Change: {old_value} → {new_value}")
        print(f"  Improvement: {change_record['improvement']:.3f}")

class EvaluationService:
    """Main service for evaluation, monitoring, and improvement."""
    
    def __init__(self, db_path: str = "metrics.db"):
        self.metrics_collector = MetricsCollector(db_path)
        self.system_monitor = SystemMonitor()
        self.feedback_analyzer = FeedbackAnalyzer()
        self.model_tuner = ModelTuner()
    
    def collect_feedback(self, user_id: str, recommendation_id: str, restaurant_id: str,
                    rating: int, helpful: bool, booked: bool, 
                    feedback_text: Optional[str] = None) -> bool:
        """Collect user feedback for evaluation."""
        try:
            feedback = UserFeedback(
                recommendation_id=recommendation_id,
                user_id=user_id,
                restaurant_id=restaurant_id,
                rating=rating,
                helpful=helpful,
                booked=booked,
                feedback_text=feedback_text,
                timestamp=datetime.now()
            )
            
            self.metrics_collector.store_user_feedback(feedback)
            return True
            
        except Exception as e:
            print(f"Error collecting feedback: {e}")
            return False
    
    def generate_performance_report(self, days: int = 30) -> Dict:
        """Generate comprehensive performance report."""
        # Get metrics
        performance_metrics = self.metrics_collector.get_performance_metrics(days)
        feedback_analysis = self.metrics_collector.get_feedback_analysis(days)
        system_status = self.system_monitor.get_system_status()
        
        # Generate insights
        feedback_insights = self.feedback_analyzer.analyze_feedback_patterns([])
        improvement_recommendations = self.feedback_analyzer.generate_improvement_recommendations(feedback_insights)
        
        # Get tuning recommendations
        new_weights = self.model_tuner.update_scoring_weights(performance_metrics)
        
        report = {
            'report_period': f"Last {days} days",
            'generated_at': datetime.now().isoformat(),
            'system_status': system_status,
            'performance_metrics': performance_metrics,
            'feedback_analysis': feedback_analysis,
            'improvement_recommendations': improvement_recommendations,
            'model_tuning': {
                'current_weights': new_weights,
                'recommended_changes': improvement_recommendations
            }
        }
        
        return report
    
    def save_report(self, report: Dict, filename: str = "performance_report.json"):
        """Save performance report to file."""
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"Performance report saved to {filename}")
    
    def get_real_time_metrics(self) -> Dict:
        """Get real-time system metrics."""
        return self.system_monitor.get_system_status()

def main():
    """Demonstrate Phase 6 evaluation functionality."""
    evaluation_service = EvaluationService()
    
    print("=== Phase 6: Evaluation & Monitoring Demo ===\n")
    
    # Simulate some feedback data
    sample_feedback = [
        UserFeedback(
            recommendation_id="rec_001",
            user_id="user_123",
            restaurant_id="rest_001",
            rating=5,
            helpful=True,
            booked=True,
            feedback_text="Perfect recommendation! Exactly what I was looking for.",
            improvement_suggestions=["More options like this", "Better location filtering"]
        ),
        UserFeedback(
            recommendation_id="rec_002",
            user_id="user_456",
            restaurant_id="rest_002",
            rating=3,
            helpful=False,
            booked=False,
            feedback_text="Restaurant was too expensive and didn't match my preferences.",
            improvement_suggestions=["Better price filtering", "More accurate cost information"]
        )
    ]
    
    # Collect feedback
    for feedback in sample_feedback:
        success = evaluation_service.collect_feedback(
            feedback.user_id,
            feedback.recommendation_id,
            feedback.restaurant_id,
            feedback.rating,
            feedback.helpful,
            feedback.booked,
            feedback.feedback_text
        )
        print(f"Collected feedback: {'✓' if success else '✗'}")
    
    # Generate performance report
    print("\nGenerating performance report...")
    report = evaluation_service.generate_performance_report(days=30)
    
    # Display key metrics
    print(f"\n📊 Key Metrics:")
    metrics = report['performance_metrics']
    print(f"  Total Recommendations: {metrics.total_recommendations}")
    print(f"  Click-through Rate: {metrics.click_through_rate:.1f}%")
    print(f"  Booking Rate: {metrics.booking_rate:.1f}%")
    print(f"  User Satisfaction: {metrics.user_satisfaction_score:.1f}/5")
    print(f"  Average Response Time: {metrics.avg_response_time:.2f}s")
    print(f"  Error Rate: {metrics.error_rate:.1f}%")
    
    # Display improvement recommendations
    print(f"\n💡 Improvement Recommendations:")
    for i, rec in enumerate(report['improvement_recommendations'], 1):
        print(f"  {i}. {rec}")
    
    # Save report
    evaluation_service.save_report(report)
    
    print(f"\n✓ Phase 6 demo completed!")

if __name__ == "__main__":
    main()
