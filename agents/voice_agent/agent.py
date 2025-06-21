"""
Voice + Audio Agent
Generates character voices and background music for the script
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
import aiofiles
import aiohttp
from datetime import datetime

from core.config import Settings
from core.models import AudioData, ScriptData, MovieData

logger = logging.getLogger(__name__)


class VoiceAudioAgent:
    """Agent responsible for generating voices and audio"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.voice_provider = settings.get_voice_provider()
        self.session = None
        self.voice_cache = {}
        
    async def initialize(self):
        """Initialize the agent and its components"""
        logger.info("Initializing Voice + Audio Agent...")
        
        # Initialize HTTP session
        self.session = aiohttp.ClientSession()
        
        # Initialize voice providers
        self.voice_providers = {
            'elevenlabs': ElevenLabsProvider(self.session, self.settings.elevenlabs_api_key),
            'bark': BarkProvider(self.session, self.settings.bark_api_key),
            'rvc': RVCProvider(self.session)
        }
        
        # Initialize music providers
        self.music_providers = {
            'boomy': BoomyProvider(self.session, self.settings.boomy_api_key),
            'suno': SunoProvider(self.session, self.settings.suno_api_key),
            'youtube': YouTubeMusicProvider(self.session)
        }
        
        # Create output directories
        Path(self.settings.audio_output_dir).mkdir(parents=True, exist_ok=True)
        
        logger.info("Voice + Audio Agent initialized successfully!")
    
    async def generate_audio(self, script_data: ScriptData, movie_data: MovieData) -> AudioData:
        """Generate audio for the entire script"""
        logger.info(f"Generating audio for script: {script_data.movie_title}")
        
        try:
            script_id = str(script_data.generation_timestamp.timestamp())
            audio_files = []
            voice_actors = {}
            sound_effects = []
            
            # Generate audio for each script part
            for i, part in enumerate(script_data.parts):
                logger.info(f"Generating audio for part {i+1}")
                
                # Generate character voices
                part_audio_file = await self._generate_part_audio(
                    part, movie_data, script_id, i+1
                )
                audio_files.append(part_audio_file)
                
                # Map characters to voice IDs
                for character in movie_data.characters:
                    if character['name'] not in voice_actors:
                        voice_actors[character['name']] = await self._get_voice_id(character)
            
            # Generate background music
            background_music = await self._generate_background_music(
                script_data, movie_data, script_id
            )
            
            # Calculate total duration
            total_duration = await self._calculate_total_duration(audio_files)
            
            # Create AudioData
            audio_data = AudioData(
                script_id=script_id,
                audio_files=audio_files,
                voice_actors=voice_actors,
                background_music=background_music,
                sound_effects=sound_effects,
                total_duration=total_duration,
                audio_quality="high",
                generation_timestamp=datetime.now()
            )
            
            logger.info(f"Audio generation completed for {script_data.movie_title}")
            return audio_data
            
        except Exception as e:
            logger.error(f"Error generating audio: {e}")
            raise
    
    async def _generate_part_audio(self, part: Dict[str, Any], movie_data: MovieData, script_id: str, part_num: int) -> str:
        """Generate audio for a single script part"""
        try:
            # Extract character dialogue from script part
            dialogue = self._extract_dialogue(part['text'])
            
            # Generate voice for each character
            voice_segments = []
            for char_name, lines in dialogue.items():
                voice_id = await self._get_voice_id({'name': char_name})
                voice_audio = await self._generate_character_voice(lines, voice_id)
                voice_segments.append(voice_audio)
            
            # Combine voice segments
            combined_audio = await self._combine_voice_segments(voice_segments)
            
            # Save to file
            output_path = f"{self.settings.audio_output_dir}/part_{part_num}_{script_id}.wav"
            await self._save_audio_file(combined_audio, output_path)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating part audio: {e}")
            # Return a placeholder audio file
            return f"{self.settings.audio_output_dir}/placeholder_part_{part_num}.wav"
    
    async def _generate_character_voice(self, text: str, voice_id: str) -> bytes:
        """Generate voice for a character using the selected provider"""
        try:
            if self.voice_provider == "elevenlabs":
                return await self.voice_providers['elevenlabs'].generate_voice(text, voice_id)
            elif self.voice_provider == "bark":
                return await self.voice_providers['bark'].generate_voice(text, voice_id)
            elif self.voice_provider == "rvc":
                return await self.voice_providers['rvc'].generate_voice(text, voice_id)
            else:
                # Fallback to default
                return await self.voice_providers['elevenlabs'].generate_voice(text, voice_id)
                
        except Exception as e:
            logger.error(f"Error generating character voice: {e}")
            # Return silence or placeholder
            return b""
    
    async def _generate_background_music(self, script_data: ScriptData, movie_data: MovieData, script_id: str) -> Optional[str]:
        """Generate background music matching the movie's tone"""
        try:
            # Determine music style based on movie tone and themes
            music_style = self._determine_music_style(movie_data.tone, movie_data.themes)
            
            # Generate music using selected provider
            if self.settings.boomy_api_key:
                music_data = await self.music_providers['boomy'].generate_music(music_style)
            elif self.settings.suno_api_key:
                music_data = await self.music_providers['suno'].generate_music(music_style)
            else:
                music_data = await self.music_providers['youtube'].get_music(music_style)
            
            # Save music file
            output_path = f"{self.settings.audio_output_dir}/bg_music_{script_id}.mp3"
            await self._save_audio_file(music_data, output_path)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating background music: {e}")
            return None
    
    def _extract_dialogue(self, script_text: str) -> Dict[str, str]:
        """Extract character dialogue from script text"""
        # Simple dialogue extraction (can be improved with NLP)
        dialogue = {}
        lines = script_text.split('\n')
        current_character = None
        
        for line in lines:
            line = line.strip()
            if line.isupper() and len(line) < 50:  # Character name
                current_character = line
                dialogue[current_character] = ""
            elif current_character and line:
                dialogue[current_character] += line + " "
        
        return dialogue
    
    async def _get_voice_id(self, character: Dict[str, Any]) -> str:
        """Get or create voice ID for a character"""
        char_name = character['name']
        
        if char_name in self.voice_cache:
            return self.voice_cache[char_name]
        
        # Create voice ID based on character role
        if character.get('role') == 'Protagonist':
            voice_id = "hero_voice"
        elif character.get('role') == 'Antagonist':
            voice_id = "villain_voice"
        else:
            voice_id = f"{char_name.lower()}_voice"
        
        self.voice_cache[char_name] = voice_id
        return voice_id
    
    def _determine_music_style(self, tone: str, themes: List[str]) -> str:
        """Determine background music style based on movie tone and themes"""
        if 'action' in themes or 'adventure' in themes:
            return 'epic_action'
        elif 'romance' in themes or 'love' in themes:
            return 'romantic_dramatic'
        elif 'horror' in themes or 'thriller' in themes:
            return 'suspense_horror'
        elif 'comedy' in themes:
            return 'light_comedy'
        else:
            return 'dramatic_orchestral'
    
    async def _combine_voice_segments(self, voice_segments: List[bytes]) -> bytes:
        """Combine multiple voice segments into one audio"""
        # Simple concatenation (can be improved with proper audio mixing)
        combined = b"".join(voice_segments)
        return combined
    
    async def _save_audio_file(self, audio_data: bytes, file_path: str):
        """Save audio data to file"""
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(audio_data)
        except Exception as e:
            logger.error(f"Error saving audio file: {e}")
    
    async def _calculate_total_duration(self, audio_files: List[str]) -> float:
        """Calculate total duration of all audio files"""
        # Placeholder - would use proper audio library
        return len(audio_files) * 12.0  # Assume 12 seconds per part
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_name": "voice_audio",
            "status": "healthy",
            "voice_provider": self.voice_provider,
            "voice_cache_size": len(self.voice_cache)
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up Voice + Audio Agent...")
        
        if self.session:
            await self.session.close()
        
        logger.info("Voice + Audio Agent cleanup completed")


