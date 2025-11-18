"""
Real documentation analysis implementation.

Implements comprehensive documentation quality assessment using:
- Readability scores (Flesch-Kincaid, SMOG)
- Documentation coverage (rustdoc JSON parsing)
- Example density
- Navigation & accessibility
- Content freshness
"""

import asyncio
import json
import logging
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import aiohttp

log = logging.getLogger(__name__)

# Optional imports with graceful fallback
try:
    import textstat
    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False
    textstat = None


async def analyze_documentation_quality(
    crate_name: str,
    readme_content: str = "",
    repository_url: Optional[str] = None,
    crate_metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Analyze documentation quality using multiple metrics.
    
    Args:
        crate_name: Name of the crate
        readme_content: README content (markdown)
        repository_url: Repository URL (for GitHub access)
        crate_metadata: Full crate metadata dict
        
    Returns:
        Dictionary with documentation quality metrics
    """
    result = {
        "quality_score": 5.0,
        "readability_score": 0.5,
        "coverage": 0.5,
        "example_density": 0.0,
        "navigation_score": 0.0,
        "freshness_score": 0.5,
        "completeness": 0.5,
        "examples_present": False,
        "api_documented": False,
    }
    
    try:
        # 1. Readability Score (20% weight)
        readability_score = await _compute_readability_score(readme_content)
        result["readability_score"] = readability_score
        
        # 2. Documentation Coverage (30% weight)
        coverage = await _compute_documentation_coverage(crate_name, repository_url)
        result["coverage"] = coverage
        result["api_documented"] = coverage > 0.5
        
        # 3. Example Density (25% weight)
        example_density = _compute_example_density(readme_content)
        result["example_density"] = example_density
        result["examples_present"] = example_density > 0.0
        
        # 4. Navigation & Accessibility (15% weight)
        navigation_score = _compute_navigation_score(readme_content)
        result["navigation_score"] = navigation_score
        
        # 5. Content Freshness (10% weight)
        freshness_score = await _compute_freshness_score(
            crate_metadata, repository_url
        )
        result["freshness_score"] = freshness_score
        
        # Compute weighted quality score (0-10 scale)
        quality_score = (
            readability_score * 0.20 +
            coverage * 0.30 +
            example_density * 0.25 +
            navigation_score * 0.15 +
            freshness_score * 0.10
        ) * 10.0
        
        result["quality_score"] = round(quality_score, 2)
        result["completeness"] = round(
            (readability_score + coverage + example_density + navigation_score) / 4.0,
            2
        )
        
    except Exception as e:
        log.error(f"Documentation analysis error for {crate_name}: {e}")
        result["error"] = str(e)
    
    return result


async def _compute_readability_score(text: str) -> float:
    """Compute readability score using textstat (Flesch-Kincaid, SMOG)."""
    if not text or not TEXTSTAT_AVAILABLE:
        return 0.5
    
    try:
        # Flesch Reading Ease (higher = easier, 0-100)
        flesch_score = textstat.flesch_reading_ease(text)
        # Normalize to 0-1 (assuming good docs are 60-100)
        flesch_normalized = max(0, min(1, (flesch_score - 30) / 70))
        
        # SMOG Index (lower = easier, typically 1-20)
        smog_score = textstat.smog_index(text)
        # Normalize to 0-1 (assuming good docs are 1-12)
        smog_normalized = max(0, min(1, 1 - (smog_score - 1) / 11))
        
        # Average of both metrics
        return (flesch_normalized + smog_normalized) / 2.0
        
    except Exception as e:
        log.warning(f"Readability computation failed: {e}")
        return 0.5


async def _compute_documentation_coverage(
    crate_name: str, repository_url: Optional[str] = None
) -> float:
    """
    Compute documentation coverage by parsing rustdoc JSON.
    
    This requires downloading and building the crate, so it's
    best-effort and may return 0.5 if unavailable.
    """
    import tempfile
    import shutil
    
    temp_dir = None
    try:
        # Create temporary directory for crate download and build
        temp_dir = Path(tempfile.mkdtemp(prefix=f"rustdoc_{crate_name}_"))
        
        # Try to download crate source
        crate_url = f"https://crates.io/api/v1/crates/{crate_name}/download"
        timeout = aiohttp.ClientTimeout(total=60)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(crate_url) as resp:
                if resp.status != 200:
                    log.debug(f"Could not download {crate_name} for doc coverage analysis")
                    return 0.5
                
                # Save tarball
                tarball_path = temp_dir / f"{crate_name}.tar.gz"
                with open(tarball_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(8192):
                        f.write(chunk)
        
        # Extract tarball
        import tarfile
        with tarfile.open(tarball_path, "r:gz") as tar:
            tar.extractall(temp_dir)
        
        # Find Cargo.toml (usually in root or first subdirectory)
        cargo_toml = None
        for path in temp_dir.rglob("Cargo.toml"):
            if path.parent.name == crate_name or path.parent == temp_dir:
                cargo_toml = path
                break
        
        if not cargo_toml:
            log.debug(f"Could not find Cargo.toml for {crate_name}")
            return 0.5
        
        crate_root = cargo_toml.parent
        
        # Run cargo doc --output-format json
        # Note: This requires Rust toolchain to be installed
        try:
            result = subprocess.run(
                ["cargo", "doc", "--output-format", "json", "--no-deps", "--quiet"],
                cwd=crate_root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                check=False,
            )
            
            if result.returncode != 0:
                log.debug(f"cargo doc failed for {crate_name}: {result.stderr[:200]}")
                return 0.5
            
            # Find rustdoc JSON output (usually in target/doc/*.json)
            doc_json_files = list(crate_root.glob("target/doc/*.json"))
            if not doc_json_files:
                log.debug(f"No rustdoc JSON files found for {crate_name}")
                return 0.5
            
            # Parse JSON to count documented vs total public items
            total_public = 0
            documented = 0
            
            for json_file in doc_json_files:
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        doc_data = json.load(f)
                    
                    # Count items in the crate index
                    if "index" in doc_data:
                        for item in doc_data["index"].values():
                            # Check if item is public (not starting with _)
                            name = item.get("name", "")
                            if name and not name.startswith("_"):
                                total_public += 1
                                # Check if item has documentation
                                docs = item.get("docs", "")
                                if docs and docs.strip():
                                    documented += 1
                    
                    # Also check crate-level documentation
                    if "crate" in doc_data:
                        crate_info = doc_data["crate"]
                        if crate_info.get("name") == crate_name:
                            total_public += 1  # Count crate itself
                            if crate_info.get("docs") and crate_info.get("docs", "").strip():
                                documented += 1
                
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    log.debug(f"Error parsing rustdoc JSON for {crate_name}: {e}")
                    continue
            
            if total_public == 0:
                log.debug(f"No public items found for {crate_name}")
                return 0.5
            
            coverage = documented / total_public
            log.debug(f"Documentation coverage for {crate_name}: {documented}/{total_public} = {coverage:.2f}")
            return coverage
        
        except subprocess.TimeoutExpired:
            log.warning(f"cargo doc timed out for {crate_name}")
            return 0.5
        except FileNotFoundError:
            log.debug("cargo command not found, skipping doc coverage analysis")
            return 0.5
        except Exception as e:
            log.debug(f"Error running cargo doc for {crate_name}: {e}")
            return 0.5
    
    except Exception as e:
        log.debug(f"Documentation coverage analysis failed for {crate_name}: {e}")
        return 0.5
    
    finally:
        # Cleanup temporary directory
        if temp_dir and temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass


def _compute_example_density(readme_content: str) -> float:
    """
    Count Rust code blocks in README and compute density.
    
    Also detects example references, links to examples directories,
    and example lists in the README.
    """
    if not readme_content:
        return 0.0
    
    score = 0.0
    
    # 1. Count fenced code blocks marked as Rust
    rust_code_block_pattern = r'```rust\s*\n.*?```'
    rust_matches = re.findall(rust_code_block_pattern, readme_content, re.DOTALL | re.IGNORECASE)
    score += len(rust_matches) * 0.3  # Each code block = 0.3 points
    
    # 1b. Also check for code blocks with language tags like ```rust or ```rs
    rust_tagged_pattern = r'```(?:rust|rs)\s*\n.*?```'
    rust_tagged_matches = re.findall(rust_tagged_pattern, readme_content, re.DOTALL | re.IGNORECASE)
    if len(rust_tagged_matches) > len(rust_matches):
        score += (len(rust_tagged_matches) - len(rust_matches)) * 0.3
    
    # 2. Count generic code blocks that might be Rust
    generic_blocks = re.findall(r'```\s*\n.*?```', readme_content, re.DOTALL)
    # Check if generic blocks contain Rust-like code
    rust_like_in_generic = 0
    for block in generic_blocks:
        # Check for Rust keywords in the code block
        if re.search(r'\b(fn|let|mut|pub|struct|enum|impl|trait|use|mod|async|await|match|if let)\b', block, re.IGNORECASE):
            rust_like_in_generic += 1
    score += rust_like_in_generic * 0.25  # Rust-like generic blocks = 0.25 points
    score += (len(generic_blocks) - rust_like_in_generic) * 0.15  # Other generic blocks = 0.15 points
    
    # 3. Detect example links/references (e.g., links to examples/ directory)
    example_link_patterns = [
        r'\[.*?examples?.*?\]\([^)]*examples?[^)]*\)',  # Markdown links to examples
        r'https?://[^\s)]*examples?[^\s)]*',  # HTTP links to examples
        r'examples?/[^\s)]+',  # Relative paths to examples
        r'More\s+examples?\s+can\s+be\s+found',  # "More examples can be found" text
        r'More\s+examples?\s+[^\s]+',  # "More examples" followed by link or text
    ]
    example_links = 0
    for pattern in example_link_patterns:
        matches = re.findall(pattern, readme_content, re.IGNORECASE)
        example_links += len(matches)
    score += min(example_links * 0.15, 0.6)  # Cap at 0.6 for links
    
    # 3b. Also check for escaped markdown code blocks (common in scraped content)
    # Pattern: ``` followed by escaped backticks or code-like content
    # Handle escaped format like: ``` ```[``dependencies``]` `tokio = ...`
    escaped_code_patterns = [
        r'```\s*\n.*?(?:tokio|use\s+tokio|fn\s+main|async\s+fn|let\s+\w+|pub\s+fn)',  # Specific crate/function names
        r'```\s*```.*?(?:use\s+\w+|fn\s+\w+|let\s+\w+|pub\s+\w+)',  # Escaped backticks format
        r'```\s*\n.*?\[``.*?``\]',  # Escaped markdown like [``dependencies``]
    ]
    escaped_matches_count = 0
    for pattern in escaped_code_patterns:
        matches = re.findall(pattern, readme_content, re.DOTALL | re.IGNORECASE)
        escaped_matches_count += len(matches)
    if escaped_matches_count > 0:
        score += min(escaped_matches_count * 0.25, 0.5)  # Escaped code blocks still count, cap at 0.5
    
    # 4. Detect example sections/lists (e.g., "Examples:", "More Examples", etc.)
    example_section_patterns = [
        r'#+\s*examples?\s*[:#]',  # Headers like "## Examples:" or "## Examples"
        r'More\s+Examples',  # "More Examples" section
        r'Example\s+Usage',  # "Example Usage" section
        r'Usage\s+Examples?',  # "Usage Examples" section
        r'##\s+Example\b',  # "## Example" header
        r'Example\s*$',  # "Example" at end of line (likely a header)
    ]
    example_sections = 0
    for pattern in example_section_patterns:
        if re.search(pattern, readme_content, re.IGNORECASE | re.MULTILINE):
            example_sections += 1
    score += min(example_sections * 0.2, 0.4)  # Cap at 0.4 for sections
    
    # 4b. Check for "Example" followed by code blocks (common pattern)
    # Handle both normal and escaped markdown formats
    example_header_patterns = [
        r'(?:##\s+Example|Example\s*:)\s*\n.*?```',  # Normal markdown
        r'(?:##\s+Example|Example\s*:)\s*\n.*?```\s*```',  # Escaped markdown (``` ```)
        r'(?:##\s+Example|Example\s*:)\s*\n.*?(?:use\s+\w+|fn\s+\w+|let\s+\w+)',  # Example header followed by Rust code
    ]
    for pattern in example_header_patterns:
        if re.search(pattern, readme_content, re.IGNORECASE | re.DOTALL):
            score += 0.3  # Example header with code = strong signal
            break
    
    # 5. Detect example lists (bullet points or numbered lists under Examples sections)
    # Look for list items that appear after an "Examples" header
    # Pattern: find "Examples" header, then count list items in the following lines
    examples_header_pattern = r'#+\s*examples?\s*[:#]?\s*\n'
    examples_section_match = re.search(examples_header_pattern, readme_content, re.IGNORECASE | re.MULTILINE)
    if examples_section_match:
        # Extract content after the Examples header (up to next major section or 50 lines)
        start_pos = examples_section_match.end()
        section_content = readme_content[start_pos:start_pos + 5000]  # Check next 5000 chars
        # Count list items (bullet points or numbered) in this section
        list_item_pattern = r'(?:^|\n)\s*[-*•]\s+[^\n]+|(?:^|\n)\s*\d+[.)]\s+[^\n]+'
        list_items = re.findall(list_item_pattern, section_content, re.MULTILINE)
        # Filter out very short items (likely not examples)
        example_list_items = [item for item in list_items if len(item.strip()) > 5]
        if len(example_list_items) >= 3:  # If 3+ items, likely an example list
            score += min(len(example_list_items) * 0.08, 0.5)  # Cap at 0.5 for list items
    
    # Normalize to 0-1 scale: assume good docs have 3+ code blocks OR example references
    # If we have example links/sections, that's also valuable even without code blocks
    # Also check for inline code examples (single backticks with Rust-like syntax)
    if score == 0.0:
        # Check for inline code that might be examples
        inline_code_pattern = r'`[^`]+`'
        inline_matches = re.findall(inline_code_pattern, readme_content)
        # Look for Rust-like patterns in inline code
        rust_keywords = ['fn ', 'let ', 'mut ', 'pub ', 'struct ', 'enum ', 'impl ', 'trait ', 'use ', 'mod ', 'tokio', 'async', 'await']
        rust_inline_count = sum(1 for match in inline_matches if any(keyword in match for keyword in rust_keywords))
        if rust_inline_count >= 3:
            score = 0.2  # Some examples present in inline code
        
        # Also check for "More examples" text which indicates examples exist
        if re.search(r'More\s+examples?\s+can\s+be\s+found', readme_content, re.IGNORECASE):
            score = max(score, 0.15)  # At least some examples exist if this text is present
    
    if score > 0:
        # Scale: 1.0 = 3+ code blocks OR 5+ example links OR example section + links
        # But even 0.1 means examples are present
        return min(1.0, max(0.1, score / 1.0))  # Ensure minimum 0.1 if any examples found
    
    return 0.0


def _compute_navigation_score(readme_content: str) -> float:
    """Check for table of contents and valid internal links."""
    if not readme_content:
        return 0.0
    
    score = 0.0
    
    # Check for table of contents (common patterns)
    toc_patterns = [
        r'##\s*Table\s+of\s+Contents',
        r'##\s*Contents',
        r'##\s*TOC',
        r'#+\s*Table\s+of\s+Contents',
    ]
    
    has_toc = any(re.search(pattern, readme_content, re.IGNORECASE) for pattern in toc_patterns)
    if has_toc:
        score += 0.5
    
    # Check for internal links (markdown links)
    internal_link_pattern = r'\[.*?\]\(#.*?\)'
    internal_links = re.findall(internal_link_pattern, readme_content)
    
    if internal_links:
        score += 0.5
    
    return min(1.0, score)


async def _compute_freshness_score(
    crate_metadata: Optional[Dict[str, Any]] = None,
    repository_url: Optional[str] = None,
) -> float:
    """
    Compare documentation update date to latest release.
    
    Returns 1.0 if docs are fresh, lower if stale.
    """
    from datetime import datetime, timezone
    
    try:
        latest_release_date = None
        
        # 1. Get latest release date from crate_metadata
        if crate_metadata:
            # Try to get from newest_version
            newest_version = crate_metadata.get("newest_version")
            if newest_version and isinstance(newest_version, dict):
                created_at = newest_version.get("created_at")
                if created_at:
                    try:
                        latest_release_date = datetime.fromisoformat(
                            created_at.replace("Z", "+00:00")
                        )
                    except (ValueError, AttributeError):
                        pass
            
            # Fallback: try versions list
            if not latest_release_date:
                versions = crate_metadata.get("versions", [])
                if versions and isinstance(versions, list):
                    # Versions are typically sorted newest first
                    for version in versions[:5]:  # Check first 5 versions
                        created_at = version.get("created_at")
                        if created_at:
                            try:
                                latest_release_date = datetime.fromisoformat(
                                    created_at.replace("Z", "+00:00")
                                )
                                break
                            except (ValueError, AttributeError):
                                continue
        
        # 2. If no release date from metadata, try fetching from crates.io API
        if not latest_release_date and crate_metadata:
            crate_name = crate_metadata.get("name")
            if crate_name:
                try:
                    timeout = aiohttp.ClientTimeout(total=10)
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        url = f"https://crates.io/api/v1/crates/{crate_name}"
                        async with session.get(url) as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                crate_info = data.get("crate", {})
                                newest_version = crate_info.get("newest_version")
                                if newest_version:
                                    created_at = newest_version.get("created_at")
                                    if created_at:
                                        latest_release_date = datetime.fromisoformat(
                                            created_at.replace("Z", "+00:00")
                                        )
                except Exception as e:
                    log.debug(f"Failed to fetch release date from crates.io: {e}")
        
        # 3. Get last commit date from GitHub API
        last_commit_date = None
        if repository_url:
            parsed = urlparse(repository_url)
            if "github.com" in parsed.netloc:
                path_parts = parsed.path.strip("/").split("/")
                if len(path_parts) >= 2:
                    github_path = f"{path_parts[0]}/{path_parts[1]}"
                    try:
                        timeout = aiohttp.ClientTimeout(total=10)
                        async with aiohttp.ClientSession(timeout=timeout) as session:
                            # Get latest commit from default branch
                            commits_url = f"https://api.github.com/repos/{github_path}/commits"
                            async with session.get(
                                commits_url, params={"per_page": 1}
                            ) as resp:
                                if resp.status == 200:
                                    commits = await resp.json()
                                    if commits and isinstance(commits, list):
                                        commit = commits[0]
                                        commit_date_str = commit.get("commit", {}).get(
                                            "author", {}
                                        ).get("date")
                                        if commit_date_str:
                                            last_commit_date = datetime.fromisoformat(
                                                commit_date_str.replace("Z", "+00:00")
                                            )
                    except Exception as e:
                        log.debug(f"Failed to fetch GitHub commit date: {e}")
        
        # 4. Compute freshness score
        if not latest_release_date:
            # No release date available, return moderate score
            return 0.5
        
        now = datetime.now(timezone.utc)
        days_since_release = (now - latest_release_date).days
        
        # If we have commit date, use it to determine if docs are being updated
        if last_commit_date:
            days_since_commit = (now - last_commit_date).days
            
            # If commits are recent (within 30 days), docs are likely fresh
            if days_since_commit <= 30:
                return 1.0
            elif days_since_commit <= 90:
                return 0.8
            elif days_since_commit <= 180:
                return 0.6
            else:
                return 0.4
        
        # Otherwise, base score on release date
        # Fresh if release is within last 90 days
        if days_since_release <= 90:
            return 1.0
        elif days_since_release <= 180:
            return 0.8
        elif days_since_release <= 365:
            return 0.6
        elif days_since_release <= 730:
            return 0.4
        else:
            return 0.2
    
    except Exception as e:
        log.debug(f"Freshness score computation failed: {e}")
        return 0.5

