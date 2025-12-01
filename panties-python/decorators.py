# panties/decorators.py
from contextlib import contextmanager
from typing import Callable, TypeVar, Any

from .state import get_client

F = TypeVar("F", bound=Callable[..., Any])


def capture_exceptions(func: F) -> F:
    """
    Decorator che cattura tutte le eccezioni della funzione, le invia a panties
    e poi le rilancia.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            client = get_client()
            if client is not None:
                client.capture_exception()
            raise

    return wrapper  # type: ignore[return-value]


@contextmanager
def capture_exceptions_ctx():
    """
    Context manager che cattura le eccezioni nello scope del blocco.
    """
    try:
        yield
    except Exception:
        client = get_client()
        if client is not None:
            client.capture_exception()
        raise
