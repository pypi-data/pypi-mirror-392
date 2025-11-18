"""
This module provides a Sanitizer class for removing PII and secrets from
text and data structures, and utilities for sanitizing documentation content.
"""

import logging
import re
from typing import Any, Dict, Optional

try:
    import spacy
    from presidio_analyzer import AnalyzerEngine
    from presidio_analyzer.nlp_engine import NlpEngineProvider
    SPACY_AVAILABLE = True
except ImportError:
    spacy = None
    AnalyzerEngine = None
    NlpEngineProvider = None
    SPACY_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    BeautifulSoup = None

log = logging.getLogger(__name__)

# Basic regex for finding things that look like keys/secrets
SECRET_REGEXES = {
    "api_key": re.compile(
        r"([a-zA-Z0-9_]*?key[a-zA-Z0-9_]*?)\s*[:=]\s*['\"]?" r"([a-zA-Z0-9_.-]+)['\"]?",
        re.IGNORECASE,
    ),
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "aws_secret_key": re.compile(r"[a-zA-Z0-9/+=]{40}"),
    "github_token": re.compile(r"ghp_[a-zA-Z0-9]{36}"),
    "generic_secret": re.compile(
        r"(['\"]?[a-zA-Z0-9_.-]*secret[a-zA-Z0-9_.-]*['\"]?\s*[:=]\s*"
        r"['\"]?[a-zA-Z0-9_.-]+['\"]?)",
        re.IGNORECASE,
    ),
    # Additional patterns for common secret variable names
    "api_token": re.compile(
        r"(api[_-]?token|api[_-]?key|auth[_-]?token|auth[_-]?key)\s*[:=]\s*['\"]?"
        r"([a-zA-Z0-9_.-]{20,})['\"]?",
        re.IGNORECASE,
    ),
    "password": re.compile(
        r"(password|passwd|pwd)\s*[:=]\s*['\"]?"
        r"([a-zA-Z0-9_.-]{8,})['\"]?",
        re.IGNORECASE,
    ),
    "high_entropy_string": re.compile(
        r"([a-zA-Z0-9_]+)\s*[:=]\s*['\"]?"
        r"([a-zA-Z0-9+/=]{32,})['\"]?",  # Base64-like strings 32+ chars
        re.IGNORECASE,
    ),
}


def download_spacy_model_if_not_present(model="en_core_web_sm"):
    """Checks if a spaCy model is available and downloads it if not."""
    try:
        spacy.load(model)
        log.info(f"SpaCy model '{model}' already installed.")
    except OSError:
        log.warning(f"SpaCy model '{model}' not found. Downloading...")
        from spacy.cli.download import download

        download(model)
        log.info(f"Successfully downloaded SpaCy model '{model}'.")


class Sanitizer:
    """Utility to optionally scrub PII/secret-esque tokens.

    By default sanitisation is now **disabled** because Rust crates' public
    metadata should not contain PII.  Pass ``enabled=True`` if you still want
    the behaviour (e.g. for tests).
    """

    def __init__(self, *, enabled: bool = False):
        self.enabled = enabled

        if self.enabled:
            # Heavy-weight models are only loaded if sanitisation requested
            download_spacy_model_if_not_present()

            # Set up Presidio Analyzer
            provider = NlpEngineProvider()
            nlp_engine = provider.create_engine()
            self.analyzer = AnalyzerEngine(
                nlp_engine=nlp_engine, supported_languages=["en"]
            )

    def sanitize_text(self, text: str) -> str:
        """Sanitizes a single string of text."""
        if not isinstance(text, str):
            return text

        if not self.enabled:
            return text

        # PII sanitization
        pii_results = self.analyzer.analyze(text=text, language="en")
        for result in pii_results:
            text = text.replace(
                text[result.start : result.end], f"[{result.entity_type}]"
            )

        # Secret sanitization
        for secret_type, regex in SECRET_REGEXES.items():
            text = regex.sub(f"[{secret_type.upper()}_REDACTED]", text)

        return text

    def sanitize_data(self, data: Any) -> Any:
        """Recursively sanitizes a data structure (dict, list, string)."""
        if not self.enabled:
            return data

        if isinstance(data, dict):
            return {key: self.sanitize_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_data(item) for item in data]
        elif isinstance(data, str):
            return self.sanitize_text(data)
        else:
            return data


