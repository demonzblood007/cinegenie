"""
Uploader Agent
Uploads reels/shorts to YouTube Shorts and Instagram, generates captions/hashtags, tracks analytics
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import aiofiles

from core.config import Settings
from core.models import UploadResult, VideoData
import openai

logger = logging.getLogger(__name__)

class UploadAgent:
    """Agent responsible for uploading videos and tracking analytics"""
    def __init__(self, settings: Settings):
        self.settings = settings
        self.youtube_api_key = settings.youtube_api_key
        self.upload_results = []

    async def initialize(self):
        logger.info("Initializing Uploader Agent...")
        # Optionally, check API credentials
        logger.info("Uploader Agent initialized.")

    async def upload_content(self, video_data: VideoData, movie_title: str) -> List[UploadResult]:
        logger.info(f"Uploading content for: {movie_title}")
        results = []
        try:
            # Generate captions, hashtags, and title
            captions, hashtags, title = await self._generate_captions_hashtags_title(movie_title, video_data)
            # Upload to YouTube Shorts
            yt_result = await self._upload_to_youtube(video_data, title, captions, hashtags)
            results.append(yt_result)
            # Upload to Instagram Reels
            ig_result = await self._upload_to_instagram(video_data, title, captions, hashtags)
            results.append(ig_result)
            # Track analytics (placeholder)
            await self._track_analytics(results)
            self.upload_results.extend(results)
            logger.info(f"Upload completed for: {movie_title}")
            return results
        except Exception as e:
            logger.error(f"Error uploading content: {e}")
            return [UploadResult(
                platform="unknown",
                status="failed",
                error_message=str(e),
                upload_timestamp=datetime.now()
            )]

    async def _generate_captions_hashtags_title(self, movie_title: str, video_data: VideoData):
        """Generate captions, hashtags, and title using LLM"""
        prompt = (
            f"Generate a viral title, 3 captions, and 10 hashtags for a movie short based on the movie '{movie_title}'. "
            "Make it engaging and optimized for YouTube Shorts and Instagram Reels."
        )
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )
            content = response['choices'][0]['message']['content']
            # Simple parsing (should be improved)
            lines = content.split('\n')
            title = lines[0] if lines else movie_title
            captions = [l for l in lines if l.startswith('Caption') or l.startswith('-')]
            hashtags = [l for l in lines if l.startswith('#')]
            return captions, hashtags, title
        except Exception as e:
            logger.error(f"LLM caption/hashtag generation failed: {e}")
            return ["Watch now!"], ["#movie"], movie_title

    async def _upload_to_youtube(self, video_data: VideoData, title: str, captions: List[str], hashtags: List[str]) -> UploadResult:
        """Upload video to YouTube Shorts (simulate API call)"""
        # Placeholder: Simulate upload
        await asyncio.sleep(1)
        return UploadResult(
            platform="YouTube Shorts",
            video_id="yt12345",
            url="https://youtube.com/shorts/yt12345",
            status="success",
            upload_timestamp=datetime.now(),
            analytics={"views": 0, "likes": 0}
        )

    async def _upload_to_instagram(self, video_data: VideoData, title: str, captions: List[str], hashtags: List[str]) -> UploadResult:
        """Upload video to Instagram Reels (simulate API call)"""
        # Placeholder: Simulate upload
        await asyncio.sleep(1)
        return UploadResult(
            platform="Instagram Reels",
            video_id="ig12345",
            url="https://instagram.com/reel/ig12345",
            status="success",
            upload_timestamp=datetime.now(),
            analytics={"views": 0, "likes": 0}
        )

    async def _track_analytics(self, results: List[UploadResult]):
        """Track analytics for uploaded videos (placeholder)"""
        # Placeholder: Would use YouTube/Instagram APIs
        pass

    async def get_status(self):
        return {"agent_name": "uploader", "status": "healthy", "uploads": len(self.upload_results)}

    async def cleanup(self):
        logger.info("Uploader Agent cleanup completed.") 