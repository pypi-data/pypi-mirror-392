"""
Analysis coordination functions for UnifiedSigilPipeline.

Extracted from unified_pipeline.py to reduce file size and improve maintainability.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import ValidationError

from .exceptions import PipelineError
from .core import TrustVerdict
from .schemas import DocumentationResults
from .scraping import ScrapingResult
from .utils.sanitization import sanitize_documentation_dict

logger = logging.getLogger(__name__)


async def perform_sacred_chain_analysis(
    irl_engine: Any,
    sanitizer: Any,
    crate_name: str,
    crate_version: str,
    documentation_results: Dict[str, ScrapingResult],
    fetched_metadata: Optional[Dict[str, Any]],
    summarize_code_snippets: Any,  # Callable
    add_crate_analysis_results: Any,  # Callable
    add_llm_enrichment: Any,  # Callable
    logger: logging.Logger,
    ml_predictions: Optional[Dict[str, Any]] = None,
) -> Any:  # SacredChainTrace
    """Perform Sacred Chain analysis for a crate."""
    if not irl_engine:
        raise RuntimeError("IRL Engine not initialized")

    logger.info("Performing Sacred Chain analysis for %s", crate_name)

    try:
        # Convert dataclass ScrapingResult objects to dictionaries for validation
        # The DocumentationResults model expects Pydantic ScrapingResult objects
        converted_results = {}
        for source, result in documentation_results.items():
            if result is None:
                converted_results[source] = None
            else:
                # Convert dataclass to dict format expected by Pydantic model
                converted_results[source] = {
                    "url": result.url,
                    "content": result.content,
                    "error": result.error,
                    "status_code": None,  # Not available in dataclass version
                }

        # Validate the documentation results
        try:
            validated_docs = DocumentationResults.model_validate(converted_results)
        except ValidationError as e:
            # Provide specific error context about which fields failed validation
            error_details = []
            for error in e.errors():
                field_path = " -> ".join(str(loc) for loc in error["loc"])
                error_type = error["type"]
                error_msg = error["msg"]
                error_details.append(
                    f"Field '{field_path}': {error_type} - {error_msg}"
                )

            error_summary = "; ".join(error_details)
            logger.error(f"Documentation results validation failed: {error_summary}")
            raise PipelineError(
                f"Documentation results validation failed: {error_summary}"
            )

        # First sanitize PII/secrets if enabled
        sanitized_docs = sanitizer.sanitize_data(validated_docs.model_dump())
        # Then sanitize and truncate documentation content
        sanitized_docs = sanitize_documentation_dict(
            sanitized_docs, max_words=500, max_bytes=4096
        )

        # Prepare context for IRL engine analysis
        irl_context = {}
        if fetched_metadata:
            irl_context["metadata"] = fetched_metadata
            irl_context["repository_url"] = fetched_metadata.get("repository")
            # Extract README from documentation results
            # Priority: github_repo > docs_rs > lib_rs > crates_io > any other source
            readme_content = ""
            sources_priority = ["github_repo", "github", "docs_rs", "lib_rs", "crates_io"]
            
            # First, try priority sources
            for priority_source in sources_priority:
                for source, result in documentation_results.items():
                    if priority_source in source.lower() and result and result.content:
                        content = result.content[:10000]  # Limit size
                        if len(content.strip()) > 100:  # Ensure meaningful content
                            readme_content = content
                            logger.debug(f"Using README from {source} ({len(content)} chars)")
                            break
                if readme_content:
                    break
            
            # Fallback: use any source with content if priority sources didn't work
            if not readme_content:
                for source, result in documentation_results.items():
                    if result and result.content:
                        content = result.content[:10000]
                        if len(content.strip()) > 100:
                            readme_content = content
                            logger.debug(f"Using README from fallback source {source} ({len(content)} chars)")
                            break
            
            irl_context["readme"] = readme_content
            if readme_content:
                logger.debug(f"Extracted README content: {len(readme_content)} chars for {crate_name}")
            else:
                logger.warning(f"No README content found for {crate_name}")
        
        # Add sanitized documentation to context for ecosystem analyzer (for parsing lib.rs content)
        irl_context["sanitized_documentation"] = sanitized_docs
        
        # Add ML predictions to context if available
        if ml_predictions:
            irl_context["ml_predictions"] = ml_predictions
        
        async with irl_engine as irl_engine_instance:
            trace = await irl_engine_instance.analyze_with_sacred_chain(
                crate_name, context=irl_context
            )

        # Storing sanitized docs in the trace for later use by enrichment functions
        trace.audit_info["sanitized_documentation"] = sanitized_docs

        # Store the fetched metadata in trace for later use (before enrichment)
        if fetched_metadata:
            trace.audit_info["fetched_crate_metadata"] = fetched_metadata

        snippet_summary = summarize_code_snippets(sanitized_docs)
        if snippet_summary:
            trace.audit_info["snippet_heuristics"] = snippet_summary

        await add_crate_analysis_results(crate_name, crate_version, trace)

        await add_llm_enrichment(crate_name, crate_version, trace)

        _enforce_validation_guards(trace)

        return trace

    except (RuntimeError, ValueError, KeyError) as e:
        logger.error("Sacred Chain analysis failed: %s", e)
        raise


def _enforce_validation_guards(trace: Any) -> None:
    """Force manual review when validation signals disagree with crawl data."""
    if not trace or not getattr(trace, "audit_info", None):
        return

    audit_info = trace.audit_info
    enriched = audit_info.get("enriched_crate") or {}
    fetched = audit_info.get("fetched_crate_metadata") or {}
    validation = (
        enriched.get("validation_summary")
        or audit_info.get("validation_summary")
        or {}
    )

    issues: List[str] = []

    status = validation.get("status")
    if not status:
        issues.append("LLM validation summary missing")
    elif status != "validated":
        issues.append(f"Validation status={status}")

    if validation.get("issues"):
        issues.extend(str(item) for item in validation["issues"])

    speculative = validation.get("speculative_fields") or []
    if speculative:
        issues.append(f"Speculative fields present: {', '.join(speculative)}")

    fetched_version = fetched.get("version")
    enriched_version = enriched.get("version")
    if (
        fetched_version
        and enriched_version
        and fetched_version != enriched_version
    ):
        issues.append(
            f"Version mismatch (crawl={fetched_version}, enriched={enriched_version})"
        )

    fetched_downloads = fetched.get("downloads")
    enriched_downloads = (
        enriched.get("analysis", {}).get("estimated_downloads")
        if isinstance(enriched.get("analysis"), dict)
        else None
    )
    if (
        fetched_downloads is not None
        and enriched_downloads is not None
        and fetched_downloads != enriched_downloads
    ):
        issues.append("Downloads mismatch between crawl and enrichment")

    if issues:
        guard_reason = "; ".join(issues)
        trace.reasoning_steps.append(f"Validation guard triggered: {guard_reason}")
        trace.suggestion = "DEFER: validation guard triggered"
        trace.verdict = TrustVerdict.DEFER
        audit_info.setdefault("validation_guard", {})["issues"] = issues

