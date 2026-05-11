"""
Phase 4: LLM Reasoning and Ranking
Goal: Generate personalized rankings and explainable recommendations.
"""

import json
import requests
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
from phase2_preference_capture import UserPreferences

load_dotenv()

class PromptConstructor:
    """Constructs prompts for LLM recommendation generation."""
    
    def __init__(self):
        self.base_prompt = """
You are an expert restaurant recommendation AI with deep knowledge of cuisines, dining experiences, and customer preferences.

Your task is to analyze the provided user preferences and restaurant candidates, then rank them with personalized explanations.

User Profile Analysis:
{user_preferences}

Restaurant Candidates:
{restaurant_candidates}

Please provide:
1. A ranked list of top 3-5 restaurants
2. Personalized explanation for each recommendation
3. Specific reasons why each restaurant matches the user's preferences
4. Practical details about what makes each choice special

Format your response as JSON:
{
    "recommendations": [
        {
            "rank": 1,
            "restaurant_name": "Restaurant Name",
            "explanation": "Detailed explanation of why this restaurant fits the user perfectly",
            "match_score": 95,
            "key_highlights": ["Highlight 1", "Highlight 2", "Highlight 3"],
            "practical_tips": "Specific advice for this restaurant"
        }
    ]
}

Focus on personalization, authenticity, and practical dining advice.
"""
    
    def build_ranking_prompt(self, preferences: UserPreferences, candidates: List[Dict]) -> str:
        """Build comprehensive prompt for LLM ranking."""
        
        # Format user preferences
        user_context = f"""
- Location: {preferences.location}
- Budget: ₹{preferences.budget} for two people
- Minimum Rating: {preferences.rating or 'No minimum'}
- Preferred Cuisines: {', '.join(preferences.cuisines) if preferences.cuisines else 'Any'}
- Dietary Restrictions: {preferences.dietary_restrictions or 'None'}
- Ambiance: {preferences.ambiance or 'Any'}
- Meal Type: {preferences.meal_type or 'Any'}
- Group Size: {preferences.group_size or 2} people
"""
        
        # Format restaurant candidates
        candidates_context = ""
        for i, candidate in enumerate(candidates, 1):
            candidates_context += f"""
{i}. {candidate['name']}
   - Location: {candidate['location']}
   - Cuisines: {candidate['cuisines']}
   - Rating: {candidate['rating']}/5
   - Cost: ₹{candidate['cost_for_two']} for two
   - Address: {candidate.get('address', 'N/A')}
   - Match Score: {candidate.get('composite_score', 0):.1f}
"""
        
        return self.base_prompt.format(
            user_preferences=user_context,
            restaurant_candidates=candidates_context
        )
    
    def build_refinement_prompt(self, preferences: UserPreferences, previous_recommendations: List[Dict], feedback: str) -> str:
        """Build prompt for refining recommendations based on user feedback."""
        
        refinement_prompt = f"""
The user provided feedback on previous recommendations:
User Feedback: "{feedback}"

Previous Recommendations:
{json.dumps(previous_recommendations, indent=2)}

User Preferences (unchanged):
- Location: {preferences.location}
- Budget: ₹{preferences.budget}
- Rating: {preferences.rating or 'Any'}
- Cuisines: {', '.join(preferences.cuisines) if preferences.cuisines else 'Any'}

Please provide 3 refined restaurant recommendations that better address the user's feedback.
Consider what they liked/disliked and adjust accordingly.

Format as JSON with the same structure as before.
"""
        
        return refinement_prompt

