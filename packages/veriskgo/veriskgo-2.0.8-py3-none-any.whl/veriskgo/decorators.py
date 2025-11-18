# src/veriskgo/decorators.py

"""
Auto-span decorator for functions
Uses OpenTelemetry global tracer
"""

from functools import wraps
from opentelemetry import trace


def trace_span(name: str):
    """
    Decorator that automatically creates a span around a function.
    Example:
        @trace_span("llm.generate")
        def foo():
            return 123
    """
    tracer = trace.get_tracer("veriskgo.auto")

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(name) as span:
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("success", True)
                    return result
                except Exception as e:
                    span.set_attribute("success", False)
                    span.set_attribute("error.message", str(e))
                    raise

        return wrapper

    return decorator
