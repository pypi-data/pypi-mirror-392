# llm_factory.py
import logging
import os
from typing import Optional

from .config import PipelineConfig
from .llm_client import LLMClient, LLMConfig

logger = logging.getLogger(__name__)


def create_llm_client_from_config(config: PipelineConfig) -> LLMClient:
    """Create LLM client from existing pipeline configuration."""

    provider = getattr(config, "llm_provider", None)
    model = getattr(config, "llm_model", None)
    api_base = getattr(config, "llm_api_base", None)
    api_key = getattr(config, "llm_api_key", None)
    temperature = getattr(config, "temperature", 0.2)
    request_timeout = getattr(
        config, "llm_request_timeout", getattr(config, "http_timeout", 120.0)
    )
    max_retries = getattr(config, "llm_max_retries", getattr(config, "max_retries", 6))
    num_ctx = getattr(config, "model_token_limit", 4096)

    if getattr(config, "use_azure_openai", False) or (
        provider and provider.lower() == "azure"
    ):
        provider = "azure"
        model = getattr(config, "azure_openai_deployment_name", model or "gpt-4")
        api_base = getattr(config, "azure_openai_endpoint", api_base)
        api_key = getattr(config, "azure_openai_api_key", api_key)
    elif not provider:
        provider = os.getenv("LLM_PROVIDER", "ollama")
        model = os.getenv("LLM_MODEL", model or "tinyllama")
        api_base = os.getenv("LLM_API_BASE", api_base or "http://localhost:11434")
        api_key = os.getenv("LLM_API_KEY", api_key or "ollama")

    provider = provider or "ollama"
    model = model or "tinyllama"

    if provider == "ollama":
        host = getattr(config, "ollama_host", None) or api_base or "http://localhost:11434"
        api_base = host.rstrip("/")
        if not api_base.endswith("/v1"):
            api_base = f"{api_base}/v1"
        api_key = api_key or "ollama"

    llm_config = LLMConfig(
        provider=provider,
        model=model,
        api_base=api_base,
        api_key=api_key,
        request_timeout=request_timeout,
        max_retries=max_retries,
        num_ctx=num_ctx,
        temperature=temperature,
    )

    if provider == "llama-cpp":
        llm_config.model_path = model
        llm_config.n_gpu_layers = getattr(config, "llama_cpp_gpu_layers", -1)
        llm_config.n_ctx = getattr(config, "llama_cpp_context_size", num_ctx)
    elif provider == "litellm":
        llm_config.litellm_model_name = model

    logger.info(f"Created LLM client: {provider}/{model}")
    return LLMClient(llm_config)


def create_llm_client_from_env() -> LLMClient:
    """Create LLM client from environment variables."""

    # Check environment variables for provider choice
    provider = os.getenv("LLM_PROVIDER", "ollama")
    model = os.getenv("LLM_MODEL", "gpt-oss-120b")
    api_base = os.getenv("LLM_API_BASE")
    api_key = os.getenv("LLM_API_KEY", "ollama")

    llm_config = LLMConfig(
        provider=provider,
        model=model,
        api_base=api_base,
        api_key=api_key,
        request_timeout=float(os.getenv("LLM_TIMEOUT", "120.0")),
        max_retries=int(os.getenv("LLM_MAX_RETRIES", "6")),
        num_ctx=int(os.getenv("LLM_NUM_CTX", "8192")),
    )

    # Add provider-specific configurations
    if provider == "llama-cpp":
        llm_config.model_path = os.getenv("LLAMA_CPP_MODEL_PATH", model)
        llm_config.n_gpu_layers = int(os.getenv("LLAMA_CPP_GPU_LAYERS", "-1"))
        llm_config.n_ctx = int(os.getenv("LLAMA_CPP_N_CTX", "8192"))
    elif provider == "litellm":
        llm_config.litellm_model_name = os.getenv("LITELLM_MODEL_NAME", model)

    logger.info(f"Created LLM client from env: {provider}/{model}")
    return LLMClient(llm_config)


def create_ollama_client(
    model: str = "gpt-oss-120b",
    host: str = "localhost",
    port: int = 11434,
    *,
    request_timeout: float | None = None,
    max_retries: int | None = None,
) -> LLMClient:
    """Create Ollama client with specific model and host."""
    api_base = host if host.startswith("http") else f"http://{host}:{port}"

    llm_config = LLMConfig(
        provider="ollama",
        model=model,
        api_base=api_base,
        api_key="ollama",
        num_ctx=8192,
        keep_alive="1h",
        request_timeout=request_timeout or 120.0,
        max_retries=max_retries or 6,
    )

    logger.info(f"Created Ollama client: {model}@{host}:{port}")
    return LLMClient(llm_config)


def create_llama_cpp_client(
    model_path: str,
    n_gpu_layers: int = -1,
    n_ctx: int = 8192,
    *,
    request_timeout: float | None = None,
    max_retries: int | None = None,
) -> LLMClient:
    """Create llama-cpp-python client with specific model."""
    llm_config = LLMConfig(
        provider="llama-cpp",
        model=model_path,
        model_path=model_path,
        n_gpu_layers=n_gpu_layers,
        n_ctx=n_ctx,
        request_timeout=request_timeout or 120.0,
        max_retries=max_retries or 6,
    )

    logger.info(f"Created llama-cpp client: {model_path}")
    return LLMClient(llm_config)


def create_litellm_client(
    model: str,
    *,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    request_timeout: float | None = None,
    max_retries: int | None = None,
) -> LLMClient:
    """Create LiteLLM client with specific model.
    
    For OpenAI-compatible APIs (like LM Studio), set api_base to the base URL.
    The model name should be the actual model identifier (e.g., 'llama-3.1-8b-instruct').
    """
    llm_config = LLMConfig(
        provider="litellm",
        model=model,
        api_key=api_key,
        api_base=api_base,
        litellm_model_name=model,
        request_timeout=request_timeout or 120.0,
        max_retries=max_retries or 6,
    )

    logger.info(f"Created LiteLLM client: {model} (api_base: {api_base})")
    return LLMClient(llm_config)


def create_azure_client(
    *,
    model: str,
    api_base: str,
    api_key: str,
    request_timeout: float | None = None,
    max_retries: int | None = None,
) -> LLMClient:
    """Create Azure OpenAI client."""
    llm_config = LLMConfig(
        provider="azure",
        model=model,
        api_base=api_base,
        api_key=api_key,
        request_timeout=request_timeout or 120.0,
        max_retries=max_retries or 6,
    )

    logger.info(f"Created Azure client: {model}")
    return LLMClient(llm_config)


def create_openai_client(
    *,
    model: str,
    api_key: str,
    api_base: Optional[str] = None,
    request_timeout: float | None = None,
    max_retries: int | None = None,
) -> LLMClient:
    """Create OpenAI client."""
    llm_config = LLMConfig(
        provider="openai",
        model=model,
        api_base=api_base,
        api_key=api_key,
        request_timeout=request_timeout or 120.0,
        max_retries=max_retries or 6,
    )

    logger.info(f"Created OpenAI client: {model}")
    return LLMClient(llm_config)
