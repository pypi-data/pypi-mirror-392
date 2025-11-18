"""
Real ecosystem position analysis implementation.

Uses CHAOSS-inspired metrics to assess crate's position in Rust ecosystem.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import aiohttp

log = logging.getLogger(__name__)


async def analyze_ecosystem_position(
    crate_name: str,
    repository_url: Optional[str] = None,
    crate_metadata: Optional[Dict[str, Any]] = None,
    github_token: Optional[str] = None,
    sanitized_documentation: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Analyze ecosystem position using CHAOSS-inspired metrics.
    
    Args:
        crate_name: Name of the crate
        repository_url: Repository URL
        crate_metadata: Full crate metadata dict
        github_token: Optional GitHub API token
        sanitized_documentation: Optional scraped documentation (for parsing lib.rs content)
        
    Returns:
        Dictionary with ecosystem metrics
    """
    result = {
        "category": "utilities",
        "maturity": "pre-stable",
        "dependencies_count": 0,
        "reverse_dependencies_count": 0,
        "contributor_count": 0,
        "release_frequency": 0.0,
        "issue_closure_rate": 0.0,
        "median_resolution_days": 0.0,
        "ecosystem_score": 5.0,
    }
    
    try:
        # 1. Category and maturity from metadata
        if crate_metadata:
            categories = crate_metadata.get("categories", [])
            if categories:
                result["category"] = categories[0] if isinstance(categories, list) else "utilities"
            
            version = crate_metadata.get("version", "0.0.0")
            if version and version[0] != "0":
                result["maturity"] = "stable"
            else:
                result["maturity"] = "pre-stable"
            
            dependencies = crate_metadata.get("dependencies", [])
            if isinstance(dependencies, list):
                result["dependencies_count"] = len(dependencies)
        
        # 2. Reverse dependencies - try lib.rs scraped content first, then API
        reverse_deps = 0
        if sanitized_documentation:
            reverse_deps = _parse_reverse_deps_from_librs(sanitized_documentation)
        
        if reverse_deps == 0:
            reverse_deps = await _fetch_reverse_dependencies(crate_name)
        result["reverse_dependencies_count"] = reverse_deps
        
        # 3. GitHub metrics (contributors, releases, issues)
        github_path = None
        if repository_url:
            parsed = urlparse(repository_url)
            if "github.com" in parsed.netloc:
                path_parts = parsed.path.strip("/").split("/")
                if len(path_parts) >= 2:
                    github_path = f"{path_parts[0]}/{path_parts[1]}"
        
        if github_path:
            github_metrics = await _fetch_github_ecosystem_metrics(
                github_path, github_token
            )
            result.update(github_metrics)
        
        # 4. Compute ecosystem score (0-10)
        ecosystem_score = _compute_ecosystem_score(result)
        result["ecosystem_score"] = round(ecosystem_score, 2)
        
    except Exception as e:
        log.error(f"Ecosystem analysis error for {crate_name}: {e}")
        result["error"] = str(e)
    
    return result


