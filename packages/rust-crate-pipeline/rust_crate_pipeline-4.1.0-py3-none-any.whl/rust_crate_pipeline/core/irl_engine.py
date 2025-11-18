import json
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from ..version import __version__

from .canon_registry import CanonRegistry
from .sacred_chain import SacredChainBase, SacredChainTrace, TrustVerdict

# Import real analysis implementations
try:
    from ..utils.documentation_analyzer import analyze_documentation_quality
    from ..utils.sentiment_analyzer import analyze_community_sentiment
    from ..utils.ecosystem_analyzer import analyze_ecosystem_position
    REAL_ANALYSIS_AVAILABLE = True
except ImportError:
    REAL_ANALYSIS_AVAILABLE = False
    analyze_documentation_quality = None
    analyze_community_sentiment = None
    analyze_ecosystem_position = None


class IRLEngine(SacredChainBase):
    def __init__(
        self, config: Any, canon_registry: Optional[CanonRegistry] = None
    ) -> None:
        super().__init__()
        self.config = config
        self.canon_registry = canon_registry or CanonRegistry()
        self.logger = logging.getLogger(__name__)
        self.canon_version = __version__
        # Context storage for analysis functions
        self._crate_context: Dict[str, Any] = {}

    async def __aenter__(self) -> "IRLEngine":
        self.logger.info("IRL Engine initialized with full traceability")
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any],
    ) -> None:
        self._finalize_audit_log()

    def _finalize_audit_log(self) -> None:
        if not self.execution_log:
            return

        audit_file = f"audits/records/sigil_audit_{int(time.time())}.json"
        try:
            # Ensure audits/records directory exists
            import os

            os.makedirs("audits/records", exist_ok=True)

            from ..utils.file_utils import atomic_write_json

            # Since to_audit_log() returns JSON string, parse it first
            audit_data = []
            for trace in self.execution_log:
                try:
                    audit_entry = json.loads(trace.to_audit_log())
                    audit_data.append(audit_entry)
                except (json.JSONDecodeError, TypeError) as e:
                    self.logger.error(f"Failed to serialize trace: {e}")
                    # Add a fallback entry
                    audit_data.append(
                        {
                            "execution_id": getattr(trace, "execution_id", "unknown"),
                            "timestamp": getattr(trace, "timestamp", "unknown"),
                            "error": f"Serialization failed: {str(e)}",
                            "rule_zero_compliant": False,
                        }
                    )

            atomic_write_json(audit_file, audit_data)
            self.logger.info(f"Audit log finalized: {audit_file}")
        except IOError as e:
            self.logger.error(f"Failed to write audit log {audit_file}: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error finalizing audit log: {e}")

    async def analyze_with_sacred_chain(
        self, input_data: str, context: Optional[Dict[str, Any]] = None
    ) -> SacredChainTrace:
        canonical_input = self._canonicalize_input(input_data)
        reasoning_steps = [
            f"Input canonicalized: '{input_data}' -> '{canonical_input}'"
        ]
        
        # Store context for analysis functions
        if context:
            self._crate_context = context
            # Store fetched_crate_metadata reference for later use in trust decisions
            if "metadata" in context:
                self._fetched_crate_metadata = context["metadata"]
            else:
                self._fetched_crate_metadata = None
        else:
            self._crate_context = {}
            self._fetched_crate_metadata = None

        context_sources = await self._gather_validated_context(canonical_input)
        reasoning_steps.append(
            f"Context gathered from {len(context_sources)} validated sources"
        )

        analysis_results = await self._execute_reasoning_chain(
            canonical_input, context_sources
        )
        reasoning_steps.extend(analysis_results[0])

        # Extract results for easier access
        metadata = analysis_results[1]
        docs = analysis_results[2]
        sentiment = analysis_results[3]
        ecosystem = analysis_results[4]
        quality_score = analysis_results[5]

        # Ensure we have fetched_crate_metadata available for trust decisions
        # It should be in context, but also check if metadata has downloads
        if not hasattr(self, '_fetched_crate_metadata') or not self._fetched_crate_metadata:
            # Try to get it from context if available
            if self._crate_context and "metadata" in self._crate_context:
                self._fetched_crate_metadata = self._crate_context["metadata"]

        suggestion = self._generate_traceable_suggestion(
            reasoning_steps, quality_score, docs, sentiment, ecosystem, metadata
        )
        
        # Get ML predictions from context if available
        ml_predictions = None
        if self._crate_context:
            ml_predictions = self._crate_context.get("ml_predictions")
        
        verdict, verdict_reason = self._make_trust_decision(
            reasoning_steps,
            suggestion,
            quality_score,
            metadata,
            docs,
            sentiment,
            ecosystem,
            ml_predictions=ml_predictions,
        )
        reasoning_steps.append(f"Trust decision: {verdict} - {verdict_reason}")

        irl_score = self._calculate_irl_score(
            context_sources, reasoning_steps, verdict, quality_score, docs, sentiment, ecosystem
        )
        reasoning_steps.append(f"Analysis confidence: {irl_score:.3f} (confidence in analysis process, not trustworthiness)")

        audit_info = {
            "metadata": analysis_results[1],
            "docs": analysis_results[2],
            "sentiment": analysis_results[3],
            "ecosystem": analysis_results[4],
            "quality_score": analysis_results[5],
            "verdict_reason": verdict_reason,
        }

        return self.create_sacred_chain_trace(
            input_data=canonical_input,
            context_sources=context_sources,
            reasoning_steps=reasoning_steps,
            suggestion=suggestion,
            verdict=verdict,
            audit_info=audit_info,
            irl_score=irl_score,
        )

    def _canonicalize_input(self, input_data: str) -> str:
        canonical = input_data.strip().lower()
        if canonical.startswith("crate:"):
            canonical = canonical[6:]
        if canonical.startswith("rust:"):
            canonical = canonical[5:]
        return canonical

    async def _gather_validated_context(self, input_data: str) -> List[str]:
        valid_sources = self.canon_registry.get_valid_canon_sources()
        context_sources = []

        for source in valid_sources:
            authority_level = self.canon_registry.get_authority_level(source)
            if authority_level >= 5:
                context_sources.append(source)

        return context_sources

    async def _execute_reasoning_chain(
        self, input_data: str, sources: List[str]
    ) -> Tuple[
        List[str], Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any], float
    ]:
        reasoning_steps = []

        metadata = await self._extract_basic_metadata(input_data)
        reasoning_steps.append(f"Metadata extracted: {len(metadata)} fields")

        docs = {}
        docs = await self._analyze_documentation(input_data)
        reasoning_steps.append(
            f"Documentation analyzed: quality {docs.get('quality_score', 0):.1f}"
        )

        sentiment = await self._analyze_community_sentiment(input_data)
        reasoning_steps.append(
            f"Sentiment analyzed: {sentiment.get('overall', 'unknown')}"
        )

        ecosystem = await self._analyze_ecosystem_position(input_data)
        reasoning_steps.append(
            f"Ecosystem analyzed: {ecosystem.get('category', 'unknown')}"
        )

        # Get ML predictions from context if available
        ml_predictions = None
        if self._crate_context:
            ml_predictions = self._crate_context.get("ml_predictions")
        
        quality_score = self._synthesize_quality_score(
            metadata, docs, sentiment, ecosystem, ml_predictions=ml_predictions
        )
        # Debug: log the components for troubleshooting
        star_count = sentiment.get("star_count", 0)
        doc_score = docs.get("quality_score", 5.0)
        ecosystem_score = ecosystem.get("ecosystem_score", 5.0)
        reasoning_steps.append(
            f"Quality score synthesized: {quality_score:.2f} "
            f"(docs={doc_score:.1f}, stars={star_count}, ecosystem={ecosystem_score:.1f})"
        )

        return reasoning_steps, metadata, docs, sentiment, ecosystem, quality_score

    async def _extract_basic_metadata(self, input_data: str) -> Dict[str, Any]:
        """Extract basic metadata, using context if available."""
        metadata = {
            "name": input_data,
            "type": "rust_crate",
            "source": "manual_input",
            "extraction_method": "irl_engine",
        }
        
        # Use fetched metadata from context if available (includes downloads, etc.)
        if self._crate_context:
            # Context should have "metadata" key set by pipeline_analysis.py
            fetched_metadata = self._crate_context.get("metadata")
            if fetched_metadata:
                # Merge important fields from fetched metadata
                downloads = fetched_metadata.get("downloads", 0)
                license_value = fetched_metadata.get("license")
                
                # If license is not in metadata, try to parse from lib.rs scraped content
                if not license_value:
                    sanitized_docs = self._crate_context.get("sanitized_documentation")
                    if sanitized_docs:
                        license_value = self._parse_license_from_librs(sanitized_docs)
                
                metadata.update({
                    "downloads": downloads if downloads else 0,
                    "version": fetched_metadata.get("version"),
                    "description": fetched_metadata.get("description"),
                    "repository": fetched_metadata.get("repository"),
                    "license": license_value,
                    "github_stars": fetched_metadata.get("github_stars", 0),
                })
                # Debug: log if downloads are found
                if downloads:
                    self.logger.debug(f"Extracted downloads from context: {downloads:,} for {input_data}")
                if license_value:
                    self.logger.debug(f"Extracted license: {license_value} for {input_data}")
        
        return metadata

    def _parse_license_from_librs(self, sanitized_docs: Dict[str, Any]) -> Optional[str]:
        """Parse license from lib.rs scraped content."""
        import re
        
        lib_rs_data = sanitized_docs.get("lib_rs")
        if not lib_rs_data or not isinstance(lib_rs_data, dict):
            return None
        
        content = lib_rs_data.get("content", "")
        if not content:
            return None
        
        # Pattern 1: "**MIT** license" or "**MIT/Apache** license"
        pattern1 = r'\*\*([A-Za-z0-9\-\s/]+)\*\*\s+license'
        match1 = re.search(pattern1, content, re.IGNORECASE)
        if match1:
            license_str = match1.group(1).strip()
            # Normalize common variations
            license_str = license_str.replace(' ', '-')
            self.logger.debug(f"Found license from lib.rs: {license_str}")
            return license_str
        
        # Pattern 2: "license: MIT" or "License: MIT/Apache-2.0"
        pattern2 = r'[Ll]icense\s*[:=]\s*([A-Za-z0-9\-\s/]+)'
        match2 = re.search(pattern2, content)
        if match2:
            license_str = match2.group(1).strip()
            # Remove trailing punctuation
            license_str = re.sub(r'[.,;]+$', '', license_str)
            license_str = license_str.replace(' ', '-')
            self.logger.debug(f"Found license from lib.rs (pattern 2): {license_str}")
            return license_str
        
        # Pattern 3: Look for common license names near "license" keyword
        common_licenses = ['MIT', 'Apache-2.0', 'Apache', 'BSD', 'GPL', 'LGPL', 'ISC', 'Unlicense', 'CC0']
        for license_name in common_licenses:
            # Look for license name within 50 chars of "license" keyword
            pattern3 = rf'license.{0,50}?{re.escape(license_name)}|{re.escape(license_name)}.{0,50}?license'
            if re.search(pattern3, content, re.IGNORECASE):
                self.logger.debug(f"Found license from lib.rs (pattern 3): {license_name}")
                return license_name
        
        return None

    async def _analyze_documentation(self, input_data: str) -> Dict[str, Any]:
        """Analyze documentation quality using real implementation."""
        try:
            if REAL_ANALYSIS_AVAILABLE and analyze_documentation_quality:
                # Extract context
                readme_content = self._crate_context.get("readme", "")
                repository_url = self._crate_context.get("repository_url")
                crate_metadata = self._crate_context.get("metadata")
                
                result = await analyze_documentation_quality(
                    crate_name=input_data,
                    readme_content=readme_content,
                    repository_url=repository_url,
                    crate_metadata=crate_metadata,
                )
                return result
            else:
                # Fallback to stub
                self.logger.warning("Real documentation analysis not available, using stub")
                return {
                    "quality_score": 7.0,
                    "completeness": 0.8,
                    "examples_present": True,
                    "api_documented": True,
                }
        except Exception as e:
            self.logger.error(f"Documentation analysis failed: {e}")
            return {"quality_score": 5.0, "error": str(e)}

    async def _analyze_community_sentiment(self, input_data: str) -> Dict[str, Any]:
        """Analyze community sentiment using real implementation."""
        try:
            if REAL_ANALYSIS_AVAILABLE and analyze_community_sentiment:
                repository_url = self._crate_context.get("repository_url")
                github_token = getattr(self.config, "github_token", None)
                
                result = await analyze_community_sentiment(
                    crate_name=input_data,
                    repository_url=repository_url,
                    github_token=github_token,
                )
                return result
            else:
                # Fallback to stub
                self.logger.warning("Real sentiment analysis not available, using stub")
                return {
                    "overall": "positive",
                    "positive_mentions": 10,
                    "negative_mentions": 2,
                    "neutral_mentions": 5,
                    "total_mentions": 17,
                }
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {e}")
            return {
                "overall": "unknown",
                "positive_mentions": 0,
                "negative_mentions": 0,
                "neutral_mentions": 0,
                "error": str(e),
            }

    async def _analyze_ecosystem_position(self, input_data: str) -> Dict[str, Any]:
        """Analyze ecosystem position using real implementation."""
        try:
            if REAL_ANALYSIS_AVAILABLE and analyze_ecosystem_position:
                repository_url = self._crate_context.get("repository_url")
                crate_metadata = self._crate_context.get("metadata")
                github_token = getattr(self.config, "github_token", None)
                # Get sanitized_documentation from context if available (for parsing lib.rs content)
                sanitized_documentation = self._crate_context.get("sanitized_documentation")
                
                result = await analyze_ecosystem_position(
                    crate_name=input_data,
                    repository_url=repository_url,
                    crate_metadata=crate_metadata,
                    github_token=github_token,
                    sanitized_documentation=sanitized_documentation,
                )
                return result
            else:
                # Fallback to stub
                self.logger.warning("Real ecosystem analysis not available, using stub")
                return {
                    "category": "utilities",
                    "maturity": "stable",
                    "dependencies_count": 5,
                    "reverse_deps_visible": 15,
                    "ecosystem_score": 7.5,
                }
        except Exception as e:
            self.logger.error(f"Ecosystem analysis failed: {e}")
            return {
                "category": "utilities",
                "maturity": "pre-stable",
                "dependencies_count": 0,
                "reverse_dependencies_count": 0,
                "ecosystem_score": 5.0,
                "error": str(e),
            }

    def _synthesize_quality_score(
        self,
        metadata: Dict[str, Any],
        docs: Dict[str, Any],
        sentiment: Dict[str, Any],
        ecosystem: Dict[str, Any],
        ml_predictions: Optional[Dict[str, Any]] = None,
    ) -> float:
        """Synthesize overall quality score from component scores.
        
        Uses weighted average to give more importance to ecosystem position
        for well-established crates, while still considering documentation and sentiment.
        Now incorporates ML predictions when available.
        """
        # Base doc score - but don't penalize if scraping failed
        doc_score = docs.get("quality_score", 5.0)
        # If doc score is very low but we have metadata, assume docs are decent
        if doc_score < 4.0 and metadata.get("name"):
            doc_score = 6.0  # Default to moderate if we can't assess
        
        # Sentiment scoring with popularity boost
        star_count = sentiment.get("star_count", 0)
        sentiment_overall = sentiment.get("overall", "neutral")
        
        # Base sentiment score
        if sentiment_overall == "positive":
            sentiment_score = 8.0
        elif sentiment_overall == "negative":
            sentiment_score = 3.0
        else:  # neutral or unknown
            sentiment_score = 6.0  # Neutral is slightly positive
        
        # Boost sentiment score based on popularity (stars indicate trust)
        if star_count > 10000:
            sentiment_score = min(9.5, sentiment_score + 2.0)  # Major boost for 10k+ stars
        elif star_count > 5000:
            sentiment_score = min(9.0, sentiment_score + 1.5)
        elif star_count > 1000:
            sentiment_score = min(8.5, sentiment_score + 1.0)
        elif star_count > 500:
            sentiment_score = min(8.0, sentiment_score + 0.5)
        
        # Ecosystem score with popularity consideration
        ecosystem_score = ecosystem.get("ecosystem_score", 5.0)
        # Boost ecosystem score for highly popular crates (they're foundational)
        if star_count > 10000:
            ecosystem_score = max(ecosystem_score, 8.5)  # At least 8.5 for 10k+ stars
        elif star_count > 5000:
            ecosystem_score = max(ecosystem_score, 7.5)
        elif star_count > 1000:
            ecosystem_score = max(ecosystem_score, 7.0)
        
        # Incorporate ML predictions if available
        ml_score = None
        ml_confidence = 0.0
        if ml_predictions:
            ml_quality = ml_predictions.get("quality_score")
            ml_confidence = ml_predictions.get("confidence", 0.0)
            if ml_quality is not None:
                # Convert ML score (0-1) to 0-10 scale
                ml_score = ml_quality * 10.0
        
        # Weighted average: ecosystem 40%, sentiment 35%, docs 25%
        # If ML predictions available with high confidence, blend them in
        if ml_score is not None and ml_confidence > 0.5:
            # Blend heuristic score (70%) with ML score (30%) when ML confidence is high
            heuristic_score = (
                doc_score * 0.25 +
                sentiment_score * 0.35 +
                ecosystem_score * 0.40
            )
            # Weight ML more heavily if confidence is very high
            ml_weight = min(0.4, ml_confidence * 0.6)  # Up to 40% weight for high confidence
            weighted_score = (
                heuristic_score * (1.0 - ml_weight) +
                ml_score * ml_weight
            )
        else:
            # Standard weighted average without ML
            weighted_score = (
                doc_score * 0.25 +
                sentiment_score * 0.35 +
                ecosystem_score * 0.40
            )
        
        return weighted_score

    def _generate_traceable_suggestion(
        self,
        reasoning_steps: List[str],
        quality_score: float,
        docs: Dict[str, Any],
        sentiment: Dict[str, Any],
        ecosystem: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate traceable suggestion based on computed metrics."""
        if not reasoning_steps:
            return "DEFER: Insufficient reasoning data"

        doc_score = docs.get("quality_score", 5.0)
        sentiment_overall = sentiment.get("overall", "unknown")
        ecosystem_score = ecosystem.get("ecosystem_score", 5.0)
        
        # Get actual adoption metrics
        star_count = sentiment.get("star_count", 0)
        downloads = 0
        if metadata:
            downloads = metadata.get("downloads", 0)
        reverse_deps = ecosystem.get("reverse_dependencies_count", 0)
        
        # Determine if crate has widespread adoption
        has_widespread_adoption = (
            downloads > 1000000 or  # 1M+ downloads
            star_count > 5000 or    # 5k+ stars
            reverse_deps > 100      # 100+ reverse dependencies
        )

        # High quality, positive sentiment, strong ecosystem
        if (
            quality_score >= 8.0
            and sentiment_overall == "positive"
            and ecosystem_score >= 8.0
        ):
            return (
                f"ALLOW: High quality (score {quality_score:.1f}), "
                f"strong community sentiment, and robust ecosystem position "
                f"(score {ecosystem_score:.1f})"
            )

        # Poor documentation or negative sentiment
        if quality_score < 5.0 or sentiment_overall == "negative":
            reason_parts = []
            if quality_score < 5.0:
                reason_parts.append(f"low quality score ({quality_score:.1f})")
            if sentiment_overall == "negative":
                reason_parts.append("negative community sentiment")
            return f"DENY: {' and '.join(reason_parts)}"

        # Middling or contradictory metrics
        if (
            (quality_score >= 6.0 and quality_score < 8.0)
            or sentiment_overall == "neutral"
            or (doc_score >= 7.0 and sentiment_overall != "positive")
        ):
            reasons = []
            if doc_score >= 7.0 and sentiment_overall != "positive":
                reasons.append("good documentation but mixed sentiment")
            # Only flag "limited ecosystem adoption" if ecosystem_score is low AND adoption metrics are also low
            if ecosystem_score < 6.0 and not has_widespread_adoption:
                reasons.append("limited ecosystem adoption")
            elif ecosystem_score < 6.0 and has_widespread_adoption:
                # Ecosystem score is low but adoption is high - this is a scoring issue, not an adoption issue
                reasons.append("ecosystem metrics may need review")
            reason_text = "; ".join(reasons) if reasons else "inconsistent signals"
            return f"FLAG: {reason_text}, manual review required"

        # Default defer
        return "DEFER: Requires additional analysis"

    def _make_trust_decision(
        self,
        reasoning_steps: List[str],
        suggestion: str,
        quality_score: float,
        metadata: Dict[str, Any],
        docs: Dict[str, Any],
        sentiment: Dict[str, Any],
        ecosystem: Dict[str, Any],
        ml_predictions: Optional[Dict[str, Any]] = None,
    ) -> Tuple[TrustVerdict, str]:
        """Make trust decision based on computed metrics with improved thresholds.
        
        Now incorporates ML predictions for security risk and maintenance score.
        """
        sentiment_overall = sentiment.get("overall", "unknown")
        ecosystem_score = ecosystem.get("ecosystem_score", 5.0)
        doc_score = docs.get("quality_score", 5.0)
        
        # Extract ML predictions if available
        ml_security_risk = None
        ml_maintenance_score = None
        ml_confidence = 0.0
        if ml_predictions:
            ml_security_risk = ml_predictions.get("security_risk")
            ml_maintenance_score = ml_predictions.get("maintenance_score")
            ml_confidence = ml_predictions.get("confidence", 0.0)

        # Check for insufficient data
        if (
            doc_score == 0
            or sentiment_overall == "unknown"
            or not docs.get("completeness", 0) > 0
        ):
            return TrustVerdict.DEFER, "Insufficient data for decision (missing docs or community data)"

        # ALLOW: High quality with positive sentiment OR highly trusted crates
        # Also allow crates with moderate quality (>= 6.0) if they're highly trusted
        star_count = sentiment.get("star_count", 0)
        # Use fetched_crate_metadata for downloads (more reliable than basic metadata)
        downloads = 0
        if hasattr(self, '_fetched_crate_metadata') and self._fetched_crate_metadata:
            downloads = self._fetched_crate_metadata.get("downloads", 0)
            if downloads:
                self.logger.debug(f"Using downloads from fetched_crate_metadata: {downloads:,}")
        elif metadata:
            downloads = metadata.get("downloads", 0)
            if downloads:
                self.logger.debug(f"Using downloads from basic metadata: {downloads:,}")
        else:
            self.logger.debug("No downloads found in fetched_crate_metadata or basic metadata")
        is_highly_trusted = star_count >= 10000 or downloads >= 100_000_000
        
        if quality_score >= 7.0 and sentiment_overall == "positive":
            return (
                TrustVerdict.ALLOW,
                f"High quality score ({quality_score:.1f}) with positive community sentiment",
            )
        elif quality_score >= 6.0 and is_highly_trusted:
            return (
                TrustVerdict.ALLOW,
                f"Moderate quality ({quality_score:.1f}) but highly trusted crate "
                f"({star_count:,} stars, {downloads:,} downloads)",
            )

        # DENY: Very low quality, negative sentiment, or high security risk
        # Use ML security risk if available and confidence is high
        security_risk_high = False
        if ml_security_risk and ml_confidence > 0.6:
            security_risk_high = ml_security_risk in ("high", "critical")
            if security_risk_high:
                return (
                    TrustVerdict.DENY,
                    f"High security risk detected by ML model ({ml_security_risk}) "
                    f"with confidence {ml_confidence:.2f}",
                )
        
        # Check maintenance score - low maintenance indicates abandonment risk
        if ml_maintenance_score is not None and ml_confidence > 0.6:
            # Convert 0-1 score to 0-10 scale for comparison
            maintenance_score_10 = ml_maintenance_score * 10.0
            if maintenance_score_10 < 3.0:
                return (
                    TrustVerdict.FLAG,
                    f"Low maintenance score ({maintenance_score_10:.1f}/10) indicates "
                    f"potential abandonment risk",
                )
        
        # Adjusted threshold: only deny if quality is very low (< 4.0) OR negative sentiment
        # This prevents highly trusted crates from being incorrectly denied
        if quality_score < 4.0 or sentiment_overall == "negative":
            if quality_score < 4.0:
                return (
                    TrustVerdict.DENY,
                    f"Very low quality score ({quality_score:.1f})",
                )
            else:
                return TrustVerdict.DENY, "Negative community sentiment"

        # FLAG: Middling quality with neutral sentiment
        if quality_score >= 6.0 and sentiment_overall == "neutral":
            return (
                TrustVerdict.FLAG,
                f"Moderate quality ({quality_score:.1f}) with neutral sentiment, review recommended",
            )

        # FLAG: Good docs but weak ecosystem or mixed signals
        if doc_score >= 7.0 and ecosystem_score < 6.0:
            return (
                TrustVerdict.FLAG,
                f"Good documentation but limited ecosystem adoption (score {ecosystem_score:.1f})",
            )

        # Default DEFER for edge cases
        return TrustVerdict.DEFER, "Insufficient data for decision"

    def _calculate_irl_score(
        self,
        context_sources: List[str],
        reasoning_steps: List[str],
        verdict: TrustVerdict,
        quality_score: Optional[float] = None,
        docs: Optional[Dict[str, Any]] = None,
        sentiment: Optional[Dict[str, Any]] = None,
        ecosystem: Optional[Dict[str, Any]] = None,
    ) -> float:
        """Calculate IRL score based on analysis quality and confidence.
        
        The IRL score represents confidence in the analysis process, incorporating:
        - Data source quality (authority levels)
        - Analysis completeness (reasoning steps)
        - Analysis quality (quality scores, data completeness)
        - Decision confidence (verdict type)
        """
        base_score = 5.0

        # Authority bonus: quality of data sources
        authority_bonus = (
            sum(
                self.canon_registry.get_authority_level(source)
                for source in context_sources
            )
            / 10.0
        )
        base_score += min(authority_bonus, 2.0)

        # Reasoning bonus: completeness of analysis
        reasoning_bonus = min(len(reasoning_steps) * 0.2, 2.0)
        base_score += reasoning_bonus

        # Quality bonus: incorporate actual analysis quality
        quality_bonus = 0.0
        if quality_score is not None:
            # Normalize quality_score (0-10 scale) to bonus (0-1.5)
            quality_bonus = (quality_score / 10.0) * 1.5
        
        # Data completeness bonus: reward comprehensive analysis
        completeness_bonus = 0.0
        if docs and sentiment and ecosystem:
            # Check if we have meaningful data
            doc_completeness = docs.get("completeness", 0.0)
            sentiment_data = sentiment.get("comment_sample_size", 0) > 0 or sentiment.get("star_count", 0) > 0
            ecosystem_data = ecosystem.get("ecosystem_score", 0) > 0
            
            # Reward having complete data
            if doc_completeness > 0.3 and sentiment_data and ecosystem_data:
                completeness_bonus = 0.5
            elif doc_completeness > 0.1 and (sentiment_data or ecosystem_data):
                completeness_bonus = 0.25
        
        base_score += quality_bonus + completeness_bonus

        # Verdict bonus: decision confidence
        if verdict == TrustVerdict.ALLOW:
            base_score += 1.0
        elif verdict == TrustVerdict.DENY:
            base_score += 0.5
        elif verdict == TrustVerdict.FLAG:
            base_score += 0.75

        return min(base_score, 10.0)
