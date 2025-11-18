"""Utility functions for proper subprocess management and cleanup."""

import asyncio
import logging
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _get_cargo_bin_path() -> Path:
    """Get the cargo bin directory path where subcommands are installed."""
    # Check CARGO_HOME environment variable first
    cargo_home = os.environ.get("CARGO_HOME")
    if cargo_home:
        return Path(cargo_home) / "bin"
    
    # Default location: ~/.cargo/bin (Unix) or %USERPROFILE%\.cargo\bin (Windows)
    home_dir = Path.home()
    if platform.system() == "Windows":
        return home_dir / ".cargo" / "bin"
    else:
        return home_dir / ".cargo" / "bin"


def _get_env_with_cargo_path() -> Dict[str, str]:
    """Get environment variables with cargo bin directory added to PATH."""
    env = os.environ.copy()
    cargo_bin = _get_cargo_bin_path()
    cargo_bin_str = str(cargo_bin)
    
    # Get current PATH
    current_path = env.get("PATH", "")
    
    # Add cargo bin to PATH if it's not already there
    if cargo_bin_str not in current_path:
        if platform.system() == "Windows":
            env["PATH"] = f"{cargo_bin_str};{current_path}"
        else:
            env["PATH"] = f"{cargo_bin_str}:{current_path}"
    
    return env


async def run_command_with_cleanup(
    command: List[str],
    cwd: Path,
    logger: Optional[logging.Logger] = None,
) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    """
    Runs a command with proper cleanup to prevent asyncio transport warnings.

    Args:
        command: The command to run as a list of strings
        cwd: Working directory for the command
        logger: Optional logger for debug messages

    Returns:
        Tuple of (results, error_message)
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    logger.info("Running command: %s in %s", " ".join(command), cwd)
    process = None

    # Ensure cargo bin directory is in PATH for cargo subcommands
    env = _get_env_with_cargo_path()

    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,  # Use environment with cargo bin in PATH
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            logger.warning(
                "Command failed with exit code %d", process.returncode
            )
            logger.warning("Stderr: %s", stderr.decode(errors="ignore"))

        results = []
        if stdout:
            for line in stdout.decode(errors="ignore").splitlines():
                if line.strip():
                    try:
                        import json

                        results.append(json.loads(line))
                    except json.JSONDecodeError:
                        logger.warning("Could not parse JSON line: %s", line)
        return results, None

    except subprocess.TimeoutExpired as e:
        logger.error("Command timed out: %s", e)
        return None, f"Command timed out: {str(e)}"
    except subprocess.SubprocessError as e:
        logger.error("Subprocess error: %s", e)
        return None, f"Subprocess error: {str(e)}"
    except OSError as e:
        logger.error("OS error running command: %s", e)
        return None, f"OS error: {str(e)}"
    except asyncio.TimeoutError as e:
        logger.error("Async timeout error: %s", e)
        return None, f"Async timeout: {str(e)}"
    except Exception as e:
        logger.error("Unexpected error running command: %s", e)
        return None, f"Unexpected error: {str(e)}"

    finally:
        await cleanup_subprocess(process, logger)


async def cleanup_subprocess(
    process: Optional[asyncio.subprocess.Process],
    logger: Optional[logging.Logger] = None,
) -> None:
    """
    Properly cleans up a subprocess to prevent asyncio transport warnings.
    
    On Windows with ProactorEventLoop, transports must be closed carefully
    to avoid "I/O operation on closed pipe" errors.

    Args:
        process: The subprocess to cleanup
        logger: Optional logger for debug messages
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    if process is None:
        return

    try:
        # Check if process is still running
        if process.returncode is None:
            # Try to terminate gracefully first
            try:
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    # Force kill if termination doesn't work
                    process.kill()
                    await process.wait()
            except (ProcessLookupError, ValueError):
                # Process already terminated or doesn't exist
                pass

        # Explicitly close transport to prevent ResourceWarning
        # On Windows ProactorEventLoop, we need to be careful about accessing closed transports
        try:
            if hasattr(process, "_transport") and process._transport is not None:
                transport = process._transport
                # Check if transport is already closed before trying to close it
                if hasattr(transport, "_closed") and not transport._closed:
                    transport.close()
                elif not hasattr(transport, "_closed"):
                    # If _closed attribute doesn't exist, try to close anyway
                    # but catch any errors
                    try:
                        transport.close()
                    except (ValueError, OSError):
                        # Transport already closed or pipe is closed - this is OK
                        pass
        except (AttributeError, ValueError, OSError) as transport_error:
            # Transport may already be closed or not accessible
            # This is expected on Windows ProactorEventLoop after process completion
            logger.debug("Transport cleanup note (expected on Windows): %s", transport_error)
        except Exception as cleanup_error:
            # Log unexpected errors but don't fail
            logger.debug("Unexpected error during transport cleanup: %s", cleanup_error)

    except (ProcessLookupError, asyncio.TimeoutError, ValueError) as cleanup_error:
        # These are expected in some cases (process already gone, etc.)
        logger.debug("Process cleanup note: %s", cleanup_error)
    except Exception as cleanup_error:
        logger.debug("Unexpected error during process cleanup: %s", cleanup_error)


def setup_asyncio_windows_fixes() -> None:
    """
    Apply Windows-specific fixes for asyncio subprocess issues.

    This function should be called early in the application startup
    to prevent asyncio transport warnings on Windows.
    """
    if sys.platform == "win32":
        # Set up proper event loop policy for Windows
        if hasattr(asyncio, "WindowsProactorEventLoopPolicy"):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        # Suppress ResourceWarning for unclosed transports
        # On Windows ProactorEventLoop, transports are automatically closed
        # when processes complete, but Python's __del__ methods try to access
        # them during garbage collection, causing warnings
        import warnings

        warnings.filterwarnings(
            "ignore",
            message="unclosed transport",
            category=ResourceWarning,
        )
        warnings.filterwarnings(
            "ignore",
            message="I/O operation on closed pipe",
            category=ResourceWarning,
        )
        # Also suppress the specific ValueError from __del__ methods
        warnings.filterwarnings(
            "ignore",
            message=".*I/O operation on closed pipe.*",
            category=ResourceWarning,
        )
