"""
LLM enrichment functions for UnifiedSigilPipeline.

Extracted from unified_pipeline.py to reduce file size and improve maintainability.
"""

import logging
from typing import Any, Dict, List, Optional

from .config import CrateMetadata

logger = logging.getLogger(__name__)


def ensure_int(value: Any, default: Optional[int] = None) -> Optional[int]:
    """Best-effort conversion of numeric metadata to integers."""
    if value is None:
        return default

    if isinstance(value, bool):
        return default

    if isinstance(value, (int, float)):
        return int(value)

    if isinstance(value, str):
        cleaned = value.replace(",", "").strip()
        if not cleaned:
            return default
        try:
            return int(float(cleaned))
        except ValueError:
            return default

    return default


def coerce_to_list(value: Any) -> List[Any]:
    """Convert metadata values to lists when appropriate."""
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    if isinstance(value, (set, frozenset)):
        return list(value)

    if isinstance(value, str):
        return [value]

    return []


def extract_metadata_from_scrape(
    scraped_data: Dict[str, Any],
    fallback_description: str,
) -> Dict[str, Any]:
    """Collect crate metadata fields from scraped documentation results."""

    crates_io_data = {}
    if isinstance(scraped_data, dict):
        crates_io_data = scraped_data.get("crates_io") or {}

    metadata_sources: List[Dict[str, Any]] = []
    structured_data = crates_io_data.get("structured_data")
    if isinstance(structured_data, dict):
        crate_section = structured_data.get("crate")
        if isinstance(crate_section, dict):
            metadata_sources.append(crate_section)
        metadata_sources.append(structured_data)

    for key in ("metadata", "data"):
        section = crates_io_data.get(key)
        if isinstance(section, dict):
            metadata_sources.append(section)

    if isinstance(crates_io_data, dict):
        metadata_sources.append(crates_io_data)

    combined: Dict[str, Any] = {}
    for source in metadata_sources:
        combined.update(source)

    description = combined.get("description") or fallback_description
    repository = combined.get("repository") or combined.get("repo") or ""
    keywords = coerce_to_list(combined.get("keywords"))
    categories = coerce_to_list(combined.get("categories"))

    downloads: Optional[int] = combined.get("downloads")
    if downloads is None:
        downloads = combined.get("downloads_total") or combined.get("download_count")

    if downloads is None:
        stats_section = combined.get("stats")
        if isinstance(stats_section, dict):
            downloads = (
                stats_section.get("downloads")
                or stats_section.get("downloads_total")
                or stats_section.get("total_downloads")
            )

    downloads = ensure_int(downloads, default=0)

    dependencies = combined.get("dependencies")
    if not isinstance(dependencies, list):
        dependencies = []

    features = combined.get("features")
    if not isinstance(features, dict):
        features = {}

    librs_downloads: Optional[int] = None
    lib_rs_data = scraped_data.get("lib_rs") if isinstance(scraped_data, dict) else None
    if isinstance(lib_rs_data, dict):
        lib_rs_structured = lib_rs_data.get("structured_data")
        if isinstance(lib_rs_structured, dict):
            stats_section = lib_rs_structured.get("stats")
            if isinstance(stats_section, dict):
                librs_downloads = (
                    stats_section.get("downloads")
                    or stats_section.get("downloads_total")
                    or stats_section.get("total_downloads")
                )

            if librs_downloads is None:
                librs_downloads = lib_rs_structured.get("downloads")

        if librs_downloads is None:
            librs_downloads = lib_rs_data.get("downloads")

    librs_downloads = ensure_int(librs_downloads)

    return {
        "description": description,
        "repository": repository,
        "keywords": keywords,
        "categories": categories,
        "downloads": downloads,
        "dependencies": dependencies,
        "features": features,
        "librs_downloads": librs_downloads,
    }


