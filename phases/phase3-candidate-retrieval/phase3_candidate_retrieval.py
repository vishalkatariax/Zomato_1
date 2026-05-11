"""
Phase 3: Candidate Retrieval Layer
Goal: Narrow down dataset to highly relevant candidate restaurants.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from phase2_preference_capture import UserPreferences
import re

class RestaurantFilter:
    """Rule-based filtering engine for restaurant recommendations."""
    
    def __init__(self, restaurant_data: pd.DataFrame):
        self.restaurants = restaurant_data.copy()
        self.candidates = pd.DataFrame()
    
    def apply_hard_constraints(self, preferences: UserPreferences) -> pd.DataFrame:
        """Apply mandatory filters (location, budget, minimum rating)."""
        filtered = self.restaurants.copy()
        
        print(f"Starting with {len(filtered)} restaurants")
        
        # Location filter - must match exactly or be in same area
        location_filtered = self._filter_by_location(filtered, preferences.location)
        print(f"After location filter: {len(location_filtered)} restaurants")
        
        # Budget filter - cost must be within or below budget
        budget_filtered = self._filter_by_budget(location_filtered, preferences.budget)
        print(f"After budget filter: {len(budget_filtered)} restaurants")
        
        # Rating filter - minimum rating requirement
        if preferences.rating:
            rating_filtered = self._filter_by_rating(budget_filtered, preferences.rating)
            print(f"After rating filter: {len(rating_filtered)} restaurants")
        else:
            rating_filtered = budget_filtered
        
        self.candidates = rating_filtered
        return rating_filtered
    
    def apply_soft_matching(self, preferences: UserPreferences) -> pd.DataFrame:
        """Apply optional preference matching with scoring."""
        if self.candidates.empty:
            return pd.DataFrame()
        
        candidates_with_scores = self.candidates.copy()
        candidates_with_scores['soft_score'] = 0
        
        # Cuisine preference matching
        if preferences.cuisines:
            candidates_with_scores['cuisine_match_score'] = candidates_with_scores.apply(
                lambda row: self._calculate_cuisine_score(row, preferences.cuisines), axis=1
            )
            candidates_with_scores['soft_score'] += candidates_with_scores['cuisine_match_score']
        
        # Ambiance preference matching
        if preferences.ambiance:
            candidates_with_scores['ambiance_match_score'] = candidates_with_scores.apply(
                lambda row: self._calculate_ambiance_score(row, preferences.ambiance), axis=1
            )
            candidates_with_scores['soft_score'] += candidates_with_scores['ambiance_match_score']
        
        # Meal type preference
        if preferences.meal_type:
            candidates_with_scores['meal_type_score'] = candidates_with_scores.apply(
                lambda row: self._calculate_meal_type_score(row, preferences.meal_type), axis=1
            )
            candidates_with_scores['soft_score'] += candidates_with_scores['meal_type_score']
        
        # Group size consideration
        if preferences.group_size:
            candidates_with_scores['group_size_score'] = candidates_with_scores.apply(
                lambda row: self._calculate_group_size_score(row, preferences.group_size), axis=1
            )
            candidates_with_scores['soft_score'] += candidates_with_scores['group_size_score']
        
        return candidates_with_scores
    
    def _filter_by_location(self, df: pd.DataFrame, location: str) -> pd.DataFrame:
        """Filter restaurants by location with fuzzy matching."""
        location_lower = location.lower()
        
        # Exact match first
        exact_match = df[df['location'].str.lower() == location_lower]
        if not exact_match.empty:
            return exact_match
        
        # Partial match for nearby areas
        partial_match = df[df['location'].str.lower().str.contains(location_lower, na=False)]
        return partial_match
    
    def _filter_by_budget(self, df: pd.DataFrame, budget: int) -> pd.DataFrame:
        """Filter restaurants by budget with some flexibility."""
        # Allow restaurants up to 20% over budget for exceptional cases
        max_budget = budget * 1.2
        return df[df['cost_for_two'] <= max_budget]
    
    def _filter_by_rating(self, df: pd.DataFrame, min_rating: float) -> pd.DataFrame:
        """Filter restaurants by minimum rating."""
        return df[df['rating'] >= min_rating]
    
    def _calculate_cuisine_score(self, restaurant_row, preferred_cuisines: List[str]) -> float:
        """Calculate cuisine preference match score (0-20 points)."""
        if not preferred_cuisines:
            return 0
        
        restaurant_cuisines = str(restaurant_row['cuisines']).lower().split(', ')
        preferred_lower = [c.lower() for c in preferred_cuisines]
        
        # Exact matches get highest score
        exact_matches = sum(1 for c in preferred_lower if c in restaurant_cuisines)
        if exact_matches > 0:
            return min(exact_matches * 10, 20)
        
        # Partial matches for similar cuisines
        partial_score = 0
        for preferred in preferred_lower:
            for restaurant_cuisine in restaurant_cuisines:
                if self._cuisines_similar(preferred, restaurant_cuisine):
                    partial_score += 5
        
        return min(partial_score, 10)
    
    def _calculate_ambiance_score(self, restaurant_row, preferred_ambiance: str) -> float:
        """Calculate ambiance preference match score (0-15 points)."""
        # This would require additional data about restaurant ambiance
        # For now, use heuristics based on cuisine and cost
        cost = restaurant_row['cost_for_two']
        rating = restaurant_row['rating']
        
        if preferred_ambiance.lower() == 'fine dining':
            return 15 if cost > 2000 and rating > 4.0 else 5
        elif preferred_ambiance.lower() == 'casual':
            return 15 if cost < 1500 else 5
        elif preferred_ambiance.lower() == 'romantic':
            return 15 if rating > 4.2 and cost > 1800 else 5
        else:
            return 5  # Default score
    
    def _calculate_meal_type_score(self, restaurant_row, meal_type: str) -> float:
        """Calculate meal type preference score (0-10 points)."""
        # This would require additional data about restaurant specialties
        # For now, use simple heuristics
        return 5  # Default score
    
    def _calculate_group_size_score(self, restaurant_row, group_size: int) -> float:
        """Calculate group size suitability score (0-10 points)."""
        cost_per_person = restaurant_row['cost_for_two'] / 2
        
        if group_size <= 2:
            return 10  # Most restaurants accommodate small groups
        elif group_size <= 4:
            return 8   # Most restaurants accommodate medium groups
        elif group_size <= 6:
            return 5   # Some restaurants accommodate larger groups
        else:
            return 2   # Few restaurants accommodate very large groups
    
    def _cuisines_similar(self, cuisine1: str, cuisine2: str) -> bool:
        """Check if two cuisines are similar."""
        similar_pairs = [
            ('chinese', 'sichuan'), ('chinese', 'hunan'),
            ('italian', 'continental'), ('north indian', 'south indian'),
            ('american', 'bar food'), ('japanese', 'sushi')
        ]
        
        for pair in similar_pairs:
            if (cuisine1 in pair and cuisine2 in pair):
                return True
        
        return cuisine1 == cuisine2

class CandidateScorer:
    """Scores and ranks candidate restaurants for LLM processing."""
    
    def __init__(self):
        pass
    
    def calculate_composite_score(self, candidates_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate composite score for ranking candidates."""
        if candidates_df.empty:
            return pd.DataFrame()
        
        scored = candidates_df.copy()
        
        # Base score components
        scored['rating_score'] = (scored['rating'] / 5.0) * 30  # 30% weight
        scored['cost_score'] = self._calculate_cost_score(scored['cost_for_two'])  # 20% weight
        scored['location_relevance'] = 15  # 15% weight (all passed location filter)
        scored['soft_preference_score'] = scored.get('soft_score', 0)  # 20% weight
        
        # Randomness for variety (15% weight)
        scored['variety_score'] = np.random.uniform(5, 15, size=len(scored))
        
        # Calculate final composite score
        scored['composite_score'] = (
            scored['rating_score'] +
            scored['cost_score'] +
            scored['location_relevance'] +
            scored['soft_preference_score'] +
            scored['variety_score']
        )
        
        # Rank by composite score
        scored = scored.sort_values('composite_score', ascending=False)
        scored['rank'] = range(1, len(scored) + 1)
        
        return scored
    
    def _calculate_cost_score(self, costs: pd.Series) -> pd.Series:
        """Calculate cost preference score (lower is better up to a point)."""
        # Ideal cost range: 1000-2000 for two people
        ideal_min, ideal_max = 1000, 2000
        
        scores = []
        for cost in costs:
            if ideal_min <= cost <= ideal_max:
                scores.append(20)  # Perfect score
            elif cost < ideal_min:
                # Too cheap might indicate quality issues
                scores.append(10)
            else:
                # Too expensive
                over_budget = (cost - ideal_max) / ideal_max
                scores.append(max(0, 20 - (over_budget * 30)))
        
        return pd.Series(scores)

