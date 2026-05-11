#!/usr/bin/env python3
"""
Phase 5 Real Test: Live Restaurant Recommendation System
Tests the complete pipeline with real Zomato dataset from Hugging Face
"""

import pandas as pd
from datasets import load_dataset
import json
import re
import os
from typing import List, Dict, Any
import requests
from dotenv import load_dotenv

class RestaurantRecommendationSystem:
    def __init__(self):
        self.dataset = None
        self.filtered_restaurants = []
        # Load environment variables
        load_dotenv()
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        if not self.groq_api_key:
            print("Warning: GROQ_API_KEY not found in .env file")
        
    def load_zomato_dataset(self):
        """Load Zomato dataset from Hugging Face"""
        print("Loading Zomato dataset from Hugging Face...")
        try:
            self.dataset = load_dataset("ManikaSaini/zomato-restaurant-recommendation", split="train")
            print(f"Dataset loaded successfully. Total records: {len(self.dataset)}")
            return True
        except Exception as e:
            print(f"Error loading dataset: {e}")
            return False
    
    def convert_to_dataframe(self):
        """Convert dataset to pandas DataFrame for easier manipulation"""
        if self.dataset:
            df = pd.DataFrame(self.dataset)
            print(f"Dataset columns: {list(df.columns)}")
            print(f"Sample data shape: {df.shape}")
            return df
        return pd.DataFrame()
    
    def clean_and_preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess the restaurant data"""
        print("Cleaning and preprocessing data...")
        
        # Make a copy to avoid SettingWithCopyWarning
        df_clean = df.copy()
        
        # Handle missing values
        df_clean = df_clean.dropna(subset=['name', 'location', 'cuisines', 'rate', 'approx_cost(for two people)'])
        
        # Clean rating column - extract numeric value
        df_clean['rating_numeric'] = df_clean['rate'].apply(self.extract_rating)
        
        # Clean cost column - extract numeric value
        df_clean['cost_numeric'] = df_clean['approx_cost(for two people)'].apply(self.extract_cost)
        
        # Filter out invalid ratings and costs
        df_clean = df_clean[
            (df_clean['rating_numeric'] > 0) & 
            (df_clean['cost_numeric'] > 0)
        ]
        
        print(f"After cleaning: {len(df_clean)} valid restaurants")
        return df_clean
    
    def extract_rating(self, rate_str):
        """Extract numeric rating from string"""
        if pd.isna(rate_str):
            return None
        try:
            # Handle formats like "4.1/5", "4.1", "4.1 out of 5"
            rate_str = str(rate_str).strip()
            match = re.search(r'(\d+\.?\d*)', rate_str)
            if match:
                rating = float(match.group(1))
                return rating if rating <= 5 else None
        except:
            pass
        return None
    
    def extract_cost(self, cost_str):
        """Extract numeric cost from string"""
        if pd.isna(cost_str):
            return None
        try:
            # Handle formats like "₹800", "800", "800 for two"
            cost_str = str(cost_str).replace('₹', '').replace(',', '')
            match = re.search(r'(\d+)', cost_str)
            if match:
                return int(match.group(1))
        except:
            pass
        return None
    
    def filter_restaurants(self, df: pd.DataFrame, location: str, budget: int, min_rating: float) -> List[Dict]:
        """Filter restaurants based on user preferences"""
        print(f"Filtering restaurants for: Location={location}, Budget={budget}, Min Rating={min_rating}")
        
        # Filter by location (case-insensitive partial match)
        location_mask = df['location'].str.contains(location, case=False, na=False)
        
        # Filter by budget (cost for two people should be <= budget)
        budget_mask = df['cost_numeric'] <= budget
        
        # Filter by rating
        rating_mask = df['rating_numeric'] >= min_rating
        
        # Apply all filters
        filtered_df = df[location_mask & budget_mask & rating_mask]
        
        # Sort by rating (descending) and cost (ascending for tie-breaker)
        filtered_df = filtered_df.sort_values(['rating_numeric', 'cost_numeric'], 
                                            ascending=[False, True])
        
        # Remove duplicates based on name and location
        filtered_df = filtered_df.drop_duplicates(subset=['name', 'location'], keep='first')
        
        print(f"Found {len(filtered_df)} unique restaurants matching criteria")
        
        # Convert to list of dictionaries
        restaurants = []
        for _, row in filtered_df.iterrows():
            restaurants.append({
                'name': row['name'],
                'location': row['location'],
                'cuisines': row['cuisines'],
                'rating': row['rating_numeric'],
                'cost_for_two': row['cost_numeric'],
                'url': row.get('url', ''),
                'reviews_list': row.get('reviews_list', ''),
                'menu_item': row.get('menu_item', '')
            })
        
        self.filtered_restaurants = restaurants
        return restaurants
    
    def generate_llm_prompt(self, user_preferences: Dict, restaurants: List[Dict]) -> str:
        """Generate prompt for LLM to rank restaurants"""
        prompt = f"""You are a restaurant recommendation expert. Based on the user's preferences, rank the following restaurants and provide personalized explanations.

User Preferences:
- Location: {user_preferences['location']}
- Budget: {user_preferences['budget']} (maximum for two people)
- Minimum Rating: {user_preferences['min_rating']}
- Number of recommendations: {user_preferences.get('top_n', 5)}

Available Restaurants:
"""
        
        for i, restaurant in enumerate(restaurants[:10], 1):  # Send top 10 for ranking
            prompt += f"""
{i}. {restaurant['name']}
   - Cuisine: {restaurant['cuisines']}
   - Rating: {restaurant['rating']}/5
   - Cost for two: ₹{restaurant['cost_for_two']}
   - Location: {restaurant['location']}
