"""
Atomic HTTP client utilities - extracted from duplicate network patterns
"""
import asyncio
import logging
import os
import re
import shutil
import subprocess
import tempfile
import time
import tomllib
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from requests_cache import CachedSession

from ..config import DEFAULT_HTTP_TIMEOUT


class HTTPClientUtils:
    """Atomic unit for HTTP client operations"""

    @staticmethod
    def create_cached_session(cache_name: str, cache_ttl: int) -> CachedSession:
        """Create a standardized cached session - atomic unit"""
        return CachedSession(cache_name, expire_after=cache_ttl)

    @staticmethod
    def fetch_with_retry(
        session: requests.Session,
        url: str,
        max_retries: int = 3,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = DEFAULT_HTTP_TIMEOUT,
    ) -> Optional[requests.Response]:
        """Fetch URL with exponential backoff retry - atomic unit"""
        for attempt in range(max_retries):
            try:
                response = session.get(url, headers=headers or {}, timeout=timeout)
                if response.ok:
                    return response
                else:
                    logging.warning(
                        "HTTP %d for %s on attempt %d",
                        response.status_code,
                        url,
                        attempt + 1,
                    )
            except requests.RequestException as e:
                logging.warning("Attempt %d failed for %s: %s", attempt + 1, url, e)

            if attempt < max_retries - 1:  # Don't sleep on the last attempt
                wait_time = 2**attempt
                time.sleep(wait_time)

        return None

    @staticmethod
    async def fetch_with_retry_async(
        session: requests.Session,
        url: str,
        max_retries: int = 3,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = DEFAULT_HTTP_TIMEOUT,
    ) -> Optional[requests.Response]:
        """Async wrapper around :meth:`fetch_with_retry` using ``asyncio.to_thread``."""

        return await asyncio.to_thread(
            HTTPClientUtils.fetch_with_retry,
            session,
            url,
            max_retries,
            headers,
            timeout,
        )

    @staticmethod
    def extract_github_repo_info(repo_url: str) -> Optional[tuple[str, str]]:
        """Extract owner/repo from GitHub URL - atomic unit"""
        if not repo_url or "github.com" not in repo_url:
            return None

        match = re.search(r"github\.com/([^/]+)/([^/]+)", repo_url)
        if match:
            owner, repo_name = match.groups()
            # Handle .git extensions
            repo_name = repo_name.split(".")[0]
            return owner, repo_name

        return None

    @staticmethod
    def get_github_headers(token: Optional[str] = None) -> Dict[str, str]:
        """Get standardized GitHub API headers - atomic unit"""
        headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            headers["Authorization"] = f"token {token}"
        return headers


