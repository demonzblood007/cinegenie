#!/usr/bin/env python3
"""
Enhanced CineGenie - AI Movie Reels Generator
Main FastAPI application with LangGraph workflow
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from core.config import Settings
from core.orchestrator import EnhancedOrchestrator
from core.models import MovieData, ScriptData, AudioData, VideoData

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global orchestrator instance
orchestrator: Optional[EnhancedOrchestrator] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global orchestrator
    
    # Startup
    logger.info("Starting CineGenie Enhanced AI Movie Reels Generator")
    
    # Initialize settings and orchestrator
    settings = Settings()
    config = {
        "api_keys": {
            "openai": settings.openai_api_key,
            "elevenlabs": settings.elevenlabs_api_key,
            "boomy": settings.boomy_api_key,
            "tmdb": settings.tmdb_api_key,
            "youtube": settings.youtube_api_key,
            "spotify_client_id": settings.spotify_client_id,
            "spotify_client_secret": settings.spotify_client_secret,
            "runway": settings.runway_api_key,
            "pika": settings.pika_api_key,
            "stable_video": settings.stable_video_api_key,
        },
        "output_dir": "output",
        "max_tokens": 4000,
        "temperature": 0.8,
        "model": "gpt-4-turbo-preview",
        "voice_cloning_enabled": True,
        "character_accuracy_threshold": 0.8,
        "audio_quality_target": "high",
        "video_quality": "high",
        "resolution": "1080x1920",
        "fps": 30,
        "character_consistency_threshold": 0.8,
        "cinematic_quality_target": 0.85
    }
    
    orchestrator = EnhancedOrchestrator(config)
    logger.info("Enhanced Orchestrator initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CineGenie")

# Create FastAPI app
app = FastAPI(
    title="CineGenie Enhanced - AI Movie Reels Generator",
    description="Advanced AI system for generating viral movie continuation content using comprehensive data collection and LangGraph workflows",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class MovieRequest(BaseModel):
    movie_title: Optional[str] = None
    auto_select: bool = True

class AutoTrendRequest(BaseModel):
    max_movies: int = 10

class WorkflowStatusRequest(BaseModel):
    workflow_id: str

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CineGenie Enhanced - AI Movie Reels Generator",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Automated movie selection",
            "Comprehensive data collection",
            "Enhanced script generation",
            "Character-accurate voice generation",
            "Cinematic video generation",
            "Multi-platform upload",
            "LangGraph workflow orchestration"
        ]
    }

@app.get("/status")
async def get_status():
    """Get system status"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    return {
        "status": "healthy",
        "orchestrator": "initialized",
        "agents": {
            "trend_agent": "ready",
            "movie_data_collector": "ready",
            "movie_agent": "ready",
            "script_agent": "enhanced",
            "voice_agent": "enhanced",
            "video_agent": "enhanced",
            "upload_agent": "ready"
        },
        "workflow": "langgraph_enabled",
        "features": {
            "auto_movie_selection": True,
            "comprehensive_data_collection": True,
            "character_voice_cloning": True,
            "cinematic_video_generation": True,
            "viral_optimization": True
        }
    }

@app.get("/trending-movies")
async def get_trending_movies():
    """Get trending movies for content generation"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    try:
        trending_movies = await orchestrator.trend_agent.get_trending_movies()
        return {
            "status": "success",
            "trending_movies": trending_movies,
            "count": len(trending_movies)
        }
    except Exception as e:
        logger.error(f"Error getting trending movies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting trending movies: {str(e)}")

@app.post("/process-movie")
async def process_movie(request: MovieRequest, background_tasks: BackgroundTasks):
    """
    Process a movie with enhanced workflow
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    try:
        logger.info(f"Processing movie: {request.movie_title or 'auto-select'}")
        
        # Start workflow
        results = await orchestrator.process_movie(
            movie_title=request.movie_title,
            auto_select=request.auto_select
        )
        
        return {
            "status": "success",
            "workflow_id": results.get("workflow_id"),
            "movie_title": results.get("movie_title"),
            "selected_movie": results.get("selected_movie"),
            "message": f"Started processing movie: {results.get('movie_title')}",
            "workflow_status": results.get("status")
        }
        
    except Exception as e:
        logger.error(f"Error processing movie: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing movie: {str(e)}")

