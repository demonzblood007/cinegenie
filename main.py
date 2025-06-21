#!/usr/bin/env python3
"""
Multi-Agent Movie Continuation System
Main entry point for the entire pipeline
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from core.config import Settings
from core.orchestrator import MovieContinuationOrchestrator
from agents.trend_miner.agent import TrendMiningAgent
from agents.movie_analyzer.agent import MovieUnderstandingAgent
from agents.script_generator.agent import ScriptGeneratorAgent
from agents.voice_agent.agent import VoiceAudioAgent
from agents.video_generator.agent import VideoGeneratorAgent
from agents.uploader.agent import UploadAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Movie Continuation System",
    description="AI-powered system for generating viral movie continuation content",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator instance
orchestrator: MovieContinuationOrchestrator = None

@app.on_event("startup")
async def startup_event():
    """Initialize the system on startup"""
    global orchestrator
    
    logger.info("Starting Movie Continuation System...")
    
    # Load settings
    settings = Settings()
    
    # Initialize orchestrator
    orchestrator = MovieContinuationOrchestrator(settings)
    
    # Initialize all agents
    await orchestrator.initialize_agents()
    
    logger.info("System initialized successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Movie Continuation System...")
    if orchestrator:
        await orchestrator.cleanup()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Movie Continuation System",
        "version": "1.0.0"
    }

@app.get("/status")
async def get_status():
    """Get system status and agent health"""
    if not orchestrator:
        return {"status": "initializing"}
    
    return await orchestrator.get_status()

@app.post("/process-movie")
async def process_movie(
    movie_title: str,
    background_tasks: BackgroundTasks
):
    """Process a specific movie through the entire pipeline"""
    if not orchestrator:
        return {"error": "System not initialized"}
    
    # Start processing in background
    background_tasks.add_task(orchestrator.process_movie, movie_title)
    
    return {
        "message": f"Started processing movie: {movie_title}",
        "movie_title": movie_title,
        "status": "processing"
    }

@app.post("/auto-trend-analysis")
async def auto_trend_analysis(background_tasks: BackgroundTasks):
    """Automatically analyze trending movies and process the top one"""
    if not orchestrator:
        return {"error": "System not initialized"}
    
    background_tasks.add_task(orchestrator.auto_trend_analysis)
    
    return {
        "message": "Started automatic trend analysis",
        "status": "processing"
    }

@app.get("/results/{movie_title}")
async def get_results(movie_title: str):
    """Get results for a processed movie"""
    if not orchestrator:
        return {"error": "System not initialized"}
    
    return await orchestrator.get_results(movie_title)

@app.get("/trending-movies")
async def get_trending_movies():
    """Get current trending movies"""
    if not orchestrator:
        return {"error": "System not initialized"}
    
    return await orchestrator.get_trending_movies()

if __name__ == "__main__":
    # Create necessary directories
    Path("./output/videos").mkdir(parents=True, exist_ok=True)
    Path("./output/audio").mkdir(parents=True, exist_ok=True)
    Path("./temp").mkdir(parents=True, exist_ok=True)
    Path("./data").mkdir(parents=True, exist_ok=True)
    
    # Run the FastAPI server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 