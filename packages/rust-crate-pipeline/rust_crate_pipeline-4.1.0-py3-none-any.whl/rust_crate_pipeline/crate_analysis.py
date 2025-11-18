import asyncio
import json
import logging
import os
import platform
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import toml

from .crate_environment import detect_platform_info, prepare_crate_environment, prepare_crate_for_analysis
from .crate_compilation import (
    assess_crate_complexity,
    get_progressive_command_strategy,
)
from .utils.validation import sanitize_crate_name_for_command


def _get_cargo_bin_path() -> Path:
    """Get the cargo bin directory path where subcommands are installed."""
    # Check CARGO_HOME environment variable first
    cargo_home = os.environ.get("CARGO_HOME")
    if cargo_home:
        return Path(cargo_home) / "bin"
    
    # Default location: ~/.cargo/bin (Unix) or %USERPROFILE%\.cargo\bin (Windows)
    home_dir = Path.home()
    if platform.system() == "Windows":
        return home_dir / ".cargo" / "bin"
    else:
        return home_dir / ".cargo" / "bin"


def _get_env_with_cargo_path() -> Dict[str, str]:
    """Get environment variables with cargo bin directory added to PATH."""
    env = os.environ.copy()
    cargo_bin = _get_cargo_bin_path()
    cargo_bin_str = str(cargo_bin)
    
    # Get current PATH
    current_path = env.get("PATH", "")
    
    # Add cargo bin to PATH if it's not already there
    if cargo_bin_str not in current_path:
        if platform.system() == "Windows":
            env["PATH"] = f"{cargo_bin_str};{current_path}"
        else:
            env["PATH"] = f"{cargo_bin_str}:{current_path}"
    
    return env


