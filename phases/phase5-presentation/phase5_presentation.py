"""
Phase 5: Presentation and User Experience
Goal: Display recommendation results clearly and help users decide quickly.
"""

import json
from typing import List, Dict, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass
import pandas as pd

@dataclass
class RecommendationCard:
    """Data structure for recommendation display cards."""
    rank: int
    restaurant_name: str
    location: str
    cuisines: str
    rating: float
    cost_for_two: int
    match_score: int
    ai_explanation: str
    key_highlights: List[str]
    practical_tips: str

class RecommendationRenderer:
    """Renders restaurant recommendations in various formats."""
    
    def __init__(self):
        self.card_template = """
<div class="recommendation-card" style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin: 16px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
    <div class="card-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <h3 class="restaurant-name" style="margin: 0; font-size: 1.2em; font-weight: bold; color: #333;">{rank}. {restaurant_name}</h3>
        <div class="match-badge" style="background: #4CAF50; color: white; padding: 4px 8px; border-radius: 12px; font-weight: bold; font-size: 0.9em;">{match_score}% Match</div>
    </div>
    
    <div class="card-body" style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 12px;">
        <div class="restaurant-info">
            <div class="info-row" style="margin-bottom: 8px;">
                <span class="label" style="font-weight: bold; color: #666;">Location:</span>
                <span class="value" style="color: #333;">{location}</span>
            </div>
            <div class="info-row" style="margin-bottom: 8px;">
                <span class="label" style="font-weight: bold; color: #666;">Cuisines:</span>
                <span class="value" style="color: #333;">{cuisines}</span>
            </div>
            <div class="info-row" style="margin-bottom: 8px;">
                <span class="label" style="font-weight: bold; color: #666;">Rating:</span>
                <span class="rating" style="color: #FFA500;">{'⭐' * int(rating)}</span>
                <span class="value" style="color: #333;">{rating}/5</span>
            </div>
            <div class="info-row" style="margin-bottom: 8px;">
                <span class="label" style="font-weight: bold; color: #666;">Cost:</span>
                <span class="value" style="color: #333;">₹{cost_for_two} for two</span>
            </div>
        </div>
        
        <div class="ai-insights" style="background: #f8f9fa; padding: 12px; border-radius: 6px; border-left: 4px solid #2196F3;">
            <h4 class="insights-title" style="margin: 0 0 8px 0; font-size: 1em; color: #2196F3;">Why we picked this</h4>
            <p class="explanation" style="margin: 0; line-height: 1.5; color: #333;">{ai_explanation}</p>
            
            <div class="highlights" style="margin-top: 12px;">
                <h5 class="highlights-title" style="margin: 0 0 8px 0; font-size: 0.9em; color: #666;">Key Highlights:</h5>
                <ul class="highlights-list" style="margin: 0; padding-left: 20px; color: #333;">
                    {highlights_html}
                </ul>
            </div>
            
            <div class="tips" style="margin-top: 12px; background: #fff3cd; padding: 8px; border-radius: 4px;">
                <h5 class="tips-title" style="margin: 0 0 4px 0; font-size: 0.9em; color: #856404;">💡 Practical Tips:</h5>
                <p class="tips-content" style="margin: 0; color: #333;">{practical_tips}</p>
            </div>
        </div>
    </div>
    
    <div class="card-actions" style="display: flex; gap: 12px; margin-top: 16px;">
        <button class="btn-primary" style="background: #2196F3; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: bold;">📅 Book Table</button>
        <button class="btn-secondary" style="background: #6C757D; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: bold;">📍 Get Directions</button>
        <button class="btn-outline" style="background: white; color: #2196F3; border: 2px solid #2196F3; padding: 8px 16px; border-radius: 6px; cursor: pointer;">❤️ Save</button>
    </div>
</div>
"""
    
    def render_card(self, recommendation: RecommendationCard) -> str:
        """Render a single recommendation card."""
        highlights_html = ""
        for highlight in recommendation.key_highlights:
            highlights_html += f"<li>{highlight}</li>"
        
        return self.card_template.format(
            rank=recommendation.rank,
            restaurant_name=recommendation.restaurant_name,
            location=recommendation.location,
            cuisines=recommendation.cuisines,
            rating=recommendation.rating,
            cost_for_two=recommendation.cost_for_two,
            match_score=recommendation.match_score,
            ai_explanation=recommendation.ai_explanation,
            highlights_html=highlights_html,
            practical_tips=recommendation.practical_tips
        )
    
    def render_comparison_table(self, recommendations: List[RecommendationCard]) -> str:
        """Render recommendations in comparison table format."""
        if not recommendations:
            return "<p>No recommendations available.</p>"
        
        table_html = """
<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
    <thead>
        <tr style="background: #f8f9fa; border-bottom: 2px solid #dee2e6;">
            <th style="padding: 12px; text-align: left; border: 1px solid #dee2e6;">Rank</th>
            <th style="padding: 12px; text-align: left; border: 1px solid #dee2e6;">Restaurant</th>
            <th style="padding: 12px; text-align: left; border: 1px solid #dee2e6;">Location</th>
            <th style="padding: 12px; text-align: left; border: 1px solid #dee2e6;">Rating</th>
            <th style="padding: 12px; text-align: left; border: 1px solid #dee2e6;">Cost</th>
            <th style="padding: 12px; text-align: left; border: 1px solid #dee2e6;">Match</th>
        </tr>
    </thead>
    <tbody>
        {table_rows}
    </tbody>
</table>
"""
        
        table_rows = ""
        for rec in recommendations:
            row_class = "even" if rec.rank % 2 == 0 else "odd"
            table_rows += f"""
<tr class="{row_class}" style="border-bottom: 1px solid #dee2e6;">
    <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">{rec.rank}</td>
    <td style="padding: 12px; border: 1px solid #dee2e6;">
        <div style="font-weight: bold; color: #333;">{rec.restaurant_name}</div>
        <div style="font-size: 0.9em; color: #666; margin-top: 4px;">{rec.cuisines}</div>
    </td>
    <td style="padding: 12px; border: 1px solid #dee2e6;">{rec.location}</td>
    <td style="padding: 12px; border: 1px solid #dee2e6;">
        <span style="color: #FFA500;">{'⭐' * int(rec.rating)}</span>
        <span style="margin-left: 4px;">{rec.rating}</span>
    </td>
    <td style="padding: 12px; border: 1px solid #dee2e6;">₹{rec.cost_for_two}</td>
    <td style="padding: 12px; border: 1px solid #dee2e6;">
        <div style="background: #4CAF50; color: white; padding: 4px 8px; border-radius: 12px; font-weight: bold; display: inline-block;">{rec.match_score}%</div>
    </td>
</tr>
"""
        
        return table_html.format(table_rows=table_rows)
    
    def render_summary_stats(self, recommendations: List[RecommendationCard]) -> str:
        """Render summary statistics for recommendations."""
        if not recommendations:
            return "<p>No recommendations to analyze.</p>"
        
        stats = {
            'total': len(recommendations),
            'avg_rating': sum(rec.rating for rec in recommendations) / len(recommendations),
            'avg_cost': sum(rec.cost_for_two for rec in recommendations) / len(recommendations),
            'avg_match_score': sum(rec.match_score for rec in recommendations) / len(recommendations),
            'cuisine_types': len(set(cuisine for rec in recommendations for cuisine in rec.cuisines.split(', '))),
            'price_range': f"₹{min(rec.cost_for_two for rec in recommendations)} - ₹{max(rec.cost_for_two for rec in recommendations)}"
        }
        
        stats_html = f"""
<div class="summary-stats" style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
    <h3 style="margin: 0 0 16px 0; color: #333;">📊 Recommendation Summary</h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
        <div class="stat-item" style="text-align: center;">
            <div class="stat-value" style="font-size: 2em; font-weight: bold; color: #2196F3;">{stats['total']}</div>
            <div class="stat-label" style="color: #666;">Total Restaurants</div>
        </div>
        <div class="stat-item" style="text-align: center;">
            <div class="stat-value" style="font-size: 2em; font-weight: bold; color: #FFA500;">{stats['avg_rating']:.1f}</div>
            <div class="stat-label" style="color: #666;">Average Rating</div>
        </div>
        <div class="stat-item" style="text-align: center;">
            <div class="stat-value" style="font-size: 2em; font-weight: bold; color: #4CAF50;">{stats['avg_match_score']:.0f}%</div>
            <div class="stat-label" style="color: #666;">Average Match Score</div>
        </div>
        <div class="stat-item" style="text-align: center;">
            <div class="stat-value" style="font-size: 2em; font-weight: bold; color: #FF5722;">₹{stats['avg_cost']:.0f}</div>
            <div class="stat-label" style="color: #666;">Average Cost</div>
        </div>
        <div class="stat-item" style="text-align: center;">
            <div class="stat-value" style="font-size: 2em; font-weight: bold; color: #9C27B0;">{stats['cuisine_types']}</div>
            <div class="stat-label" style="color: #666;">Cuisine Types</div>
        </div>
        <div class="stat-item" style="text-align: center;">
            <div class="stat-value" style="font-size: 1em; font-weight: bold; color: #673AB7;">{stats['price_range']}</div>
            <div class="stat-label" style="color: #666;">Price Range</div>
        </div>
    </div>
</div>
"""
        
        return stats_html

