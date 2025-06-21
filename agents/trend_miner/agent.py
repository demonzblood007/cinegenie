"""
Trend Mining Agent
Analyzes movie popularity, scrapes reviews, and identifies fan desires
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import aiohttp
import json

from core.config import Settings
from core.models import TrendAnalysis
from agents.trend_miner.scrapers import (
    IMDbScraper, YouTubeScraper, RedditScraper, TwitterScraper
)
from agents.trend_miner.analyzers import SentimentAnalyzer, TrendAnalyzer

logger = logging.getLogger(__name__)


class TrendMiningAgent:
    """Agent responsible for trend analysis and sentiment mining"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.scrapers = {}
        self.analyzers = {}
        self.session = None
        self.cache = {}
        
    async def initialize(self):
        """Initialize the agent and its components"""
        logger.info("Initializing Trend Mining Agent...")
        
        # Initialize HTTP session
        self.session = aiohttp.ClientSession()
        
        # Initialize scrapers
        self.scrapers = {
            'imdb': IMDbScraper(self.session),
            'youtube': YouTubeScraper(self.session, self.settings.youtube_api_key),
            'reddit': RedditScraper(self.session, self.settings.reddit_client_id, self.settings.reddit_client_secret),
            'twitter': TwitterScraper(self.session, self.settings.twitter_api_key, self.settings.twitter_api_secret)
        }
        
        # Initialize analyzers
        self.analyzers = {
            'sentiment': SentimentAnalyzer(),
            'trend': TrendAnalyzer()
        }
        
        logger.info("Trend Mining Agent initialized successfully!")
    
    async def analyze_movie_trends(self, movie_title: str) -> TrendAnalysis:
        """Analyze trends and sentiment for a specific movie"""
        logger.info(f"Analyzing trends for movie: {movie_title}")
        
        try:
            # Check cache first
            cache_key = f"trends_{movie_title.lower().replace(' ', '_')}"
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                if datetime.now() - cached_data['timestamp'] < timedelta(hours=1):
                    logger.info(f"Using cached trend data for {movie_title}")
                    return cached_data['data']
            
            # Step 1: Gather data from multiple sources
            scraped_data = await self._gather_movie_data(movie_title)
            
            # Step 2: Analyze sentiment and trends
            analysis_result = await self._analyze_data(scraped_data, movie_title)
            
            # Step 3: Extract fan desires and viral potential
            fan_insights = await self._extract_fan_insights(scraped_data)
            
            # Step 4: Create comprehensive trend analysis
            trend_analysis = TrendAnalysis(
                movie_title=movie_title,
                popularity_score=analysis_result['popularity_score'],
                social_mentions=analysis_result['social_mentions'],
                review_count=analysis_result['review_count'],
                average_rating=analysis_result['average_rating'],
                sentiment_distribution=analysis_result['sentiment_distribution'],
                trending_topics=analysis_result['trending_topics'],
                fan_desires=fan_insights['desires'],
                most_anticipated_continuations=fan_insights['continuations'],
                viral_potential_score=fan_insights['viral_potential'],
                target_audience=fan_insights['target_audience']
            )
            
            # Cache the result
            self.cache[cache_key] = {
                'data': trend_analysis,
                'timestamp': datetime.now()
            }
            
            logger.info(f"Completed trend analysis for {movie_title}")
            return trend_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing trends for {movie_title}: {e}")
            raise
    
    async def get_trending_movies(self) -> List[Dict[str, Any]]:
        """Get current trending movies across platforms"""
        logger.info("Fetching trending movies...")
        
        try:
            trending_movies = []
            
            # Get trending from multiple sources
            sources = ['imdb', 'youtube', 'reddit']
            
            for source in sources:
                try:
                    if source in self.scrapers:
                        source_trends = await self.scrapers[source].get_trending_movies()
                        trending_movies.extend(source_trends)
                except Exception as e:
                    logger.warning(f"Failed to get trends from {source}: {e}")
            
            # Aggregate and rank trending movies
            ranked_movies = await self._rank_trending_movies(trending_movies)
            
            logger.info(f"Found {len(ranked_movies)} trending movies")
            return ranked_movies[:10]  # Return top 10
            
        except Exception as e:
            logger.error(f"Error getting trending movies: {e}")
            return []
    
    async def _gather_movie_data(self, movie_title: str) -> Dict[str, Any]:
        """Gather movie data from multiple sources"""
        logger.info(f"Gathering data for {movie_title} from multiple sources")
        
        tasks = []
        sources = ['imdb', 'youtube', 'reddit', 'twitter']
        
        for source in sources:
            if source in self.scrapers:
                task = self.scrapers[source].scrape_movie_data(movie_title)
                tasks.append(task)
        
        # Execute all scraping tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        combined_data = {
            'reviews': [],
            'comments': [],
            'ratings': [],
            'mentions': [],
            'metadata': {}
        }
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"Failed to scrape from {sources[i]}: {result}")
                continue
            
            if result:
                combined_data['reviews'].extend(result.get('reviews', []))
                combined_data['comments'].extend(result.get('comments', []))
                combined_data['ratings'].extend(result.get('ratings', []))
                combined_data['mentions'].extend(result.get('mentions', []))
                combined_data['metadata'].update(result.get('metadata', {}))
        
        logger.info(f"Gathered {len(combined_data['reviews'])} reviews and {len(combined_data['comments'])} comments")
        return combined_data
    
    async def _analyze_data(self, scraped_data: Dict[str, Any], movie_title: str) -> Dict[str, Any]:
        """Analyze scraped data for sentiment and trends"""
        logger.info(f"Analyzing data for {movie_title}")
        
        # Analyze sentiment
        sentiment_analysis = await self.analyzers['sentiment'].analyze_batch(
            scraped_data['reviews'] + scraped_data['comments']
        )
        
        # Analyze trends
        trend_analysis = await self.analyzers['trend'].analyze_trends(
            scraped_data, movie_title
        )
        
        return {
            'popularity_score': trend_analysis['popularity_score'],
            'social_mentions': len(scraped_data['mentions']),
            'review_count': len(scraped_data['reviews']),
            'average_rating': sentiment_analysis['average_rating'],
            'sentiment_distribution': sentiment_analysis['distribution'],
            'trending_topics': trend_analysis['topics']
        }
    
    async def _extract_fan_insights(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract fan desires and insights from reviews and comments"""
        logger.info("Extracting fan insights")
        
        # Combine all text data
        all_text = []
        for review in scraped_data['reviews']:
            all_text.append(review.get('text', ''))
        for comment in scraped_data['comments']:
            all_text.append(comment.get('text', ''))
        
        # Use trend analyzer to extract insights
        insights = await self.analyzers['trend'].extract_fan_insights(all_text)
        
        return {
            'desires': insights.get('desires', []),
            'continuations': insights.get('continuations', []),
            'viral_potential': insights.get('viral_potential', 0.0),
            'target_audience': insights.get('target_audience', [])
        }
    
    async def _rank_trending_movies(self, movies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank trending movies by popularity and viral potential"""
        logger.info("Ranking trending movies")
        
        # Calculate scores for each movie
        for movie in movies:
            score = 0.0
            
            # Popularity factors
            if 'rating' in movie:
                score += movie['rating'] * 0.3
            if 'review_count' in movie:
                score += min(movie['review_count'] / 1000, 1.0) * 0.2
            if 'social_mentions' in movie:
                score += min(movie['social_mentions'] / 10000, 1.0) * 0.3
            if 'recent_release' in movie and movie['recent_release']:
                score += 0.2
            
            movie['trending_score'] = score
        
        # Sort by trending score
        ranked_movies = sorted(movies, key=lambda x: x.get('trending_score', 0), reverse=True)
        
        return ranked_movies
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_name": "trend_miner",
            "status": "healthy",
            "last_heartbeat": datetime.now(),
            "cache_size": len(self.cache),
            "scrapers_active": len(self.scrapers),
            "analyzers_active": len(self.analyzers)
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up Trend Mining Agent...")
        
        if self.session:
            await self.session.close()
        
        # Clear cache
        self.cache.clear()
        
        logger.info("Trend Mining Agent cleanup completed") 