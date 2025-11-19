# src/agent_instrumentation/_bootstrap/environment_variables.py
"""
Environment variable constants for instrumentation.
This module centralizes all environment variable names used for configuration.
"""

# Application Configuration
AMP_APP_NAME = "AMP_APP_NAME"
AMP_OTEL_EXPORTER_OTLP_ENDPOINT = "AMP_OTEL_EXPORTER_OTLP_ENDPOINT"
AMP_API_KEY = "AMP_API_KEY"

# Downstream environment variables that get set for Traceloop
TRACELOOP_TRACE_CONTENT = "TRACELOOP_TRACE_CONTENT"
TRACELOOP_METRICS_ENABLED = "TRACELOOP_METRICS_ENABLED"
OTEL_EXPORTER_OTLP_INSECURE = "OTEL_EXPORTER_OTLP_INSECURE"
