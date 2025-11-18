# utils/rust_code_analyzer.py
"""
Unified Rust code analysis utilities - consolidates complexity scoring,
topic detection, and code structure analysis.

Now uses AST-based analysis when tree-sitter is available, falling back to regex.
"""
import math
import re
from typing import Any, List

# Try to import AST-based analyzer
try:
    from .rust_ast_analyzer import get_rust_ast_analyzer
    AST_ANALYZER_AVAILABLE = True
except ImportError:
    AST_ANALYZER_AVAILABLE = False
    get_rust_ast_analyzer = None


class RustCodeAnalyzer:
    """Unified analyzer for Rust source code patterns, complexity, and topics"""

    @staticmethod
    def create_empty_metrics() -> dict[str, Any]:
        """Create standardized empty metrics structure"""
        return {
            "file_count": 0,
            "loc": 0,
            "complexity": [],
            "types": [],
            "traits": [],
            "functions": [],
            "has_tests": False,
            "has_examples": False,
            "has_benchmarks": False,
        }

    @staticmethod
    def analyze_rust_content(content: str) -> dict[str, Any]:
        """Analyze a single Rust file's content - atomic unit for content analysis.
        
        Uses AST-based analysis when available, falls back to regex patterns.
        """
        if not content:
            return {"loc": 0, "functions": [], "types": [], "traits": []}

        # Try AST-based analysis first
        if AST_ANALYZER_AVAILABLE and get_rust_ast_analyzer:
            try:
                ast_analyzer = get_rust_ast_analyzer()
                ast_result = ast_analyzer.analyze_rust_content(content)
                
                # Convert AST result to expected format
                return {
                    "loc": ast_result["loc"],
                    "functions": ast_result["functions"],
                    "types": ast_result["structs"] + ast_result["enums"],
                    "traits": ast_result["traits"],
                    # Additional AST-derived information
                    "async_functions": ast_result.get("async_functions", []),
                    "unsafe_functions": ast_result.get("unsafe_functions", []),
                    "generic_functions": ast_result.get("generic_functions", []),
                    "macros": ast_result.get("macros", []),
                    "unsafe_blocks": ast_result.get("unsafe_blocks", 0),
                    "async_blocks": ast_result.get("async_blocks", 0),
                }
            except Exception as e:
                # Fall back to regex if AST analysis fails
                import logging
                logger = logging.getLogger(__name__)
                logger.debug(f"AST analysis failed, using regex fallback: {e}")

        # Fallback to regex-based analysis
        loc = len(content.splitlines())
        fn_matches = re.findall(r"fn\s+([a-zA-Z0-9_]+)", content)
        struct_matches = re.findall(r"struct\s+([a-zA-Z0-9_]+)", content)
        trait_matches = re.findall(r"trait\s+([a-zA-Z0-9_]+)", content)

        return {
            "loc": loc,
            "functions": fn_matches,
            "types": struct_matches,
            "traits": trait_matches,
        }

    @staticmethod
    def detect_project_structure(file_list: list[str]) -> dict[str, bool]:
        """Detect project structure patterns - atomic unit for structure detection"""
        structure = {
            "has_tests": False,
            "has_examples": False,
            "has_benchmarks": False,
        }

        # Convert to lowercase for case-insensitive checking
        files_lower = [f.lower() for f in file_list]

        # Detect common Rust project patterns
        structure["has_tests"] = any("test" in f for f in files_lower)
        structure["has_examples"] = any("example" in f for f in files_lower)
        structure["has_benchmarks"] = any("bench" in f for f in files_lower)

        return structure

    @staticmethod
    def aggregate_metrics(
        metrics: dict[str, Any],
        content_analysis: dict[str, Any],
        structure: dict[str, bool],
    ) -> dict[str, Any]:
        """Aggregate analysis results - atomic unit for combining results"""
        metrics["loc"] += content_analysis["loc"]
        metrics["functions"].extend(content_analysis["functions"])
        metrics["types"].extend(content_analysis["types"])
        metrics["traits"].extend(content_analysis["traits"])

        # Update structure flags (OR operation to preserve True values)
        metrics["has_tests"] = metrics["has_tests"] or structure["has_tests"]
        metrics["has_examples"] = metrics["has_examples"] or structure["has_examples"]
        metrics["has_benchmarks"] = (
            metrics["has_benchmarks"] or structure["has_benchmarks"]
        )

        return metrics

    # Complexity scoring constants
    _COMPLEXITY_FEATURES: tuple[tuple[str, float], ...] = (
        (r"fn\s+\w+", 1.5),
        (r"impl\s+\w+", 1.2),
        (r"trait\s+\w+", 1.2),
        (r"enum\s+\w+", 1.0),
        (r"struct\s+\w+", 1.0),
        (r"match\s+", 0.8),
        (r"async\s", 1.0),
        (r"unsafe", 2.0),
        (r"<[^>]+>", 0.6),
        (r"::", 0.4),
        (r"for\s+\w+\s+in", 0.6),
    )

    @staticmethod
    def complexity_score(rs_code: str) -> float:
        """
        Return a normalized complexity score for the provided Rust code.
        
        Uses AST-based analysis when available for more accurate scoring.
        
        Args:
            rs_code: Rust code to analyze
            
        Returns:
            Complexity score between 0.0 and 1.0
        """
        # Try AST-based complexity scoring first
        if AST_ANALYZER_AVAILABLE and get_rust_ast_analyzer:
            try:
                ast_analyzer = get_rust_ast_analyzer()
                return ast_analyzer.complexity_score(rs_code)
            except Exception:
                # Fall back to regex-based scoring
                pass

        # Fallback to regex-based complexity scoring
        lines = [line for line in rs_code.splitlines() if line.strip()]
        line_score = min(len(lines) * 0.15, 6.0)

        feature_score = 0.0
        for pattern, weight in RustCodeAnalyzer._COMPLEXITY_FEATURES:
            matches = re.findall(pattern, rs_code)
            feature_score += len(matches) * weight

        nesting_bonus = 0.0
        brace_depth = 0
        max_depth = 0
        for char in rs_code:
            if char == "{":
                brace_depth += 1
                max_depth = max(max_depth, brace_depth)
            elif char == "}":
                brace_depth = max(0, brace_depth - 1)
        if max_depth >= 4:
            nesting_bonus = 2.0
        elif max_depth == 3:
            nesting_bonus = 1.0

        raw_score = line_score + feature_score + nesting_bonus
        normalized = 1 - math.exp(-raw_score / 10.0)
        return min(max(normalized, 0.0), 1.0)

    @staticmethod
    def classify_complexity_level(rs_code: str) -> str:
        """
        Classify code complexity into human-friendly buckets.
        
        Args:
            rs_code: Rust code to analyze
            
        Returns:
            "beginner", "intermediate", or "advanced"
        """
        score = RustCodeAnalyzer.complexity_score(rs_code)
        if score < 0.3:
            return "beginner"
        if score < 0.6:
            return "intermediate"
        return "advanced"

    # Topic detection constants
    _TOPIC_RULES: tuple[tuple[str, str], ...] = (
        ("fn main", "main_function"),
        ("struct ", "data_structures"),
        ("enum ", "enumerations"),
        ("trait ", "traits"),
        ("async", "asynchronous_programming"),
        ("#[test]", "testing"),
        ("serde", "serialization"),
        ("tokio", "async_runtime"),
        ("std::", "standard_library"),
        ("Result<", "error_handling"),
        ("Error", "error_handling"),
        ("Iterator", "iterators"),
        ("Stream", "streams"),
    )

    @staticmethod
    def detect_topics(rs_code: str) -> List[str]:
        """
        Detect high-level topics demonstrated by the Rust code.
        
        Args:
            rs_code: Rust code to analyze
            
        Returns:
            List of detected topic names
        """
        lowered = rs_code.lower()
        topics: List[str] = []

        for marker, topic in RustCodeAnalyzer._TOPIC_RULES:
            if marker.lower() in lowered:
                topics.append(topic)

        if re.search(r"#\[derive\s*\(.*serde::", lowered):
            if "serialization" not in topics:
                topics.append("serialization")

        if re.search(r"(Arc|Rc|Mutex|RwLock)(::|<)", rs_code):
            topics.append("concurrency")

        if "unsafe" in lowered:
            topics.append("unsafe_code")

        if "::from" in rs_code or "TryFrom" in rs_code:
            topics.append("conversions")

        if "Iterator" in rs_code and "collect" in rs_code:
            if "iterators" not in topics:
                topics.append("iterators")

        seen = set()
        ordered_topics = []
        for topic in topics:
            if topic not in seen:
                ordered_topics.append(topic)
                seen.add(topic)
        return ordered_topics


# Convenience functions for backward compatibility
def complexity_score(rs_code: str) -> float:
    """Convenience function delegating to RustCodeAnalyzer.complexity_score"""
    return RustCodeAnalyzer.complexity_score(rs_code)


def detect_topics(rs_code: str) -> List[str]:
    """Convenience function delegating to RustCodeAnalyzer.detect_topics"""
    return RustCodeAnalyzer.detect_topics(rs_code)


def classify_complexity_level(rs_code: str) -> str:
    """Convenience function delegating to RustCodeAnalyzer.classify_complexity_level"""
    return RustCodeAnalyzer.classify_complexity_level(rs_code)