def _parse_reverse_deps_from_librs(sanitized_documentation: Dict[str, Any]) -> int:
    """Parse reverse dependency count from lib.rs scraped content."""
    import re
    
    lib_rs_data = sanitized_documentation.get("lib_rs")
    if not lib_rs_data or not isinstance(lib_rs_data, dict):
        return 0
    
    content = lib_rs_data.get("content", "")
    if not content:
        return 0
    
    # Pattern 1: "Used in [**49,106** crates (34,205 directly)]" or "Used in **49,106** crates"
    # Handle both markdown link format [**XX** crates] and plain **XX** crates
    pattern1a = r'Used\s+in\s+\[?\*\*(\d+(?:,\d+)*)\*\*\s+crates?\s*(?:\([^)]+\))?\]?'
    match1a = re.search(pattern1a, content, re.IGNORECASE)
    if match1a:
        count_str = match1a.group(1).replace(',', '')
        try:
            count = int(count_str)
            log.debug(f"Found {count} reverse dependencies from lib.rs content (pattern 1a)")
            return count
        except ValueError:
            pass
    
    # Pattern 1b: Also try without markdown bold - "Used in 99,344 crates"
    pattern1b = r'Used\s+in\s+(?:\[)?(\d+(?:,\d+)*)\s+crates?\s*(?:\([^)]+\))?(?:\))?'
    match1b = re.search(pattern1b, content, re.IGNORECASE)
    if match1b:
        count_str = match1b.group(1).replace(',', '')
        try:
            count = int(count_str)
            log.debug(f"Found {count} reverse dependencies from lib.rs content (pattern 1b)")
            return count
        except ValueError:
            pass
    
    # Pattern 2: "**XX,XXX** crates depend on" or "XX crates depend on"
    pattern2 = r'\*\*(\d+(?:,\d+)*)\*\*\s+crates?\s+depend\s+on|(\d+(?:,\d+)*)\s+crates?\s+depend\s+on'
    match2 = re.search(pattern2, content, re.IGNORECASE)
    if match2:
        count_str = (match2.group(1) or match2.group(2)).replace(',', '')
        try:
            count = int(count_str)
            log.debug(f"Found {count} reverse dependencies from lib.rs content (pattern 2)")
            return count
        except ValueError:
            pass
    
    # Pattern 3: Look for numbers followed by "crates" near "depend" or "rev"
    pattern3 = r'(\d+(?:,\d+)*)\s+crates?\s*(?:\([^)]+\))?\s*(?:depend|rev|reverse)'
    match3 = re.search(pattern3, content, re.IGNORECASE)
    if match3:
        count_str = match3.group(1).replace(',', '')
        try:
            count = int(count_str)
            log.debug(f"Found {count} reverse dependencies from lib.rs content (pattern 3)")
            return count
        except ValueError:
            pass
    
    return 0


async def _fetch_reverse_dependencies(crate_name: str) -> int:
    """Fetch reverse dependency count from crates.io."""
    timeout = aiohttp.ClientTimeout(total=15)
    
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Crates.io doesn't have a direct reverse deps endpoint in v1 API
            # We need to scrape the web page or use the reverse dependencies endpoint
            # Try the reverse dependencies API endpoint first (if available)
            reverse_deps_url = f"https://crates.io/api/v1/crates/{crate_name}/reverse_dependencies"
            
            try:
                async with session.get(reverse_deps_url, params={"per_page": 1}) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        # The API returns paginated results with total count
                        meta = data.get("meta", {})
                        total = meta.get("total", 0)
                        if total > 0:
                            log.debug(f"Found {total} reverse dependencies for {crate_name} via API")
                            return total
            except Exception as api_error:
                log.debug(f"Reverse deps API failed for {crate_name}: {api_error}, trying web scraping")
            
            # Fallback: Try to scrape the web page for reverse dependency count
            # The crates.io page shows reverse dependencies with a count
            web_url = f"https://crates.io/crates/{crate_name}/reverse_dependencies"
            try:
                async with session.get(web_url, headers={"User-Agent": "SigilDERG-Data-Production/4.1.0"}) as resp:
                    if resp.status == 200:
                        html = await resp.text(encoding='utf-8')
                        # Look for patterns like "X crates depend on this"
                        import re
                        # Pattern 1: "X crates depend on"
                        match = re.search(r'(\d+(?:,\d+)*)\s+crates?\s+depend\s+on', html, re.IGNORECASE)
                        if match:
                            count_str = match.group(1).replace(',', '')
                            count = int(count_str)
                            log.debug(f"Found {count} reverse dependencies for {crate_name} via web scraping")
                            return count
                        # Pattern 2: Look for data attributes or JSON in page
                        # Some pages have reverse_deps_count in JSON-LD or data attributes
                        json_match = re.search(r'"reverse_deps_count"\s*:\s*(\d+)', html)
                        if json_match:
                            count = int(json_match.group(1))
                            log.debug(f"Found {count} reverse dependencies for {crate_name} via JSON in page")
                            return count
            except Exception as scrape_error:
                log.debug(f"Web scraping failed for {crate_name}: {scrape_error}")
            
            # If all methods fail, return 0
            log.warning(f"Could not fetch reverse dependencies for {crate_name}, returning 0")
            return 0
            
    except Exception as e:
        log.warning(f"Failed to fetch reverse dependencies for {crate_name}: {e}")
        return 0


