"""
Analyzers for sentiment, emotion, and trend extraction from movie reviews and comments
"""

import logging
from typing import List, Dict, Any
import nltk
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from bertopic import BERTopic
import openai
import numpy as np

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Performs sentiment and emotion analysis on text batches"""
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        # Optionally, load other models (DistilBERT, etc.)

    async def analyze_batch(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze a batch of texts for sentiment distribution and average rating"""
        sentiments = {'pos': 0, 'neu': 0, 'neg': 0}
        scores = []
        for text in texts:
            vs = self.vader.polarity_scores(text)
            scores.append(vs['compound'])
            if vs['compound'] >= 0.05:
                sentiments['pos'] += 1
            elif vs['compound'] <= -0.05:
                sentiments['neg'] += 1
            else:
                sentiments['neu'] += 1
        total = max(1, len(texts))
        distribution = {k: v / total for k, v in sentiments.items()}
        average_rating = np.mean(scores) * 5  # Scale to 1-5
        return {
            'distribution': distribution,
            'average_rating': float(average_rating)
        }

class TrendAnalyzer:
    """Performs clustering, topic modeling, and insight extraction"""
    def __init__(self):
        self.topic_model = BERTopic(verbose=False)

    async def analyze_trends(self, scraped_data: Dict[str, Any], movie_title: str) -> Dict[str, Any]:
        """Cluster and summarize topics from reviews/comments"""
        texts = [r.get('text', '') for r in scraped_data.get('reviews', [])] + [c.get('text', '') for c in scraped_data.get('comments', [])]
        if not texts:
            return {
                'popularity_score': 0.0,
                'topics': [],
            }
        topics, _ = self.topic_model.fit_transform(texts)
        topic_info = self.topic_model.get_topic_info()
        top_topics = topic_info['Name'].tolist()[:5]
        popularity_score = min(len(texts) / 1000, 1.0) * 10
        return {
            'popularity_score': popularity_score,
            'topics': top_topics
        }

    async def extract_fan_insights(self, texts: List[str]) -> Dict[str, Any]:
        """Extract unmet desires, continuations, and viral potential from text using LLM summarization"""
        if not texts:
            return {'desires': [], 'continuations': [], 'viral_potential': 0.0, 'target_audience': []}
        # Use OpenAI or other LLM for summarization
        prompt = (
            "Given the following movie reviews/comments, extract: "
            "1. The top 5 unmet fan desires (what fans wanted next), "
            "2. The most anticipated continuations, "
            "3. Estimate viral potential (0-1), "
            "4. Target audience keywords.\n\n"
            f"Reviews:\n{texts[:1000]}"
        )
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            content = response['choices'][0]['message']['content']
            # Simple parsing (should be improved)
            lines = content.split('\n')
            desires = [l for l in lines if l.startswith('1.') or l.startswith('-')]
            continuations = [l for l in lines if l.startswith('2.')]
            viral_potential = 0.8  # Placeholder
            target_audience = [l for l in lines if l.startswith('4.')]
            return {
                'desires': desires,
                'continuations': continuations,
                'viral_potential': viral_potential,
                'target_audience': target_audience
            }
        except Exception as e:
            logger.error(f"LLM summarization failed: {e}")
            return {'desires': [], 'continuations': [], 'viral_potential': 0.0, 'target_audience': []} 