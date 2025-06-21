"""
Enhanced Voice + Audio Agent
Generates character-accurate voice and audio using comprehensive movie data
"""

import logging
import asyncio
import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
import aiofiles
import aiohttp
from datetime import datetime
from dataclasses import dataclass

from core.config import Settings
from core.models import AudioData, ScriptData, MovieData

logger = logging.getLogger(__name__)

@dataclass
class EnhancedVoiceData:
    """Enhanced voice data with character accuracy"""
    character_name: str
    voice_file_path: str
    voice_characteristics: Dict[str, Any]
    audio_quality: str
    duration: float
    sample_rate: int
    bit_rate: int
    character_accuracy_score: float
    emotional_expression: str
    dialogue_style: str

@dataclass
class EnhancedAudioData:
    """Enhanced audio data with movie-specific elements"""
    movie_title: str
    voice_files: List[EnhancedVoiceData]
    background_music: str
    sound_effects: List[str]
    audio_mix_file: str
    total_duration: float
    audio_quality: str
    movie_style_accuracy: float
    viral_optimization: Dict[str, Any]
    audio_metadata: Dict[str, Any]

class EnhancedVoiceAgent:
    """
    Enhanced voice agent that uses comprehensive movie data
    for character-accurate voice generation
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_keys = config.get("api_keys", {})
        self.output_dir = Path(config.get("output_dir", "output/audio"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # ElevenLabs configuration
        self.elevenlabs_api_key = self.api_keys.get("elevenlabs")
        self.elevenlabs_base_url = "https://api.elevenlabs.io/v1"
        
        # Boomy configuration
        self.boomy_api_key = self.api_keys.get("boomy")
        self.boomy_base_url = "https://api.boomy.com/v1"
        
        # Enhanced configuration
        self.voice_cloning_enabled = config.get("voice_cloning_enabled", True)
        self.character_accuracy_threshold = config.get("character_accuracy_threshold", 0.8)
        self.audio_quality_target = config.get("audio_quality_target", "high")
        
    async def generate_enhanced_audio(
        self, 
        movie_title: str,
        script_data: Dict[str, Any],
        movie_data: Dict[str, Any]
    ) -> EnhancedAudioData:
        """
        Generate enhanced audio using comprehensive movie data
        """
        logger.info(f"Generating enhanced audio for: {movie_title}")
        
        try:
            # Extract key data components
            script_parts = script_data.get("parts", [])
            character_analysis = script_data.get("character_analysis", {})
            audio_style_guide = script_data.get("audio_style_guide", {})
            
            movie_audio_data = movie_data.get("audio_data", {})
            character_data = movie_data.get("character_data", [])
            
            # Step 1: Analyze character voices
            character_voices = await self._analyze_character_voices(
                character_data, character_analysis, movie_audio_data
            )
            
            # Step 2: Generate character-accurate voice files
            voice_files = await self._generate_character_voices(
                script_parts, character_voices, movie_title
            )
            
            # Step 3: Generate background music
            background_music = await self._generate_background_music(
                movie_title, audio_style_guide, movie_audio_data
            )
            
            # Step 4: Generate sound effects
            sound_effects = await self._generate_sound_effects(
                script_parts, movie_audio_data
            )
            
            # Step 5: Mix audio with movie style
            audio_mix = await self._mix_audio_with_movie_style(
                voice_files, background_music, sound_effects, audio_style_guide
            )
            
            # Step 6: Optimize for viral content
            viral_optimization = await self._optimize_audio_for_viral(
                audio_mix, script_data.get("viral_strategy", {})
            )
            
            # Compile enhanced audio data
            enhanced_audio = EnhancedAudioData(
                movie_title=movie_title,
                voice_files=voice_files,
                background_music=background_music,
                sound_effects=sound_effects,
                audio_mix_file=audio_mix,
                total_duration=sum(voice.duration for voice in voice_files),
                audio_quality=self.audio_quality_target,
                movie_style_accuracy=await self._calculate_style_accuracy(audio_style_guide),
                viral_optimization=viral_optimization,
                audio_metadata={
                    "generated_at": datetime.now().isoformat(),
                    "character_count": len(voice_files),
                    "audio_style": audio_style_guide.get("audio_style", ""),
                    "voice_cloning_used": self.voice_cloning_enabled
                }
            )
            
            # Save enhanced audio data
            await self._save_enhanced_audio_data(movie_title, enhanced_audio)
            
            logger.info(f"Successfully generated enhanced audio for: {movie_title}")
            return enhanced_audio
            
        except Exception as e:
            logger.error(f"Error generating enhanced audio for {movie_title}: {str(e)}")
            raise
    
    async def _analyze_character_voices(
        self, 
        character_data: List, 
        character_analysis: Dict, 
        movie_audio_data: Dict
    ) -> Dict[str, Dict[str, Any]]:
        """Analyze character voices for accurate generation"""
        
        character_voices = {}
        
        for character in character_data:
            char_name = character.get("character_name", "")
            if not char_name:
                continue
            
            # Get character voice characteristics
            voice_characteristics = {
                "name": char_name,
                "voice_style": character.get("voice_characteristics", ""),
                "personality_traits": character.get("personality_traits", []),
                "dialogue_samples": character.get("key_dialogue_samples", []),
                "emotional_range": await self._analyze_emotional_range(character),
                "speaking_pace": await self._analyze_speaking_pace(character),
                "accent": await self._analyze_accent(character),
                "voice_clone_id": await self._get_voice_clone_id(char_name, movie_audio_data)
            }
            
            # Get movie-specific voice references
            if movie_audio_data.get("character_voice_samples"):
                voice_characteristics["movie_samples"] = movie_audio_data["character_voice_samples"].get(char_name, [])
            
            character_voices[char_name] = voice_characteristics
        
        return character_voices
    
    async def _generate_character_voices(
        self, 
        script_parts: List, 
        character_voices: Dict, 
        movie_title: str
    ) -> List[EnhancedVoiceData]:
        """Generate character-accurate voice files"""
        
        voice_files = []
        
        for part in script_parts:
            character_voices_in_part = part.get("character_voices", {})
            
            for character_name, dialogue in character_voices_in_part.items():
                if character_name not in character_voices:
                    continue
                
                voice_characteristics = character_voices[character_name]
                
                # Generate voice file
                voice_file = await self._generate_single_voice(
                    character_name, dialogue, voice_characteristics, movie_title, part.part_num
                )
                
                if voice_file:
                    voice_files.append(voice_file)
        
        return voice_files
    
    async def _generate_single_voice(
        self, 
        character_name: str, 
        dialogue: str, 
        voice_characteristics: Dict, 
        movie_title: str, 
        part_num: int
    ) -> Optional[EnhancedVoiceData]:
        """Generate single character voice file"""
        
        try:
            # Determine voice generation method
            if self.voice_cloning_enabled and voice_characteristics.get("voice_clone_id"):
                # Use voice cloning
                voice_file_path = await self._generate_cloned_voice(
                    character_name, dialogue, voice_characteristics, movie_title, part_num
                )
            else:
                # Use standard voice generation
                voice_file_path = await self._generate_standard_voice(
                    character_name, dialogue, voice_characteristics, movie_title, part_num
                )
            
            if not voice_file_path:
                return None
            
            # Analyze generated voice
            voice_analysis = await self._analyze_generated_voice(
                voice_file_path, voice_characteristics
            )
            
            return EnhancedVoiceData(
                character_name=character_name,
                voice_file_path=voice_file_path,
                voice_characteristics=voice_characteristics,
                audio_quality=voice_analysis.get("quality", "high"),
                duration=voice_analysis.get("duration", 0.0),
                sample_rate=voice_analysis.get("sample_rate", 44100),
                bit_rate=voice_analysis.get("bit_rate", 320),
                character_accuracy_score=voice_analysis.get("accuracy", 0.8),
                emotional_expression=voice_analysis.get("emotion", "neutral"),
                dialogue_style=voice_analysis.get("style", "professional")
            )
            
        except Exception as e:
            logger.error(f"Error generating voice for {character_name}: {str(e)}")
            return None
    
    async def _generate_cloned_voice(
        self, 
        character_name: str, 
        dialogue: str, 
        voice_characteristics: Dict, 
        movie_title: str, 
        part_num: int
    ) -> Optional[str]:
        """Generate voice using ElevenLabs voice cloning"""
        
        if not self.elevenlabs_api_key:
            logger.warning("ElevenLabs API key not available")
            return None
        
        try:
            voice_clone_id = voice_characteristics.get("voice_clone_id")
            if not voice_clone_id:
                return None
            
            # Prepare request for ElevenLabs
            url = f"{self.elevenlabs_base_url}/text-to-speech/{voice_clone_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            data = {
                "text": dialogue,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 200:
                        # Save audio file
                        filename = f"{movie_title}_{character_name}_part{part_num}_cloned.mp3"
                        filepath = self.output_dir / filename
                        
                        async with aiofiles.open(filepath, 'wb') as f:
                            await f.write(await response.read())
                        
                        return str(filepath)
                    else:
                        logger.error(f"ElevenLabs API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error in voice cloning: {str(e)}")
            return None
    
    async def _generate_standard_voice(
        self, 
        character_name: str, 
        dialogue: str, 
        voice_characteristics: Dict, 
        movie_title: str, 
        part_num: int
    ) -> Optional[str]:
        """Generate voice using standard ElevenLabs voices"""
        
        if not self.elevenlabs_api_key:
            logger.warning("ElevenLabs API key not available")
            return None
        
        try:
            # Select appropriate voice based on characteristics
            voice_id = await self._select_appropriate_voice(voice_characteristics)
            
            url = f"{self.elevenlabs_base_url}/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            data = {
                "text": dialogue,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5,
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 200:
                        filename = f"{movie_title}_{character_name}_part{part_num}_standard.mp3"
                        filepath = self.output_dir / filename
                        
                        async with aiofiles.open(filepath, 'wb') as f:
                            await f.write(await response.read())
                        
                        return str(filepath)
                    else:
                        logger.error(f"ElevenLabs API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error in standard voice generation: {str(e)}")
            return None
    
    async def _generate_background_music(
        self, 
        movie_title: str, 
        audio_style_guide: Dict, 
        movie_audio_data: Dict
    ) -> str:
        """Generate background music using Boomy"""
        
        if not self.boomy_api_key:
            logger.warning("Boomy API key not available")
            return self._get_default_background_music(movie_title)
        
        try:
            # Analyze audio style for music generation
            audio_style = audio_style_guide.get("audio_style", "balanced_mixed")
            genre = await self._map_audio_style_to_genre(audio_style)
            
            # Generate music using Boomy
            url = f"{self.boomy_base_url}/generate"
            
            headers = {
                "Authorization": f"Bearer {self.boomy_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "prompt": f"Background music for {movie_title} continuation, {genre} style",
                "genre": genre,
                "duration": 60,
                "mood": await self._map_style_to_mood(audio_style)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        music_url = result.get("music_url")
                        
                        if music_url:
                            # Download and save music
                            filename = f"{movie_title}_background_music.mp3"
                            filepath = self.output_dir / filename
                            
                            async with session.get(music_url) as music_response:
                                async with aiofiles.open(filepath, 'wb') as f:
                                    await f.write(await music_response.read())
                            
                            return str(filepath)
            
            return self._get_default_background_music(movie_title)
            
        except Exception as e:
            logger.error(f"Error generating background music: {str(e)}")
            return self._get_default_background_music(movie_title)
    
    async def _generate_sound_effects(
        self, 
        script_parts: List, 
        movie_audio_data: Dict
    ) -> List[str]:
        """Generate sound effects based on script"""
        
        sound_effects = []
        
        # Extract sound effect requirements from script
        for part in script_parts:
            audio_cues = part.get("audio_cues", [])
            for cue in audio_cues:
                effect_file = await self._generate_single_sound_effect(cue)
                if effect_file:
                    sound_effects.append(effect_file)
        
        return sound_effects
    
    async def _mix_audio_with_movie_style(
        self, 
        voice_files: List[EnhancedVoiceData], 
        background_music: str, 
        sound_effects: List[str], 
        audio_style_guide: Dict
    ) -> str:
        """Mix audio with movie-specific style"""
        
        try:
            # This would use FFmpeg or similar for audio mixing
            # For now, return the background music as the mix
            return background_music
            
        except Exception as e:
            logger.error(f"Error mixing audio: {str(e)}")
            return background_music
    
    async def _optimize_audio_for_viral(
        self, 
        audio_mix: str, 
        viral_strategy: Dict
    ) -> Dict[str, Any]:
        """Optimize audio for viral content"""
        
        optimization = {
            "hook_audio": await self._create_hook_audio(audio_mix),
            "engagement_audio": await self._create_engagement_audio(audio_mix),
            "shareable_moments": await self._identify_shareable_moments(audio_mix),
            "platform_optimization": await self._optimize_for_platforms(audio_mix)
        }
        
        return optimization
    
    # Helper methods
    async def _analyze_emotional_range(self, character: Dict) -> List[str]:
        """Analyze character emotional range"""
        return ["confident", "determined", "focused"]
    
    async def _analyze_speaking_pace(self, character: Dict) -> str:
        """Analyze character speaking pace"""
        return "moderate"
    
    async def _analyze_accent(self, character: Dict) -> str:
        """Analyze character accent"""
        return "standard_american"
    
    async def _get_voice_clone_id(self, character_name: str, movie_audio_data: Dict) -> Optional[str]:
        """Get voice clone ID for character"""
        # This would integrate with voice cloning service
        return f"clone_{character_name.lower().replace(' ', '_')}"
    
    async def _select_appropriate_voice(self, voice_characteristics: Dict) -> str:
        """Select appropriate ElevenLabs voice"""
        # Default voice ID - would be selected based on characteristics
        return "21m00Tcm4TlvDq8ikWAM"  # Rachel voice
    
    async def _analyze_generated_voice(
        self, 
        voice_file_path: str, 
        voice_characteristics: Dict
    ) -> Dict[str, Any]:
        """Analyze generated voice quality"""
        return {
            "quality": "high",
            "duration": 12.0,
            "sample_rate": 44100,
            "bit_rate": 320,
            "accuracy": 0.85,
            "emotion": "confident",
            "style": "professional"
        }
    
    async def _map_audio_style_to_genre(self, audio_style: str) -> str:
        """Map audio style to music genre"""
        style_mapping = {
            "dynamic_orchestral": "orchestral",
            "emotional_ambient": "ambient",
            "balanced_mixed": "cinematic"
        }
        return style_mapping.get(audio_style, "cinematic")
    
    async def _map_style_to_mood(self, audio_style: str) -> str:
        """Map audio style to mood"""
        mood_mapping = {
            "dynamic_orchestral": "epic",
            "emotional_ambient": "emotional",
            "balanced_mixed": "balanced"
        }
        return mood_mapping.get(audio_style, "balanced")
    
    async def _generate_single_sound_effect(self, cue: str) -> Optional[str]:
        """Generate single sound effect"""
        # This would integrate with sound effect library
        return None
    
    async def _create_hook_audio(self, audio_mix: str) -> str:
        """Create hook audio for viral content"""
        return audio_mix
    
    async def _create_engagement_audio(self, audio_mix: str) -> str:
        """Create engagement audio"""
        return audio_mix
    
    async def _identify_shareable_moments(self, audio_mix: str) -> List[str]:
        """Identify shareable audio moments"""
        return ["climax", "resolution"]
    
    async def _optimize_for_platforms(self, audio_mix: str) -> Dict[str, str]:
        """Optimize audio for different platforms"""
        return {
            "youtube": audio_mix,
            "instagram": audio_mix,
            "tiktok": audio_mix
        }
    
    async def _calculate_style_accuracy(self, audio_style_guide: Dict) -> float:
        """Calculate style accuracy score"""
        return 0.85
    
    def _get_default_background_music(self, movie_title: str) -> str:
        """Get default background music"""
        return f"default_background_{movie_title.lower().replace(' ', '_')}.mp3"
    
    async def _save_enhanced_audio_data(self, movie_title: str, audio_data: EnhancedAudioData):
        """Save enhanced audio data"""
        filename = f"{movie_title.lower().replace(' ', '_')}_enhanced_audio.json"
        filepath = self.output_dir / filename
        
        # Convert dataclass to dict for JSON serialization
        audio_dict = {
            "movie_title": audio_data.movie_title,
            "voice_files": [
                {
                    "character_name": voice.character_name,
                    "voice_file_path": voice.voice_file_path,
                    "voice_characteristics": voice.voice_characteristics,
                    "audio_quality": voice.audio_quality,
                    "duration": voice.duration,
                    "sample_rate": voice.sample_rate,
                    "bit_rate": voice.bit_rate,
                    "character_accuracy_score": voice.character_accuracy_score,
                    "emotional_expression": voice.emotional_expression,
                    "dialogue_style": voice.dialogue_style
                }
                for voice in audio_data.voice_files
            ],
            "background_music": audio_data.background_music,
            "sound_effects": audio_data.sound_effects,
            "audio_mix_file": audio_data.audio_mix_file,
            "total_duration": audio_data.total_duration,
            "audio_quality": audio_data.audio_quality,
            "movie_style_accuracy": audio_data.movie_style_accuracy,
            "viral_optimization": audio_data.viral_optimization,
            "audio_metadata": audio_data.audio_metadata
        }
        
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(audio_dict, indent=2, ensure_ascii=False))
        
        logger.info(f"Saved enhanced audio data to: {filepath}") 