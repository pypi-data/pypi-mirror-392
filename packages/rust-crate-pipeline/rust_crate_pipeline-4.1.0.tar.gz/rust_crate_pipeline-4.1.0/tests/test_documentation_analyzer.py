"""
Unit tests for documentation analyzer.
"""

import pytest
from unittest.mock import patch, AsyncMock
from rust_crate_pipeline.utils.documentation_analyzer import (
    analyze_documentation_quality,
    _compute_readability_score,
    _compute_example_density,
    _compute_navigation_score,
)


@pytest.mark.asyncio
async def test_analyze_documentation_quality_basic():
    """Test basic documentation quality analysis."""
    result = await analyze_documentation_quality(
        crate_name="test",
        readme_content="# Test\n\nThis is a test crate.",
    )
    
    assert "quality_score" in result
    assert 0 <= result["quality_score"] <= 10
    assert "readability_score" in result
    assert "coverage" in result
    assert "example_density" in result


@pytest.mark.asyncio
async def test_compute_example_density_with_examples():
    """Test example density computation with Rust code blocks."""
    readme = """
# Test Crate

Here's an example:

```rust
fn main() {
    println!("Hello");
}
```

Another example:

```rust
fn add(a: i32, b: i32) -> i32 {
    a + b
}
```
"""
    density = _compute_example_density(readme)
    assert density > 0.0
    assert density <= 1.0


@pytest.mark.asyncio
async def test_compute_example_density_no_examples():
    """Test example density with no code blocks."""
    readme = "# Test\n\nJust text, no examples."
    density = _compute_example_density(readme)
    assert density == 0.0


@pytest.mark.asyncio
async def test_compute_navigation_score_with_toc():
    """Test navigation score with table of contents."""
    readme = """
# Test Crate

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)

## Installation

## Usage
"""
    score = _compute_navigation_score(readme)
    assert score > 0.0


@pytest.mark.asyncio
async def test_compute_navigation_score_no_toc():
    """Test navigation score without TOC."""
    readme = "# Test\n\nJust content."
    score = _compute_navigation_score(readme)
    assert score >= 0.0


@pytest.mark.asyncio
@patch("rust_crate_pipeline.utils.documentation_analyzer.TEXTSTAT_AVAILABLE", True)
@patch("rust_crate_pipeline.utils.documentation_analyzer.textstat")
async def test_compute_readability_score(mock_textstat):
    """Test readability score computation."""
    mock_textstat.flesch_reading_ease.return_value = 70.0
    mock_textstat.smog_index.return_value = 8.0
    
    score = await _compute_readability_score("Test text here.")
    
    assert 0 <= score <= 1.0
    mock_textstat.flesch_reading_ease.assert_called_once()
    mock_textstat.smog_index.assert_called_once()