class GroqLLMService:
    """Service for interacting with Groq LLM API."""
    
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
    
    def generate_recommendations(self, prompt: str) -> Dict:
        """Generate restaurant recommendations using Groq LLM."""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert restaurant recommendation AI. Always respond in valid JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Parse JSON response
            # Remove markdown code blocks if present
            content = content.replace('```json', '').replace('```', '').strip()
            
            try:
                recommendations = json.loads(content)
                return recommendations
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                print(f"Raw content: {content}")
                return self._fallback_recommendations()
                
        except requests.exceptions.RequestException as e:
            print(f"API request error: {e}")
            return self._fallback_recommendations()
    
    def _fallback_recommendations(self) -> Dict:
        """Fallback recommendations when API fails."""
        return {
            "recommendations": [
                {
                    "rank": 1,
                    "restaurant_name": "Top Rated Restaurant",
                    "explanation": "This restaurant has excellent ratings and matches your preferences well.",
                    "match_score": 85,
                    "key_highlights": ["High ratings", "Good location", "Quality food"],
                    "practical_tips": "Book in advance for better seating"
                }
            ]
        }

class ResponseParser:
    """Parses and validates LLM responses."""
    
    def __init__(self):
        pass
    
    def parse_recommendations(self, llm_response: Dict, candidates: List[Dict]) -> List[Dict]:
        """Parse LLM response and match with candidate data."""
        
        if 'recommendations' not in llm_response:
            return self._create_fallback_recommendations(candidates)
        
        parsed_recommendations = []
        
        for rec in llm_response['recommendations']:
            # Find matching candidate data
            candidate_data = self._find_candidate_by_name(rec.get('restaurant_name', ''), candidates)
            
            if candidate_data:
                recommendation = {
                    'rank': rec.get('rank', len(parsed_recommendations) + 1),
                    'restaurant': {
                        'id': candidate_data.get('id', f"restaurant_{len(parsed_recommendations) + 1}"),
                        'name': rec.get('restaurant_name', candidate_data.get('name', 'Unknown')),
                        'location': candidate_data.get('location', 'Unknown'),
                        'cuisines': candidate_data.get('cuisines', 'Unknown'),
                        'rating': candidate_data.get('rating', 0.0),
                        'cost_for_two': candidate_data.get('cost_for_two', 0),
                        'address': candidate_data.get('address', '')
                    },
                    'ai_explanation': rec.get('explanation', 'Great match for your preferences'),
                    'match_score': rec.get('match_score', 80),
                    'key_highlights': rec.get('key_highlights', []),
                    'practical_tips': rec.get('practical_tips', ''),
                    'llm_rank': rec.get('rank', 1)
                }
                parsed_recommendations.append(recommendation)
            else:
                # Create recommendation from LLM data only
                recommendation = {
                    'rank': rec.get('rank', len(parsed_recommendations) + 1),
                    'restaurant': {
                        'id': f"llm_{len(parsed_recommendations) + 1}",
                        'name': rec.get('restaurant_name', 'Unknown'),
                        'location': 'Unknown',
                        'cuisines': 'Unknown',
                        'rating': 0.0,
                        'cost_for_two': 0,
                        'address': ''
                    },
                    'ai_explanation': rec.get('explanation', 'Great match for your preferences'),
                    'match_score': rec.get('match_score', 80),
                    'key_highlights': rec.get('key_highlights', []),
                    'practical_tips': rec.get('practical_tips', ''),
                    'llm_rank': rec.get('rank', 1)
                }
                parsed_recommendations.append(recommendation)
        
        return parsed_recommendations
    
    def _find_candidate_by_name(self, name: str, candidates: List[Dict]) -> Optional[Dict]:
        """Find candidate data by restaurant name."""
        if not name:
            return None
        
        # Try exact match first
        for candidate in candidates:
            if candidate['name'].lower() == name.lower():
                return candidate
        
        # Try partial match
        for candidate in candidates:
            if name.lower() in candidate['name'].lower() or candidate['name'].lower() in name.lower():
                return candidate
        
        return None
    
    def _create_fallback_recommendations(self, candidates: List[Dict]) -> List[Dict]:
        """Create fallback recommendations from candidate data."""
        if not candidates:
            return []
        
        fallback_recommendations = []
        for i, candidate in enumerate(candidates[:3], 1):
            recommendation = {
                'rank': i,
                'restaurant': candidate,
                'ai_explanation': f"Good option with {candidate['rating']} rating and {candidate['cuisines']} cuisine. Costs ₹{candidate['cost_for_two']} for two people.",
                'match_score': 75 + (5 - i) * 5,
                'key_highlights': [f"Rating: {candidate['rating']}", f"Cuisine: {candidate['cuisines']}"],
                'practical_tips': f"Located in {candidate['location']}",
                'llm_rank': i
            }
            fallback_recommendations.append(recommendation)
        
        return fallback_recommendations

