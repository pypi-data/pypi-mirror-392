# src/agent_instrumentation/_bootstrap/initialization.py
"""
Instrumentation initialization logic.
This module contains the core initialization function for instrumentation.
"""

import os
import logging
import threading
from . import environment_variables as env_vars

logger = logging.getLogger(__name__)

# Track initialization state with thread safety
_initialized = False
_init_lock = threading.Lock()


class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid."""
    pass


def _get_required_env_var(var_name: str) -> str:
    """
    Get a required environment variable or raise ConfigurationError.

    Raises:
        ConfigurationError: If the variable is missing or empty.
    """
    value = os.getenv(var_name)
    if not value or not value.strip():
        raise ConfigurationError(
            f"Required environment variable '{var_name}' is not set or is empty. "
            f"Please set this variable before running the application."
        )
    return value.strip()


def initialize_instrumentation() -> None:
    """
    Initialize instrumentation from environment variables.
    """
    global _initialized

    with _init_lock:
        if _initialized:
            logger.debug("Instrumentation already initialized, skipping.")
            return

        try:
            # Validate and read required configuration
            app_name = _get_required_env_var(env_vars.AMP_APP_NAME)
            otel_endpoint = _get_required_env_var(env_vars.AMP_OTEL_EXPORTER_OTLP_ENDPOINT)
            api_key = _get_required_env_var(env_vars.AMP_API_KEY)

            # Set Traceloop environment variables
            os.environ[env_vars.TRACELOOP_TRACE_CONTENT] = "true"
            os.environ[env_vars.TRACELOOP_METRICS_ENABLED] = "false"
            os.environ[env_vars.OTEL_EXPORTER_OTLP_INSECURE] = "true"

            # Import and initialize Traceloop
            from traceloop.sdk import Traceloop

            # Initialize Traceloop with configuration
            Traceloop.init(
                telemetry_enabled=False,
                app_name=app_name,
                api_endpoint=otel_endpoint,
                headers={"x-api-key": api_key}
            )

            _initialized = True
            logger.info(f"Instrumentation initialized successfully for application: {app_name}")

        except ConfigurationError as e:
            logger.error(f"Configuration error: {e}")
            raise

        except ImportError as e:
            logger.error(f"Failed to import traceloop-sdk: {e}. Ensure traceloop-sdk is installed.")
            raise 


        except Exception as e:
            logger.error(f"Unexpected error during instrumentation initialization: {e}", exc_info=True)
            raise  
