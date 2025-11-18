from unittest.mock import AsyncMock, Mock

import aiohttp
import pytest
import requests
import threading
import time

from rust_crate_pipeline.exceptions import ValidationError as PipelineValidationError
from rust_crate_pipeline.utils import http_session


def test_get_with_retry_eventual_success(monkeypatch):
    session = requests.Session()
    calls = {"count": 0}

    def fake_get(url, **kwargs):
        calls["count"] += 1
        if calls["count"] < 3:
            raise requests.RequestException("boom")
        return Mock(status_code=200)

    monkeypatch.setattr(session, "get", fake_get)
    monkeypatch.setattr(http_session, "_session", session)
    monkeypatch.setattr(http_session.time, "sleep", lambda _: None)

    resp = http_session.get_with_retry("http://example.com")
    assert resp.status_code == 200
    assert calls["count"] == 3


def test_get_with_retry_invalid_url():
    """Test that invalid URLs raise ValidationError."""
    with pytest.raises(PipelineValidationError):
        http_session.get_with_retry("not-a-url")
    with pytest.raises(PipelineValidationError):
        http_session.get_with_retry("ftp://example.com")
    with pytest.raises(PipelineValidationError):
        http_session.get_with_retry("http://")


@pytest.mark.asyncio
async def test_async_get_with_retry_success():
    session = AsyncMock()
    response = AsyncMock()
    response.status = 200
    session.get.return_value = response

    result = await http_session.async_get_with_retry(
        "http://example.com", session=session
    )

    assert result is response
    session.get.assert_called_once_with("http://example.com")


@pytest.mark.asyncio
async def test_async_get_with_retry_forcelist():
    session = AsyncMock()
    response = AsyncMock()
    response.status = 500
    response.text = AsyncMock(return_value="boom")
    response.release = AsyncMock()
    response.history = tuple()
    response.headers = {}
    response.request_info = Mock(real_url="http://example.com")
    session.get.return_value = response

    with pytest.raises(aiohttp.ClientResponseError):
        await http_session.async_get_with_retry(
            "http://example.com", session=session, retries=1
        )

    response.text.assert_awaited()
    response.release.assert_awaited()


def test_get_with_retry_all_fail(monkeypatch):
    session = requests.Session()
    calls = {"count": 0}

    def fake_get(url, **kwargs):
        calls["count"] += 1
        raise requests.RequestException("boom")

    monkeypatch.setattr(session, "get", fake_get)
    monkeypatch.setattr(http_session, "_session", session)
    monkeypatch.setattr(http_session.time, "sleep", lambda _: None)

    try:
        http_session.get_with_retry("http://example.com")
    except requests.RequestException:
        pass
    else:
        assert False, "Expected RequestException"

    assert calls["count"] == 3


def test_get_session_thread_safety():
    """Test that get_session is thread-safe."""
    results = []
    errors = []
    
    def get_session_in_thread(thread_id):
        try:
            session = http_session.get_session()
            results.append((thread_id, id(session)))
        except Exception as e:
            errors.append((thread_id, e))
    
    # Create multiple threads accessing get_session concurrently
    threads = []
    for i in range(10):
        thread = threading.Thread(target=get_session_in_thread, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Check that no errors occurred
    assert len(errors) == 0, f"Errors occurred: {errors}"
    
    # All threads should get the same session instance
    session_ids = [result[1] for result in results]
    assert len(set(session_ids)) == 1, "Multiple session instances created"


def test_get_session_expiration(monkeypatch):
    """Test that sessions expire after SESSION_MAX_AGE."""
    # Reset the global session
    http_session._session = None
    http_session._session_created_at = None
    
    # Get initial session
    session1 = http_session.get_session()
    session1_id = id(session1)
    
    # Mock time to simulate expiration
    original_time = time.time
    current_time = [original_time()]
    
    def mock_time():
        return current_time[0]
    
    monkeypatch.setattr(time, "time", mock_time)
    
    # Advance time past expiration
    current_time[0] += http_session.SESSION_MAX_AGE + 1
    
    # Get new session - should be different
    session2 = http_session.get_session()
    session2_id = id(session2)
    
    assert session1_id != session2_id, "Session should be refreshed after expiration"


def test_get_session_force_refresh(monkeypatch):
    """Test force_refresh parameter."""
    # Reset the global session
    http_session._session = None
    http_session._session_created_at = None
    
    # Get initial session
    session1 = http_session.get_session()
    session1_id = id(session1)
    
    # Force refresh
    session2 = http_session.get_session(force_refresh=True)
    session2_id = id(session2)
    
    assert session1_id != session2_id, "Force refresh should create new session"


def test_get_session_singleton():
    """Test that get_session returns the same instance."""
    # Reset the global session
    http_session._session = None
    http_session._session_created_at = None
    
    session1 = http_session.get_session()
    session2 = http_session.get_session()
    
    assert session1 is session2, "Should return the same session instance"
    assert isinstance(session1, requests.Session), "Should return a requests.Session"
