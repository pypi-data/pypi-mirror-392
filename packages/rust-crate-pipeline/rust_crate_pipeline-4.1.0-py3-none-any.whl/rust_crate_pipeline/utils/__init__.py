"""Utility helpers for the :mod:`rust_crate_pipeline` package.

The helper modules historically lived as loose files that were imported by
mutating ``sys.path`` inside scripts.  Treating them as a proper subpackage
allows every consumer to rely on normal relative imports, which keeps the
package importable once it has been installed with ``pip install -e .``.
"""

from . import resume_utils
# Removed unused imports: tagging, version_policy (not used anywhere)
# Advanced cache moved to experimental/future_modules - import only if needed
try:
    import sys
    from pathlib import Path
    experimental_path = Path(__file__).parent.parent.parent / "experimental" / "future_modules"
    if str(experimental_path) not in sys.path:
        sys.path.insert(0, str(experimental_path))
    from advanced_cache import (AdvancedCache, CacheEntry, CacheMetrics,
                                 CacheStrategy, DiskCache, MemoryCache, RedisCache,
                                 get_cache)
except ImportError:
    # Advanced cache not available - it's in experimental/future_modules
    AdvancedCache = None
    CacheEntry = None
    CacheMetrics = None
    CacheStrategy = None
    DiskCache = None
    MemoryCache = None
    RedisCache = None
    get_cache = None
from .code_example_quality import is_high_quality_example
from .file_utils import atomic_write_json
from .local_rag_manager import LocalRAGManager
from .logging_utils import configure_logging
from .rust_code_analyzer import RustCodeAnalyzer
from .serialization_utils import add_field_explanations, to_serializable
from .status_utils import ProgressTracker, status, with_retry
from .subprocess_utils import (cleanup_subprocess, run_command_with_cleanup,
                               setup_asyncio_windows_fixes)

# Export the high-level resume helpers directly so callers can simply import
# from :mod:`rust_crate_pipeline.utils` without reaching into submodules.
from .resume_utils import (create_resume_report, get_processed_crates,
                           get_remaining_crates, load_crate_list,
                           validate_resume_state)

__all__ = [
    # Cache helpers (optional, from experimental/future_modules)
    # "AdvancedCache",  # Moved to experimental/future_modules
    # "CacheEntry",  # Moved to experimental/future_modules
    # "CacheMetrics",  # Moved to experimental/future_modules
    # "CacheStrategy",  # Moved to experimental/future_modules
    # "DiskCache",  # Moved to experimental/future_modules
    # "MemoryCache",  # Moved to experimental/future_modules
    # "RedisCache",  # Moved to experimental/future_modules
    # "get_cache",  # Moved to experimental/future_modules
    # General utilities
    "atomic_write_json",
    "cleanup_subprocess",
    "configure_logging",
    "LocalRAGManager",
    "RustCodeAnalyzer",
    "is_high_quality_example",
    "run_command_with_cleanup",
    "setup_asyncio_windows_fixes",
    "status",
    "add_field_explanations",
    "to_serializable",
    "with_retry",
    "ProgressTracker",
    # Resume utilities
    "create_resume_report",
    "get_processed_crates",
    "get_remaining_crates",
    "load_crate_list",
    "validate_resume_state",
    # Submodules that remain part of the public surface area
    "resume_utils",
]
