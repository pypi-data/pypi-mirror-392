"""
Manifest Generator for Pipeline Outputs

Generates Rule-Zero compliant manifests for all pipeline outputs, including:
- Pipeline version and commit hash
- Input data hash
- Generator metadata
- Reproducibility information
"""

import hashlib
import json
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

log = logging.getLogger(__name__)


def get_git_commit_hash() -> Optional[str]:
    """Get the current git commit hash."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        pass
    return None


def get_pipeline_version() -> str:
    """Get the pipeline version from pyproject.toml or __init__.py."""
    try:
        # Try pyproject.toml first
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        if pyproject_path.exists():
            import tomli
            with open(pyproject_path, "rb") as f:
                data = tomli.load(f)
                version = data.get("project", {}).get("version")
                if version:
                    return str(version)
    except Exception:
        pass
    
    try:
        # Fallback to __init__.py
        init_path = Path(__file__).parent.parent / "__init__.py"
        if init_path.exists():
            content = init_path.read_text(encoding="utf-8")
            for line in content.split("\n"):
                if line.startswith("__version__"):
                    version = line.split("=")[1].strip().strip('"').strip("'")
                    return version
    except Exception:
        pass
    
    return "unknown"


def compute_data_hash(data: Any) -> str:
    """Compute SHA-256 hash of data (JSON-serializable)."""
    json_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(json_str.encode("utf-8")).hexdigest()


def generate_manifest(
    output_type: str,
    input_data: Any,
    output_data: Optional[Any] = None,
    generator_info: Optional[Dict[str, Any]] = None,
    additional_metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate a Rule-Zero compliant manifest for pipeline output.
    
    Args:
        output_type: Type of output (e.g., "teaching_bundle", "training_dataset", "audit_log")
        input_data: Input data (crate name, list of crates, etc.)
        output_data: Optional output data to hash
        generator_info: Optional generator-specific metadata
        additional_metadata: Optional additional metadata to include
    
    Returns:
        Manifest dictionary
    """
    commit_hash = get_git_commit_hash()
    version = get_pipeline_version()
    
    # Compute input hash
    if isinstance(input_data, str):
        input_hash = hashlib.sha256(input_data.encode("utf-8")).hexdigest()
    elif isinstance(input_data, list):
        input_hash = compute_data_hash(sorted(input_data))
    else:
        input_hash = compute_data_hash(input_data)
    
    # Compute output hash if provided
    output_hash = None
    if output_data is not None:
        output_hash = compute_data_hash(output_data)
    
    manifest = {
        "manifest_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "pipeline_version": version,
        "commit_hash": commit_hash,
        "output_type": output_type,
        "input_data_hash": input_hash,
        "generator": {
            "name": "rust_crate_pipeline",
            "version": version,
            "commit": commit_hash,
        },
    }
    
    if output_hash:
        manifest["output_data_hash"] = output_hash
    
    if generator_info:
        manifest["generator_info"] = generator_info
    
    if additional_metadata:
        manifest["metadata"] = additional_metadata
    
    return manifest


def attach_manifest_to_output(
    output_path: Path,
    output_type: str,
    input_data: Any,
    output_data: Optional[Any] = None,
    generator_info: Optional[Dict[str, Any]] = None,
    additional_metadata: Optional[Dict[str, Any]] = None,
) -> Path:
    """
    Generate a manifest and save it alongside the output file.
    
    Args:
        output_path: Path to the output file
        output_type: Type of output
        input_data: Input data
        output_data: Optional output data
        generator_info: Optional generator info
        additional_metadata: Optional additional metadata
    
    Returns:
        Path to the manifest file
    """
    manifest = generate_manifest(
        output_type=output_type,
        input_data=input_data,
        output_data=output_data,
        generator_info=generator_info,
        additional_metadata=additional_metadata,
    )
    
    manifest_path = output_path.parent / f"{output_path.stem}.manifest.json"
    
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    log.info(f"Generated manifest: {manifest_path}")
    return manifest_path


def load_manifest(manifest_path: Path) -> Optional[Dict[str, Any]]:
    """Load a manifest from a file."""
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log.warning(f"Failed to load manifest from {manifest_path}: {e}")
        return None


def verify_manifest_integrity(
    manifest: Dict[str, Any], output_data: Any
) -> bool:
    """
    Verify that the manifest's output hash matches the actual output data.
    
    Returns:
        True if hash matches, False otherwise
    """
    expected_hash = manifest.get("output_data_hash")
    if not expected_hash:
        return True  # No hash to verify
    
    actual_hash = compute_data_hash(output_data)
    return expected_hash == actual_hash