class RetrievalService:
    """Main service for retrieving and ranking restaurant candidates."""
    
    def __init__(self, restaurant_data: pd.DataFrame):
        self.restaurant_data = restaurant_data
        self.filter = RestaurantFilter(restaurant_data)
        self.scorer = CandidateScorer()
    
    def get_candidates(self, preferences: UserPreferences, limit: int = 10) -> List[Dict]:
        """Get top-N candidate restaurants for LLM ranking."""
        # Apply hard constraints
        constrained_candidates = self.filter.apply_hard_constraints(preferences)
        
        if constrained_candidates.empty:
            return []
        
        # Apply soft matching and scoring
        scored_candidates = self.filter.apply_soft_matching(preferences)
        
        # Calculate composite scores
        ranked_candidates = self.scorer.calculate_composite_score(scored_candidates)
        
        # Take top candidates
        top_candidates = ranked_candidates.head(limit)
        
        # Convert to list of dictionaries for LLM processing
        candidate_list = []
        for _, row in top_candidates.iterrows():
            candidate = {
                'name': row['name'],
                'location': row['location'],
                'cuisines': row['cuisines'],
                'rating': float(row['rating']),
                'cost_for_two': int(row['cost_for_two']),
                'address': row.get('address', ''),
                'composite_score': float(row['composite_score']),
                'rank': int(row['rank'])
            }
            candidate_list.append(candidate)
        
        return candidate_list
    
    def get_retrieval_stats(self, preferences: UserPreferences) -> Dict:
        """Get statistics about the retrieval process."""
        constrained_candidates = self.filter.apply_hard_constraints(preferences)
        
        return {
            'total_restaurants': len(self.restaurant_data),
            'after_hard_filters': len(constrained_candidates),
            'location': preferences.location,
            'budget': preferences.budget,
            'min_rating': preferences.rating,
            'cuisines': preferences.cuisines
        }