def sanitize_documentation_content(
    content: str,
    max_words: int = 500,
    max_bytes: int = 4096,
    extract_sections: bool = True,
) -> str:
    """
    Sanitize and truncate documentation content.
    
    Args:
        content: Raw documentation content (HTML or markdown)
        max_words: Maximum number of words to keep
        max_bytes: Maximum size in bytes
        extract_sections: Whether to extract only useful sections
        
    Returns:
        Sanitized and truncated content
    """
    if not content:
        return ""
    
    # If HTML, extract useful sections and remove navigation
    if extract_sections and BS4_AVAILABLE and BeautifulSoup:
        content = _extract_useful_sections(content)
    
    # Remove common navigation/header patterns (markdown)
    content = _remove_navigation_headers(content)
    
    # Truncate by words first (more meaningful)
    words = content.split()
    if len(words) > max_words:
        content = " ".join(words[:max_words]) + "..."
    
    # Then truncate by bytes if still too large
    content_bytes = content.encode('utf-8')
    if len(content_bytes) > max_bytes:
        content = content_bytes[:max_bytes].decode('utf-8', errors='ignore')
        # Try to end at a word boundary
        if not content.endswith('...'):
            last_space = content.rfind(' ')
            if last_space > max_bytes * 0.9:  # If we're close to the limit
                content = content[:last_space] + "..."
    
    return content.strip()


def _extract_useful_sections(html_content: str) -> str:
    """Extract only useful sections from HTML (overview, examples, API summary)."""
    if not BS4_AVAILABLE or not BeautifulSoup:
        return html_content
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove navigation elements
        for nav in soup.find_all(['nav', 'header', 'footer', 'aside']):
            nav.decompose()
        
        # Remove common navigation classes/IDs
        for elem in soup.find_all(class_=re.compile(r'nav|menu|sidebar|toc', re.I)):
            elem.decompose()
        for elem in soup.find_all(id=re.compile(r'nav|menu|sidebar|toc', re.I)):
            elem.decompose()
        
        # Extract main content areas
        useful_selectors = [
            'main', '.main-content', '#main-content',
            '.docblock', '.rustdoc', '.content',
            'article', '.article-content',
        ]
        
        extracted_parts = []
        for selector in useful_selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text(separator=' ', strip=True)
                if text and len(text) > 50:  # Only meaningful content
                    extracted_parts.append(text)
        
        if extracted_parts:
            return "\n\n".join(extracted_parts)
        else:
            # Fallback: get all text but still remove nav elements
            return soup.get_text(separator=' ', strip=True)
            
    except Exception as e:
        log.warning(f"Failed to extract HTML sections: {e}")
        return html_content


def _remove_navigation_headers(content: str) -> str:
    """Remove common navigation headers and footers from markdown/text."""
    lines = content.split('\n')
    filtered_lines = []
    skip_section = False
    
    nav_patterns = [
        r'^#+\s*(table\s+of\s+contents|toc|navigation|menu|links)$',
        r'^\[.*?\]\(#.*?\)\s*$',  # Link-only lines (often nav)
        r'^---+\s*$',  # Horizontal rules (often separators)
    ]
    
    for line in lines:
        # Skip navigation sections
        if any(re.match(pattern, line, re.IGNORECASE) for pattern in nav_patterns):
            skip_section = True
            continue
        
        # Skip lines that are just links (common in nav)
        if re.match(r'^\s*\[.*?\]\(.*?\)\s*$', line):
            continue
        
        # Skip very short lines that are likely nav
        if len(line.strip()) < 3:
            continue
        
        filtered_lines.append(line)
        skip_section = False
    
    return '\n'.join(filtered_lines)


def sanitize_documentation_dict(
    docs_dict: Dict[str, Any],
    max_words: int = 500,
    max_bytes: int = 4096,
) -> Dict[str, Any]:
    """
    Sanitize documentation dictionary, truncating content fields.
    
    Args:
        docs_dict: Dictionary with documentation content (e.g., from scraping)
        max_words: Maximum words per content field
        max_bytes: Maximum bytes per content field
        
    Returns:
        Sanitized dictionary with truncated content
    """
    sanitized = {}
    
    for key, value in docs_dict.items():
        if isinstance(value, dict):
            # Recursively sanitize nested dicts
            sanitized[key] = sanitize_documentation_dict(value, max_words, max_bytes)
        elif isinstance(value, str) and key in ['content', 'text', 'body', 'description']:
            # Sanitize content fields
            sanitized[key] = sanitize_documentation_content(
                value, max_words=max_words, max_bytes=max_bytes
            )
        else:
            sanitized[key] = value
    
    return sanitized
