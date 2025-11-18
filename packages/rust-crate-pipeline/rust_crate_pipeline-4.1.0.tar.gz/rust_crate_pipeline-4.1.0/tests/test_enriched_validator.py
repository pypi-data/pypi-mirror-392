import json
from pathlib import Path

import pytest

from rust_crate_pipeline.validation import EnrichedValidator, ValidationFailure

SCHEMA_PATH = Path("schemas/enriched_crate.schema.json")


def _sample_proposal() -> dict:
    return {
        "enriched": {
            "crate": {"name": "tokio", "version": "1.48.0"},
            "readme_summary": "Async runtime for Rust.",
            "feature_summary": "Provides IO, runtime, macros.",
            "quality_score": 0.82,
            "use_case": "async-runtime",
            "analysis": {
                "maintenance_status": "active",
                "community_health": "high",
                "code_quality": "high",
                "documentation_quality": "medium",
                "security_concerns": [],
                "performance_characteristics": "Highly optimized for IO",
                "use_case_suitability": ["networking", "async apps"],
            },
            "user_behavior": {
                "target_audience": "systems developers",
                "adoption_patterns": "widely used in networking stacks",
            },
            "security": {"risk_level": "low", "vulnerabilities": []},
            "capabilities": {
                "no_std": False,
                "supported_formats": ["ron"],
            },
            "warnings": [],
            "speculative_fields": [],
        }
    }


@pytest.fixture(scope="module")
def validator() -> EnrichedValidator:
    return EnrichedValidator(schema_path=SCHEMA_PATH)


def test_supported_formats_clamped_when_snapshot_has_no_evidence(validator: EnrichedValidator):
    snapshot = {"name": "tokio", "version": "1.48.0", "description": "Async runtime"}
    proposal = _sample_proposal()

    result = validator.validate(snapshot, proposal)

    assert result.enriched["capabilities"]["supported_formats"] == []
    assert "capabilities.supported_formats" in result.speculative_fields
    assert result.enriched["quality_score"] == 8.2  # scaled to 0-10


def test_validation_failure_for_missing_schema_fields(validator: EnrichedValidator):
    snapshot = {"name": "tokio", "version": "1.48.0"}
    proposal = {"enriched": {"readme_summary": "x"}}  # incomplete

    with pytest.raises(ValidationFailure):
        validator.validate(snapshot, proposal)

