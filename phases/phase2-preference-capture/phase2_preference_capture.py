"""
Phase 2: Preference Capture and Query Interface
Goal: Collect user preferences in a structured way and prepare query inputs.
"""

from typing import Dict, List, Optional, Union
from pydantic import BaseModel, validator
import re

class UserPreferences(BaseModel):
    """Structured user preference model for restaurant recommendations."""
    
    location: str
    budget: int
    rating: Optional[float] = None
    cuisines: Optional[List[str]] = None
    dietary_restrictions: Optional[List[str]] = None
    ambiance: Optional[str] = None
    meal_type: Optional[str] = None
    group_size: Optional[int] = None
    
    @validator('location')
    def validate_location(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Location must be at least 2 characters')
        return v.strip().title()
    
    @validator('budget')
    def validate_budget(cls, v):
        if v <= 0:
            raise ValueError('Budget must be positive')
        if v > 50000:
            raise ValueError('Budget seems too high (max ₹50,000)')
        return v
    
    @validator('rating')
    def validate_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Rating must be between 1 and 5')
        return v
    
    @validator('cuisines')
    def validate_cuisines(cls, v):
        if v is not None and len(v) > 10:
            raise ValueError('Too many cuisine preferences (max 10)')
        return v

class PreferenceParser:
    """Parses and validates user input into structured preferences."""
    
    def __init__(self):
        self.valid_locations = [
            'Bellandur', 'Koramangala', 'Indiranagar', 'HSR Layout',
            'Whitefield', 'Marathahalli', 'Electronic City', 'Manhattan'
        ]
        self.valid_cuisines = [
            'Chinese', 'Italian', 'Continental', 'North Indian', 'South Indian',
            'Thai', 'Mexican', 'American', 'Japanese', 'Korean', 'Sichuan'
        ]
        self.valid_ambiance = [
            'Casual', 'Fine Dining', 'Romantic', 'Family Friendly',
            'Trendy', 'Quiet', 'Lively', 'Outdoor Seating'
        ]
    
    def parse_text_input(self, text: str) -> UserPreferences:
        """Parse natural language text into structured preferences."""
        preferences = {}
        
        # Extract location
        location_match = re.search(r'(?:in|at|near)\s+([A-Za-z\s]+)', text, re.IGNORECASE)
        if location_match:
            preferences['location'] = location_match.group(1).strip()
        else:
            # Try to find any location names
            for location in self.valid_locations:
                if location.lower() in text.lower():
                    preferences['location'] = location
                    break
        
        # Extract budget
        budget_patterns = [
            r'(?:under|below|less than|max)\s*₹?(\d+)',
            r'₹?(\d+)\s*(?:or less|budget)',
            r'₹?(\d+)\s*(?:for two|per person)',
            r'budget\s*(?:of\s*)?₹?(\d+)'
        ]
        
        for pattern in budget_patterns:
            budget_match = re.search(pattern, text, re.IGNORECASE)
            if budget_match:
                preferences['budget'] = int(budget_match.group(1))
                break
        
        # Extract rating
        rating_match = re.search(r'(\d+\.?\d*)\s*stars?', text, re.IGNORECASE)
        if rating_match:
            rating = float(rating_match.group(1))
            if rating <= 5:
                preferences['rating'] = rating
        
        # Extract cuisines
        found_cuisines = []
        for cuisine in self.valid_cuisines:
            if cuisine.lower() in text.lower():
                found_cuisines.append(cuisine)
        
        if found_cuisines:
            preferences['cuisines'] = found_cuisines
        
        # Extract ambiance
        for ambiance in self.valid_ambiance:
            if ambiance.lower() in text.lower():
                preferences['ambiance'] = ambiance
                break
        
        # Extract meal type
        meal_types = ['breakfast', 'lunch', 'dinner', 'brunch', 'snacks']
        for meal_type in meal_types:
            if meal_type in text.lower():
                preferences['meal_type'] = meal_type.title()
                break
        
        # Extract group size
        group_match = re.search(r'(\d+)\s*(?:people|person|guest)', text, re.IGNORECASE)
        if group_match:
            preferences['group_size'] = int(group_match.group(1))
        
        return UserPreferences(**preferences)
    
    def validate_preferences(self, preferences: UserPreferences) -> Dict[str, Union[str, List[str]]]:
        """Validate preferences and return suggestions for missing/invalid data."""
        suggestions = []
        
        # Check location
        if preferences.location not in self.valid_locations:
            suggestions.append(f"Location '{preferences.location}' not found. Try: {', '.join(self.valid_locations[:5])}")
        
        # Check budget
        if preferences.budget < 200:
            suggestions.append("Budget seems low for restaurants. Consider increasing to at least ₹200")
        
        # Check rating
        if preferences.rating is None:
            suggestions.append("Consider adding a minimum rating (3+ recommended)")
        
        # Check cuisines
        if not preferences.cuisines:
            suggestions.append(f"Add cuisine preferences. Available: {', '.join(self.valid_cuisines[:5])}")
        
        return {
            'valid': len(suggestions) == 0,
            'suggestions': suggestions
        }

class QueryBuilder:
    """Builds structured queries from user preferences."""
    
    def __init__(self):
        pass
    
    def build_search_query(self, preferences: UserPreferences) -> Dict:
        """Build search query for restaurant database."""
        query = {
            'filters': {},
            'sort': [],
            'limit': 20
        }
        
        # Location filter
        query['filters']['location'] = preferences.location
        
        # Budget filter
        query['filters']['max_cost'] = preferences.budget
        
        # Rating filter
        if preferences.rating:
            query['filters']['min_rating'] = preferences.rating
        
        # Cuisine filter
        if preferences.cuisines:
            query['filters']['cuisines'] = preferences.cuisines
        
        # Sort preferences
        query['sort'] = [
            {'field': 'rating', 'order': 'desc'},
            {'field': 'cost_for_two', 'order': 'asc'}
        ]
        
        return query
    
    def build_recommendation_prompt(self, preferences: UserPreferences) -> str:
        """Build prompt for LLM recommendation generation."""
        prompt = f"""
        User Preferences:
        - Location: {preferences.location}
        - Budget: ₹{preferences.budget} for two people
        - Minimum Rating: {preferences.rating or 'Any'}
        - Preferred Cuisines: {', '.join(preferences.cuisines) if preferences.cuisines else 'Any'}
        - Ambiance: {preferences.ambiance or 'Any'}
        - Meal Type: {preferences.meal_type or 'Any'}
        - Group Size: {preferences.group_size or 2} people
        
        Please recommend restaurants that match these preferences and explain why each recommendation is suitable.
        """
        return prompt

def main():
    """Demonstrate Phase 2 preference capture functionality."""
    parser = PreferenceParser()
    query_builder = QueryBuilder()
    
    # Example user inputs
    example_inputs = [
        "I want Chinese food in Bellandur under ₹2000 for dinner, at least 4 stars",
        "Looking for Italian restaurants in Koramangala, budget ₹1500, good for date night",
        "Find me something spicy in Manhattan, budget around 2500, highly rated"
    ]
    
    print("=== Phase 2: Preference Capture Demo ===\n")
    
    for i, user_input in enumerate(example_inputs, 1):
        print(f"Example {i}: '{user_input}'")
        
        # Parse preferences
        try:
            preferences = parser.parse_text_input(user_input)
            print(f"Parsed Preferences: {preferences.dict()}")
            
            # Validate preferences
            validation = parser.validate_preferences(preferences)
            if not validation['valid']:
                print("Suggestions:")
                for suggestion in validation['suggestions']:
                    print(f"  - {suggestion}")
            else:
                print("✓ Preferences are valid")
            
            # Build search query
            search_query = query_builder.build_search_query(preferences)
            print(f"Search Query: {search_query}")
            
            print("-" * 50)
            
        except Exception as e:
            print(f"Error: {e}")
            print("-" * 50)

if __name__ == "__main__":
    main()