def extract_readme_content(scraped_data: Dict[str, Any], logger: logging.Logger) -> str:
    """Extract the best available README content from scraped data"""
    # Priority order: docs.rs (most comprehensive) > lib.rs > crates.io
    sources_priority = ["docs_rs", "lib_rs", "crates_io"]

    for source in sources_priority:
        source_result = scraped_data.get(source)
        if not source_result:
            continue

        if isinstance(source_result, dict):
            error = source_result.get("error")
            readme_text = source_result.get("content")
        else:
            error = getattr(source_result, "error", None)
            readme_text = getattr(source_result, "content", None)

        if error:
            continue

        if (
            readme_text
            and isinstance(readme_text, str)
            and len(readme_text.strip()) > 100
        ):
            logger.info(
                f"[README] Using README content from {source} ({len(readme_text)} chars)"
            )
            return readme_text

    # Fallback: return first available content (don't concatenate duplicates)
    # The sources usually contain the same README, so concatenating wastes tokens
    for source in sources_priority:
        source_result = scraped_data.get(source)
        if not source_result:
            continue

        if isinstance(source_result, dict):
            error = source_result.get("error")
            content = source_result.get("content")
        else:
            error = getattr(source_result, "error", None)
            content = getattr(source_result, "content", None)

        if not error and content and isinstance(content, str) and len(content.strip()) > 100:
            logger.info(
                f"[README] Using README content from {source} (fallback, {len(content)} chars)"
            )
            return content

    logger.warning("[README] No README content found in scraped data")
    return ""


async def add_unified_llm_enrichment(
    unified_llm_processor: Any,
    sanitizer: Any,
    crate_name: str,
    crate_version: str,
    trace: Any,  # SacredChainTrace
    logger: logging.Logger,
) -> None:
    """Add enrichment using unified LLM processor"""
    if not unified_llm_processor:
        return

    try:
        logger.info("Adding unified LLM enrichment for %s", crate_name)

        # Get scraped data from trace
        scraped_data = trace.audit_info.get("sanitized_documentation", {})
        
        # Get fetched metadata from API (preferred source)
        fetched_metadata = trace.audit_info.get("fetched_crate_metadata", {})
        
        # Extract metadata from scrape (fallback)
        metadata_fields = extract_metadata_from_scrape(
            scraped_data,
            trace.suggestion or "No description available",
        )
        
        # Prefer fetched metadata over scraped metadata for key fields
        if fetched_metadata:
            logger.info(f"Using fetched metadata for {crate_name}: downloads={fetched_metadata.get('downloads', 0)}, deps={len(fetched_metadata.get('dependencies', []))}, features={len(fetched_metadata.get('features', {}))}, github_stars={fetched_metadata.get('github_stars', 0)}")
        else:
            logger.warning(f"No fetched metadata available for {crate_name}, using scraped data only")
        
        if fetched_metadata:
            # Use fetched metadata as primary source
            metadata_fields.update({
                "downloads": fetched_metadata.get("downloads", metadata_fields.get("downloads", 0)),
                "dependencies": fetched_metadata.get("dependencies", metadata_fields.get("dependencies", [])),
                "features": fetched_metadata.get("features", metadata_fields.get("features", {})),
                "repository": fetched_metadata.get("repository", metadata_fields.get("repository", "")),
                "github_stars": fetched_metadata.get("github_stars", 0),
                "license": fetched_metadata.get("license"),  # Include license from API
            })
            # Update description if fetched one is better
            if fetched_metadata.get("description") and len(fetched_metadata.get("description", "")) > len(metadata_fields.get("description", "")):
                metadata_fields["description"] = fetched_metadata.get("description")
            # Update keywords and categories if fetched ones are available
            if fetched_metadata.get("keywords"):
                metadata_fields["keywords"] = fetched_metadata.get("keywords")
            if fetched_metadata.get("categories"):
                metadata_fields["categories"] = fetched_metadata.get("categories")
            
            # Convert features from list format to dict format if needed
            features = metadata_fields.get("features", {})
            if isinstance(features, list):
                # Convert from [{"name": k, "dependencies": v}] to {k: v}
                features_dict = {}
                for feat in features:
                    if isinstance(feat, dict):
                        feat_name = feat.get("name")
                        feat_deps = feat.get("dependencies", [])
                        if feat_name:
                            features_dict[feat_name] = feat_deps if isinstance(feat_deps, list) else []
                metadata_fields["features"] = features_dict

        # Extract README content from multiple sources
        readme_content = extract_readme_content(scraped_data, logger)

        crate_metadata = CrateMetadata(
            name=crate_name,
            version=crate_version,
            description=metadata_fields["description"],
            repository=metadata_fields["repository"],
            keywords=metadata_fields["keywords"],
            categories=metadata_fields["categories"],
            readme=readme_content,
            downloads=metadata_fields["downloads"],
            github_stars=metadata_fields.get("github_stars", 0),
            dependencies=metadata_fields["dependencies"],
            features=metadata_fields["features"],
            code_snippets=[],
            readme_sections={},
            librs_downloads=metadata_fields["librs_downloads"],
            license=metadata_fields.get("license"),
            source="crates.io",
            enhanced_scraping={},
            enhanced_features=[],
            enhanced_dependencies=[],
        )

        # Store the metadata used for enrichment
        trace.audit_info["crate_metadata"] = crate_metadata.to_dict()

        # Enrich the crate using unified LLM processor
        enriched_crate = await unified_llm_processor.process_crate(crate_metadata)

        # Add enrichment results to trace - handle different return types safely
        if hasattr(enriched_crate, "to_dict"):
            trace.audit_info["enriched_crate"] = sanitizer.sanitize_data(
                enriched_crate.to_dict()
            )
        elif isinstance(enriched_crate, dict):
            trace.audit_info["enriched_crate"] = sanitizer.sanitize_data(
                enriched_crate
            )
        else:
            # Convert object to dict using vars() or dataclass fields
            try:
                if hasattr(enriched_crate, "__dict__"):
                    trace.audit_info["enriched_crate"] = sanitizer.sanitize_data(
                        vars(enriched_crate)
                    )
                else:
                    trace.audit_info["enriched_crate"] = {
                        "enrichment_status": "completed",
                        "type": str(type(enriched_crate)),
                    }
            except Exception as serialization_error:
                logger.warning(
                    f"Could not serialize enriched crate: {serialization_error}"
                )
                trace.audit_info["enriched_crate"] = {
                    "enrichment_status": "completed_but_not_serializable"
                }

        logger.info("Enriched data for %s using Unified LLM", crate_name)

    except (RuntimeError, ValueError, AttributeError) as e:
        logger.warning("Failed to add unified LLM enrichment: %s", e)


