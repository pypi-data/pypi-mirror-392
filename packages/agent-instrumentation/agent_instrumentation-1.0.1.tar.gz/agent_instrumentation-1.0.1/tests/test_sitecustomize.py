# tests/test_sitecustomize.py
"""Tests for sitecustomize.py automatic initialization."""

import sys
import subprocess
from pathlib import Path


def test_sitecustomize_initialization_failure_exits_with_error():
    """
    Test that sitecustomize.py exits with error code 1 when initialization fails.
    """
    bootstrap_dir = Path(__file__).parent.parent / "src" / "agent_instrumentation" / "_bootstrap"

    # Test script that imports sitecustomize (which will fail due to missing env vars)
    script = 'import sitecustomize'

    # Run WITHOUT required environment variables to trigger initialization failure
    result = subprocess.run(
        [sys.executable, "-c", script],
        env={"PYTHONPATH": str(bootstrap_dir)},
        capture_output=True,
        text=True
    )

    # Should exit with error code 1
    assert result.returncode == 1, "Expected exit code 1 when initialization fails"

    # Should print error message to stderr
    assert "ERROR: AMP instrumentation failed" in result.stderr
    assert "Check your environment variables and configuration" in result.stderr


def test_sitecustomize_successful_initialization():
    """
    Test that sitecustomize.py initializes successfully when all env vars are set.

    This verifies that sitecustomize actually initializes instrumentation when
    imported with proper environment variable configuration.
    """
    bootstrap_dir = Path(__file__).parent.parent / "src" / "agent_instrumentation" / "_bootstrap"

    # Test script that imports sitecustomize and verifies initialization
    script = '''
import sitecustomize
from agent_instrumentation._bootstrap import initialization
# Check that initialization was successful
assert initialization._initialized is True, "Instrumentation should be initialized"
print("INIT_SUCCESS")
'''

    # Run with required environment variables
    env = {
        "PYTHONPATH": str(bootstrap_dir),
        "AMP_APP_NAME": "test-app",
        "AMP_OTEL_EXPORTER_OTLP_ENDPOINT": "https://otel.example.com",
        "AMP_API_KEY": "test-key"
    }

    result = subprocess.run(
        [sys.executable, "-c", script],
        env=env,
        capture_output=True,
        text=True
    )

    # Should exit successfully
    assert result.returncode == 0, f"Expected success but got: {result.stderr}"
    assert "INIT_SUCCESS" in result.stdout
