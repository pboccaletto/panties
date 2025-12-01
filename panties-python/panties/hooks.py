# panties/hooks.py
import sys
import threading
from types import TracebackType
from typing import Optional, Type

from .state import get_client

_original_sys_excepthook = None
_original_threading_excepthook = None


def install_global_excepthook() -> None:
    """
    Sostituisce sys.excepthook con una versione che invia l'eccezione a panties
    e poi richiama l'hook originale.
    """
    global _original_sys_excepthook

    if _original_sys_excepthook is not None:
        # Già installato
        return

    _original_sys_excepthook = sys.excepthook

    def panties_excepthook(
        exc_type: Type[BaseException],
        exc_value: BaseException,
        tb: Optional[TracebackType],
    ) -> None:
        client = get_client()
        if client is not None:
            client.capture_exception(exc_type, exc_value, tb)
            # Flush the queue to ensure the event is sent before exit
            try:
                client.transport.flush(timeout=2.0)
            except Exception:
                pass

        if _original_sys_excepthook is not None:
            _original_sys_excepthook(exc_type, exc_value, tb)

    sys.excepthook = panties_excepthook


def install_threading_excepthook() -> None:
    """
    Installa un hook per eccezioni sollevate nei thread (Python 3.8+).
    Se threading.excepthook non è disponibile, non fa nulla.
    """
    if not hasattr(threading, "excepthook"):
        return

    global _original_threading_excepthook
    if _original_threading_excepthook is not None:
        # Già installato
        return

    _original_threading_excepthook = threading.excepthook

    def panties_thread_excepthook(args: "threading.ExceptHookArgs") -> None:
        client = get_client()
        if client is not None:
            client.capture_exception(
                exc_type=args.exc_type,
                exc_value=args.exc_value,
                tb=args.exc_traceback,
            )

        if _original_threading_excepthook is not None:
            _original_threading_excepthook(args)

    threading.excepthook = panties_thread_excepthook
