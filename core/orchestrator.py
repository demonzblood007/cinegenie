"""
Main orchestrator for the Movie Continuation System
Coordinates all agents in the pipeline
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from core.config import Settings
from core.models import MovieData, TrendAnalysis, ScriptData, AudioData, VideoData
from agents.trend_miner.agent import TrendMiningAgent
from agents.movie_analyzer.agent import MovieUnderstandingAgent
from agents.script_generator.agent import ScriptGeneratorAgent
from agents.voice_agent.agent import VoiceAudioAgent
from agents.video_generator.agent import VideoGeneratorAgent
from agents.uploader.agent import UploadAgent

logger = logging.getLogger(__name__)


class MovieContinuationOrchestrator:
    """Main orchestrator for the movie continuation pipeline"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.agents = {}
        self.processing_tasks = {}
        self.results_cache = {}
        
        # Initialize agents
        self.trend_agent = None
        self.movie_agent = None
        self.script_agent = None
        self.voice_agent = None
        self.video_agent = None
        self.upload_agent = None
    
    async def initialize_agents(self):
        """Initialize all agents"""
        logger.info("Initializing agents...")
        
        try:
            # Initialize trend mining agent
            self.trend_agent = TrendMiningAgent(self.settings)
            await self.trend_agent.initialize()
            
            # Initialize movie understanding agent
            self.movie_agent = MovieUnderstandingAgent(self.settings)
            await self.movie_agent.initialize()
            
            # Initialize script generator agent
            self.script_agent = ScriptGeneratorAgent(self.settings)
            await self.script_agent.initialize()
            
            # Initialize voice and audio agent
            self.voice_agent = VoiceAudioAgent(self.settings)
            await self.voice_agent.initialize()
            
            # Initialize video generator agent
            self.video_agent = VideoGeneratorAgent(self.settings)
            await self.video_agent.initialize()
            
            # Initialize upload agent
            self.upload_agent = UploadAgent(self.settings)
            await self.upload_agent.initialize()
            
            logger.info("All agents initialized successfully!")
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            raise
    
    async def process_movie(self, movie_title: str) -> Dict[str, Any]:
        """Process a movie through the entire pipeline"""
        logger.info(f"Starting processing for movie: {movie_title}")
        
        try:
            # Step 1: Trend Analysis
            logger.info(f"Step 1: Analyzing trends for {movie_title}")
            trend_data = await self.trend_agent.analyze_movie_trends(movie_title)
            
            # Step 2: Movie Understanding
            logger.info(f"Step 2: Understanding movie content for {movie_title}")
            movie_data = await self.movie_agent.analyze_movie(movie_title)
            
            # Step 3: Script Generation
            logger.info(f"Step 3: Generating continuation script for {movie_title}")
            script_data = await self.script_agent.generate_script(
                movie_data, trend_data
            )
            
            # Step 4: Voice and Audio Generation
            logger.info(f"Step 4: Generating audio for {movie_title}")
            audio_data = await self.voice_agent.generate_audio(
                script_data, movie_data
            )
            
            # Step 5: Video Generation
            logger.info(f"Step 5: Generating video for {movie_title}")
            video_data = await self.video_agent.generate_video(
                script_data, audio_data, movie_data
            )
            
            # Step 6: Upload Content
            logger.info(f"Step 6: Uploading content for {movie_title}")
            upload_results = await self.upload_agent.upload_content(
                video_data, movie_title
            )
            
            # Store results
            results = {
                "movie_title": movie_title,
                "timestamp": datetime.now().isoformat(),
                "trend_data": trend_data,
                "movie_data": movie_data,
                "script_data": script_data,
                "audio_data": audio_data,
                "video_data": video_data,
                "upload_results": upload_results,
                "status": "completed"
            }
            
            self.results_cache[movie_title] = results
            logger.info(f"Successfully completed processing for {movie_title}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing movie {movie_title}: {e}")
            error_result = {
                "movie_title": movie_title,
                "timestamp": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e)
            }
            self.results_cache[movie_title] = error_result
            return error_result
    
    async def auto_trend_analysis(self) -> Dict[str, Any]:
        """Automatically analyze trending movies and process the top one"""
        logger.info("Starting automatic trend analysis")
        
        try:
            # Get trending movies
            trending_movies = await self.trend_agent.get_trending_movies()
            
            if not trending_movies:
                return {"status": "no_trending_movies_found"}
            
            # Select the top trending movie
            top_movie = trending_movies[0]
            logger.info(f"Selected top trending movie: {top_movie['title']}")
            
            # Process the movie
            result = await self.process_movie(top_movie['title'])
            
            return {
                "status": "completed",
                "selected_movie": top_movie,
                "processing_result": result
            }
            
        except Exception as e:
            logger.error(f"Error in auto trend analysis: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def get_trending_movies(self) -> List[Dict[str, Any]]:
        """Get current trending movies"""
        try:
            return await self.trend_agent.get_trending_movies()
        except Exception as e:
            logger.error(f"Error getting trending movies: {e}")
            return []
    
    async def get_results(self, movie_title: str) -> Optional[Dict[str, Any]]:
        """Get results for a processed movie"""
        return self.results_cache.get(movie_title)
    
    async def get_status(self) -> Dict[str, Any]:
        """Get system status and agent health"""
        agent_status = {}
        
        # Check each agent's status
        for agent_name, agent in [
            ("trend_agent", self.trend_agent),
            ("movie_agent", self.movie_agent),
            ("script_agent", self.script_agent),
            ("voice_agent", self.voice_agent),
            ("video_agent", self.video_agent),
            ("upload_agent", self.upload_agent)
        ]:
            try:
                if agent:
                    agent_status[agent_name] = await agent.get_status()
                else:
                    agent_status[agent_name] = "not_initialized"
            except Exception as e:
                agent_status[agent_name] = f"error: {str(e)}"
        
        return {
            "status": "running",
            "agents": agent_status,
            "processing_tasks": len(self.processing_tasks),
            "cached_results": len(self.results_cache),
            "timestamp": datetime.now().isoformat()
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up orchestrator...")
        
        # Cleanup agents
        for agent in [
            self.trend_agent,
            self.movie_agent,
            self.script_agent,
            self.voice_agent,
            self.video_agent,
            self.upload_agent
        ]:
            if agent:
                try:
                    await agent.cleanup()
                except Exception as e:
                    logger.error(f"Error cleaning up agent: {e}")
        
        # Cancel any running tasks
        for task in self.processing_tasks.values():
            if not task.done():
                task.cancel()
        
        logger.info("Orchestrator cleanup completed") 