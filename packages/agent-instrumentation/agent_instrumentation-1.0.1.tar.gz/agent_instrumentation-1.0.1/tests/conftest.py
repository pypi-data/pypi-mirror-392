# tests/conftest.py
"""Pytest configuration and shared fixtures."""

import os
import pytest
from typing import Generator, Dict


@pytest.fixture
def clean_environment() -> Generator[None, None, None]:
    """
    Fixture to clean up environment variables before and after tests.

    Yields control to the test and restores the original environment afterward.
    """
    # Save original environment
    original_env = os.environ.copy()

    # Remove AMP-related environment variables
    amp_vars = [
        "AMP_APP_NAME",
        "AMP_OTEL_EXPORTER_OTLP_ENDPOINT",
        "AMP_API_KEY",
    ]

    for var in amp_vars:
        os.environ.pop(var, None)

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def set_env_vars() -> Dict[str, str]:
    """
    Fixture providing a valid set of environment variables.

    Returns:
        Dictionary with valid AMP configuration
    """
    return {
        "AMP_APP_NAME": "test-app",
        "AMP_OTEL_EXPORTER_OTLP_ENDPOINT": "https://otel.example.com",
        "AMP_API_KEY": "test-api-key",
    }


@pytest.fixture
def configure_environment(clean_environment, set_env_vars) -> Dict[str, str]:
    """
    Fixture that sets valid environment variables for testing.

    Args:
        clean_environment: Fixture that ensures clean environment
        set_env_vars: Fixture with valid configuration

    Returns:
        Dictionary with the set environment variables
    """
    for key, value in set_env_vars.items():
        os.environ[key] = value
    return set_env_vars


@pytest.fixture
def mock_traceloop(monkeypatch):
    """
    Fixture to mock the Traceloop SDK to avoid actual initialization during tests.

    Args:
        monkeypatch: Pytest monkeypatch fixture
    """
    class MockTraceloop:
        initialized = False
        init_kwargs = {}

        @classmethod
        def init(cls, **kwargs):
            cls.initialized = True
            cls.init_kwargs = kwargs

        @classmethod
        def reset(cls):
            """Reset class state for clean test isolation."""
            cls.initialized = False
            cls.init_kwargs = {}

    # Reset state before each test
    MockTraceloop.reset()

    # Mock the import
    import sys
    from unittest.mock import MagicMock

    mock_module = MagicMock()
    mock_module.Traceloop = MockTraceloop
    sys.modules['traceloop.sdk'] = mock_module

    yield MockTraceloop

    # Clean up
    if 'traceloop.sdk' in sys.modules:
        del sys.modules['traceloop.sdk']
    if 'traceloop' in sys.modules:
        del sys.modules['traceloop']
