#!/usr/bin/env python3
"""
Phase 8: Streamlit Deployment and Interactive Dashboard
Interactive restaurant recommendation system with real-time analytics
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time
from typing import Dict, List, Any

# Import our existing systems
from working_complete_system import WorkingCompleteSystem
from phase7_working import Phase7WorkingSystem

# Page configuration
st.set_page_config(
    page_title="🍽️ Restaurant Recommendation System",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .recommendation-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 0.5rem 0;
    }
    .sidebar-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = f"user_{int(time.time())}"
if 'recommendations_history' not in st.session_state:
    st.session_state.recommendations_history = []
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = None

# Initialize systems
@st.cache_resource
def get_systems():
    """Initialize recommendation systems"""
    phase5_system = WorkingCompleteSystem()
    phase7_system = Phase7WorkingSystem()
    return phase5_system, phase7_system

phase5_system, phase7_system = get_systems()

def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">🍽️ AI Restaurant Recommendation System</h1>', unsafe_allow_html=True)
    
    # Sidebar for user controls
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.header("🎯 Recommendation Settings")
        
        # User preferences
        location = st.text_input("📍 Location", value="Bellandur", help="Enter your preferred location")
        budget = st.slider("💰 Budget (₹)", min_value=200, max_value=5000, value=2000, step=100)
        min_rating = st.slider("⭐ Min Rating", min_value=1.0, max_value=5.0, value=3.5, step=0.1)
        cuisine_preference = st.selectbox(
            "🍽️ Cuisine Preference",
            ["Any", "Italian", "Chinese", "Indian", "American", "Mexican", "Thai", "Japanese"]
        )
        top_n = st.slider("📊 Number of Recommendations", min_value=1, max_value=10, value=5)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # User profile section
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.header("👤 User Profile")
        
        user_name = st.text_input("Name", value="", help="Enter your name for personalization")
        
        if st.button("🔧 Create/Update Profile"):
            if user_name:
                preferences = {
                    'cuisines': [cuisine_preference] if cuisine_preference != "Any" else [],
                    'locations': [location],
                    'budget_range': (budget - 500, budget + 500),
                    'min_rating': min_rating
                }
                
                profile = phase7_system.create_profile(
                    user_id=st.session_state.user_id,
                    name=user_name,
                    preferences=preferences
                )
                
                st.session_state.user_profile = profile
                st.success(f"✅ Profile created for {user_name}!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # System info
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.header("📊 System Info")
        st.info(f"User ID: {st.session_state.user_id}")
        st.info(f"History: {len(st.session_state.recommendations_history)} requests")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Recommendations", "👤 Profile Analysis", "📈 Analytics", "⚙️ Settings"])
    
    with tab1:
        show_recommendations_tab(location, budget, min_rating, cuisine_preference, top_n)
    
    with tab2:
        show_profile_analysis_tab()
    
    with tab3:
        show_analytics_tab()
    
    with tab4:
        show_settings_tab()

def show_recommendations_tab(location, budget, min_rating, cuisine_preference, top_n):
    """Show recommendations tab"""
    
    st.subheader("🎯 Get Restaurant Recommendations")
    
    # Get recommendations button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Get Recommendations", type="primary", use_container_width=True):
            with st.spinner("🤖 AI is finding perfect restaurants for you..."):
                # Get recommendations
                result = phase5_system.get_recommendations(
                    location=location,
                    budget=budget,
                    min_rating=min_rating,
                    cuisine_preference=cuisine_preference.lower() if cuisine_preference != "Any" else "any",
                    top_n=top_n
                )
                
                # Store in session state
                st.session_state.last_recommendations = result
                st.session_state.recommendations_history.append({
                    'timestamp': datetime.now(),
                    'preferences': {
                        'location': location,
                        'budget': budget,
                        'min_rating': min_rating,
                        'cuisine_preference': cuisine_preference,
                        'top_n': top_n
                    },
                    'result': result
                })
                
                # Record interaction
                phase5_system.track_user_interaction(
                    user_id=st.session_state.user_id,
                    restaurant_name="recommendation_request",
                    interaction_type="search",
                    metadata={
                        'location': location,
                        'budget': budget,
                        'cuisine': cuisine_preference
                    }
                )
    
    # Show recommendations if available
    if 'last_recommendations' in st.session_state:
        result = st.session_state.last_recommendations
        
        if result.get('success'):
            st.success(f"✅ Found {len(result['recommendations'])} restaurants for {location}!")
            
            # Show recommendations in cards
            for i, rec in enumerate(result['recommendations'], 1):
                restaurant = rec['restaurant']
                
                with st.container():
                    st.markdown(f"""
                    <div class="recommendation-card">
                        <h3>🏆 {i}. {restaurant['name']}</h3>
                        <p><strong>🍽️ Cuisines:</strong> {restaurant['cuisines']}</p>
                        <p><strong>⭐ Rating:</strong> {restaurant['rating']}/5</p>
                        <p><strong>💰 Cost for Two:</strong> ₹{restaurant['cost']}</p>
                        <p><strong>📍 Location:</strong> {restaurant['location']}</p>
                        <p><strong>🤖 AI Explanation:</strong> {rec['ai_explanation']}</p>
                        <p><strong>🎯 Match Score:</strong> {rec['match_score']}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Action buttons
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        if st.button(f"👁️ View {i}", key=f"view_{i}"):
                            phase5_system.track_user_interaction(
                                user_id=st.session_state.user_id,
                                restaurant_name=restaurant['name'],
                                interaction_type="click",
                                metadata={'position': i}
                            )
                            st.success(f"👁️ Viewed {restaurant['name']}")
                    
                    with col2:
                        if st.button(f"❤️ Save {i}", key=f"save_{i}"):
                            phase5_system.track_user_interaction(
                                user_id=st.session_state.user_id,
                                restaurant_name=restaurant['name'],
                                interaction_type="save",
                                metadata={'position': i}
                            )
                            st.success(f"❤️ Saved {restaurant['name']}")
                    
                    with col3:
                        if st.button(f"📞 Book {i}", key=f"book_{i}"):
                            phase5_system.track_user_interaction(
                                user_id=st.session_state.user_id,
                                restaurant_name=restaurant['name'],
                                interaction_type="book",
                                metadata={'position': i}
                            )
                            st.success(f"📞 Booking {restaurant['name']}")
                    
                    with col4:
                        rating = st.slider(f"⭐ Rate {i}", 1, 5, 3, key=f"rating_{i}")
                        if st.button(f"📝 Submit Rating {i}", key=f"submit_{i}"):
                            phase5_system.track_user_interaction(
                                user_id=st.session_state.user_id,
                                restaurant_name=restaurant['name'],
                                interaction_type="feedback",
                                rating=rating,
                                metadata={'position': i}
                            )
                            st.success(f"⭐ Rated {restaurant['name']}: {rating}/5")
                    
                    st.divider()
        else:
            st.error(f"❌ {result.get('error', 'Unknown error occurred')}")
    
    # Show processing time if available
    if 'last_recommendations' in st.session_state and st.session_state.last_recommendations.get('success'):
        processing_time = st.session_state.last_recommendations.get('processing_time_ms', 0)
        st.info(f"⚡ Processing Time: {processing_time:.0f}ms")