class LLMRankingService:
    """Main service for LLM-powered restaurant ranking."""
    
    def __init__(self):
        self.prompt_constructor = PromptConstructor()
        self.llm_service = GroqLLMService()
        self.response_parser = ResponseParser()
    
    def rank_restaurants(self, preferences: UserPreferences, candidates: List[Dict]) -> List[Dict]:
        """Generate AI-powered rankings for restaurants."""
        
        if not candidates:
            return []
        
        # Build ranking prompt
        prompt = self.prompt_constructor.build_ranking_prompt(preferences, candidates)
        
        # Get LLM recommendations
        llm_response = self.llm_service.generate_recommendations(prompt)
        
        # Parse and validate response
        recommendations = self.response_parser.parse_recommendations(llm_response, candidates)
        
        return recommendations
    
    def refine_recommendations(self, preferences: UserPreferences, previous_recommendations: List[Dict], feedback: str) -> List[Dict]:
        """Refine recommendations based on user feedback."""
        
        # Build refinement prompt
        prompt = self.prompt_constructor.build_refinement_prompt(preferences, previous_recommendations, feedback)
        
        # Get refined recommendations
        llm_response = self.llm_service.generate_recommendations(prompt)
        
        # Parse response
        refined_recommendations = self.response_parser.parse_recommendations(llm_response, [])
        
        return refined_recommendations
    
    def get_ranking_stats(self, recommendations: List[Dict]) -> Dict:
        """Get statistics about the ranking process."""
        if not recommendations:
            return {}
        
        scores = [rec['match_score'] for rec in recommendations]
        ratings = [rec['restaurant']['rating'] for rec in recommendations]
        
        return {
            'total_recommendations': len(recommendations),
            'avg_match_score': sum(scores) / len(scores) if scores else 0,
            'highest_score': max(scores) if scores else 0,
            'lowest_score': min(scores) if scores else 0,
            'avg_rating': sum(ratings) / len(ratings) if ratings else 0,
            'cuisine_diversity': len(set(rec['restaurant']['cuisines'].split(', ') for rec in recommendations)),
            'llm_processing': True
        }

def main():
    """Demonstrate Phase 4 LLM ranking functionality."""
    from phase3_candidate_retrieval import RetrievalService
    from phase1_data_preparation import DataPreprocessor
    
    # Load and process data
    processor = DataPreprocessor()
    data = processor.load_data()
    clean_data = processor.clean_data()
    
    # Initialize services
    retrieval_service = RetrievalService(clean_data)
    ranking_service = LLMRankingService()
    
    # Example preferences
    preferences = UserPreferences(
        location="Bellandur",
        budget=2000,
        rating=4.0,
        cuisines=["Chinese", "Italian"],
        ambiance="Romantic"
    )
    
    print("=== Phase 4: LLM Ranking Demo ===\n")
    print(f"User Preferences: {preferences.dict()}")
    
    # Get candidates
    candidates = retrieval_service.get_candidates(preferences, limit=5)
    print(f"\nRetrieved {len(candidates)} candidates for ranking")
    
    # Generate AI rankings
    recommendations = ranking_service.rank_restaurants(preferences, candidates)
    
    print(f"\nGenerated {len(recommendations)} AI-powered recommendations:")
    for rec in recommendations:
        print(f"\nRank {rec['rank']}: {rec['restaurant']['name']}")
        print(f"  Match Score: {rec['match_score']}%")
        print(f"  Explanation: {rec['ai_explanation']}")
        print(f"  Highlights: {', '.join(rec['key_highlights'])}")
        print(f"  Tips: {rec['practical_tips']}")
    
    # Get stats
    stats = ranking_service.get_ranking_stats(recommendations)
    print(f"\nRanking Stats: {stats}")

if __name__ == "__main__":
    main()
