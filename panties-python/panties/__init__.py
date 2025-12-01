# panties/__init__.py
from typing import Optional, Dict, Any

from .client import PantiesClient
from .state import set_client, get_client
from .hooks import install_global_excepthook, install_threading_excepthook
from .decorators import capture_exceptions, capture_exceptions_ctx

__all__ = [
    "init",
    "capture_exception",
    "capture_message",
    "get_client",
    "capture_exceptions",
    "capture_exceptions_ctx",
]


def init(
    api_token: str,
    endpoint: str,
    environment: str = "production",
    service_name: str = "default-service",
    timeout: float = 2.0,
    install_sys_hook: bool = True,
    install_thread_hook: bool = True,
) -> PantiesClient:
    """
    Inizializza il client globale di panties e registra gli hook sulle eccezioni.

    Va chiamato il prima possibile nel processo (es. all'avvio dell'app).
    """
    client = PantiesClient(
        api_token=api_token,
        endpoint=endpoint,
        environment=environment,
        service_name=service_name,
        timeout=timeout,
    )
    set_client(client)

    if install_sys_hook:
        install_global_excepthook()
    if install_thread_hook:
        install_threading_excepthook()

    return client


def capture_exception(
    exc_type=None,
    exc_value=None,
    tb=None,
    extra: Optional[Dict[str, Any]] = None,
    tags: Optional[Dict[str, str]] = None,
) -> None:
    """
    API pubblica per inviare un'eccezione.

    - Se exc_type/ exc_value/ tb non sono passati, usa l'eccezione corrente (sys.exc_info()).
    """
    client = get_client()
    if client is None:
        return
    client.capture_exception(exc_type, exc_value, tb, extra=extra, tags=tags)


def capture_message(
    message: str,
    level: str = "info",
    extra: Optional[Dict[str, Any]] = None,
    tags: Optional[Dict[str, str]] = None,
) -> None:
    """
    API pubblica per inviare un messaggio (non necessariamente un'eccezione).
    """
    client = get_client()
    if client is None:
        return
    client.capture_message(message, level=level, extra=extra, tags=tags)
