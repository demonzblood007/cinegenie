"""
Web scrapers for gathering movie data from various platforms
"""

import asyncio
import logging
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import aiohttp
from bs4 import BeautifulSoup
import json

logger = logging.getLogger(__name__)


class BaseScraper:
    """Base class for all scrapers"""
    
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def scrape_movie_data(self, movie_title: str) -> Dict[str, Any]:
        """Scrape movie data - to be implemented by subclasses"""
        raise NotImplementedError
    
    async def get_trending_movies(self) -> List[Dict[str, Any]]:
        """Get trending movies - to be implemented by subclasses"""
        raise NotImplementedError


class IMDbScraper(BaseScraper):
    """Scraper for IMDb movie data"""
    
    async def scrape_movie_data(self, movie_title: str) -> Dict[str, Any]:
        """Scrape movie data from IMDb"""
        logger.info(f"Scraping IMDb data for: {movie_title}")
        
        try:
            # Search for movie
            search_url = f"https://www.imdb.com/find?q={movie_title.replace(' ', '+')}"
            async with self.session.get(search_url, headers=self.headers) as response:
                if response.status != 200:
                    return {}
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find first movie result
                movie_link = soup.find('a', href=re.compile(r'/title/tt\d+'))
                if not movie_link:
                    return {}
                
                movie_url = f"https://www.imdb.com{movie_link['href']}"
                
                # Get movie page
                async with self.session.get(movie_url, headers=self.headers) as response:
                    if response.status != 200:
                        return {}
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract basic info
                    title = soup.find('h1').text.strip() if soup.find('h1') else movie_title
                    rating_elem = soup.find('span', {'class': 'AggregateRatingButton__RatingScore'})
                    rating = float(rating_elem.text) if rating_elem else 0.0
                    
                    # Get reviews
                    reviews_url = f"{movie_url}/reviews"
                    reviews = await self._scrape_reviews(reviews_url)
                    
                    return {
                        'reviews': reviews,
                        'comments': [],
                        'ratings': [{'rating': rating, 'source': 'imdb'}],
                        'mentions': [],
                        'metadata': {
                            'title': title,
                            'rating': rating,
                            'source': 'imdb'
                        }
                    }
                    
        except Exception as e:
            logger.error(f"Error scraping IMDb for {movie_title}: {e}")
            return {}
    
    async def _scrape_reviews(self, reviews_url: str) -> List[Dict[str, Any]]:
        """Scrape reviews from IMDb"""
        try:
            async with self.session.get(reviews_url, headers=self.headers) as response:
                if response.status != 200:
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                reviews = []
                review_elements = soup.find_all('div', {'class': 'review-container'})
                
                for elem in review_elements[:50]:  # Limit to 50 reviews
                    title_elem = elem.find('a', {'class': 'title'})
                    content_elem = elem.find('div', {'class': 'content'})
                    rating_elem = elem.find('span', {'class': 'rating-other-user-rating'})
                    
                    if title_elem and content_elem:
                        reviews.append({
                            'title': title_elem.text.strip(),
                            'text': content_elem.text.strip(),
                            'rating': float(rating_elem.text) if rating_elem else None,
                            'source': 'imdb'
                        })
                
                return reviews
                
        except Exception as e:
            logger.error(f"Error scraping IMDb reviews: {e}")
            return []
    
    async def get_trending_movies(self) -> List[Dict[str, Any]]:
        """Get trending movies from IMDb"""
        try:
            url = "https://www.imdb.com/chart/moviemeter"
            async with self.session.get(url, headers=self.headers) as response:
                if response.status != 200:
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                movies = []
                movie_elements = soup.find_all('h3', {'class': 'ipc-title__text'})
                
                for elem in movie_elements[:20]:
                    title = elem.text.strip()
                    if title and title != "Rank":
                        movies.append({
                            'title': title,
                            'source': 'imdb',
                            'recent_release': True
                        })
                
                return movies
                
        except Exception as e:
            logger.error(f"Error getting IMDb trending movies: {e}")
            return []


