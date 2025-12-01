# panties/client.py
import sys
import time
import uuid
import traceback
from typing import Optional, Dict, Any

from .transport import HttpTransport


class PantiesClient:
    """
    Client principale di panties.
    Si occupa di costruire gli eventi e delegare l'invio al transport.
    """

    def __init__(
        self,
        api_token: str,
        endpoint: str,
        environment: str = "production",
        service_name: str = "default-service",
        timeout: float = 2.0,
    ) -> None:
        self.api_token = api_token
        self.endpoint = endpoint
        self.environment = environment
        self.service_name = service_name
        self.transport = HttpTransport(
            endpoint=endpoint,
            api_token=api_token,
            timeout=timeout,
        )

    # ------- Event building -------

    def _base_event(self) -> Dict[str, Any]:
        return {
            "event_id": str(uuid.uuid4()),
            "timestamp": int(time.time()),
            "environment": self.environment,
            "service_name": self.service_name,
            "sdk": {
                "name": "panties-python",
                "version": "0.1.0",
            },
        }

    def _build_exception_event(
        self,
        exc_type,
        exc_value,
        tb,
        extra: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        # Stacktrace serializzato in forma semplice
        frames = traceback.format_tb(tb) if tb else []
        return {
            **self._base_event(),
            "type": "exception",
            "exception": {
                "type": exc_type.__name__ if exc_type else None,
                "message": str(exc_value),
                "stacktrace": frames,
            },
            "tags": tags or {},
            "extra": extra or {},
        }

    def _build_message_event(
        self,
        message: str,
        level: str = "info",
        extra: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        return {
            **self._base_event(),
            "type": "message",
            "message": {
                "text": message,
                "level": level,
            },
            "tags": tags or {},
            "extra": extra or {},
        }

    # ------- Public capture methods -------

    def capture_exception(
        self,
        exc_type=None,
        exc_value=None,
        tb=None,
        extra: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Invia un'eccezione al backend panties.

        Se exc_type/ exc_value/ tb non sono specificati, usa sys.exc_info().
        """
        if exc_type is None or exc_value is None or tb is None:
            exc_type, exc_value, tb = sys.exc_info()

        if exc_type is None:
            # Nessuna eccezione corrente
            return

        event = self._build_exception_event(
            exc_type=exc_type,
            exc_value=exc_value,
            tb=tb,
            extra=extra,
            tags=tags,
        )
        self.transport.send(event)

    def capture_message(
        self,
        message: str,
        level: str = "info",
        extra: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Invia un evento di tipo "message".
        """
        event = self._build_message_event(
            message=message,
            level=level,
            extra=extra,
            tags=tags,
        )
        self.transport.send(event)
