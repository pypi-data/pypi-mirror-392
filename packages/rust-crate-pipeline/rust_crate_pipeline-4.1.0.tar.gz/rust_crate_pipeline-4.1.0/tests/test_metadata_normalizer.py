"""Tests for metadata normalization module."""

import pytest

from rust_crate_pipeline.utils.metadata_normalizer import MetadataNormalizer


class TestMetadataNormalizer:
    """Test MetadataNormalizer class."""
    
    def test_normalize_downloads_int(self):
        """Test normalizing integer downloads."""
        assert MetadataNormalizer.normalize_downloads(1000) == 1000
        assert MetadataNormalizer.normalize_downloads(0) == 0
        assert MetadataNormalizer.normalize_downloads(-5) == 0  # Negative becomes 0
    
    def test_normalize_downloads_float(self):
        """Test normalizing float downloads."""
        assert MetadataNormalizer.normalize_downloads(1000.5) == 1000
        assert MetadataNormalizer.normalize_downloads(1000.9) == 1000
        assert MetadataNormalizer.normalize_downloads(-5.5) == 0
    
    def test_normalize_downloads_string(self):
        """Test normalizing string downloads."""
        assert MetadataNormalizer.normalize_downloads("1000") == 1000
        assert MetadataNormalizer.normalize_downloads("1,000") == 1000
        assert MetadataNormalizer.normalize_downloads("1 000") == 1000
        assert MetadataNormalizer.normalize_downloads("invalid") == 0
    
    def test_normalize_downloads_none(self):
        """Test normalizing None downloads."""
        assert MetadataNormalizer.normalize_downloads(None) == 0
    
    def test_normalize_keywords_list(self):
        """Test normalizing list of keywords."""
        keywords = ["rust", "async", "tokio"]
        result = MetadataNormalizer.normalize_keywords(keywords)
        assert result == ["rust", "async", "tokio"]
    
    def test_normalize_keywords_tuple(self):
        """Test normalizing tuple of keywords."""
        keywords = ("rust", "async", "tokio")
        result = MetadataNormalizer.normalize_keywords(keywords)
        assert result == ["rust", "async", "tokio"]
    
    def test_normalize_keywords_string_comma(self):
        """Test normalizing comma-separated keywords."""
        keywords = "rust, async, tokio"
        result = MetadataNormalizer.normalize_keywords(keywords)
        assert "rust" in result
        assert "async" in result
        assert "tokio" in result
    
    def test_normalize_keywords_string_space(self):
        """Test normalizing space-separated keywords."""
        keywords = "rust async tokio"
        result = MetadataNormalizer.normalize_keywords(keywords)
        assert len(result) == 3
    
    def test_normalize_keywords_empty(self):
        """Test normalizing empty keywords."""
        assert MetadataNormalizer.normalize_keywords(None) == []
        assert MetadataNormalizer.normalize_keywords([]) == []
        assert MetadataNormalizer.normalize_keywords("") == []
    
    def test_normalize_keywords_with_whitespace(self):
        """Test normalizing keywords with extra whitespace."""
        keywords = [" rust ", "  async  ", "tokio"]
        result = MetadataNormalizer.normalize_keywords(keywords)
        assert result == ["rust", "async", "tokio"]
    
    def test_normalize_features_list(self):
        """Test normalizing list of features."""
        features = ["feature1", "feature2", "feature3"]
        result = MetadataNormalizer.normalize_features(features)
        assert result == ["feature1", "feature2", "feature3"]
    
    def test_normalize_features_dict(self):
        """Test normalizing dict of features."""
        features = {
            "feature1": ["dep1"],
            "feature2": ["dep2"],
            "feature3": []
        }
        result = MetadataNormalizer.normalize_features(features)
        assert "feature1" in result
        assert "feature2" in result
        assert "feature3" in result
    
    def test_normalize_features_string(self):
        """Test normalizing string features."""
        features = "feature1,feature2"
        result = MetadataNormalizer.normalize_features(features)
        assert len(result) >= 1
    
    def test_normalize_features_empty(self):
        """Test normalizing empty features."""
        assert MetadataNormalizer.normalize_features(None) == []
        assert MetadataNormalizer.normalize_features([]) == []
        assert MetadataNormalizer.normalize_features({}) == []
    
    def test_normalize_version_string(self):
        """Test normalizing version strings."""
        assert MetadataNormalizer.normalize_version("1.0.0") == "1.0.0"
        assert MetadataNormalizer.normalize_version("1.0") == "1.0"
        assert MetadataNormalizer.normalize_version("latest") == "latest"
    
    def test_normalize_version_none(self):
        """Test normalizing None version."""
        assert MetadataNormalizer.normalize_version(None) == ""
        assert MetadataNormalizer.normalize_version("") == ""
    
    def test_normalize_version_int(self):
        """Test normalizing integer version."""
        assert MetadataNormalizer.normalize_version(1) == "1"
        assert MetadataNormalizer.normalize_version(0) == "0"
    
    def test_normalize_categories_list(self):
        """Test normalizing list of categories."""
        categories = ["category1", "category2"]
        result = MetadataNormalizer.normalize_categories(categories)
        assert result == ["category1", "category2"]
    
    def test_normalize_categories_string(self):
        """Test normalizing string categories."""
        categories = "category1, category2"
        result = MetadataNormalizer.normalize_categories(categories)
        assert len(result) >= 1
    
    def test_normalize_categories_empty(self):
        """Test normalizing empty categories."""
        assert MetadataNormalizer.normalize_categories(None) == []
        assert MetadataNormalizer.normalize_categories([]) == []
    
    def test_normalize_metadata_complete(self):
        """Test normalizing complete metadata dictionary."""
        metadata = {
            "downloads": "1,000",
            "keywords": "rust, async",
            "features": ["feature1", "feature2"],
            "version": "1.0.0",
            "categories": ["category1"]
        }
        result = MetadataNormalizer.normalize_metadata(metadata)
        assert result["downloads"] == 1000
        assert isinstance(result["keywords"], list)
        assert isinstance(result["features"], list)
        assert result["version"] == "1.0.0"
        assert isinstance(result["categories"], list)
    
    def test_normalize_metadata_partial(self):
        """Test normalizing partial metadata."""
        metadata = {
            "downloads": 1000,
            "keywords": ["rust"]
        }
        result = MetadataNormalizer.normalize_metadata(metadata)
        assert result["downloads"] == 1000
        assert result["keywords"] == ["rust"]
    
    def test_normalize_metadata_empty(self):
        """Test normalizing empty metadata."""
        result = MetadataNormalizer.normalize_metadata({})
        assert isinstance(result, dict)
    
    def test_normalize_metadata_none_values(self):
        """Test normalizing metadata with None values."""
        metadata = {
            "downloads": None,
            "keywords": None,
            "features": None
        }
        result = MetadataNormalizer.normalize_metadata(metadata)
        assert result["downloads"] == 0
        assert result["keywords"] == []
        assert result["features"] == []

