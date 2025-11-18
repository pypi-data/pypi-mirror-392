"""
Real community sentiment analysis implementation.

Uses GitHub API and sentiment analysis tools to assess community perception.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import aiohttp

log = logging.getLogger(__name__)

# Optional imports with graceful fallback
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    SentimentIntensityAnalyzer = None

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    TextBlob = None


async def analyze_community_sentiment(
    crate_name: str,
    repository_url: Optional[str] = None,
    github_token: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Analyze community sentiment using GitHub API and sentiment analysis.
    
    Args:
        crate_name: Name of the crate
        repository_url: Repository URL (for GitHub API access)
        github_token: Optional GitHub API token for rate limits
        
    Returns:
        Dictionary with sentiment metrics
    """
    result = {
        "overall": "unknown",
        "positive_mentions": 0,
        "negative_mentions": 0,
        "neutral_mentions": 0,
        "star_count": 0,
        "fork_count": 0,
        "dependent_crate_count": 0,
        "comment_sample_size": 0,
        "sentiment_ratio": 0.0,
    }
    
    try:
        # Extract GitHub owner/repo from URL
        github_path = None
        if repository_url:
            parsed = urlparse(repository_url)
            if "github.com" in parsed.netloc:
                path_parts = parsed.path.strip("/").split("/")
                if len(path_parts) >= 2:
                    github_path = f"{path_parts[0]}/{path_parts[1]}"
        
        if github_path:
            # Fetch GitHub metrics and comments
            github_data = await _fetch_github_metrics(github_path, github_token)
            result.update(github_data)
            
            # Analyze sentiment from comments
            comments = await _fetch_recent_comments(github_path, github_token)
            sentiment_scores = _analyze_comment_sentiment(comments)
            
            result["positive_mentions"] = sentiment_scores["positive"]
            result["negative_mentions"] = sentiment_scores["negative"]
            result["neutral_mentions"] = sentiment_scores["neutral"]
            result["comment_sample_size"] = len(comments)
            
            # Determine overall sentiment
            total = result["positive_mentions"] + result["negative_mentions"]
            if total > 0:
                result["sentiment_ratio"] = result["positive_mentions"] / total
                if result["sentiment_ratio"] >= 0.6:
                    result["overall"] = "positive"
                elif result["sentiment_ratio"] <= 0.4:
                    result["overall"] = "negative"
                else:
                    result["overall"] = "neutral"
            else:
                result["overall"] = "neutral"
        else:
            # No GitHub URL, return neutral defaults
            result["overall"] = "neutral"
            
    except Exception as e:
        log.error(f"Sentiment analysis error for {crate_name}: {e}")
        result["error"] = str(e)
        result["overall"] = "unknown"
    
    return result


async def _fetch_github_metrics(
    github_path: str, github_token: Optional[str] = None
) -> Dict[str, Any]:
    """Fetch GitHub repository metrics (stars, forks, etc.)."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    
    timeout = aiohttp.ClientTimeout(total=10)
    
    try:
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            url = f"https://api.github.com/repos/{github_path}"
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "star_count": data.get("stargazers_count", 0),
                        "fork_count": data.get("forks_count", 0),
                    }
    except Exception as e:
        log.warning(f"Failed to fetch GitHub metrics: {e}")
    
    return {"star_count": 0, "fork_count": 0}


async def _fetch_recent_comments(
    github_path: str, github_token: Optional[str] = None, limit: int = 100
) -> List[str]:
    """Fetch recent issue and PR comments from GitHub."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    
    timeout = aiohttp.ClientTimeout(total=10)
    comments = []
    
    try:
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            # Fetch recent issues
            issues_url = f"https://api.github.com/repos/{github_path}/issues"
            async with session.get(issues_url, params={"state": "all", "per_page": 30}) as resp:
                if resp.status == 200:
                    issues = await resp.json()
                    for issue in issues[:10]:  # Limit to first 10 issues
                        if "comments_url" in issue:
                            async with session.get(issue["comments_url"]) as comments_resp:
                                if comments_resp.status == 200:
                                    issue_comments = await comments_resp.json()
                                    for comment in issue_comments:
                                        if "body" in comment:
                                            comments.append(comment["body"])
                                        if len(comments) >= limit:
                                            break
                        if len(comments) >= limit:
                            break
    except Exception as e:
        log.warning(f"Failed to fetch GitHub comments: {e}")
    
    return comments[:limit]


def _analyze_comment_sentiment(comments: List[str]) -> Dict[str, int]:
    """Analyze sentiment of comments using VADER or TextBlob."""
    positive = 0
    negative = 0
    neutral = 0
    
    if not comments:
        return {"positive": 0, "negative": 0, "neutral": 0}
    
    # Try VADER first (better for social media)
    if VADER_AVAILABLE:
        analyzer = SentimentIntensityAnalyzer()
        for comment in comments:
            scores = analyzer.polarity_scores(comment)
            compound = scores["compound"]
            if compound >= 0.05:
                positive += 1
            elif compound <= -0.05:
                negative += 1
            else:
                neutral += 1
    elif TEXTBLOB_AVAILABLE:
        for comment in comments:
            blob = TextBlob(comment)
            polarity = blob.sentiment.polarity
            if polarity > 0.1:
                positive += 1
            elif polarity < -0.1:
                negative += 1
            else:
                neutral += 1
    else:
        # Fallback: assume neutral if no sentiment library available
        neutral = len(comments)
    
    return {"positive": positive, "negative": negative, "neutral": neutral}

