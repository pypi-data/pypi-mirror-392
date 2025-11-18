from __future__ import annotations

"""
Utility helpers for safely converting complex/third-party objects into
JSON-serialisable data.

This is mainly needed because some libraries (e.g. LiteLLM) return custom
objects like `MarkdownGenerationResult` that don't implement a standard
`__iter__`/`__dict__`/`to_dict` interface.  Downstream code (our CLI and
report generator) can import `to_serializable` when they need to dump
arbitrary nested structures with `json`.
"""

from typing import Any, Dict, List

_PRIMITIVES = (str, int, float, bool, type(None))

try:
    from litellm.utils import MarkdownGenerationResult  # type: ignore
except ImportError:  # pragma: no cover
    MarkdownGenerationResult = None  # type: ignore


def to_serializable(obj: Any) -> Any:  # noqa: ANN401 – generic helper
    """Recursively convert *obj* into something that ``json`` can dump.

    Rules (in order):
    1. Primitive types are returned unchanged.
    2. ``dict`` values and ``list`` / ``tuple`` items are processed recursively.
    3. An object with a ``dict()`` or ``to_dict()`` method is replaced by that
       representation.
    4. Fallback: use ``str(obj)``.
    """
    if isinstance(obj, _PRIMITIVES):
        return obj

    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}

    if isinstance(obj, (list, tuple, set)):
        return [to_serializable(i) for i in obj]

    if hasattr(obj, "to_dict"):
        try:
            return to_serializable(obj.to_dict())
        except Exception:  # pragma: no cover – be permissive
            pass
    elif hasattr(obj, "__dict__"):
        return to_serializable(obj.__dict__)

    # Specific library objects
    if MarkdownGenerationResult is not None and isinstance(
        obj, MarkdownGenerationResult
    ):
        # Prefer the plain markdown string; fall back to str(obj)
        try:
            return obj.raw_markdown  # type: ignore[attr-defined]
        except Exception:
            return str(obj)

    # Last resort: stringify
    return str(obj)


def add_field_explanations(enriched_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add explanations for null/empty fields to help LLM training data.
    
    This function analyzes the enriched crate data and adds a 'field_explanations'
    section that explains why certain fields are null or empty. This is important
    for LLM training data to distinguish between:
    - Fields that are null by design (e.g., target field for platform-agnostic deps)
    - Fields that are empty because no data was available
    - Fields that are legitimately empty (e.g., no keywords)
    
    Args:
        enriched_data: The enriched crate data dictionary
        
    Returns:
        The enriched data dictionary with a 'field_explanations' key added
    """
    explanations: Dict[str, str] = {}
    
    # Check top-level fields
    if not enriched_data.get("readme"):
        explanations["readme"] = (
            "Empty because README content was not successfully scraped from "
            "crates.io, docs.rs, lib.rs, or GitHub. This may indicate scraping "
            "failures or the crate may not have a README file."
        )
    
    if not enriched_data.get("keywords"):
        explanations["keywords"] = (
            "Empty array because the crate has no keywords assigned on crates.io. "
            "This is common for older crates or crates that haven't been updated "
            "with metadata."
        )
    
    if not enriched_data.get("categories"):
        explanations["categories"] = (
            "Empty array because the crate has no categories assigned on crates.io. "
            "Categories help users discover crates but are optional metadata."
        )
    
    if enriched_data.get("librs_downloads") is None:
        explanations["librs_downloads"] = (
            "Null because lib.rs download statistics were not available. This could "
            "mean the crate is not listed on lib.rs, scraping failed, or lib.rs "
            "doesn't provide download stats for this crate."
        )
    
    if not enriched_data.get("license"):
        explanations["license"] = (
            "Null or empty because license information was not available from crates.io API. "
            "This may indicate the crate doesn't declare a license in Cargo.toml, or the "
            "license field was not successfully fetched. License information is important "
            "for compliance and legal use of the crate."
        )
    
    if not enriched_data.get("code_snippets"):
        explanations["code_snippets"] = (
            "Empty array because no code snippets were extracted from documentation. "
            "This may indicate that the documentation doesn't contain code examples, "
            "or the extraction process didn't find suitable snippets."
        )
    
    if not enriched_data.get("readme_sections"):
        explanations["readme_sections"] = (
            "Empty object because README content was not available to parse into "
            "sections. This field would contain structured sections if README "
            "parsing was successful."
        )
    
    if not enriched_data.get("enhanced_scraping"):
        explanations["enhanced_scraping"] = (
            "Empty object because enhanced scraping (using Crawl4AI with LLM extraction) "
            "was not performed or did not return additional structured data beyond "
            "standard scraping."
        )
    
    if not enriched_data.get("enhanced_features"):
        explanations["enhanced_features"] = (
            "Empty array because no additional features were discovered through "
            "enhanced analysis beyond what's declared in Cargo.toml."
        )
    
    if not enriched_data.get("enhanced_dependencies"):
        explanations["enhanced_dependencies"] = (
            "Empty array because no additional dependencies were discovered through "
            "enhanced analysis beyond what's declared in Cargo.toml."
        )
    
    # Check dependency target fields
    dependencies = enriched_data.get("dependencies", [])
    if dependencies:
        null_target_count = sum(1 for dep in dependencies if dep.get("target") is None)
        if null_target_count > 0:
            explanations["dependencies[].target"] = (
                f"Null for {null_target_count} out of {len(dependencies)} dependencies "
                "because these dependencies are platform-agnostic (apply to all platforms). "
                "A null target means the dependency is required on all platforms. "
                "Platform-specific dependencies would have a target string like "
                "'i686-pc-windows-gnu' or 'cfg(target_os = \"windows\")'."
            )
    
    # Check security vulnerabilities
    security = enriched_data.get("security", {})
    if isinstance(security, dict):
        vulnerabilities = security.get("vulnerabilities", [])
        if not vulnerabilities:
            explanations["security.vulnerabilities"] = (
                "Empty array because no known critical security vulnerabilities were found "
                "for this crate version in the RustSec advisory database. This is a positive "
                "indicator, but note that absence of reported vulnerabilities does not "
                "guarantee security - it means no vulnerabilities have been publicly reported "
                "and added to the advisory database. Users should still exercise caution and "
                "review the crate's security practices."
            )
    
    # Check source_analysis security_concerns
    source_analysis = enriched_data.get("source_analysis", {})
    if isinstance(source_analysis, dict):
        security_concerns = source_analysis.get("security_concerns", [])
        if not security_concerns:
            explanations["source_analysis.security_concerns"] = (
                "Empty array because the LLM analysis did not identify any specific "
                "security concerns. This is based on analysis of documentation and "
                "metadata, not a comprehensive security audit."
            )
    
    # Only add explanations if we found any
    if explanations:
        enriched_data["field_explanations"] = explanations
    
    return enriched_data
