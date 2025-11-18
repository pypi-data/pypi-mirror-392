"""
AST-based Rust code analysis using tree-sitter.

Replaces regex-based analysis with proper AST parsing for accurate detection of:
- Functions (including async, unsafe, generic)
- Structs, enums, traits
- Macros
- Unsafe blocks
- Async blocks
- Generics
"""

import logging
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# Try to import tree-sitter
try:
    import tree_sitter
    from tree_sitter import Language, Parser
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    tree_sitter = None
    Language = None
    Parser = None

# Try to import tree-sitter-languages for Rust grammar
try:
    from tree_sitter_languages import get_language, get_parser
    TREE_SITTER_LANGUAGES_AVAILABLE = True
except ImportError:
    TREE_SITTER_LANGUAGES_AVAILABLE = False
    get_language = None
    get_parser = None

# Fallback to regex if tree-sitter unavailable
import re


class RustASTAnalyzer:
    """AST-based Rust code analyzer using tree-sitter."""

    def __init__(self):
        """Initialize the AST analyzer."""
        self.parser: Optional[Parser] = None
        self._init_parser()

    def _init_parser(self) -> None:
        """Initialize tree-sitter parser for Rust."""
        if not TREE_SITTER_AVAILABLE:
            logger.warning("tree-sitter not available, falling back to regex analysis")
            return

        try:
            if TREE_SITTER_LANGUAGES_AVAILABLE:
                # Use tree-sitter-languages convenience function
                self.parser = get_parser("rust")
                if self.parser:
                    logger.info("Initialized tree-sitter Rust parser")
                    return
            else:
                # Try to build parser manually (requires rust grammar)
                try:
                    rust_lang = get_language("rust")
                    if rust_lang:
                        self.parser = Parser(rust_lang)
                        logger.info("Initialized tree-sitter Rust parser (manual)")
                        return
                except Exception as e:
                    logger.debug(f"Could not initialize Rust parser manually: {e}")

            logger.warning("Could not initialize tree-sitter Rust parser, using regex fallback")
        except Exception as e:
            logger.warning(f"Failed to initialize tree-sitter parser: {e}, using regex fallback")

    def analyze_rust_content(self, content: str) -> Dict[str, Any]:
        """
        Analyze Rust code using AST parsing.
        
        Args:
            content: Rust source code to analyze
            
        Returns:
            Dictionary with analysis results including:
            - loc: lines of code
            - functions: list of function names
            - async_functions: list of async function names
            - unsafe_functions: list of unsafe function names
            - generic_functions: list of generic function names
            - structs: list of struct names
            - enums: list of enum names
            - traits: list of trait names
            - macros: list of macro invocations
            - unsafe_blocks: count of unsafe blocks
            - async_blocks: count of async blocks
            - generics: count of generic type parameters
        """
        if not content:
            return self._empty_result()

        if self.parser:
            return self._analyze_with_ast(content)
        else:
            return self._analyze_with_regex(content)

    def _analyze_with_ast(self, content: str) -> Dict[str, Any]:
        """Analyze using tree-sitter AST."""
        try:
            tree = self.parser.parse(bytes(content, "utf8"))
            root_node = tree.root_node

            result = self._empty_result()
            result["loc"] = len(content.splitlines())

            # Traverse AST to extract elements
            self._traverse_ast(root_node, content, result)

            return result
        except Exception as e:
            logger.warning(f"AST analysis failed: {e}, falling back to regex")
            return self._analyze_with_regex(content)

    def _traverse_ast(
        self, node: Any, source: str, result: Dict[str, Any]
    ) -> None:
        """Recursively traverse AST nodes to extract code elements."""
        if not node:
            return

        node_type = node.type
        node_text = source[node.start_byte : node.end_byte].decode("utf8", errors="ignore")

        # Extract functions
        if node_type == "function_item":
            func_name = self._extract_function_name(node, source)
            if func_name:
                result["functions"].append(func_name)
                # Check for async
                if self._has_child(node, "async"):
                    result["async_functions"].append(func_name)
                # Check for unsafe
                if self._has_child(node, "unsafe"):
                    result["unsafe_functions"].append(func_name)
                # Check for generics
                if self._has_child(node, "type_parameters"):
                    result["generic_functions"].append(func_name)

        # Extract structs
        elif node_type == "struct_item":
            struct_name = self._extract_type_name(node, source)
            if struct_name:
                result["structs"].append(struct_name)
                if self._has_child(node, "type_parameters"):
                    result["generics"] += 1

        # Extract enums
        elif node_type == "enum_item":
            enum_name = self._extract_type_name(node, source)
            if enum_name:
                result["enums"].append(enum_name)
                if self._has_child(node, "type_parameters"):
                    result["generics"] += 1

        # Extract traits
        elif node_type == "trait_item":
            trait_name = self._extract_type_name(node, source)
            if trait_name:
                result["traits"].append(trait_name)
                if self._has_child(node, "type_parameters"):
                    result["generics"] += 1

        # Extract macros
        elif node_type == "macro_invocation":
            macro_name = self._extract_macro_name(node, source)
            if macro_name:
                result["macros"].append(macro_name)

        # Count unsafe blocks
        elif node_type == "unsafe_block":
            result["unsafe_blocks"] += 1

        # Count async blocks
        elif node_type == "async_block":
            result["async_blocks"] += 1

        # Recursively traverse children
        for child in node.children:
            self._traverse_ast(child, source, result)

    def _has_child(self, node: Any, child_type: str) -> bool:
        """Check if node has a child of specified type."""
        if not node or not hasattr(node, "children"):
            return False
        return any(child.type == child_type for child in node.children)

    def _extract_function_name(self, node: Any, source: str) -> Optional[str]:
        """Extract function name from function_item node."""
        try:
            # Look for identifier child
            for child in node.children:
                if child.type == "identifier":
                    return source[child.start_byte : child.end_byte].decode("utf8", errors="ignore")
        except Exception:
            pass
        return None

    def _extract_type_name(self, node: Any, source: str) -> Optional[str]:
        """Extract type name from struct/enum/trait node."""
        try:
            # Look for type_identifier child
            for child in node.children:
                if child.type == "type_identifier":
                    return source[child.start_byte : child.end_byte].decode("utf8", errors="ignore")
        except Exception:
            pass
        return None

    def _extract_macro_name(self, node: Any, source: str) -> Optional[str]:
        """Extract macro name from macro_invocation node."""
        try:
            # Macro name is typically the first identifier
            for child in node.children:
                if child.type == "identifier":
                    return source[child.start_byte : child.end_byte].decode("utf8", errors="ignore")
        except Exception:
            pass
        return None

    def _analyze_with_regex(self, content: str) -> Dict[str, Any]:
        """Fallback to regex-based analysis."""
        result = self._empty_result()
        result["loc"] = len(content.splitlines())

        # Extract functions (including async and unsafe)
        fn_pattern = r"(?:async\s+)?(?:unsafe\s+)?fn\s+([a-zA-Z0-9_]+)"
        fn_matches = re.findall(fn_pattern, content)
        result["functions"] = fn_matches

        # Extract async functions
        async_fn_pattern = r"async\s+fn\s+([a-zA-Z0-9_]+)"
        async_matches = re.findall(async_fn_pattern, content)
        result["async_functions"] = async_matches

        # Extract unsafe functions
        unsafe_fn_pattern = r"unsafe\s+fn\s+([a-zA-Z0-9_]+)"
        unsafe_matches = re.findall(unsafe_fn_pattern, content)
        result["unsafe_functions"] = unsafe_matches

        # Extract generic functions (simplified - looks for <T>)
        generic_fn_pattern = r"fn\s+([a-zA-Z0-9_]+)\s*<"
        generic_matches = re.findall(generic_fn_pattern, content)
        result["generic_functions"] = generic_matches

        # Extract structs
        struct_pattern = r"struct\s+([a-zA-Z0-9_]+)"
        struct_matches = re.findall(struct_pattern, content)
        result["structs"] = struct_matches

        # Extract enums
        enum_pattern = r"enum\s+([a-zA-Z0-9_]+)"
        enum_matches = re.findall(enum_pattern, content)
        result["enums"] = enum_matches

        # Extract traits
        trait_pattern = r"trait\s+([a-zA-Z0-9_]+)"
        trait_matches = re.findall(trait_pattern, content)
        result["traits"] = trait_matches

        # Extract macros (simplified)
        macro_pattern = r"([a-zA-Z0-9_]+)!\s*\("
        macro_matches = re.findall(macro_pattern, content)
        result["macros"] = macro_matches

        # Count unsafe blocks
        unsafe_block_pattern = r"unsafe\s*\{"
        result["unsafe_blocks"] = len(re.findall(unsafe_block_pattern, content))

        # Count async blocks
        async_block_pattern = r"async\s*\{"
        result["async_blocks"] = len(re.findall(async_block_pattern, content))

        # Count generics (simplified - count <T> patterns)
        generic_pattern = r"<[^>]+>"
        result["generics"] = len(re.findall(generic_pattern, content))

        return result

    def _empty_result(self) -> Dict[str, Any]:
        """Create empty analysis result structure."""
        return {
            "loc": 0,
            "functions": [],
            "async_functions": [],
            "unsafe_functions": [],
            "generic_functions": [],
            "structs": [],
            "enums": [],
            "traits": [],
            "macros": [],
            "unsafe_blocks": 0,
            "async_blocks": 0,
            "generics": 0,
        }

    def complexity_score(self, rs_code: str) -> float:
        """
        Calculate complexity score based on AST analysis.
        
        Uses actual code structure rather than regex patterns.
        """
        result = self.analyze_rust_content(rs_code)

        # Base complexity from LOC
        loc = result["loc"]
        loc_score = min(loc * 0.15, 6.0)

        # Complexity from code elements
        element_score = (
            len(result["functions"]) * 1.5
            + len(result["structs"]) * 1.0
            + len(result["enums"]) * 1.0
            + len(result["traits"]) * 1.2
            + len(result["macros"]) * 0.8
        )

        # Higher complexity for advanced features
        advanced_score = (
            len(result["async_functions"]) * 1.5
            + len(result["unsafe_functions"]) * 2.0
            + len(result["generic_functions"]) * 1.2
            + result["unsafe_blocks"] * 1.5
            + result["async_blocks"] * 1.0
            + result["generics"] * 0.6
        )

        raw_score = loc_score + element_score + advanced_score
        import math

        normalized = 1 - math.exp(-raw_score / 10.0)
        return min(max(normalized, 0.0), 1.0)


# Global instance for convenience
_analyzer_instance: Optional[RustASTAnalyzer] = None


def get_rust_ast_analyzer() -> RustASTAnalyzer:
    """Get or create global AST analyzer instance."""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = RustASTAnalyzer()
    return _analyzer_instance

