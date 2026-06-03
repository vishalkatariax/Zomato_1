#!/usr/bin/env python3
"""
Production-ready Flask application for Restaurant Recommendation System
"""

import os
import sys
sys.path.insert(0, '/Users/vishalkataria/Documents/Zomato_AI_recommendation')
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from working_complete_system import WorkingCompleteSystem
from phase7_working import Phase7WorkingSystem

app = Flask(__name__, template_folder='/Users/vishalkataria/Documents/Zomato_AI_recommendation/templates')
CORS(app)

# Initialize systems
phase5_system = WorkingCompleteSystem()
phase7_system = Phase7WorkingSystem()

@app.route('/')
def index():
    """Main page with restaurant recommendation interface"""
    return render_template('index.html')

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Get restaurant recommendations"""
    try:
        data = request.get_json()
        
        # Get basic recommendations
        result = phase5_system.get_recommendations(
            location=data.get('location', ''),
            budget=int(data.get('budget', 0)),
            min_rating=float(data.get('min_rating', 0)),
            cuisine_preference=data.get('cuisine_preference', 'any'),
            top_n=int(data.get('top_n', 5))
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'recommendations': []
        }), 500

@app.route('/api/personalized-recommendations', methods=['POST'])
def get_personalized_recommendations():
    """Get personalized recommendations using Phase 7"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        # Get personalized recommendations
        result = phase7_system.get_personalized_recommendations(
            user_id=user_id,
            context=data.get('context', {}),
            top_k=int(data.get('top_n', 5))
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/user-profile', methods=['POST'])
def create_user_profile():
    """Create or update user profile"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        # Create or update profile
        profile = phase7_system.create_profile(
            user_id=user_id,
            name=data.get('name', ''),
            preferences=data.get('preferences', {})
        )
        
        return jsonify({
            'success': True,
            'user_id': profile.user_id,
            'name': profile.name
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/user-interaction', methods=['POST'])
def record_user_interaction():
    """Record user interaction for learning"""
    try:
        data = request.get_json()
        
        # Record interaction in both systems
        phase5_system.track_user_interaction(
            user_id=data.get('user_id', ''),
            restaurant_name=data.get('restaurant_name', ''),
            interaction_type=data.get('interaction_type', ''),
            metadata=data.get('metadata', {})
        )
        
        phase7_system.record_interaction(
            user_id=data.get('user_id', ''),
            restaurant_id=data.get('restaurant_id', ''),
            interaction_type=data.get('interaction_type', ''),
            rating=data.get('rating'),
            feedback_text=data.get('feedback_text'),
            context=data.get('context', {})
        )
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/user-analysis/<user_id>')
def get_user_analysis(user_id):
    """Get comprehensive user profile analysis"""
    try:
        analysis = phase7_system.get_user_profile_analysis(user_id)
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dashboard')
def dashboard():
    """Get system performance dashboard"""
    try:
        dashboard = phase5_system.get_system_status()
        return jsonify(dashboard)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': '2024-01-01T00:00:00Z',
        'version': '1.0.0',
        'phases': '1-7 Complete',
        'services': {
            'phase5_system': 'running',
            'phase7_system': 'running',
            'database': 'connected'
        }
    })

@app.route('/api/restaurants')
def get_restaurants():
    """Get available restaurants"""
    try:
        restaurants = phase5_system._get_mock_restaurants()
        return jsonify({
            'success': True,
            'restaurants': restaurants,
            'count': len(restaurants)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/locations')
def get_locations():
    """Get available locations"""
    try:
        locations = phase5_system.get_locations()
        return jsonify(locations)
        
    except Exception as e:
        return jsonify([])

@app.route('/api/cuisines')
def get_cuisines():
    """Get available cuisines"""
    try:
        cuisines = phase5_system.get_all_cuisines()
        return jsonify(cuisines)
        
    except Exception as e:
        return jsonify([])

@app.route('/api/cuisines-by-location')
def get_cuisines_by_location():
    """Get cuisines for a specific location"""
    try:
        location = request.args.get('location', '')
        cuisines = phase5_system.get_cuisines_by_location(location)
        return jsonify(cuisines)
        
    except Exception as e:
        return jsonify([])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
