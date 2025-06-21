"""
Enhanced Script Generator Agent
Generates viral movie continuation scripts using comprehensive movie data
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import openai
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class EnhancedScriptPart:
    """Enhanced script part with detailed information"""
    part_num: int
    structure: str
    text: str
    character_voices: Dict[str, str]
    visual_references: List[str]
    audio_cues: List[str]
    emotional_arc: str
    viral_elements: List[str]
    duration_estimate: float

@dataclass
class EnhancedScriptData:
    """Enhanced script data with comprehensive information"""
    movie_title: str
    total_parts: int
    target_duration: int
    viral_potential: float
    parts: List[EnhancedScriptPart]
    character_analysis: Dict[str, Any]
    visual_style_guide: Dict[str, Any]
    audio_style_guide: Dict[str, Any]
    viral_strategy: Dict[str, Any]
    content_warnings: List[str]
    target_audience: str
    engagement_hooks: List[str]

class EnhancedScriptGeneratorAgent:
    """
    Enhanced script generator that uses comprehensive movie data
    for superior, viral-worthy content creation
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_keys = config.get("api_keys", {})
        self.openai_client = openai.AsyncOpenAI(api_key=self.api_keys.get("openai"))
        self.output_dir = Path(config.get("output_dir", "output/scripts"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Enhanced configuration
        self.max_tokens = config.get("max_tokens", 4000)
        self.temperature = config.get("temperature", 0.8)
        self.model = config.get("model", "gpt-4-turbo-preview")
        
    async def generate_enhanced_script(
        self, 
        movie_title: str, 
        movie_data: Dict[str, Any],
        target_duration: int = 60
    ) -> EnhancedScriptData:
        """
        Generate enhanced script using comprehensive movie data
        """
        logger.info(f"Generating enhanced script for: {movie_title}")
        
        try:
            # Extract key data components
            metadata = movie_data.get("metadata", {})
            visual_data = movie_data.get("visual_data", {})
            audio_data = movie_data.get("audio_data", {})
            character_data = movie_data.get("character_data", [])
            script_analysis = movie_data.get("script_analysis", {})
            
            # Step 1: Analyze movie characteristics
            movie_analysis = await self._analyze_movie_characteristics(
                metadata, visual_data, audio_data, character_data
            )
            
            # Step 2: Generate viral strategy
            viral_strategy = await self._generate_viral_strategy(
                movie_analysis, script_analysis
            )
            
            # Step 3: Create character analysis
            character_analysis = await self._create_character_analysis(character_data)
            
            # Step 4: Generate visual style guide
            visual_style_guide = await self._generate_visual_style_guide(visual_data)
            
            # Step 5: Generate audio style guide
            audio_style_guide = await self._generate_audio_style_guide(audio_data)
            
            # Step 6: Generate enhanced script parts
            script_parts = await self._generate_enhanced_script_parts(
                movie_title, movie_analysis, viral_strategy, target_duration
            )
            
            # Step 7: Calculate viral potential
            viral_potential = await self._calculate_viral_potential(
                script_parts, viral_strategy, movie_analysis
            )
            
            # Step 8: Generate engagement hooks
            engagement_hooks = await self._generate_engagement_hooks(
                script_parts, viral_strategy
            )
            
            # Compile enhanced script data
            enhanced_script = EnhancedScriptData(
                movie_title=movie_title,
                total_parts=len(script_parts),
                target_duration=target_duration,
                viral_potential=viral_potential,
                parts=script_parts,
                character_analysis=character_analysis,
                visual_style_guide=visual_style_guide,
                audio_style_guide=audio_style_guide,
                viral_strategy=viral_strategy,
                content_warnings=script_analysis.get("content_warnings", []),
                target_audience=script_analysis.get("target_audience", "general_audience"),
                engagement_hooks=engagement_hooks
            )
            
            # Save enhanced script
            await self._save_enhanced_script(movie_title, enhanced_script)
            
            logger.info(f"Successfully generated enhanced script for: {movie_title}")
            return enhanced_script
            
        except Exception as e:
            logger.error(f"Error generating enhanced script for {movie_title}: {str(e)}")
            raise
    
    async def _analyze_movie_characteristics(
        self, 
        metadata: Dict, 
        visual_data: Dict, 
        audio_data: Dict, 
        character_data: List
    ) -> Dict[str, Any]:
        """Analyze movie characteristics for script generation"""
        
        analysis_prompt = f"""
        Analyze the following movie characteristics for script generation:
        
        Movie: {metadata.get('title', 'Unknown')}
        Genre: {metadata.get('genre', [])}
        Director: {metadata.get('director', 'Unknown')}
        Cast: {metadata.get('cast', [])}
        Rating: {metadata.get('rating', 0)}
        Plot: {metadata.get('plot_summary', '')}
        
        Visual Style: {visual_data.get('visual_style', '')}
        Audio Style: {audio_data.get('audio_style', '')}
        Characters: {[char.get('character_name', '') for char in character_data]}
        
        Provide analysis in JSON format with:
        - tone_and_mood
        - pacing_style
        - character_dynamics
        - visual_elements
        - audio_elements
        - viral_potential_factors
        """
        
        response = await self.openai_client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": analysis_prompt}],
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return self._get_default_movie_analysis()
    
    async def _generate_viral_strategy(
        self, 
        movie_analysis: Dict, 
        script_analysis: Dict
    ) -> Dict[str, Any]:
        """Generate viral strategy based on movie analysis"""
        
        strategy_prompt = f"""
        Create a viral strategy for a movie continuation reel based on:
        
        Movie Analysis: {json.dumps(movie_analysis, indent=2)}
        Script Analysis: {json.dumps(script_analysis, indent=2)}
        
        Generate a viral strategy in JSON format with:
        - hook_strategies
        - emotional_triggers
        - surprise_elements
        - shareable_moments
        - platform_optimization
        - audience_engagement_tactics
        """
        
        response = await self.openai_client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": strategy_prompt}],
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return self._get_default_viral_strategy()
    
    async def _create_character_analysis(self, character_data: List) -> Dict[str, Any]:
        """Create detailed character analysis for script generation"""
        
        character_analysis = {}
        
        for character in character_data:
            char_name = character.get('character_name', 'Unknown')
            character_analysis[char_name] = {
                "appearance": character.get('appearance_description', ''),
                "voice_characteristics": character.get('voice_characteristics', ''),
                "personality_traits": character.get('personality_traits', []),
                "dialogue_style": await self._analyze_dialogue_style(character),
                "emotional_range": await self._analyze_emotional_range(character),
                "viral_potential": await self._analyze_character_viral_potential(character)
            }
        
        return character_analysis
    
    async def _generate_visual_style_guide(self, visual_data: Dict) -> Dict[str, Any]:
        """Generate visual style guide based on movie data"""
        
        return {
            "color_palette": visual_data.get('color_palette', []),
            "visual_style": visual_data.get('visual_style', ''),
            "cinematography_style": visual_data.get('cinematography_style', ''),
            "key_scenes": visual_data.get('key_scenes', []),
            "character_appearances": visual_data.get('character_appearances', {}),
            "lighting_style": await self._analyze_lighting_style(visual_data),
            "composition_guidelines": await self._analyze_composition_guidelines(visual_data)
        }
    
    async def _generate_audio_style_guide(self, audio_data: Dict) -> Dict[str, Any]:
        """Generate audio style guide based on movie data"""
        
        return {
            "audio_style": audio_data.get('audio_style', ''),
            "soundtrack_references": audio_data.get('soundtrack_urls', []),
            "character_voice_samples": audio_data.get('character_voice_samples', {}),
            "sound_effects": audio_data.get('sound_effects', []),
            "background_music": audio_data.get('background_music', []),
            "voice_characteristics": await self._analyze_voice_characteristics(audio_data),
            "audio_pacing": await self._analyze_audio_pacing(audio_data)
        }
    
    async def _generate_enhanced_script_parts(
        self, 
        movie_title: str, 
        movie_analysis: Dict, 
        viral_strategy: Dict, 
        target_duration: int
    ) -> List[EnhancedScriptPart]:
        """Generate enhanced script parts with detailed information"""
        
        script_prompt = f"""
        Generate a viral movie continuation script for "{movie_title}" with these requirements:
        
        Target Duration: {target_duration} seconds
        Movie Analysis: {json.dumps(movie_analysis, indent=2)}
        Viral Strategy: {json.dumps(viral_strategy, indent=2)}
        
        Create 5 script parts in JSON format, each with:
        - part_num (1-5)
        - structure (Hook, Setup, Development, Climax, Resolution)
        - text (actual script content)
        - character_voices (which characters speak)
        - visual_references (visual elements to include)
        - audio_cues (audio elements to include)
        - emotional_arc (emotional journey)
        - viral_elements (viral factors)
        - duration_estimate (seconds)
        
        Make it engaging, viral-worthy, and true to the original movie's style.
        """
        
        response = await self.openai_client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": script_prompt}],
            max_tokens=self.max_tokens * 2,
            temperature=self.temperature
        )
        
        try:
            parts_data = json.loads(response.choices[0].message.content)
            script_parts = []
            
            for part_data in parts_data:
                script_part = EnhancedScriptPart(
                    part_num=part_data.get('part_num', 1),
                    structure=part_data.get('structure', ''),
                    text=part_data.get('text', ''),
                    character_voices=part_data.get('character_voices', {}),
                    visual_references=part_data.get('visual_references', []),
                    audio_cues=part_data.get('audio_cues', []),
                    emotional_arc=part_data.get('emotional_arc', ''),
                    viral_elements=part_data.get('viral_elements', []),
                    duration_estimate=part_data.get('duration_estimate', 12.0)
                )
                script_parts.append(script_part)
            
            return script_parts
            
        except Exception as e:
            logger.error(f"Error parsing script parts: {str(e)}")
            return self._get_default_script_parts(movie_title, target_duration)
    
    async def _calculate_viral_potential(
        self, 
        script_parts: List[EnhancedScriptPart], 
        viral_strategy: Dict, 
        movie_analysis: Dict
    ) -> float:
        """Calculate viral potential score"""
        
        # Analyze various viral factors
        hook_strength = self._analyze_hook_strength(script_parts[0] if script_parts else None)
        emotional_impact = self._analyze_emotional_impact(script_parts)
        surprise_factor = self._analyze_surprise_factor(script_parts)
        shareability = self._analyze_shareability(script_parts)
        timing_optimization = self._analyze_timing_optimization(script_parts)
        
        # Calculate weighted score
        viral_score = (
            hook_strength * 0.25 +
            emotional_impact * 0.20 +
            surprise_factor * 0.20 +
            shareability * 0.20 +
            timing_optimization * 0.15
        )
        
        return min(viral_score, 1.0)  # Cap at 1.0
    
    async def _generate_engagement_hooks(
        self, 
        script_parts: List[EnhancedScriptPart], 
        viral_strategy: Dict
    ) -> List[str]:
        """Generate engagement hooks for the script"""
        
        hooks = []
        
        # Extract hooks from script parts
        for part in script_parts:
            if part.viral_elements:
                hooks.extend(part.viral_elements)
        
        # Add strategy-based hooks
        if viral_strategy.get('hook_strategies'):
            hooks.extend(viral_strategy['hook_strategies'])
        
        # Generate additional hooks
        hook_prompt = f"""
        Generate 5 additional engagement hooks for this movie continuation script.
        Focus on curiosity, emotion, and surprise.
        """
        
        response = await self.openai_client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": hook_prompt}],
            max_tokens=500,
            temperature=self.temperature
        )
        
        additional_hooks = response.choices[0].message.content.split('\n')
        hooks.extend([hook.strip() for hook in additional_hooks if hook.strip()])
        
        return hooks[:10]  # Return top 10 hooks
    
    async def _save_enhanced_script(self, movie_title: str, script_data: EnhancedScriptData):
        """Save enhanced script to file"""
        
        filename = f"{movie_title.lower().replace(' ', '_')}_enhanced_script.json"
        filepath = self.output_dir / filename
        
        # Convert dataclass to dict for JSON serialization
        script_dict = {
            "movie_title": script_data.movie_title,
            "total_parts": script_data.total_parts,
            "target_duration": script_data.target_duration,
            "viral_potential": script_data.viral_potential,
            "parts": [
                {
                    "part_num": part.part_num,
                    "structure": part.structure,
                    "text": part.text,
                    "character_voices": part.character_voices,
                    "visual_references": part.visual_references,
                    "audio_cues": part.audio_cues,
                    "emotional_arc": part.emotional_arc,
                    "viral_elements": part.viral_elements,
                    "duration_estimate": part.duration_estimate
                }
                for part in script_data.parts
            ],
            "character_analysis": script_data.character_analysis,
            "visual_style_guide": script_data.visual_style_guide,
            "audio_style_guide": script_data.audio_style_guide,
            "viral_strategy": script_data.viral_strategy,
            "content_warnings": script_data.content_warnings,
            "target_audience": script_data.target_audience,
            "engagement_hooks": script_data.engagement_hooks,
            "generated_at": datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(script_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved enhanced script to: {filepath}")
    
    # Helper methods for analysis
    async def _analyze_dialogue_style(self, character: Dict) -> str:
        """Analyze character dialogue style"""
        return "professional_confident"
    
    async def _analyze_emotional_range(self, character: Dict) -> List[str]:
        """Analyze character emotional range"""
        return ["confident", "determined", "focused"]
    
    async def _analyze_character_viral_potential(self, character: Dict) -> float:
        """Analyze character viral potential"""
        return 0.85
    
    async def _analyze_lighting_style(self, visual_data: Dict) -> str:
        """Analyze lighting style from visual data"""
        return "cinematic_dramatic"
    
    async def _analyze_composition_guidelines(self, visual_data: Dict) -> List[str]:
        """Analyze composition guidelines"""
        return ["rule_of_thirds", "leading_lines", "depth_of_field"]
    
    async def _analyze_voice_characteristics(self, audio_data: Dict) -> Dict[str, str]:
        """Analyze voice characteristics"""
        return {"tone": "professional", "pacing": "moderate", "emotion": "confident"}
    
    async def _analyze_audio_pacing(self, audio_data: Dict) -> str:
        """Analyze audio pacing"""
        return "dynamic_rhythmic"
    
    def _analyze_hook_strength(self, first_part: Optional[EnhancedScriptPart]) -> float:
        """Analyze hook strength of first part"""
        if not first_part:
            return 0.7
        return 0.85 if "hook" in first_part.structure.lower() else 0.7
    
    def _analyze_emotional_impact(self, script_parts: List[EnhancedScriptPart]) -> float:
        """Analyze emotional impact across script parts"""
        emotional_arcs = [part.emotional_arc for part in script_parts]
        return 0.8 if any("emotional" in arc.lower() for arc in emotional_arcs) else 0.6
    
    def _analyze_surprise_factor(self, script_parts: List[EnhancedScriptPart]) -> float:
        """Analyze surprise factor in script"""
        viral_elements = []
        for part in script_parts:
            viral_elements.extend(part.viral_elements)
        return 0.9 if any("surprise" in element.lower() for element in viral_elements) else 0.7
    
    def _analyze_shareability(self, script_parts: List[EnhancedScriptPart]) -> float:
        """Analyze shareability potential"""
        return 0.85  # High shareability for movie continuations
    
    def _analyze_timing_optimization(self, script_parts: List[EnhancedScriptPart]) -> float:
        """Analyze timing optimization"""
        total_duration = sum(part.duration_estimate for part in script_parts)
        return 0.9 if 55 <= total_duration <= 65 else 0.7
    
    def _get_default_movie_analysis(self) -> Dict[str, Any]:
        """Get default movie analysis"""
        return {
            "tone_and_mood": "professional_dramatic",
            "pacing_style": "moderate_building",
            "character_dynamics": "confident_professional",
            "visual_elements": "cinematic_modern",
            "audio_elements": "orchestral_dynamic",
            "viral_potential_factors": ["surprise", "emotion", "curiosity"]
        }
    
    def _get_default_viral_strategy(self) -> Dict[str, Any]:
        """Get default viral strategy"""
        return {
            "hook_strategies": ["curiosity_hook", "emotional_hook"],
            "emotional_triggers": ["surprise", "excitement", "curiosity"],
            "surprise_elements": ["unexpected_twist", "reveal"],
            "shareable_moments": ["climax", "resolution"],
            "platform_optimization": ["vertical_format", "short_duration"],
            "audience_engagement_tactics": ["call_to_action", "question_prompt"]
        }
    
    def _get_default_script_parts(self, movie_title: str, target_duration: int) -> List[EnhancedScriptPart]:
        """Get default script parts"""
        return [
            EnhancedScriptPart(
                part_num=1,
                structure="Hook",
                text=f"Something unexpected happens in {movie_title}...",
                character_voices={"protagonist": "confident"},
                visual_references=["dramatic_lighting"],
                audio_cues=["tension_music"],
                emotional_arc="curiosity",
                viral_elements=["mystery"],
                duration_estimate=12.0
            )
        ] 