async def add_azure_openai_enrichment(
    ai_enricher: Any,
    sanitizer: Any,
    crate_name: str,
    trace: Any,  # SacredChainTrace
    logger: logging.Logger,
) -> None:
    """Add enrichment using Azure OpenAI"""
    if not ai_enricher:
        return

    try:
        logger.info("Adding Azure OpenAI enrichment for %s", crate_name)

        # Get scraped data from trace
        scraped_data = trace.audit_info.get("sanitized_documentation", {})
        metadata_fields = extract_metadata_from_scrape(
            scraped_data,
            trace.suggestion or "No description available",
        )

        # Extract README content from multiple sources
        readme_content = extract_readme_content(scraped_data, logger)

        crate_metadata = CrateMetadata(
            name=crate_name,
            version="unknown",
            description=metadata_fields["description"],
            repository=metadata_fields["repository"],
            keywords=metadata_fields["keywords"],
            categories=metadata_fields["categories"],
            readme=readme_content,
            downloads=metadata_fields["downloads"],
            github_stars=0,
            dependencies=metadata_fields["dependencies"],
            features=metadata_fields["features"],
            code_snippets=[],
            readme_sections={},
            librs_downloads=metadata_fields["librs_downloads"],
            license=metadata_fields.get("license"),
            source="crates.io",
            enhanced_scraping={},
            enhanced_features=[],
            enhanced_dependencies=[],
        )

        # Store the metadata used for enrichment
        trace.audit_info["crate_metadata"] = crate_metadata.to_dict()

        # Enrich the crate using Azure OpenAI
        enriched_crate = await ai_enricher.enrich_crate(crate_metadata)

        # Add enrichment results to trace
        trace.audit_info["enriched_crate"] = sanitizer.sanitize_data(
            enriched_crate.to_dict()
        )
        logger.info("Enriched data for %s using Azure OpenAI", crate_name)

    except (RuntimeError, ValueError, AttributeError) as e:
        logger.warning("Failed to add Azure OpenAI enrichment: %s", e)

