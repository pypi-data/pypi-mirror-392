"""
Integration tests for real analysis implementations.

Tests the full pipeline with real (but mocked) API calls.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from rust_crate_pipeline.core.irl_engine import IRLEngine
from rust_crate_pipeline.core.sacred_chain import TrustVerdict


@pytest.fixture
def mock_config():
    """Create mock config."""
    config = MagicMock()
    config.github_token = None
    return config


@pytest.mark.asyncio
async def test_full_analysis_flow_popular_crate(mock_config):
    """Test full analysis flow for a popular crate (e.g., serde)."""
    engine = IRLEngine(mock_config)
    
    # Mock context with realistic data for popular crate
    context = {
        "readme": """
# Serde

Serde is a framework for serializing and deserializing Rust data structures.

## Example

```rust
use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize)]
struct Point {
    x: i32,
    y: i32,
}
```
""",
        "repository_url": "https://github.com/serde-rs/serde",
        "metadata": {
            "name": "serde",
            "version": "1.0.0",
            "categories": ["encoding"],
            "dependencies": [],
        },
    }
    
    with patch("rust_crate_pipeline.core.irl_engine.REAL_ANALYSIS_AVAILABLE", True):
        with patch("rust_crate_pipeline.utils.documentation_analyzer.analyze_documentation_quality") as mock_docs:
            with patch("rust_crate_pipeline.utils.sentiment_analyzer.analyze_community_sentiment") as mock_sentiment:
                with patch("rust_crate_pipeline.utils.ecosystem_analyzer.analyze_ecosystem_position") as mock_ecosystem:
                    # Mock realistic responses
                    mock_docs.return_value = {
                        "quality_score": 9.0,
                        "readability_score": 0.9,
                        "coverage": 0.95,
                        "example_density": 0.85,
                        "navigation_score": 1.0,
                        "freshness_score": 0.95,
                        "completeness": 0.92,
                        "examples_present": True,
                        "api_documented": True,
                    }
                    
                    mock_sentiment.return_value = {
                        "overall": "positive",
                        "positive_mentions": 200,
                        "negative_mentions": 5,
                        "neutral_mentions": 20,
                        "star_count": 5000,
                        "fork_count": 300,
                        "sentiment_ratio": 0.98,
                    }
                    
                    mock_ecosystem.return_value = {
                        "category": "encoding",
                        "maturity": "stable",
                        "dependencies_count": 2,
                        "reverse_dependencies_count": 5000,
                        "contributor_count": 150,
                        "release_frequency": 8.0,
                        "issue_closure_rate": 0.95,
                        "ecosystem_score": 9.5,
                    }
                    
                    trace = await engine.analyze_with_sacred_chain("serde", context=context)
                    
                    # Verify results
                    assert trace.verdict == TrustVerdict.ALLOW
                    assert "serde" in trace.input_data.lower()
                    assert trace.audit_info["quality_score"] > 8.0
                    assert trace.audit_info["sentiment"]["overall"] == "positive"
                    assert trace.audit_info["ecosystem"]["ecosystem_score"] > 8.0


@pytest.mark.asyncio
async def test_full_analysis_flow_low_quality_crate(mock_config):
    """Test full analysis flow for a low-quality crate."""
    engine = IRLEngine(mock_config)
    
    context = {
        "readme": "# Test\n\nMinimal docs.",
        "repository_url": None,  # No GitHub
        "metadata": {
            "name": "test-crate",
            "version": "0.1.0",
            "categories": [],
        },
    }
    
    with patch("rust_crate_pipeline.core.irl_engine.REAL_ANALYSIS_AVAILABLE", True):
        with patch("rust_crate_pipeline.utils.documentation_analyzer.analyze_documentation_quality") as mock_docs:
            with patch("rust_crate_pipeline.utils.sentiment_analyzer.analyze_community_sentiment") as mock_sentiment:
                with patch("rust_crate_pipeline.utils.ecosystem_analyzer.analyze_ecosystem_position") as mock_ecosystem:
                    # Mock low-quality responses
                    mock_docs.return_value = {
                        "quality_score": 3.0,
                        "readability_score": 0.3,
                        "coverage": 0.2,
                        "example_density": 0.0,
                        "navigation_score": 0.0,
                        "freshness_score": 0.5,
                        "completeness": 0.25,
                        "examples_present": False,
                        "api_documented": False,
                    }
                    
                    mock_sentiment.return_value = {
                        "overall": "neutral",
                        "positive_mentions": 0,
                        "negative_mentions": 0,
                        "neutral_mentions": 0,
                        "star_count": 0,
                        "fork_count": 0,
                        "sentiment_ratio": 0.5,
                    }
                    
                    mock_ecosystem.return_value = {
                        "category": "utilities",
                        "maturity": "pre-stable",
                        "dependencies_count": 0,
                        "reverse_dependencies_count": 0,
                        "contributor_count": 1,
                        "release_frequency": 0.5,
                        "issue_closure_rate": 0.3,
                        "ecosystem_score": 2.0,
                    }
                    
                    trace = await engine.analyze_with_sacred_chain("test-crate", context=context)
                    
                    # Should defer or deny due to low quality
                    assert trace.verdict in [TrustVerdict.DEFER, TrustVerdict.DENY]
                    assert trace.audit_info["quality_score"] < 5.0


@pytest.mark.asyncio
async def test_analysis_with_missing_data(mock_config):
    """Test analysis when some data is missing."""
    engine = IRLEngine(mock_config)
    
    context = {}  # Empty context
    
    trace = await engine.analyze_with_sacred_chain("unknown-crate", context=context)
    
    # Should defer due to insufficient data
    assert trace.verdict == TrustVerdict.DEFER
    assert "insufficient" in trace.suggestion.lower() or "defer" in trace.suggestion.lower()

