#!/usr/bin/env python3
"""
Integration Service: Connects Phase 6 evaluation with existing recommendation system
"""

import os
import sys
from typing import Dict, List, Any
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append('/Users/vishalkataria/Documents/Docs')  # Add main project path

from phase6_evaluation_fixed import EvaluationService, UserFeedback
from phase5_real_test import RestaurantRecommendationSystem

class IntegratedRecommendationService:
    """Integrated service combining recommendation engine with Phase 6 evaluation."""
    
    def __init__(self, db_path: str = "integrated_metrics.db"):
        self.recommendation_system = RestaurantRecommendationSystem()
        self.evaluation_service = EvaluationService(db_path)
        
        print("🔗 Integrated Recommendation Service Initialized")
        print("   - Recommendation Engine: Phase 5")
        print("   - Evaluation & Monitoring: Phase 6")
    
    def get_recommendations_with_tracking(self, location: str, budget: int, 
                                       min_rating: float, user_id: str) -> Dict[str, Any]:
        """Get recommendations with full Phase 6 tracking."""
        
        # Start performance tracking
        self.evaluation_service.system_monitor.log_request(0, True)  # Start timing
        
        start_time = datetime.now()
        
        try:
            # Get recommendations from Phase 5 system
            print(f"🔍 Finding restaurants for {location}, budget: {budget}, rating: {min_rating}")
            
            # Load and filter data
            self.recommendation_system.load_zomato_dataset()
            df = self.recommendation_system.convert_to_dataframe()
            df_clean = self.recommendation_system.clean_and_preprocess(df)
            
            # Filter restaurants
            restaurants = self.recommendation_system.filter_restaurants(
                df_clean, location, budget, min_rating
            )
            
            if not restaurants:
                result = {
                    'success': False,
                    'error': 'No restaurants found matching criteria',
                    'recommendations': [],
                    'processing_time_ms': 0
                }
                self.evaluation_service.system_monitor.log_request(0, False)
                return result
            
            # Generate LLM prompt and get recommendations
            user_preferences = {
                'location': location,
                'budget': budget,
                'min_rating': min_rating,
                'top_n': 5
            }
            
            prompt = self.recommendation_system.generate_llm_prompt(user_preferences, restaurants)
            
            # Get LLM response (real API call)
            llm_response = self.recommendation_system.call_groq_api(prompt)
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Log recommendation request
            self.evaluation_service.metrics_collector.log_recommendation_request(
                user_id=user_id,
                preferences=user_preferences,
                recommendations=llm_response.get('recommendations', []),
                response_time=processing_time,
                success=True
            )
            
            # Create interaction records for each recommendation
            for i, rec in enumerate(llm_response.get('recommendations', [])):
                interaction_id = f"{user_id}_{start_time.timestamp()}_{i}"
                
                # Log initial view interaction
                self.evaluation_service.metrics_collector.log_recommendation_request(
                    user_id=user_id,
                    preferences={'viewed_recommendation': True},
                    recommendations=[rec],
                    response_time=0,
                    success=True
                )
            
            result = {
                'success': True,
                'user_id': user_id,
                'recommendations': llm_response.get('recommendations', []),
                'processing_time_ms': processing_time,
                'total_candidates': len(restaurants),
                'interaction_ids': [f"{user_id}_{start_time.timestamp()}_{i}" 
                                   for i in range(len(llm_response.get('recommendations', [])))],
                'timestamp': start_time.isoformat()
            }
            
            # End performance tracking
            self.evaluation_service.system_monitor.log_request(processing_time, True)
            
            print(f"✅ Generated {len(llm_response.get('recommendations', []))} recommendations in {processing_time:.0f}ms")
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            error_msg = str(e)
            
            # Log error
            self.evaluation_service.metrics_collector.log_recommendation_request(
                user_id=user_id,
                preferences={'error': True},
                recommendations=[],
                response_time=processing_time,
                success=False,
                error_message=error_msg
            )
            
            self.evaluation_service.system_monitor.log_request(processing_time, False)
            
            print(f"❌ Recommendation failed: {error_msg}")
            
            return {
                'success': False,
                'error': error_msg,
                'recommendations': [],
                'processing_time_ms': processing_time
            }
    
    def collect_user_interaction(self, user_id: str, interaction_id: str, 
                            interaction_type: str, restaurant_id: str = None,
                            metadata: Dict = None):
        """Collect user interaction with recommendations."""
        
        # Log interaction for Phase 6 tracking
        self.evaluation_service.metrics_collector.log_recommendation_request(
            user_id=user_id,
            preferences={'interaction': interaction_type, 'restaurant_id': restaurant_id},
            recommendations=[],
            response_time=0,
            success=True
        )
        
        print(f"👆 User interaction: {interaction_type} for {restaurant_id or 'recommendation'}")
        
        return {
            'success': True,
            'interaction_type': interaction_type,
            'restaurant_id': restaurant_id,
            'timestamp': datetime.now().isoformat()
        }
    
    def collect_feedback(self, user_id: str, recommendation_id: str, 
                      restaurant_id: str, rating: int, helpful: bool, 
                      booked: bool, feedback_text: str = None):
        """Collect user feedback with full integration."""
        
        # Collect feedback using Phase 6 system
        success = self.evaluation_service.collect_feedback(
            user_id=user_id,
            recommendation_id=recommendation_id,
            restaurant_id=restaurant_id,
            rating=rating,
            helpful=helpful,
            booked=booked,
            feedback_text=feedback_text
        )
        
        if success:
            print(f"⭐ Feedback collected: {rating}/5 stars, helpful: {helpful}")
            
            # Trigger immediate analysis for this feedback
            self._analyze_immediate_feedback(user_id, restaurant_id, rating)
        else:
            print(f"❌ Failed to collect feedback")
        
        return {'success': success}
    
    def _analyze_immediate_feedback(self, user_id: str, restaurant_id: str, rating: int):
        """Analyze feedback immediately and suggest improvements."""
        
        # Get recent feedback for this restaurant
        feedback_analysis = self.evaluation_service.metrics_collector.get_feedback_analysis(days=1)
        
        # Check if this restaurant needs attention
        if rating <= 2:
            print(f"🚨 Alert: Restaurant {restaurant_id} received low rating ({rating}/5)")
            print("   Recommendation: Review restaurant data quality")
            print("   Action: Consider removing from recommendations")
        
        # Check feedback patterns
        if feedback_analysis.get('avg_rating', 5) < 3.5:
            print(f"📉 Alert: Overall satisfaction dropping ({feedback_analysis['avg_rating']:.1f}/5)")
            print("   Recommendation: Review recommendation algorithm")
            print("   Action: Adjust scoring weights")
    
    def get_comprehensive_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate comprehensive report combining recommendation and evaluation data."""
        
        print("📊 Generating comprehensive report...")
        
        # Get performance metrics
        performance_metrics = self.evaluation_service.metrics_collector.get_performance_metrics(days)
        
        # Get feedback analysis
        feedback_analysis = self.evaluation_service.metrics_collector.get_feedback_analysis(days)
        
        # Get system status
        system_status = self.evaluation_service.system_monitor.get_system_status()
        
        # Generate improvement recommendations
        feedback_insights = self.evaluation_service.feedback_analyzer.analyze_feedback_patterns([])
        improvement_recommendations = self.evaluation_service.feedback_analyzer.generate_improvement_recommendations(feedback_insights)
        
        # Get model tuning suggestions
        tuning_suggestions = self.evaluation_service.model_tuner.update_scoring_weights(performance_metrics)
        
        report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'report_period_days': days,
                'integration_version': 'Phase 5 + Phase 6',
                'system_status': 'operational'
            },
            'recommendation_performance': {
                'total_recommendations_generated': performance_metrics.total_recommendations,
                'average_processing_time_ms': performance_metrics.avg_response_time,
                'success_rate': 100 - performance_metrics.error_rate,
                'llm_api_calls': len(self.evaluation_service.metrics_collector.get_feedback_analysis(days)),
                'token_usage': performance_metrics.token_usage
            },
            'user_engagement': {
                'click_through_rate': performance_metrics.click_through_rate,
                'booking_rate': performance_metrics.booking_rate,
                'average_satisfaction': performance_metrics.user_satisfaction_score,
                'total_feedback_collected': feedback_analysis.get('total_feedback', 0),
                'helpful_rate': feedback_analysis.get('helpful_rate', 0)
            },
            'system_health': {
                'uptime_seconds': system_status['uptime_seconds'],
                'error_rate': performance_metrics.error_rate,
                'requests_per_minute': system_status['requests_per_minute'],
                'status': system_status['status']
            },
            'improvement_insights': {
                'top_issues': feedback_analysis.get('common_suggestions', [])[:3],
                'recommended_actions': improvement_recommendations[:5],
                'model_tuning': {
                    'current_weights': tuning_suggestions,
                    'performance_impact': 'Positive' if performance_metrics.user_satisfaction_score > 4.0 else 'Needs Attention'
                }
            }
        }
        
        # Save report
        self.evaluation_service.save_report(report, f"comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        print(f"✅ Comprehensive report generated and saved")
        return report
    
    def get_real_time_dashboard_data(self) -> Dict[str, Any]:
        """Get real-time dashboard data."""
        
        system_status = self.evaluation_service.system_monitor.get_system_status()
        recent_metrics = self.evaluation_service.metrics_collector.get_performance_metrics(days=1)
        
        return {
            'real_time_metrics': {
                'current_status': system_status['status'],
                'uptime': system_status['uptime_formatted'],
                'requests_today': recent_metrics.total_recommendations,
                'avg_response_time': recent_metrics.avg_response_time,
                'error_rate_today': recent_metrics.error_rate
            },
            'performance_trends': {
                'status_emoji': '🟢' if system_status['status'] == 'healthy' else '🟡',
                'performance_grade': 'A' if recent_metrics.avg_response_time < 1.0 else 'B' if recent_metrics.avg_response_time < 2.0 else 'C',
                'user_satisfaction_emoji': '😊' if recent_metrics.user_satisfaction_score > 4.0 else '😐' if recent_metrics.user_satisfaction_score > 3.0 else '😞'
            },
            'alerts': self._generate_alerts(system_status, recent_metrics)
        }
    
    def _generate_alerts(self, system_status: Dict, metrics: Any) -> List[str]:
        """Generate system alerts based on current status."""
        alerts = []
        
        if system_status['status'] != 'healthy':
            alerts.append(f"⚠️ System status: {system_status['status']}")
        
        if system_status['error_rate'] > 5:
            alerts.append(f"🚨 High error rate: {system_status['error_rate']:.1f}%")
        
        if metrics.avg_response_time > 2.0:
            alerts.append(f"⏱️ Slow response time: {metrics.avg_response_time:.2f}s")
        
        if metrics.user_satisfaction_score < 3.5:
            alerts.append(f"💔 Low user satisfaction: {metrics.user_satisfaction_score:.1f}/5")
        
        return alerts if alerts else ["✅ All systems operational"]

# Demo integration
def demo_integration():
    """Demonstrate the integrated Phase 5 + Phase 6 system."""
    
    print("🚀 Phase 5 + Phase 6 Integration Demo")
    print("=" * 50)
    
    # Initialize integrated service
    integrated_service = IntegratedRecommendationService()
    
    # Simulate user session
    user_id = "demo_user_001"
    
    print(f"\n👤 User Session: {user_id}")
    print("-" * 30)
    
    # Get recommendations
    recommendations_result = integrated_service.get_recommendations_with_tracking(
        location="Bellandur",
        budget=2000,
        min_rating=4.0,
        user_id=user_id
    )
    
    if recommendations_result['success']:
        recs = recommendations_result['recommendations']
        print(f"🎯 Generated {len(recs)} recommendations")
        
        # Simulate user interactions
        if recs:
            # Simulate clicking on first recommendation
            integrated_service.collect_user_interaction(
                user_id=user_id,
                interaction_id=recommendations_result['interaction_ids'][0],
                interaction_type='click',
                restaurant_id=recs[0].get('restaurant_name', 'Unknown'),
                metadata={'position': 1}
            )
            
            # Simulate viewing second recommendation
            integrated_service.collect_user_interaction(
                user_id=user_id,
                interaction_id=recommendations_result['interaction_ids'][1],
                interaction_type='view',
                restaurant_id=recs[1].get('restaurant_name', 'Unknown'),
                metadata={'position': 2}
            )
            
            # Collect feedback for first recommendation
            integrated_service.collect_feedback(
                user_id=user_id,
                recommendation_id=recommendations_result['interaction_ids'][0],
                restaurant_id=recs[0].get('restaurant_name', 'Unknown'),
                rating=5,
                helpful=True,
                booked=True,
                feedback_text="Excellent recommendation! Perfect match for my preferences."
            )
            
            # Collect feedback for second recommendation
            integrated_service.collect_feedback(
                user_id=user_id,
                recommendation_id=recommendations_result['interaction_ids'][1],
                restaurant_id=recs[1].get('restaurant_name', 'Unknown'),
                rating=3,
                helpful=False,
                booked=False,
                feedback_text="Too expensive for my budget and location was not ideal."
            )
    
    # Get real-time dashboard data
    dashboard_data = integrated_service.get_real_time_dashboard_data()
    
    print(f"\n📊 Real-Time Dashboard:")
    print(f"   Status: {dashboard_data['real_time_metrics']['current_status']}")
    print(f"   Performance: {dashboard_data['performance_trends']['performance_grade']}")
    print(f"   Satisfaction: {dashboard_data['performance_trends']['user_satisfaction_emoji']}")
    
    if dashboard_data['alerts']:
        print(f"\n🚨 System Alerts:")
        for alert in dashboard_data['alerts']:
            print(f"   {alert}")
    
    # Generate comprehensive report
    print(f"\n📈 Generating Comprehensive Report...")
    comprehensive_report = integrated_service.get_comprehensive_report(days=7)
    
    print(f"\n📋 Report Summary:")
    print(f"   Total Recommendations: {comprehensive_report['recommendation_performance']['total_recommendations_generated']}")
    print(f"   Success Rate: {comprehensive_report['recommendation_performance']['success_rate']:.1f}%")
    print(f"   User Satisfaction: {comprehensive_report['user_engagement']['average_satisfaction']:.1f}/5")
    print(f"   System Status: {comprehensive_report['system_health']['status']}")
    
    print(f"\n✅ Integration Demo Complete!")
    print(f"📁 Reports saved to comprehensive_report_*.json")
    
    return integrated_service

if __name__ == "__main__":
    demo_integration()
