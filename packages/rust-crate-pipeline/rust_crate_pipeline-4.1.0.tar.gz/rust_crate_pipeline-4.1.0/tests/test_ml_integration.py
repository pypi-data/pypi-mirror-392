"""
Tests for ML prediction integration into trust decisions.
"""

import pytest
from unittest.mock import MagicMock
from rust_crate_pipeline.core.irl_engine import IRLEngine
from rust_crate_pipeline.core.sacred_chain import TrustVerdict


@pytest.fixture
def irl_engine():
    """Create IRL engine instance for testing."""
    config = MagicMock()
    engine = IRLEngine(config)
    return engine


def test_synthesize_quality_score_without_ml(irl_engine):
    """Test quality score synthesis without ML predictions."""
    metadata = {"name": "test_crate"}
    docs = {"quality_score": 7.0}
    sentiment = {"overall": "positive", "star_count": 1000}
    ecosystem = {"ecosystem_score": 8.0}
    
    score = irl_engine._synthesize_quality_score(
        metadata, docs, sentiment, ecosystem, ml_predictions=None
    )
    
    assert 0.0 <= score <= 10.0
    assert score > 0


def test_synthesize_quality_score_with_ml_high_confidence(irl_engine):
    """Test quality score synthesis with high-confidence ML predictions."""
    metadata = {"name": "test_crate"}
    docs = {"quality_score": 7.0}
    sentiment = {"overall": "positive", "star_count": 1000}
    ecosystem = {"ecosystem_score": 8.0}
    ml_predictions = {
        "quality_score": 0.9,  # High quality (0-1 scale)
        "confidence": 0.8,  # High confidence
    }
    
    score = irl_engine._synthesize_quality_score(
        metadata, docs, sentiment, ecosystem, ml_predictions=ml_predictions
    )
    
    assert 0.0 <= score <= 10.0
    # ML score of 0.9 should boost the overall score
    assert score >= 7.0


def test_synthesize_quality_score_with_ml_low_confidence(irl_engine):
    """Test that low-confidence ML predictions don't significantly affect score."""
    metadata = {"name": "test_crate"}
    docs = {"quality_score": 7.0}
    sentiment = {"overall": "positive", "star_count": 1000}
    ecosystem = {"ecosystem_score": 8.0}
    ml_predictions = {
        "quality_score": 0.3,  # Low quality
        "confidence": 0.2,  # Low confidence - should be ignored
    }
    
    score_with_ml = irl_engine._synthesize_quality_score(
        metadata, docs, sentiment, ecosystem, ml_predictions=ml_predictions
    )
    score_without_ml = irl_engine._synthesize_quality_score(
        metadata, docs, sentiment, ecosystem, ml_predictions=None
    )
    
    # Low confidence ML should not significantly change the score
    assert abs(score_with_ml - score_without_ml) < 1.0


def test_make_trust_decision_with_ml_security_risk(irl_engine):
    """Test trust decision with high ML security risk."""
    ml_predictions = {
        "security_risk": "high",
        "confidence": 0.8,
        "maintenance_score": 0.7,
    }
    
    verdict, reason = irl_engine._make_trust_decision(
        reasoning_steps=[],
        suggestion="DENY: Security risk",
        quality_score=7.0,
        metadata={"name": "test"},
        docs={"quality_score": 7.0, "completeness": 0.8},
        sentiment={"overall": "positive"},
        ecosystem={"ecosystem_score": 7.0},
        ml_predictions=ml_predictions,
    )
    
    # High security risk should result in DENY
    assert verdict == TrustVerdict.DENY
    assert "security" in reason.lower() or "risk" in reason.lower()


def test_make_trust_decision_with_ml_low_maintenance(irl_engine):
    """Test trust decision with low ML maintenance score."""
    ml_predictions = {
        "security_risk": "low",
        "confidence": 0.8,
        "maintenance_score": 0.2,  # Low maintenance (0-1 scale, so 0.2 = 2.0/10)
    }
    
    verdict, reason = irl_engine._make_trust_decision(
        reasoning_steps=[],
        suggestion="FLAG: Low maintenance",
        quality_score=6.0,
        metadata={"name": "test"},
        docs={"quality_score": 6.0, "completeness": 0.7},
        sentiment={"overall": "neutral"},
        ecosystem={"ecosystem_score": 6.0},
        ml_predictions=ml_predictions,
    )
    
    # Low maintenance should result in FLAG
    assert verdict == TrustVerdict.FLAG
    assert "maintenance" in reason.lower() or "abandonment" in reason.lower()


def test_make_trust_decision_with_ml_low_confidence(irl_engine):
    """Test that low-confidence ML predictions don't override heuristic decisions."""
    ml_predictions = {
        "security_risk": "high",
        "confidence": 0.3,  # Low confidence - should be ignored
        "maintenance_score": 0.2,
    }
    
    verdict, reason = irl_engine._make_trust_decision(
        reasoning_steps=[],
        suggestion="ALLOW: High quality",
        quality_score=8.0,
        metadata={"name": "test"},
        docs={"quality_score": 8.0, "completeness": 0.9},
        sentiment={"overall": "positive"},
        ecosystem={"ecosystem_score": 8.0},
        ml_predictions=ml_predictions,
    )
    
    # Low confidence ML should not override high quality + positive sentiment
    assert verdict == TrustVerdict.ALLOW

