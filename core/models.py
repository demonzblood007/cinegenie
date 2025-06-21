"""
Data models for the Movie Continuation System
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class MovieData(BaseModel):
    """Movie information and analysis data"""
    title: str
    year: Optional[int] = None
    genre: List[str] = []
    director: Optional[str] = None
    cast: List[str] = []
    plot_summary: str
    characters: List[Dict[str, Any]] = []
    themes: List[str] = []
    tone: str
    ending_summary: str
    unresolved_plot_points: List[str] = []
    fan_favorite_scenes: List[str] = []
    metadata: Dict[str, Any] = {}


class TrendAnalysis(BaseModel):
    """Trend and sentiment analysis data"""
    movie_title: str
    popularity_score: float
    social_mentions: int
    review_count: int
    average_rating: float
    sentiment_distribution: Dict[str, float]
    trending_topics: List[str] = []
    fan_desires: List[str] = []
    most_anticipated_continuations: List[str] = []
    viral_potential_score: float
    target_audience: List[str] = []
    analysis_timestamp: datetime = Field(default_factory=datetime.now)


class ScriptData(BaseModel):
    """Generated script data"""
    movie_title: str
    script_type: str = "continuation"  # continuation, prequel, spin-off
    total_parts: int = 5
    parts: List[Dict[str, Any]] = []
    main_characters: List[str] = []
    story_arc: str
    emotional_tone: str
    target_duration: int = 60  # seconds
    fan_desire_alignment: float
    viral_potential: float
    generation_timestamp: datetime = Field(default_factory=datetime.now)


class AudioData(BaseModel):
    """Audio generation data"""
    script_id: str
    audio_files: List[str] = []  # File paths
    voice_actors: Dict[str, str] = {}  # Character -> Voice ID
    background_music: Optional[str] = None
    sound_effects: List[str] = []
    total_duration: float
    audio_quality: str
    generation_timestamp: datetime = Field(default_factory=datetime.now)


class VideoData(BaseModel):
    """Video generation data"""
    script_id: str
    video_files: List[str] = []  # File paths
    thumbnail_path: Optional[str] = None
    video_metadata: Dict[str, Any] = {}
    platform_optimizations: Dict[str, Any] = {}
    total_duration: float
    resolution: str
    file_size: int
    generation_timestamp: datetime = Field(default_factory=datetime.now)


class UploadResult(BaseModel):
    """Upload result data"""
    platform: str
    video_id: Optional[str] = None
    url: Optional[str] = None
    status: str  # success, failed, pending
    error_message: Optional[str] = None
    upload_timestamp: datetime = Field(default_factory=datetime.now)
    analytics: Dict[str, Any] = {}


class ProcessingStatus(BaseModel):
    """Processing status for a movie"""
    movie_title: str
    current_step: str
    progress: float  # 0.0 to 1.0
    status: str  # processing, completed, failed, pending
    start_time: datetime
    estimated_completion: Optional[datetime] = None
    error_message: Optional[str] = None
    step_results: Dict[str, Any] = {}


class AgentStatus(BaseModel):
    """Agent health and status"""
    agent_name: str
    status: str  # healthy, error, offline
    last_heartbeat: datetime
    error_count: int = 0
    processing_count: int = 0
    average_response_time: float = 0.0
    resource_usage: Dict[str, float] = {}


class SystemMetrics(BaseModel):
    """System-wide metrics"""
    total_movies_processed: int = 0
    successful_generations: int = 0
    failed_generations: int = 0
    average_processing_time: float = 0.0
    total_views_generated: int = 0
    total_engagement: int = 0
    system_uptime: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now) 