class CrateAnalyzer:
    def __init__(self, crate_source_path: str):
        self.crate_source_path = crate_source_path
        self.logger = logging.getLogger(__name__)
        self.platform_info = detect_platform_info()

    # Platform detection moved to crate_environment.py

    def run_cargo_cmd(self, cmd, timeout=600) -> Dict[str, Any]:
        """Run cargo command with structured error handling."""
        from .exceptions import PipelineError
        
        # Ensure cargo bin directory is in PATH
        env = _get_env_with_cargo_path()
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.crate_source_path,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,  # Use environment with cargo bin in PATH
            )
            return {
                "cmd": " ".join(cmd),
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
            }
        except subprocess.TimeoutExpired as e:
            self.logger.warning(f"Cargo command timed out after {timeout}s: {' '.join(cmd)}")
            return {
                "cmd": " ".join(cmd),
                "error": f"Command timed out after {timeout}s",
                "error_type": "timeout",
                "success": False,
            }
        except subprocess.SubprocessError as e:
            self.logger.warning(f"Cargo subprocess error: {e}")
            return {
                "cmd": " ".join(cmd),
                "error": str(e),
                "error_type": "subprocess_error",
                "success": False,
            }
        except OSError as e:
            self.logger.error(f"OS error running cargo command: {e}")
            return {
                "cmd": " ".join(cmd),
                "error": f"OS error: {str(e)}",
                "error_type": "os_error",
                "success": False,
            }
        except Exception as e:
            self.logger.error(f"Unexpected error running cargo command: {e}")
            return {
                "cmd": " ".join(cmd),
                "error": f"Unexpected error: {str(e)}",
                "error_type": "unknown_error",
                "success": False,
            }

    async def run_cargo_cmd_async(self, cmd, timeout=600) -> Dict[str, Any]:
        """Run cargo command in a background thread to avoid blocking the loop."""

        return await asyncio.to_thread(self.run_cargo_cmd, cmd, timeout)

    def run_cargo_cmd_with_fallback(
        self,
        primary_cmd: List[str],
        fallback_cmd: Optional[List[str]] = None,
        timeout=600,
    ) -> Dict[str, Any]:
        """Run cargo command with fallback if primary fails."""
        result = self.run_cargo_cmd(primary_cmd, timeout)

        # If primary command failed and we have a fallback, try it
        if result.get("returncode", 0) != 0 and fallback_cmd:
            self.logger.warning(
                "Primary command failed (exit %s): %s",
                result.get("returncode", "unknown"),
                " ".join(primary_cmd),
            )
            self.logger.info("Trying fallback command: %s", " ".join(fallback_cmd))
            fallback_result = self.run_cargo_cmd(fallback_cmd, timeout)
            fallback_result["used_fallback"] = True
            fallback_result["primary_failure_reason"] = result.get(
                "stderr", "Unknown error"
            )
            return fallback_result
        elif result.get("returncode", 0) != 0:
            # No fallback available, but log the failure details
            self.logger.error(
                "Command failed with no fallback available: %s", " ".join(primary_cmd)
            )
            self.logger.error(
                "Error output: %s", result.get("stderr", "No error output")
            )

        return result

    async def run_cargo_cmd_with_fallback_async(
        self,
        primary_cmd: List[str],
        fallback_cmd: Optional[List[str]] = None,
        timeout=600,
    ) -> Dict[str, Any]:
        """Async wrapper for run_cargo_cmd_with_fallback using a worker thread."""

        return await asyncio.to_thread(
            self.run_cargo_cmd_with_fallback, primary_cmd, fallback_cmd, timeout
        )

    def _calculate_quality_score(
        self, warnings: List[Dict], errors: List[Dict], suggestions: List[Dict]
    ) -> float:
        """Calculate a quality score based on analysis results."""
        base_score = 1.0

        # Deduct points for errors (most severe)
        error_penalty = len(errors) * 0.1
        base_score -= min(error_penalty, 0.5)  # Cap at 50% penalty for errors

        # Deduct points for warnings (moderate)
        warning_penalty = len(warnings) * 0.02
        base_score -= min(warning_penalty, 0.3)  # Cap at 30% penalty for warnings

        # Small bonus for suggestions (shows good practices)
        suggestion_bonus = min(len(suggestions) * 0.005, 0.1)  # Cap at 10% bonus
        base_score += suggestion_bonus

        return max(0.0, min(1.0, base_score))  # Ensure score is between 0 and 1

    def _is_critical_issue(self, message: Dict) -> bool:
        """Determine if a clippy/compiler message represents a critical issue."""
        critical_patterns = [
            r"unsafe",
            r"unchecked",
            r"panic",
            r"unreachable",
            r"dead_code",
            r"unused_imports",
            r"missing_docs",
            r"clippy::all",
            r"clippy::pedantic",
        ]

        message_text = message.get("message", {}).get("message", "").lower()
        for pattern in critical_patterns:
            if re.search(pattern, message_text):
                return True
        return False

    def process_clippy_results(self, clippy_output: List[Dict]) -> Dict[str, Any]:
        """Process clippy results into actionable insights."""
        warnings = []
        errors = []
        suggestions = []
        critical_issues = []

        for message in clippy_output:
            msg_data = message.get("message", {})
            level = msg_data.get("level", "unknown")

            if level == "warning":
                warnings.append(message)
                if self._is_critical_issue(message):
                    critical_issues.append(message)
            elif level == "error":
                errors.append(message)
                critical_issues.append(message)
            elif level == "help":
                suggestions.append(message)

        quality_score = self._calculate_quality_score(warnings, errors, suggestions)

        return {
            "warning_count": len(warnings),
            "error_count": len(errors),
            "suggestion_count": len(suggestions),
            "critical_issue_count": len(critical_issues),
            "quality_score": quality_score,
            "critical_issues": critical_issues[:10],  # Limit to first 10 for storage
            "warnings": warnings[:20],  # Limit to first 20
            "errors": errors[:10],  # Limit to first 10
            "suggestions": suggestions[:10],  # Limit to first 10
        }

    def process_audit_results(self, audit_output: str) -> Dict[str, Any]:
        """Process cargo audit results."""
        try:
            audit_data = json.loads(audit_output)
            vulnerabilities = audit_data.get("vulnerabilities", [])
            advisories = audit_data.get("advisories", {})

            return {
                "vulnerability_count": len(vulnerabilities),
                "advisory_count": len(advisories),
                "vulnerabilities": vulnerabilities,
                "advisories": list(advisories.values())[:10],  # Limit to first 10
                "risk_level": self._calculate_security_risk_level(vulnerabilities),
                "has_critical_vulnerabilities": any(
                    isinstance(v, dict) and v.get("cvss", {}).get("score", 0) >= 9.0
                    for v in vulnerabilities
                ),
            }
        except (json.JSONDecodeError, KeyError):
            return {
                "vulnerability_count": 0,
                "advisory_count": 0,
                "risk_level": "unknown",
                "error": "Failed to parse audit results",
            }

    def process_geiger_results(self, geiger_output: str) -> Dict[str, Any]:
        """Process cargo-geiger results for unsafe code analysis."""
        try:
            geiger_data = json.loads(geiger_output)
            packages = geiger_data.get("packages", [])

            total_unsafe_functions = 0
            total_unsafe_expressions = 0
            total_unsafe_impls = 0
            total_unsafe_methods = 0
            packages_with_unsafe = 0
            packages_forbidding_unsafe = 0

            for package in packages:
                unsafety = package.get("unsafety", {})
                used = unsafety.get("used", {})

                # Count unsafe usage
                unsafe_functions = used.get("functions", {}).get("unsafe_", 0)
                unsafe_expressions = used.get("exprs", {}).get("unsafe_", 0)
                unsafe_impls = used.get("item_impls", {}).get("unsafe_", 0)
                unsafe_methods = used.get("methods", {}).get("unsafe_", 0)

                total_unsafe_functions += unsafe_functions
                total_unsafe_expressions += unsafe_expressions
                total_unsafe_impls += unsafe_impls
                total_unsafe_methods += unsafe_methods

                if any(
                    [unsafe_functions, unsafe_expressions, unsafe_impls, unsafe_methods]
                ):
                    packages_with_unsafe += 1

                if unsafety.get("forbids_unsafe", False):
                    packages_forbidding_unsafe += 1

            total_unsafe_items = (
                total_unsafe_functions
                + total_unsafe_expressions
                + total_unsafe_impls
                + total_unsafe_methods
            )

            # Calculate safety score (0-1, higher is safer)
            if total_unsafe_items == 0:
                safety_score = 1.0
            else:
                # Penalize based on unsafe usage, but don't go below 0.3
                safety_score = max(0.3, 1.0 - (total_unsafe_items * 0.01))

            return {
                "total_unsafe_items": total_unsafe_items,
                "unsafe_functions": total_unsafe_functions,
                "unsafe_expressions": total_unsafe_expressions,
                "unsafe_impls": total_unsafe_impls,
                "unsafe_methods": total_unsafe_methods,
                "packages_with_unsafe": packages_with_unsafe,
                "packages_forbidding_unsafe": packages_forbidding_unsafe,
                "total_packages": len(packages),
                "safety_score": safety_score,
                "has_unsafe_code": total_unsafe_items > 0,
                "risk_level": (
                    "high"
                    if total_unsafe_items > 50
                    else "medium"
                    if total_unsafe_items > 10
                    else "low"
                ),
            }
        except (json.JSONDecodeError, KeyError):
            return {
                "total_unsafe_items": 0,
                "safety_score": 1.0,
                "has_unsafe_code": False,
                "risk_level": "unknown",
                "error": "Failed to parse geiger results",
            }

    def _calculate_security_risk_level(self, vulnerabilities: List[Dict]) -> str:
        """Calculate security risk level based on vulnerabilities."""
        if not vulnerabilities:
            return "low"

        # Handle case where vulnerabilities might be strings or other types
        cvss_scores = []
        for v in vulnerabilities:
            if isinstance(v, dict):
                cvss_score = v.get("cvss", {}).get("score", 0)
                if isinstance(cvss_score, (int, float)):
                    cvss_scores.append(cvss_score)

        if not cvss_scores:
            return "low"

        max_cvss = max(cvss_scores)

        if max_cvss >= 9.0:
            return "critical"
        elif max_cvss >= 7.0:
            return "high"
        elif max_cvss >= 4.0:
            return "medium"
        else:
            return "low"

    def _prepare_crate_for_analysis(self) -> bool:
        """Prepare the downloaded crate for analysis by ensuring it has a proper project structure."""
        return prepare_crate_for_analysis(self.crate_source_path)

    def _prepare_crate_environment(self) -> Dict[str, Any]:
        """Prepare the crate environment and return detailed environment info."""
        return prepare_crate_environment(self.crate_source_path)

    def _analyze_crate_features(self, env_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and filter crate features based on platform compatibility."""
        cargo_toml_path = os.path.join(self.crate_source_path, "Cargo.toml")

        feature_analysis = {
            "all_features": [],
            "platform_safe_features": [],
            "excluded_features": [],
            "feature_groups": {
                "core": [],
                "platform_specific": [],
                "optional_deps": [],
                "experimental": [],
            },
            "platform_compatibility": "unknown",
        }

        try:
            with open(cargo_toml_path, "r") as f:
                cargo_config = toml.load(f)

            # Extract features from Cargo.toml
            features = cargo_config.get("features", {})
            dependencies = cargo_config.get("dependencies", {})

            feature_analysis["all_features"] = list(features.keys())

            # Analyze each feature for platform compatibility
            for feature_name in features.keys():
                feature_lower = feature_name.lower()
                feature_value = features[feature_name]

                is_safe = True
                exclusion_reason = None

                # Check against platform exclusion patterns
                for pattern in self.platform_info["excluded_patterns"]:
                    if pattern in feature_lower:
                        is_safe = False
                        exclusion_reason = f"matches excluded pattern: {pattern}"
                        break

                # Check if feature enables platform-specific dependencies
                if is_safe and isinstance(feature_value, list):
                    for dep in feature_value:
                        if isinstance(dep, str):
                            dep_lower = dep.lower()
                            for pattern in self.platform_info["excluded_patterns"]:
                                if pattern in dep_lower:
                                    is_safe = False
                                    exclusion_reason = (
                                        f"enables excluded dependency: {dep}"
                                    )
                                    break
                            if not is_safe:
                                break

                # Categorize the feature
                if is_safe:
                    feature_analysis["platform_safe_features"].append(feature_name)

                    # Categorize by type
                    if feature_lower in ["default", "std", "alloc", "core"]:
                        feature_analysis["feature_groups"]["core"].append(feature_name)
                    elif any(
                        pattern in feature_lower
                        for pattern in ["test", "dev", "bench", "debug"]
                    ):
                        feature_analysis["feature_groups"]["experimental"].append(
                            feature_name
                        )
                    elif feature_name in dependencies:
                        feature_analysis["feature_groups"]["optional_deps"].append(
                            feature_name
                        )
                    else:
                        feature_analysis["feature_groups"]["platform_specific"].append(
                            feature_name
                        )
                else:
                    feature_analysis["excluded_features"].append(
                        {"name": feature_name, "reason": exclusion_reason}
                    )
                    self.logger.debug(
                        f"Excluding feature '{feature_name}': {exclusion_reason}"
                    )

            # Determine overall platform compatibility
            total_features = len(feature_analysis["all_features"])
            safe_features = len(feature_analysis["platform_safe_features"])

            if total_features == 0:
                feature_analysis["platform_compatibility"] = "no_features"
            elif safe_features == total_features:
                feature_analysis["platform_compatibility"] = "fully_compatible"
            elif safe_features > total_features * 0.8:
                feature_analysis["platform_compatibility"] = "mostly_compatible"
            elif safe_features > total_features * 0.5:
                feature_analysis["platform_compatibility"] = "partially_compatible"
            else:
                feature_analysis["platform_compatibility"] = "limited_compatibility"

            self.logger.info(
                f"Feature analysis: {safe_features}/{total_features} platform-safe features ({feature_analysis['platform_compatibility']})"
            )

        except Exception as e:
            self.logger.warning("Failed to analyze crate features: %s", e)
            feature_analysis["platform_compatibility"] = "analysis_failed"

        return feature_analysis

    def _get_platform_safe_feature_combinations(
        self, feature_analysis: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate platform-safe feature combinations based on analysis."""
        safe_features = feature_analysis["platform_safe_features"]
        feature_groups = feature_analysis["feature_groups"]

        combinations = {}

        if not safe_features:
            # No safe features available - use minimal approach
            combinations = {
                "minimal": "",  # No features
                "default_only": "default",  # Try default if it exists
            }
            self.logger.warning(
                "No platform-safe features detected - using minimal feature sets"
            )
            return combinations

        # Core combinations with platform-safe features
        core_features = feature_groups["core"]
        optional_deps = feature_groups["optional_deps"]

        # Basic: Core features only
        if core_features:
            combinations["basic"] = ",".join(core_features[:3])
        elif "default" in safe_features:
            combinations["basic"] = "default"
        else:
            combinations["basic"] = safe_features[0] if safe_features else ""

        # Medium: Core + some optional dependencies
        medium_features = core_features[:2] + optional_deps[:3]
        medium_features = list(dict.fromkeys(medium_features))  # Remove duplicates
        if medium_features:
            combinations["medium"] = ",".join(medium_features[:5])

        # Comprehensive: More features but still platform-safe
        comprehensive_features = safe_features[:8]  # Limit to prevent overwhelming
        if comprehensive_features:
            combinations["comprehensive"] = ",".join(comprehensive_features)

        # Individual feature testing for key features
        priority_features = [
            f
            for f in safe_features
            if any(
                p in f.lower()
                for p in ["default", "std", "serde", "async", "tokio", "http"]
            )
        ]
        for feature in priority_features[:3]:  # Test top 3 individually
            combinations[f"single_{feature}"] = feature

        # IMPROVED: Smart all-safe combination that avoids conflicts
        # Filter out potentially conflicting features
        conflicting_patterns = [
            "nightly",  # nightly features can cause issues
            "unstable", # unstable features
            "experimental", # experimental features
        ]

        # Detect conflicting feature pairs
        conflict_pairs = []
        for feature in safe_features:
            if feature.lower().startswith("no-"):
                base_feature = feature[3:]  # Remove "no-" prefix
                # Look for the positive version of this feature
                for other_feature in safe_features:
                    if other_feature != feature and base_feature in other_feature.lower():
                        conflict_pairs.append((feature, other_feature))

        # Create filtered feature list avoiding conflicts
        filtered_safe_features = []
        excluded_due_to_conflict = set()

        for feature in safe_features:
            # Skip if already excluded due to conflict
            if feature in excluded_due_to_conflict:
                continue

            # Check for conflicting patterns
            is_conflicting = any(pattern in feature.lower() for pattern in conflicting_patterns)

            # Check for conflict pairs
            for conflict_feature, positive_feature in conflict_pairs:
                if feature == conflict_feature:
                    # Prefer the positive feature over the negative one
                    excluded_due_to_conflict.add(conflict_feature)
                    is_conflicting = True
                    self.logger.debug(
                        "Excluding conflicting feature '%s' in favor of '%s'",
                        conflict_feature,
                        positive_feature,
                    )
                    break

            if not is_conflicting:
                filtered_safe_features.append(feature)

        # Create a conservative all-safe combination
        if len(filtered_safe_features) > 1:
            # Prioritize core features, limit to 4-5 features max to avoid conflicts
            priority_order = []

            # Add core features first
            for feature in ["default", "std", "alloc", "core"]:
                if feature in filtered_safe_features:
                    priority_order.append(feature)

            # Add other safe features, but limit total
            for feature in filtered_safe_features:
                if feature not in priority_order and len(priority_order) < 5:
                    priority_order.append(feature)

            combinations["all_safe"] = ",".join(priority_order)
            self.logger.debug(
                "Smart all_safe combination: %s", combinations["all_safe"]
            )
        elif filtered_safe_features:
            combinations["all_safe"] = filtered_safe_features[0]
        else:
            combinations["all_safe"] = "default" if "default" in safe_features else safe_features[0] if safe_features else ""

        self.logger.info(
            "Generated %d platform-safe feature combinations "
            "(avoided %d conflicting features)",
            len(combinations),
            len(excluded_due_to_conflict),
        )
        return combinations

    def _get_progressive_command_strategy(
        self, command_type: str, env_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get a progressive list of commands to try for maximum data collection with platform-aware feature selection."""

        # Analyze crate features for platform compatibility
        feature_analysis = self._analyze_crate_features(env_info)

        # Get platform-safe feature combinations
        feature_combinations = self._get_platform_safe_feature_combinations(
            feature_analysis
        )

        # Add feature analysis to environment info for debugging
        env_info["feature_analysis"] = feature_analysis

        # Use compilation strategies module
        return get_progressive_command_strategy(
            self.platform_info,
            command_type,
            env_info,
            feature_analysis,
            feature_combinations,
        )

    # All strategy methods moved to crate_compilation.py
    # This file now only contains the main CrateAnalyzer class and its core methods

    def analyze(self) -> Dict[str, Any]:
        results = {}

        # Check what analysis is feasible before attempting commands
        env_info = self._prepare_crate_environment()
        results["environment"] = env_info

        if not env_info.get("has_cargo_toml", False):
            self.logger.warning(
                f"No analysis is feasible for crate at {self.crate_source_path}: No Cargo.toml found"
            )
            results["error"] = "No analysis feasible - no Cargo.toml found"
            return results

        # Assess crate complexity for adaptive timeout and retry strategies
        feature_analysis = self._analyze_crate_features(env_info)
        crate_complexity = assess_crate_complexity(env_info, feature_analysis)

        # Set adaptive timeouts based on complexity
        complexity_timeouts = {
            "simple": 180,  # 3 minutes for simple crates
            "moderate": 300,  # 5 minutes for moderate crates
            "system_dependent": 240,  # 4 minutes for system crates
            "complex": 120,  # 2 minutes for complex crates (conservative)
        }
        timeout = complexity_timeouts.get(crate_complexity, 300)

        self.logger.info(
            "Analysis starting for: %s (%s, edition %s) - Complexity: %s",
            env_info["crate_name"],
            env_info["crate_type"],
            env_info["edition"],
            crate_complexity,
        )

        # Define all analysis types we want to perform
        analysis_types = [
            "build",
            "test",
            "clippy",
            "fmt",
            "audit",
            "geiger",
            "outdated",
            "coverage",
            "tree",
            "doc",
            "bench",
        ]

        # Execute comprehensive analysis with resilience strategies
        successful_analyses = 0
        critical_failures = []

        for analysis_type in analysis_types:
            strategies = self._get_progressive_command_strategy(analysis_type, env_info)
            if not strategies:
                continue

            self.logger.info(
                "Starting %s analysis with %d strategies (timeout: %ds)",
                analysis_type,
                len(strategies),
                timeout,
            )

            analysis_successful = False
            for i, strategy in enumerate(strategies, 1):
                self.logger.info(
                    "  Attempt %d/%d: %s", i, len(strategies), strategy["desc"]
                )

                try:
                    result = self.run_cargo_cmd(strategy["cmd"], timeout=timeout)

                    # Store result and strategy info
                    results[analysis_type] = result
                    results[analysis_type]["strategy_used"] = strategy["desc"]
                    results[analysis_type]["attempt_number"] = i
                    results[analysis_type]["crate_complexity"] = crate_complexity

                    if result.get("returncode", 1) == 0:
                        self.logger.info(
                            f"  [OK] {analysis_type} succeeded: {strategy['desc']}"
                        )
                        analysis_successful = True
                        successful_analyses += 1
                        break
                    else:
                        self.logger.warning(
                            f"  [FAIL] {analysis_type} failed: {strategy['desc']} (exit {result.get('returncode')})"
                        )

                        # For critical analysis types, record partial data even on failure
                        if analysis_type in ["build", "fmt"] and i == len(strategies):
                            critical_failures.append(
                                {
                                    "analysis_type": analysis_type,
                                    "final_error": result.get(
                                        "stderr", "Unknown error"
                                    ),
                                    "strategies_attempted": len(strategies),
                                }
                            )

                except Exception as e:
                    self.logger.error(
                        "  %s strategy %d crashed: %s", analysis_type, i, e
                    )
                    # Continue to next strategy instead of failing entirely
                    continue

            if not analysis_successful:
                self.logger.error("  All %s strategies exhausted", analysis_type)
                # Store failure info for analysis
                results[analysis_type] = {
                    "returncode": -1,
                    "error": "All strategies failed",
                    "strategies_attempted": len(strategies),
                    "crate_complexity": crate_complexity,
                }

        # Additional metadata extraction (always attempt)
        try:
            self._extract_additional_metadata(results, env_info)
        except Exception as e:
            self.logger.warning(f"Metadata extraction failed: {e}")

        # Process results for comprehensive insights (defensive)
        try:
            results["insights"] = self._generate_comprehensive_insights(results)
        except Exception as e:
            self.logger.warning(f"Insight generation failed: {e}")
            results["insights"] = {"error": f"Insight generation failed: {e}"}

        # Add resilience metrics
        results["analysis_metrics"] = {
            "successful_analyses": successful_analyses,
            "total_attempted": len(analysis_types),
            "success_rate": successful_analyses / len(analysis_types),
            "crate_complexity": crate_complexity,
            "critical_failures": critical_failures,
            "timeout_used": timeout,
        }

        self.logger.info(
            f"🎯 Analysis completed for {env_info['crate_name']} - Success rate: {successful_analyses}/{len(analysis_types)} ({(successful_analyses/len(analysis_types)*100):.1f}%)"
        )
        return results

    async def analyze_async(self) -> Dict[str, Any]:
        """Run analyze in a worker thread for async contexts."""

        return await asyncio.to_thread(self.analyze)

    def _generate_comprehensive_insights(
        self, results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive insights from all analysis results with failure tracking."""
        insights = {
            "overall_quality_score": 0.0,
            "security_risk_level": "unknown",
            "maintenance_health": "unknown",
            "code_quality": "unknown",
            "performance_indicators": {},
            "comprehensive_recommendations": [],
            "analysis_coverage": {},
            "tool_success_rate": 0.0,
            # NEW: Comprehensive failure tracking
            "data_quality_flags": {
                "missing_analyses": [],
                "partial_failures": [],
                "tool_unavailable": [],
                "platform_incompatible": [],
                "timeout_failures": [],
                "requires_manual_review": False,
                "data_completeness_score": 0.0,
            },
            "failure_analysis": {
                "critical_missing": [],
                "acceptable_missing": [],
                "compensated_data": [],
                "intervention_needed": [],
            },
        }

        # Calculate analysis coverage with detailed failure categorization
        analysis_types = [
            "build",
            "test",
            "clippy",
            "fmt",
            "audit",
            "geiger",
            "outdated",
            "coverage",
            "tree",
            "doc",
        ]
        successful_analyses = 0
        critical_failures = []
        acceptable_failures = []

        for analysis in analysis_types:
            result = results.get(analysis, {})
            success = result.get("returncode") == 0

            if success:
                successful_analyses += 1
            else:
                # Categorize the failure type and impact
                failure_info = {
                    "analysis_type": analysis,
                    "error_message": result.get(
                        "stderr", result.get("error", "Unknown failure")
                    ),
                    "strategies_attempted": result.get("strategies_attempted", 0),
                    "crate_complexity": result.get("crate_complexity", "unknown"),
                    "impact_level": self._assess_failure_impact(analysis, result),
                }

                if failure_info["impact_level"] == "critical":
                    critical_failures.append(failure_info)
                    insights["data_quality_flags"]["missing_analyses"].append(analysis)

                    # Critical failures that need manual intervention
                    if analysis in ["build", "fmt"]:
                        insights["failure_analysis"]["critical_missing"].append(
                            {
                                "type": analysis,
                                "reason": "Core functionality failed",
                                "intervention": f"Manual {analysis} analysis required",
                            }
                        )
                        insights["data_quality_flags"]["requires_manual_review"] = True
                else:
                    acceptable_failures.append(failure_info)
                    insights["data_quality_flags"]["partial_failures"].append(analysis)

                    # Check if we can compensate for this failure
                    compensation = self._get_failure_compensation(
                        analysis, result, results
                    )
                    if compensation:
                        insights["failure_analysis"]["compensated_data"].append(
                            compensation
                        )
                    else:
                        insights["failure_analysis"]["acceptable_missing"].append(
                            {
                                "type": analysis,
                                "reason": failure_info["error_message"][
                                    :200
                                ],  # Truncate long errors
                                "impact": "Low - alternative data sources available",
                            }
                        )

        insights["analysis_coverage"] = {
            "successful_analyses": successful_analyses,
            "total_possible": len(analysis_types),
            "coverage_percentage": (successful_analyses / len(analysis_types)) * 100,
            "critical_failures": len(critical_failures),
            "acceptable_failures": len(acceptable_failures),
        }
        insights["tool_success_rate"] = successful_analyses / len(analysis_types)

        # Calculate data completeness score
        critical_weight = 0.7  # Critical analyses weigh more
        acceptable_weight = 0.3
        critical_analyses = ["build", "fmt", "clippy"]

        critical_success = sum(
            1
            for analysis in critical_analyses
            if results.get(analysis, {}).get("returncode") == 0
        )
        critical_score = critical_success / len(critical_analyses)

        acceptable_success = sum(
            1
            for analysis in analysis_types
            if analysis not in critical_analyses
            and results.get(analysis, {}).get("returncode") == 0
        )
        acceptable_total = len(analysis_types) - len(critical_analyses)
        acceptable_score = (
            acceptable_success / acceptable_total if acceptable_total > 0 else 1.0
        )

        insights["data_quality_flags"]["data_completeness_score"] = (
            critical_score * critical_weight + acceptable_score * acceptable_weight
        )

        # Process clippy results with enhanced analysis
        if results.get("clippy", {}).get("stdout"):
            try:
                clippy_data = json.loads(results["clippy"]["stdout"])
                clippy_insights = self.process_clippy_results(clippy_data)
                insights["clippy_insights"] = clippy_insights
                insights["overall_quality_score"] = clippy_insights["quality_score"]
            except (json.JSONDecodeError, KeyError):
                # Try parsing as line-delimited JSON
                try:
                    clippy_lines = results["clippy"]["stdout"].strip().split("\n")
                    clippy_data = [
                        json.loads(line) for line in clippy_lines if line.strip()
                    ]
                    clippy_insights = self.process_clippy_results(clippy_data)
                    insights["clippy_insights"] = clippy_insights
                    insights["overall_quality_score"] = clippy_insights["quality_score"]
                except Exception as e:
                    insights["data_quality_flags"]["partial_failures"].append(
                        "clippy_parsing"
                    )
                    insights["failure_analysis"]["intervention_needed"].append(
                        {
                            "type": "clippy_parsing",
                            "reason": f"Failed to parse clippy output: {e}",
                            "raw_data_available": bool(
                                results.get("clippy", {}).get("stdout")
                            ),
                        }
                    )
        else:
            # No clippy data - mark for potential manual review
            if results.get("clippy", {}).get("returncode") != 0:
                insights["failure_analysis"]["critical_missing"].append(
                    {
                        "type": "clippy",
                        "reason": "Code quality analysis unavailable",
                        "intervention": "Manual code review recommended",
                    }
                )

        # Process security audit results with failure handling
        if results.get("audit", {}).get("stdout"):
            audit_insights = self.process_audit_results(results["audit"]["stdout"])
            insights["audit_insights"] = audit_insights
            insights["security_risk_level"] = audit_insights["risk_level"]
        else:
            # Missing security audit - critical for security assessment
            insights["security_risk_level"] = "unknown_requires_manual_audit"
            insights["failure_analysis"]["critical_missing"].append(
                {
                    "type": "security_audit",
                    "reason": "Security vulnerability scan failed",
                    "intervention": "Manual security audit required",
                    "priority": "high",
                }
            )
            insights["data_quality_flags"]["requires_manual_review"] = True

        # Process unsafe code analysis
        if results.get("geiger", {}).get("stdout"):
            geiger_insights = self.process_geiger_results(results["geiger"]["stdout"])
            insights["geiger_insights"] = geiger_insights

            # Adjust security risk level based on unsafe code
            if geiger_insights.get("has_unsafe_code", False):
                current_risk = insights.get("security_risk_level", "low")
                if current_risk == "low" and geiger_insights.get("risk_level") in [
                    "medium",
                    "high",
                ]:
                    insights["security_risk_level"] = geiger_insights["risk_level"]
        else:
            # Missing unsafe code analysis
            insights["failure_analysis"]["acceptable_missing"].append(
                {
                    "type": "unsafe_code_analysis",
                    "reason": "Geiger analysis failed",
                    "impact": "Medium - manual unsafe code review recommended",
                }
            )

        # Analyze dependency health
        if results.get("outdated", {}).get("stdout"):
            insights["dependency_health"] = self._analyze_dependency_health(
                results["outdated"]["stdout"]
            )
        else:
            insights["failure_analysis"]["compensated_data"].append(
                {
                    "type": "dependency_analysis",
                    "compensation": "Using Cargo.toml dependency info as fallback",
                    "completeness": "partial",
                }
            )

        # Performance indicators from various sources
        source_stats = results.get("source_stats", {})
        insights["performance_indicators"] = {
            "codebase_size": source_stats.get("rust_lines", 0),
            "complexity_estimate": min(
                10, max(1, int(source_stats.get("rust_files", 0) / 10))
            ),
            "test_coverage_estimate": "high"
            if source_stats.get("has_tests")
            else "unknown",
            "documentation_quality": "good"
            if source_stats.get("total_lines", 0)
            > source_stats.get("rust_lines", 0) * 1.2
            else "basic",
        }

        # Determine overall maintenance health with data quality considerations
        build_success = results.get("build", {}).get("returncode", 1) == 0
        test_success = results.get("test", {}).get("returncode", 1) == 0
        fmt_success = results.get("fmt", {}).get("returncode", 1) == 0

        if build_success and test_success and fmt_success:
            insights["maintenance_health"] = "excellent"
        elif build_success and test_success:
            insights["maintenance_health"] = "good"
        elif build_success:
            insights["maintenance_health"] = "fair"
        else:
            insights["maintenance_health"] = "poor_requires_manual_review"
            insights["data_quality_flags"]["requires_manual_review"] = True

        # Enhanced recommendations with failure-aware suggestions
        recommendations = []

        if insights.get("clippy_insights", {}).get("critical_issue_count", 0) > 0:
            recommendations.append(
                f"Address {insights['clippy_insights']['critical_issue_count']} critical clippy warnings"
            )

        if insights.get("audit_insights", {}).get("vulnerability_count", 0) > 0:
            recommendations.append(
                f"Fix {insights['audit_insights']['vulnerability_count']} security vulnerabilities"
            )

        if insights.get("geiger_insights", {}).get("has_unsafe_code", False):
            unsafe_count = insights["geiger_insights"]["total_unsafe_items"]
            recommendations.append(f"Review {unsafe_count} unsafe code items")

        if not build_success:
            recommendations.append(
                "CRITICAL: Fix build errors - manual intervention required"
            )

        if not source_stats.get("has_tests"):
            recommendations.append("Add tests to improve code reliability")

        if insights["tool_success_rate"] < 0.5:
            recommendations.append(
                "MANUAL REVIEW: Low tool success rate - crate may need manual analysis"
            )

        # Add failure-specific recommendations
        if insights["data_quality_flags"]["requires_manual_review"]:
            recommendations.append(
                "MANUAL INTERVENTION REQUIRED: Critical analysis failures detected"
            )

        if len(insights["failure_analysis"]["critical_missing"]) > 0:
            recommendations.append(
                f"PRIORITY: {len(insights['failure_analysis']['critical_missing'])} critical analyses missing"
            )

        insights["comprehensive_recommendations"] = recommendations

        return insights

    def _assess_failure_impact(self, analysis_type: str, result: Dict[str, Any]) -> str:
        """Assess the impact level of an analysis failure."""
        critical_analyses = ["build", "fmt"]  # Core functionality
        high_impact_analyses = ["clippy", "audit"]  # Quality/security
        medium_impact_analyses = ["test", "coverage", "geiger"]  # Development insights
        # Note: Low-impact analyses (outdated, tree, doc, bench) fall through to "low" impact

        if analysis_type in critical_analyses:
            return "critical"
        elif analysis_type in high_impact_analyses:
            return "high"
        elif analysis_type in medium_impact_analyses:
            return "medium"
        else:
            return "low"

    def _get_failure_compensation(
        self,
        analysis_type: str,
        failed_result: Dict[str, Any],
        all_results: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Determine if we can compensate for a failed analysis with alternative data."""
        compensations = {
            "test": {
                "alternative": "source_stats",
                "check": lambda r: r.get("source_stats", {}).get("has_tests", False),
                "compensation": "Test files detected in source analysis",
                "completeness": "structural_only",
            },
            "coverage": {
                "alternative": "test",
                "check": lambda r: r.get("test", {}).get("returncode") == 0,
                "compensation": "Test execution successful - coverage derivable",
                "completeness": "partial",
            },
            "outdated": {
                "alternative": "cargo_metadata",
                "check": lambda r: bool(r.get("cargo_metadata")),
                "compensation": "Dependency info available from Cargo.toml",
                "completeness": "dependency_list_only",
            },
            "doc": {
                "alternative": "source_stats",
                "check": lambda r: r.get("source_stats", {}).get("total_lines", 0) > 0,
                "compensation": "Documentation quality estimated from source analysis",
                "completeness": "estimated",
            },
        }

        if analysis_type in compensations:
            comp = compensations[analysis_type]
            if comp["check"](all_results):
                return {
                    "failed_analysis": analysis_type,
                    "compensation_source": comp["alternative"],
                    "compensation_description": comp["compensation"],
                    "data_completeness": comp["completeness"],
                }

        return None

    def _extract_additional_metadata(
        self, results: Dict[str, Any], env_info: Dict[str, Any]
    ) -> None:
        """Extract additional metadata from analysis results."""
        try:
            metadata = {
                "crate_name": env_info.get("crate_name", "unknown"),
                "version": env_info.get("version", "unknown"),
                "analysis_timestamp": results.get("timestamp"),
                "platform": env_info.get("platform", "unknown"),
                "rust_edition": env_info.get("edition", "unknown"),
                "crate_type": env_info.get("crate_type", "unknown"),
                "feature_count": len(env_info.get("features", [])),
                "dependency_count": len(env_info.get("dependencies", [])),
                "dev_dependency_count": len(env_info.get("dev_dependencies", [])),
            }

            # Extract build metadata
            build_result = results.get("build", {})
            if build_result.get("returncode") == 0:
                metadata["build_success"] = True
                metadata["build_duration"] = build_result.get("duration", 0)
            else:
                metadata["build_success"] = False
                metadata["build_error"] = build_result.get("stderr", "")

            # Extract test metadata
            test_result = results.get("test", {})
            metadata["test_success"] = test_result.get("returncode") == 0

            # Extract security metadata
            audit_result = results.get("audit", {})
            metadata["security_audit_success"] = audit_result.get("returncode") == 0

            geiger_result = results.get("geiger", {})
            metadata["unsafe_analysis_success"] = geiger_result.get("returncode") == 0

            # Extract code quality metadata
            clippy_result = results.get("clippy", {})
            metadata["clippy_success"] = clippy_result.get("returncode") == 0

            fmt_result = results.get("fmt", {})
            metadata["format_check_success"] = fmt_result.get("returncode") == 0

            # Extract documentation metadata
            doc_result = results.get("doc", {})
            metadata["doc_generation_success"] = doc_result.get("returncode") == 0

            # Store metadata in results
            results["additional_metadata"] = metadata

        except Exception as e:
            self.logger.warning(f"Failed to extract additional metadata: {e}")
            results["additional_metadata"] = {"error": str(e)}

    def _analyze_dependency_health(self, outdated_output: str) -> Dict[str, Any]:
        """Analyze dependency health from outdated command output."""
        try:
            health_analysis = {
                "overall_score": 0.0,
                "issues": [],
                "recommendations": [],
                "outdated_count": 0,
                "vulnerable_count": 0,
                "total_dependencies": 0,
                "health_score": 1.0,
            }

            # Try to parse JSON format first
            try:
                outdated_data = json.loads(outdated_output)
                if isinstance(outdated_data, dict) and "dependencies" in outdated_data:
                    dependencies = outdated_data["dependencies"]
                    health_analysis["total_dependencies"] = len(dependencies)

                    outdated_deps = [
                        dep
                        for dep in dependencies
                        if dep.get("latest") != dep.get("project")
                    ]
                    health_analysis["outdated_count"] = len(outdated_deps)

                    if outdated_deps:
                        health_analysis["issues"].append(
                            f"Found {len(outdated_deps)} outdated dependencies"
                        )
                        health_analysis["recommendations"].append(
                            "Consider updating outdated dependencies"
                        )

            except json.JSONDecodeError:
                # Parse text format as fallback
                lines = outdated_output.split("\n")
                outdated_lines = [
                    line for line in lines if "outdated" in line.lower() or "->" in line
                ]
                health_analysis["outdated_count"] = len(outdated_lines)

                if outdated_lines:
                    health_analysis["issues"].append(
                        f"Found {len(outdated_lines)} outdated dependencies"
                    )
                    health_analysis["recommendations"].append(
                        "Consider updating outdated dependencies"
                    )

            # Calculate overall health score
            score = 1.0  # Start with perfect score

            # Penalize for outdated dependencies
            if health_analysis["outdated_count"] > 0:
                score -= min(0.3, health_analysis["outdated_count"] * 0.05)

            health_analysis["overall_score"] = max(0.0, min(1.0, score))
            health_analysis["health_score"] = health_analysis["overall_score"]

            # Add general recommendations
            if health_analysis["overall_score"] < 0.7:
                health_analysis["recommendations"].append(
                    "Consider improving dependency health"
                )

            if health_analysis["total_dependencies"] > 50:
                health_analysis["recommendations"].append(
                    "Consider reducing dependency count for better maintainability"
                )

            return health_analysis

        except Exception as e:
            self.logger.warning(f"Failed to analyze dependency health: {e}")
            return {
                "overall_score": 0.5,
                "issues": [f"Analysis failed: {e}"],
                "recommendations": ["Manual dependency review recommended"],
                "outdated_count": 0,
                "vulnerable_count": 0,
                "total_dependencies": 0,
                "health_score": 0.5,
            }
