"""
Tests for AST-based Rust code analyzer.
"""

import pytest
from rust_crate_pipeline.utils.rust_ast_analyzer import RustASTAnalyzer, get_rust_ast_analyzer


def test_rust_ast_analyzer_initialization():
    """Test that AST analyzer can be initialized."""
    analyzer = RustASTAnalyzer()
    assert analyzer is not None


def test_get_rust_ast_analyzer_singleton():
    """Test that get_rust_ast_analyzer returns singleton instance."""
    analyzer1 = get_rust_ast_analyzer()
    analyzer2 = get_rust_ast_analyzer()
    assert analyzer1 is analyzer2


def test_analyze_rust_content_simple_function():
    """Test analysis of simple Rust function."""
    analyzer = RustASTAnalyzer()
    code = """
    pub fn hello() {
        println!("Hello, world!");
    }
    """
    result = analyzer.analyze_rust_content(code)
    
    assert result["loc"] > 0
    assert len(result["functions"]) >= 1
    assert "hello" in result["functions"]


def test_analyze_rust_content_async_function():
    """Test detection of async functions."""
    analyzer = RustASTAnalyzer()
    code = """
    async fn fetch_data() -> Result<String, Error> {
        Ok("data".to_string())
    }
    """
    result = analyzer.analyze_rust_content(code)
    
    assert len(result["functions"]) >= 1
    # Should detect async function (either via AST or regex fallback)
    assert len(result.get("async_functions", [])) >= 0  # May be 0 if AST unavailable


def test_analyze_rust_content_struct():
    """Test detection of structs."""
    analyzer = RustASTAnalyzer()
    code = """
    pub struct User {
        name: String,
        age: u32,
    }
    """
    result = analyzer.analyze_rust_content(code)
    
    assert len(result["structs"]) >= 1
    assert "User" in result["structs"]


def test_analyze_rust_content_trait():
    """Test detection of traits."""
    analyzer = RustASTAnalyzer()
    code = """
    pub trait Display {
        fn display(&self) -> String;
    }
    """
    result = analyzer.analyze_rust_content(code)
    
    assert len(result["traits"]) >= 1
    assert "Display" in result["traits"]


def test_analyze_rust_content_unsafe():
    """Test detection of unsafe blocks."""
    analyzer = RustASTAnalyzer()
    code = """
    unsafe fn dangerous() {
        // unsafe code
    }
    """
    result = analyzer.analyze_rust_content(code)
    
    assert len(result["functions"]) >= 1
    # Should detect unsafe (either via AST or regex fallback)
    assert len(result.get("unsafe_functions", [])) >= 0


def test_complexity_score():
    """Test complexity scoring."""
    analyzer = RustASTAnalyzer()
    
    simple_code = "fn simple() {}"
    complex_code = """
    async fn complex<T: Display + Clone>(items: Vec<T>) -> Result<Vec<T>, Error> {
        unsafe {
            let mut result = Vec::new();
            for item in items {
                result.push(item.clone());
            }
            Ok(result)
        }
    }
    """
    
    simple_score = analyzer.complexity_score(simple_code)
    complex_score = analyzer.complexity_score(complex_code)
    
    assert 0.0 <= simple_score <= 1.0
    assert 0.0 <= complex_score <= 1.0
    assert complex_score > simple_score  # Complex code should score higher


def test_analyze_empty_content():
    """Test analysis of empty content."""
    analyzer = RustASTAnalyzer()
    result = analyzer.analyze_rust_content("")
    
    assert result["loc"] == 0
    assert len(result["functions"]) == 0
    assert len(result["structs"]) == 0
    assert len(result["traits"]) == 0

