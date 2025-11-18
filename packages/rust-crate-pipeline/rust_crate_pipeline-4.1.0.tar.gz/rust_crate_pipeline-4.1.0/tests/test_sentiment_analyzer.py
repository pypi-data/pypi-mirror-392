"""
Unit tests for sentiment analyzer.
"""

import pytest
from unittest.mock import patch, AsyncMock
from rust_crate_pipeline.utils.sentiment_analyzer import (
    analyze_community_sentiment,
    _fetch_github_metrics,
    _analyze_comment_sentiment,
)


@pytest.mark.asyncio
async def test_analyze_community_sentiment_no_github():
    """Test sentiment analysis without GitHub URL."""
    result = await analyze_community_sentiment(
        crate_name="test",
        repository_url=None,
    )
    
    assert "overall" in result
    assert result["overall"] in ["positive", "neutral", "negative", "unknown"]
    assert "positive_mentions" in result
    assert "negative_mentions" in result


@pytest.mark.asyncio
@patch("rust_crate_pipeline.utils.sentiment_analyzer._fetch_github_metrics")
@patch("rust_crate_pipeline.utils.sentiment_analyzer._fetch_recent_comments")
async def test_analyze_community_sentiment_with_github(mock_comments, mock_metrics):
    """Test sentiment analysis with GitHub URL."""
    mock_metrics.return_value = {"star_count": 1000, "fork_count": 50}
    mock_comments.return_value = [
        "This is great!",
        "Love this crate",
        "Not working for me",
    ]
    
    with patch("rust_crate_pipeline.utils.sentiment_analyzer.VADER_AVAILABLE", True):
        with patch("rust_crate_pipeline.utils.sentiment_analyzer.SentimentIntensityAnalyzer") as mock_vader:
            mock_analyzer = MagicMock()
            mock_vader.return_value = mock_analyzer
            mock_analyzer.polarity_scores.return_value = {"compound": 0.5}
            
            result = await analyze_community_sentiment(
                crate_name="test",
                repository_url="https://github.com/test/test",
            )
            
            assert result["overall"] in ["positive", "neutral", "negative"]
            assert result["star_count"] == 1000


@pytest.mark.asyncio
async def test_analyze_comment_sentiment_positive():
    """Test sentiment analysis of positive comments."""
    comments = [
        "This is great!",
        "Love this crate",
        "Very helpful",
    ]
    
    with patch("rust_crate_pipeline.utils.sentiment_analyzer.VADER_AVAILABLE", True):
        with patch("rust_crate_pipeline.utils.sentiment_analyzer.SentimentIntensityAnalyzer") as mock_vader:
            mock_analyzer = MagicMock()
            mock_vader.return_value = mock_analyzer
            mock_analyzer.polarity_scores.return_value = {"compound": 0.6}
            
            result = _analyze_comment_sentiment(comments)
            
            assert result["positive"] > 0
            assert result["positive"] >= result["negative"]


@pytest.mark.asyncio
async def test_analyze_comment_sentiment_empty():
    """Test sentiment analysis with empty comments."""
    result = _analyze_comment_sentiment([])
    assert result == {"positive": 0, "negative": 0, "neutral": 0}