class YouTubeScraper(BaseScraper):
    """Scraper for YouTube movie data"""
    
    def __init__(self, session: aiohttp.ClientSession, api_key: Optional[str] = None):
        super().__init__(session)
        self.api_key = api_key
    
    async def scrape_movie_data(self, movie_title: str) -> Dict[str, Any]:
        """Scrape movie data from YouTube"""
        logger.info(f"Scraping YouTube data for: {movie_title}")
        
        try:
            if not self.api_key:
                return {}
            
            # Search for movie reviews and discussions
            search_query = f"{movie_title} movie review discussion"
            search_url = f"https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'q': search_query,
                'type': 'video',
                'maxResults': 50,
                'key': self.api_key,
                'order': 'relevance'
            }
            
            async with self.session.get(search_url, params=params) as response:
                if response.status != 200:
                    return {}
                
                data = await response.json()
                
                comments = []
                for item in data.get('items', []):
                    video_id = item['id']['videoId']
                    video_comments = await self._get_video_comments(video_id)
                    comments.extend(video_comments)
                
                return {
                    'reviews': [],
                    'comments': comments,
                    'ratings': [],
                    'mentions': [],
                    'metadata': {
                        'title': movie_title,
                        'source': 'youtube',
                        'video_count': len(data.get('items', []))
                    }
                }
                
        except Exception as e:
            logger.error(f"Error scraping YouTube for {movie_title}: {e}")
            return {}
    
    async def _get_video_comments(self, video_id: str) -> List[Dict[str, Any]]:
        """Get comments from a YouTube video"""
        try:
            if not self.api_key:
                return []
            
            url = f"https://www.googleapis.com/youtube/v3/commentThreads"
            params = {
                'part': 'snippet',
                'videoId': video_id,
                'maxResults': 100,
                'key': self.api_key
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    return []
                
                data = await response.json()
                
                comments = []
                for item in data.get('items', []):
                    comment = item['snippet']['topLevelComment']['snippet']
                    comments.append({
                        'text': comment['textDisplay'],
                        'author': comment['authorDisplayName'],
                        'likes': comment['likeCount'],
                        'source': 'youtube'
                    })
                
                return comments
                
        except Exception as e:
            logger.error(f"Error getting YouTube comments: {e}")
            return []
    
    async def get_trending_movies(self) -> List[Dict[str, Any]]:
        """Get trending movie content from YouTube"""
        try:
            if not self.api_key:
                return []
            
            # Search for trending movie content
            search_url = f"https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'q': 'movie review trending',
                'type': 'video',
                'maxResults': 20,
                'key': self.api_key,
                'order': 'viewCount',
                'publishedAfter': (datetime.now() - timedelta(days=7)).isoformat() + 'Z'
            }
            
            async with self.session.get(search_url, params=params) as response:
                if response.status != 200:
                    return []
                
                data = await response.json()
                
                movies = []
                for item in data.get('items', []):
                    title = item['snippet']['title']
                    # Extract movie title from video title
                    movie_title = self._extract_movie_title(title)
                    if movie_title:
                        movies.append({
                            'title': movie_title,
                            'source': 'youtube',
                            'recent_release': True
                        })
                
                return movies
                
        except Exception as e:
            logger.error(f"Error getting YouTube trending movies: {e}")
            return []
    
    def _extract_movie_title(self, video_title: str) -> Optional[str]:
        """Extract movie title from video title"""
        # Simple extraction - look for patterns like "Movie Name Review"
        patterns = [
            r'(.+?)\s+Review',
            r'(.+?)\s+Movie',
            r'(.+?)\s+Film'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, video_title, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None


class RedditScraper(BaseScraper):
    """Scraper for Reddit movie data"""
    
    def __init__(self, session: aiohttp.ClientSession, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        super().__init__(session)
        self.client_id = client_id
        self.client_secret = client_secret
    
    async def scrape_movie_data(self, movie_title: str) -> Dict[str, Any]:
        """Scrape movie data from Reddit"""
        logger.info(f"Scraping Reddit data for: {movie_title}")
        
        try:
            # Search Reddit for movie discussions
            search_query = movie_title.replace(' ', '+')
            url = f"https://www.reddit.com/search.json?q={search_query}&restrict_sr=on&sort=relevance&t=month"
            
            async with self.session.get(url, headers=self.headers) as response:
                if response.status != 200:
                    return {}
                
                data = await response.json()
                
                comments = []
                for post in data.get('data', {}).get('children', []):
                    post_data = post['data']
                    comments.append({
                        'text': post_data.get('title', '') + ' ' + post_data.get('selftext', ''),
                        'author': post_data.get('author', ''),
                        'score': post_data.get('score', 0),
                        'source': 'reddit'
                    })
                
                return {
                    'reviews': [],
                    'comments': comments,
                    'ratings': [],
                    'mentions': [],
                    'metadata': {
                        'title': movie_title,
                        'source': 'reddit',
                        'post_count': len(data.get('data', {}).get('children', []))
                    }
                }
                
        except Exception as e:
            logger.error(f"Error scraping Reddit for {movie_title}: {e}")
            return {}
    
    async def get_trending_movies(self) -> List[Dict[str, Any]]:
        """Get trending movies from Reddit"""
        try:
            # Get trending from movie subreddits
            subreddits = ['movies', 'boxoffice', 'MovieDetails']
            movies = []
            
            for subreddit in subreddits:
                url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
                
                async with self.session.get(url, headers=self.headers) as response:
                    if response.status != 200:
                        continue
                    
                    data = await response.json()
                    
                    for post in data.get('data', {}).get('children', []):
                        post_data = post['data']
                        title = post_data.get('title', '')
                        
                        # Extract movie title from post title
                        movie_title = self._extract_movie_title(title)
                        if movie_title:
                            movies.append({
                                'title': movie_title,
                                'source': 'reddit',
                                'recent_release': True,
                                'score': post_data.get('score', 0)
                            })
            
            return movies
            
        except Exception as e:
            logger.error(f"Error getting Reddit trending movies: {e}")
            return []
    
    def _extract_movie_title(self, post_title: str) -> Optional[str]:
        """Extract movie title from Reddit post title"""
        # Look for patterns like "Movie Name (2024)" or "Movie Name - Discussion"
        patterns = [
            r'(.+?)\s+\(\d{4}\)',
            r'(.+?)\s+-\s+Discussion',
            r'(.+?)\s+Review',
            r'(.+?)\s+Movie'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, post_title, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None


class TwitterScraper(BaseScraper):
    """Scraper for Twitter movie data"""
    
    def __init__(self, session: aiohttp.ClientSession, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        super().__init__(session)
        self.api_key = api_key
        self.api_secret = api_secret
    
    async def scrape_movie_data(self, movie_title: str) -> Dict[str, Any]:
        """Scrape movie data from Twitter"""
        logger.info(f"Scraping Twitter data for: {movie_title}")
        
        # Note: Twitter API v2 requires OAuth 2.0 authentication
        # This is a simplified implementation
        try:
            # For now, return empty data as Twitter API requires proper authentication
            return {
                'reviews': [],
                'comments': [],
                'ratings': [],
                'mentions': [],
                'metadata': {
                    'title': movie_title,
                    'source': 'twitter',
                    'note': 'Twitter API requires OAuth 2.0 authentication'
                }
            }
            
        except Exception as e:
            logger.error(f"Error scraping Twitter for {movie_title}: {e}")
            return {}
    
    async def get_trending_movies(self) -> List[Dict[str, Any]]:
        """Get trending movies from Twitter"""
        # Note: This would require Twitter API v2 with proper authentication
        return [] 