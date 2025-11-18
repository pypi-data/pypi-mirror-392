"""Centralized heuristics for Rust snippet assessment."""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Callable, Final, List

# Import consolidated complexity and topic detection from rust_code_analyzer
from ..utils.rust_code_analyzer import (
    RustCodeAnalyzer,
    classify_complexity_level,
    complexity_score,
    detect_topics,
)

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

_MIN_CHARS: Final[int] = 50
_MAX_CHARS: Final[int] = 4000
_MIN_LINES: Final[int] = 3

_REQUIRED_CONSTRUCTS: Final[tuple[str, ...]] = (
    "fn ",
    "struct ",
    "enum ",
    "impl ",
    "trait ",
    "use ",
    "let ",
    "match ",
    "macro_rules!",
)

_ACCEPT_MARKERS: Final[tuple[str, ...]] = (
    "fn main",
    "async fn",
    "Result<",
    "Option<",
    "Vec<",
    "HashMap",
    "println!",
    "macro_rules!",
    "#[macro_export",
    "#[proc_macro",
    "async move",
    ".await",
    "tokio::",
)

_COMMENT_STARTERS: Final[tuple[str, ...]] = ("//", "/*")


@dataclass(frozen=True)
class _SnippetStats:
    """Pre-computed statistics for heuristics."""

    snippet: str
    stripped: str
    lines: List[str]

    @property
    def non_empty_lines(self) -> List[str]:
        return [line for line in self.lines if line.strip()]

    @property
    def line_count(self) -> int:
        return len(self.lines)


def _gather_stats(snippet: str) -> _SnippetStats:
    stripped = snippet.strip()
    lines = snippet.splitlines()
    return _SnippetStats(snippet=snippet, stripped=stripped, lines=lines)


def _balanced_pairs(snippet: str) -> bool:
    return snippet.count("{") == snippet.count("}") and snippet.count("(") == snippet.count(")")


def _has_required_construct(snippet: str) -> bool:
    return any(marker in snippet for marker in _REQUIRED_CONSTRUCTS)


def _has_accept_marker(snippet: str) -> bool:
    return any(marker in snippet for marker in _ACCEPT_MARKERS)


def _token_density(snippet: str) -> float:
    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", snippet)
    if not tokens:
        return 0.0
    unique_tokens = len(set(tokens))
    length = max(len(snippet), 1)
    return unique_tokens / length


def _legacy_is_high_quality_snippet(snippet: str) -> bool:
    stats = _gather_stats(snippet)

    if len(snippet) < _MIN_CHARS or len(snippet) > _MAX_CHARS:
        return False

    if stats.stripped.startswith(_COMMENT_STARTERS):
        return False

    if not _balanced_pairs(snippet):
        return False

    if not _has_required_construct(snippet):
        return False

    if _has_accept_marker(snippet):
        return True

    if any(marker in stats.stripped for marker in ("macro_rules!", "#[macro_export", "#[proc_macro")):
        return True

    for prefix in ("struct ", "enum ", "trait "):
        if stats.stripped.startswith(prefix) or stats.stripped.startswith(f"pub {prefix}"):
            return True
        if stats.stripped.startswith("pub(crate) ") and stats.stripped[len("pub(crate) ") :].startswith(prefix):
            return True

    return False


def is_high_quality_snippet(snippet: str) -> bool:
    """Return ``True`` if the snippet appears to be a high-quality Rust example."""

    stats = _gather_stats(snippet)

    if len(stats.stripped) < _MIN_CHARS or len(stats.stripped) > _MAX_CHARS:
        return False

    if stats.line_count < _MIN_LINES or not stats.non_empty_lines:
        return False

    if stats.stripped.startswith(_COMMENT_STARTERS):
        return False

    if not _balanced_pairs(stats.snippet):
        return False

    if "todo!" in stats.snippet or "unimplemented!" in stats.snippet:
        return False

    if stats.non_empty_lines and any(line.strip().startswith("# ") for line in stats.lines[:2]):
        return False

    density = _token_density(stats.snippet)
    if density < 0.02:  # Too sparse, likely not real code
        return False

    if _has_accept_marker(stats.snippet):
        return True

    if _has_required_construct(stats.snippet):
        return True

    return _legacy_is_high_quality_snippet(stats.snippet)


# Delegate to consolidated implementations in rust_code_analyzer
# These functions are kept here for backward compatibility
# The actual implementations are in rust_crate_pipeline.utils.rust_code_analyzer


def get_quality_checker(use_legacy: bool) -> Callable[[str], bool]:
    """Return a quality checker respecting the legacy toggle."""

    return _legacy_is_high_quality_snippet if use_legacy else is_high_quality_snippet


def extract_features(rs_code: str) -> List[str]:
    """
    Extract Rust language features demonstrated in the code.
    
    This is a more detailed feature extraction than detect_topics(),
    focusing on specific language constructs.
    
    Args:
        rs_code: Rust code to analyze
        
    Returns:
        List of detected feature names
    """
    features = []
    code_lower = rs_code.lower()
    
    # Async/await
    if "async" in code_lower or "await" in code_lower:
        features.append("async/await")
    
    # Error handling
    if "Result<" in rs_code:
        features.append("error_handling")
    
    # Option types
    if "Option<" in rs_code:
        features.append("option_types")
    
    # Try operator
    if "?" in rs_code:
        features.append("try_operator")
    
    # Pattern matching
    if "match " in code_lower:
        features.append("pattern_matching")
    
    # Trait implementation
    if "impl " in code_lower:
        features.append("trait_implementation")
    
    # Derive macros
    if "#[derive(" in rs_code:
        features.append("derive_macros")
    
    # Collections
    if "Vec<" in rs_code:
        features.append("collections")
    
    # Hash maps
    if "HashMap" in rs_code or "BTreeMap" in rs_code:
        features.append("hash_maps")
    
    # Smart pointers
    if "Box<" in rs_code or "Rc<" in rs_code or "Arc<" in rs_code:
        features.append("smart_pointers")
    
    # Closures
    if "fn(" in rs_code or "Fn(" in rs_code:
        features.append("closures")
    
    # Unsafe code
    if "unsafe" in code_lower:
        features.append("unsafe_code")
    
    return features


# Delegate to consolidated implementation
# classify_complexity_level is imported from rust_code_analyzer above


__all__ = [
    "complexity_score",
    "detect_topics",
    "extract_features",
    "classify_complexity_level",
    "get_quality_checker",
    "is_high_quality_snippet",
]
