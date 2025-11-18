"""
Unit tests for IRL engine analysis functions.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from rust_crate_pipeline.core.irl_engine import IRLEngine
from rust_crate_pipeline.core.sacred_chain import TrustVerdict


@pytest.fixture
def irl_engine():
    """Create IRL engine instance for testing."""
    config = MagicMock()
    engine = IRLEngine(config)
    return engine


@pytest.mark.asyncio
async def test_make_trust_decision_high_quality_positive_sentiment(irl_engine):
    """Test trust decision with high quality and positive sentiment."""
    verdict, reason = irl_engine._make_trust_decision(
        reasoning_steps=[],
        suggestion="ALLOW: High quality",
        quality_score=8.5,
        metadata={"name": "test"},
        docs={"quality_score": 8.0, "completeness": 0.9},
        sentiment={"overall": "positive", "positive_mentions": 50},
        ecosystem={"ecosystem_score": 8.0},
        ml_predictions=None,
    )
    assert verdict == TrustVerdict.ALLOW
    assert "positive" in reason.lower()


@pytest.mark.asyncio
async def test_make_trust_decision_low_quality(irl_engine):
    """Test trust decision with low quality score."""
    verdict, reason = irl_engine._make_trust_decision(
        reasoning_steps=[],
        suggestion="DENY: Low quality",
        quality_score=3.5,
        metadata={"name": "test"},
        docs={"quality_score": 3.0, "completeness": 0.3},
        sentiment={"overall": "neutral"},
        ecosystem={"ecosystem_score": 4.0},
        ml_predictions=None,
    )
    assert verdict == TrustVerdict.DENY
    assert "low" in reason.lower() or "quality" in reason.lower()


@pytest.mark.asyncio
async def test_make_trust_decision_negative_sentiment(irl_engine):
    """Test trust decision with negative sentiment."""
    verdict, reason = irl_engine._make_trust_decision(
        reasoning_steps=[],
        suggestion="DENY: Negative sentiment",
        quality_score=6.5,
        metadata={"name": "test"},
        docs={"quality_score": 7.0, "completeness": 0.7},
        sentiment={"overall": "negative", "negative_mentions": 20},
        ecosystem={"ecosystem_score": 6.0},
        ml_predictions=None,
    )
    assert verdict == TrustVerdict.DENY
    assert "negative" in reason.lower()


@pytest.mark.asyncio
async def test_make_trust_decision_insufficient_data(irl_engine):
    """Test trust decision with insufficient data."""
    verdict, reason = irl_engine._make_trust_decision(
        reasoning_steps=[],
        suggestion="DEFER: Insufficient data",
        quality_score=6.0,
        metadata={"name": "test"},
        docs={"quality_score": 0, "completeness": 0},
        sentiment={"overall": "unknown"},
        ecosystem={"ecosystem_score": 5.0},
        ml_predictions=None,
    )
    assert verdict == TrustVerdict.DEFER
    assert "insufficient" in reason.lower() or "data" in reason.lower()


@pytest.mark.asyncio
async def test_generate_suggestion_high_quality(irl_engine):
    """Test suggestion generation for high quality crate."""
    suggestion = irl_engine._generate_traceable_suggestion(
        reasoning_steps=["Quality analyzed"],
        quality_score=9.0,
        docs={"quality_score": 9.0},
        sentiment={"overall": "positive"},
        ecosystem={"ecosystem_score": 9.0},
    )
    assert "ALLOW" in suggestion
    assert "high quality" in suggestion.lower() or "quality" in suggestion.lower()


@pytest.mark.asyncio
async def test_generate_suggestion_low_quality(irl_engine):
    """Test suggestion generation for low quality crate."""
    suggestion = irl_engine._generate_traceable_suggestion(
        reasoning_steps=["Quality analyzed"],
        quality_score=3.0,
        docs={"quality_score": 3.0},
        sentiment={"overall": "neutral"},
        ecosystem={"ecosystem_score": 4.0},
    )
    assert "DENY" in suggestion
    assert "low" in suggestion.lower() or "quality" in suggestion.lower()


@pytest.mark.asyncio
async def test_analyze_documentation_with_context(irl_engine):
    """Test documentation analysis with context."""
    irl_engine._crate_context = {
        "readme": "# Test Crate\n\nThis is a test crate with examples.\n\n```rust\nfn main() {}\n```",
        "repository_url": "https://github.com/test/test",
        "metadata": {"name": "test", "version": "1.0.0"},
    }
    
    with patch("rust_crate_pipeline.core.irl_engine.REAL_ANALYSIS_AVAILABLE", True):
        with patch("rust_crate_pipeline.core.irl_engine.analyze_documentation_quality") as mock_analyze:
            mock_analyze.return_value = {
                "quality_score": 8.5,
                "readability_score": 0.9,
                "coverage": 0.85,
                "example_density": 0.8,
                "navigation_score": 1.0,
                "freshness_score": 0.9,
                "completeness": 0.88,
                "examples_present": True,
                "api_documented": True,
            }
            
            result = await irl_engine._analyze_documentation("test")
            
            assert result["quality_score"] == 8.5
            assert result["examples_present"] is True
            mock_analyze.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_community_sentiment_with_github(irl_engine):
    """Test sentiment analysis with GitHub URL."""
    irl_engine._crate_context = {
        "repository_url": "https://github.com/test/test",
    }
    
    with patch("rust_crate_pipeline.core.irl_engine.REAL_ANALYSIS_AVAILABLE", True):
        with patch("rust_crate_pipeline.core.irl_engine.analyze_community_sentiment") as mock_analyze:
            mock_analyze.return_value = {
                "overall": "positive",
                "positive_mentions": 45,
                "negative_mentions": 5,
                "neutral_mentions": 10,
                "star_count": 1234,
                "fork_count": 89,
                "sentiment_ratio": 0.9,
            }
            
            result = await irl_engine._analyze_community_sentiment("test")
            
            assert result["overall"] == "positive"
            assert result["positive_mentions"] == 45
            mock_analyze.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_ecosystem_position(irl_engine):
    """Test ecosystem position analysis."""
    irl_engine._crate_context = {
        "repository_url": "https://github.com/test/test",
        "metadata": {"version": "1.0.0", "categories": ["web"]},
    }
    
    with patch("rust_crate_pipeline.core.irl_engine.REAL_ANALYSIS_AVAILABLE", True):
        with patch("rust_crate_pipeline.core.irl_engine.analyze_ecosystem_position") as mock_analyze:
            mock_analyze.return_value = {
                "category": "web",
                "maturity": "stable",
                "dependencies_count": 12,
                "reverse_dependencies_count": 1500,
                "contributor_count": 75,
                "release_frequency": 6.0,
                "issue_closure_rate": 0.85,
                "ecosystem_score": 8.9,
            }
            
            result = await irl_engine._analyze_ecosystem_position("test")
            
            assert result["ecosystem_score"] == 8.9
            assert result["maturity"] == "stable"
            mock_analyze.assert_called_once()


@pytest.mark.asyncio
async def test_synthesize_quality_score(irl_engine):
    """Test quality score synthesis."""
    metadata = {"name": "test"}
    docs = {"quality_score": 8.0}
    sentiment = {"overall": "positive"}
    ecosystem = {"ecosystem_score": 7.5}
    
    score = irl_engine._synthesize_quality_score(metadata, docs, sentiment, ecosystem, ml_predictions=None)
    
    assert 0 <= score <= 10
    assert score > 5.0  # Should be above average with good inputs

