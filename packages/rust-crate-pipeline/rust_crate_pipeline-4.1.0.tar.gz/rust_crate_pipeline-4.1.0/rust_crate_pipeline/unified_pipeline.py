from __future__ import annotations

import argparse
import asyncio
import gzip
import json
import logging
import os
import re
import tarfile
import tempfile
import time
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

# Suppress Windows-specific asyncio resource warnings
if os.name == "nt":  # Windows
    warnings.filterwarnings("ignore", category=ResourceWarning, module="asyncio")

import aiohttp
import aiofiles

from .utils.sanitization import Sanitizer, sanitize_documentation_dict
from .utils.manifest_generator import generate_manifest, attach_manifest_to_output
from .version import __version__
from .utils.serialization_utils import to_serializable
from .pipeline_enrichment import (
    add_unified_llm_enrichment,
    add_azure_openai_enrichment,
    extract_metadata_from_scrape,
    extract_readme_content,
)
from .pipeline_analysis import perform_sacred_chain_analysis

from pydantic import ValidationError
from .config import CrateMetadata, PipelineConfig
from .pipeline import CrateDataPipeline
from .core import CanonRegistry, IRLEngine, SacredChainTrace, TrustVerdict
from .crate_analysis import CrateAnalyzer
from .exceptions import PipelineError, SecurityException
from .schemas import DocumentationResults
from .scraping import ScrapingResult, UnifiedScraper
from .quality.heuristics import complexity_score, detect_topics, get_quality_checker
from .utils.subprocess_utils import (
    run_command_with_cleanup,
    setup_asyncio_windows_fixes,
)
from .utils.validation import validate_crate_name, validate_crate_version
from .exceptions import ValidationError as PipelineValidationError

# Set up Windows-specific asyncio fixes
setup_asyncio_windows_fixes()

# Import unified LLM processor
try:
    from .llm_client import LLMConfig
    from .llm_factory import create_llm_client_from_config
    from .unified_llm_processor import UnifiedLLMProcessor

    UNIFIED_LLM_AVAILABLE = True
except ImportError:
    UNIFIED_LLM_AVAILABLE = False
    UnifiedLLMProcessor = None
    create_llm_client_from_config = None
    LLMConfig = None

# Import advanced caching system (moved to experimental/future_modules)
try:
    import sys
    from pathlib import Path
    experimental_path = Path(__file__).parent.parent.parent / "experimental" / "future_modules"
    if str(experimental_path) not in sys.path:
        sys.path.insert(0, str(experimental_path))
    import advanced_cache

    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    advanced_cache = None

# Import ML quality predictor
try:
    from .ml import quality_predictor

    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    quality_predictor = None

if TYPE_CHECKING:
    # Azure OpenAI support is now handled through UnifiedLLMProcessor
    from .llm_client import LLMConfig
    from .unified_llm_processor import UnifiedLLMProcessor


