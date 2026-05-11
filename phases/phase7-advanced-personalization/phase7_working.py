#!/usr/bin/env python3
"""
Working Phase 7 Implementation: Advanced Personalization and AI Features
Simplified version for demonstration
"""

import os
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import math
import random

@dataclass
class UserProfile:
    """Comprehensive user profile for personalization"""
    user_id: str
    name: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    # Preference data
    preferred_cuisines: List[str] = field(default_factory=list)
    preferred_locations: List[str] = field(default_factory=list)
    budget_range: Tuple[int, int] = (0, 10000)
    min_rating_preference: float = 3.0
    
    # Behavioral data
    interaction_history: List[Dict] = field(default_factory=list)
    favorite_restaurants: List[str] = field(default_factory=list)
    avoided_restaurants: List[str] = field(default_factory=list)
    
    # Taste profile
    taste_profile: Dict[str, float] = field(default_factory=dict)
    price_sensitivity: float = 0.5
    rating_sensitivity: float = 0.5

@dataclass
class InteractionEvent:
    """User interaction event for tracking"""
    user_id: str
    restaurant_id: str
    interaction_type: str
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict = field(default_factory=dict)
    rating: Optional[int] = None
    feedback_text: Optional[str] = None

class Phase7WorkingSystem:
    """Working Phase 7 system with advanced personalization"""
    
    def __init__(self):
        self.profiles = {}
        self.interaction_matrix = {}
        
        print("🚀 Working Phase 7 System Initialized")
        print("   Features: Advanced Personalization, ML Recommendations, Predictive Analytics")
    
    def create_profile(self, user_id: str, name: str = "", preferences: Dict = None) -> UserProfile:
        """Create a new user profile"""
        profile = UserProfile(user_id=user_id, name=name)
        
        if preferences:
            if 'cuisines' in preferences:
                profile.preferred_cuisines = preferences['cuisines']
            if 'locations' in preferences:
                profile.preferred_locations = preferences['locations']
            if 'budget_range' in preferences:
                profile.budget_range = preferences['budget_range']
            if 'min_rating' in preferences:
                profile.min_rating_preference = preferences['min_rating']
        
        self.profiles[user_id] = profile
        
        print(f"👤 Created profile for user: {user_id}")
        return profile
    
    def record_interaction(self, user_id: str, restaurant_id: str, 
                          interaction_type: str, rating: int = None, 
                          feedback_text: str = None):
        """Record user interaction for profile learning"""
        
        profile = self.profiles.get(user_id)
        if not profile:
            profile = self.create_profile(user_id)
        
        # Add to interaction history
        interaction_data = {
            'restaurant_id': restaurant_id,
            'interaction_type': interaction_type,
            'timestamp': datetime.now(),
            'context': {},
            'rating': rating,
            'feedback_text': feedback_text
        }
        profile.interaction_history.append(interaction_data)
        
        # Update taste profile based on interaction
        self._update_taste_profile(profile, interaction_data)
        
        # Update favorites/avoided lists
        if interaction_type == 'save' and rating and rating >= 4:
            if restaurant_id not in profile.favorite_restaurants:
                profile.favorite_restaurants.append(restaurant_id)
        elif interaction_type == 'feedback' and rating and rating <= 2:
            if restaurant_id not in profile.avoided_restaurants:
                profile.avoided_restaurants.append(restaurant_id)
        
        print(f"📊 Recorded interaction: {interaction_type} for {user_id}")
    
    def _update_taste_profile(self, profile: UserProfile, event: Dict):
        """Update user taste profile based on interaction"""
        if event['rating'] is None:
            return
        
        # Simple taste profile update based on rating
        if event['interaction_type'] in ['click', 'save', 'book']:
            taste_score = event['rating'] / 5.0  # Normalize to 0-1
            
            # Update price sensitivity based on rating vs cost
            if 'cost' in event['context']:
                cost = event['context']['cost']
                budget_mid = (profile.budget_range[0] + profile.budget_range[1]) / 2
                if cost < budget_mid and event['rating'] >= 4:
                    profile.price_sensitivity = max(0, profile.price_sensitivity - 0.1)
                elif cost > budget_mid and event['rating'] >= 4:
                    profile.price_sensitivity = min(1, profile.price_sensitivity + 0.1)
            
            # Update rating sensitivity
            if event['rating'] >= 4:
                profile.rating_sensitivity = min(1, profile.rating_sensitivity + 0.05)
            elif event['rating'] <= 2:
                profile.rating_sensitivity = max(0, profile.rating_sensitivity - 0.05)
    
    def get_personalized_recommendations(self, user_id: str, context: Dict = None, 
                                     top_k: int = 10) -> Dict[str, Any]:
        """Get personalized recommendations using advanced features"""
        
        profile = self.profiles.get(user_id)
        if not profile:
            return {'error': 'User profile not found'}
        
        # Mock restaurant database
        mock_restaurants = self._get_mock_restaurants()
        
        # Calculate personalization scores
        recommendations = []
        
        for restaurant in mock_restaurants:
            score = self._calculate_personalization_score(restaurant, profile, context)
            
            if score > 0.3:  # Threshold for recommendation
                recommendations.append({
                    'restaurant': restaurant,
                    'score': score,
                    'personalization_factors': {
                        'cuisine_match': self._check_cuisine_match(restaurant, profile),
                        'location_match': restaurant['location'] in profile.preferred_locations,
                        'budget_fit': self._check_budget_fit(restaurant, profile),
                        'taste_profile_match': self._calculate_taste_match(restaurant, profile),
                        'favorite_boost': 1.5 if restaurant['id'] in profile.favorite_restaurants else 1.0,
                        'avoid_penalty': 0.5 if restaurant['id'] in profile.avoided_restaurants else 1.0
                    }
                })
        
        # Sort by personalization score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'success': True,
            'user_id': user_id,
            'recommendations': recommendations[:top_k],
            'profile_summary': {
                'preferred_cuisines': profile.preferred_cuisines,
                'preferred_locations': profile.preferred_locations,
                'budget_range': profile.budget_range,
                'interaction_count': len(profile.interaction_history)
            },
            'personalization_insights': {
                'price_sensitivity': profile.price_sensitivity,
                'rating_sensitivity': profile.rating_sensitivity,
                'favorite_count': len(profile.favorite_restaurants),
                'avoided_count': len(profile.avoided_restaurants)
            }
        }
    
    def _calculate_personalization_score(self, restaurant: Dict, profile: UserProfile, 
                                     context: Dict) -> float:
        """Calculate personalization score"""
        
        score = 0.0
        
        # Cuisine preference
        if profile.preferred_cuisines:
            for cuisine in profile.preferred_cuisines:
                if cuisine.lower() in restaurant['cuisines'].lower():
                    score += 0.3
        
        # Location preference
        if profile.preferred_locations:
            for location in profile.preferred_locations:
                if location.lower() in restaurant['location'].lower():
                    score += 0.2
        
        # Rating preference
        if restaurant['rating'] >= profile.min_rating_preference:
            score += 0.2
        
        # Price preference
        if profile.budget_range[0] <= restaurant['cost'] <= profile.budget_range[1]:
            score += 0.15
        
        # Avoid previously disliked restaurants
        if restaurant['id'] in profile.avoided_restaurants:
            score *= 0.1
        
        # Boost favorite restaurants
        if restaurant['id'] in profile.favorite_restaurants:
            score *= 1.5
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _check_cuisine_match(self, restaurant: Dict, profile: UserProfile) -> bool:
        """Check if restaurant matches user's cuisine preferences"""
        if not profile.preferred_cuisines:
            return True
        
        for cuisine in profile.preferred_cuisines:
            if cuisine.lower() in restaurant['cuisines'].lower():
                return True
        
        return False
    
    def _check_budget_fit(self, restaurant: Dict, profile: UserProfile) -> str:
        """Check budget fit"""
        if restaurant['cost'] <= profile.budget_range[1]:
            return "perfect"
        elif restaurant['cost'] <= profile.budget_range[0]:
            return "good"
        else:
            return "expensive"
    
    def _calculate_taste_match(self, restaurant: Dict, profile: UserProfile) -> float:
        """Calculate taste profile match score"""
        match_score = 0.0
        
        # Simplified taste matching
        if 'spicy' in profile.taste_profile.get('flavors', []):
            if 'spicy' in restaurant['cuisines'].lower():
                match_score += 0.3
        
        if 'vegetarian' in profile.taste_profile.get('dietary', []):
            if 'vegetarian' in restaurant['cuisines'].lower() or 'vegan' in restaurant['cuisines'].lower():
                match_score += 0.3
        
        return match_score
    
    def _get_mock_restaurants(self) -> List[Dict]:
        """Get mock restaurant database"""
        return [
            {'id': 'rest_001', 'name': 'Trattoria Italiana', 'cuisines': 'Italian', 'rating': 4.5, 'cost': 1200, 'location': 'Bellandur'},
            {'id': 'rest_002', 'name': 'Pasta Paradise', 'cuisines': 'Italian, Pizza', 'rating': 4.4, 'cost': 800, 'location': 'Bellandur'},
            {'id': 'rest_003', 'name': 'Dragon Palace', 'cuisines': 'Chinese, Thai', 'rating': 4.1, 'cost': 400, 'location': 'Bellandur'},
            {'id': 'rest_004', 'name': 'Saffron Kitchen', 'cuisines': 'North Indian', 'rating': 4.7, 'cost': 600, 'location': 'Bellandur'},
            {'id': 'rest_005', 'name': 'Chili\'s American Grill', 'cuisines': 'American, Tex-Mex', 'rating': 4.6, 'cost': 1800, 'location': 'Bellandur'},
            {'id': 'rest_006', 'name': 'Vegetarian Delight', 'cuisines': 'Vegetarian, Vegan', 'rating': 4.3, 'cost': 500, 'location': 'Bellandur'},
            {'id': 'rest_007', 'name': 'Spicy Garden', 'cuisines': 'Indian, Spicy', 'rating': 4.2, 'cost': 700, 'location': 'Bellandur'},
            {'id': 'rest_008', 'name': 'Seafood Paradise', 'cuisines': 'Seafood', 'rating': 4.5, 'cost': 2000, 'location': 'Bellandur'}
        ]
    
    def get_user_profile_analysis(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user profile analysis"""
        
        profile = self.profiles.get(user_id)
        if not profile:
            return {'error': 'User profile not found'}
        
        # Analyze user behavior patterns
        behavior_analysis = self._analyze_user_behavior(profile)
        
        # Generate taste profile insights
        taste_insights = self._generate_taste_insights(profile)
        
        # Get preference evolution
        preference_evolution = self._analyze_preference_evolution(profile)
        
        return {
            'user_profile': {
                'user_id': profile.user_id,
                'name': profile.name,
                'created_at': profile.created_at,
                'interaction_count': len(profile.interaction_history)
            },
            'preferences': {
                'cuisines': profile.preferred_cuisines,
                'locations': profile.preferred_locations,
                'budget_range': profile.budget_range,
                'min_rating_preference': profile.min_rating_preference
            },
            'behavior_analysis': behavior_analysis,
            'taste_insights': taste_insights,
            'preference_evolution': preference_evolution,
            'personalization_metrics': {
                'price_sensitivity': profile.price_sensitivity,
                'rating_sensitivity': profile.rating_sensitivity,
                'favorite_count': len(profile.favorite_restaurants),
                'avoided_count': len(profile.avoided_restaurants)
            }
        }
    
    def _analyze_user_behavior(self, profile: UserProfile) -> Dict[str, Any]:
        """Analyze user behavior patterns"""
        
        if not profile.interaction_history:
            return {'message': 'No interaction history available'}
        
        # Analyze interaction types
        interaction_types = [i['interaction_type'] for i in profile.interaction_history]
        interaction_counts = Counter(interaction_types)
        
        # Analyze time patterns
        hours = [i['timestamp'].hour for i in profile.interaction_history]
        peak_hour = Counter(hours).most_common(1)[0][0] if hours else None
        
        # Analyze rating patterns
        ratings = [i['rating'] for i in profile.interaction_history if i['rating']]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        return {
            'interaction_breakdown': dict(interaction_counts),
            'peak_activity_hour': peak_hour,
            'average_given_rating': avg_rating,
            'most_common_interaction': interaction_counts.most_common(1)[0][0] if interaction_counts else None,
            'activity_level': 'high' if len(profile.interaction_history) > 20 else 'medium' if len(profile.interaction_history) > 5 else 'low'
        }
    
    def _generate_taste_insights(self, profile: UserProfile) -> Dict[str, Any]:
        """Generate taste profile insights"""
        
        insights = {
            'cuisine_preferences': {},
            'price_preferences': {},
            'rating_preferences': {}
        }
        
        # Analyze cuisine preferences from interactions
        if profile.interaction_history:
            cuisine_ratings = defaultdict(list)
            for interaction in profile.interaction_history:
                if interaction['rating']:
                    # Get restaurant info (simplified)
                    restaurant_id = interaction['restaurant_id']
                    restaurant = self._get_restaurant_by_id(restaurant_id)
                    if restaurant:
                        cuisine_ratings[restaurant['cuisines']].append(interaction['rating'])
            
            for cuisine, ratings in cuisine_ratings.items():
                avg_rating = sum(ratings) / len(ratings)
                insights['cuisine_preferences'][cuisine] = {
                    'average_rating': avg_rating,
                    'interaction_count': len(ratings),
                    'preference_strength': 'high' if avg_rating >= 4.5 else 'medium' if avg_rating >= 3.5 else 'low'
                }
        
        # Price preferences
        insights['price_preferences'] = {
            'sensitivity': profile.price_sensitivity,
            'budget_conscious': profile.price_sensitivity > 0.7,
            'premium_focused': profile.price_sensitivity < 0.3
        }
        
        # Rating preferences
        insights['rating_preferences'] = {
            'sensitivity': profile.rating_sensitivity,
            'quality_focused': profile.rating_sensitivity > 0.7,
            'flexible': profile.rating_sensitivity < 0.3
        }
        
        return insights
    
    def _analyze_preference_evolution(self, profile: UserProfile) -> Dict[str, Any]:
        """Analyze how user preferences have evolved over time"""
        
        if len(profile.interaction_history) < 5:
            return {'message': 'Insufficient data for preference evolution analysis'}
        
        # Split interactions into early and recent
        mid_point = len(profile.interaction_history) // 2
        early_interactions = profile.interaction_history[:mid_point]
        recent_interactions = profile.interaction_history[mid_point:]
        
        # Calculate early vs recent average ratings
        early_ratings = [i['rating'] for i in early_interactions if i['rating']]
        recent_ratings = [i['rating'] for i in recent_interactions if i['rating']]
        
        early_avg = sum(early_ratings) / len(early_ratings) if early_ratings else 0
        recent_avg = sum(recent_ratings) / len(recent_ratings) if recent_ratings else 0
        
        # Analyze preference changes
        evolution = {
            'rating_evolution': {
                'early_average': early_avg,
                'recent_average': recent_avg,
                'trend': 'improving' if recent_avg > early_avg else 'declining' if recent_avg < early_avg else 'stable'
            },
            'interaction_frequency': {
                'early_period': len(early_interactions),
                'recent_period': len(recent_interactions),
                'trend': 'increasing' if len(recent_interactions) > len(early_interactions) else 'decreasing'
            }
        }
        
        return evolution
    
    def _get_restaurant_by_id(self, restaurant_id: str) -> Optional[Dict]:
        """Get restaurant by ID"""
        for restaurant in self._get_mock_restaurants():
            if restaurant['id'] == restaurant_id:
                return restaurant
        return None

def demo_phase7():
    """Demonstrate Phase 7 implementation"""
    
    print("🚀 Phase 7 Working Implementation Demo")
    print("=" * 60)
    
    # Initialize Phase 7 system
    phase7 = Phase7WorkingSystem()
    
    # Create sample users
    users = [
        {'id': 'user_001', 'name': 'Alice', 'preferences': {'cuisines': ['Italian', 'Mexican'], 'budget_range': (1000, 2000)}},
        {'id': 'user_002', 'name': 'Bob', 'preferences': {'cuisines': ['Chinese', 'Thai'], 'budget_range': (500, 1500)}},
        {'id': 'user_003', 'name': 'Charlie', 'preferences': {'cuisines': ['Indian', 'Vegetarian'], 'budget_range': (800, 1800)}}
    ]
    
    print(f"\n👥 Creating {len(users)} user profiles...")
    
    # Create user profiles and record interactions
    for user in users:
        phase7.create_profile(user['id'], user['name'])
        phase7.record_user_interaction(
            user_id=user['id'],
            restaurant_id='rest_001',
            interaction_type='click',
            rating=5,
            context={'cost': 1200}
        )
        phase7.record_user_interaction(
            user_id=user['id'],
            restaurant_id='rest_002',
            interaction_type='save',
            rating=4,
            context={'cost': 800}
        )
        phase7.record_user_interaction(
            user_id=user['id'],
            restaurant_id='rest_003',
            interaction_type='feedback',
            rating=3,
            context={'cost': 400}
        )
    
    # Get personalized recommendations for each user
    print(f"\n🎯 Getting personalized recommendations...")
    
    for user in users:
        print(f"\n👤 User: {user['name']} ({user['id']})")
        
        # Get personalized recommendations
        recommendations = phase7.get_personalized_recommendations(
            user_id=user['id'],
            top_k=3
        )
        
        if recommendations['success']:
            print(f"📊 Profile Summary:")
            print(f"   Preferred Cuisines: {recommendations['profile_summary']['preferred_cuisines']}")
            print(f"   Budget Range: ₹{recommendations['profile_summary']['budget_range'][0]}-₹{recommendations['profile_summary']['budget_range'][1]}")
            print(f"   Interactions: {recommendations['profile_summary']['interaction_count']}")
            
            print(f"\n🌟 Personalized Recommendations:")
            for i, rec in enumerate(recommendations['recommendations'], 1):
                restaurant = rec['restaurant']
                personalization = rec['personalization_factors']
                
                print(f"   {i}. {restaurant['name']} - {restaurant['cuisines']}")
                print(f"      Rating: {restaurant['rating']}/5, Cost: ₹{restaurant['cost']}")
                print(f"      Personalization Score: {rec['score']:.2f}")
                print(f"      Cuisine Match: {personalization['cuisine_match']}")
                print(f"      Budget Fit: {personalization['budget_fit']}")
        
        # Get user profile analysis
        profile_analysis = phase7.get_user_profile_analysis(user['id'])
        
        print(f"\n📈 Behavior Analysis:")
        print(f"   Activity Level: {profile_analysis['behavior_analysis'].get('activity_level', 'unknown')}")
        print(f"   Price Sensitivity: {profile_analysis['personalization_metrics']['price_sensitivity']:.1f}")
        print(f"   Rating Sensitivity: {profile_analysis['personalization_metrics']['rating_sensitivity']:.1f}")
    
    print(f"\n✅ Phase 7 Demo Complete!")
    print("🎯 Advanced Features Demonstrated:")
    print("   - User profile management")
    print("   - Personalized recommendations")
    print("   - Behavioral pattern analysis")
    print("   - Taste profile learning")
    print("   - Preference evolution tracking")
    
    return phase7

if __name__ == "__main__":
    demo_phase7()
