"""
Crate environment detection and preparation.

Extracted from crate_analysis.py to reduce file size and improve maintainability.
"""

import logging
import os
import platform
import sys
from typing import Any, Dict

import toml


def detect_platform_info() -> Dict[str, Any]:
    """Detect comprehensive platform information for feature filtering."""
    info = {
        "os": platform.system().lower(),  # 'windows', 'linux', 'darwin'
        "os_family": None,
        "arch": platform.machine().lower(),
        "python_platform": sys.platform,
        "is_windows": platform.system().lower() == "windows",
        "is_linux": platform.system().lower() == "linux",
        "is_macos": platform.system().lower() == "darwin",
        "is_unix": platform.system().lower()
        in ["linux", "darwin", "freebsd", "openbsd"],
        "target_triple": None,
        "supported_features": set(),
        "excluded_patterns": [],
    }

    # Determine OS family for Rust cfg
    if info["is_windows"]:
        info["os_family"] = "windows"
        info["target_triple"] = "x86_64-pc-windows-msvc"
        info["excluded_patterns"] = [
            # Unix/Linux specific
            "unix",
            "linux",
            "android",
            "freebsd",
            "openbsd",
            "netbsd",
            "dragonfly",
            "epoll",
            "inotify",
            "kqueue",
            "timerfd",
            "signalfd",
            "pidfd",
            # macOS specific
            "macos",
            "darwin",
            "ios",
            "apple",
            # Architecture specific that might not be available
            "simd-accel",
            "neon",
            "avx512",
            "sse4",
        ]
    elif info["is_linux"]:
        info["os_family"] = "unix"
        info["target_triple"] = "x86_64-unknown-linux-gnu"
        info["excluded_patterns"] = [
            # Windows specific
            "windows",
            "winapi",
            "win32",
            "wepoll",
            "iocp",
            # macOS specific
            "macos",
            "darwin",
            "ios",
            "apple",
            # Architecture specific that might not be available
            "neon",
            "avx512",
        ]
    elif info["is_macos"]:
        info["os_family"] = "unix"
        info["target_triple"] = "x86_64-apple-darwin"
        info["excluded_patterns"] = [
            # Windows specific
            "windows",
            "winapi",
            "win32",
            "wepoll",
            "iocp",
            # Linux specific
            "linux",
            "android",
            "epoll",
            "inotify",
            "timerfd",
            "signalfd",
            # Architecture specific that might not be available
            "avx512",
        ]

    # Add universal safe features
    info["supported_features"] = {
        "default",
        "std",
        "alloc",
        "core",
        "no_std",
        "serde",
        "json",
        "derive",
        "macros",
        "proc-macro",
        "async",
        "tokio",
        "futures",
        "async-std",
        "http",
        "https",
        "tls",
        "ssl",
        "openssl",
        "rustls",
        "compress",
        "compression",
        "gzip",
        "deflate",
        "brotli",
        "zstd",
        "cookies",
        "secure-cookies",
        "session",
        "logging",
        "log",
        "tracing",
        "metrics",
        "testing",
        "test",
        "dev",
        "bench",
        "benchmark",
        "cli",
        "clap",
        "structopt",
        "config",
        "toml",
        "yaml",
        "env",
        "uuid",
        "chrono",
        "time",
        "rand",
        "regex",
        "parking_lot",
        "once_cell",
        "lazy_static",
    }

    logger = logging.getLogger(__name__)
    logger.info(
        "Platform detected: %s (%s) - excluding %d feature patterns",
        info["os"],
        info["target_triple"],
        len(info["excluded_patterns"]),
    )
    return info


def prepare_crate_environment(crate_source_path: str) -> Dict[str, Any]:
    """Prepare the crate environment and return detailed environment info."""
    logger = logging.getLogger(__name__)
    env_info = {
        "has_cargo_toml": False,
        "crate_name": "unknown",
        "crate_type": "unknown",
        "has_dependencies": False,
        "has_dev_dependencies": False,
        "has_build_script": False,
        "workspace_member": False,
        "features": [],
        "rust_version": None,
        "edition": "2015",  # default
        "preparation_notes": [],
    }

    try:
        cargo_toml_path = os.path.join(crate_source_path, "Cargo.toml")

        if os.path.exists(cargo_toml_path):
            env_info["has_cargo_toml"] = True

            try:
                with open(cargo_toml_path, "r") as f:
                    cargo_config = toml.load(f)

                # Extract detailed crate information
                if "package" in cargo_config:
                    package = cargo_config["package"]
                    env_info["crate_name"] = package.get("name", "unknown")
                    env_info["edition"] = package.get("edition", "2015")
                    env_info["rust_version"] = package.get("rust-version")

                    # Determine crate type
                    if "lib" in cargo_config:
                        env_info["crate_type"] = "library"
                    elif "bin" in cargo_config or package.get("default-run"):
                        env_info["crate_type"] = "binary"
                    else:
                        env_info["crate_type"] = "mixed"

                # Check dependencies
                env_info["has_dependencies"] = bool(
                    cargo_config.get("dependencies")
                )
                env_info["has_dev_dependencies"] = bool(
                    cargo_config.get("dev-dependencies")
                )
                env_info["has_build_script"] = bool(
                    cargo_config.get("build-dependencies")
                    or os.path.exists(
                        os.path.join(crate_source_path, "build.rs")
                    )
                )

                # Extract features
                if "features" in cargo_config:
                    env_info["features"] = list(cargo_config["features"].keys())

                # Check if it's a workspace member
                env_info["workspace_member"] = bool(cargo_config.get("workspace"))

                logger.info(
                    f"Crate environment prepared: {env_info['crate_name']} ({env_info['crate_type']}, edition {env_info['edition']})"
                )

            except Exception as e:
                env_info["preparation_notes"].append(
                    f"Failed to parse Cargo.toml: {e}"
                )
                logger.warning("Cargo.toml parsing failed: %s", e)
        else:
            env_info["preparation_notes"].append("No Cargo.toml found")
            logger.warning("No Cargo.toml found in %s", crate_source_path)

    except (OSError, ValueError, KeyError) as e:
        env_info["preparation_notes"].append(f"Environment preparation failed: {e}")
        logger.error("Failed to prepare crate environment: %s", e)

    return env_info


def prepare_crate_for_analysis(crate_source_path: str) -> bool:
    """Prepare the downloaded crate for analysis by ensuring it has a proper project structure."""
    logger = logging.getLogger(__name__)
    try:
        cargo_toml_path = os.path.join(crate_source_path, "Cargo.toml")

        # Check if Cargo.toml exists
        if not os.path.exists(cargo_toml_path):
            logger.warning(f"No Cargo.toml found in {crate_source_path}")
            return False

        # Check if we can read the Cargo.toml
        try:
            with open(cargo_toml_path, "r") as f:
                cargo_config = toml.load(f)

            # Verify this is a valid package
            if "package" not in cargo_config:
                logger.warning(
                    f"Cargo.toml missing [package] section in {crate_source_path}"
                )
                return False

            logger.info(
                f"Crate {cargo_config['package'].get('name', 'unknown')} prepared for analysis"
            )
            return True

        except Exception as e:
            logger.error("Failed to parse Cargo.toml: %s", e)
            return False

    except Exception as e:
        logger.error("Failed to prepare crate for analysis: %s", e)
        return False

