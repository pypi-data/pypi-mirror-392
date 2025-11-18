"""
Rule-Zero Compliant Envelope Generator

Creates Rule-Zero compliant JSON envelopes for each pipeline action,
ensuring trust scoring and audit metadata collection.
"""

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class RuleZeroEnvelope:
    """Rule-Zero compliant envelope for pipeline actions."""
    
    # Core Rule-Zero fields
    action_id: str
    action_type: str
    timestamp: str
    input_hash: str
    output_hash: str
    
    # Trust and security
    trust_score: float
    security_level: str  # "low", "medium", "high"
    verified: bool
    
    # Audit metadata
    audit_info: Dict[str, Any]
    provenance: Dict[str, Any]
    
    # Results
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None


def compute_hash(data: Any) -> str:
    """Compute SHA-256 hash of data."""
    import hashlib
    
    if isinstance(data, str):
        content = data.encode("utf-8")
    else:
        content = json.dumps(data, sort_keys=True).encode("utf-8")
    
    return hashlib.sha256(content).hexdigest()


def create_envelope(
    action_id: str,
    action_type: str,
    input_data: Any,
    output_data: Any,
    trust_score: float = 0.5,
    security_level: str = "medium",
    audit_info: Optional[Dict[str, Any]] = None,
    success: bool = True,
    error: Optional[str] = None,
) -> RuleZeroEnvelope:
    """Create a Rule-Zero compliant envelope."""
    
    input_hash = compute_hash(input_data)
    output_hash = compute_hash(output_data) if output_data else ""
    
    envelope = RuleZeroEnvelope(
        action_id=action_id,
        action_type=action_type,
        timestamp=datetime.now(timezone.utc).isoformat(),
        input_hash=input_hash,
        output_hash=output_hash,
        trust_score=max(0.0, min(1.0, trust_score)),
        security_level=security_level,
        verified=success and trust_score > 0.5,
        audit_info=audit_info or {},
        provenance={
            "generator": "rust-crate-pipeline",
            "version": "4.1.0",
            "rule_zero_compliant": True,
        },
        success=success,
        result=output_data if success else None,
        error=error,
    )
    
    return envelope


def envelope_to_dict(envelope: RuleZeroEnvelope) -> Dict[str, Any]:
    """Convert envelope to dictionary."""
    return asdict(envelope)


def envelope_to_json(envelope: RuleZeroEnvelope) -> str:
    """Convert envelope to JSON string."""
    return json.dumps(envelope_to_dict(envelope), indent=2, ensure_ascii=False)


def save_envelope(envelope: RuleZeroEnvelope, output_file: str) -> None:
    """Save envelope to JSON file."""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(envelope_to_json(envelope))
    logger.info(f"Saved Rule-Zero envelope to {output_file}")


# Example usage
if __name__ == "__main__":
    # Example: Create envelope for crate analysis
    envelope = create_envelope(
        action_id="crate_analysis_serde_001",
        action_type="crate_analysis",
        input_data={"crate_name": "serde", "version": "1.0.228"},
        output_data={"quality_score": 0.85, "security_risk": "low"},
        trust_score=0.9,
        security_level="low",
        audit_info={
            "license_check": {"status": "allowed", "licenses": ["MIT OR Apache-2.0"]},
            "source_analysis": {"files_analyzed": 150},
        },
    )
    
    print(envelope_to_json(envelope))

