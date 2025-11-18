# main.py
import argparse
import asyncio
import hashlib
import hmac
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Set, Tuple

from .audits.validate_db_hash import calculate_db_hash
from .config import PipelineConfig
from .github_token_checker import check_and_setup_github_token
from .production_config import setup_production_environment
from .unified_pipeline import UnifiedPipeline
from .utils.resume_utils import (
    create_resume_report,
    get_remaining_crates,
    load_crate_list,
    validate_resume_state,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Constants
MIN_FREE_DISK_SPACE = 1_000_000_000  # 1GB in bytes


def enforce_utf8_locale() -> None:
    """Force UTF-8 encoding across platforms for scraping/logging."""
    os.environ.setdefault("PYTHONUTF8", "1")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        for stream in (sys.stdin, sys.stdout, sys.stderr):
            if hasattr(stream, "reconfigure"):
                stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception as exc:  # pragma: no cover - defensive
        logging.debug("UTF-8 enforcement fallback: %s", exc)


def _override_audit_log_path() -> Path:
    """Return the path for persisting Rule Zero override audit events."""

    return PROJECT_ROOT / "rule_zero_override_audit.log"


def _load_override_allowlist() -> Set[str]:
    """Load the set of operators permitted to approve Rule Zero overrides."""

    allowlist: Set[str] = set()

    allowlist_env = os.environ.get("RULE_ZERO_OVERRIDE_ALLOWLIST", "")
    if allowlist_env:
        allowlist.update(
            {entry.strip() for entry in allowlist_env.split(",") if entry.strip()}
        )

    allowlist_path = os.environ.get("RULE_ZERO_OVERRIDE_ALLOWLIST_PATH")
    if allowlist_path:
        try:
            # Validate path to prevent path traversal attacks
            path = Path(allowlist_path).resolve()
            if not path.exists():
                logging.error("Allowlist path does not exist: %s", path)
            elif not path.is_file():
                logging.error("Allowlist path is not a file: %s", path)
            else:
                with path.open("r", encoding="utf-8") as handle:
                    for line in handle:
                        candidate = line.strip()
                        if candidate and not candidate.startswith("#"):
                            allowlist.add(candidate)
        except (OSError, ValueError) as exc:
            logging.error(
                "Unable to read override allowlist file %s: %s", allowlist_path, exc
            )

    return allowlist


def _verify_override_token(
    operator: str, token: str, secret: str, expected_hash: str
) -> bool:
    """Validate the override token using an HMAC signature tied to the operator."""

    message = f"{operator}:{expected_hash}"
    computed = hmac.new(
        secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    if hmac.compare_digest(computed, token):
        return True

    logging.error("Override token verification failed for operator %s", operator)
    return False


def _record_override_audit_event(
    operator: str, justification: str, expected_hash: str, actual_hash: str
) -> None:
    """Persist authorised override metadata for auditing."""

    audit_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "operator": operator,
        "justification": justification,
        "expected_hash": expected_hash,
        "actual_hash": actual_hash,
    }

    try:
        with _override_audit_log_path().open("a", encoding="utf-8") as log_file:
            log_file.write(f"{json.dumps(audit_entry)}\n")
    except OSError as exc:
        logging.error("Failed to persist Rule Zero override audit event: %s", exc)


def _attempt_authorized_override(expected_hash: str, actual_hash: str) -> bool:
    """Attempt to approve a Rule Zero override using multi-factor controls."""

    justification = (
        os.environ.get("RULE_ZERO_OVERRIDE_JUSTIFICATION")
        or os.environ.get("RULE_ZERO_OVERRIDE")
        or ""
    ).strip()
    if not justification:
        logging.error("Override justification missing; cannot bypass Rule Zero.")
        return False

    operator = os.environ.get("RULE_ZERO_OVERRIDE_OPERATOR", "").strip()
    if not operator:
        logging.error("Override operator identity missing.")
        return False

    allowlist = _load_override_allowlist()
    if not allowlist:
        logging.error("No override allowlist configured; refusing override.")
        return False
    if operator not in allowlist:
        logging.error("Operator %s is not authorised for Rule Zero overrides.", operator)
        return False

    secret = os.environ.get("RULE_ZERO_OVERRIDE_SECRET", "").strip()
    token = os.environ.get("RULE_ZERO_OVERRIDE_TOKEN", "").strip()
    if not secret or not token:
        logging.error("Override token or secret missing for operator %s.", operator)
        return False

    if not _verify_override_token(operator, token, secret, expected_hash):
        return False

    logging.warning(
        "Manual override of Rule Zero DB hash/signature validation enabled."
    )
    logging.warning("Override operator: %s", operator)
    logging.warning("Override justification: %s", justification)
    _record_override_audit_event(operator, justification, expected_hash, actual_hash)
    return True


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Rust Crate Data Processing Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings
  python -m rust_crate_pipeline

  # Process a limited number of crates with a smaller batch size
  python -m rust_crate_pipeline --limit 50 --batch-size 5

  # Specify a custom output directory and log level
  python -m rust_crate_pipeline --output-dir ./data --log-level DEBUG

  # Use a specific LLM provider and model
  python -m rust_crate_pipeline --llm-provider openai --llm-model gpt-4

  # Disable ELINT/Sacred Chain stage if needed
  python -m rust_crate_pipeline --disable-elint --crates tokio serde
        """,
    )

    # Setup and configuration
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run setup and configuration for Playwright, Crawl4AI, and Rust tools",
    )
    parser.add_argument(
        "--setup-check",
        action="store_true",
        help="Check current setup status without running setup",
    )
    parser.add_argument(
        "--verbose-setup",
        action="store_true",
        help="Verbose output during setup process",
    )

    # General configuration
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration JSON file (overrides other settings)",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default="./output",
        help="Output directory for results (default: ./output)",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    parser.add_argument(
        "--legacy-heuristics",
        action="store_true",
        help="Use the pre-unification heuristic rules for snippet scoring.",
    )

    # Crate selection
    parser.add_argument(
        "--crates",
        type=str,
        nargs="+",
        help="Specific crates to process (space-separated list)",
    )
    parser.add_argument(
        "--crate-list-path",
        "--crates-file",
        dest="crate_list_path",
        type=str,
        default="data/crates.txt",
        help="Path to file containing crates to process",
    )
    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=None,
        help="Limit the number of crates to process",
    )

    # Pipeline control
    parser.add_argument(
        "--batch-size",
        "-b",
        type=int,
        default=10,
        help="Number of crates to process in each batch (default: 10)",
    )
    parser.add_argument(
        "--max-workers",
        "-w",
        type=int,
        default=4,
        help="Number of parallel workers for API requests (default: 4)",
    )
    parser.add_argument(
        "--checkpoint-interval",
        type=int,
        default=10,
        help="Save checkpoint every N crates (default: 10)",
    )
    parser.add_argument(
        "--skip-ai",
        action="store_true",
        help="Skip AI enrichment (faster, metadata only)",
    )
    parser.add_argument(
        "--skip-source-analysis",
        action="store_true",
        help="Skip source code analysis",
    )
    parser.add_argument(
        "--sync-mode",
        action="store_true",
        help=(
            "Run the pipeline in synchronous compatibility mode, disabling"
            " background offloading of blocking operations"
        ),
    )

    # LLM configuration
    parser.add_argument(
        "--llm-provider",
        type=str,
        default="llama-cpp-python",
        help="LLM provider to use",
    )
    parser.add_argument(
        "--llm-model",
        "-m",
        type=str,
        help="LLM model identifier or path",
    )
    parser.add_argument(
        "--llm-api-base",
        type=str,
        help="Custom API base URL for OpenAI-compatible providers",
    )
    parser.add_argument(
        "--llm-api-key",
        type=str,
        help="API key/token for the selected provider",
    )
    parser.add_argument(
        "--llm-max-tokens",
        type=int,
        default=256,
        help="Maximum tokens for LLM generation",
    )
    parser.add_argument(
        "--llm-temperature",
        type=float,
        default=0.2,
        help="Generation temperature for the LLM",
    )
    parser.add_argument(
        "--azure-deployment",
        type=str,
        help="Azure OpenAI deployment name (if provider=azure)",
    )
    parser.add_argument(
        "--azure-api-version",
        type=str,
        default="2024-02-15-preview",
        help="Azure OpenAI API version",
    )
    parser.add_argument(
        "--ollama-host",
        type=str,
        default="http://localhost:11434",
        help="Base URL for Ollama servers",
    )
    parser.add_argument(
        "--llama-cpp-gpu-layers",
        type=int,
        default=-1,
        help="Number of GPU layers for llama-cpp (-1 means auto)",
    )
    parser.add_argument(
        "--llama-cpp-context-size",
        type=int,
        default=8192,
        help="Context window for llama-cpp providers",
    )

    # Crawl4AI configuration
    parser.add_argument(
        "--disable-crawl4ai",
        action="store_true",
        help="Disable enhanced Crawl4AI-powered web scraping (enabled by default)",
    )
    parser.add_argument(
        "--crawl4ai-model",
        type=str,
        help="GGUF model path for Crawl4AI content analysis",
    )

    # ELINT / Sacred Chain controls
    parser.add_argument(
        "--disable-elint",
        action="store_true",
        help="Skip ELINT (Sacred Chain) analysis stage",
    )

    parser.add_argument(
        "--auto-resume",
        action="store_true",
        help="Resume from previous progress when using a crate list file",
    )
    parser.add_argument(
        "--force-restart",
        action="store_true",
        help="Ignore resume state and process the entire crate list",
    )
    parser.add_argument(
        "--skip-problematic",
        action="store_true",
        help="Skip crates marked as historically problematic",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging (alias for --log-level DEBUG)",
    )

    return parser.parse_args()


def configure_logging(log_level: str = "INFO") -> None:
    """Configure logging with both console and file output"""
    level = getattr(logging, log_level.upper())

    # Clear any existing handlers to avoid conflicts
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Set root logger level
    root_logger.setLevel(level)

    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    simple_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)

    # File handler with unique timestamp
    log_filename = f"crate_enrichment_{time.strftime('%Y%m%d-%H%M%S')}.log"
    try:
        file_handler = logging.FileHandler(log_filename, mode="w", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)  # Always capture DEBUG+ to file
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)

        # Log a test message to verify file handler works
        logging.info("Logging initialized - file: %s", log_filename)

    except (OSError, PermissionError) as e:
        logging.error("Failed to create log file %s: %s", log_filename, e)
        print(f"Warning: Could not create log file: {e}")

    # Set library loggers to less verbose levels
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests_cache").setLevel(logging.WARNING)
    logging.getLogger("llama_cpp").setLevel(logging.WARNING)


def check_disk_space() -> None:
    """Check if there is at least 1GB of free disk space, log a warning if not."""
    if shutil.disk_usage(".").free < MIN_FREE_DISK_SPACE:
        logging.warning("Low disk space! This may affect performance.")


def enforce_rule_zero_reinforcement() -> None:
    """
    Enforce Rule Zero rigor by validating the canonical DB hash/signature
    before pipeline actions.

    Allows override for local dev, but enforces in CI/prod. Logs all events
    for traceability.
    """
    enforce: bool = (
        os.environ.get("ENFORCE_RULE_ZERO", "false").lower() == "true"
        or os.environ.get("CI", "false").lower() == "true"
        or os.environ.get("PRODUCTION", "false").lower() == "true"
    )
    if not enforce:
        logging.info("Rule Zero DB hash/signature check skipped (dev mode or override)")
        return

    db_path: Path = PROJECT_ROOT / "sigil_rag_cache.db"
    hash_path: Path = PROJECT_ROOT / "sigil_rag_cache.hash"

    if not db_path.exists() or not hash_path.exists():
        logging.critical(
            "Rule Zero DB or hash file not found. Enforcement is enabled but required "
            "files are missing. This is a security violation - failing closed."
        )
        sys.exit(1)

    try:
        logging.info("Validating Rule Zero DB hash/signature...")
        with hash_path.open("r", encoding="utf-8") as f:
            expected_hash = f.read().strip()

        actual_hash = calculate_db_hash(db_path)

        if actual_hash == expected_hash:
            logging.info("Rule Zero DB hash/signature validation successful.")
        else:
            logging.error("Rule Zero DB hash/signature validation failed:")
            logging.error("  Expected: %s", expected_hash)
            logging.error("  Actual:   %s", actual_hash)

            if _attempt_authorized_override(expected_hash, actual_hash):
                return

            logging.critical(
                "Rule Zero DB hash/signature validation failed and no authorised "
                "override provided. Exiting."
            )
            sys.exit(1)

    except (FileNotFoundError, OSError) as e:
        logging.critical(
            "Exception during Rule Zero DB hash/signature validation: %s", e
        )
        sys.exit(1)


def setup_environment() -> Tuple[argparse.Namespace, Dict[str, Any]]:
    """Sets up the environment for the pipeline to run."""
    prod_config: Dict[str, Any] = setup_production_environment()
    args = parse_arguments()
    if getattr(args, "verbose", False):
        args.log_level = "DEBUG"
    configure_logging(args.log_level)
    check_disk_space()
    # GitHub token check is deferred until after setup commands are handled
    # to allow non-interactive setup in automation
    return args, prod_config


def build_pipeline_config(
    args: argparse.Namespace, prod_config: Dict[str, Any]
) -> PipelineConfig:
    """Builds the pipeline configuration from arguments and production settings."""
    config_kwargs: Dict[str, Any] = {}
    if prod_config:
        config_kwargs.update(
            {
                "max_retries": prod_config.get("max_retries", 3),
                "batch_size": prod_config.get("batch_size", 10),
                "checkpoint_interval": prod_config.get("checkpoint_interval", 10),
            }
        )

    if args.batch_size:
        config_kwargs["batch_size"] = args.batch_size
    if args.max_workers:
        config_kwargs["n_workers"] = args.max_workers
    if args.llm_model:
        config_kwargs["model_path"] = args.llm_model
        config_kwargs["llm_model"] = args.llm_model
    if args.llm_max_tokens:
        config_kwargs["max_tokens"] = args.llm_max_tokens
    if args.checkpoint_interval:
        config_kwargs["checkpoint_interval"] = args.checkpoint_interval

    if args.config:
        import json

        with open(args.config, "r", encoding="utf-8") as f:
            file_config = json.load(f)
            config_kwargs.update(file_config)

    is_azure_provider = bool(
        args.llm_provider and args.llm_provider.lower() == "azure"
    )

    config_kwargs.update(
        {
            "enable_crawl4ai": not args.disable_crawl4ai,
            "enable_elint": not args.disable_elint,
            "crawl4ai_model": (
                args.crawl4ai_model if args.crawl4ai_model is not None else ""
            ),
            "skip_source_analysis": args.skip_source_analysis,
            "sync_mode": args.sync_mode,
            "use_legacy_heuristics": args.legacy_heuristics,
            "llm_provider": args.llm_provider if args.llm_provider else "llama-cpp-python",
            "llm_api_base": args.llm_api_base,
            "llm_api_key": args.llm_api_key,
            "temperature": args.llm_temperature,
            "ollama_host": args.ollama_host,
            "llama_cpp_gpu_layers": args.llama_cpp_gpu_layers,
            "llama_cpp_context_size": args.llama_cpp_context_size,
            "use_azure_openai": is_azure_provider,
            "azure_openai_endpoint": args.llm_api_base if is_azure_provider else "",
            "azure_openai_api_key": args.llm_api_key if is_azure_provider else "",
            "azure_openai_deployment_name": (
                args.azure_deployment
                if is_azure_provider and args.azure_deployment
                else (args.llm_model or "gpt-4o")
            ),
            "azure_openai_api_version": (
                args.azure_api_version if is_azure_provider else "2024-02-15-preview"
            ),
            "output_path": args.output_dir if args.output_dir else "output",  # Map output_dir CLI arg to output_path config
            "output_dir": args.output_dir if args.output_dir else "output",  # Also set output_dir for compatibility
        }
    )

    return PipelineConfig(**config_kwargs)


async def run_unified_pipeline(
    config: PipelineConfig, pipeline_kwargs: Dict[str, Any]
) -> None:
    """Runs the unified pipeline (ingestion + ELINT)."""
    logging.info("Unified pipeline mode")
    unified = UnifiedPipeline(config, pipeline_kwargs)
    logging.info("Starting pipeline with %s arguments", len(pipeline_kwargs))

    try:
        result = await unified.run()
        if result:
            logging.info("Unified pipeline completed successfully")
        else:
            logging.warning("Unified pipeline completed with no results")
    except (RuntimeError, OSError, ValueError, AttributeError) as e:
        logging.error("Unified pipeline failed: %s", e)
        raise
    except KeyboardInterrupt:
        logging.warning("Pipeline interrupted by user (CTRL+C)")
        raise


async def main_async() -> None:
    """The async main function."""
    enforce_utf8_locale()
    enforce_rule_zero_reinforcement()
    args, prod_config = setup_environment()

    # Handle setup commands first (before GitHub token check for non-interactive automation)
    if getattr(args, "setup", False) or getattr(args, "setup_check", False):
        from .setup_manager import SetupManager
        
        setup_manager = SetupManager(verbose=args.verbose_setup)
        
        if args.setup_check:
            status = setup_manager.get_setup_status()
            print(json.dumps(status, indent=2))
            return
        elif args.setup:
            success = await setup_manager.run_full_setup()
            if not success:
                sys.exit(1)
            return

    # Check GitHub token after setup commands (allows setup to run non-interactively)
    if not check_and_setup_github_token():
        logging.error("GitHub token setup cancelled or failed. Exiting.")
        sys.exit(1)
    logging.info("GitHub token validation successful")

    config = build_pipeline_config(args, prod_config)

    crate_list: list[str] = list(args.crates) if args.crates else []
    crate_list_path: Optional[str] = getattr(args, "crate_list_path", None)
    resume_report: Optional[str] = None

    if not crate_list:
        crate_list_path = crate_list_path or "data/crates.txt"
        if args.force_restart:
            crate_list = load_crate_list(crate_list_path)
        elif args.auto_resume:
            remaining, total, processed = get_remaining_crates(
                crate_list_path, args.output_dir, args.skip_problematic
            )
            if not remaining:
                logging.info("Auto-resume found no remaining crates. Nothing to do.")
                return
            if not validate_resume_state(remaining, total, processed, args.output_dir):
                logging.error("Resume state validation failed; aborting run.")
                sys.exit(1)
            resume_report = create_resume_report(
                remaining, total, processed, args.output_dir
            )
            crate_list = remaining
        else:
            crate_list = load_crate_list(crate_list_path)

    limit_for_pipeline = args.limit
    if crate_list:
        if args.limit is not None and args.limit > 0:
            crate_list = crate_list[: args.limit]
        limit_for_pipeline = None  # explicit list already limited

    if resume_report:
        print(resume_report)

    pipeline_kwargs: Dict[str, Any] = {
        "output_dir": args.output_dir,
        "limit": limit_for_pipeline,
        "crate_list": crate_list,
        "crate_list_path": None if crate_list else crate_list_path,
        "skip_ai": args.skip_ai,
        "skip_source": args.skip_source_analysis,
    }

    # Validate crate names at CLI entry point before processing
    if pipeline_kwargs["crate_list"]:
        from .utils.validation import validate_crate_name

        validated_crates = []
        for crate_name in pipeline_kwargs["crate_list"]:
            try:
                validated_crates.append(validate_crate_name(crate_name))
            except Exception as e:
                logging.error("Invalid crate name '%s': %s", crate_name, e)
                raise ValueError(f"Invalid crate name '{crate_name}': {e}") from e
        pipeline_kwargs["crate_list"] = validated_crates

    await run_unified_pipeline(config, pipeline_kwargs)

    logging.info("Main function execution completed successfully")


def main() -> None:
    """Main entry point for the Rust Crate Data Processing Pipeline."""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logging.warning("Pipeline interrupted by user (CTRL+C)")
        sys.exit(130)  # Standard exit code for SIGINT
    except (
        RuntimeError,
        OSError,
        ValueError,
        AttributeError,
        subprocess.CalledProcessError,
        FileNotFoundError,
        PermissionError,
    ) as e:
        logging.critical("Pipeline failed: %s", e)
        logging.debug("Exception details: %s: %s", type(e).__name__, e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