class UnifiedSigilPipeline:
    """
    Unified Sigil Pipeline for comprehensive Rust crate analysis.

    This pipeline orchestrates the analysis of Rust crates using multiple
    components including IRL engine, web scraping, LLM processing, caching,
    and ML quality prediction.

    Usage:
        config = PipelineConfig()
        pipeline = UnifiedSigilPipeline(config)
        async with pipeline:
            trace = await pipeline.analyze_crate("serde")
    """

    def __init__(
        self, config: PipelineConfig, llm_config: Optional[Any] = None
    ) -> None:
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.irl_engine: Optional[IRLEngine] = None
        self.scraper: Optional[UnifiedScraper] = None
        self.canon_registry: CanonRegistry = CanonRegistry()
        self.sanitizer = Sanitizer(enabled=False)

        # Initialize AI components
        self.ai_enricher: Optional[Any] = None
        self.unified_llm_processor: Optional[Any] = None
        self.crate_analyzer: Optional[CrateAnalyzer] = None

        # Initialize advanced components
        self.cache: Optional[Any] = None
        self.ml_predictor: Optional[Any] = None
        
        # Initialize license filter for compliance checking
        try:
            from .utils.license_filter import create_default_license_filter
            self.license_filter = create_default_license_filter()
            self.logger.info("License filter initialized")
        except (ImportError, AttributeError) as e:
            self.logger.warning("Failed to initialize license filter: %s", e)
            self.license_filter = None

        # Store LLM config for later use
        self.llm_config = llm_config
        self.sync_mode = getattr(config, "sync_mode", False)
        self.use_legacy_heuristics = getattr(config, "use_legacy_heuristics", False)
        self._snippet_quality = get_quality_checker(self.use_legacy_heuristics)

        self._initialize_components()

    def _initialize_components(self) -> None:
        try:
            # Initialize metrics collector
            try:
                from .utils.metrics import get_metrics_collector
                self.metrics_collector = get_metrics_collector(enable_prometheus=False)
                self.logger.info("Metrics collector initialized")
            except ImportError:
                self.metrics_collector = None
                self.logger.debug("Metrics collector not available")
            
            self.irl_engine = IRLEngine(self.config, self.canon_registry)
            self.logger.info("IRL Engine initialized successfully")

            # Initialize scraper
            try:
                self.scraper = UnifiedScraper()
                self.logger.info("Unified Scraper initialized successfully")
            except (ImportError, AttributeError, ValueError) as e:
                self.logger.warning("Failed to initialize scraper: %s", e)

            # Initialize unified LLM processor if available
            if UNIFIED_LLM_AVAILABLE:
                try:
                    processor_config = self.llm_config or self.config
                    if processor_config is None:
                        self.logger.warning(
                            "No configuration provided for UnifiedLLMProcessor; skipping"
                        )
                    else:
                        if UnifiedLLMProcessor is not None:
                            self.unified_llm_processor = UnifiedLLMProcessor(
                                processor_config
                            )
                            provider = "custom"
                            model = "unknown"
                            # Check if processor_config is an LLMConfig instance
                            if self.llm_config is not None:
                                # Try to get provider/model from llm_config
                                if hasattr(self.llm_config, "provider"):
                                    provider = getattr(self.llm_config, "provider", "custom")
                                if hasattr(self.llm_config, "model"):
                                    model = getattr(self.llm_config, "model", "unknown")
                            elif isinstance(processor_config, PipelineConfig):
                                if getattr(processor_config, "use_azure_openai", False):
                                    provider = "azure"
                                    model = getattr(
                                        processor_config,
                                        "azure_openai_deployment_name",
                                        "unknown",
                                    )
                                else:
                                    provider = getattr(
                                        processor_config, "llm_provider", "unknown"
                                    )
                                    model = getattr(
                                        processor_config, "llm_model", "unknown"
                                    )
                            self.logger.info(
                                "Unified LLM Processor initialized successfully "
                                "(provider=%s, model=%s)",
                                provider,
                                model,
                            )
                        else:
                            self.logger.warning("UnifiedLLMProcessor is not available")
                except (ImportError, AttributeError, ValueError, TypeError) as e:
                    self.logger.warning(
                        "Failed to initialize Unified LLM Processor: %s", e
                    )

            # Initialize Azure OpenAI enricher if configured (fallback)
            elif self.config.use_azure_openai:
                try:
                    # Initialize unified LLM enricher (handles all providers)
                    from .ai_processing import LLMEnricher

                    self.ai_enricher = LLMEnricher(self.config)
                    self.logger.info("Unified LLM enricher initialized successfully")
                except (ImportError, AttributeError, ValueError) as e:
                    self.logger.warning(
                        "Failed to initialize Azure OpenAI Enricher: %s", e
                    )

            # Initialize advanced caching system
            if CACHE_AVAILABLE and advanced_cache is not None:
                try:
                    self.cache = advanced_cache.get_cache()
                    self.logger.info("Advanced caching system initialized")
                except (AttributeError, ValueError) as e:
                    self.logger.warning("Failed to initialize cache: %s", e)

            # Initialize ML quality predictor
            if ML_AVAILABLE and quality_predictor is not None:
                try:
                    self.ml_predictor = quality_predictor.get_predictor()
                    self.logger.info("ML quality predictor initialized")
                except (AttributeError, ValueError) as e:
                    self.logger.warning("Failed to initialize ML predictor: %s", e)

        except (AttributeError, ValueError, TypeError) as e:
            self.logger.error("Failed to initialize pipeline components: %s", e)
            raise

    async def __aenter__(self) -> "UnifiedSigilPipeline":
        if self.irl_engine:
            await self.irl_engine.__aenter__()
        # Don't start scraper here - will be created per task
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any],
    ) -> None:
        if self.irl_engine:
            await self.irl_engine.__aexit__(exc_type, exc_val, exc_tb)
        # Scraper cleanup is handled per task

    async def analyze_crate(
        self, crate_name: str, crate_version: Optional[str] = None
    ) -> SacredChainTrace:
        # Validate and normalize crate name immediately to prevent path traversal
        # This must happen before any network calls or filesystem operations
        try:
            crate_name = validate_crate_name(crate_name)
        except PipelineValidationError as e:
            self.logger.error("Invalid crate name '%s': %s", crate_name, e)
            raise ValueError(f"Invalid crate name: {e}") from e

        self.logger.info("Starting analysis of crate: %s", crate_name)

        try:
            if crate_version is None:
                crate_version = await self._get_latest_crate_version(crate_name)
                if not crate_version:
                    raise RuntimeError(
                        f"Could not determine latest version for {crate_name}"
                    )
                # Validate API-returned version to prevent path traversal
                try:
                    crate_version = validate_crate_version(crate_version)
                except PipelineValidationError as e:
                    self.logger.error(
                        "Invalid version returned from API '%s': %s", crate_version, e
                    )
                    raise RuntimeError(
                        f"Invalid version format returned from API for {crate_name}: {e}"
                    ) from e
            else:
                # Validate user-provided crate version to prevent path traversal
                try:
                    crate_version = validate_crate_version(crate_version)
                except PipelineValidationError as e:
                    self.logger.error("Invalid crate version '%s': %s", crate_version, e)
                    raise ValueError(f"Invalid crate version: {e}") from e

            # Create a new scraper instance for this task to avoid browser context conflicts
            scraper_config = {
                "verbose": False,
                "word_count_threshold": 10,
                "crawl_config": {},
            }

            # Check cache first
            cache_key = f"crate_analysis:{crate_name}:{crate_version}"
            if self.cache:
                cached_result = self.cache.get(cache_key)
                if asyncio.iscoroutine(cached_result):
                    cached_result = await cached_result
                if cached_result:
                    self.logger.info("Using cached analysis for %s", crate_name)
                    return cached_result

            async with UnifiedScraper(scraper_config) as scraper:
                # Fetch crate metadata to get repository URL and full data
                crate_metadata_dict = await self._fetch_crate_metadata(crate_name)
                
                # Check license compliance before processing
                license_result = None
                if crate_metadata_dict:
                    license_result = self._check_license_compliance(
                        crate_name, crate_metadata_dict
                    )
                    if license_result.is_forbidden():
                        self.logger.warning(
                            "Skipping %s due to incompatible license: %s",
                            crate_name,
                            license_result.message,
                        )
                        # Store license decision in audit trail
                        execution_id = f"license-skip-{crate_name}-{int(time.time())}"
                        
                        error_trace = SacredChainTrace(
                            input_data=crate_name,
                            context_sources=["crates.io"],
                            reasoning_steps=[
                                f"License check failed: {license_result.message}",
                                f"Detected licenses: {', '.join(license_result.detected_licenses)}",
                                "Crate excluded from processing due to license policy",
                            ],
                            suggestion=f"SKIP: License incompatibility - {license_result.message}",
                            verdict=TrustVerdict.DEFER,  # Use DEFER for skipped crates
                            audit_info={
                                "license_check": {
                                    "detected_licenses": license_result.detected_licenses,
                                    "status": license_result.status,
                                    "message": license_result.message,
                                    "confidence": license_result.confidence,
                                    "justification": (
                                        f"Crate uses license(s) incompatible with distribution policy. "
                                        f"Detected: {', '.join(license_result.detected_licenses)}. "
                                        f"Policy excludes GPL, AGPL, and other copyleft licenses."
                                    ),
                                },
                                "skipped_reason": "license_incompatibility",
                            },
                            irl_score=0.0,
                            execution_id=execution_id,
                            timestamp=datetime.now(timezone.utc).isoformat(),
                            canon_version=self.canon_registry.version,
                        )
                        return error_trace

                documentation_results = await self._gather_documentation(
                    crate_name, scraper, crate_metadata_dict
                )

                # Get ML predictions BEFORE sacred chain analysis so they can be used in trust decisions
                ml_predictions = None
                if self.ml_predictor:
                    # Create a preliminary trace for ML prediction (we'll update it after)
                    preliminary_trace_data = {
                        "name": crate_name,
                        "description": crate_metadata_dict.get("description", ""),
                        "context_sources": ["crates.io"],
                        "reasoning_steps": [],
                        "irl_score": 0.0,
                        "audit_info": {
                            "metadata": crate_metadata_dict,
                            "docs": {},
                            "sentiment": {},
                            "ecosystem": {},
                        },
                    }
                    # Get preliminary ML predictions
                    try:
                        prediction = self.ml_predictor.predict_quality(preliminary_trace_data)
                        ml_predictions = {
                            "quality_score": prediction.quality_score,
                            "security_risk": prediction.security_risk,
                            "maintenance_score": prediction.maintenance_score,
                            "popularity_trend": prediction.popularity_trend,
                            "dependency_health": prediction.dependency_health,
                            "confidence": prediction.confidence,
                            "model_version": prediction.model_version,
                        }
                    except Exception as e:
                        self.logger.debug("Preliminary ML prediction failed: %s", e)
                
                # Perform sacred chain analysis with ML predictions in context
                sacred_chain_trace = await self._perform_sacred_chain_analysis(
                    crate_name, crate_version, documentation_results, crate_metadata_dict, ml_predictions=ml_predictions
                )
                
                # Always record license information in audit trail (even if allowed)
                if license_result:
                    sacred_chain_trace.audit_info["license_check"] = {
                        "detected_licenses": license_result.detected_licenses,
                        "status": license_result.status,
                        "message": license_result.message,
                        "confidence": license_result.confidence,
                        "justification": (
                            f"License check passed. Detected licenses: {', '.join(license_result.detected_licenses)}. "
                            f"Licenses are compatible with distribution policy."
                            if license_result.status == "allowed"
                            else f"License status: {license_result.status}. {license_result.message}"
                        ),
                    }

                # Store ML predictions in audit info (may have been updated during analysis)
                if ml_predictions:
                    sacred_chain_trace.audit_info["ml_predictions"] = ml_predictions
                
                # Record metrics
                if self.metrics_collector:
                    import time
                    processing_time = time.time() - (getattr(self, '_crate_start_time', time.time()))
                    verdict_str = str(sacred_chain_trace.verdict.value) if hasattr(sacred_chain_trace.verdict, 'value') else str(sacred_chain_trace.verdict)
                    quality_score = sacred_chain_trace.audit_info.get("quality_score", 5.0)
                    self.metrics_collector.record_crate_processed(
                        verdict=verdict_str,
                        quality_score=quality_score,
                        processing_time=processing_time
                    )
                    
                    if ml_predictions:
                        self.metrics_collector.record_ml_prediction()

                # Cache the result
                if self.cache:
                    result = self.cache.set(
                        cache_key,
                        sacred_chain_trace,
                        ttl=3600,
                        tags=["crate_analysis", crate_name],
                    )
                    if asyncio.iscoroutine(result):
                        await result

                await self._generate_analysis_report(crate_name, sacred_chain_trace)

                self.logger.info("Analysis completed for %s", crate_name)
                return sacred_chain_trace

        except (RuntimeError, ValueError, KeyError) as e:
            self.logger.error("Analysis failed for %s: %s", crate_name, e)
            # Return structured error trace instead of crashing
            error_trace = SacredChainTrace(
                input_data=crate_name,
                context_sources=[],
                reasoning_steps=[f"Analysis failed: {str(e)}"],
                suggestion="DEFER: Analysis error",
                verdict=TrustVerdict.DEFER,
                audit_info={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "failed_stage": "analysis",
                },
                irl_score=0.0,
                execution_id=f"error-{crate_name}-{int(time.time())}",
                timestamp=datetime.now(timezone.utc).isoformat(),
                canon_version=self.canon_registry.version,
            )
            return error_trace

    async def _add_ml_predictions(
        self, crate_name: str, sacred_chain_trace: SacredChainTrace
    ) -> Dict[str, Any]:
        """Add ML predictions to the analysis."""
        if not self.ml_predictor:
            return {}

        try:
            # Extract crate data from sacred chain trace
            crate_data = {
                "name": crate_name,
                "description": sacred_chain_trace.suggestion,
                "context_sources": sacred_chain_trace.context_sources,
                "reasoning_steps": sacred_chain_trace.reasoning_steps,
                "irl_score": sacred_chain_trace.irl_score,
                "audit_info": sacred_chain_trace.audit_info,
            }

            # Get ML predictions
            prediction = self.ml_predictor.predict_quality(crate_data)

            return {
                "quality_score": prediction.quality_score,
                "security_risk": prediction.security_risk,
                "maintenance_score": prediction.maintenance_score,
                "popularity_trend": prediction.popularity_trend,
                "dependency_health": prediction.dependency_health,
                "confidence": prediction.confidence,
                "model_version": prediction.model_version,
            }

        except (AttributeError, ValueError, KeyError) as e:
            self.logger.warning("ML prediction failed for %s: %s", crate_name, e)
            return {}

    def _check_license_compliance(
        self, crate_name: str, crate_metadata_dict: Dict[str, Any]
    ) -> Any:  # LicenseCheckResult
        """
        Check if a crate's license is compliant with policy.
        
        Args:
            crate_name: Name of the crate
            crate_metadata_dict: Metadata dictionary from API
            
        Returns:
            LicenseCheckResult indicating if license is allowed/forbidden
        """
        if not self.license_filter:
            # If license filter not available, allow all (fail open)
            from .utils.license_filter import LicenseCheckResult
            return LicenseCheckResult(
                detected_licenses=[],
                status="unknown",
                message="License filter not available - allowing crate",
                confidence=0.0,
            )
        
        # Extract license from metadata
        license_expr = crate_metadata_dict.get("license")
        
        # Get documentation text for license extraction
        documentation_text = ""
        readme = crate_metadata_dict.get("readme", "")
        if readme:
            documentation_text = readme
        
        # Check license compliance
        result = self.license_filter.check_license(
            license_expr=license_expr,
            crate_api_data={"crate": crate_metadata_dict},
            documentation_text=documentation_text,
        )
        
        # Log license decision
        if result.is_forbidden():
            self.logger.warning(
                "License check for %s: FORBIDDEN - %s (licenses: %s)",
                crate_name,
                result.message,
                ", ".join(result.detected_licenses) if result.detected_licenses else "none detected",
            )
        elif result.is_allowed():
            self.logger.debug(
                "License check for %s: ALLOWED - %s",
                crate_name,
                ", ".join(result.detected_licenses) if result.detected_licenses else "no license detected",
            )
        else:
            self.logger.info(
                "License check for %s: %s - %s",
                crate_name,
                result.status.upper(),
                result.message,
            )
        
        return result

    async def _fetch_crate_metadata(self, crate_name: str) -> Optional[Dict[str, Any]]:
        """Fetch crate metadata from crates.io API using CrateAPIClient for full data"""
        try:
            # Use CrateAPIClient for comprehensive metadata fetching
            from .network import CrateAPIClient
            
            api_client = CrateAPIClient(self.config)
            metadata = await api_client.fetch_crate_metadata_async(crate_name)
            
            if metadata:
                self.logger.info(f"Fetched full metadata for {crate_name}: downloads={metadata.get('downloads', 0)}, deps={len(metadata.get('dependencies', []))}, features={len(metadata.get('features', {}))}, github_stars={metadata.get('github_stars', 0)}")
                return metadata
            else:
                self.logger.warning(f"Failed to fetch metadata for {crate_name} using CrateAPIClient")
                return None
        except Exception as e:
            self.logger.error(f"Error fetching crate metadata for {crate_name}: {e}")
            return None

    def _summarize_code_snippets(
        self, sanitized_docs: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract heuristic metadata for documentation code snippets."""

        summaries: List[Dict[str, Any]] = []
        for source, payload in sanitized_docs.items():
            if not isinstance(payload, dict):
                continue
            content = payload.get("content")
            if not content:
                continue

            matches = re.findall(
                r"```(?:rust|rs)\s*\n(.*?)\n```", content, re.DOTALL | re.IGNORECASE
            )
            for snippet in matches[:5]:
                snippet = snippet.strip()
                if not snippet:
                    continue

                summaries.append(
                    {
                        "source": source,
                        "quality": self._snippet_quality(snippet),
                        "complexity_score": round(complexity_score(snippet), 4),
                        "topics": detect_topics(snippet),
                        "heuristics_mode": "legacy"
                        if self.use_legacy_heuristics
                        else "default",
                        "preview": snippet[:160].strip(),
                    }
                )

            if len(summaries) >= 25:
                break

        return summaries

    async def _gather_documentation(
        self,
        crate_name: str,
        scraper: UnifiedScraper,
        crate_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, ScrapingResult]:
        if not scraper:
            raise RuntimeError("Scraper not initialized")

        self.logger.info("Gathering documentation for %s", crate_name)

        try:
            # Get repository URL from crate metadata if available
            repository_url = None
            if crate_metadata:
                repository_url = crate_metadata.get("repository")
                if repository_url:
                    self.logger.info(
                        "Found repository URL for %s: %s", crate_name, repository_url
                    )
                else:
                    self.logger.info("No repository URL found for %s", crate_name)

            # Call scraper with repository URL for GitHub integration
            results = await scraper.scrape_crate_documentation(
                crate_name, repository_url
            )

            successful_sources = [
                source
                for source, result in results.items()
                if result is not None and result.error is None
            ]
            failed_sources = [
                source
                for source, result in results.items()
                if result is None or result.error is not None
            ]

            self.logger.info(
                "Successfully scraped %d sources: %s",
                len(successful_sources),
                successful_sources,
            )
            if failed_sources:
                self.logger.warning(
                    "Failed to scrape %d sources: %s",
                    len(failed_sources),
                    failed_sources,
                )

            return results

        except (RuntimeError, ValueError, KeyError) as e:
            self.logger.error("Documentation gathering failed: %s", e)
            raise

    async def _perform_sacred_chain_analysis(
        self,
        crate_name: str,
        crate_version: str,
        documentation_results: Dict[str, ScrapingResult],
        fetched_metadata: Optional[Dict[str, Any]] = None,
        ml_predictions: Optional[Dict[str, Any]] = None,
    ) -> SacredChainTrace:
        """Perform Sacred Chain analysis - delegates to pipeline_analysis module."""
        async def add_llm_enrichment(name: str, version: str, trace: SacredChainTrace) -> None:
            """Helper to add LLM enrichment."""
            if self.unified_llm_processor:
                await add_unified_llm_enrichment(
                    self.unified_llm_processor,
                    self.sanitizer,
                    name,
                    version,
                    trace,
                    self.logger,
                )
            elif self.ai_enricher:
                await add_azure_openai_enrichment(
                    self.ai_enricher,
                    self.sanitizer,
                    name,
                    trace,
                    self.logger,
                )

        return await perform_sacred_chain_analysis(
            self.irl_engine,
            self.sanitizer,
            crate_name,
            crate_version,
            documentation_results,
            fetched_metadata,
            self._summarize_code_snippets,
            self._add_crate_analysis_results,
            add_llm_enrichment,
            self.logger,
            ml_predictions=ml_predictions,
        )

    async def _handle_toolchain_override(
        self, crate_source_path: Path
    ) -> Optional[Path]:
        """
        Handle rust-toolchain files that might override to incompatible versions.
        Returns the path of the backed up file if one was found, None otherwise.
        """
        toolchain_files = [
            crate_source_path / "rust-toolchain.toml",
            crate_source_path / "rust-toolchain",
        ]

        for toolchain_file in toolchain_files:
            if toolchain_file.exists():
                self.logger.info("Found toolchain override file: %s", toolchain_file)
                # Backup the file by renaming it
                backup_path = toolchain_file.with_suffix(
                    toolchain_file.suffix + ".backup"
                )
                try:
                    toolchain_file.rename(backup_path)
                    self.logger.info(
                        "Temporarily disabled toolchain override: %s -> %s",
                        toolchain_file,
                        backup_path,
                    )
                    return backup_path
                except Exception as e:
                    self.logger.warning(
                        "Failed to backup toolchain file %s: %s", toolchain_file, e
                    )

        return None

    async def _restore_toolchain_override(self, backup_path: Optional[Path]) -> None:
        """Restore a backed up rust-toolchain file."""
        if backup_path and backup_path.exists():
            try:
                original_path = backup_path.with_suffix(
                    backup_path.suffix.replace(".backup", "")
                )
                backup_path.rename(original_path)
                self.logger.info(
                    "Restored toolchain override: %s -> %s", backup_path, original_path
                )
            except Exception as e:
                    self.logger.warning(
                        "Failed to restore toolchain file %s: %s", backup_path, e
                    )

    async def _add_crate_analysis_results(
        self, crate_name: str, crate_version: str, trace: SacredChainTrace
    ) -> None:
        """Add crate analysis results to the sacred chain trace"""
        temp_dir = None
        try:
            if trace.audit_info.get("should_analyze_source_code", True):
                self.logger.info(
                    "Adding crate analysis results for %s v%s", crate_name, crate_version
                )

                # Create temporary directory and ensure cleanup
                temp_dir = Path(tempfile.mkdtemp(prefix=f"crate_analysis_{crate_name}_"))
                crate_source_path = await self._download_and_extract_crate(
                    crate_name, crate_version, temp_dir
                )

                if not crate_source_path:
                    trace.audit_info["crate_analysis"] = {
                        "status": "error",
                        "note": "Failed to download or extract crate.",
                    }
                    return

                # Handle toolchain overrides that might cause compatibility issues
                backup_path = await self._handle_toolchain_override(crate_source_path)

                try:
                    # Use enhanced crate analysis with additional tools and insights
                    from .crate_analysis import CrateAnalyzer

                    analyzer = CrateAnalyzer(str(crate_source_path))
                    analysis_results = await analyzer.analyze_async()

                    # Also run individual commands for backward compatibility
                    check_results, check_error = await self._run_command(
                        ["cargo", "+stable", "check", "--message-format=json"],
                        cwd=crate_source_path,
                    )
                    clippy_results, clippy_error = await self._run_command(
                        ["cargo", "+stable", "clippy", "--message-format=json"],
                        cwd=crate_source_path,
                    )
                    audit_results, audit_error = await self._run_command(
                        ["cargo", "+stable", "audit", "--json"], cwd=crate_source_path
                    )

                    trace.audit_info["crate_analysis"] = self.sanitizer.sanitize_data(
                        {
                            "status": "completed",
                            "enhanced_analysis": analysis_results,
                            "check": check_results,
                            "check_error": check_error,
                            "clippy": clippy_results,
                            "clippy_error": clippy_error,
                            "audit": audit_results,
                            "audit_error": audit_error,
                            "note": "Enhanced crate analysis performed with additional tools and insights.",
                        }
                    )

                finally:
                    # Restore any backed up toolchain file
                    await self._restore_toolchain_override(backup_path)

        except Exception as e:
            self.logger.warning("Failed to add crate analysis results: %s", e)
            trace.audit_info["crate_analysis"] = {"status": "error", "note": str(e)}
        
        finally:
            # Clean up temporary directory to prevent disk space leaks
            if temp_dir and temp_dir.exists():
                try:
                    import shutil
                    shutil.rmtree(temp_dir)
                    self.logger.debug(f"Cleaned up temporary directory: {temp_dir}")
                except Exception as cleanup_error:
                    self.logger.warning(
                        f"Failed to clean up temporary directory {temp_dir}: {cleanup_error}"
                    )

    async def _download_and_extract_crate(
        self,
        crate_name: str,
        crate_version: str,
        target_dir: Path,
        crate_registry_base: Optional[str] = None,
    ) -> Optional[Path]:
        """Downloads and extracts a crate from crates.io."""
        # Defense-in-depth: validate version again before using in paths/URLs
        try:
            crate_version = validate_crate_version(crate_version)
        except PipelineValidationError as e:
            self.logger.error("Invalid crate version '%s': %s", crate_version, e)
            raise ValueError(f"Invalid crate version: {e}") from e

        crate_base = (crate_registry_base or "https://static.crates.io/crates").rstrip(
            "/"
        )
        crate_url = (
            f"{crate_base}/{crate_name}/{crate_name}-{crate_version}.crate"
        )
        try:
            import ssl  # Local import to avoid unnecessary dependency at module load
            import certifi
            import aiohttp

            ssl_context = ssl.create_default_context(cafile=certifi.where())
            connector = aiohttp.TCPConnector(
                ssl=ssl_context, enable_cleanup_closed=True
            )
            timeout = aiohttp.ClientTimeout(total=120, connect=20, sock_read=100)

            async with aiohttp.ClientSession(
                connector=connector, timeout=timeout
            ) as session:
                async with session.get(crate_url) as response:
                    if response.status != 200:
                        self.logger.error(
                            f"Failed to download {crate_url}: HTTP {response.status}"
                        )
                        return None

                    # Save the .crate file
                    crate_file_path = target_dir / f"{crate_name}-{crate_version}.crate"
                    await self._stream_response_to_file(response, crate_file_path)

                    if self.sync_mode:
                        crate_source_dir = self._extract_crate_tarball(
                            crate_file_path,
                            target_dir,
                            crate_name,
                            crate_version,
                        )
                    else:
                        crate_source_dir = await asyncio.to_thread(
                            self._extract_crate_tarball,
                            crate_file_path,
                            target_dir,
                            crate_name,
                            crate_version,
                        )

                    return crate_source_dir

        except Exception as e:
            self.logger.warning(
                f"Could not download crate source for {crate_name}: {e}"
            )
            self.logger.info(
                "This is optional - web scraping analysis will continue without source code"
            )
            return None

    async def _get_latest_crate_version(self, crate_name: str) -> Optional[str]:
        """Fetches the latest version of a crate from crates.io API."""
        api_url = f"https://crates.io/api/v1/crates/{crate_name}"
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            connector = self._create_tls_connector()

            async with aiohttp.ClientSession(
                connector=connector, timeout=timeout
            ) as session:
                async with session.get(api_url) as response:
                    if response.status != 200:
                        self.logger.error(
                            f"Failed to fetch crate info from {api_url}: HTTP {response.status}"
                        )
                        return None

                    data = await response.json()
                    return data.get("crate", {}).get("max_version")
        except Exception as e:
            self.logger.error(
                f"Error fetching latest crate version for {crate_name}: {e}"
            )
            return None

    async def _stream_response_to_file(
        self,
        response: aiohttp.ClientResponse,
        file_path: Path,
        chunk_size: int = 65536,
    ) -> None:
        """Stream a HTTP response body to disk without blocking the event loop."""
        async with aiofiles.open(file_path, "wb") as file:
            async for chunk in response.content.iter_chunked(chunk_size):
                if chunk:
                    await file.write(chunk)

    def _extract_crate_tarball(
        self,
        crate_file_path: Path,
        target_dir: Path,
        crate_name: str,
        crate_version: str,
    ) -> Optional[Path]:
        """Extract a crate tarball ensuring no path traversal occurs."""
        base_dir = Path(target_dir).resolve()
        validated_members = []
        
        with gzip.open(crate_file_path, "rb") as gz_file:
            with tarfile.open(fileobj=gz_file, mode="r:*") as tar_file:
                for member in tar_file.getmembers():
                    # Resolve the target path to catch path traversal attempts
                    target_path = (base_dir / member.name).resolve()
                    
                    # Use commonpath to ensure target is actually within base directory
                    # This prevents false positives from startswith() string comparison
                    try:
                        common = os.path.commonpath([base_dir, target_path])
                        if common != str(base_dir):
                            raise SecurityException(
                                f"Attempted path traversal in tar file: {member.name}"
                            )
                    except ValueError:
                        # commonpath raises ValueError if paths are on different drives (Windows)
                        # In this case, reject as it's definitely outside
                        raise SecurityException(
                            f"Attempted path traversal in tar file: {member.name}"
                        )
                    
                    # Reject symlinks that point outside the base directory
                    if member.issym() or member.islnk():
                        # Resolve symlink target relative to the symlink's location
                        symlink_path = base_dir / member.name
                        symlink_target = symlink_path.parent / member.linkname
                        resolved_target = symlink_target.resolve()
                        
                        # Ensure resolved symlink target is within base directory
                        try:
                            common = os.path.commonpath([base_dir, resolved_target])
                            if common != str(base_dir):
                                raise SecurityException(
                                    f"Symlink in tar file points outside base directory: {member.name} -> {member.linkname}"
                                )
                        except ValueError:
                            # Different drive on Windows - reject
                            raise SecurityException(
                                f"Symlink in tar file points outside base directory: {member.name} -> {member.linkname}"
                            )
                    
                    # Only add validated members to the list
                    validated_members.append(member)
                
                # Extract only validated members to prevent any security issues
                tar_file.extractall(path=target_dir, members=validated_members)

        crate_source_dir = target_dir / f"{crate_name}-{crate_version}"
        if crate_source_dir.is_dir():
            return crate_source_dir

        self.logger.error(
            f"Could not find extracted directory: {crate_source_dir}"
        )
        return None

    def _create_tls_connector(self) -> aiohttp.TCPConnector:
        """
        Create a TLS connector that enforces certificate verification.
        
        Always uses certifi's certificate bundle for consistent verification
        across all platforms. Falls back to default context only if certifi
        is unavailable (should not happen in production).
        """
        import ssl
        import certifi

        try:
            # Always use certifi for certificate verification
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            # Enforce strong TLS settings
            if hasattr(ssl, 'TLSVersion'):
                ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
            ssl_context.check_hostname = True
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            
            return aiohttp.TCPConnector(
                ssl=ssl_context, 
                enable_cleanup_closed=True,
                limit=100,  # Connection pool limit
                limit_per_host=10,  # Per-host limit
            )
        except Exception as ssl_error:
            self.logger.warning(
                "Falling back to default TLS context due to setup issue: %s",
                ssl_error,
            )
            # Even in fallback, create a basic secure context
            try:
                ssl_context = ssl.create_default_context()
                if hasattr(ssl, 'TLSVersion'):
                    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
                return aiohttp.TCPConnector(
                    ssl=ssl_context,
                    enable_cleanup_closed=True,
                )
            except Exception:
                # Last resort: default connector (still secure, just not using certifi)
                return aiohttp.TCPConnector(enable_cleanup_closed=True)

    async def _run_command(
        self, command: List[str], cwd: Path
    ) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
        """Runs a command and returns the parsed JSON output and any errors."""
        return await run_command_with_cleanup(command, cwd, self.logger)

    async def _add_ai_enrichment(
        self, crate_name: str, crate_version: str, trace: SacredChainTrace
    ) -> None:
        """Add AI enrichment results to the sacred chain trace"""
        # Use unified LLM processor if available, otherwise fall back to Azure OpenAI
        if self.unified_llm_processor:
            await add_unified_llm_enrichment(
                self.unified_llm_processor,
                self.sanitizer,
                crate_name,
                crate_version,
                trace,
                self.logger,
            )
        elif self.ai_enricher:
            await add_azure_openai_enrichment(
                self.ai_enricher,
                self.sanitizer,
                crate_name,
                trace,
                self.logger,
            )
        else:
            self.logger.info("ℹ️  No AI enricher available, skipping AI enrichment")

    # LLM enrichment methods moved to pipeline_enrichment.py
    # Metadata extraction helpers moved to pipeline_enrichment.py

    async def _generate_analysis_report(
        self, crate_name: str, trace: SacredChainTrace
    ) -> None:
        """Generate analysis report and save to file"""
        try:
            self.logger.info("Generating analysis report for %s", crate_name)

            # Use config output directory, fallback to "output" if not set
            output_dir = Path(self.config.output_dir if hasattr(self.config, 'output_dir') and self.config.output_dir else "output")
            output_dir.mkdir(parents=True, exist_ok=True)

            report_path = output_dir / f"{crate_name}_analysis_report.json"

            report_data = to_serializable(trace.to_dict())

            # Manually handle MarkdownGenerationResult
            enrichment_path = report_data.get("audit_info", {}).get("llm_enrichment")
            if enrichment_path is not None and not isinstance(
                enrichment_path, (dict, list, str, int, float, bool, type(None))
            ):
                # Fallback: convert to string to guarantee JSON serialization
                report_data["audit_info"]["llm_enrichment"] = str(enrichment_path)

            def _write_report() -> None:
                with open(report_path, "w", encoding="utf-8") as f:
                    json.dump(report_data, f, indent=4, default=str)

            if self.sync_mode:
                _write_report()
            else:
                await asyncio.to_thread(_write_report)

            self.logger.info("Analysis report generated at %s", report_path)

        except Exception as e:
            # Catch all exceptions and log with full traceback for debugging
            import traceback
            self.logger.error(
                "Failed to generate analysis report for %s: %s\n%s",
                crate_name,
                e,
                traceback.format_exc()
            )
            # Don't re-raise - report generation failure shouldn't fail the entire analysis
            # The audit record is already created, so we log the error and continue

    async def analyze_multiple_crates(
        self, crate_names: List[str]
    ) -> Dict[str, SacredChainTrace]:
        if not crate_names:
            return {}

        self.logger.info("Starting concurrent analysis of %d crates", len(crate_names))

        semaphore = asyncio.Semaphore(self.config.n_workers)

        async def analyze_single_crate(
            crate_name: str,
        ) -> "tuple[str, SacredChainTrace]":
            async with semaphore:
                try:
                    trace = await self.analyze_crate(crate_name)
                    return crate_name, trace
                except (RuntimeError, ValueError, KeyError) as e:
                    self.logger.error("Analysis failed for %s: %s", crate_name, e)
                    error_trace = SacredChainTrace(
                        input_data=crate_name,
                        context_sources=[],
                        reasoning_steps=[f"Analysis failed: {str(e)}"],
                        suggestion="DEFER: Analysis failed",
                        verdict=TrustVerdict.DEFER,
                        audit_info={"error": str(e)},
                        irl_score=0.0,
                        execution_id=f"error-{int(time.time())}",
                        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        canon_version=__version__,
                    )
                    return crate_name, error_trace

        tasks = [analyze_single_crate(name) for name in crate_names]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        analysis_results: Dict[str, SacredChainTrace] = {}
        for result in results:
            if isinstance(result, tuple):
                crate_name, trace = result
                analysis_results[crate_name] = trace
            else:
                self.logger.error("Unexpected result type: %s", type(result))

        self.logger.info("Completed analysis of %d crates", len(analysis_results))
        
        # Generate provenance manifest
        try:
            output_dir = Path(self.config.output_dir)
            crate_list = list(analysis_results.keys())
            manifest_file = output_dir / "dataset_manifest.json"
            
            # Generate and save manifest
            attach_manifest_to_output(
                output_path=manifest_file,
                output_type="pipeline_analysis",
                input_data=crate_list,
                output_data=analysis_results,
                generator_info={
                    "pipeline_version": __version__,
                    "crates_analyzed": len(crate_list),
                },
            )
            self.logger.info("Generated provenance manifest: %s", manifest_file)
        except Exception as e:
            self.logger.warning("Failed to generate provenance manifest: %s", e)
        
        return analysis_results

    def get_pipeline_summary(self) -> Dict[str, Any]:
        """Get a summary of the pipeline configuration and status"""
        summary = {
            "pipeline_version": __version__,
            "components": {
                "irl_engine": self.irl_engine is not None,
                "scraper": "per_task",  # Scrapers are created per task now
                "canon_registry": self.canon_registry is not None,
            },
            "ai_components": {
                "unified_llm_processor": self.unified_llm_processor is not None,
                "azure_openai_enricher": self.ai_enricher is not None,
                "crate_analyzer": self.crate_analyzer is not None,
            },
            "configuration": {
                "max_tokens": self.config.max_tokens,
                "checkpoint_interval": self.config.checkpoint_interval,
                "batch_size": self.config.batch_size,
                "enable_crawl4ai": self.config.enable_crawl4ai,
            },
        }

        # Add LLM configuration if available
        if self.llm_config:
            summary["llm_configuration"] = {
                "provider": self.llm_config.provider,
                "model": self.llm_config.model,
                "temperature": self.llm_config.temperature,
                "max_tokens": self.llm_config.max_tokens,
                "timeout": self.llm_config.timeout,
                "max_retries": self.llm_config.max_retries,
            }
        elif self.config.use_azure_openai:
            summary["llm_configuration"] = {
                "provider": "azure_openai",
                "model": self.config.azure_openai_deployment_name,
                "endpoint": self.config.azure_openai_endpoint,
                "max_tokens": self.config.max_tokens,
            }

        return summary


class UnifiedPipeline:
    """
    Unified orchestration layer that combines the standard data pipeline with
    Sacred Chain / ELINT analysis into a single execution flow.
    """

    def __init__(self, config: PipelineConfig, pipeline_kwargs: Dict[str, Any]) -> None:
        self.config = config
        self.pipeline_kwargs = pipeline_kwargs
        self.logger = logging.getLogger(__name__)

        # Standard pipeline handles ingestion, scraping, source analysis, and enrichment
        self.standard_pipeline = CrateDataPipeline(config, **pipeline_kwargs)

        # Ensure downstream components share the same run-specific output directory
        self.config.output_dir = getattr(self.standard_pipeline, "output_dir", self.config.output_dir)

        self.elint_enabled = getattr(config, "enable_elint", True)
        self.elint_pipeline: Optional[UnifiedSigilPipeline] = None
        if self.elint_enabled:
            try:
                self.elint_pipeline = UnifiedSigilPipeline(config)
            except Exception as exc:  # pragma: no cover - defensive
                self.logger.error("Failed to initialize ELINT pipeline: %s", exc)
                self.elint_pipeline = None

    async def run(self) -> Optional[Tuple[Any, Any]]:
        """Run the full pipeline (standard + ELINT when enabled)."""
        standard_result = await self.standard_pipeline.run()

        if (
            self.elint_pipeline
            and getattr(self.standard_pipeline, "crates", None)
            and self.standard_pipeline.crates
        ):
            crate_names = [crate.name for crate in self.standard_pipeline.crates]
            try:
                async with self.elint_pipeline:
                    await self.elint_pipeline.analyze_multiple_crates(crate_names)
            except Exception as exc:
                self.logger.warning(
                    "Sacred Chain analysis failed (continuing without ELINT): %s", exc
                )
        elif self.elint_enabled and not self.elint_pipeline:
            self.logger.warning("ELINT stage requested but unavailable; continuing.")

        return standard_result

def create_pipeline_from_args(args: argparse.Namespace) -> UnifiedSigilPipeline:
    """Create pipeline from command line arguments"""
    # Create base config
    config = PipelineConfig()
    if hasattr(args, "sync_mode"):
        config.sync_mode = bool(args.sync_mode)

    # Create LLM config if LLM arguments are provided
    llm_config = None
    if hasattr(args, "llm_provider") and args.llm_provider:
        if UNIFIED_LLM_AVAILABLE and LLMConfig is not None:
            llm_config_params = {
                "provider": args.llm_provider,
                "model": args.llm_model or "gpt-4o",
                "api_base": getattr(args, "llm_api_base", None),
                "api_key": getattr(args, "llm_api_key", None),
                "temperature": float(getattr(args, "llm_temperature", 0.2)),
                "max_tokens": int(getattr(args, "llm_max_tokens", 256)),
                "timeout": float(getattr(args, "llm_timeout", 30)),
                "max_retries": int(getattr(args, "llm_max_retries", 3)),
                "azure_deployment": getattr(args, "azure_deployment", None),
                "azure_api_version": getattr(args, "azure_api_version", None),
                "ollama_host": getattr(args, "ollama_host", None),
                "lmstudio_host": getattr(args, "lmstudio_host", None),
            }
            # Filter out None values so that default values in LLMConfig are
            # used
            llm_config_params = {
                k: v for k, v in llm_config_params.items() if v is not None
            }
            llm_config = LLMConfig(**llm_config_params)
        else:
            logging.warning(
                "Unified LLM processor not available, falling back to Azure OpenAI"
            )

    return UnifiedSigilPipeline(config, llm_config)


def add_llm_arguments(parser: argparse.ArgumentParser) -> None:
    """Add LLM-related command line arguments to the parser"""
    llm_group = parser.add_argument_group("LLM Configuration")

    llm_group.add_argument(
        "--llm-provider",
        choices=[
            "azure",
            "ollama",
            "lmstudio",
            "openai",
            "anthropic",
            "google",
            "cohere",
            "huggingface",
            "lambda",  # Add Lambda.AI support
        ],
        help="LLM provider to use (default: azure)",
    )

    llm_group.add_argument(
        "--llm-model",
        default="gpt-4o",
        help="Model name/identifier (e.g., gpt-4, llama2, claude-3, "
        "qwen25-coder-32b-instruct)",
    )

    llm_group.add_argument(
        "--llm-api-base", help="API base URL (for local providers or custom endpoints)"
    )

    llm_group.add_argument("--llm-api-key", help="API key (if required by provider)")

    llm_group.add_argument(
        "--llm-temperature",
        type=float,
        default=0.2,
        help="Temperature for LLM generation (default: 0.2)",
    )

    llm_group.add_argument(
        "--llm-max-tokens",
        type=int,
        default=256,
        help="Maximum tokens for LLM generation (default: 256)",
    )

    llm_group.add_argument(
        "--llm-timeout",
        type=int,
        default=30,
        help="Timeout for LLM API calls in seconds (default: 30)",
    )

    llm_group.add_argument(
        "--llm-max-retries",
        type=int,
        default=3,
        help="Maximum retries for LLM API calls (default: 3)",
    )

    # Provider-specific arguments
    azure_group = parser.add_argument_group("Azure OpenAI Configuration")
    azure_group.add_argument("--azure-deployment", help="Azure OpenAI deployment name")
    azure_group.add_argument("--azure-api-version", help="Azure OpenAI API version")

    ollama_group = parser.add_argument_group("Ollama Configuration")
    ollama_group.add_argument(
        "--ollama-host",
        default="http://localhost:11434",
        help="Ollama host URL (default: http://localhost:11434)",
    )

    lmstudio_group = parser.add_argument_group("LM Studio Configuration")
    lmstudio_group.add_argument(
        "--lmstudio-host",
        default="http://localhost:1234/v1",
        help="LM Studio host URL (default: http://localhost:1234/v1)",
    )

    # Add Lambda.AI configuration group
    lambda_group = parser.add_argument_group("Lambda.AI Configuration")
    lambda_group.add_argument(
        "--lambda-api-base",
        default="https://api.lambda.ai/v1",
        help="Lambda.AI API base URL (default: https://api.lambda.ai/v1)",
    )


async def quick_analyze_crate(
    crate_name: str,
    config: Optional[PipelineConfig] = None,
    llm_config: Optional[Any] = None,
) -> SacredChainTrace:
    """Quick analysis of a single crate"""
    # Validate crate name at entry point before creating pipeline
    try:
        crate_name = validate_crate_name(crate_name)
    except PipelineValidationError as e:
        raise ValueError(f"Invalid crate name: {e}") from e

    if config is None:
        config = PipelineConfig()

    async with UnifiedSigilPipeline(config, llm_config) as pipeline:
        return await pipeline.analyze_crate(crate_name)


async def batch_analyze_crates(
    crate_names: List[str],
    config: Optional[PipelineConfig] = None,
    llm_config: Optional[Any] = None,
) -> Dict[str, SacredChainTrace]:
    """Batch analysis of multiple crates"""
    # Validate all crate names at entry point before creating pipeline
    validated_names = []
    for crate_name in crate_names:
        try:
            validated_names.append(validate_crate_name(crate_name))
        except PipelineValidationError as e:
            raise ValueError(f"Invalid crate name '{crate_name}': {e}") from e

    if config is None:
        config = PipelineConfig()

    async with UnifiedSigilPipeline(config, llm_config) as pipeline:
        return await pipeline.analyze_multiple_crates(validated_names)