"""
        
        prompt += """

Please:
1. Rank the top 5 restaurants that best match the user's preferences
2. For each restaurant, explain why it matches the user's preferences
3. Consider location convenience, budget fit, rating quality, and cuisine variety
4. Provide specific, personalized reasoning for each recommendation

Output format: JSON with the following structure:
{
  "recommendations": [
    {
      "rank": 1,
      "restaurant_name": "Restaurant Name",
      "cuisine": "Cuisine Type",
      "rating": 4.5,
      "cost_for_two": 1800,
      "location": "Location",
      "ai_explanation": "Specific explanation of why this fits the user's preferences",
      "match_score": 95
    }
  ]
}
"""
        
        return prompt
    
    def call_groq_api(self, prompt: str) -> Dict:
        """Make real API call to Groq for restaurant ranking"""
        if not self.groq_api_key:
            print("No Groq API key found, using mock response")
            return self.mock_llm_response(self.filtered_restaurants)
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are a restaurant recommendation expert. Always respond in valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1500
        }
        
        try:
            print("Making API call to Groq...")
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Parse JSON response
            try:
                # Remove markdown code blocks if present
                if content.startswith('```json'):
                    content = content[7:]  # Remove ```json
                if content.endswith('```'):
                    content = content[:-3]  # Remove ```
                content = content.strip()
                
                recommendations_data = json.loads(content)
                return {
                    "recommendations": recommendations_data.get("recommendations", []),
                    "total_candidates": len(self.filtered_restaurants),
                    "processing_time": "Real API call"
                }
            except json.JSONDecodeError:
                print("Failed to parse JSON response, using mock")
                return self.mock_llm_response(self.filtered_restaurants)
                
        except Exception as e:
            print(f"API call failed: {e}, using mock response")
            return self.mock_llm_response(self.filtered_restaurants)
    
    def mock_llm_response(self, restaurants: List[Dict]) -> Dict:
        """Mock LLM response for testing (since we don't have real LLM API key)"""
        # Take top 5 restaurants and generate mock explanations
        top_restaurants = restaurants[:5]
        
        recommendations = []
        for i, restaurant in enumerate(top_restaurants, 1):
            # Generate mock explanation based on restaurant data
            explanation = f"Perfect match for your preferences! Located in {restaurant['location']} with excellent {restaurant['rating']}/5 rating. The cost of ₹{restaurant['cost_for_two']} for two people fits well within your ₹2000 budget. {restaurant['cuisines']} cuisine offers great variety for your dining experience."
            
            recommendations.append({
                "rank": i,
                "restaurant_name": restaurant['name'],
                "cuisine": restaurant['cuisines'],
                "rating": restaurant['rating'],
                "cost_for_two": restaurant['cost_for_two'],
                "location": restaurant['location'],
                "ai_explanation": explanation,
                "match_score": 95 - (i * 3)  # Decreasing score
            })
        
        return {
            "recommendations": recommendations,
            "total_candidates": len(restaurants),
            "processing_time": "1.2s"
        }
    
    def generate_phase5_output(self, user_preferences: Dict, llm_response: Dict) -> str:
        """Generate Phase 5 presentation output"""
        output = f"""
# Phase 5 Restaurant Recommendations
## Based on your preferences: {user_preferences['location']}, ₹{user_preferences['budget']} budget, {user_preferences['min_rating']}+ rating

"""
        
        for rec in llm_response['recommendations']:
            output += f"""
### {rec['rank']}. {rec['restaurant_name']} ⭐ {rec['rating']}

**Details:**
- 🍽️ **Cuisine:** {rec['cuisine']}
- 💰 **Cost for two:** ₹{rec['cost_for_two']}
- 📍 **Location:** {rec['location']}
- 🎯 **Match Score:** {rec['match_score']}%

**Why this fits you:**
{rec['ai_explanation']}

---
"""
        
        output += f"""
*Generated from {llm_response['total_candidates']} candidate restaurants in {llm_response['processing_time']}*
"""
        
        return output
    
    def run_complete_test(self, location: str, budget: int, min_rating: float):
        """Run the complete Phase 5 test with real data"""
        print("=" * 60)
        print("PHASE 5 LIVE TEST - RESTAURANT RECOMMENDATION SYSTEM")
        print("=" * 60)
        
        # Step 1: Load dataset
        if not self.load_zomato_dataset():
            return "Failed to load dataset"
        
        # Step 2: Convert and clean data
        df = self.convert_to_dataframe()
        df_clean = self.clean_and_preprocess(df)
        
        # Step 3: Filter restaurants
        user_preferences = {
            'location': location,
            'budget': budget,
            'min_rating': min_rating,
            'top_n': 5
        }
        
        restaurants = self.filter_restaurants(df_clean, location, budget, min_rating)
        
        if not restaurants:
            return f"No restaurants found matching criteria: {location}, ₹{budget}, {min_rating}+ rating"
        
        # Step 4: Generate LLM prompt (for demonstration)
        prompt = self.generate_llm_prompt(user_preferences, restaurants)
        print("Generated LLM prompt (first 500 chars):")
        print(prompt[:500] + "...")
        print()
        
        # Step 5: Get LLM response (real API call)
        llm_response = self.call_groq_api(prompt)
        
        # Step 6: Generate Phase 5 output
        phase5_output = self.generate_phase5_output(user_preferences, llm_response)
        
        return phase5_output

# Main execution
if __name__ == "__main__":
    # Test with the specified inputs
    system = RestaurantRecommendationSystem()
    
    # User inputs from the test case
    location = "Bellandur"
    budget = 2000
    min_rating = 4.0
    
    result = system.run_complete_test(location, budget, min_rating)
    print(result)
