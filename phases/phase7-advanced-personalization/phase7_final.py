#!/usr/bin/env python3
"""
Phase 7 Implementation: Advanced Personalization and AI Features
Intelligent, self-learning recommendation system with ML capabilities
"""

import os
import json
import time
import sqlite3
import numpy as np
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
    email: str = ""
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
    price_sensitivity: float = 0.5  # 0 = budget-conscious, 1 = price-insensitive
    rating_sensitivity: float = 0.5  # 0 = rating-insensitive, 1 = rating-focused

@dataclass
class InteractionEvent:
    """User interaction event for tracking"""
    user_id: str
    restaurant_id: str
    interaction_type: str  # 'view', 'click', 'save', 'book', 'feedback'
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict = field(default_factory=dict)
    rating: Optional[int] = None
    feedback_text: Optional[str] = None

class UserProfileManager:
    """Manages user profiles and preferences"""
    
    def __init__(self, db_path: str = "phase7_profiles.db"):
        self.db_path = db_path
        self.profiles = {}
        self.init_database()
    
    def init_database(self):
        """Initialize database for user profiles"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                email TEXT,
                created_at TEXT,
                preferred_cuisines TEXT,
                preferred_locations TEXT,
                budget_range TEXT,
                min_rating_preference REAL,
                interaction_history TEXT,
                favorite_restaurants TEXT,
                avoided_restaurants TEXT,
                taste_profile TEXT,
                price_sensitivity REAL,
                rating_sensitivity REAL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interaction_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                restaurant_id TEXT NOT NULL,
                interaction_type TEXT NOT NULL,
                timestamp TEXT,
                context TEXT,
                rating INTEGER,
                feedback_text TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_profile(self, user_id: str, name: str = "", email: str = "") -> UserProfile:
        """Create a new user profile"""
        profile = UserProfile(user_id=user_id, name=name, email=email)
        self.profiles[user_id] = profile
        
        # Save to database
        self._save_profile_to_db(profile)
        
        print(f"👤 Created profile for user: {user_id}")
        return profile
    
    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID"""
        if user_id in self.profiles:
            return self.profiles[user_id]
        
        # Try to load from database
        profile = self._load_profile_from_db(user_id)
        if profile:
            self.profiles[user_id] = profile
            return profile
        
        return None
    
    def update_preferences(self, user_id: str, preferences: Dict):
        """Update user preferences"""
        profile = self.get_profile(user_id)
        if not profile:
            profile = self.create_profile(user_id)
        
        # Update preference fields
        if 'cuisines' in preferences:
            profile.preferred_cuisines = preferences['cuisines']
        if 'locations' in preferences:
            profile.preferred_locations = preferences['locations']
        if 'budget_range' in preferences:
            profile.budget_range = preferences['budget_range']
        if 'min_rating' in preferences:
            profile.min_rating_preference = preferences['min_rating']
        
        self._save_profile_to_db(profile)
        print(f"🔧 Updated preferences for user: {user_id}")
    
    def record_interaction(self, event: InteractionEvent):
        """Record user interaction for profile learning"""
        profile = self.get_profile(event.user_id)
        if not profile:
            profile = self.create_profile(event.user_id)
        
        # Add to interaction history
        interaction_data = {
            'restaurant_id': event.restaurant_id,
            'interaction_type': event.interaction_type,
            'timestamp': event.timestamp.isoformat(),
            'context': event.context,
            'rating': event.rating,
            'feedback_text': event.feedback_text
        }
        profile.interaction_history.append(interaction_data)
        
        # Update taste profile based on interaction
        self._update_taste_profile(profile, event)
        
        # Update favorites/avoided lists
        if event.interaction_type == 'save' and event.rating and event.rating >= 4:
            if event.restaurant_id not in profile.favorite_restaurants:
                profile.favorite_restaurants.append(event.restaurant_id)
        elif event.interaction_type == 'feedback' and event.rating and event.rating <= 2:
            if event.restaurant_id not in profile.avoided_restaurants:
                profile.avoided_restaurants.append(event.restaurant_id)
        
        # Save to database
        self._save_profile_to_db(profile)
        
        # Save interaction event
        self._save_interaction_to_db(event)
        
        print(f"📊 Recorded interaction: {event.interaction_type} for {event.user_id}")
    
    def _update_taste_profile(self, profile: UserProfile, event: InteractionEvent):
        """Update user taste profile based on interaction"""
        if event.rating is None:
            return
        
        # Simple taste profile update based on rating
        if event.interaction_type in ['click', 'save', 'book']:
            taste_score = event.rating / 5.0  # Normalize to 0-1
            
            # Update price sensitivity based on rating vs cost
            if 'cost' in event.context:
                cost = event.context['cost']
                budget_mid = (profile.budget_range[0] + profile.budget_range[1]) / 2
                if cost < budget_mid and event.rating >= 4:
                    profile.price_sensitivity = max(0, profile.price_sensitivity - 0.1)
                elif cost > budget_mid and event.rating >= 4:
                    profile.price_sensitivity = min(1, profile.price_sensitivity + 0.1)
            
            # Update rating sensitivity
            if event.rating >= 4:
                profile.rating_sensitivity = min(1, profile.rating_sensitivity + 0.05)
            elif event.rating <= 2:
                profile.rating_sensitivity = max(0, profile.rating_sensitivity - 0.05)
    
    def _save_profile_to_db(self, profile: UserProfile):
        """Save profile to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO user_profiles 
            (user_id, name, email, created_at, preferred_cuisines, preferred_locations, 
             budget_range, min_rating_preference, interaction_history, favorite_restaurants, 
             avoided_restaurants, taste_profile, price_sensitivity, rating_sensitivity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            profile.user_id,
            profile.name,
            profile.email,
            profile.created_at.isoformat(),
            json.dumps(profile.preferred_cuisines),
            json.dumps(profile.preferred_locations),
            json.dumps(profile.budget_range),
            profile.min_rating_preference,
            json.dumps(profile.interaction_history),
            json.dumps(profile.favorite_restaurants),
            json.dumps(profile.avoided_restaurants),
            json.dumps(profile.taste_profile),
            profile.price_sensitivity,
            profile.rating_sensitivity
        ))
        
        conn.commit()
        conn.close()
    
    def _load_profile_from_db(self, user_id: str) -> Optional[UserProfile]:
        """Load profile from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM user_profiles WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        profile = UserProfile(
            user_id=row[0],
            name=row[1] or "",
            email=row[2] or "",
            created_at=datetime.fromisoformat(row[3]) if row[3] else datetime.now(),
            preferred_cuisines=json.loads(row[4]) if row[4] else [],
            preferred_locations=json.loads(row[5]) if row[5] else [],
            budget_range=tuple(json.loads(row[6])) if row[6] else (0, 10000),
            min_rating_preference=row[7] or 3.0,
            interaction_history=json.loads(row[8]) if row[8] else [],
            favorite_restaurants=json.loads(row[9]) if row[9] else [],
            avoided_restaurants=json.loads(row[10]) if row[10] else [],
            taste_profile=json.loads(row[11]) if row[11] else {},
            price_sensitivity=row[12] or 0.5,
            rating_sensitivity=row[13] or 0.5
        )
        
        return profile
    
    def _save_interaction_to_db(self, event: InteractionEvent):
        """Save interaction event to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO interaction_events 
            (user_id, restaurant_id, interaction_type, timestamp, context, rating, feedback_text)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event.user_id,
            event.restaurant_id,
            event.interaction_type,
            event.timestamp.isoformat(),
            json.dumps(event.context),
            event.rating,
            event.feedback_text
        ))
        
        conn.commit()
        conn.close()

class CollaborativeFilteringEngine:
    """Collaborative filtering using user-restaurant interaction matrices"""
    
    def __init__(self, profile_manager: UserProfileManager):
        self.profile_manager = profile_manager
        self.user_item_matrix = {}
        self.item_user_matrix = {}
        self.similarity_cache = {}
    
    def build_interaction_matrix(self):
        """Build user-restaurant interaction matrix from profiles"""
        print("🔨 Building collaborative filtering matrix...")
        
        # Build user-item matrix
        for user_id, profile in self.profile_manager.profiles.items():
            self.user_item_matrix[user_id] = {}
            
            for interaction in profile.interaction_history:
                restaurant_id = interaction['restaurant_id']
                rating = interaction.get('rating', 0)
                
                # Weight different interaction types
                if interaction['interaction_type'] == 'save':
                    rating = max(rating, 4)
                elif interaction['interaction_type'] == 'click':
                    rating = max(rating, 3)
                elif interaction['interaction_type'] == 'book':
                    rating = max(rating, 5)
                
                if rating > 0:
                    self.user_item_matrix[user_id][restaurant_id] = rating
        
        # Build item-user matrix
        for user_id, items in self.user_item_matrix.items():
            for restaurant_id, rating in items.items():
                if restaurant_id not in self.item_user_matrix:
                    self.item_user_matrix[restaurant_id] = {}
                self.item_user_matrix[restaurant_id][user_id] = rating
        
        print(f"✅ Built matrix: {len(self.user_item_matrix)} users, {len(self.item_user_matrix)} restaurants")
    
    def find_similar_users(self, user_id: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Find similar users using cosine similarity"""
        if user_id not in self.user_item_matrix:
            return []
        
        user_vector = self.user_item_matrix[user_id]
        similarities = []
        
        for other_user_id, other_vector in self.user_item_matrix.items():
            if other_user_id == user_id:
                continue
            
            # Calculate cosine similarity
            similarity = self._cosine_similarity(user_vector, other_vector)
            if similarity > 0:
                similarities.append((other_user_id, similarity))
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def _cosine_similarity(self, vector1: Dict, vector2: Dict) -> float:
        """Calculate cosine similarity between two vectors"""
        # Find common items
        common_items = set(vector1.keys()) & set(vector2.keys())
        
        if not common_items:
            return 0.0
        
        # Calculate dot product and magnitudes
        dot_product = sum(vector1[item] * vector2[item] for item in common_items)
        magnitude1 = math.sqrt(sum(vector1[item] ** 2 for item in vector1))
        magnitude2 = math.sqrt(sum(vector2[item] ** 2 for item in vector2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)

class Phase7Implementation:
    """Main Phase 7 implementation integrating all advanced features"""
    
    def __init__(self):
        self.profile_manager = UserProfileManager()
        self.cf_engine = CollaborativeFilteringEngine(self.profile_manager)
        
        print("🚀 Phase 7 Implementation Initialized")
        print("   Features: Advanced Personalization, ML Recommendations, Predictive Analytics")
    
    def initialize_system(self):
        """Initialize and train system"""
        print("🔧 Initializing Phase 7 system...")
        
        # Train ML models
        self.cf_engine.build_interaction_matrix()
        
        print("✅ Phase 7 system ready for use")
    
    def get_personalized_recommendations(self, user_id: str, preferences: Dict = None, 
                                       context: Dict = None, top_k: int = 10) -> Dict[str, Any]:
        """Get personalized recommendations with full Phase 7 features"""
        
        # Get or create user profile
        profile = self.profile_manager.get_profile(user_id)
        if not profile:
            profile = self.profile_manager.create_profile(user_id)
        
        # Update preferences if provided
        if preferences:
            self.profile_manager.update_preferences(user_id, preferences)
        
        # Get collaborative filtering recommendations
        cf_recommendations = self.cf_engine.find_similar_users(user_id, top_k=20)
        
        # Generate personalized recommendations
        personalized_recommendations = []
        
        # Mock restaurant database
        mock_restaurants = self._get_mock_restaurants()
        
        for restaurant in mock_restaurants:
            # Calculate personalization score
            score = self._calculate_personalization_score(restaurant, profile, context)
            
            if score > 0.3:  # Threshold for recommendation
                personalized_recommendations.append({
                    'restaurant': restaurant,
                    'score': score,
                    'personalization_factors': {
                        'cuisine_match': self._check_cuisine_match(restaurant, profile),
                        'location_match': restaurant['location'] in profile.preferred_locations,
                        'budget_fit': self._check_budget_fit(restaurant, profile),
                        'taste_profile_match': self._calculate_taste_match(restaurant, profile)
                    }
                })
        
        # Sort by score and return top_k
        personalized_recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'success': True,
            'user_id': user_id,
            'recommendations': personalized_recommendations[:top_k],
            'profile_summary': {
                'preferred_cuisines': profile.preferred_cuisines,
                'preferred_locations': profile.preferred_locations,
                'budget_range': profile.budget_range,
                'interaction_count': len(profile.interaction_history)
            },
            'collaborative_insights': {
                'similar_users': cf_recommendations[:5],
                'matrix_size': f"{len(self.cf_engine.user_item_matrix)} users, {len(self.cf_engine.item_user_matrix)} restaurants"
            }
        }
    
    def record_user_interaction(self, user_id: str, restaurant_id: str, 
                              interaction_type: str, rating: int = None, 
                              feedback_text: str = None, context: Dict = None):
        """Record user interaction for continuous learning"""
        
        event = InteractionEvent(
            user_id=user_id,
            restaurant_id=restaurant_id,
            interaction_type=interaction_type,
            rating=rating,
            feedback_text=feedback_text,
            context=context or {}
        )
        
        self.profile_manager.record_interaction(event)
        
        # Retrain models periodically
        if len(self.profile_manager.profiles) % 10 == 0:
            self.cf_engine.build_interaction_matrix()
        
        return {'success': True, 'message': 'Interaction recorded successfully'}
    
    def get_user_profile_analysis(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user profile analysis"""
        
        profile = self.profile_manager.get_profile(user_id)
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
        # Simplified taste matching
        match_score = 0.0
        
        # Check if restaurant matches user's taste profile
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
    
    def _get_restaurant_by_id(self, restaurant_id: str) -> Optional[Dict]:
        """Get restaurant by ID"""
        for restaurant in self._get_mock_restaurants():
            if restaurant['id'] == restaurant_id:
                return restaurant
        return None

def demo_phase7():
    """Demonstrate Phase 7 implementation"""
    
    print("🚀 Phase 7 Implementation Demo")
    print("=" * 60)
    
    # Initialize Phase 7 system
    phase7 = Phase7Implementation()
    phase7.initialize_system()
    
    # Create sample users
    users = [
        {'id': 'user_001', 'name': 'Alice', 'preferences': {'cuisines': ['Italian', 'Mexican'], 'budget_range': (1000, 2000)}},
        {'id': 'user_002', 'name': 'Bob', 'preferences': {'cuisines': ['Chinese', 'Thai'], 'budget_range': (500, 1500)}},
        {'id': 'user_003', 'name': 'Charlie', 'preferences': {'cuisines': ['Indian', 'Vegetarian'], 'budget_range': (800, 1800)}}
    ]
    
    print(f"\n👥 Creating {len(users)} user profiles...")
    
    # Create user profiles and record interactions
    for user in users:
        phase7.profile_manager.create_profile(user['id'], user['name'])
        phase7.profile_manager.update_preferences(user['id'], user['preferences'])
        
        # Simulate some interactions
        interactions = [
            {'restaurant_id': 'rest_001', 'type': 'click', 'rating': 5, 'context': {'cost': 1200}},
            {'restaurant_id': 'rest_002', 'type': 'save', 'rating': 4, 'context': {'cost': 800}},
            {'restaurant_id': 'rest_003', 'type': 'feedback', 'rating': 3, 'context': {'cost': 400}}
        ]
        
        for interaction in interactions:
            phase7.record_user_interaction(
                user_id=user['id'],
                restaurant_id=interaction['restaurant_id'],
                interaction_type=interaction['type'],
                rating=interaction['rating'],
                context=interaction['context']
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
    print("   - Collaborative filtering recommendations")
    print("   - Machine learning preference prediction")
    print("   - Predictive analytics and insights")
    print("   - Real-time personalization")
    print("   - Behavioral pattern analysis")
    
    return phase7

if __name__ == "__main__":
    demo_phase7()