@app.post("/auto-trend-analysis")
async def auto_trend_analysis(request: AutoTrendRequest):
    """
    Perform automatic trend analysis and content generation
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    try:
        logger.info("Starting automatic trend analysis")
        
        results = await orchestrator.auto_trend_analysis()
        
        return {
            "status": "success",
            "auto_analysis": results,
            "message": "Automatic trend analysis completed"
        }
        
    except Exception as e:
        logger.error(f"Error in auto trend analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in auto trend analysis: {str(e)}")

@app.get("/results/{movie_title}")
async def get_results(movie_title: str):
    """
    Get processing results for a specific movie
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    try:
        # This would retrieve results from storage
        # For now, return mock enhanced results
        enhanced_results = {
            "movie_title": movie_title,
            "timestamp": "2024-01-15T10:30:00Z",
            "status": "completed",
            "workflow_id": f"workflow_{movie_title.lower().replace(' ', '_')}",
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
                "character_analysis": {
                    "protagonist": {
                        "appearance": "Professional protagonist appearance",
                        "voice_characteristics": "Confident, determined",
                        "personality_traits": ["confident", "charismatic", "professional"]
                    }
                },
                "visual_style_guide": {
                    "color_palette": ["#1a1a1a", "#4a4a4a", "#8b0000", "#ffd700"],
                    "visual_style": "cinematic_dark_contrast",
                    "lighting_style": "dramatic_side_lighting"
                },
                "audio_style_guide": {
                    "audio_style": "dynamic_orchestral",
                    "voice_characteristics": {"tone": "professional", "pacing": "moderate"}
                },
                "viral_strategy": {
                    "hook_strategies": ["curiosity_hook", "emotional_hook"],
                    "emotional_triggers": ["surprise", "excitement", "curiosity"],
                    "surprise_elements": ["unexpected_twist", "reveal"]
                },
                "parts": [
                    {
                        "part_num": 1,
                        "structure": "Hook",
                        "text": "Cobb wakes up in a new dream level...",
                        "character_voices": {"protagonist": "confident"},
                        "visual_references": ["dramatic_lighting"],
                        "audio_cues": ["tension_music"],
                        "emotional_arc": "curiosity",
                        "viral_elements": ["mystery"],
                        "duration_estimate": 12.0
                    }
                ]
            },
            "audio_data": {
                "voice_files": [
                    {
                        "character_name": "protagonist",
                        "voice_file_path": f"output/audio/{movie_title}_protagonist_part1_cloned.mp3",
                        "character_accuracy_score": 0.85,
                        "emotional_expression": "confident",
                        "dialogue_style": "professional"
                    }
                ],
                "background_music": f"output/audio/{movie_title}_background_music.mp3",
                "movie_style_accuracy": 0.85,
                "viral_optimization": {
                    "hook_audio": "optimized_hook.mp3",
                    "engagement_audio": "optimized_engagement.mp3"
                }
            },
            "video_data": {
                "video_files": [f"output/videos/{movie_title}_scene_1_enhanced.mp4"],
                "scenes": [
                    {
                        "scene_num": 1,
                        "visual_description": "Cinematic scene with dramatic atmosphere",
                        "character_positions": {"protagonist": "center"},
                        "camera_angles": ["medium_shot", "close_up"],
                        "lighting_style": "dramatic_side_lighting",
                        "color_palette": ["#1a1a1a", "#4a4a4a", "#8b0000", "#ffd700"],
                        "visual_effects": ["color_grading", "depth_of_field"],
                        "duration": 12.0,
                        "viral_elements": ["mystery"]
                    }
                ],
                "visual_style_accuracy": 0.85,
                "character_consistency": 0.80,
                "cinematic_quality": 0.85,
                "viral_optimization": {
                    "hook_frames": ["hook_frame_0"],
                    "engagement_moments": ["engagement_moment_0"],
                    "shareable_clips": ["shareable_clip_0"]
                }
            },
            "upload_results": [
                {
                    "platform": "YouTube Shorts",
                    "status": "success",
                    "url": f"https://youtube.com/shorts/{movie_title.lower().replace(' ', '_')}",
                    "analytics": {"views": 1250, "likes": 89}
                },
                {
                    "platform": "Instagram Reels",
                    "status": "success",
                    "url": f"https://instagram.com/reel/{movie_title.lower().replace(' ', '_')}",
                    "analytics": {"views": 890, "likes": 67}
                }
            ]
        }
        
        return enhanced_results
        
    except Exception as e:
        logger.error(f"Error getting results for {movie_title}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting results: {str(e)}")

@app.get("/workflow-status/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """
    Get workflow status by ID
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    try:
        status = await orchestrator.get_workflow_status(workflow_id)
        return status
    except Exception as e:
        logger.error(f"Error getting workflow status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting workflow status: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-15T10:30:00Z",
        "version": "2.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 