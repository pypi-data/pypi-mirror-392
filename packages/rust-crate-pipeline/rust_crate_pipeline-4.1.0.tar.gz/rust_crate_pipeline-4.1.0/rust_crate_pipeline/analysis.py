# analysis.py
from __future__ import annotations

import io
import logging
import os
import re
import asyncio
import subprocess
import tarfile
import tempfile
import time
from typing import Any

import aiohttp

from .config import EnrichedCrate
from .utils.http_session import get_with_retry
from .utils.rust_code_analyzer import RustCodeAnalyzer


# Constants for URLs and paths
CRATES_IO_API_URL = "https://crates.io/api/v1/crates"
GITHUB_API_URL = "https://api.github.com/repos"
LIB_RS_URL = "https://lib.rs/crates"


class SourceAnalyzer:
    @staticmethod
    async def analyze_crate_source_async(crate: EnrichedCrate) -> dict[str, Any]:
        """Async version: Orchestrate source analysis from multiple sources."""
        repo_url = crate.repository

        attempted_sources = []
        # Method 1: Try to download from crates.io
        try:
            attempted_sources.append("crates.io")
            url = f"{CRATES_IO_API_URL}/{crate.name}/{crate.version}/download"
            
            # Use async HTTP
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    content = await response.read()
                    logging.info(f"Successfully downloaded {crate.name} from crates.io")
                    return SourceAnalyzer.analyze_crate_tarball(content)
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logging.warning(f"Failed to download from crates.io: {e}")

        # Method 2: Try GitHub if we have a GitHub URL
        if repo_url and "github.com" in repo_url:
            attempted_sources.append("github")
            match = re.search(r"github\.com/([^/]+)/([^/]+)", repo_url)
            if match:
                owner, repo_name = match.groups()
                repo_name = repo_name.replace(".git", "")
                try:
                    github_url = f"{GITHUB_API_URL}/{owner}/{repo_name}/tarball"
                    timeout = aiohttp.ClientTimeout(total=30)
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.get(github_url) as response:
                            response.raise_for_status()
                            content = await response.read()
                            logging.info(f"Successfully downloaded {crate.name} from GitHub")
                            return SourceAnalyzer.analyze_github_tarball(content)
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    logging.warning(f"Failed to analyze from GitHub: {e}")

        # Method 3: Fallback to cloning from the repository directly
        if repo_url:
            attempted_sources.append("git_clone")
            try:
                logging.info(f"Attempting to clone repository for {crate.name}")
                return await SourceAnalyzer.analyze_crate_source_from_repo_async(repo_url)
            except Exception as e:
                logging.error(f"Failed to clone and analyze repository {repo_url}: {e}")

        return {
            "error": "Could not analyze crate from any available source.",
            "attempted_sources": attempted_sources,
            "file_count": 0,
            "loc": 0,
        }

    @staticmethod
    def analyze_crate_source(crate: EnrichedCrate) -> dict[str, Any]:
        """
        Synchronous wrapper for async source analysis.
        
        For backward compatibility. Prefer analyze_crate_source_async() in async contexts.
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, we need to use a different approach
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run, SourceAnalyzer.analyze_crate_source_async(crate)
                    )
                    return future.result()
            else:
                return loop.run_until_complete(SourceAnalyzer.analyze_crate_source_async(crate))
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(SourceAnalyzer.analyze_crate_source_async(crate))

    @staticmethod
    def _analyze_tarball_content(content: bytes) -> dict[str, Any]:
        """Shared logic to analyze tarball content from any source."""
        metrics = RustCodeAnalyzer.create_empty_metrics()
        try:
            with io.BytesIO(content) as tar_content, tarfile.open(
                fileobj=tar_content, mode="r:gz"
            ) as tar:
                rust_files = [f for f in tar.getnames() if f.endswith(".rs")]
                metrics["file_count"] = len(rust_files)
                structure = RustCodeAnalyzer.detect_project_structure(tar.getnames())

                for member in tar.getmembers():
                    if member.isfile() and member.name.endswith(".rs"):
                        file_content = tar.extractfile(member)
                        if file_content:
                            try:
                                content_str = file_content.read().decode("utf-8")
                                analysis = RustCodeAnalyzer.analyze_rust_content(
                                    content_str
                                )
                                metrics = RustCodeAnalyzer.aggregate_metrics(
                                    metrics, analysis, structure
                                )
                            except UnicodeDecodeError:
                                logging.warning(
                                    f"Skipping non-UTF-8 file: {member.name}"
                                )
        except tarfile.TarError as e:
            metrics["error"] = f"Failed to read tarball: {e}"
            logging.error(metrics["error"])
        return metrics

    @staticmethod
    def analyze_crate_tarball(content: bytes) -> dict[str, Any]:
        """Analyze a .crate tarball from crates.io."""
        return SourceAnalyzer._analyze_tarball_content(content)

    @staticmethod
    def analyze_github_tarball(content: bytes) -> dict[str, Any]:
        """Analyze a GitHub tarball."""
        return SourceAnalyzer._analyze_tarball_content(content)

    @staticmethod
    async def download_crate(crate: Any, extract_dir: str) -> str:
        """Download a crate's source code and extract it to the given directory."""
        repo_url = getattr(crate, "repository", None)

        async def _extract(content: bytes) -> str:
            def extract() -> str:
                with io.BytesIO(content) as tar_content:
                    with tarfile.open(fileobj=tar_content, mode="r:gz") as tar:
                        members = tar.getmembers()
                        root = members[0].name.split("/")[0] if members else ""
                        tar.extractall(extract_dir)
                return os.path.join(extract_dir, root)

            return await asyncio.to_thread(extract)

        async with aiohttp.ClientSession() as session:
            # Try downloading from crates.io
            try:
                url = f"{CRATES_IO_API_URL}/{crate.name}/{crate.version}/download"
                async with session.get(url, timeout=30) as response:
                    response.raise_for_status()
                    content = await response.read()
                    return await _extract(content)
            except aiohttp.ClientError:
                pass

            # Try GitHub tarball if repository is on GitHub
            if repo_url and "github.com" in repo_url:
                match = re.search(r"github\.com/([^/]+)/([^/]+)", repo_url)
                if match:
                    owner, repo_name = match.groups()
                    repo_name = repo_name.replace(".git", "")
                    try:
                        github_url = f"{GITHUB_API_URL}/{owner}/{repo_name}/tarball"
                        async with session.get(github_url, timeout=30) as response:
                            response.raise_for_status()
                            content = await response.read()
                            return await _extract(content)
                    except aiohttp.ClientError:
                        pass

        # Fallback to cloning the repository directly
        if repo_url:
            proc = None
            try:
                proc = await asyncio.create_subprocess_exec(
                    "git",
                    "clone",
                    "--depth=1",
                    repo_url,
                    extract_dir,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)
                if proc.returncode != 0:
                    raise subprocess.CalledProcessError(
                        proc.returncode, proc.args, stdout, stderr
                    )
                return extract_dir
            except (subprocess.CalledProcessError, asyncio.TimeoutError) as e:
                logging.error(f"Failed to clone repository {repo_url}: {e}")
            finally:
                # Clean up subprocess to prevent transport warnings
                if proc:
                    from .utils.subprocess_utils import cleanup_subprocess
                    await cleanup_subprocess(proc, logging.getLogger(__name__))

        raise RuntimeError(f"Could not download source for {crate.name}")

    @staticmethod
    def analyze_local_directory(directory: str) -> dict[str, Any]:
        """Analyze source code from a local directory."""
        metrics = RustCodeAnalyzer.create_empty_metrics()
        try:
            rust_files: list[str] = []
            all_paths: list[str] = []
            for root, dirs, files in os.walk(directory):
                # Exclude target and .git directories
                dirs[:] = [d for d in dirs if d not in ["target", ".git"]]
                for file in files:
                    full_path = os.path.join(root, file)
                    all_paths.append(full_path)
                    if file.endswith(".rs"):
                        rust_files.append(full_path)

            metrics["file_count"] = len(rust_files)
            structure = RustCodeAnalyzer.detect_project_structure(all_paths)

            for file_path in rust_files:
                try:
                    with open(file_path, encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    analysis = RustCodeAnalyzer.analyze_rust_content(content)
                    metrics = RustCodeAnalyzer.aggregate_metrics(
                        metrics, analysis, structure
                    )
                except Exception as e:
                    logging.warning(f"Error analyzing file {file_path}: {e}")
        except Exception as e:
            metrics["error"] = f"Failed to analyze local directory {directory}: {e}"
            logging.error(metrics["error"])
        return metrics

    @staticmethod
    async def analyze_crate_source_from_repo_async(repo_url: str) -> dict[str, Any]:
        """Async version: Clone and analyze a crate's source code from a repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            proc = None
            try:
                logging.info(f"Cloning {repo_url} into {temp_dir}")
                proc = await asyncio.create_subprocess_exec(
                    "git",
                    "clone",
                    "--depth=1",
                    repo_url,
                    temp_dir,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)
                if proc.returncode != 0:
                    raise subprocess.CalledProcessError(
                        proc.returncode, proc.args, stdout, stderr
                    )
                return SourceAnalyzer.analyze_local_directory(temp_dir)
            except (
                subprocess.CalledProcessError,
                asyncio.TimeoutError,
            ) as e:
                error_output = str(e)
                logging.error(f"Failed to clone repository {repo_url}: {error_output}")
                return {
                    "error": f"Failed to clone repository: {error_output}",
                    "file_count": 0,
                    "loc": 0,
                }
            finally:
                # Clean up subprocess to prevent transport warnings
                if proc:
                    from .utils.subprocess_utils import cleanup_subprocess
                    await cleanup_subprocess(proc, logging.getLogger(__name__))


class SecurityAnalyzer:
    @staticmethod
    def check_security_metrics(crate: EnrichedCrate) -> dict[str, Any]:
        """Check security metrics for a crate (placeholder)."""
        security_data: dict[str, Any] = {
            "advisories": [],
            "vulnerability_count": 0,
            "cargo_audit": None,
            "unsafe_blocks": 0,
        }
        # In a real implementation, this would run tools like `cargo-audit`
        # and parse the output. For now, it remains a placeholder.
        logging.info(f"Running placeholder security check for {crate.name}")
        return security_data


class UserBehaviorAnalyzer:
    @staticmethod
    def _get_github_headers() -> dict[str, str]:
        """Get headers for GitHub API requests, including auth if available."""
        headers = {"Accept": "application/vnd.github.v3+json"}
        if token := os.environ.get("GITHUB_TOKEN"):
            headers["Authorization"] = f"token {token}"
        return headers

    @staticmethod
    async def fetch_user_behavior_data_async(crate: EnrichedCrate) -> dict[str, Any]:
        """Async version: Fetch user behavior data from GitHub and crates.io."""
        result: dict[str, Any] = {
            "issues": [],
            "pull_requests": [],
            "version_adoption": {},
            "community_metrics": {},
        }
        repo_url = crate.repository
        if not repo_url or "github.com" not in repo_url:
            return result

        match = re.search(r"github\.com/([^/]+)/([^/]+)", repo_url)
        if not match:
            return result
        owner, repo = match.groups()
        repo = repo.replace(".git", "")

        headers = UserBehaviorAnalyzer._get_github_headers()
        await UserBehaviorAnalyzer._fetch_github_activity_async(owner, repo, headers, result)
        await UserBehaviorAnalyzer._fetch_crates_io_versions_async(crate.name, result)

        return result

    @staticmethod
    def fetch_user_behavior_data(crate: EnrichedCrate) -> dict[str, Any]:
        """
        Synchronous wrapper for async user behavior data fetch.
        
        For backward compatibility. Prefer fetch_user_behavior_data_async() in async contexts.
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        UserBehaviorAnalyzer.fetch_user_behavior_data_async(crate)
                    )
                    return future.result()
            else:
                return loop.run_until_complete(
                    UserBehaviorAnalyzer.fetch_user_behavior_data_async(crate)
                )
        except RuntimeError:
            return asyncio.run(
                UserBehaviorAnalyzer.fetch_user_behavior_data_async(crate)
            )

    @staticmethod
    async def _fetch_github_activity_async(
        owner: str, repo: str, headers: dict[str, str], result: dict[str, Any]
    ) -> None:
        """Async version: Fetch issues, PRs, and commit activity from GitHub."""
        try:
            timeout = aiohttp.ClientTimeout(total=60)
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                # Fetch issues/PRs
                issues_url = f"{GITHUB_API_URL}/{owner}/{repo}/issues?state=all&per_page=30"
                async with session.get(issues_url) as issues_resp:
                    issues_resp.raise_for_status()
                    items = await issues_resp.json()

                    for item in items:
                        is_pr = "pull_request" in item
                        data_list = result["pull_requests"] if is_pr else result["issues"]
                        data_list.append(
                            {
                                "number": item["number"],
                                "title": item["title"],
                                "state": item["state"],
                                "created_at": item["created_at"],
                                "closed_at": item.get("closed_at"),
                                "url": item["html_url"],
                            }
                        )

                # Fetch commit activity (retries on 202)
                activity_url = f"{GITHUB_API_URL}/{owner}/{repo}/stats/commit_activity"
                for _ in range(3):  # Retry up to 3 times
                    async with session.get(activity_url) as activity_resp:
                        if activity_resp.status == 200:
                            result["community_metrics"]["commit_activity"] = await activity_resp.json()
                            break
                        elif activity_resp.status == 202:
                            logging.info(
                                f"GitHub is calculating stats for {owner}/{repo}, waiting..."
                            )
                            await asyncio.sleep(2)
                        else:
                            activity_resp.raise_for_status()

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logging.warning(f"Error fetching GitHub data for {owner}/{repo}: {e}")

    @staticmethod
    def _fetch_github_activity(
        owner: str, repo: str, headers: dict[str, str], result: dict[str, Any]
    ) -> None:
        """
        Synchronous wrapper for async GitHub activity fetch.
        
        For backward compatibility. Prefer _fetch_github_activity_async() in async contexts.
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        UserBehaviorAnalyzer._fetch_github_activity_async(owner, repo, headers, result)
                    )
                    future.result()
            else:
                loop.run_until_complete(
                    UserBehaviorAnalyzer._fetch_github_activity_async(owner, repo, headers, result)
                )
        except RuntimeError:
            asyncio.run(
                UserBehaviorAnalyzer._fetch_github_activity_async(owner, repo, headers, result)
            )

    @staticmethod
    async def _fetch_crates_io_versions_async(crate_name: str, result: dict[str, Any]) -> None:
        """Async version: Fetch version adoption data from crates.io."""
        try:
            versions_url = f"{CRATES_IO_API_URL}/{crate_name}/versions"
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(versions_url) as versions_resp:
                    versions_resp.raise_for_status()
                    versions_data = (await versions_resp.json()).get("versions", [])

                    for version in versions_data[:10]:  # Top 10 versions
                        result["version_adoption"][version["num"]] = {
                            "downloads": version["downloads"],
                            "created_at": version["created_at"],
                        }
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logging.warning(
                f"Error fetching crates.io version data for {crate_name}: {e}"
            )

    @staticmethod
    def _fetch_crates_io_versions(crate_name: str, result: dict[str, Any]) -> None:
        """
        Synchronous wrapper for async crates.io version fetch.
        
        For backward compatibility. Prefer _fetch_crates_io_versions_async() in async contexts.
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        UserBehaviorAnalyzer._fetch_crates_io_versions_async(crate_name, result)
                    )
                    future.result()
            else:
                loop.run_until_complete(
                    UserBehaviorAnalyzer._fetch_crates_io_versions_async(crate_name, result)
                )
        except RuntimeError:
            asyncio.run(
                UserBehaviorAnalyzer._fetch_crates_io_versions_async(crate_name, result)
            )


class DependencyAnalyzer:
    @staticmethod
    def analyze_dependencies(crates: list[EnrichedCrate]) -> dict[str, Any]:
        """Analyze dependencies within a given list of crates."""
        crate_names = {crate.name for crate in crates}
        dependency_graph: dict[str, list[str]] = {
            crate.name: [
                dep_id
                for dep in crate.dependencies
                if (dep_id := dep.get("crate_id")) and dep_id in crate_names
            ]
            for crate in crates
        }

        reverse_deps: dict[str, list[str]] = {}
        for crate_name, deps in dependency_graph.items():
            for dep in deps:
                if dep:  # Ensure dep is not None
                    reverse_deps.setdefault(dep, []).append(crate_name)

        most_depended = sorted(
            reverse_deps.items(), key=lambda item: len(item[1]), reverse=True
        )[:10]

        return {
            "dependency_graph": dependency_graph,
            "reverse_dependencies": reverse_deps,
            "most_depended": most_depended,
        }
