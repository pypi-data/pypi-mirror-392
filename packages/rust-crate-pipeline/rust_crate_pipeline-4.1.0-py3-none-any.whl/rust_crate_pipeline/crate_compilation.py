"""
Crate compilation strategies and command generation.

Extracted from crate_analysis.py to reduce file size and improve maintainability.
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def assess_crate_complexity(
    env_info: Dict[str, Any], feature_analysis: Dict[str, Any]
) -> str:
    """Assess crate complexity to determine appropriate analysis strategies."""
    crate_name = env_info.get("crate_name", "").lower()
    feature_count = len(feature_analysis.get("platform_safe_features", []))
    has_workspace = env_info.get("workspace_member", False)
    has_build_script = env_info.get("has_build_script", False)

    # Known complex crates that need special handling
    complex_crates = {
        "tokio",
        "async-std",
        "actix-web",
        "rocket",
        "diesel",
        "sqlx",
        "bevy",
        "tauri",
        "wgpu",
        "winit",
        "alsa",
        "pulseaudio",
        "gstreamer",
        "openssl",
        "ring",
        "rustls",
        "webpki",
        "x509-parser",
        "proc-macro2",
        "syn",
        "quote",
        "serde_derive",
    }

    # System/network dependent crates
    system_dependent = {
        "alsa",
        "pulseaudio",
        "winapi",
        "windows",
        "libc",
        "nix",
        "socket2",
        "mio",
        "polling",
        "async-io",
        "smol",
    }

    if crate_name in complex_crates:
        return "complex"
    elif crate_name in system_dependent:
        return "system_dependent"
    elif has_workspace or has_build_script or feature_count > 10:
        return "moderate"
    else:
        return "simple"


def get_build_strategies(
    platform_info: Dict[str, Any],
    feature_combinations: Dict[str, str],
    platform_name: str,
    complexity: str,
) -> List[Dict[str, Any]]:
    """Get platform-specific build strategies based on crate complexity."""
    platform = platform_info["os"]

    # Platform-specific cargo build commands
    if platform == "windows":
        base_cmd = ["cargo.exe", "build"]
        check_cmd = ["cargo.exe", "check"]
        metadata_cmd = ["cargo.exe", "metadata"]
    else:  # Linux, macOS, other Unix
        base_cmd = ["cargo", "build"]
        check_cmd = ["cargo", "check"]
        metadata_cmd = ["cargo", "metadata"]

    if complexity == "complex":
        return [
            # Start conservatively for complex crates
            {
                "cmd": check_cmd,
                "desc": f"Conservative check for complex crate ({platform})",
            },
            {
                "cmd": base_cmd + [
                    "--features",
                    feature_combinations.get("basic", "default"),
                ],
                "desc": f"Basic build: {feature_combinations.get('basic', 'default')} ({platform})",
            },
            {
                "cmd": base_cmd + [
                    "--features",
                    feature_combinations.get("comprehensive", "default"),
                ],
                "desc": f"Comprehensive build: {feature_combinations.get('comprehensive', 'default')} ({platform})",
            },
            {
                "cmd": base_cmd,
                "desc": f"Minimal build no features ({platform})",
            },
            {
                "cmd": metadata_cmd + ["--format-version", "1"],
                "desc": f"Metadata extraction ({platform})",
            },
        ]
    elif complexity == "system_dependent":
        return [
            # Focus on platform compatibility
            {
                "cmd": check_cmd + [
                    "--features",
                    feature_combinations.get("basic", "default"),
                ],
                "desc": f"Platform check: {feature_combinations.get('basic', 'default')} ({platform})",
            },
            {
                "cmd": base_cmd + [
                    "--features",
                    feature_combinations.get("basic", "default"),
                ],
                "desc": f"Platform build: {feature_combinations.get('basic', 'default')} ({platform})",
            },
            {
                "cmd": base_cmd,
                "desc": f"Minimal build ({platform})",
            },
            {
                "cmd": metadata_cmd + ["--format-version", "1"],
                "desc": f"Metadata extraction ({platform})",
            },
        ]
    else:
        # Standard aggressive approach for simple/moderate crates
        return [
            {
                "cmd": base_cmd + [
                    "--features",
                    feature_combinations.get("all_safe", "default"),
                ],
                "desc": f"Build with ALL platform-safe features: {feature_combinations.get('all_safe', 'default')} ({platform})",
            },
            {
                "cmd": base_cmd + [
                    "--release",
                    "--features",
                    feature_combinations.get("comprehensive", "default"),
                ],
                "desc": f"Release build: {feature_combinations.get('comprehensive', 'default')} ({platform})",
            },
            {
                "cmd": base_cmd + [
                    "--all-targets",
                    "--features",
                    feature_combinations.get("basic", "default"),
                ],
                "desc": f"All targets: {feature_combinations.get('basic', 'default')} ({platform})",
            },
            {
                "cmd": check_cmd + [
                    "--features",
                    feature_combinations.get("comprehensive", "default"),
                ],
                "desc": f"Comprehensive check ({platform})",
            },
            {
                "cmd": metadata_cmd + ["--format-version", "1"],
                "desc": f"Metadata extraction ({platform})",
            },
        ]


def get_test_strategies(
    platform_info: Dict[str, Any],
    feature_combinations: Dict[str, str],
    platform_name: str,
    complexity: str,
) -> List[Dict[str, Any]]:
    """Get platform-specific test strategies based on crate complexity."""
    platform = platform_info["os"]

    # Platform-specific cargo test commands
    if platform == "windows":
        base_cmd = ["cargo.exe", "test"]
    else:  # Linux, macOS, other Unix
        base_cmd = ["cargo", "test"]

    if complexity == "complex":
        return [
            # Only compile tests for complex crates, don't try to run them
            {
                "cmd": base_cmd + ["--no-run"],
                "desc": f"Compile tests only - complex crate safety ({platform})",
            },
            {
                "cmd": base_cmd + [
                    "--features",
                    feature_combinations.get("basic", "default"),
                    "--no-run",
                ],
                "desc": f"Compile tests with basic features: {feature_combinations.get('basic', 'default')} ({platform})",
            },
            {
                "cmd": base_cmd + ["--lib", "--no-run"],
                "desc": f"Compile library tests only ({platform})",
            },
            {
                "cmd": base_cmd + ["--", "--list"],
                "desc": f"List available tests ({platform})",
            },
        ]
    elif complexity == "system_dependent":
        return [
            # Minimal testing for system-dependent crates
            {
                "cmd": base_cmd + ["--no-run"],
                "desc": f"Compile tests - system crate ({platform})",
            },
            {
                "cmd": base_cmd + ["--lib", "--no-run"],
                "desc": f"Compile library tests ({platform})",
            },
            {
                "cmd": base_cmd + ["--", "--list"],
                "desc": f"List tests ({platform})",
            },
        ]
    else:
        # Full testing for simple/moderate crates
        return [
            {
                "cmd": base_cmd + [
                    "--features",
                    feature_combinations.get("all_safe", "default"),
                ],
                "desc": f"RUN tests with safe features: {feature_combinations.get('all_safe', 'default')} ({platform})",
            },
            {
                "cmd": base_cmd + ["--lib"],
                "desc": f"RUN library tests ({platform})",
            },
            {
                "cmd": base_cmd + [
                    "--features",
                    feature_combinations.get("basic", "default"),
                ],
                "desc": f"RUN tests with basic features: {feature_combinations.get('basic', 'default')} ({platform})",
            },
            {
                "cmd": base_cmd + ["--no-run"],
                "desc": f"Compile tests fallback ({platform})",
            },
            {
                "cmd": base_cmd + ["--", "--list"],
                "desc": f"List available tests ({platform})",
            },
        ]


def get_clippy_strategies(
    platform_info: Dict[str, Any],
    feature_combinations: Dict[str, str],
    platform_name: str,
    complexity: str,
) -> List[Dict[str, Any]]:
    """Get platform-specific clippy strategies based on complexity."""
    platform = platform_info["os"]

    # Platform-specific cargo clippy commands
    if platform == "windows":
        base_cmd = ["cargo.exe", "clippy"]
    else:  # Linux, macOS, other Unix
        base_cmd = ["cargo", "clippy"]

    # Platform-specific clippy arguments
    common_args = [
        "--message-format=json",
        "--",
        "-W",
        "clippy::all",
        "-W",
        "clippy::pedantic",
        "-A",
        "clippy::missing_docs_in_private_items",
        "-A",
        "clippy::module_name_repetitions",
    ]

    if complexity == "complex":
        return [
            {
                "cmd": base_cmd + ["--message-format=json"],
                "desc": f"Basic clippy JSON - complex crate ({platform})",
            },
            {
                "cmd": base_cmd + ["--no-deps"],
                "desc": f"Clippy without deps - complex crate ({platform})",
            },
            {
                "cmd": base_cmd,
                "desc": f"Basic clippy - complex crate ({platform})",
            },
        ]
    else:
        strategies = []

        # Try with safe features first
        safe_features = feature_combinations.get("all_safe", "")
        if safe_features and safe_features != "default":
            strategies.extend(
                [
                    {
                        "cmd": base_cmd + ["--features", safe_features] + common_args,
                        "desc": f"Clippy with safe features: {safe_features} ({platform})",
                    },
                    {
                        "cmd": base_cmd + ["--features", safe_features, "--message-format=json"],
                        "desc": f"Clippy with safe features JSON: {safe_features} ({platform})",
                    },
                ]
            )

        # Basic strategies
        strategies.extend(
            [
                {
                    "cmd": base_cmd + common_args,
                    "desc": f"Clippy with comprehensive checks ({platform})",
                },
                {
                    "cmd": base_cmd + ["--message-format=json", "--no-deps"],
                    "desc": f"Clippy without deps JSON ({platform})",
                },
                {
                    "cmd": base_cmd + ["--message-format=json"],
                    "desc": f"Basic clippy JSON ({platform})",
                },
                {
                    "cmd": base_cmd + ["--no-deps"],
                    "desc": f"Clippy without deps ({platform})",
                },
                {
                    "cmd": base_cmd,
                    "desc": f"Basic clippy ({platform})",
                },
            ]
        )

        return strategies


def get_audit_strategies(
    platform_info: Dict[str, Any], complexity: str
) -> List[Dict[str, Any]]:
    """Get platform-specific audit strategies with proper project setup."""
    platform = platform_info["os"]

    # Platform-specific cargo audit commands
    if platform == "windows":
        base_cmd = ["cargo.exe", "audit"]
        lockfile_cmd = ["cargo.exe", "generate-lockfile"]
    else:  # Linux, macOS, other Unix
        base_cmd = ["cargo", "audit"]
        lockfile_cmd = ["cargo", "generate-lockfile"]

    strategies = [
        {
            "cmd": lockfile_cmd,
            "desc": f"Generate Cargo.lock for audit ({platform})",
        },
        {
            "cmd": base_cmd + ["--json", "--stale"],
            "desc": f"Security audit JSON with stale DB ({platform})",
        },
        {
            "cmd": base_cmd + ["--ignore-yanked", "--stale"],
            "desc": f"Security audit ignore yanked with stale DB ({platform})",
        },
        {
            "cmd": base_cmd + ["--stale"],
            "desc": f"Security audit text with stale DB ({platform})",
        },
        # Fallback without stale flag
        {
            "cmd": base_cmd + ["--json"],
            "desc": f"Security audit JSON ({platform})",
        },
        {
            "cmd": base_cmd + ["--ignore-yanked"],
            "desc": f"Security audit ignore yanked ({platform})",
        },
        {
            "cmd": base_cmd,
            "desc": f"Security audit text ({platform})",
        },
    ]

    return strategies


def get_fmt_strategies(platform_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get platform-specific format checking strategies."""
    platform = platform_info["os"]

    # Platform-specific cargo fmt commands
    if platform == "windows":
        base_cmd = ["cargo.exe", "fmt"]
        rustfmt_cmd = ["rustfmt.exe"]
    else:  # Linux, macOS, other Unix
        base_cmd = ["cargo", "fmt"]
        rustfmt_cmd = ["rustfmt"]

    return [
        {
            "cmd": base_cmd + ["--", "--check"],
            "desc": f"Format check ({platform})",
        },
        {
            "cmd": rustfmt_cmd + ["--version"],
            "desc": f"Rustfmt availability check ({platform})",
        },
    ]