async def _fetch_github_ecosystem_metrics(
    github_path: str, github_token: Optional[str] = None
) -> Dict[str, Any]:
    """Fetch GitHub metrics: contributors, releases, issue activity."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    
    timeout = aiohttp.ClientTimeout(total=10)
    result = {
        "contributor_count": 0,
        "release_frequency": 0.0,
        "issue_closure_rate": 0.0,
        "median_resolution_days": 0.0,
    }
    
    try:
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            # Fetch contributors
            contributors_url = f"https://api.github.com/repos/{github_path}/contributors"
            async with session.get(contributors_url, params={"per_page": 100}) as resp:
                if resp.status == 200:
                    contributors = await resp.json()
                    result["contributor_count"] = len(contributors)
            
            # Fetch releases to compute frequency
            releases_url = f"https://api.github.com/repos/{github_path}/releases"
            async with session.get(releases_url, params={"per_page": 100}) as resp:
                if resp.status == 200:
                    releases = await resp.json()
                    if releases:
                        # Compute releases per year
                        if len(releases) > 1:
                            first_release = datetime.fromisoformat(
                                releases[-1]["published_at"].replace("Z", "+00:00")
                            )
                            last_release = datetime.fromisoformat(
                                releases[0]["published_at"].replace("Z", "+00:00")
                            )
                            days_diff = (last_release - first_release).days
                            if days_diff > 0:
                                result["release_frequency"] = (
                                    len(releases) / days_diff * 365
                                )
            
            # Fetch issues to compute closure rate
            issues_url = f"https://api.github.com/repos/{github_path}/issues"
            async with session.get(
                issues_url, params={"state": "all", "per_page": 100}
            ) as resp:
                if resp.status == 200:
                    issues = await resp.json()
                    closed_count = sum(1 for issue in issues if issue.get("state") == "closed")
                    total_count = len(issues)
                    if total_count > 0:
                        result["issue_closure_rate"] = closed_count / total_count
                        
                        # Compute median resolution time from closed issues
                        closed_issues = [
                            issue for issue in issues if issue.get("state") == "closed"
                        ]
                        if closed_issues:
                            resolution_times = []
                            for issue in closed_issues:
                                created_at = issue.get("created_at")
                                closed_at = issue.get("closed_at")
                                if created_at and closed_at:
                                    try:
                                        created = datetime.fromisoformat(
                                            created_at.replace("Z", "+00:00")
                                        )
                                        closed = datetime.fromisoformat(
                                            closed_at.replace("Z", "+00:00")
                                        )
                                        days = (closed - created).days
                                        if days >= 0:  # Only count valid resolutions
                                            resolution_times.append(days)
                                    except (ValueError, AttributeError):
                                        continue
                            
                            if resolution_times:
                                # Calculate median
                                sorted_times = sorted(resolution_times)
                                mid = len(sorted_times) // 2
                                if len(sorted_times) % 2 == 0:
                                    median = (sorted_times[mid - 1] + sorted_times[mid]) / 2.0
                                else:
                                    median = float(sorted_times[mid])
                                result["median_resolution_days"] = median
                            else:
                                result["median_resolution_days"] = 0.0
                            
    except Exception as e:
        log.warning(f"Failed to fetch GitHub ecosystem metrics: {e}")
    
    return result


def _compute_ecosystem_score(metrics: Dict[str, Any]) -> float:
    """
    Compute ecosystem score (0-10) using weighted metrics.
    
    Primary weights:
    - Reverse dependencies: 40%
    - Contributors: 20%
    - Release frequency: 15%
    - Issue closure rate: 15%
    - Maturity: 10%
    """
    score = 0.0
    
    # Reverse dependencies (normalize: assume 1000+ is excellent)
    reverse_deps = metrics.get("reverse_dependencies_count", 0)
    reverse_deps_score = min(1.0, reverse_deps / 1000.0) * 0.40
    score += reverse_deps_score
    
    # Contributors (normalize: assume 50+ is excellent)
    contributors = metrics.get("contributor_count", 0)
    contributors_score = min(1.0, contributors / 50.0) * 0.20
    score += contributors_score
    
    # Release frequency (normalize: assume 6+ per year is excellent)
    release_freq = metrics.get("release_frequency", 0.0)
    release_score = min(1.0, release_freq / 6.0) * 0.15
    score += release_score
    
    # Issue closure rate (already 0-1)
    closure_rate = metrics.get("issue_closure_rate", 0.0)
    closure_score = closure_rate * 0.15
    score += closure_score
    
    # Maturity (stable = 1.0, pre-stable = 0.5)
    maturity = metrics.get("maturity", "pre-stable")
    maturity_score = 1.0 if maturity == "stable" else 0.5
    score += maturity_score * 0.10
    
    return score * 10.0  # Scale to 0-10

