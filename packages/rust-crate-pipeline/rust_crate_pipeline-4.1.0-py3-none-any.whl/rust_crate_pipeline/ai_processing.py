# ai_processing.py
import asyncio
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    tiktoken = None
    TIKTOKEN_AVAILABLE = False

from .config import CrateMetadata, EnrichedCrate, PipelineConfig
from .config_loader import get_config_loader
from .llm_factory import create_llm_client_from_config
from .utils.canonical_store import CanonicalDataManager, SnapshotMetadata
from .validation import EnrichedValidator, ValidationFailure

if TYPE_CHECKING:
    from .validation.enriched_validator import ValidationResult


class LLMEnricher:
    def __init__(self, config: PipelineConfig, llm_client=None) -> None:
        """Initialize LLMEnricher with new LLM client
        
        Args:
            config: Pipeline configuration
            llm_client: Optional LLM client to use. If not provided, creates one from config.
        """
        self.config = config
        if not TIKTOKEN_AVAILABLE:
            raise ImportError("tiktoken is required for LLMEnricher. Install with: pip install tiktoken or pip install -e '.[ai]'")
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.config_loader = get_config_loader()

        # Use provided LLM client or create one from config
        if llm_client is not None:
            self.llm_client = llm_client
        else:
            self.llm_client = create_llm_client_from_config(config)
        self.logger = logging.getLogger(__name__)

    async def enrich_crate(
        self,
        crate: CrateMetadata,
        *,
        snapshot: Optional[Dict[str, Any]] = None,
        canonical_manager: Optional[CanonicalDataManager] = None,
        validator: Optional[EnrichedValidator] = None,
        snapshot_metadata: Optional[SnapshotMetadata] = None,
    ) -> EnrichedCrate:
        """Enrich crate metadata using LLM analysis"""
        try:
            # Create enriched crate with original data
            enriched = EnrichedCrate(
                name=crate.name,
                version=crate.version,
                description=crate.description,
                repository=crate.repository,
                keywords=crate.keywords,
                categories=crate.categories,
                readme=crate.readme,
                downloads=crate.downloads,
                github_stars=crate.github_stars,
                dependencies=crate.dependencies,
                features=crate.features,
                code_snippets=crate.code_snippets,
                readme_sections=crate.readme_sections,
                librs_downloads=crate.librs_downloads,
                license=crate.license,
                source=crate.source,
                enhanced_scraping=crate.enhanced_scraping,
                enhanced_features=crate.enhanced_features,
                enhanced_dependencies=crate.enhanced_dependencies,
            )

            if canonical_manager is None or validator is None:
                self.logger.warning(
                    "Canonical validation disabled for %s; using legacy enrichment",
                    crate.name,
                )
                await self._legacy_enrichment(enriched)
                return enriched

            snapshot_payload = snapshot or crate.to_dict()
            validation = await self._perform_ai_enrichment(
                enriched,
                snapshot_payload,
                canonical_manager,
                validator,
                snapshot_metadata,
            )
            if validation:
                self.logger.debug(
                    "AI enrichment result for %s: issues=%s speculative=%s",
                    crate.name,
                    validation.issues,
                    validation.speculative_fields,
                )
            return enriched

        except Exception as e:
            self.logger.error(f"Error enriching crate {crate.name}: {e}")
            # Return basic enriched crate without AI data
            return EnrichedCrate(
                name=crate.name,
                version=crate.version,
                description=crate.description,
                repository=crate.repository,
                keywords=crate.keywords,
                categories=crate.categories,
                readme=crate.readme,
                downloads=crate.downloads,
                github_stars=crate.github_stars,
                dependencies=crate.dependencies,
                features=crate.features,
                code_snippets=crate.code_snippets,
                readme_sections=crate.readme_sections,
                librs_downloads=crate.librs_downloads,
                license=crate.license,
                source=crate.source,
                enhanced_scraping=crate.enhanced_scraping,
                enhanced_features=crate.enhanced_features,
                enhanced_dependencies=crate.enhanced_dependencies,
                readme_summary="Error during enrichment",
                feature_summary="Error during enrichment",
                use_case="unknown",
                score=0.0,
                factual_counterfactual="Error during enrichment",
                source_analysis={"error": str(e)},
                user_behavior={"error": str(e)},
                security={"error": str(e)},
            )

    async def _perform_ai_enrichment(
        self,
        enriched: EnrichedCrate,
        snapshot: Dict[str, Any],
        canonical_manager: Optional[CanonicalDataManager],
        validator: Optional[EnrichedValidator],
        snapshot_metadata: Optional[SnapshotMetadata],
    ) -> Optional["ValidationResult"]:
        """Perform AI-based enrichment of crate data using structured prompts."""
        if not canonical_manager or not validator:
            raise ValidationFailure(
                "Canonical data manager and validator are required for enrichment"
            )

        validation, request_meta, response_path = await self._invoke_structured_transformer(
            enriched,
            snapshot,
            canonical_manager,
            validator,
            snapshot_metadata,
        )

        data = validation.enriched
        analysis_block = data.get("analysis", {})

        enriched.readme_summary = data.get("readme_summary")
        enriched.feature_summary = data.get("feature_summary")
        enriched.score = data.get("quality_score")
        enriched.use_case = data.get("use_case")
        enriched.capabilities = data.get("capabilities", {})
        enriched.factual_counterfactual = analysis_block.get(
            "performance_characteristics", ""
        )
        enriched.user_behavior = data.get("user_behavior", {})
        enriched.security = data.get("security", {})

        enriched.validation_summary = {
            "status": "validated",
            "snapshot_hash": validation.snapshot_hash,
            "issues": validation.issues,
            "speculative_fields": validation.speculative_fields,
            "schema": str(validation.schema_path) if validation.schema_path else None,
            "request_log": str(request_meta.get("request_path")),
            "response_log": str(response_path),
            "payload_bytes": request_meta.get("payload_bytes"),
            "payload_truncated": request_meta.get("truncated", False),
        }
        try:
            canonical_manager.save_validated_output(
                enriched.name,
                enriched.version,
                {
                    "enriched": data,
                    "validation": enriched.validation_summary,
                },
            )
        except Exception as save_error:
            self.logger.warning(
                "Failed to persist validated enrichment for %s: %s",
                enriched.name,
                save_error,
            )
        return validation

    async def _invoke_structured_transformer(
        self,
        enriched: EnrichedCrate,
        snapshot: Dict[str, Any],
        canonical_manager: CanonicalDataManager,
        validator: EnrichedValidator,
        snapshot_metadata: Optional[SnapshotMetadata],
    ) -> Tuple["ValidationResult", Dict[str, Any], Path]:
        """Call LM Studio with the canonical snapshot + schema."""
        contract = validator.prompt_contract()
        payload = {
            "crate_snapshot": self._prepare_snapshot_for_llm(snapshot),
            "target_schema": contract,
        }

        system_prompt = (
            "You are a JSON transformer operating under strict governance. "
            "You must extract and transform information from crate_snapshot into the enriched object. "
            "You may ONLY use information from crate_snapshot and its source_analysis; do NOT use any external knowledge or assumptions.\n"
            "\n"
            "CRITICAL OUTPUT FORMAT:\n"
            "The final JSON must have this exact shape at the top level:\n"
            '{\n  "enriched": { ... }\n}\n'
            "Do NOT include $schema, title, properties, or any schema definition fields in your output. "
            "Only output the enriched object wrapped exactly as shown above.\n"
            "\n"
            "REQUIRED FIELDS (must always be present):\n"
            "- warnings: Array of strings. Always include this field. If no warnings, use []. "
            "Include warnings for: missing security audits, parsing errors, inferred values, ambiguous data.\n"
            "- speculative_fields: Array of JSON paths (strings) for fields that rely on inference. "
            "Always include this field. If nothing is speculative, use []. "
            "Example paths: \"analysis.community_health\", \"user_behavior.target_audience\".\n"
            "\n"
            "A field is speculative if it is NOT a direct copy or trivial rephrasing of a single input value. "
            "Any interpreted, inferred, or combined field MUST have its JSON path added to speculative_fields.\n"
            "At minimum, treat these as speculative when they are not direct copies:\n"
            "- analysis.community_health\n"
            "- analysis.code_quality\n"
            "- analysis.performance_characteristics\n"
            "- analysis.use_case_suitability\n"
            "- user_behavior.target_audience\n"
            "- user_behavior.adoption_patterns\n"
            "\n"
            "MECHANICAL EXTRACTION RULES (follow exactly):\n"
            "\n"
            "quality_score:\n"
            "- If source_analysis.insights.overall_quality_score exists and is a number, use that value.\n"
            "- Only use null if source_analysis.insights.overall_quality_score is completely missing.\n"
            "\n"
            "capabilities.no_std:\n"
            "- Set to true if \"no-std\" appears in crate_snapshot.categories (as a string) OR in any feature name.\n"
            "- Set to false otherwise.\n"
            "- This is a boolean check, not inference.\n"
            "\n"
            "capabilities.supported_formats:\n"
            "- Only include data formats like \"JSON\", \"TOML\", \"YAML\", \"CBOR\", \"RON\", \"MessagePack\".\n"
            "- Do NOT list programming languages (Rust, C++, etc.) here.\n"
            "- Check description and keywords for explicit format mentions.\n"
            "- If no formats are mentioned, use empty array [].\n"
            "\n"
            "analysis.security_concerns:\n"
            "- Build as array of strings from:\n"
            "  * source_analysis.failure_analysis.critical_missing (if present)\n"
            "  * source_analysis.geiger_insights.errors or warnings\n"
            "  * source_analysis.insights.security_risk_level if it indicates issues\n"
            "  * Any failed or missing security audit tools\n"
            "- Example: [\"Security audit missing - manual review required\", \"Geiger parsing error\"]\n"
            "- If no security concerns found, use [].\n"
            "\n"
            "OTHER FIELD RULES:\n"
            "- readme_summary: Summarize description and keywords if readme is empty\n"
            "- feature_summary: Describe the features from the features object\n"
            "- use_case: Derive from description, keywords, and categories\n"
            "- analysis.maintenance_status: Use source_analysis.insights.maintenance_health if available\n"
            "- analysis.community_health: Infer from downloads, github_stars, and source_analysis\n"
            "- analysis.code_quality: Use source_analysis.insights.code_quality or infer from clippy/test results\n"
            "- analysis.documentation_quality: Use source_analysis.insights.performance_indicators.documentation_quality\n"
            "- analysis.performance_characteristics: Summarize from source_analysis.build/test results\n"
            "- analysis.use_case_suitability: Derive from keywords, categories, and description\n"
            "- user_behavior.target_audience: Infer from description, keywords, and categories\n"
            "- user_behavior.adoption_patterns: Infer from downloads and github_stars\n"
            "- security.risk_level: Use source_analysis.insights.security_risk_level\n"
            "\n"
            "IMPORTANT GUIDELINES:\n"
            "- Prefer \"unknown\" over guessing when data is missing or ambiguous.\n"
            "- For string fields with no reliable information, use the literal string \"unknown\".\n"
            "- For array fields with no items, use [].\n"
            "- For quality_score, only use null as specified above.\n"
            "- Do not invent details (e.g., supported formats, languages) that are not present in the input.\n"
            "- Mark inferred fields in speculative_fields array as described above.\n"
            "- Output must be a single JSON object that validates against target_schema and uses the required top-level shape."
        )
        user_prompt = (
            "Extract and transform information from crate_snapshot to fill the `enriched` object according to target_schema. "
            "Be thorough and mechanical in following the extraction rules.\n"
            "\n"
            "REQUIRED: Return ONLY this JSON structure:\n"
            '{\n  "enriched": { ... }\n}\n'
            "\n"
            "CRITICAL: The enriched object MUST include:\n"
            "- warnings: array (can be [] if none)\n"
            "- speculative_fields: array (can be [] if none)\n"
            "\n"
            "Follow the mechanical rules exactly, especially for quality_score, capabilities.no_std, "
            "capabilities.supported_formats, and analysis.security_concerns.\n"
            "\n"
            "Respond with valid JSON only - no markdown, no schema definition, no commentary."
        )
        payload_text = json.dumps(payload, ensure_ascii=False, indent=2)
        
        # Token counting safety check - use chunking if exceeds context limit
        if TIKTOKEN_AVAILABLE:
            prompt_tokens = len(self.tokenizer.encode(system_prompt + user_prompt + payload_text))
            max_context = self.config.model_token_limit
            # Reserve space for response tokens (typically 1-2k)
            response_reserve = 2000
            # If prompt exceeds available space, use chunking
            if prompt_tokens > (max_context - response_reserve):
                self.logger.info(
                    "Prompt for %s is %d tokens, exceeds context limit of %d. Using chunked processing.",
                    enriched.name,
                    prompt_tokens,
                    max_context,
                )
                return await self._process_chunked_enrichment(
                    enriched, snapshot, canonical_manager, validator, snapshot_metadata
                )
            elif prompt_tokens > self.config.prompt_token_margin:
                self.logger.warning(
                    "Prompt for %s is %d tokens, exceeds margin of %d. May cause truncation.",
                    enriched.name,
                    prompt_tokens,
                    self.config.prompt_token_margin,
                )
            else:
                self.logger.debug(
                    "Prompt for %s is %d tokens (within %d margin)",
                    enriched.name,
                    prompt_tokens,
                    self.config.prompt_token_margin,
                )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{user_prompt}\n\n{payload_text}"},
        ]

        cfg = getattr(self.llm_client, "cfg", None)
        provider = getattr(cfg, "provider", "unknown")
        model = getattr(cfg, "model", "unknown")

        request_meta = canonical_manager.log_llm_request(
            enriched.name,
            enriched.version,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            payload=payload,
            provider=provider,
            model=model,
        )

        snapshot_hash = snapshot_metadata.hash if snapshot_metadata else None
        
        # Add timeout for large contexts - use config timeout with extra buffer for processing
        timeout_seconds = self.config.llm_request_timeout * 1.5  # 50% buffer for large contexts
        try:
            response = await asyncio.wait_for(
                self.llm_client.chat_json(
                    messages,
                    schema=contract,
                    max_tokens=max(1200, self.config.max_tokens),
                    temperature=0.0,
                ),
                timeout=timeout_seconds,
            )
        except asyncio.TimeoutError:
            self.logger.error(
                "LLM request timed out after %d seconds for %s. Prompt may be too large.",
                timeout_seconds,
                enriched.name,
            )
            raise ValidationFailure(
                f"LLM request timed out for {enriched.name}. Consider using chunking or increasing timeout."
            )
        
        response_path = canonical_manager.log_llm_response(
            enriched.name, enriched.version, response
        )

        validation = validator.validate(
            snapshot, response, snapshot_hash=snapshot_hash
        )
        return validation, request_meta, response_path

    def _estimate_token_count(self, data: Dict[str, Any]) -> int:
        """Estimate token count for a data structure."""
        if not TIKTOKEN_AVAILABLE:
            # Fallback: rough estimate (4 chars per token)
            json_str = json.dumps(data, ensure_ascii=False)
            return len(json_str) // 4
        json_str = json.dumps(data, ensure_ascii=False)
        return len(self.tokenizer.encode(json_str))

    def _chunk_snapshot_intelligently(
        self, 
        snapshot: Dict[str, Any], 
        max_tokens_per_chunk: int
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Chunk snapshot into multiple pieces that fit within context window.
        Returns list of (chunk_type, chunk_data) tuples.
        Each chunk includes core metadata + specific data sections.
        """
        chunks: List[Tuple[str, Dict[str, Any]]] = []
        core_metadata = {
            "name": snapshot.get("name"),
            "version": snapshot.get("version"),
            "description": snapshot.get("description"),
            "repository": snapshot.get("repository"),
            "keywords": snapshot.get("keywords"),
            "categories": snapshot.get("categories"),
            "downloads": snapshot.get("downloads"),
            "github_stars": snapshot.get("github_stars"),
            "license": snapshot.get("license"),
        }
        
        # Estimate core metadata size
        core_tokens = self._estimate_token_count(core_metadata)
        # Reserve tokens for prompts (system + user prompts) - more conservative
        prompt_overhead = 2000  # Approximate tokens for system/user prompts in chunked mode
        available_tokens = max_tokens_per_chunk - core_tokens - prompt_overhead
        
        # Ensure we have reasonable space for data
        if available_tokens < 1000:
            self.logger.warning(
                "Very limited tokens available per chunk (%d). Using more aggressive chunking.",
                available_tokens,
            )
            # Reduce prompt overhead if needed
            available_tokens = max(500, max_tokens_per_chunk - core_tokens - 1000)
        
        if available_tokens < 500:
            self.logger.warning(
                "Very limited tokens available per chunk (%d). Chunking may be inefficient.",
                available_tokens,
            )
        
        # Chunk 1: Core + Dependencies
        deps = snapshot.get("dependencies") or []
        if deps:
            deps_data = {"dependencies": deps, "dependency_count": len(deps)}
            deps_tokens = self._estimate_token_count(deps_data)
            if deps_tokens <= available_tokens:
                chunk1 = {**core_metadata, **deps_data}
                chunks.append(("dependencies", chunk1))
            else:
                # Split dependencies into batches
                num_batches = (deps_tokens // available_tokens) + 1
                chunk_size = max(1, len(deps) // num_batches)
                for i in range(0, len(deps), chunk_size):
                    chunk_deps = deps[i:i+chunk_size]
                    chunk_data = {
                        **core_metadata,
                        "dependencies": chunk_deps,
                        "dependency_batch": f"{i//chunk_size + 1}",
                        "dependency_total": len(deps),
                    }
                    chunks.append(("dependencies", chunk_data))
        
        # Chunk 2: Core + Features
        features = snapshot.get("features") or {}
        if features:
            features_data = {"features": features, "feature_count": len(features)}
            features_tokens = self._estimate_token_count(features_data)
            if features_tokens <= available_tokens:
                chunks.append(("features", {**core_metadata, **features_data}))
            else:
                # Split features
                feature_items = list(features.items())
                num_batches = (features_tokens // available_tokens) + 1
                chunk_size = max(1, len(feature_items) // num_batches)
                for i in range(0, len(feature_items), chunk_size):
                    chunk_features = dict(feature_items[i:i+chunk_size])
                    chunk_data = {
                        **core_metadata,
                        "features": chunk_features,
                        "feature_batch": f"{i//chunk_size + 1}",
                        "feature_total": len(features),
                    }
                    chunks.append(("features", chunk_data))
        
        # Chunk 3: Core + Source Analysis (split by section, more aggressively)
        analysis = snapshot.get("source_analysis") or {}
        if analysis:
            # Split analysis into logical sections
            analysis_sections = {
                "environment": analysis.get("environment"),
                "build": analysis.get("build"),
                "test": analysis.get("test"),
                "clippy": analysis.get("clippy"),
                "fmt": analysis.get("fmt"),
                "audit": analysis.get("audit"),
                "geiger": analysis.get("geiger"),
                "insights": analysis.get("insights"),
                "failure_analysis": analysis.get("failure_analysis"),
            }
            
            # Process each section individually to ensure they fit
            for section_name, section_data in analysis_sections.items():
                if not section_data:
                    continue
                
                # Check if section fits alone
                section_tokens = self._estimate_token_count({"source_analysis": {section_name: section_data}})
                if core_tokens + section_tokens <= available_tokens:
                    # Section fits with core metadata
                    chunks.append(("source_analysis", {
                        **core_metadata,
                        "source_analysis": {section_name: section_data}
                    }))
                else:
                    # Section is too large - split it further if it's a dict
                    if isinstance(section_data, dict):
                        # Split large sections by sub-keys
                        for sub_key, sub_value in list(section_data.items())[:20]:  # Limit to prevent explosion
                            sub_section_tokens = self._estimate_token_count({
                                "source_analysis": {section_name: {sub_key: sub_value}}
                            })
                            if core_tokens + sub_section_tokens <= available_tokens:
                                chunks.append(("source_analysis", {
                                    **core_metadata,
                                    "source_analysis": {section_name: {sub_key: sub_value}}
                                }))
                            else:
                                # Still too large - just include a summary
                                self.logger.debug(
                                    "Section %s.%s is too large (%d tokens), including summary only",
                                    section_name,
                                    sub_key,
                                    sub_section_tokens,
                                )
                                # Include just the key name as a placeholder
                                chunks.append(("source_analysis", {
                                    **core_metadata,
                                    "source_analysis": {section_name: {sub_key: "[data too large - see full snapshot]"}}
                                }))
                    else:
                        # Non-dict section that's too large - include summary
                        chunks.append(("source_analysis", {
                            **core_metadata,
                            "source_analysis": {section_name: "[data too large - see full snapshot]"}
                        }))
        
        # Chunk 4: Core + README (split by sections if too large)
        readme = snapshot.get("readme")
        if readme and isinstance(readme, str):
            readme_data = {"readme": readme}
            readme_tokens = self._estimate_token_count(readme_data)
            if readme_tokens <= available_tokens:
                chunks.append(("readme", {**core_metadata, **readme_data}))
            else:
                # Split README by sections (markdown headers)
                sections = re.split(r'\n(#{1,6}\s+.+?)\n', readme)
                current_readme = ""
                current_tokens = core_tokens
                section_idx = 0
                
                for i, section in enumerate(sections):
                    section_tokens = self._estimate_token_count({"readme": section})
                    if current_tokens + section_tokens <= available_tokens:
                        current_readme += section
                        current_tokens += section_tokens
                    else:
                        if current_readme:
                            chunks.append(("readme", {
                                **core_metadata,
                                "readme": current_readme,
                                "readme_section": f"{section_idx}",
                            }))
                            section_idx += 1
                        current_readme = section
                        current_tokens = core_tokens + section_tokens
                
                if current_readme:
                    chunks.append(("readme", {
                        **core_metadata,
                        "readme": current_readme,
                        "readme_section": f"{section_idx}",
                    }))
        
        # Chunk 5: Core + Rustdoc JSON (split by top-level keys)
        rustdoc = snapshot.get("rustdoc_json")
        if rustdoc:
            if isinstance(rustdoc, dict):
                rustdoc_tokens = self._estimate_token_count({"rustdoc_json": rustdoc})
                if rustdoc_tokens <= available_tokens:
                    chunks.append(("rustdoc", {**core_metadata, "rustdoc_json": rustdoc}))
                else:
                    # Split rustdoc by top-level keys
                    for key, value in rustdoc.items():
                        key_data = {"rustdoc_json": {key: value}}
                        key_tokens = self._estimate_token_count(key_data)
                        if key_tokens <= available_tokens:
                            chunks.append(("rustdoc", {
                                **core_metadata,
                                **key_data,
                                "rustdoc_key": key,
                            }))
                        else:
                            # Further split large rustdoc sections
                            if isinstance(value, dict):
                                for subkey, subvalue in list(value.items())[:10]:  # Limit to prevent explosion
                                    chunks.append(("rustdoc", {
                                        **core_metadata,
                                        "rustdoc_json": {key: {subkey: subvalue}},
                                        "rustdoc_key": f"{key}.{subkey}",
                                    }))
            elif isinstance(rustdoc, str):
                # If rustdoc is a string (path or JSON string), include as-is if small enough
                rustdoc_data = {"rustdoc_json": rustdoc}
                rustdoc_tokens = self._estimate_token_count(rustdoc_data)
                if rustdoc_tokens <= available_tokens:
                    chunks.append(("rustdoc", {**core_metadata, **rustdoc_data}))
        
        # Enhanced scraping data
        enhanced_scraping = snapshot.get("enhanced_scraping")
        if enhanced_scraping:
            enhanced_data = {"enhanced_scraping": enhanced_scraping}
            enhanced_tokens = self._estimate_token_count(enhanced_data)
            if enhanced_tokens <= available_tokens:
                chunks.append(("enhanced_scraping", {**core_metadata, **enhanced_data}))
        
        # If no chunks created, return at least core metadata
        if not chunks:
            chunks.append(("core", core_metadata))
        
        return chunks

    async def _process_chunked_enrichment(
        self,
        enriched: EnrichedCrate,
        snapshot: Dict[str, Any],
        canonical_manager: CanonicalDataManager,
        validator: EnrichedValidator,
        snapshot_metadata: Optional[SnapshotMetadata],
    ) -> Tuple["ValidationResult", Dict[str, Any], Path]:
        """
        Process enrichment in chunks and merge results without data loss.
        Includes robust error handling and timeouts.
        """
        # Use actual model context limit (may be smaller than config)
        # LM Studio models often have smaller context than advertised
        max_context = min(self.config.model_token_limit, 12000)  # Conservative limit
        # Reserve space for response tokens and prompt overhead
        response_reserve = 2000  # For LLM response
        prompt_overhead = 2000   # For system + user prompts
        max_tokens_per_chunk = max_context - response_reserve - prompt_overhead
        
        # Chunk the snapshot
        chunks = self._chunk_snapshot_intelligently(snapshot, max_tokens_per_chunk)
        
        self.logger.info(
            "Processing %s@%s in %d chunks (prompt exceeds context window)",
            enriched.name,
            enriched.version,
            len(chunks),
        )
        
        # Process each chunk with timeout and error handling
        chunk_results: List[Dict[str, Any]] = []
        timeout_seconds = self.config.llm_request_timeout * 2.0  # Extra timeout for chunked processing
        
        for chunk_idx, (chunk_type, chunk_data) in enumerate(chunks):
            self.logger.debug(
                "Processing chunk %d/%d (type: %s) for %s",
                chunk_idx + 1,
                len(chunks),
                chunk_type,
                enriched.name,
            )
            
            try:
                # Create a temporary enriched object for this chunk
                chunk_enriched = EnrichedCrate(
                    name=enriched.name,
                    version=enriched.version,
                    description=enriched.description,
                    repository=enriched.repository,
                    keywords=enriched.keywords,
                    categories=enriched.categories,
                    readme=enriched.readme,
                    downloads=enriched.downloads,
                    github_stars=enriched.github_stars,
                    dependencies=enriched.dependencies,
                    features=enriched.features,
                    license=enriched.license,
                )
                
                # Process this chunk with timeout
                try:
                    validation, request_meta, response_path = await asyncio.wait_for(
                        self._invoke_single_chunk(
                            chunk_enriched,
                            chunk_data,
                            chunk_type,
                            chunk_idx,
                            canonical_manager,
                            validator,
                            snapshot_metadata,
                        ),
                        timeout=timeout_seconds,
                    )
                    
                    chunk_results.append({
                        "chunk_type": chunk_type,
                        "chunk_idx": chunk_idx,
                        "validation": validation,
                        "enriched": validation.enriched if validation else {},
                        "success": True,
                    })
                    
                except asyncio.TimeoutError:
                    self.logger.warning(
                        "Chunk %d (type: %s) timed out after %d seconds for %s",
                        chunk_idx + 1,
                        chunk_type,
                        timeout_seconds,
                        enriched.name,
                    )
                    chunk_results.append({
                        "chunk_type": chunk_type,
                        "chunk_idx": chunk_idx,
                        "validation": None,
                        "enriched": {},
                        "success": False,
                        "error": "timeout",
                    })
                except Exception as e:
                    self.logger.warning(
                        "Chunk %d (type: %s) failed for %s: %s",
                        chunk_idx + 1,
                        chunk_type,
                        enriched.name,
                        e,
                    )
                    chunk_results.append({
                        "chunk_type": chunk_type,
                        "chunk_idx": chunk_idx,
                        "validation": None,
                        "enriched": {},
                        "success": False,
                        "error": str(e),
                    })
                
                # Small delay between chunks to avoid overwhelming the LLM server
                await asyncio.sleep(0.5)
                
            except Exception as e:
                self.logger.error(
                    "Unexpected error processing chunk %d for %s: %s",
                    chunk_idx + 1,
                    enriched.name,
                    e,
                )
                chunk_results.append({
                    "chunk_type": chunk_type,
                    "chunk_idx": chunk_idx,
                    "validation": None,
                    "enriched": {},
                    "success": False,
                    "error": str(e),
                })
        
        # Check if we have any successful chunks
        successful_chunks = [r for r in chunk_results if r.get("success")]
        if not successful_chunks:
            raise ValidationFailure(
                f"All chunks failed for {enriched.name}. Cannot proceed with enrichment."
            )
        
        self.logger.info(
            "Successfully processed %d/%d chunks for %s",
            len(successful_chunks),
            len(chunks),
            enriched.name,
        )
        
        # Merge chunk results intelligently
        merged_enriched = self._merge_chunk_results(chunk_results, snapshot)
        
        # Validate merged result
        snapshot_hash = snapshot_metadata.hash if snapshot_metadata else None
        try:
            final_validation = validator.validate(
                snapshot,
                {"enriched": merged_enriched},
                snapshot_hash=snapshot_hash,
            )
        except Exception as e:
            self.logger.error(
                "Validation failed for merged chunks of %s: %s",
                enriched.name,
                e,
            )
            raise ValidationFailure(
                f"Merged chunk validation failed for {enriched.name}: {e}"
            )
        
        # Log chunked processing metadata
        canonical_manager.log_llm_request(
            enriched.name,
            enriched.version,
            system_prompt="[CHUNKED PROCESSING]",
            user_prompt=f"Processed {len(chunks)} chunks ({len(successful_chunks)} successful)",
            payload={
                "chunks": len(chunks),
                "successful_chunks": len(successful_chunks),
                "chunk_types": [c[0] for c in chunks],
            },
            provider="chunked",
            model="chunked",
        )
        
        return final_validation, {"enriched": merged_enriched}, response_path

    async def _invoke_single_chunk(
        self,
        enriched: EnrichedCrate,
        chunk_data: Dict[str, Any],
        chunk_type: str,
        chunk_idx: int,
        canonical_manager: CanonicalDataManager,
        validator: EnrichedValidator,
        snapshot_metadata: Optional[SnapshotMetadata],
    ) -> Tuple["ValidationResult", Dict[str, Any], Path]:
        """Process a single chunk through the LLM."""
        contract = validator.prompt_contract()
        payload = {
            "crate_snapshot": chunk_data,
            "target_schema": contract,
        }
        
        system_prompt = (
            "You are a JSON transformer operating under strict governance. "
            "You must extract and transform information from crate_snapshot into the enriched object. "
            "You may ONLY use information from crate_snapshot and its source_analysis; do NOT use any external knowledge or assumptions.\n"
            "\n"
            "NOTE: This is CHUNK %d of a multi-chunk processing. The crate_snapshot contains a subset of the full crate data.\n"
            "Focus on extracting information from the provided chunk. Some fields may be incomplete.\n"
            "\n"
            "CRITICAL OUTPUT FORMAT:\n"
            "The final JSON must have this exact shape at the top level:\n"
            '{\n  "enriched": { ... }\n}\n'
            "Do NOT include $schema, title, properties, or any schema definition fields in your output. "
            "Only output the enriched object wrapped exactly as shown above.\n"
            "\n"
            "REQUIRED FIELDS (must always be present - use placeholders if data unavailable):\n"
            "- crate: Object with 'name' and 'version' from crate_snapshot. REQUIRED.\n"
            "- readme_summary: String. If readme is in this chunk, summarize it. Otherwise use \"unknown\" or \"See other chunks\". REQUIRED.\n"
            "- feature_summary: String. If features are in this chunk, summarize them. Otherwise use \"unknown\" or \"See other chunks\". REQUIRED.\n"
            "- quality_score: Number or null. Extract from source_analysis.insights.overall_quality_score if available, otherwise null. REQUIRED.\n"
            "- use_case: String. Derive from description/keywords if available, otherwise \"unknown\". REQUIRED.\n"
            "- analysis: Object with all required subfields (maintenance_status, community_health, code_quality, documentation_quality, security_concerns, performance_characteristics, use_case_suitability). Use \"unknown\" for missing data. REQUIRED.\n"
            "- user_behavior: Object (can be empty {} if no data). REQUIRED.\n"
            "- security: Object (can be empty {} if no data). REQUIRED.\n"
            "- capabilities: Object with no_std (boolean) and supported_formats (array). REQUIRED.\n"
            "- warnings: Array of strings. Always include this field. If no warnings, use []. "
            "Include warnings for: missing security audits, parsing errors, inferred values, ambiguous data, incomplete chunk data.\n"
            "- speculative_fields: Array of JSON paths (strings) for fields that rely on inference. "
            "Always include this field. If nothing is speculative, use []. "
            "Example paths: \"analysis.community_health\", \"user_behavior.target_audience\".\n"
            "\n"
            "MECHANICAL EXTRACTION RULES (follow exactly):\n"
            "\n"
            "quality_score:\n"
            "- If source_analysis.insights.overall_quality_score exists and is a number, use that value.\n"
            "- Only use null if source_analysis.insights.overall_quality_score is completely missing.\n"
            "\n"
            "capabilities.no_std:\n"
            "- Set to true if \"no-std\" appears in crate_snapshot.categories (as a string) OR in any feature name.\n"
            "- Set to false otherwise.\n"
            "- This is a boolean check, not inference.\n"
            "\n"
            "capabilities.supported_formats:\n"
            "- Only include data formats like \"JSON\", \"TOML\", \"YAML\", \"CBOR\", \"RON\", \"MessagePack\".\n"
            "- Do NOT list programming languages (Rust, C++, etc.) here.\n"
            "- Check description and keywords for explicit format mentions.\n"
            "- If no formats are mentioned, use empty array [].\n"
            "\n"
            "analysis.security_concerns:\n"
            "- Build as array of strings from:\n"
            "  * source_analysis.failure_analysis.critical_missing (if present)\n"
            "  * source_analysis.geiger_insights.errors or warnings\n"
            "  * source_analysis.insights.security_risk_level if it indicates issues\n"
            "  * Any failed or missing security audit tools\n"
            "- Example: [\"Security audit missing - manual review required\", \"Geiger parsing error\"]\n"
            "- If no security concerns found, use [].\n"
            "\n"
            "IMPORTANT GUIDELINES:\n"
            "- Prefer \"unknown\" over guessing when data is missing or ambiguous.\n"
            "- For string fields with no reliable information, use the literal string \"unknown\".\n"
            "- For array fields with no items, use [].\n"
            "- For quality_score, only use null as specified above.\n"
            "- Do not invent details (e.g., supported formats, languages) that are not present in the input.\n"
            "- Mark inferred fields in speculative_fields array.\n"
            "- Output must be a single JSON object that validates against target_schema and uses the required top-level shape."
        ) % (chunk_idx + 1)
        
        user_prompt = (
            "Extract and transform information from crate_snapshot to fill the `enriched` object according to target_schema. "
            "Be thorough and mechanical in following the extraction rules.\n"
            "\n"
            "NOTE: This is chunk %d. Extract what you can from this chunk's data.\n"
            "\n"
            "REQUIRED: Return ONLY this JSON structure:\n"
            '{\n  "enriched": { ... }\n}\n'
            "\n"
            "CRITICAL: The enriched object MUST include ALL required fields:\n"
            "- crate: {name: string, version: string} - REQUIRED (from crate_snapshot.name and crate_snapshot.version)\n"
            "- readme_summary: string - REQUIRED (use \"unknown\" if readme not in this chunk)\n"
            "- feature_summary: string - REQUIRED (use \"unknown\" if features not in this chunk)\n"
            "- quality_score: number or null - REQUIRED\n"
            "- use_case: string - REQUIRED (use \"unknown\" if cannot determine)\n"
            "- analysis: object with all subfields - REQUIRED\n"
            "- user_behavior: object - REQUIRED (can be empty {})\n"
            "- security: object - REQUIRED (can be empty {})\n"
            "- capabilities: object - REQUIRED\n"
            "- warnings: array - REQUIRED\n"
            "- speculative_fields: array - REQUIRED\n"
            "\n"
            "Follow the mechanical rules exactly, especially for quality_score, capabilities.no_std, "
            "capabilities.supported_formats, and analysis.security_concerns.\n"
            "\n"
            "Respond with valid JSON only - no markdown, no schema definition, no commentary."
        ) % (chunk_idx + 1)
        
        payload_text = json.dumps(payload, ensure_ascii=False, indent=2)
        full_user_content = f"{user_prompt}\n\n{payload_text}"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_user_content},
        ]
        
        # Verify chunk size before sending
        if TIKTOKEN_AVAILABLE:
            total_tokens = len(self.tokenizer.encode(system_prompt + full_user_content))
            max_safe_tokens = 10000  # Conservative limit for LM Studio
            if total_tokens > max_safe_tokens:
                self.logger.warning(
                    "Chunk %d (type: %s) is %d tokens, exceeds safe limit of %d. "
                    "This may cause errors. Consider more aggressive chunking.",
                    chunk_idx + 1,
                    chunk_type,
                    total_tokens,
                    max_safe_tokens,
                )
        
        cfg = getattr(self.llm_client, "cfg", None)
        provider = getattr(cfg, "provider", "unknown")
        model = getattr(cfg, "model", "unknown")
        
        request_meta = canonical_manager.log_llm_request(
            enriched.name,
            enriched.version,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            payload=payload,
            provider=f"{provider}_chunk_{chunk_idx}",
            model=model,
        )
        
        snapshot_hash = snapshot_metadata.hash if snapshot_metadata else None
        response = await self.llm_client.chat_json(
            messages,
            schema=contract,
            max_tokens=max(1200, self.config.max_tokens),
            temperature=0.0,
        )
        response_path = canonical_manager.log_llm_response(
            enriched.name, enriched.version, response
        )
        
        validation = validator.validate(
            chunk_data, response, snapshot_hash=snapshot_hash
        )
        return validation, request_meta, response_path

    def _merge_chunk_results(
        self,
        chunk_results: List[Dict[str, Any]],
        original_snapshot: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Merge multiple chunk results into a single enriched object.
        Strategy: Prefer direct extractions, combine arrays, merge objects deeply.
        Prevents hallucinations by prioritizing canonical data.
        """
        merged: Dict[str, Any] = {}
        warnings: List[str] = []
        speculative_fields: set = set()
        
        # Track which chunks contributed which fields
        field_sources: Dict[str, List[str]] = {}
        
        # Process chunks in order, with later chunks filling in gaps
        for chunk_result in chunk_results:
            if not chunk_result.get("success"):
                continue  # Skip failed chunks
                
            enriched = chunk_result.get("enriched", {})
            chunk_type = chunk_result.get("chunk_type", "unknown")
            
            # Merge warnings
            if isinstance(enriched.get("warnings"), list):
                warnings.extend(enriched["warnings"])
            
            # Merge speculative_fields
            if isinstance(enriched.get("speculative_fields"), list):
                speculative_fields.update(enriched["speculative_fields"])
            
            # Merge fields intelligently
            for key, value in enriched.items():
                if key in ("warnings", "speculative_fields"):
                    continue  # Handled separately
                
                if key not in merged:
                    # First occurrence - use as-is
                    merged[key] = value
                    field_sources[key] = [chunk_type]
                else:
                    # Merge based on type
                    existing = merged[key]
                    field_sources.setdefault(key, []).append(chunk_type)
                    
                    if isinstance(value, dict) and isinstance(existing, dict):
                        # Deep merge dictionaries
                        merged[key] = self._deep_merge_dicts(existing, value)
                    elif isinstance(value, list) and isinstance(existing, list):
                        # Combine lists, removing duplicates (preserve order)
                        seen = set()
                        combined = []
                        for item in existing + value:
                            # Use JSON string representation for deduplication
                            item_str = json.dumps(item, sort_keys=True) if isinstance(item, (dict, list)) else str(item)
                            if item_str not in seen:
                                seen.add(item_str)
                                combined.append(item)
                        merged[key] = combined
                    elif value is not None and existing is None:
                        # Replace None with actual value
                        merged[key] = value
                    elif isinstance(value, (str, int, float, bool)):
                        # For primitive types, prefer non-"unknown" values
                        if value != "unknown" and existing == "unknown":
                            merged[key] = value
                        elif existing == "unknown" and value == "unknown":
                            # Both unknown, keep existing
                            pass
                        # Otherwise keep existing value (first chunk wins for conflicts)
                    # For other types, keep existing value
        
        # Add merged warnings and speculative_fields
        merged["warnings"] = list(set(warnings))  # Deduplicate
        merged["speculative_fields"] = list(speculative_fields)
        
        # Ensure required fields from canonical snapshot are preserved
        # These should come from validator cross-checking, but ensure they're present
        if "quality_score" not in merged:
            # Extract from source_analysis if available
            insights = original_snapshot.get("source_analysis", {}).get("insights", {})
            if "overall_quality_score" in insights:
                merged["quality_score"] = insights["overall_quality_score"]
            else:
                merged["quality_score"] = None
        
        if "capabilities" not in merged:
            merged["capabilities"] = {}
        
        # Ensure no_std is set correctly from canonical data (prevent hallucination)
        if "capabilities" in merged:
            categories = original_snapshot.get("categories", [])
            features = original_snapshot.get("features", {})
            all_feature_names = list(features.keys()) if isinstance(features, dict) else []
            
            # Check canonical data directly
            has_no_std = (
                "no-std" in categories or
                any("no-std" in str(f).lower() or "no_std" in str(f).lower() for f in all_feature_names)
            )
            merged.setdefault("capabilities", {})["no_std"] = has_no_std
        
        # Ensure supported_formats comes from canonical data (prevent hallucination)
        if "capabilities" in merged and "supported_formats" not in merged.get("capabilities", {}):
            # Extract from canonical snapshot text
            text_candidates: List[str] = []
            for key in ("description", "readme"):
                value = original_snapshot.get(key)
                if isinstance(value, str):
                    text_candidates.append(value.lower())
            keywords = original_snapshot.get("keywords") or []
            if isinstance(keywords, list):
                text_candidates.extend(str(k).lower() for k in keywords)
            
            combined = " ".join(text_candidates)
            format_keywords = {
                "JSON": ["json"],
                "TOML": ["toml"],
                "YAML": ["yaml", "yml"],
                "CBOR": ["cbor"],
                "RON": ["ron"],
                "MessagePack": ["messagepack", "msgpack", "message-pack"],
            }
            detected_formats = []
            for fmt, tokens in format_keywords.items():
                if any(token in combined for token in tokens):
                    detected_formats.append(fmt)
            merged.setdefault("capabilities", {})["supported_formats"] = detected_formats
        
        # Add chunking metadata to warnings
        if field_sources:
            chunk_info = ", ".join(f"{k}:{','.join(v)}" for k, v in list(field_sources.items())[:5])
            merged["warnings"].append(f"Data merged from chunks: {chunk_info}")
        
        return merged

    def _deep_merge_dicts(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries, with dict1 taking precedence for conflicts."""
        result = dict1.copy()
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge_dicts(result[key], value)
            elif key not in result:
                result[key] = value
            # Otherwise keep existing value (dict1 wins)
        return result

    def _prepare_snapshot_for_llm(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare snapshot for LLM with 13k context window - pass more complete canonical data."""
        prepared: Dict[str, Any] = {
            "name": snapshot.get("name"),
            "version": snapshot.get("version"),
            "description": snapshot.get("description"),
            "repository": snapshot.get("repository"),
            "keywords": snapshot.get("keywords"),
            "categories": snapshot.get("categories"),
            "downloads": snapshot.get("downloads"),
            "github_stars": snapshot.get("github_stars"),
            "license": snapshot.get("license"),
        }

        # With 13k context, include FULL dependency list (not just top 10)
        dependencies = snapshot.get("dependencies") or []
        if isinstance(dependencies, list):
            prepared["dependencies"] = dependencies  # Full list for complete canonical data
            prepared["dependency_count"] = len(dependencies)

        # Include FULL feature set (not just top 10)
        features = snapshot.get("features") or {}
        if isinstance(features, dict):
            prepared["features"] = features  # Complete features dict
            prepared["feature_count"] = len(features)

        # Include much more README content (up to 5000 chars instead of 1000)
        readme = snapshot.get("readme")
        if isinstance(readme, str):
            # With 13k context, we can afford ~5k chars of README
            if len(readme) <= 5000:
                prepared["readme"] = readme
            else:
                prepared["readme"] = readme[:5000] + f"\n... [truncated, full length: {len(readme)} chars]"

        # Include FULL source analysis instead of just summary
        analysis = snapshot.get("source_analysis")
        if isinstance(analysis, dict):
            prepared["source_analysis"] = analysis  # Complete analysis for better grounding

        # Include enhanced scraping data if available
        enhanced_scraping = snapshot.get("enhanced_scraping")
        if enhanced_scraping:
            prepared["enhanced_scraping"] = enhanced_scraping

        # Include rustdoc JSON if available (for comprehensive documentation analysis)
        rustdoc_json = snapshot.get("rustdoc_json")
        if rustdoc_json:
            # For very large rustdoc JSON, we may still need to truncate
            # but with 13k context we can include more of it
            if isinstance(rustdoc_json, dict):
                prepared["rustdoc_json"] = rustdoc_json
            elif isinstance(rustdoc_json, str):
                # If it's a string path or JSON string, include it
                prepared["rustdoc_json"] = rustdoc_json

        return prepared

    async def _legacy_enrichment(self, enriched: EnrichedCrate) -> Dict[str, Any]:
        """Fallback enrichment pathway without canonical enforcement."""
        context = self._build_crate_context(enriched)
        enriched.readme_summary = await self._generate_summary(context)
        enriched.feature_summary = await self._generate_feature_summary(enriched)
        analysis = await self._perform_analysis(context)
        enriched.source_analysis = analysis.get("analysis", {})
        enriched.score = analysis.get("quality_score", 0.0)
        enriched.use_case = analysis.get("use_case", "unknown")
        enriched.factual_counterfactual = analysis.get("factual_pairs", "")
        enriched.user_behavior = analysis.get("user_behavior", {})
        enriched.security = analysis.get("security", {})
        enriched.validation_summary = {
            "status": "legacy",
            "issues": ["canonical validator unavailable"],
        }
        return analysis

    def _build_crate_context(self, enriched: EnrichedCrate) -> str:
        """Build context string for LLM analysis"""
        context_parts = []

        # Basic info
        context_parts.append(f"Crate: {enriched.name} v{enriched.version}")
        if enriched.description:
            context_parts.append(f"Description: {enriched.description}")

        # Repository
        if enriched.repository:
            context_parts.append(f"Repository: {enriched.repository}")

        # Keywords and categories
        if enriched.keywords:
            context_parts.append(f"Keywords: {', '.join(enriched.keywords)}")
        if enriched.categories:
            context_parts.append(f"Categories: {', '.join(enriched.categories)}")

        # Dependencies
        if enriched.dependencies:
            deps = [
                f"{dep.get('name', 'unknown')} {dep.get('version', '')}"
                for dep in enriched.dependencies
            ]
            context_parts.append(f"Dependencies: {', '.join(deps)}")

        # Features
        if enriched.features:
            context_parts.append(f"Features: {', '.join(enriched.features.keys())}")

        # Downloads and stars
        if enriched.downloads is not None:
            context_parts.append(f"Downloads: {enriched.downloads}")
        if enriched.github_stars is not None:
            context_parts.append(f"GitHub Stars: {enriched.github_stars}")

        # README (truncated)
        if enriched.readme:
            readme_preview = (
                enriched.readme[:1000] + "..."
                if len(enriched.readme) > 1000
                else enriched.readme
            )
            context_parts.append(f"README Preview: {readme_preview}")

        return "\n".join(context_parts)

    async def _generate_summary(self, context: str) -> str:
        """Generate AI summary of the crate"""
        prompt = (
            f"Analyze this Rust crate and provide a concise summary "
            f"(2-3 sentences):\n\n"
            f"{context}\n\n"
            f"Summary:"
        )

        try:
            response = await self.llm_client.chat(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,  # Increased for more detailed summaries
                temperature=0.3,
            )
            return response.strip()
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return "Summary generation failed"

    def _detect_special_capabilities(self, enriched: EnrichedCrate) -> Dict[str, Any]:
        """Detect special capabilities like no_std support and data formats"""
        capabilities = {
            "no_std": False,
            "data_formats": [],
        }
        
        # Check for no_std support
        no_std_indicators = ["no_std", "no-std", "nostd", "no std"]
        text_to_check = " ".join([
            enriched.description.lower(),
            " ".join(enriched.keywords).lower(),
            " ".join(enriched.categories).lower(),
            " ".join(enriched.features.keys()).lower() if enriched.features else "",
        ])
        
        if any(indicator in text_to_check for indicator in no_std_indicators):
            capabilities["no_std"] = True
        
        # Check for data format support
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
        
        for format_name, keywords in format_keywords.items():
            if any(keyword in text_to_check for keyword in keywords):
                capabilities["data_formats"].append(format_name)
        
        return capabilities

    async def _generate_feature_summary(self, enriched: EnrichedCrate) -> str:
        """Generate feature summary"""
        if not enriched.features:
            return "No features defined"

        # Detect special capabilities
        capabilities = self._detect_special_capabilities(enriched)
        
        # Build enhanced prompt
        prompt_parts = [
            "Summarize the key features of this Rust crate:",
            "",
            f"Crate: {enriched.name}",
            f"Features: {enriched.features}",
            f"Description: {enriched.description}",
        ]
        
        # Add special capabilities context
        if capabilities["no_std"]:
            prompt_parts.append(
                "\nNote: This crate supports no_std environments (can run without the Rust standard library), "
                "making it suitable for embedded systems, WebAssembly, and other constrained environments."
            )
        
        if capabilities["data_formats"]:
            formats_str = ", ".join(capabilities["data_formats"])
            prompt_parts.append(
                f"\nNote: This crate supports the following data formats: {formats_str}. "
                "Mention these formats in the summary when relevant."
            )
        
        prompt_parts.append("\nFeature Summary:")
        prompt = "\n".join(prompt_parts)

        try:
            response = await self.llm_client.chat(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,  # Increased to allow comprehensive summaries with no_std and format details
                temperature=0.2,
            )
            return response.strip()
        except Exception as e:
            self.logger.error(f"Error generating feature summary: {e}")
            return "Feature summary generation failed"

    async def _perform_analysis(self, context: str) -> Dict:
        """Perform comprehensive AI analysis of the crate"""
        prompt = (
            f"Analyze this Rust crate and provide a structured analysis in JSON format:\n\n"
            f"{context}\n\n"
            f"Provide analysis in this JSON format:\n"
            f"{{\n"
            f'    "analysis": {{\n'
            f'        "maintenance_status": "active|inactive|unknown",\n'
            f'        "community_health": "high|medium|low",\n'
            f'        "code_quality": "high|medium|low",\n'
            f'        "documentation_quality": "high|medium|low",\n'
            f'        "security_concerns": ["list", "of", "concerns"],\n'
            f'        "performance_characteristics": "description",\n'
            f'        "use_case_suitability": ["list", "of", "use", "cases"]\n'
            f"    }},\n"
            f'    "quality_score": 0.0-1.0,\n'
            f'    "use_case": "primary use case category",\n'
            f'    "factual_pairs": "3 factual statements and 3 counterfactual statements",\n'
            f'    "user_behavior": {{\n'
            f'        "target_audience": "description",\n'
            f'        "adoption_patterns": "description"\n'
            f"    }},\n"
            f'    "security": {{\n'
            f'        "risk_level": "low|medium|high",\n'
            f'        "vulnerabilities": ["list", "of", "concerns"]\n'
            f"    }}\n"
            f"}}"
        )

        try:
            response = await self.llm_client.chat_json(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.2,
            )
            return response
        except Exception as e:
            self.logger.error(f"Error performing analysis: {e}")
            return {
                "analysis": {"error": str(e)},
                "quality_score": 0.5,
                "use_case": "unknown",
                "factual_pairs": "Analysis failed",
                "user_behavior": {"error": str(e)},
                "security": {"error": str(e)},
            }

    async def close(self) -> None:
        """Close LLM client resources"""
        await self.llm_client.aclose()
