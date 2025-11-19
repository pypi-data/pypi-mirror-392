# src/agent_instrumentation/_bootstrap/sitecustomize.py
"""
This module is automatically loaded by Python at startup when PYTHONPATH includes
the _bootstrap directory. It initializes  instrumentation before any user code runs.
"""

import logging
import sys
from agent_instrumentation._bootstrap.initialization import initialize_instrumentation

# Configure logging only if not already configured
# Use NullHandler to avoid interfering with user's logging setup
logger = logging.getLogger(__name__)
if not logger.handlers:
    logger.addHandler(logging.NullHandler())

# Initialize automatically when this module is loaded
try:
    initialize_instrumentation()
    logger.info("AMP instrumentation initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize AMP instrumentation: {e}", exc_info=True)
    print(f"ERROR: AMP instrumentation failed: {e}", file=sys.stderr)
    print("Check your environment variables and configuration.", file=sys.stderr)
    sys.exit(1)
