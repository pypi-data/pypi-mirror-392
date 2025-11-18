from functools import wraps
from .tracer import start_span, end_span

def trace(name: str):
    def decorator(func):
        @wraps(func)
        def wrap(*a, **kw):
            span = start_span(name, input=f"{a} {kw}")
            try:
                result = func(*a, **kw)
                end_span(span, output=str(result), success=True)
                return result
            except Exception as e:
                end_span(span, output=str(e), success=False)
                raise
        return wrap
    return decorator
