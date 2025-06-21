"""
Streamlit Frontend for Movie Continuation System
Beautiful UI for generating viral movie reels
"""

import streamlit as st
import requests
import time
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List

# Configure Streamlit page
st.set_page_config(
    page_title="AI Movie Reels Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF6B6B;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #4ECDC4;
        margin-bottom: 1rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
    }
    .demo-mode {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Demo mode configuration
DEMO_MODE = True
API_BASE_URL = "http://localhost:8000" if not DEMO_MODE else None

def get_demo_status():
    """Get demo system status"""
    return {
        "status": "running",
        "agents": {
            "trend_agent": "healthy",
            "movie_agent": "healthy", 
            "script_agent": "healthy",
            "voice_agent": "healthy",
            "video_agent": "healthy",
            "upload_agent": "healthy"
        },
        "processing_tasks": 0,
        "cached_results": 3,
        "timestamp": datetime.now().isoformat()
    }

def get_demo_trending_movies():
    """Get demo trending movies"""
    return [
        {"title": "Inception", "source": "imdb", "trending_score": 9.2},
        {"title": "The Dark Knight", "source": "youtube", "trending_score": 8.9},
        {"title": "Avengers: Endgame", "source": "reddit", "trending_score": 8.7},
        {"title": "Interstellar", "source": "imdb", "trending_score": 8.5},
        {"title": "The Matrix", "source": "youtube", "trending_score": 8.3}
    ]

def get_demo_results(movie_title: str):
    """Get demo processing results"""
    return {
        "movie_title": movie_title,
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "trend_data": {
            "popularity_score": 8.7,
            "social_mentions": 15420,
            "review_count": 8920,
            "average_rating": 4.2,
            "viral_potential_score": 0.85,
            "fan_desires": [
                "More dream sequences",
                "Cobb's backstory revealed",
                "Mal's character development",
                "The ending explained",
                "Team reunion"
            ]
        },
        "script_data": {
            "total_parts": 5,
            "target_duration": 60,
            "viral_potential": 0.88,
            "parts": [
                {"part_num": 1, "structure": "Intro", "text": "Cobb wakes up in a new dream level..."},
                {"part_num": 2, "structure": "Conflict", "text": "The team discovers a new threat..."},
                {"part_num": 3, "structure": "Development", "text": "Mal appears with a warning..."},
                {"part_num": 4, "structure": "Climax", "text": "The final confrontation begins..."},
                {"part_num": 5, "structure": "Resolution", "text": "Cobb finally finds his way home..."}
            ]
        },
        "video_data": {
            "video_files": ["reel_1.mp4", "reel_2.mp4", "reel_3.mp4", "reel_4.mp4", "reel_5.mp4"],
            "total_duration": 60.0,
            "file_size": 25000000,
            "resolution": "1080x1920"
        },
        "upload_results": [
            {
                "platform": "YouTube Shorts",
                "status": "success",
                "url": "https://youtube.com/shorts/demo123",
                "analytics": {"views": 1250, "likes": 89}
            },
            {
                "platform": "Instagram Reels", 
                "status": "success",
                "url": "https://instagram.com/reel/demo456",
                "analytics": {"views": 890, "likes": 67}
            }
        ]
    }

def check_backend_status():
    """Check if the backend is running"""
    if DEMO_MODE:
        return True
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_system_status():
    """Get system status from backend"""
    if DEMO_MODE:
        return get_demo_status()
    try:
        response = requests.get(f"{API_BASE_URL}/status", timeout=10)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def get_trending_movies():
    """Get trending movies from backend"""
    if DEMO_MODE:
        return get_demo_trending_movies()
    try:
        response = requests.get(f"{API_BASE_URL}/trending-movies", timeout=10)
        return response.json() if response.status_code == 200 else []
    except:
        return []

def process_movie(movie_title: str):
    """Start movie processing"""
    if DEMO_MODE:
        # Simulate processing delay
        time.sleep(2)
        return {
            "message": f"Started processing movie: {movie_title}",
            "movie_title": movie_title,
            "status": "processing"
        }
    try:
        response = requests.post(
            f"{API_BASE_URL}/process-movie",
            params={"movie_title": movie_title},
            timeout=30
        )
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Error processing movie: {str(e)}")
        return None

def get_results(movie_title: str):
    """Get processing results for a movie"""
    if DEMO_MODE:
        return get_demo_results(movie_title)
    try:
        response = requests.get(f"{API_BASE_URL}/results/{movie_title}", timeout=10)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def auto_trend_analysis():
    """Start automatic trend analysis"""
    if DEMO_MODE:
        time.sleep(1)
        return {
            "status": "completed",
            "selected_movie": {"title": "Inception", "trending_score": 9.2},
            "processing_result": get_demo_results("Inception")
        }
    try:
        response = requests.post(f"{API_BASE_URL}/auto-trend-analysis", timeout=30)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Error in auto trend analysis: {str(e)}")
        return None

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🎬 AI Movie Reels Generator</h1>', unsafe_allow_html=True)
    st.markdown("### Generate viral movie continuation content with AI")
    
    # Demo mode indicator
    if DEMO_MODE:
        st.markdown("""
        <div class="demo-mode">
            🎭 <strong>DEMO MODE</strong> - This is a preview with simulated data. 
            Add API keys to enable full functionality.
        </div>
        """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🎯 Quick Actions")
        
        # Backend status
        if check_backend_status():
            st.success("✅ Backend Connected")
        else:
            if DEMO_MODE:
                st.info("🎭 Demo Mode Active")
            else:
                st.error("❌ Backend Disconnected")
                st.info("Please start the backend server first")
                return
        
        # System status
        status = get_system_status()
        if status:
            st.subheader("System Status")
            st.metric("Agents Active", len([a for a in status.get('agents', {}).values() if a == 'healthy']))
            st.metric("Cached Results", status.get('cached_results', 0))
        
        # Auto trend analysis
        if st.button("🚀 Auto Trend Analysis", use_container_width=True):
            with st.spinner("Analyzing trending movies..."):
                result = auto_trend_analysis()
                if result:
                    st.success("Auto analysis completed!")
                    st.json(result)
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎭 Generate Movie Reels")
        
        # Movie input
        movie_title = st.text_input(
            "Enter a movie title:",
            placeholder="e.g., Inception, The Dark Knight, Avengers: Endgame"
        )
        
        # Trending movies suggestion
        trending = get_trending_movies()
        if trending:
            st.info("🔥 Trending movies:")
            for i, movie in enumerate(trending[:5]):
                if st.button(f"📽️ {movie.get('title', 'Unknown')}", key=f"trend_{i}"):
                    movie_title = movie.get('title', '')
                    st.session_state.movie_title = movie_title
        
        # Process button
        if st.button("🎬 Generate Reels", type="primary", use_container_width=True):
            if movie_title:
                with st.spinner("Processing movie..."):
                    result = process_movie(movie_title)
                    if result:
                        st.session_state.processing_movie = movie_title
                        st.session_state.processing_started = datetime.now()
                        st.success(f"Started processing: {movie_title}")
                        if DEMO_MODE:
                            st.info("🎭 Demo: Simulated processing completed!")
                        st.json(result)
            else:
                st.error("Please enter a movie title")
    
    with col2:
        st.subheader("📊 Quick Stats")
        
        # Display metrics
        if status:
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Processing Tasks", status.get('processing_tasks', 0))
            with col_b:
                st.metric("System Uptime", "Running")
        
        # Recent activity
        st.subheader("🕒 Recent Activity")
        if 'processing_movie' in st.session_state:
            st.info(f"Processing: {st.session_state.processing_movie}")
    
    # Results section
    if 'processing_movie' in st.session_state:
        st.markdown("---")
        st.subheader("📈 Processing Results")
        
        # Poll for results
        results = get_results(st.session_state.processing_movie)
        
        if results:
            if results.get('status') == 'completed':
                st.markdown('<div class="status-box success-box">✅ Processing Completed!</div>', unsafe_allow_html=True)
                
                # Display results
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.subheader("📊 Trend Analysis")
                    trend_data = results.get('trend_data', {})
                    if trend_data:
                        st.metric("Popularity Score", f"{trend_data.get('popularity_score', 0):.2f}")
                        st.metric("Social Mentions", trend_data.get('social_mentions', 0))
                        st.metric("Viral Potential", f"{trend_data.get('viral_potential_score', 0):.2f}")
                
                with col2:
                    st.subheader("🎭 Script Data")
                    script_data = results.get('script_data', {})
                    if script_data:
                        st.metric("Script Parts", script_data.get('total_parts', 0))
                        st.metric("Duration", f"{script_data.get('target_duration', 0)}s")
                        st.metric("Viral Potential", f"{script_data.get('viral_potential', 0):.2f}")
                
                with col3:
                    st.subheader("🎬 Video Data")
                    video_data = results.get('video_data', {})
                    if video_data:
                        st.metric("Video Files", len(video_data.get('video_files', [])))
                        st.metric("Total Duration", f"{video_data.get('total_duration', 0):.1f}s")
                        st.metric("File Size", f"{video_data.get('file_size', 0) / 1e6:.1f}MB")
                
                # Upload results
                upload_results = results.get('upload_results', [])
                if upload_results:
                    st.subheader("📤 Upload Results")
                    for upload in upload_results:
                        if upload.get('status') == 'success':
                            st.success(f"✅ {upload.get('platform')}: {upload.get('url', 'N/A')}")
                        else:
                            st.error(f"❌ {upload.get('platform')}: {upload.get('error_message', 'Upload failed')}")
                
                # Clear processing state
                if st.button("🔄 Process Another Movie"):
                    del st.session_state.processing_movie
                    st.rerun()
                    
            elif results.get('status') == 'failed':
                st.markdown('<div class="status-box error-box">❌ Processing Failed</div>', unsafe_allow_html=True)
                st.error(f"Error: {results.get('error', 'Unknown error')}")
                
                if st.button("🔄 Retry"):
                    del st.session_state.processing_movie
                    st.rerun()
            else:
                st.markdown('<div class="status-box info-box">⏳ Processing in Progress...</div>', unsafe_allow_html=True)
                
                # Show progress
                if 'processing_started' in st.session_state:
                    elapsed = (datetime.now() - st.session_state.processing_started).seconds
                    st.progress(min(elapsed / 300, 1.0))  # Assume 5 minutes max
                    st.info(f"Processing for {elapsed} seconds...")
                
                # Auto-refresh
                time.sleep(2)
                st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🎬 AI Movie Reels Generator | Powered by Multi-Agent AI System</p>
        <p>Generate viral movie continuation content automatically</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 