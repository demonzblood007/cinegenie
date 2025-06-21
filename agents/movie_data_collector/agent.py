"""
Enhanced Movie Data Collector Agent
Collects comprehensive movie data for superior content generation
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class MovieVisualData:
    """Visual reference data for movie scenes"""
    movie_title: str
    screenshots: List[str]
    color_palette: List[str]
    visual_style: str
    cinematography_style: str
    key_scenes: List[Dict[str, Any]]
    character_appearances: Dict[str, str]

@dataclass
class MovieAudioData:
    """Audio reference data for movie content"""
    movie_title: str
    soundtrack_urls: List[str]
    character_voice_samples: Dict[str, List[str]]
    sound_effects: List[str]
    audio_style: str
    background_music: List[str]

@dataclass
class MovieCharacterData:
    """Character analysis and reference data"""
    character_name: str
    appearance_description: str
    voice_characteristics: str
    personality_traits: List[str]
    key_dialogue_samples: List[str]
    visual_references: List[str]

@dataclass
class MovieMetadata:
    """Comprehensive movie metadata"""
    title: str
    year: int
    genre: List[str]
    director: str
    cast: List[str]
    plot_summary: str
    rating: float
    runtime: int
    language: str
    country: str

class MovieDataCollectorAgent:
    """
    Enhanced movie data collector that gathers comprehensive data
    from multiple sources for superior content generation
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_keys = config.get("api_keys", {})
        self.output_dir = Path(config.get("output_dir", "data/movies"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # API endpoints
        self.tmdb_api_key = self.api_keys.get("tmdb")
        self.youtube_api_key = self.api_keys.get("youtube")
        self.spotify_client_id = self.api_keys.get("spotify_client_id")
        self.spotify_client_secret = self.api_keys.get("spotify_client_secret")
        
        # Base URLs
        self.tmdb_base_url = "https://api.themoviedb.org/3"
        self.youtube_base_url = "https://www.googleapis.com/youtube/v3"
        
    async def collect_comprehensive_data(self, movie_title: str) -> Dict[str, Any]:
        """
        Collect comprehensive movie data from multiple sources
        """
        logger.info(f"Starting comprehensive data collection for: {movie_title}")
        
        try:
            # Step 1: Get movie metadata
            metadata = await self._get_movie_metadata(movie_title)
            if not metadata:
                raise ValueError(f"Could not find metadata for: {movie_title}")
            
            # Step 2: Collect visual data
            visual_data = await self._collect_visual_data(metadata)
            
            # Step 3: Collect audio data
            audio_data = await self._collect_audio_data(metadata)
            
            # Step 4: Collect character data
            character_data = await self._collect_character_data(metadata)
            
            # Step 5: Analyze script requirements
            script_analysis = await self._analyze_script_requirements(metadata)
            
            # Compile comprehensive data
            comprehensive_data = {
                "metadata": metadata,
                "visual_data": visual_data,
                "audio_data": audio_data,
                "character_data": character_data,
                "script_analysis": script_analysis,
                "collection_timestamp": datetime.now().isoformat(),
                "movie_title": movie_title
            }
            
            # Save to file
            await self._save_comprehensive_data(movie_title, comprehensive_data)
            
            logger.info(f"Successfully collected comprehensive data for: {movie_title}")
            return comprehensive_data
            
        except Exception as e:
            logger.error(f"Error collecting data for {movie_title}: {str(e)}")
            raise
    
    async def _get_movie_metadata(self, movie_title: str) -> Optional[MovieMetadata]:
        """Get comprehensive movie metadata from TMDB"""
        if not self.tmdb_api_key:
            logger.warning("TMDB API key not available, using mock data")
            return self._get_mock_metadata(movie_title)
        
        async with aiohttp.ClientSession() as session:
            # Search for movie
            search_url = f"{self.tmdb_base_url}/search/movie"
            params = {
                "api_key": self.tmdb_api_key,
                "query": movie_title,
                "language": "en-US"
            }
            
            async with session.get(search_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("results"):
                        movie = data["results"][0]
                        movie_id = movie["id"]
                        
                        # Get detailed movie info
                        detail_url = f"{self.tmdb_base_url}/movie/{movie_id}"
                        detail_params = {
                            "api_key": self.tmdb_api_key,
                            "append_to_response": "credits,videos,images"
                        }
                        
                        async with session.get(detail_url, params=detail_params) as detail_response:
                            if detail_response.status == 200:
                                detail_data = await detail_response.json()
                                return self._parse_movie_metadata(detail_data)
        
        return None
    
    async def _collect_visual_data(self, metadata: MovieMetadata) -> MovieVisualData:
        """Collect visual reference data"""
        logger.info(f"Collecting visual data for: {metadata.title}")
        
        visual_data = MovieVisualData(
            movie_title=metadata.title,
            screenshots=[],
            color_palette=[],
            visual_style="",
            cinematography_style="",
            key_scenes=[],
            character_appearances={}
        )
        
        if self.tmdb_api_key:
            async with aiohttp.ClientSession() as session:
                # Get movie images
                images_url = f"{self.tmdb_base_url}/movie/{metadata.title}/images"
                params = {"api_key": self.tmdb_api_key}
                
                async with session.get(images_url, params=params) as response:
                    if response.status == 200:
                        images_data = await response.json()
                        
                        # Collect screenshots
                        if images_data.get("backdrops"):
                            visual_data.screenshots = [
                                f"https://image.tmdb.org/t/p/original{img['file_path']}"
                                for img in images_data["backdrops"][:10]
                            ]
                        
                        # Analyze visual style
                        visual_data.visual_style = await self._analyze_visual_style(images_data)
                        visual_data.color_palette = await self._extract_color_palette(images_data)
        
        # Get character appearances
        visual_data.character_appearances = await self._get_character_appearances(metadata)
        
        return visual_data
    
    async def _collect_audio_data(self, metadata: MovieMetadata) -> MovieAudioData:
        """Collect audio reference data"""
        logger.info(f"Collecting audio data for: {metadata.title}")
        
        audio_data = MovieAudioData(
            movie_title=metadata.title,
            soundtrack_urls=[],
            character_voice_samples={},
            sound_effects=[],
            audio_style="",
            background_music=[]
        )
        
        # Get soundtrack information
        if self.spotify_client_id and self.spotify_client_secret:
            audio_data.soundtrack_urls = await self._get_soundtrack_urls(metadata)
        
        # Get character voice samples from YouTube
        if self.youtube_api_key:
            audio_data.character_voice_samples = await self._get_character_voice_samples(metadata)
        
        # Analyze audio style
        audio_data.audio_style = await self._analyze_audio_style(metadata)
        
        return audio_data
    
    async def _collect_character_data(self, metadata: MovieMetadata) -> List[MovieCharacterData]:
        """Collect detailed character data"""
        logger.info(f"Collecting character data for: {metadata.title}")
        
        characters = []
        
        for actor in metadata.cast[:5]:  # Top 5 cast members
            character_data = MovieCharacterData(
                character_name=actor,
                appearance_description="",
                voice_characteristics="",
                personality_traits=[],
                key_dialogue_samples=[],
                visual_references=[]
            )
            
            # Get character details
            if self.tmdb_api_key:
                character_details = await self._get_character_details(actor, metadata.title)
                if character_details:
                    character_data.appearance_description = character_details.get("description", "")
                    character_data.personality_traits = character_details.get("traits", [])
            
            # Get voice samples
            if self.youtube_api_key:
                character_data.key_dialogue_samples = await self._get_dialogue_samples(actor, metadata.title)
            
            characters.append(character_data)
        
        return characters
    
    async def _analyze_script_requirements(self, metadata: MovieMetadata) -> Dict[str, Any]:
        """Analyze what the script needs based on collected data"""
        logger.info(f"Analyzing script requirements for: {metadata.title}")
        
        script_analysis = {
            "required_characters": [],
            "visual_references": [],
            "audio_references": [],
            "style_guidelines": {},
            "content_warnings": [],
            "target_audience": "",
            "viral_elements": []
        }
        
        # Analyze genre for style guidelines
        if "action" in metadata.genre:
            script_analysis["style_guidelines"]["pacing"] = "fast"
            script_analysis["viral_elements"].append("thrilling_action")
        elif "drama" in metadata.genre:
            script_analysis["style_guidelines"]["pacing"] = "emotional"
            script_analysis["viral_elements"].append("emotional_depth")
        elif "comedy" in metadata.genre:
            script_analysis["style_guidelines"]["pacing"] = "humorous"
            script_analysis["viral_elements"].append("humor")
        
        # Determine target audience
        if metadata.rating >= 8.0:
            script_analysis["target_audience"] = "movie_enthusiasts"
        elif metadata.rating >= 7.0:
            script_analysis["target_audience"] = "general_audience"
        else:
            script_analysis["target_audience"] = "casual_viewers"
        
        return script_analysis
    
    async def _get_mock_metadata(self, movie_title: str) -> MovieMetadata:
        """Get mock metadata for testing"""
        return MovieMetadata(
            title=movie_title,
            year=2020,
            genre=["Action", "Sci-Fi"],
            director="Christopher Nolan",
            cast=["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Ellen Page"],
            plot_summary="A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
            rating=8.8,
            runtime=148,
            language="English",
            country="USA"
        )
    
    async def _analyze_visual_style(self, images_data: Dict) -> str:
        """Analyze visual style from movie images"""
        # This would use computer vision to analyze image characteristics
        return "cinematic_dark_contrast"
    
    async def _extract_color_palette(self, images_data: Dict) -> List[str]:
        """Extract dominant colors from movie images"""
        # This would use color analysis algorithms
        return ["#1a1a1a", "#4a4a4a", "#8b0000", "#ffd700"]
    
    async def _get_character_appearances(self, metadata: MovieMetadata) -> Dict[str, str]:
        """Get character appearance descriptions"""
        appearances = {}
        for actor in metadata.cast[:3]:
            appearances[actor] = f"Professional {actor} appearance from {metadata.title}"
        return appearances
    
    async def _get_soundtrack_urls(self, metadata: MovieMetadata) -> List[str]:
        """Get soundtrack URLs from Spotify"""
        # Implementation would use Spotify API
        return [f"spotify:track:soundtrack_{metadata.title.lower().replace(' ', '_')}"]
    
    async def _get_character_voice_samples(self, metadata: MovieMetadata) -> Dict[str, List[str]]:
        """Get character voice samples from YouTube"""
        samples = {}
        for actor in metadata.cast[:3]:
            samples[actor] = [f"youtube:voice_sample_{actor.lower().replace(' ', '_')}"]
        return samples
    
    async def _analyze_audio_style(self, metadata: MovieMetadata) -> str:
        """Analyze audio style based on movie characteristics"""
        if "action" in metadata.genre:
            return "dynamic_orchestral"
        elif "drama" in metadata.genre:
            return "emotional_ambient"
        else:
            return "balanced_mixed"
    
    async def _get_character_details(self, actor: str, movie_title: str) -> Optional[Dict]:
        """Get detailed character information"""
        # Implementation would use TMDB API
        return {
            "description": f"Professional {actor} character from {movie_title}",
            "traits": ["confident", "charismatic", "professional"]
        }
    
    async def _get_dialogue_samples(self, actor: str, movie_title: str) -> List[str]:
        """Get dialogue samples for character"""
        # Implementation would use YouTube API
        return [f"dialogue_sample_{actor.lower().replace(' ', '_')}_1"]
    
    async def _save_comprehensive_data(self, movie_title: str, data: Dict[str, Any]):
        """Save comprehensive data to file"""
        filename = f"{movie_title.lower().replace(' ', '_')}_data.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved comprehensive data to: {filepath}")
    
    async def get_data_for_script(self, movie_title: str, script_content: str) -> Dict[str, Any]:
        """
        Get specific data needed for script enhancement
        """
        logger.info(f"Getting script-specific data for: {movie_title}")
        
        # Analyze script to identify required elements
        required_elements = await self._analyze_script_elements(script_content)
        
        # Get comprehensive data
        comprehensive_data = await self.collect_comprehensive_data(movie_title)
        
        # Filter data based on script requirements
        filtered_data = {
            "required_characters": required_elements.get("characters", []),
            "required_scenes": required_elements.get("scenes", []),
            "required_audio": required_elements.get("audio", []),
            "visual_references": comprehensive_data["visual_data"],
            "audio_references": comprehensive_data["audio_data"],
            "character_references": comprehensive_data["character_data"]
        }
        
        return filtered_data
    
    async def _analyze_script_elements(self, script_content: str) -> Dict[str, List[str]]:
        """Analyze script to identify required elements"""
        # This would use NLP to extract character names, scenes, etc.
        return {
            "characters": ["protagonist", "antagonist"],
            "scenes": ["opening", "climax", "ending"],
            "audio": ["dialogue", "background_music", "sound_effects"]
        } 