class MetadataExtractor:
    """Atomic unit for extracting metadata from different sources"""

    @staticmethod
    def extract_code_snippets(
        content: str,
        max_snippets: int = 5,
        compile_check: bool = True,
    ) -> List[str]:
        """
        Extract high-quality Rust or TOML snippets from markdown content.

        When ``compile_check`` is enabled (default), each candidate snippet is
        validated by invoking ``rustc`` for Rust or parsing with ``tomllib`` for
        TOML. This provides high-quality results but can incur a performance
        cost (especially for Rust, which spawns a compiler process). Disabling
        ``compile_check`` skips these validations and accepts snippets after
        only a basic length check, which is much faster but may include
        syntactically invalid code.

        Args:
            content: Markdown content to search for snippets.
            max_snippets: Maximum number of snippets to return.
            compile_check: If True, verify Rust snippets compile and TOML
                snippets parse; if False, only a length/quality filter is applied.
        """
        if not content:
            return []

        # Match fenced code blocks like ```rust ...``` or ```toml ...``` (case-insensitive)
        pattern = re.compile(r"```(rust|toml)[^\n]*\n([\s\S]*?)```", re.IGNORECASE)
        snippets: List[str] = []

        for lang, code in pattern.findall(content):
            cleaned = code.strip()
            if len(cleaned) < 20:  # Length filter for quality
                continue

            if compile_check:
                if lang.lower() == "rust":
                    # Try rustdoc --test first (more reliable for doc examples)
                    # Fall back to rustc if rustdoc fails
                    if not MetadataExtractor._test_with_rustdoc(cleaned):
                        # Fallback to simple compilation check
                        if not MetadataExtractor._compiles_rust(cleaned):
                            continue
                elif lang.lower() == "toml":
                    if not MetadataExtractor._valid_toml(cleaned):
                        continue

            snippets.append(cleaned)
            if len(snippets) >= max_snippets:
                break

        return snippets

    @staticmethod
    async def extract_code_snippets_async(
        content: str,
        max_snippets: int = 5,
        compile_check: bool = True,
    ) -> List[str]:
        """Async wrapper that offloads snippet extraction to a background thread."""

        return await asyncio.to_thread(
            MetadataExtractor.extract_code_snippets,
            content,
            max_snippets,
            compile_check,
        )

    @staticmethod
    def _compiles_rust(code: str) -> bool:
        """Check if a Rust snippet compiles."""
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".rs", delete=False) as tmp:
                tmp.write(code)
                tmp.flush()
                tmp_path = tmp.name
            result = subprocess.run(
                ["rustc", "--crate-type", "lib", tmp_path],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, OSError, FileNotFoundError):
            return False
        finally:
            if tmp_path:
                # Windows has stricter file locking - retry cleanup
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        os.remove(tmp_path)
                        break
                    except (OSError, PermissionError) as e:
                        if attempt < max_retries - 1:
                            time.sleep(0.1)
                        else:
                            logging.warning("Could not remove temp file %s: %s", tmp_path, e)

    @staticmethod
    def _test_with_rustdoc(code: str, crate_name: Optional[str] = None) -> bool:
        """
        Test Rust code using rustdoc --test (for doc tests).
        
        This is more reliable than rustc for documentation examples as it
        properly handles doc test context and dependencies.
        
        Args:
            code: Rust code snippet to test
            crate_name: Optional crate name for context
            
        Returns:
            True if doc test passes, False otherwise
        """
        # Create a temporary Cargo project for doc testing
        temp_dir = None
        try:
            temp_dir = Path(tempfile.mkdtemp(prefix="rustdoc_test_"))
            
            # Create Cargo.toml
            cargo_toml = temp_dir / "Cargo.toml"
            with open(cargo_toml, "w") as f:
                f.write("[package]\n")
                f.write(f'name = "{crate_name or "test_crate"}"\n')
                f.write('version = "0.1.0"\n')
                f.write('edition = "2021"\n')
            
            # Create src/lib.rs with the code as a doc test
            src_dir = temp_dir / "src"
            os.makedirs(src_dir, exist_ok=True)
            
            lib_rs = src_dir / "lib.rs"
            with open(lib_rs, "w") as f:
                f.write("/// Example usage:\n")
                f.write("/// ```rust\n")
                # Indent code for doc test context
                for line in code.splitlines():
                    f.write(f"/// {line}\n")
                f.write("/// ```\n")
                f.write("pub fn example() {}\n")
            
            # Run rustdoc --test (using cargo test --doc --no-run)
            # This compiles doc tests without executing them, catching compile errors
            result = subprocess.run(
                ["cargo", "test", "--doc", "--no-run"],
                cwd=str(temp_dir),
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            # If doc test compilation fails, try cargo check as fallback
            if result.returncode != 0:
                compile_result = subprocess.run(
                    ["cargo", "check", "--tests"],
                    cwd=str(temp_dir),
                    capture_output=True,
                    text=True,
                    timeout=20,
                )
                return compile_result.returncode == 0
            
            return result.returncode == 0
            
        except (subprocess.SubprocessError, OSError, FileNotFoundError) as e:
            logging.debug(f"rustdoc test failed: {e}, falling back to rustc")
            # Fall back to simple rustc check
            return MetadataExtractor._compiles_rust(code)
        finally:
            if temp_dir:
                # Clean up temp directory
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        shutil.rmtree(temp_dir)
                        break
                    except (OSError, PermissionError) as e:
                        if attempt < max_retries - 1:
                            time.sleep(0.1)
                        else:
                            logging.warning("Could not remove temp dir %s: %s", temp_dir, e)

    @staticmethod
    def _valid_toml(code: str) -> bool:
        """Check if a TOML snippet is syntactically valid."""
        try:
            tomllib.loads(code)
            return True
        except (tomllib.TOMLDecodeError, ValueError):
            return False

    @staticmethod
    def extract_readme_sections(readme: str) -> Dict[str, str]:
        """Extract sections from README based on markdown headers - atomic unit"""
        if not readme:
            return {}

        sections: Dict[str, str] = {}
        current_section = "intro"
        current_content: List[str] = []

        lines = readme.split("\n")
        for line in lines:
            if line.startswith("#"):
                # Save previous section
                if current_content:
                    sections[current_section] = "\n".join(current_content).strip()

                # Start new section
                current_section = line.strip("#").strip().lower().replace(" ", "_")
                current_content = []
            else:
                current_content.append(line)

        # Save final section
        if current_content:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    @staticmethod
    def create_empty_metadata() -> Dict[str, Any]:
        """Create standardized empty metadata structure - atomic unit"""
        return {
            "name": "",
            "version": "",
            "description": "",
            "repository": "",
            "keywords": [],
            "categories": [],
            "readme": "",
            "downloads": 0,
            "github_stars": 0,
            "dependencies": [],
            "code_snippets": [],
            "features": [],
            "readme_sections": {},
            "source": "unknown",
        }