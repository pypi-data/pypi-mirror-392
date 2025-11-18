# config.py
"""Configuration module for the Rust Crate Pipeline.

This module provides configuration classes and utilities for managing
pipeline settings, credentials, and runtime parameters.

All configuration follows PEP 8 style guidelines and enterprise security
best practices.
"""
import os
import warnings
from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, Any, Union

from .exceptions import ConfigurationError
from .utils.serialization_utils import to_serializable

if TYPE_CHECKING:
    from typing import Dict, List


# Default HTTP timeout for all requests (in seconds)
DEFAULT_HTTP_TIMEOUT = 15.0


# Filter Pydantic deprecation warnings from dependencies
# Rule Zero Compliance: Suppress third-party warnings while maintaining
# awareness
warnings.filterwarnings(
    "ignore",
    message=".*Support for class-based `config` is deprecated.*",
    category=DeprecationWarning,
    module="pydantic._internal._config",
)


@dataclass
class PipelineConfig:
    # Model configuration
    model_path: str = os.path.expanduser(
        "~/models/deepseek/deepseek-coder-6.7b-instruct.Q4_K_M.gguf"
    )
    max_tokens: int = 256
    model_token_limit: int = 13312  # 13k context for richer canonical data
    prompt_token_margin: int = 10000  # Leave ~10k for prompt, ~3k for response

    # LLM Configuration (for JSON config compatibility)
    llm_provider: str = "llama-cpp-python"
    llm_model: str = ""
    llm_api_base: str = ""
    llm_api_key: str = ""
    llm_request_timeout: float = 300.0  # Increased for 13k context window processing
    llm_max_retries: int = 3
    llm_num_ctx: int = 13312  # Match model_token_limit for 13k context
    llm_keep_alive: str = "1h"
    ollama_host: str = "http://localhost:11434"
    llama_cpp_gpu_layers: int = -1
    llama_cpp_context_size: int = 13312  # Match for llama-cpp

    # Generation parameters
    temperature: float = 0.3
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

    # Local model optimization settings
    local_model_mode: bool = field(
        default_factory=lambda: os.getenv("LOCAL_MODEL_MODE", "false").lower() == "true"
    )
    local_model_token_limit: int = 2048  # Conservative for local models
    local_model_prompt_margin: int = 1500  # More room for responses
    local_model_max_tokens: int = 512  # Allow longer responses
    local_model_temperature: float = 0.1  # Lower temperature for consistency
    local_model_chunk_size: int = 800  # Smaller chunks for local models

    # Pipeline configuration
    checkpoint_interval: int = 10
    max_retries: int = 3
    cache_ttl: int = 3600  # 1 hour
    batch_size: int = 10
    n_workers: int = 4
    skip_source_analysis: bool = False
    sync_mode: bool = False
    use_legacy_heuristics: bool = False

    # GitHub configuration
    github_token: str = field(default_factory=lambda: os.getenv("GITHUB_TOKEN", ""))

    # HTTP configuration
    http_timeout: float = DEFAULT_HTTP_TIMEOUT

    # Enhanced scraping configuration
    enable_crawl4ai: bool = True
    enable_elint: bool = True
    crawl4ai_model: str = os.path.expanduser(
        "~/models/deepseek/deepseek-coder-6.7b-instruct.Q4_K_M.gguf"
    )
    crawl4ai_timeout: int = 30

    # Output configuration
    output_path: str = "output"
    output_dir: str = "output"
    verbose: bool = False

    # Azure OpenAI Configuration - NO DEFAULTS FOR SENSITIVE DATA
    use_azure_openai: bool = field(
        default_factory=lambda: os.getenv("USE_AZURE_OPENAI", "false").lower() == "true"
    )
    azure_openai_endpoint: str = field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_ENDPOINT", "")
    )
    azure_openai_api_key: str = field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_API_KEY", "")
    )
    azure_openai_deployment_name: str = field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
    )
    azure_openai_api_version: str = field(
        default_factory=lambda: os.getenv(
            "AZURE_OPENAI_API_VERSION", "2024-02-15-preview"
        )
    )

    # Environment configuration
    environment: str = field(
        default_factory=lambda: os.getenv("ENVIRONMENT", "development")
    )

    # Removed unused from_json_config method - not used anywhere

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate configuration values."""
        # Validate Azure OpenAI configuration if enabled
        if self.use_azure_openai:
            if not self.azure_openai_endpoint:
                raise ConfigurationError(
                    "Azure OpenAI is enabled but AZURE_OPENAI_ENDPOINT is not set"
                )
            if not self.azure_openai_api_key:
                raise ConfigurationError(
                    "Azure OpenAI is enabled but AZURE_OPENAI_API_KEY is not set"
                )

        # Validate GitHub token if needed (can be optional for public repos)
        if not self.github_token and self.environment == "production":
            warnings.warn(
                "No GitHub token provided. API rate limits will be restricted.",
                RuntimeWarning,
            )

        # Validate numeric configurations
        if self.batch_size <= 0:
            raise ConfigurationError(
                f"batch_size must be positive, got {self.batch_size}"
            )
        if self.n_workers <= 0:
            raise ConfigurationError(
                f"n_workers must be positive, got {self.n_workers}"
            )
        if self.max_retries < 0:
            raise ConfigurationError(
                f"max_retries must be non-negative, got {self.max_retries}"
            )

    class Config:
        validate_assignment = True


@dataclass
class CrateMetadata:
    name: str
    version: str
    description: str
    repository: str
    keywords: "List[str]"
    categories: "List[str]"
    readme: str
    downloads: int
    github_stars: int = 0
    dependencies: "List[Dict[str, Any]]" = field(default_factory=list)
    features: "Dict[str, List[str]]" = field(default_factory=dict)
    code_snippets: "List[str]" = field(default_factory=list)
    readme_sections: "Dict[str, str]" = field(default_factory=dict)
    librs_downloads: Union[int, None] = None
    license: Union[str, None] = None  # SPDX license expression (e.g., "MIT OR Apache-2.0")
    source: str = "crates.io"
    # Enhanced scraping fields
    enhanced_scraping: "Dict[str, Any]" = field(default_factory=dict)
    enhanced_features: "List[str]" = field(default_factory=list)
    enhanced_dependencies: "List[str]" = field(default_factory=list)

    def to_dict(self) -> "Dict[str, Any]":
        """Convert the object to a dictionary."""
        result = to_serializable(asdict(self))
        if isinstance(result, dict):
            return result
        else:
            return {"data": str(result)}


@dataclass
class EnrichedCrate(CrateMetadata):
    readme_summary: Union[str, None] = None
    feature_summary: Union[str, None] = None
    use_case: Union[str, None] = None
    score: Union[float, None] = None
    factual_counterfactual: Union[str, None] = None
    source_analysis: Union["Dict[str, Any]", None] = None
    user_behavior: Union["Dict[str, Any]", None] = None
    security: Union["Dict[str, Any]", None] = None
    capabilities: "Dict[str, Any]" = field(default_factory=dict)
    ai_analysis: Union["Dict[str, Any]", None] = None
    ml_predictions: "Dict[str, Any]" = field(default_factory=dict)
    validation_summary: "Dict[str, Any]" = field(default_factory=dict)