def show_profile_analysis_tab():
    """Show user profile analysis tab"""
    
    st.subheader("👤 User Profile Analysis")
    
    if st.session_state.user_profile:
        profile = st.session_state.user_profile
        
        # Profile summary
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("User ID", profile.user_id)
            st.metric("Name", profile.name)
            st.metric("Interactions", len(profile.interaction_history))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Favorite Restaurants", len(profile.favorite_restaurants))
            st.metric("Avoided Restaurants", len(profile.avoided_restaurants))
            st.metric("Price Sensitivity", f"{profile.price_sensitivity:.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Preferences
        st.subheader("🎯 Preferences")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Preferred Cuisines:**")
            st.write(profile.preferred_cuisines if profile.preferred_cuisines else "None set")
            
            st.write("**Preferred Locations:**")
            st.write(profile.preferred_locations if profile.preferred_locations else "None set")
        
        with col2:
            st.write("**Budget Range:**")
            st.write(f"₹{profile.budget_range[0]} - ₹{profile.budget_range[1]}")
            
            st.write("**Min Rating Preference:**")
            st.write(f"{profile.min_rating_preference}/5")
        
        # Get personalized recommendations
        if st.button("🎯 Get Personalized Recommendations"):
            with st.spinner("🤖 Generating personalized recommendations..."):
                personalized_recs = phase7_system.get_personalized_recommendations(
                    user_id=st.session_state.user_id,
                    top_k=5
                )
                
                if personalized_recs.get('success'):
                    st.success("✅ Personalized recommendations generated!")
                    
                    for i, rec in enumerate(personalized_recs['recommendations'], 1):
                        restaurant = rec['restaurant']
                        personalization = rec['personalization_factors']
                        
                        with st.expander(f"{i}. {restaurant['name']} - Score: {rec['score']:.2f}"):
                            st.write(f"**Cuisines:** {restaurant['cuisines']}")
                            st.write(f"**Rating:** {restaurant['rating']}/5")
                            st.write(f"**Cost:** ₹{restaurant['cost']}")
                            st.write(f"**Location:** {restaurant['location']}")
                            st.write(f"**Personalization Score:** {rec['score']:.2f}")
                            st.write(f"**Cuisine Match:** {personalization['cuisine_match']}")
                            st.write(f"**Location Match:** {personalization['location_match']}")
                            st.write(f"**Budget Fit:** {personalization['budget_fit']}")
                else:
                    st.error("❌ Failed to generate personalized recommendations")
    else:
        st.info("👤 Please create a user profile in the sidebar to see personalized analysis.")

def show_analytics_tab():
    """Show analytics tab"""
    
    st.subheader("📈 System Analytics")
    
    # System performance
    dashboard = phase5_system.get_system_status()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("System Status", dashboard['status'])
        st.metric("Total Requests", dashboard['total_requests'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Success Rate", f"{dashboard['success_rate']:.1f}%")
        st.metric("Error Rate", f"{dashboard['error_rate']:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Avg Response Time", f"{dashboard['avg_processing_time_ms']:.0f}ms")
        st.metric("Uptime", dashboard['uptime_formatted'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Tokens", dashboard['total_tokens_used'])
        st.metric("Avg Tokens/Request", f"{dashboard['avg_token_usage']:.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Recommendation history chart
    if st.session_state.recommendations_history:
        st.subheader("📊 Recommendation History")
        
        # Create dataframe for visualization
        history_data = []
        for entry in st.session_state.recommendations_history:
            history_data.append({
                'timestamp': entry['timestamp'],
                'location': entry['preferences']['location'],
                'budget': entry['preferences']['budget'],
                'cuisine': entry['preferences']['cuisine_preference'],
                'success': entry['result'].get('success', False),
                'num_recommendations': len(entry['result'].get('recommendations', []))
            })
        
        df = pd.DataFrame(history_data)
        
        # Timeline chart
        fig = px.line(
            df, x='timestamp', y='num_recommendations',
            title="Recommendations Over Time",
            labels={'timestamp': 'Time', 'num_recommendations': 'Number of Recommendations'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Success rate chart
        success_df = df.groupby('timestamp')['success'].mean().reset_index()
        fig2 = px.line(
            success_df, x='timestamp', y='success',
            title="Success Rate Over Time",
            labels={'timestamp': 'Time', 'success': 'Success Rate'}
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Location distribution
        location_counts = df['location'].value_counts()
        fig3 = px.pie(
            values=location_counts.values,
            names=location_counts.index,
            title="Recommendations by Location"
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("📊 No recommendation history available yet.")

def show_settings_tab():
    """Show settings tab"""
    
    st.subheader("⚙️ System Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**System Information**")
        st.info("🍽️ Restaurant Recommendation System")
        st.info("📊 Phases 1-8 Complete")
        st.info("🤖 AI-Powered with Personalization")
        st.info("📈 Real-time Analytics")
        
        st.write("**Performance Settings**")
        cache_timeout = st.slider("Cache Timeout (seconds)", 60, 3600, 300)
        max_recommendations = st.slider("Max Recommendations", 1, 20, 10)
        
        if st.button("🔄 Clear Cache"):
            st.cache_resource.clear()
            st.success("✅ Cache cleared!")
    
    with col2:
        st.write("**Export Options**")
        
        if st.button("📥 Export Recommendations History"):
            if st.session_state.recommendations_history:
                # Convert to CSV
                history_data = []
                for entry in st.session_state.recommendations_history:
                    history_data.append({
                        'timestamp': entry['timestamp'].isoformat(),
                        'location': entry['preferences']['location'],
                        'budget': entry['preferences']['budget'],
                        'cuisine_preference': entry['preferences']['cuisine_preference'],
                        'min_rating': entry['preferences']['min_rating'],
                        'success': entry['result'].get('success', False),
                        'num_recommendations': len(entry['result'].get('recommendations', []))
                    })
                
                df = pd.DataFrame(history_data)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"recommendations_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("⚠️ No history to export")
        
        if st.button("🔄 Reset Session"):
            st.session_state.clear()
            st.session_state.user_id = f"user_{int(time.time())}"
            st.session_state.recommendations_history = []
            st.session_state.user_profile = None
            st.success("✅ Session reset!")
            st.rerun()
        
        st.write("**About**")
        st.info("This is a complete restaurant recommendation system with AI-powered personalization, real-time analytics, and interactive dashboard.")
        st.info("Built with Streamlit, Flask, and Machine Learning.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🍽️ Restaurant Recommendation System | Phases 1-8 Complete | 🤖 AI-Powered | 📈 Real-time Analytics</p>
    <p>Built with ❤️ using Streamlit, Flask, and Machine Learning</p>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