class VisualizationGenerator:
    """Generates visualizations for recommendation analysis."""
    
    def __init__(self):
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def create_match_score_chart(self, recommendations: List[RecommendationCard], save_path: str = "match_scores.png"):
        """Create bar chart of match scores."""
        if not recommendations:
            return
        
        names = [rec.restaurant_name[:15] for rec in recommendations]  # Truncate long names
        scores = [rec.match_score for rec in recommendations]
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(names, scores, color='#4CAF50', alpha=0.7)
        
        # Customize the chart
        plt.title('Restaurant Match Scores', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Restaurants', fontsize=12)
        plt.ylabel('Match Score (%)', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bar, score in zip(bars, scores):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{score}%', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Match score chart saved to {save_path}")
    
    def create_cost_rating_scatter(self, recommendations: List[RecommendationCard], save_path: str = "cost_rating.png"):
        """Create scatter plot of cost vs rating."""
        if not recommendations:
            return
        
        costs = [rec.cost_for_two for rec in recommendations]
        ratings = [rec.rating for rec in recommendations]
        names = [rec.restaurant_name[:10] for rec in recommendations]
        
        plt.figure(figsize=(10, 8))
        scatter = plt.scatter(costs, ratings, s=100, alpha=0.7, c='#2196F3')
        
        # Customize the chart
        plt.title('Cost vs Rating Analysis', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Cost for Two (₹)', fontsize=12)
        plt.ylabel('Rating', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Add restaurant labels
        for i, name in enumerate(names):
            plt.annotate(name, (costs[i], ratings[i]), 
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=9, alpha=0.8)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Cost vs rating chart saved to {save_path}")
    
    def create_cuisine_distribution(self, recommendations: List[RecommendationCard], save_path: str = "cuisine_dist.png"):
        """Create pie chart of cuisine distribution."""
        if not recommendations:
            return
        
        # Count cuisines
        cuisine_counts = {}
        for rec in recommendations:
            cuisines = [c.strip() for c in rec.cuisines.split(',')]
            for cuisine in cuisines:
                cuisine_counts[cuisine] = cuisine_counts.get(cuisine, 0) + 1
        
        if not cuisine_counts:
            return
        
        # Create pie chart
        plt.figure(figsize=(10, 8))
        colors = plt.cm.Set3(range(len(cuisine_counts)))
        wedges, texts, autotexts = plt.pie(
            cuisine_counts.values(),
            labels=cuisine_counts.keys(),
            autopct='%1.1f%%',
            colors=colors,
            startangle=90
        )
        
        plt.title('Cuisine Distribution', fontsize=16, fontweight='bold', pad=20)
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Cuisine distribution chart saved to {save_path}")

class PresentationService:
    """Main service for presenting restaurant recommendations."""
    
    def __init__(self):
        self.renderer = RecommendationRenderer()
        self.visualizer = VisualizationGenerator()
    
    def present_recommendations(self, recommendations_data: List[Dict], format: str = "cards") -> str:
        """Present recommendations in specified format."""
        
        # Convert to RecommendationCard objects
        recommendation_cards = []
        for rec_data in recommendations_data:
            card = RecommendationCard(
                rank=rec_data.get('rank', 1),
                restaurant_name=rec_data.get('restaurant', {}).get('name', 'Unknown'),
                location=rec_data.get('restaurant', {}).get('location', 'Unknown'),
                cuisines=rec_data.get('restaurant', {}).get('cuisines', 'Unknown'),
                rating=rec_data.get('restaurant', {}).get('rating', 0.0),
                cost_for_two=rec_data.get('restaurant', {}).get('cost_for_two', 0),
                match_score=rec_data.get('match_score', 0),
                ai_explanation=rec_data.get('ai_explanation', 'Great match for your preferences'),
                key_highlights=rec_data.get('key_highlights', []),
                practical_tips=rec_data.get('practical_tips', '')
            )
            recommendation_cards.append(card)
        
        # Generate presentation based on format
        if format == "cards":
            return self._generate_cards_html(recommendation_cards)
        elif format == "table":
            return self._generate_table_html(recommendation_cards)
        elif format == "summary":
            return self._generate_summary_html(recommendation_cards)
        else:
            return self._generate_cards_html(recommendation_cards)
    
    def _generate_cards_html(self, recommendations: List[RecommendationCard]) -> str:
        """Generate HTML for card layout."""
        if not recommendations:
            return "<p>No recommendations available.</p>"
        
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Restaurant Recommendations</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #333; margin: 0; }
        .recommendations { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }
        .summary { margin-bottom: 30px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🍽 Your Personalized Restaurant Recommendations</h1>
        </div>
        
        <div class="summary">
            {summary_stats}
        </div>
        
        <div class="recommendations">
            {recommendation_cards}
        </div>
    </div>
</body>
</html>
"""
        
        # Generate summary stats
        summary_html = self.renderer.render_summary_stats(recommendations)
        
        # Generate recommendation cards
        cards_html = ""
        for rec in recommendations:
            cards_html += self.renderer.render_card(rec)
        
        return html_content.format(
            summary_stats=summary_html,
            recommendation_cards=cards_html
        )
    
    def _generate_table_html(self, recommendations: List[RecommendationCard]) -> str:
        """Generate HTML for table layout."""
        if not recommendations:
            return "<p>No recommendations available.</p>"
        
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Restaurant Recommendations - Table View</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #333; margin: 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🍽 Restaurant Recommendations - Comparison Table</h1>
        </div>
        
        {comparison_table}
    </div>
</body>
</html>
"""
        
        # Generate comparison table
        table_html = self.renderer.render_comparison_table(recommendations)
        
        return html_content.format(comparison_table=table_html)
    
    def _generate_summary_html(self, recommendations: List[RecommendationCard]) -> str:
        """Generate HTML for summary view."""
        if not recommendations:
            return "<p>No recommendations available.</p>"
        
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Restaurant Recommendations - Summary</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #333; margin: 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🍽 Restaurant Recommendations - Summary</h1>
        </div>
        
        {summary_stats}
    </div>
</body>
</html>
"""
        
        # Generate summary stats
        summary_html = self.renderer.render_summary_stats(recommendations)
        
        return html_content.format(summary_stats=summary_html)
    
    def generate_visualizations(self, recommendations: List[RecommendationCard], output_dir: str = "visualizations"):
        """Generate visualizations for recommendations."""
        import os
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Generate various charts
        self.visualizer.create_match_score_chart(recommendations, f"{output_dir}/match_scores.png")
        self.visualizer.create_cost_rating_scatter(recommendations, f"{output_dir}/cost_rating.png")
        self.visualizer.create_cuisine_distribution(recommendations, f"{output_dir}/cuisine_dist.png")
        
        print(f"Visualizations generated in {output_dir} directory")

def main():
    """Demonstrate Phase 5 presentation functionality."""
    
    # Sample recommendation data (would come from Phase 4)
    sample_recommendations = [
        {
            'rank': 1,
            'restaurant': {
                'name': 'Málà Project - Manhattan',
                'location': 'Manhattan',
                'cuisines': 'Sichuan, Dry Pot',
                'rating': 4.8,
                'cost_for_two': 2500
            },
            'match_score': 95,
            'ai_explanation': 'Perfect match for spicy food lovers! This restaurant specializes in authentic Sichuan cuisine with numbing spices. The upscale ambiance matches your preference for fine dining, and they\'re known for exceptional service.',
            'key_highlights': ['Authentic Sichuan flavors', 'Upscale ambiance', 'Excellent service'],
            'practical_tips': 'Book in advance as this place gets busy. Try their signature dry pot dishes.'
        },
        {
            'rank': 2,
            'restaurant': {
                'name': 'Toit - Bellandur',
                'location': 'Bellandur',
                'cuisines': 'European, Asian',
                'rating': 4.5,
                'cost_for_two': 1500
            },
            'match_score': 88,
            'ai_explanation': 'Great choice for diverse tastes! Toit offers a unique fusion of European and Asian cuisines. The brewery atmosphere provides a casual yet sophisticated dining experience perfect for social gatherings.',
            'key_highlights': ['Fusion cuisine', 'Brewery on-site', 'Casual upscale'],
            'practical_tips': 'Try their craft beers and don\'t miss the rooftop seating on weekends.'
        },
        {
            'rank': 3,
            'restaurant': {
                'name': 'Cafe Thulp - Koramangala',
                'location': 'Koramangala',
                'cuisines': 'Continental, Italian',
                'rating': 4.0,
                'cost_for_two': 1200
            },
            'match_score': 82,
            'ai_explanation': 'Ideal for casual dining! This cafe offers comfort food at reasonable prices. The Italian options include excellent pasta dishes, and the continental menu has something for everyone.',
            'key_highlights': ['Budget-friendly', 'Comfort food', 'Good portions'],
            'practical_tips': 'Perfect for lunch or casual dinner. Their pasta dishes are highly recommended.'
        }
    ]
    
    print("=== Phase 5: Presentation Demo ===\n")
    
    # Initialize presentation service
    presentation_service = PresentationService()
    
    # Generate different presentation formats
    formats = ["cards", "table", "summary"]
    
    for format_type in formats:
        print(f"\nGenerating {format_type} presentation...")
        
        # Generate HTML presentation
        html_content = presentation_service.present_recommendations(sample_recommendations, format_type)
        
        # Save to file
        filename = f"recommendations_{format_type}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ {filename} generated successfully")
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    presentation_service.generate_visualizations([
        RecommendationCard(**{k: v for k, v in rec.items() if k != 'restaurant'} | 
                   {'restaurant': rec['restaurant']} for rec in sample_recommendations)
    ])
    
    print("\n✓ Phase 5 presentation demo completed!")
    print("Generated files:")
    print("  - recommendations_cards.html")
    print("  - recommendations_table.html") 
    print("  - recommendations_summary.html")
    print("  - visualizations/ directory with charts")

if __name__ == "__main__":
    main()
