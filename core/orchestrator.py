"""
Enhanced Orchestrator with LangGraph Workflow
Coordinates all agents with comprehensive data collection and automated movie selection
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import uuid

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from agents.trend_miner.agent import TrendMinerAgent
from agents.movie_analyzer.agent import MovieAnalyzerAgent
from agents.script_generator.agent import EnhancedScriptGeneratorAgent
from agents.voice_agent.agent import EnhancedVoiceAgent
from agents.video_generator.agent import EnhancedVideoGeneratorAgent
from agents.uploader.agent import UploaderAgent
from agents.movie_data_collector.agent import MovieDataCollectorAgent

logger = logging.getLogger(__name__)

@dataclass
class WorkflowState:
    """State for the LangGraph workflow"""
    # Input
    movie_title: Optional[str] = None
    auto_select_movie: bool = True
    
    # Trend Analysis
    trending_movies: List[Dict] = None
    selected_movie: Optional[Dict] = None
    trend_analysis_complete: bool = False
    
    # Movie Data Collection
    movie_data: Optional[Dict] = None
    data_collection_complete: bool = False
    
    # Movie Analysis
    movie_analysis: Optional[Dict] = None
    analysis_complete: bool = False
    
    # Script Generation
    script_data: Optional[Dict] = None
    script_complete: bool = False
    
    # Voice Generation
    audio_data: Optional[Dict] = None
    audio_complete: bool = False
    
    # Video Generation
    video_data: Optional[Dict] = None
    video_complete: bool = False
    
    # Upload
    upload_results: List[Dict] = None
    upload_complete: bool = False
    
    # Workflow Control
    current_step: str = "start"
    error_message: Optional[str] = None
    workflow_id: str = None
    
    def __post_init__(self):
        if self.trending_movies is None:
            self.trending_movies = []
        if self.upload_results is None:
            self.upload_results = []
        if self.workflow_id is None:
            self.workflow_id = str(uuid.uuid4())

class EnhancedOrchestrator:
    """
    Enhanced orchestrator with LangGraph workflow for automated movie content generation
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_dir = Path(config.get("output_dir", "output"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize all agents
        self.trend_agent = TrendMinerAgent(config)
        self.movie_data_collector = MovieDataCollectorAgent(config)
        self.movie_agent = MovieAnalyzerAgent(config)
        self.script_agent = EnhancedScriptGeneratorAgent(config)
        self.voice_agent = EnhancedVoiceAgent(config)
        self.video_agent = EnhancedVideoGeneratorAgent(config)
        self.upload_agent = UploaderAgent(config)
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
        
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create state graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("trend_analysis", self._trend_analysis_node)
        workflow.add_node("movie_selection", self._movie_selection_node)
        workflow.add_node("data_collection", self._data_collection_node)
        workflow.add_node("movie_analysis", self._movie_analysis_node)
        workflow.add_node("script_generation", self._script_generation_node)
        workflow.add_node("voice_generation", self._voice_generation_node)
        workflow.add_node("video_generation", self._video_generation_node)
        workflow.add_node("upload_content", self._upload_content_node)
        workflow.add_node("error_handler", self._error_handler_node)
        
        # Define edges
        workflow.set_entry_point("trend_analysis")
        
        # Conditional routing
        workflow.add_conditional_edges(
            "trend_analysis",
            self._should_auto_select_movie,
            {
                "auto_select": "movie_selection",
                "manual_input": "data_collection",
                "error": "error_handler"
            }
        )
        
        workflow.add_conditional_edges(
            "movie_selection",
            self._movie_selection_router,
            {
                "success": "data_collection",
                "error": "error_handler"
            }
        )
        
        workflow.add_conditional_edges(
            "data_collection",
            self._data_collection_router,
            {
                "success": "movie_analysis",
                "error": "error_handler"
            }
        )
        
        workflow.add_conditional_edges(
            "movie_analysis",
            self._movie_analysis_router,
            {
                "success": "script_generation",
                "error": "error_handler"
            }
        )
        
        workflow.add_conditional_edges(
            "script_generation",
            self._script_generation_router,
            {
                "success": "voice_generation",
                "error": "error_handler"
            }
        )
        
        workflow.add_conditional_edges(
            "voice_generation",
            self._voice_generation_router,
            {
                "success": "video_generation",
                "error": "error_handler"
            }
        )
        
        workflow.add_conditional_edges(
            "video_generation",
            self._video_generation_router,
            {
                "success": "upload_content",
                "error": "error_handler"
            }
        )
        
        workflow.add_conditional_edges(
            "upload_content",
            self._upload_router,
            {
                "success": END,
                "error": "error_handler"
            }
        )
        
        workflow.add_edge("error_handler", END)
        
        # Compile workflow
        return workflow.compile(checkpointer=MemorySaver())
    
    async def process_movie(self, movie_title: Optional[str] = None, auto_select: bool = True) -> Dict[str, Any]:
        """
        Process movie with enhanced workflow
        """
        logger.info(f"Starting enhanced workflow for movie: {movie_title or 'auto-select'}")
        
        try:
            # Initialize state
            initial_state = WorkflowState(
                movie_title=movie_title,
                auto_select_movie=auto_select,
                current_step="start"
            )
            
            # Run workflow
            config = {"configurable": {"thread_id": initial_state.workflow_id}}
            final_state = await self.workflow.ainvoke(initial_state, config)
            
            # Compile results
            results = await self._compile_results(final_state)
            
            # Save workflow results
            await self._save_workflow_results(final_state, results)
            
            logger.info(f"Workflow completed successfully for: {final_state.selected_movie or movie_title}")
            return results
            
        except Exception as e:
            logger.error(f"Workflow error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "workflow_id": initial_state.workflow_id if 'initial_state' in locals() else None
            }
    
    # Workflow Nodes
    async def _trend_analysis_node(self, state: WorkflowState) -> WorkflowState:
        """Trend analysis node"""
        logger.info("Executing trend analysis node")
        
        try:
            state.current_step = "trend_analysis"
            
            # Get trending movies
            trending_movies = await self.trend_agent.get_trending_movies()
            state.trending_movies = trending_movies
            
            # Calculate viral potential scores
            for movie in trending_movies:
                movie["viral_potential"] = await self._calculate_viral_potential(movie)
            
            # Sort by viral potential
            state.trending_movies.sort(key=lambda x: x.get("viral_potential", 0), reverse=True)
            
            state.trend_analysis_complete = True
            logger.info(f"Trend analysis complete. Found {len(trending_movies)} trending movies")
            
        except Exception as e:
            state.error_message = f"Trend analysis error: {str(e)}"
            logger.error(f"Trend analysis error: {str(e)}")
        
        return state
    
    async def _movie_selection_node(self, state: WorkflowState) -> WorkflowState:
        """Movie selection node"""
        logger.info("Executing movie selection node")
        
        try:
            state.current_step = "movie_selection"
            
            if not state.trending_movies:
                raise ValueError("No trending movies available")
            
            # Select the highest viral potential movie
            selected_movie = state.trending_movies[0]
            state.selected_movie = selected_movie
            state.movie_title = selected_movie.get("title")
            
            logger.info(f"Selected movie: {state.movie_title} (viral potential: {selected_movie.get('viral_potential', 0)})")
            
        except Exception as e:
            state.error_message = f"Movie selection error: {str(e)}"
            logger.error(f"Movie selection error: {str(e)}")
        
        return state
    
    async def _data_collection_node(self, state: WorkflowState) -> WorkflowState:
        """Data collection node"""
        logger.info(f"Executing data collection node for: {state.movie_title}")
        
        try:
            state.current_step = "data_collection"
            
            # Collect comprehensive movie data
            movie_data = await self.movie_data_collector.collect_comprehensive_data(state.movie_title)
            state.movie_data = movie_data
            
            state.data_collection_complete = True
            logger.info(f"Data collection complete for: {state.movie_title}")
            
        except Exception as e:
            state.error_message = f"Data collection error: {str(e)}"
            logger.error(f"Data collection error: {str(e)}")
        
        return state
    
    async def _movie_analysis_node(self, state: WorkflowState) -> WorkflowState:
        """Movie analysis node"""
        logger.info(f"Executing movie analysis node for: {state.movie_title}")
        
        try:
            state.current_step = "movie_analysis"
            
            # Analyze movie using collected data
            movie_analysis = await self.movie_agent.analyze_movie_with_data(
                state.movie_title, 
                state.movie_data
            )
            state.movie_analysis = movie_analysis
            
            state.analysis_complete = True
            logger.info(f"Movie analysis complete for: {state.movie_title}")
            
        except Exception as e:
            state.error_message = f"Movie analysis error: {str(e)}"
            logger.error(f"Movie analysis error: {str(e)}")
        
        return state
    
    async def _script_generation_node(self, state: WorkflowState) -> WorkflowState:
        """Script generation node"""
        logger.info(f"Executing script generation node for: {state.movie_title}")
        
        try:
            state.current_step = "script_generation"
            
            # Generate enhanced script using comprehensive data
            script_data = await self.script_agent.generate_enhanced_script(
                state.movie_title,
                state.movie_data
            )
            state.script_data = asdict(script_data)
            
            state.script_complete = True
            logger.info(f"Script generation complete for: {state.movie_title}")
            
        except Exception as e:
            state.error_message = f"Script generation error: {str(e)}"
            logger.error(f"Script generation error: {str(e)}")
        
        return state
    
    async def _voice_generation_node(self, state: WorkflowState) -> WorkflowState:
        """Voice generation node"""
        logger.info(f"Executing voice generation node for: {state.movie_title}")
        
        try:
            state.current_step = "voice_generation"
            
            # Generate enhanced audio using comprehensive data
            audio_data = await self.voice_agent.generate_enhanced_audio(
                state.movie_title,
                state.script_data,
                state.movie_data
            )
            state.audio_data = asdict(audio_data)
            
            state.audio_complete = True
            logger.info(f"Voice generation complete for: {state.movie_title}")
            
        except Exception as e:
            state.error_message = f"Voice generation error: {str(e)}"
            logger.error(f"Voice generation error: {str(e)}")
        
        return state
    
    async def _video_generation_node(self, state: WorkflowState) -> WorkflowState:
        """Video generation node"""
        logger.info(f"Executing video generation node for: {state.movie_title}")
        
        try:
            state.current_step = "video_generation"
            
            # Generate enhanced video using comprehensive data
            video_data = await self.video_agent.generate_enhanced_video(
                state.movie_title,
                state.script_data,
                state.movie_data,
                state.audio_data
            )
            state.video_data = asdict(video_data)
            
            state.video_complete = True
            logger.info(f"Video generation complete for: {state.movie_title}")
            
        except Exception as e:
            state.error_message = f"Video generation error: {str(e)}"
            logger.error(f"Video generation error: {str(e)}")
        
        return state
    
    async def _upload_content_node(self, state: WorkflowState) -> WorkflowState:
        """Upload content node"""
        logger.info(f"Executing upload content node for: {state.movie_title}")
        
        try:
            state.current_step = "upload_content"
            
            # Upload content to platforms
            upload_results = await self.upload_agent.upload_enhanced_content(
                state.movie_title,
                state.video_data,
                state.audio_data,
                state.script_data
            )
            state.upload_results = upload_results
            
            state.upload_complete = True
            logger.info(f"Upload complete for: {state.movie_title}")
            
        except Exception as e:
            state.error_message = f"Upload error: {str(e)}"
            logger.error(f"Upload error: {str(e)}")
        
        return state
    
    async def _error_handler_node(self, state: WorkflowState) -> WorkflowState:
        """Error handler node"""
        logger.error(f"Workflow error at step {state.current_step}: {state.error_message}")
        
        # Log error details
        error_details = {
            "workflow_id": state.workflow_id,
            "step": state.current_step,
            "error": state.error_message,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save error log
        error_file = self.output_dir / f"error_{state.workflow_id}.json"
        with open(error_file, 'w') as f:
            json.dump(error_details, f, indent=2)
        
        return state
    
    # Router Functions
    def _should_auto_select_movie(self, state: WorkflowState) -> str:
        """Determine if should auto-select movie"""
        if state.error_message:
            return "error"
        elif state.auto_select_movie:
            return "auto_select"
        else:
            return "manual_input"
    
    def _movie_selection_router(self, state: WorkflowState) -> str:
        """Route after movie selection"""
        if state.error_message:
            return "error"
        else:
            return "success"
    
    def _data_collection_router(self, state: WorkflowState) -> str:
        """Route after data collection"""
        if state.error_message:
            return "error"
        else:
            return "success"
    
    def _movie_analysis_router(self, state: WorkflowState) -> str:
        """Route after movie analysis"""
        if state.error_message:
            return "error"
        else:
            return "success"
    
    def _script_generation_router(self, state: WorkflowState) -> str:
        """Route after script generation"""
        if state.error_message:
            return "error"
        else:
            return "success"
    
    def _voice_generation_router(self, state: WorkflowState) -> str:
        """Route after voice generation"""
        if state.error_message:
            return "error"
        else:
            return "success"
    
    def _video_generation_router(self, state: WorkflowState) -> str:
        """Route after video generation"""
        if state.error_message:
            return "error"
        else:
            return "success"
    
    def _upload_router(self, state: WorkflowState) -> str:
        """Route after upload"""
        if state.error_message:
            return "error"
        else:
            return "success"
    
    # Helper Methods
    async def _calculate_viral_potential(self, movie: Dict) -> float:
        """Calculate viral potential for a movie"""
        # This would use a sophisticated algorithm
        base_score = movie.get("trending_score", 0) / 10.0
        popularity_boost = min(movie.get("social_mentions", 0) / 10000, 1.0)
        return min(base_score + popularity_boost * 0.3, 1.0)
    
    async def _compile_results(self, state: WorkflowState) -> Dict[str, Any]:
        """Compile final results"""
        return {
            "workflow_id": state.workflow_id,
            "status": "completed" if not state.error_message else "error",
            "movie_title": state.movie_title,
            "selected_movie": state.selected_movie,
            "trending_movies": state.trending_movies,
            "movie_data": state.movie_data,
            "movie_analysis": state.movie_analysis,
            "script_data": state.script_data,
            "audio_data": state.audio_data,
            "video_data": state.video_data,
            "upload_results": state.upload_results,
            "error_message": state.error_message,
            "completed_at": datetime.now().isoformat()
        }
    
    async def _save_workflow_results(self, state: WorkflowState, results: Dict[str, Any]):
        """Save workflow results"""
        results_file = self.output_dir / f"workflow_results_{state.workflow_id}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Workflow results saved to: {results_file}")
    
    async def auto_trend_analysis(self) -> Dict[str, Any]:
        """
        Perform automatic trend analysis and content generation
        """
        logger.info("Starting automatic trend analysis")
        
        try:
            # Run workflow with auto-selection
            results = await self.process_movie(auto_select=True)
            
            if results.get("status") == "completed":
                logger.info("Auto trend analysis completed successfully")
                return {
                    "status": "completed",
                    "selected_movie": results.get("selected_movie"),
                    "processing_result": results
                }
            else:
                logger.error("Auto trend analysis failed")
                return {
                    "status": "failed",
                    "error": results.get("error_message")
                }
                
        except Exception as e:
            logger.error(f"Auto trend analysis error: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow status"""
        try:
            # This would query the workflow state from memory
            return {
                "workflow_id": workflow_id,
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "workflow_id": workflow_id,
                "status": "error",
                "error": str(e)
            } 