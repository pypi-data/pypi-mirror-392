# github_token_checker.py
"""
GitHub Token Checker Module
Lightweight version of the token checker for integration into the main pipeline.
"""

import asyncio
import logging
import os
import sys

import aiohttp


async def check_github_token_quick_async() -> tuple[bool, str]:
    """Async quick check if GitHub token is available and valid"""
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        return False, "GITHUB_TOKEN environment variable not set"

    if len(token) < 20:
        return False, "GITHUB_TOKEN seems too short - may be invalid"

    try:
        # Quick API check using aiohttp
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {token}",
        }

        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(
                "https://api.github.com/rate_limit", headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    remaining = data["resources"]["core"]["remaining"]
                    return True, f"Token valid, {remaining} API calls remaining"
                elif response.status == 401:
                    return False, "GitHub token is invalid or expired"
                else:
                    return (
                        False,
                        f"GitHub API returned status code: {response.status}",
                    )
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        return False, f"API request failed: {e}"
    except Exception as e:
        return False, f"Error checking token: {str(e)}"


def check_github_token_quick() -> tuple[bool, str]:
    """
    Synchronous wrapper for async token check.
    
    For backward compatibility. Prefer check_github_token_quick_async() in async contexts.
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're in an async context, we need to use a different approach
            # Create a new event loop in a thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run, check_github_token_quick_async()
                )
                return future.result()
        else:
            return loop.run_until_complete(check_github_token_quick_async())
    except RuntimeError:
        # No event loop, create one
        return asyncio.run(check_github_token_quick_async())


def prompt_for_token_setup() -> bool:
    """Prompt user to set up GitHub token"""
    print("\n" + "=" * 60)
    print("[KEY] GitHub Token Required")
    print("=" * 60)
    print("\nThe Rust Crate Pipeline requires a GitHub Personal Access Token")
    print("to access repository information and avoid rate limits.")
    print("\n[GUIDE] Quick Setup:")
    print("1. Get token: https://github.com/settings/tokens")
    print("2. Required scopes: public_repo, read:user")
    print("3. Set in environment:")
    print('   export GITHUB_TOKEN="your_token_here"')
    print("\n[TOOLS] Setup Scripts Available:")
    print("   ./setup_github_token.sh    (Interactive setup)")
    print("   python -m rust_crate_pipeline.github_token_checker  (Direct check)")
    print("\n" + "=" * 60)

    # Ask if user wants to continue without token (limited functionality)
    response = input("\nContinue without GitHub token? (y/N): ").strip().lower()

    if response in ["y", "yes"]:
        print("[WARNING] Running with limited GitHub API access (60 requests/hour)")
        print("   You may encounter rate limit warnings.")
        return True
    else:
        print("\n[STOP] Please set up your GitHub token and try again.")
        return False


def check_and_setup_github_token() -> bool:
    """Checks and sets up the GitHub token."""
    is_valid, message = check_github_token_quick()

    if is_valid:
        logging.debug(f"GitHub token check: {message}")
        return True

    # Token is missing or invalid
    logging.warning(f"GitHub token issue: {message}")

    # Check if we're in a non-interactive environment
    if not sys.stdin.isatty():
        logging.error("GitHub token not configured and running in non-interactive mode")
        logging.error("Set GITHUB_TOKEN environment variable before running")
        return False

    # Interactive prompt
    return prompt_for_token_setup()


if __name__ == "__main__":
    # Allow running this module directly for testing
    is_valid, message = check_github_token_quick()
    print(f"Token check: {'[OK]' if is_valid else '[FAIL]'} {message}")

    if not is_valid:
        check_and_setup_github_token()
