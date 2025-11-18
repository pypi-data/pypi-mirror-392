"""
Unit tests for ecosystem analyzer.
"""

import pytest
from unittest.mock import patch, AsyncMock
from rust_crate_pipeline.utils.ecosystem_analyzer import (
    analyze_ecosystem_position,
    _compute_ecosystem_score,
)


@pytest.mark.asyncio
async def test_analyze_ecosystem_position_basic():
    """Test basic ecosystem position analysis."""
    result = await analyze_ecosystem_position(
        crate_name="test",
        crate_metadata={"version": "1.0.0", "categories": ["web"]},
    )
    
    assert "category" in result
    assert "maturity" in result
    assert "ecosystem_score" in result
    assert 0 <= result["ecosystem_score"] <= 10


@pytest.mark.asyncio
async def test_compute_ecosystem_score_high():
    """Test ecosystem score computation for popular crate."""
    metrics = {
        "reverse_dependencies_count": 2000,
        "contributor_count": 100,
        "release_frequency": 8.0,
        "issue_closure_rate": 0.9,
        "maturity": "stable",
    }
    
    score = _compute_ecosystem_score(metrics)
    
    assert score > 7.0  # Should be high for popular crate
    assert score <= 10.0


@pytest.mark.asyncio
async def test_compute_ecosystem_score_low():
    """Test ecosystem score computation for obscure crate."""
    metrics = {
        "reverse_dependencies_count": 5,
        "contributor_count": 1,
        "release_frequency": 0.5,
        "issue_closure_rate": 0.3,
        "maturity": "pre-stable",
    }
    
    score = _compute_ecosystem_score(metrics)
    
    assert score < 5.0  # Should be low for obscure crate
    assert score >= 0.0

