"""
Canonical data storage helpers for crate snapshots, LLM request logs,
and validated enrichment artifacts.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


def _timestamp() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
        .replace(":", "-")
    )


def _sanitize(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in value)


def _compute_hash(payload: Any) -> str:
    data = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


@dataclass
class SnapshotMetadata:
    path: Path
    hash: str
    timestamp: str


class CanonicalDataManager:
    """Manages canonical crate snapshots and LLM exchange logs."""

    MAX_PAYLOAD_BYTES = 400_000  # ~400 KB safety warning

    def __init__(self, base_output_dir: str, logger: Optional[logging.Logger] = None):
        self.base_output = Path(base_output_dir)
        self.logger = logger or logging.getLogger(__name__)

    def _crate_root(self, crate_name: str, crate_version: str) -> Path:
        return (
            self.base_output
            / "crates"
            / _sanitize(crate_name)
            / _sanitize(crate_version or "unspecified")
        )

    def save_snapshot(
        self, crate_name: str, crate_version: str, snapshot: Dict[str, Any]
    ) -> SnapshotMetadata:
        """Persist raw crate snapshot before any LLM interaction."""
        crate_root = self._crate_root(crate_name, crate_version)
        snapshot_dir = crate_root / "snapshots"
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        snapped_at = _timestamp()
        snapshot_hash = _compute_hash(snapshot)
        snapshot_path = snapshot_dir / f"crate_snapshot_{snapped_at}.json"

        payload = {
            "snapshot": snapshot,
            "metadata": {
                "crate": crate_name,
                "version": crate_version,
                "hash": snapshot_hash,
                "captured_at": snapped_at,
            },
        }
        snapshot_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        self.logger.info(
            "Saved canonical snapshot for %s@%s → %s",
            crate_name,
            crate_version,
            snapshot_path,
        )

        return SnapshotMetadata(path=snapshot_path, hash=snapshot_hash, timestamp=snapped_at)

    def log_llm_request(
        self,
        crate_name: str,
        crate_version: str,
        *,
        system_prompt: str,
        user_prompt: str,
        payload: Dict[str, Any],
        provider: str,
        model: str,
    ) -> Dict[str, Any]:
        """Persist raw LLM request payloads for replay/debugging."""
        crate_root = self._crate_root(crate_name, crate_version)
        log_dir = crate_root / "llm_requests"
        log_dir.mkdir(parents=True, exist_ok=True)

        serialized_payload = json.dumps(payload, ensure_ascii=False, indent=2)
        payload_bytes = len(serialized_payload.encode("utf-8"))
        truncated = payload_bytes > self.MAX_PAYLOAD_BYTES

        log_path = log_dir / f"request_{_timestamp()}.json"
        log_body = {
            "provider": provider,
            "model": model,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "payload": payload,
            "payload_bytes": payload_bytes,
            "payload_warning": (
                "Payload exceeds recommended size; risk of truncation"
                if truncated
                else "ok"
            ),
            "logged_at": _timestamp(),
        }
        log_path.write_text(json.dumps(log_body, ensure_ascii=False, indent=2), encoding="utf-8")

        if truncated:
            self.logger.warning(
                "LLM payload for %s@%s is %s bytes (>%s). Provider may truncate input.",
                crate_name,
                crate_version,
                payload_bytes,
                self.MAX_PAYLOAD_BYTES,
            )

        return {
            "request_path": log_path,
            "payload_bytes": payload_bytes,
            "truncated": truncated,
        }

    def log_llm_response(
        self,
        crate_name: str,
        crate_version: str,
        response: Dict[str, Any],
    ) -> Path:
        """Persist raw LLM responses."""
        crate_root = self._crate_root(crate_name, crate_version)
        log_dir = crate_root / "llm_responses"
        log_dir.mkdir(parents=True, exist_ok=True)

        log_path = log_dir / f"response_{_timestamp()}.json"
        log_path.write_text(json.dumps(response, ensure_ascii=False, indent=2), encoding="utf-8")
        return log_path

    def save_validated_output(
        self,
        crate_name: str,
        crate_version: str,
        validated_payload: Dict[str, Any],
    ) -> Path:
        """Persist validator-approved enrichment results."""
        crate_root = self._crate_root(crate_name, crate_version)
        validated_dir = crate_root / "validated"
        validated_dir.mkdir(parents=True, exist_ok=True)

        validated_path = validated_dir / f"validated_{_timestamp()}.json"
        validated_path.write_text(
            json.dumps(validated_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self.logger.info(
            "Saved validated enrichment for %s@%s → %s",
            crate_name,
            crate_version,
            validated_path,
        )
        return validated_path

    def save_manual_review(
        self,
        crate_name: str,
        crate_version: str,
        reason: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Path:
        """Persist manual-review records when validation fails."""
        crate_root = self._crate_root(crate_name, crate_version)
        review_dir = crate_root / "manual_review"
        review_dir.mkdir(parents=True, exist_ok=True)

        review_payload = {
            "reason": reason,
            "timestamp": _timestamp(),
            "context": context or {},
        }
        review_path = review_dir / f"manual_review_{_timestamp()}.json"
        review_path.write_text(
            json.dumps(review_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self.logger.warning(
            "Manual review required for %s@%s (%s)",
            crate_name,
            crate_version,
            reason,
        )
        return review_path