class ElevenLabsProvider:
    """Provider for ElevenLabs voice generation"""
    
    def __init__(self, session: aiohttp.ClientSession, api_key: Optional[str]):
        self.session = session
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
    
    async def generate_voice(self, text: str, voice_id: str) -> bytes:
        """Generate voice using ElevenLabs API"""
        if not self.api_key:
            return b""
        
        try:
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            async with self.session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    logger.error(f"ElevenLabs API error: {response.status}")
                    return b""
                    
        except Exception as e:
            logger.error(f"Error with ElevenLabs: {e}")
            return b""


class BarkProvider:
    """Provider for Bark voice generation"""
    
    def __init__(self, session: aiohttp.ClientSession, api_key: Optional[str]):
        self.session = session
        self.api_key = api_key
    
    async def generate_voice(self, text: str, voice_id: str) -> bytes:
        """Generate voice using Bark"""
        # Bark implementation would go here
        # For now, return placeholder
        return b""


class RVCProvider:
    """Provider for RVC voice cloning"""
    
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
    
    async def generate_voice(self, text: str, voice_id: str) -> bytes:
        """Generate voice using RVC"""
        # RVC implementation would go here
        # For now, return placeholder
        return b""


class BoomyProvider:
    """Provider for Boomy music generation"""
    
    def __init__(self, session: aiohttp.ClientSession, api_key: Optional[str]):
        self.session = session
        self.api_key = api_key
    
    async def generate_music(self, style: str) -> bytes:
        """Generate music using Boomy"""
        # Boomy implementation would go here
        # For now, return placeholder
        return b""


class SunoProvider:
    """Provider for Suno music generation"""
    
    def __init__(self, session: aiohttp.ClientSession, api_key: Optional[str]):
        self.session = session
        self.api_key = api_key
    
    async def generate_music(self, style: str) -> bytes:
        """Generate music using Suno"""
        # Suno implementation would go here
        # For now, return placeholder
        return b""


class YouTubeMusicProvider:
    """Provider for YouTube free music"""
    
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
    
    async def get_music(self, style: str) -> bytes:
        """Get free music from YouTube"""
        # YouTube music implementation would go here
        # For now, return placeholder
        return b"" 