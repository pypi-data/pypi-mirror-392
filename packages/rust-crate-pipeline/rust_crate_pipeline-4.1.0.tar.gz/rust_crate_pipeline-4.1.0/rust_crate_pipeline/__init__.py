# rust_crate_pipeline/__init__.py
"""
Rust Crate Data Processing Pipeline

A comprehensive system for gathering, enriching, and analyzing metadata for Rust crates.
Includes AI-powered enrichment using local LLMs and dependency analysis.

Example usage:
    from rust_crate_pipeline.config import PipelineConfig
    from rust_crate_pipeline.unified_pipeline import UnifiedPipeline

    config = PipelineConfig()
    pipeline = UnifiedPipeline(config, {"crate_list": ["serde"], "output_dir": "./output"})
    asyncio.run(pipeline.run())

Components:
    - UnifiedPipeline: Public orchestration entry point
    - CrateDataPipeline: Internal ingestion/enrichment engine
    - PipelineConfig: Configuration management
    - Various analyzers for AI, security, and dependency analysis
"""

# The following imports are for making package-level metadata and components
# easily accessible to users of the library.
from .version import __version__  # noqa: F401

__author__ = "SuperUser666-Sigil"
__email__ = "miragemodularframework@gmail.com"
__license__ = "MIT"

# The main components are demonstrated in the docstring and are not directly
# exported here to avoid circular dependencies and to keep the namespace clean.
# Users should import them directly from the respective modules.

# Suppress specific warnings at the package initialization level
# Rule Zero Compliance: Only suppress third-party Pydantic deprecation warnings
# that originate from dependencies, not from our own code
import warnings

warnings.filterwarnings(
    "ignore",
    message=".*Support for class-based.*config.*is deprecated.*",
    category=DeprecationWarning,
    module="pydantic._internal._config",
)