def get_outdated_strategies(platform_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get platform-specific dependency update strategies."""
    platform = platform_info["os"]

    # Platform-specific cargo outdated commands
    if platform == "windows":
        base_cmd = ["cargo.exe", "outdated"]
    else:  # Linux, macOS, other Unix
        base_cmd = ["cargo", "outdated"]

    return [
        {
            "cmd": base_cmd + ["--format", "json"],
            "desc": f"Dependency updates JSON ({platform})",
        },
        {
            "cmd": base_cmd,
            "desc": f"Dependency updates text ({platform})",
        },
    ]


def get_tree_strategies(
    platform_info: Dict[str, Any],
    feature_combinations: Dict[str, str],
    platform_name: str,
) -> List[Dict[str, Any]]:
    """Get platform-specific dependency tree strategies."""
    platform = platform_info["os"]

    # Platform-specific cargo tree commands
    if platform == "windows":
        base_cmd = ["cargo.exe", "tree"]
    else:  # Linux, macOS, other Unix
        base_cmd = ["cargo", "tree"]

    return [
        {
            "cmd": base_cmd + [
                "--features",
                feature_combinations.get("all_safe", "default"),
                "--format",
                "json",
            ],
            "desc": f"Dependency tree with safe features: {feature_combinations.get('all_safe', 'default')} ({platform})",
        },
        {
            "cmd": base_cmd + ["--format", "json"],
            "desc": f"Basic dependency tree JSON ({platform})",
        },
        {
            "cmd": base_cmd,
            "desc": f"Basic dependency tree ({platform})",
        },
    ]


def get_doc_strategies(
    platform_info: Dict[str, Any],
    feature_combinations: Dict[str, str],
    platform_name: str,
) -> List[Dict[str, Any]]:
    """Get platform-specific documentation strategies."""
    platform = platform_info["os"]

    # Platform-specific cargo doc commands
    if platform == "windows":
        base_cmd = ["cargo.exe", "doc"]
    else:  # Linux, macOS, other Unix
        base_cmd = ["cargo", "doc"]

    return [
        {
            "cmd": base_cmd + [
                "--features",
                feature_combinations.get("all_safe", "default"),
                "--no-deps",
            ],
            "desc": f"Documentation with safe features: {feature_combinations.get('all_safe', 'default')} ({platform})",
        },
        {
            "cmd": base_cmd + ["--no-deps"],
            "desc": f"Basic documentation generation ({platform})",
        },
    ]


def get_bench_strategies(
    platform_info: Dict[str, Any],
    feature_combinations: Dict[str, str],
    platform_name: str,
    complexity: str,
) -> List[Dict[str, Any]]:
    """Get platform-specific benchmark strategies based on complexity."""
    platform = platform_info["os"]

    # Platform-specific cargo bench commands
    if platform == "windows":
        base_cmd = ["cargo.exe", "bench"]
        test_cmd = ["cargo.exe", "test"]
    else:  # Linux, macOS, other Unix
        base_cmd = ["cargo", "bench"]
        test_cmd = ["cargo", "test"]

    if complexity == "complex":
        return [
            {
                "cmd": base_cmd + ["--no-run"],
                "desc": f"Compile benchmarks only - complex crate ({platform})",
            },
            {
                "cmd": test_cmd + ["--benches", "--no-run"],
                "desc": f"Compile benchmark tests ({platform})",
            },
        ]
    else:
        return [
            {
                "cmd": base_cmd + [
                    "--features",
                    feature_combinations.get("all_safe", "default"),
                ],
                "desc": f"RUN benchmarks with safe features: {feature_combinations.get('all_safe', 'default')} ({platform})",
            },
            {
                "cmd": base_cmd + ["--no-run"],
                "desc": f"Compile benchmarks fallback ({platform})",
            },
            {
                "cmd": test_cmd + ["--benches", "--no-run"],
                "desc": f"Compile benchmark tests ({platform})",
            },
        ]


def get_coverage_strategies(
    platform_info: Dict[str, Any],
    feature_combinations: Dict[str, str],
    platform_name: str,
    complexity: str,
) -> List[Dict[str, Any]]:
    """Get platform-specific coverage strategies based on crate complexity."""
    platform = platform_info["os"]

    # Platform-specific cargo coverage commands
    if platform == "windows":
        llvm_cov_cmd = ["cargo.exe", "llvm-cov"]
        rustup_cmd = ["rustup.exe"]
        test_cmd = ["cargo.exe", "test"]
    else:  # Linux, macOS, other Unix
        llvm_cov_cmd = ["cargo", "llvm-cov"]
        rustup_cmd = ["rustup"]
        test_cmd = ["cargo", "test"]

    base_strategies = [
        {
            "cmd": llvm_cov_cmd + ["--version"],
            "desc": f"Coverage tool version check ({platform})",
        },
        {
            "cmd": rustup_cmd + ["component", "list", "--installed"],
            "desc": f"Check installed components ({platform})",
        },
        {
            "cmd": llvm_cov_cmd + ["clean"],
            "desc": f"Clean previous coverage data ({platform})",
        },
    ]

    if complexity == "complex":
        # Conservative coverage for complex crates
        base_strategies.extend(
            [
                {
                    "cmd": llvm_cov_cmd + ["test", "--no-run"],
                    "desc": f"Coverage build only - complex crate ({platform})",
                },
                {
                    "cmd": llvm_cov_cmd + ["--summary-only"],
                    "desc": f"Generate coverage summary ({platform})",
                },
                {
                    "cmd": test_cmd + ["--no-run"],
                    "desc": f"Test compilation fallback ({platform})",
                },
            ]
        )
    elif complexity == "system_dependent":
        # Basic coverage for system crates
        base_strategies.extend(
            [
                {
                    "cmd": llvm_cov_cmd + ["test", "--lib", "--no-run"],
                    "desc": f"Library coverage build ({platform})",
                },
                {
                    "cmd": llvm_cov_cmd + ["--summary-only"],
                    "desc": f"Coverage summary ({platform})",
                },
                {
                    "cmd": test_cmd + ["--no-run"],
                    "desc": f"Test compilation fallback ({platform})",
                },
            ]
        )
    else:
        # Full coverage for simple/moderate crates
        base_strategies.extend(
            [
                {
                    "cmd": llvm_cov_cmd + [
                        "test",
                        "--features",
                        feature_combinations.get("all_safe", "default"),
                        "--json",
                    ],
                    "desc": f"Full coverage with safe features: {feature_combinations.get('all_safe', 'default')} ({platform})",
                },
                {
                    "cmd": llvm_cov_cmd + ["test", "--lib", "--json"],
                    "desc": f"Library coverage ({platform})",
                },
                {
                    "cmd": llvm_cov_cmd + ["--json"],
                    "desc": f"Generate coverage report JSON ({platform})",
                },
                {
                    "cmd": llvm_cov_cmd + ["--summary-only"],
                    "desc": f"Coverage summary ({platform})",
                },
                {
                    "cmd": test_cmd + ["--no-run"],
                    "desc": f"Test compilation fallback ({platform})",
                },
            ]
        )

    return base_strategies


def get_geiger_strategies(
    platform_info: Dict[str, Any],
    feature_combinations: Dict[str, str],
    platform_name: str,
    complexity: str,
) -> List[Dict[str, Any]]:
    """Get platform-specific geiger strategies based on complexity."""
    platform = platform_info["os"]

    # Platform-specific cargo geiger commands
    if platform == "windows":
        base_cmd = ["cargo.exe", "geiger"]
    else:  # Linux, macOS, other Unix
        base_cmd = ["cargo", "geiger"]

    if complexity == "complex":
        return [
            {
                "cmd": base_cmd + ["--format", "json"],
                "desc": f"Basic unsafe analysis JSON ({platform})",
            },
            {
                "cmd": base_cmd + ["--forbid-only"],
                "desc": f"Quick unsafe scan ({platform})",
            },
        ]
    else:
        return [
            {
                "cmd": base_cmd + [
                    "--features",
                    feature_combinations.get("all_safe", "default"),
                    "--format",
                    "json",
                ],
                "desc": f"Unsafe analysis with safe features: {feature_combinations.get('all_safe', 'default')} ({platform})",
            },
            {
                "cmd": base_cmd + ["--format", "json"],
                "desc": f"Basic unsafe analysis JSON ({platform})",
            },
            {
                "cmd": base_cmd + ["--forbid-only"],
                "desc": f"Quick unsafe scan ({platform})",
            },
        ]


def get_progressive_command_strategy(
    platform_info: Dict[str, Any],
    command_type: str,
    env_info: Dict[str, Any],
    feature_analysis: Dict[str, Any],
    feature_combinations: Dict[str, str],
) -> List[Dict[str, Any]]:
    """Get a progressive list of commands to try for maximum data collection with platform-aware feature selection."""
    platform_name = platform_info["os"]
    
    # Determine crate complexity level for adaptive strategies
    complexity = assess_crate_complexity(env_info, feature_analysis)

    strategies = {
        "build": get_build_strategies(
            platform_info, feature_combinations, platform_name, complexity
        ),
        "test": get_test_strategies(
            platform_info, feature_combinations, platform_name, complexity
        ),
        "clippy": get_clippy_strategies(
            platform_info, feature_combinations, platform_name, complexity
        ),
        "audit": get_audit_strategies(platform_info, complexity),
        "fmt": get_fmt_strategies(platform_info),
        "geiger": get_geiger_strategies(
            platform_info, feature_combinations, platform_name, complexity
        ),
        "outdated": get_outdated_strategies(platform_info),
        "coverage": get_coverage_strategies(
            platform_info, feature_combinations, platform_name, complexity
        ),
        "tree": get_tree_strategies(platform_info, feature_combinations, platform_name),
        "doc": get_doc_strategies(platform_info, feature_combinations, platform_name),
        "bench": get_bench_strategies(
            platform_info, feature_combinations, platform_name, complexity
        ),
    }

    if command_type in strategies:
        commands = strategies[command_type]

        # Add individual feature testing for platform-safe features
        for key, feature_combo in feature_combinations.items():
            if key.startswith("single_") and command_type in [
                "build",
                "clippy",
                "test",
            ]:
                feature_name = key.replace("single_", "")
                if command_type == "test":
                    cmd = ["cargo", "test", "--features", feature_combo, "--no-run"]
                else:
                    cmd = ["cargo", command_type, "--features", feature_combo]
                
                # Platform-specific command
                if platform_info["os"] == "windows":
                    cmd[0] = "cargo.exe"

                commands.insert(
                    -3,
                    {  # Insert before fallbacks
                        "cmd": cmd,
                        "desc": f"{command_type.title()} with single safe feature '{feature_name}' on {platform_name}",
                    },
                )

        return commands

    return []

