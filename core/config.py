"""
Configuration management for the Movie Continuation System
"""

from typing import Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # LLM API Keys
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    cohere_api_key: Optional[str] = Field(default=None, env="COHERE_API_KEY")
    mistral_api_key: Optional[str] = Field(default=None, env="MISTRAL_API_KEY")
    
    # Voice & Audio APIs
    elevenlabs_api_key: Optional[str] = Field(default=None, env="ELEVENLABS_API_KEY")
    bark_api_key: Optional[str] = Field(default=None, env="BARK_API_KEY")
    
    # Video & Music APIs
    boomy_api_key: Optional[str] = Field(default=None, env="BOOMY_API_KEY")
    suno_api_key: Optional[str] = Field(default=None, env="SUNO_API_KEY")
    capcut_api_key: Optional[str] = Field(default=None, env="CAPCUT_API_KEY")
    
    # Social Media APIs
    youtube_api_key: Optional[str] = Field(default=None, env="YOUTUBE_API_KEY")
    twitter_api_key: Optional[str] = Field(default=None, env="TWITTER_API_KEY")
    twitter_api_secret: Optional[str] = Field(default=None, env="TWITTER_API_SECRET")
    twitter_access_token: Optional[str] = Field(default=None, env="TWITTER_ACCESS_TOKEN")
    twitter_access_secret: Optional[str] = Field(default=None, env="TWITTER_ACCESS_SECRET")
    reddit_client_id: Optional[str] = Field(default=None, env="REDDIT_CLIENT_ID")
    reddit_client_secret: Optional[str] = Field(default=None, env="REDDIT_CLIENT_SECRET")
    
    # Database & Storage
    supabase_url: Optional[str] = Field(default=None, env="SUPABASE_URL")
    supabase_key: Optional[str] = Field(default=None, env="SUPABASE_KEY")
    qdrant_url: Optional[str] = Field(default="http://localhost:6333", env="QDRANT_URL")
    qdrant_api_key: Optional[str] = Field(default=None, env="QDRANT_API_KEY")
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Cloud Services
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    aws_s3_bucket: Optional[str] = Field(default=None, env="AWS_S3_BUCKET")
    
    # Monitoring
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    
    # Application Settings
    max_concurrent_agents: int = Field(default=5, env="MAX_CONCURRENT_AGENTS")
    video_output_dir: str = Field(default="./output/videos", env="VIDEO_OUTPUT_DIR")
    audio_output_dir: str = Field(default="./output/audio", env="AUDIO_OUTPUT_DIR")
    temp_dir: str = Field(default="./temp", env="TEMP_DIR")
    
    # Agent Configuration
    trend_analysis_interval: int = Field(default=3600, env="TREND_ANALYSIS_INTERVAL")
    max_reviews_per_movie: int = Field(default=10000, env="MAX_REVIEWS_PER_MOVIE")
    script_max_length: int = Field(default=5000, env="SCRIPT_MAX_LENGTH")
    video_max_duration: int = Field(default=60, env="VIDEO_MAX_DURATION")
    upload_retry_attempts: int = Field(default=3, env="UPLOAD_RETRY_ATTEMPTS")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def validate_required_keys(self) -> list[str]:
        """Validate that required API keys are present"""
        missing_keys = []
        
        # Check for at least one LLM provider
        if not any([
            self.openai_api_key,
            self.anthropic_api_key,
            self.cohere_api_key,
            self.mistral_api_key
        ]):
            missing_keys.append("At least one LLM API key (OPENAI, ANTHROPIC, COHERE, or MISTRAL)")
        
        # Check for voice API
        if not self.elevenlabs_api_key and not self.bark_api_key:
            missing_keys.append("At least one voice API key (ELEVENLABS or BARK)")
        
        # Check for social media APIs
        if not self.youtube_api_key:
            missing_keys.append("YOUTUBE_API_KEY")
        
        return missing_keys
    
    def get_llm_provider(self) -> str:
        """Get the primary LLM provider based on available keys"""
        if self.openai_api_key:
            return "openai"
        elif self.anthropic_api_key:
            return "anthropic"
        elif self.cohere_api_key:
            return "cohere"
        elif self.mistral_api_key:
            return "mistral"
        else:
            raise ValueError("No LLM API key configured")
    
    def get_voice_provider(self) -> str:
        """Get the primary voice provider based on available keys"""
        if self.elevenlabs_api_key:
            return "elevenlabs"
        elif self.bark_api_key:
            return "bark"
        else:
            raise ValueError("No voice API key configured") 