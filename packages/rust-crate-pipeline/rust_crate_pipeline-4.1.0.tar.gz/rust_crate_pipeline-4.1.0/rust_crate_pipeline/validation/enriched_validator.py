"""
Structured validation for LLM-enriched crate metadata.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from jsonschema import Draft7Validator, ValidationError as JSONSchemaError

from ..utils.canonical_store import _compute_hash  # reuse hash helper

logger = logging.getLogger(__name__)


class ValidationFailure(RuntimeError):
    """Raised when an LLM proposal cannot be validated."""


def _detect_supported_formats(snapshot: Dict[str, Any]) -> List[str]:
    """Infer supported formats directly from canonical snapshot text."""
    text_candidates: List[str] = []
    for key in ("description", "readme"):
        value = snapshot.get(key)
        if isinstance(value, str):
            text_candidates.append(value.lower())
    keywords = snapshot.get("keywords") or []
    if isinstance(keywords, list):
        text_candidates.extend(str(k).lower() for k in keywords)
    categories = snapshot.get("categories") or []
    if isinstance(categories, list):
        text_candidates.extend(str(k).lower() for k in categories)

    combined = " ".join(text_candidates)
    if not combined:
        return []

    format_keywords = {
        "json": ["json"],
        "cbor": ["cbor"],
        "yaml": ["yaml", "yml"],
        "toml": ["toml"],
        "xml": ["xml"],
        "messagepack": ["messagepack", "msgpack", "message-pack"],
        "bincode": ["bincode", "bin-code"],
        "postcard": ["postcard"],
        "ron": ["ron"],
        "bson": ["bson"],
    }

    detected: List[str] = []
    for fmt, tokens in format_keywords.items():
        if any(token in combined for token in tokens):
            detected.append(fmt)
    return detected


@dataclass
class ValidationResult:
    enriched: Dict[str, Any]
    issues: List[str] = field(default_factory=list)
    speculative_fields: List[str] = field(default_factory=list)
    snapshot_hash: Optional[str] = None
    schema_path: Optional[Path] = None


class EnrichedValidator:
    """Validates LLM enriched outputs against canonical snapshots."""

    def __init__(self, schema_path: Optional[Path] = None):
        if schema_path is None:
            schema_path = Path("schemas/enriched_crate.schema.json")
        self.schema_path = schema_path
        try:
            schema_data = json.loads(schema_path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"Enriched schema not found at {schema_path}. "
                "Ensure the schemas directory is available."
            ) from exc
        self.schema = schema_data
        self.validator = Draft7Validator(schema_data)

    def prompt_contract(self) -> Dict[str, Any]:
        """Minimal schema shared with the LLM."""
        return self.schema

    def validate(
        self,
        snapshot: Dict[str, Any],
        proposal: Dict[str, Any],
        *,
        snapshot_hash: Optional[str] = None,
    ) -> ValidationResult:
        """Validate proposal and cross-check canonical data."""
        try:
            self.validator.validate(proposal)
        except JSONSchemaError as exc:
            raise ValidationFailure(f"Schema validation failed: {exc.message}") from exc

        enriched = proposal["enriched"]
        issues: List[str] = []
        speculative_fields: List[str] = []

        # Enforce canonical crate identity
        crate_info = enriched.setdefault("crate", {})
        crate_info["name"] = snapshot.get("name")
        crate_info["version"] = snapshot.get("version")

        # Downloads and stars must match snapshot (if available)
        downloads = snapshot.get("downloads")
        if downloads is not None:
            enriched.setdefault("analysis", {})
            enriched["analysis"]["estimated_downloads"] = downloads

        # Capabilities reconciliation
        supported_formats = enriched.get("capabilities", {}).get("supported_formats") or []
        canonical_formats = _detect_supported_formats(snapshot)
        if not canonical_formats and supported_formats:
            issues.append(
                "Supported formats absent from snapshot; clearing LLM-provided values"
            )
            speculative_fields.append("capabilities.supported_formats")
            supported_formats = []
        elif canonical_formats:
            supported_formats = sorted(set(canonical_formats))
        enriched["capabilities"]["supported_formats"] = supported_formats

        # Ensure no_std is grounded on snapshot evidence
        no_std_claim = enriched["capabilities"].get("no_std")
        indicator_tokens = ["no_std", "no-std", "nostd", "no std"]
        
        # Check description and readme
        snapshot_text = " ".join(
            str(snapshot.get(key, "")).lower() for key in ("description", "readme")
        )
        detected_no_std = any(token in snapshot_text for token in indicator_tokens)
        
        # Also check categories (e.g., "no-std" category)
        categories = snapshot.get("categories") or []
        if isinstance(categories, list):
            category_text = " ".join(str(c).lower() for c in categories)
            if any(token in category_text for token in indicator_tokens):
                detected_no_std = True
        
        # Also check feature names
        features = snapshot.get("features") or {}
        if isinstance(features, dict):
            feature_names = " ".join(str(k).lower() for k in features.keys())
            if any(token in feature_names for token in indicator_tokens):
                detected_no_std = True

        if no_std_claim and not detected_no_std:
            issues.append("no_std claim lacks canonical evidence; forcing False")
            speculative_fields.append("capabilities.no_std")
            no_std_claim = False
        elif detected_no_std and not no_std_claim:
            # Canonical evidence exists but LLM didn't set it - fix it
            no_std_claim = True
        enriched["capabilities"]["no_std"] = bool(detected_no_std)

        # Normalize quality score to 0-10 scale
        quality_score = enriched.get("quality_score")
        if isinstance(quality_score, (int, float)):
            # Assume 0-1 inputs represent percentages
            if 0 <= quality_score <= 1:
                quality_score = round(quality_score * 10.0, 2)
            else:
                quality_score = round(min(max(quality_score, 0.0), 10.0), 2)
        else:
            # Try to extract from snapshot's source_analysis
            source_analysis = snapshot.get("source_analysis", {})
            insights = source_analysis.get("insights", {})
            overall_quality_score = insights.get("overall_quality_score")
            if isinstance(overall_quality_score, (int, float)):
                # Normalize 0-1 to 0-10 scale
                if 0 <= overall_quality_score <= 1:
                    quality_score = round(overall_quality_score * 10.0, 2)
                else:
                    quality_score = round(min(max(overall_quality_score, 0.0), 10.0), 2)
            else:
                quality_score = 0.0
                issues.append("Missing quality_score; defaulting to 0")
        enriched["quality_score"] = quality_score

        # Extract security concerns from snapshot if missing or empty
        security_concerns = enriched.get("analysis", {}).get("security_concerns", [])
        if not security_concerns:
            source_analysis = snapshot.get("source_analysis", {})
            failure_analysis = source_analysis.get("failure_analysis", {})
            critical_missing = failure_analysis.get("critical_missing", [])
            
            # Extract security-related critical missing items
            for item in critical_missing:
                if isinstance(item, dict):
                    item_type = item.get("type", "")
                    if "security" in item_type.lower() or "audit" in item_type.lower():
                        reason = item.get("reason", "")
                        intervention = item.get("intervention", "")
                        if reason:
                            security_concerns.append(reason)
                        elif intervention:
                            security_concerns.append(intervention)
            
            # Check geiger insights for errors
            geiger_insights = source_analysis.get("geiger_insights", {})
            geiger_error = geiger_insights.get("error")
            if geiger_error:
                security_concerns.append(f"Geiger parsing error: {geiger_error}")
            
            # Check security risk level
            insights = source_analysis.get("insights", {})
            security_risk_level = insights.get("security_risk_level", "")
            if security_risk_level and "unknown_requires_manual_audit" in str(security_risk_level):
                if not any("manual" in c.lower() or "audit" in c.lower() for c in security_concerns):
                    security_concerns.append("Security audit missing - manual review required")
            
            if security_concerns:
                enriched.setdefault("analysis", {})["security_concerns"] = security_concerns

        # Guarantee warnings list
        warnings_list = enriched.get("warnings")
        if not isinstance(warnings_list, list):
            warnings_list = []
        warnings_list.extend(issues)
        enriched["warnings"] = sorted(set(warnings_list))

        return ValidationResult(
            enriched=enriched,
            issues=issues,
            speculative_fields=speculative_fields,
            snapshot_hash=snapshot_hash or _compute_hash(snapshot),
            schema_path=self.schema_path,
        )

