# network.py
import asyncio
import logging
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Union

import aiohttp
import requests

try:
    from bs4 import BeautifulSoup, Tag
    BS4_AVAILABLE = True
except ImportError:
    BeautifulSoup = None
    Tag = None
    BS4_AVAILABLE = False

from .config import PipelineConfig, DEFAULT_HTTP_TIMEOUT
from .exceptions import ValidationError as PipelineValidationError
from .utils.validation import validate_crate_name


class GitHubBatchClient:
    def __init__(self, config: PipelineConfig) -> None:
        self.config = config
        # Simple headers without dependency on HTTPClientUtils
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "SigilDERG-Data-Production/1.3.2",
        }
        if config.github_token:
            self.headers["Authorization"] = f"token {config.github_token}"

        self.remaining_calls = 5000
        self.reset_time = 0
        self._lock = threading.Lock()
        # Use thread-local storage for session to ensure thread-safety
        self._local = threading.local()

    def _get_session(self) -> requests.Session:
        """Get a thread-local session."""
        if not hasattr(self._local, "session"):
            self._local.session = requests.Session()
        return self._local.session

    def cleanup(self) -> None:
        """Clean up thread-local sessions."""
        if hasattr(self._local, "session"):
            self._local.session.close()
            delattr(self._local, "session")

    def __enter__(self) -> "GitHubBatchClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit with cleanup."""
        self.cleanup()
        return False

    async def check_rate_limit_async(self) -> None:
        """Async version: Check and update current rate limit status"""
        try:
            timeout = getattr(self.config, "http_timeout", DEFAULT_HTTP_TIMEOUT)
            timeout_obj = aiohttp.ClientTimeout(total=timeout)
            async with aiohttp.ClientSession(timeout=timeout_obj, headers=self.headers) as session:
                async with session.get("https://api.github.com/rate_limit") as response:
                    if response.status == 200:
                        data = await response.json()
                        with self._lock:
                            self.remaining_calls = data["resources"]["core"]["remaining"]
                            self.reset_time = data["resources"]["core"]["reset"]

                        if self.remaining_calls < 100:
                            reset_in = self.reset_time - time.time()
                            logging.warning(
                                "GitHub API rate limit low: %d remaining. Resets in %.1f minutes",
                                self.remaining_calls,
                                reset_in / 60,
                            )
        except (aiohttp.ClientError, asyncio.TimeoutError, KeyError, ValueError) as e:
            logging.debug("Rate limit check failed: %s", e)
            pass

    def check_rate_limit(self) -> None:
        """
        Synchronous wrapper for async rate limit check.
        
        For backward compatibility. Prefer check_rate_limit_async() in async contexts.
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.check_rate_limit_async())
                    future.result()
            else:
                loop.run_until_complete(self.check_rate_limit_async())
        except RuntimeError:
            asyncio.run(self.check_rate_limit_async())

    async def get_repo_stats_async(self, owner: str, repo: str) -> "dict[str, Any]":
        """Async version: Get repository statistics"""
        try:
            timeout = getattr(self.config, "http_timeout", DEFAULT_HTTP_TIMEOUT)
            timeout_obj = aiohttp.ClientTimeout(total=timeout)
            url = f"https://api.github.com/repos/{owner}/{repo}"
            async with aiohttp.ClientSession(timeout=timeout_obj, headers=self.headers) as session:
                async with session.get(url) as response:
                    headers = response.headers
                    if "X-RateLimit-Remaining" in headers:
                        with self._lock:
                            self.remaining_calls = int(headers.get("X-RateLimit-Remaining", "0"))
                            self.reset_time = int(headers.get("X-RateLimit-Reset", "0"))
                    if response.status == 200:
                        return await response.json()
                    logging.warning(
                        "Failed to get repo stats for %s/%s: %d",
                        owner,
                        repo,
                        response.status,
                    )
                    return {}
        except (aiohttp.ClientError, asyncio.TimeoutError, KeyError, ValueError) as e:
            logging.error("Error fetching repo stats: %s", e)
            return {}

    def get_repo_stats(self, owner: str, repo: str) -> "dict[str, Any]":
        """
        Synchronous wrapper for async repo stats fetch.
        
        For backward compatibility. Prefer get_repo_stats_async() in async contexts.
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run, self.get_repo_stats_async(owner, repo)
                    )
                    return future.result()
            else:
                return loop.run_until_complete(self.get_repo_stats_async(owner, repo))
        except RuntimeError:
            return asyncio.run(self.get_repo_stats_async(owner, repo))

    async def batch_get_repo_stats_async(
        self, repo_list: "list[str]"
    ) -> "dict[str, dict[str, Any]]":
        """Async version: Get statistics for multiple repositories concurrently"""
        await self.check_rate_limit_async()

        results: "dict[str, dict[str, Any]]" = {}
        remaining = list(repo_list)
        while remaining:
            # Check and update rate limit atomically
            with self._lock:
                allowed = self.remaining_calls
                if allowed <= 0:
                    sleep_for = max(self.reset_time - time.time(), 0)
                    if sleep_for > 0:
                        logging.warning(
                            "GitHub API rate limit reached. Sleeping for %.0f seconds",
                            sleep_for,
                        )
                    # Release lock before sleeping (exit context manager)
                else:
                    # Reserve calls for this batch
                    batch_size = min(allowed, len(remaining))
                    self.remaining_calls -= batch_size
                    # Lock will be released when exiting context manager
            
            # Sleep outside the lock if needed
            if allowed <= 0:
                if sleep_for > 0:
                    await asyncio.sleep(sleep_for)
                await self.check_rate_limit_async()
                continue

            # Process batch outside the lock using async gather
            batch = remaining[:batch_size]
            remaining = remaining[batch_size:]

            async def fetch(repo_url: str) -> tuple[str, dict[str, Any]]:
                match = re.search(r"github\.com/([^/]+)/([^/\.]+)", repo_url)
                if not match:
                    return repo_url, {}
                owner, repo = match.groups()
                repo = repo.split(".")[0]
                stats = await self.get_repo_stats_async(owner, repo)
                return repo_url, stats

            # Use asyncio.gather for concurrent async requests
            tasks = [fetch(url) for url in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in batch_results:
                if isinstance(result, Exception):
                    logging.warning(f"Error fetching repo stats: {result}")
                    continue
                repo_url, stats = result
                results[repo_url] = stats

        return results

    def batch_get_repo_stats(
        self, repo_list: "list[str]"
    ) -> "dict[str, dict[str, Any]]":
        """
        Synchronous wrapper for async batch repo stats fetch.
        
        For backward compatibility. Prefer batch_get_repo_stats_async() in async contexts.
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run, self.batch_get_repo_stats_async(repo_list)
                    )
                    return future.result()
            else:
                return loop.run_until_complete(self.batch_get_repo_stats_async(repo_list))
        except RuntimeError:
            return asyncio.run(self.batch_get_repo_stats_async(repo_list))


class CrateAPIClient:
    def __init__(self, config: PipelineConfig) -> None:
        self.config = config
        # Simple session without dependency on HTTPClientUtils
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "SigilDERG-Data-Production/1.3.2"})
        self.timeout = getattr(config, "http_timeout", DEFAULT_HTTP_TIMEOUT)

    def __enter__(self) -> "CrateAPIClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit with cleanup."""
        self.session.close()
        return False

    async def fetch_crate_metadata_async(self, crate_name: str) -> "dict[str, Any] | None":
        """Async version: Fetch metadata with retry logic"""
        # Validate crate name
        crate_name = validate_crate_name(crate_name)
        for attempt in range(self.config.max_retries):
            try:
                return await self._fetch_metadata_async(crate_name)
            except (aiohttp.ClientError, asyncio.TimeoutError, KeyError, ValueError) as e:
                logging.warning(
                    "Attempt %d failed for %s: %s", attempt + 1, crate_name, e
                )
                wait = 2**attempt
                await asyncio.sleep(wait)
        return None

    def fetch_crate_metadata(self, crate_name: str) -> "dict[str, Any] | None":
        """
        Synchronous wrapper for async metadata fetch.
        
        For backward compatibility. Prefer fetch_crate_metadata_async() in async contexts.
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run, self.fetch_crate_metadata_async(crate_name)
                    )
                    return future.result()
            else:
                return loop.run_until_complete(self.fetch_crate_metadata_async(crate_name))
        except RuntimeError:
            return asyncio.run(self.fetch_crate_metadata_async(crate_name))

    async def _fetch_metadata_async(self, crate_name: str) -> "dict[str, Any] | None":
        """Async version: Enhanced metadata fetching that tries multiple sources"""
        timeout_obj = aiohttp.ClientTimeout(total=self.timeout)
        headers = {"User-Agent": "SigilDERG-Data-Production/1.3.2"}
        
        # First try crates.io (primary source)
        try:
            async with aiohttp.ClientSession(timeout=timeout_obj, headers=headers) as session:
                async with session.get(f"https://crates.io/api/v1/crates/{crate_name}") as r:
                    if r.status == 200:
                        data = await r.json()
                        crate_data = data["crate"]
                        latest = crate_data["newest_version"]

                        # Get readme, dependencies, and features concurrently
                        readme_url = f"https://crates.io/api/v1/crates/{crate_name}/readme"
                        deps_url = f"https://crates.io/api/v1/crates/{crate_name}/{latest}/dependencies"
                        versions_url = f"https://crates.io/api/v1/crates/{crate_name}/{latest}"
                        
                        readme_resp, deps_resp, versions_resp = await asyncio.gather(
                            session.get(readme_url),
                            session.get(deps_url),
                            session.get(versions_url),
                            return_exceptions=True
                        )
                        
                        readme = ""
                        if isinstance(readme_resp, aiohttp.ClientResponse) and readme_resp.status == 200:
                            readme = await readme_resp.text()
                        
                        deps: list[dict[str, Any]] = []
                        if isinstance(deps_resp, aiohttp.ClientResponse) and deps_resp.status == 200:
                            deps_data = await deps_resp.json()
                            deps = deps_data.get("dependencies", [])
                        
                        features = []
                        downloads = 0
                        # First, try to get total downloads from the crate object (this is the total for all versions)
                        downloads = crate_data.get("downloads", 0)
                        
                        license_value = None
                        if isinstance(versions_resp, aiohttp.ClientResponse) and versions_resp.status == 200:
                            version_data = await versions_resp.json()
                            version_obj = version_data.get("version", {})
                            features_dict = version_obj.get("features", {})
                            features = [{"name": k, "dependencies": v} for k, v in features_dict.items()]
                            # If crate-level downloads is 0, try version-level as fallback
                            # Note: version downloads are per-version, not total, so prefer crate total
                            if downloads == 0:
                                downloads = version_obj.get("downloads", 0)
                            # Try to get license from version object if not in crate object
                            license_value = version_obj.get("license")

                        # Prefer crate-level license, fallback to version-level
                        if not license_value:
                            license_value = crate_data.get("license")

                        # Repository info and GitHub stars
                        repo = crate_data.get("repository", "")
                        gh_stars = 0

                        # Check if it's a GitHub repo
                        if "github.com" in repo and self.config.github_token:
                            match = re.search(r"github.com/([^/]+)/([^/]+)", repo)
                            if match:
                                owner, repo_name = match.groups()
                                repo_name = repo_name.split(".")[0]
                                gh_url = f"https://api.github.com/repos/{owner}/{repo_name}"
                                gh_headers = {"Authorization": f"token {self.config.github_token}"}
                                async with session.get(gh_url, headers=gh_headers) as gh:
                                    if gh.status == 200:
                                        gh_data = await gh.json()
                                        gh_stars = gh_data.get("stargazers_count", 0)

                        # Check if it's hosted on lib.rs
                        lib_rs_data = {}
                        if "lib.rs" in repo:
                            lib_rs_url = f"https://lib.rs/crates/{crate_name}"
                            async with session.get(lib_rs_url) as lib_rs_response:
                                if lib_rs_response.status == 200:
                                    html_text = await lib_rs_response.text()
                                    soup = BeautifulSoup(html_text, "html.parser")
                                    if not readme:
                                        readme_div = soup.find("div", class_="readme")
                                        if readme_div:
                                            readme = readme_div.get_text(strip=True)
                                    stats_div = soup.find("div", class_="crate-stats")
                                    if isinstance(stats_div, Tag):
                                        downloads_text = stats_div.find(string=re.compile(r"[\d,]+ downloads"))
                                        if downloads_text:
                                            lib_rs_data["librs_downloads"] = int(re.sub(r"[^\d]", "", str(downloads_text)))

                        # Extract code snippets and sections (simplified)
                        code_snippets: list[str] = []
                        readme_sections: dict[str, str] = {}

                        result: dict[str, Any] = {
                            "name": crate_name,
                            "version": latest,
                            "description": crate_data.get("description", ""),
                            "repository": repo,
                            "keywords": crate_data.get("keywords", []),
                            "categories": crate_data.get("categories", []),
                            "readme": readme,
                            "downloads": downloads,
                            "github_stars": gh_stars,
                            "dependencies": deps,
                            "code_snippets": code_snippets,
                            "features": features_dict,
                            "readme_sections": readme_sections,
                            "license": license_value,  # SPDX license expression (from crate or version)
                            **lib_rs_data,
                        }
                        return result

        except (aiohttp.ClientError, asyncio.TimeoutError, KeyError, ValueError) as e:
            logging.error("Failed fetching metadata for %s: %s", crate_name, e)
            # Continue to fallback sources

        # If crates.io fails, try lib.rs
        try:
            async with aiohttp.ClientSession(timeout=timeout_obj, headers=headers) as session:
                async with session.get(f"https://lib.rs/crates/{crate_name}") as r:
                    if r.status == 200:
                        html_text = await r.text()
                        soup = BeautifulSoup(html_text, "html.parser")

                        h1 = soup.select_one("h1")
                        name = h1.text.strip() if h1 else crate_name
                        desc_elem = soup.select_one(".description")
                        description = desc_elem.text.strip() if desc_elem else ""
                        repo_link: Union[str, None] = None
                        for a in soup.select("a"):
                            href = a.get("href")
                            if href and isinstance(href, str) and "github.com" in href:
                                repo_link = href
                                break
                        keywords_elem = soup.select_one(".keywords")
                        keywords = (
                            [k.text.strip() for k in keywords_elem.find_all("a")]
                            if keywords_elem
                            else []
                        )
                        return {
                            "name": name,
                            "version": "latest",
                            "description": description,
                            "repository": repo_link or "",
                            "keywords": keywords,
                            "categories": [],
                            "readme": "",
                            "downloads": 0,
                            "github_stars": 0,
                            "dependencies": [],
                            "code_snippets": [],
                            "features": [],
                            "readme_sections": {},
                            "source": "lib.rs",
                        }
        except (aiohttp.ClientError, asyncio.TimeoutError, KeyError, AttributeError):
            pass

        # Finally, try GitHub search
        if self.config.github_token:
            try:
                gh_search_headers = {"Authorization": f"token {self.config.github_token}"}
                search_url = f"https://api.github.com/search/repositories?q={crate_name}+language:rust"
                async with aiohttp.ClientSession(timeout=timeout_obj, headers=gh_search_headers) as session:
                    async with session.get(search_url) as r:
                        if r.status == 200:
                            search_data = await r.json()
                            results = search_data.get("items", [])
                            if results:
                                repo = results[0]
                                return {
                                    "name": crate_name,
                                    "version": "unknown",
                                    "description": repo.get("description", ""),
                                    "repository": repo.get("html_url", ""),
                                    "keywords": [],
                                    "categories": [],
                                    "readme": "",
                                    "downloads": 0,
                                    "github_stars": repo.get("stargazers_count", 0),
                                    "dependencies": [],
                                    "code_snippets": [],
                                    "features": [],
                                    "readme_sections": {},
                                    "source": "github",
                                }
            except (aiohttp.ClientError, asyncio.TimeoutError, KeyError, ValueError):
                pass

        # If all sources fail
        return None