def main():
    """Demonstrate Phase 3 candidate retrieval functionality."""
    from phase1_data_preparation import DataPreprocessor
    
    # Load and process data
    processor = DataPreprocessor()
    data = processor.load_data()
    clean_data = processor.clean_data()
    
    # Initialize retrieval service
    retrieval_service = RetrievalService(clean_data)
    
    # Example preferences
    example_preferences = [
        UserPreferences(
            location="Bellandur",
            budget=2000,
            rating=4.0,
            cuisines=["Chinese", "Italian"]
        ),
        UserPreferences(
            location="Koramangala",
            budget=1500,
            rating=3.5,
            cuisines=["North Indian"],
            ambiance="Casual"
        )
    ]
    
    print("=== Phase 3: Candidate Retrieval Demo ===\n")
    
    for i, preferences in enumerate(example_preferences, 1):
        print(f"Example {i}: {preferences.dict()}")
        
        # Get candidates
        candidates = retrieval_service.get_candidates(preferences, limit=5)
        
        print(f"Retrieved {len(candidates)} candidates:")
        for candidate in candidates:
            print(f"  {candidate['rank']}. {candidate['name']} - Score: {candidate['composite_score']:.1f}")
        
        # Get stats
        stats = retrieval_service.get_retrieval_stats(preferences)
        print(f"Retrieval Stats: {stats}")
        
        print("-" * 50)

if __name__ == "__main__":
    main()
