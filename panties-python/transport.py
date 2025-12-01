# panties/transport.py
import json
import queue
import threading
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

__all__ = ["HttpTransport"]


class HttpTransport:
    """
    Transport HTTP asincrono:
    - queue in memoria
    - worker thread in background
    """

    def __init__(
        self,
        endpoint: str,
        api_token: str,
        timeout: float = 2.0,
        max_queue_size: int = 1000,
    ) -> None:
        self.endpoint = endpoint
        self.api_token = api_token
        self.timeout = timeout
        self._queue: "queue.Queue[Optional[Dict[str, Any]]]" = queue.Queue(
            maxsize=max_queue_size
        )
        self._worker = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker.start()

    def _worker_loop(self) -> None:
        while True:
            event = self._queue.get()
            if event is None:
                # Segnale di shutdown (non usato al momento)
                break
            try:
                self._send_sync(event)
            except Exception:
                # Qui potresti loggare su stderr, metriche, ecc.
                pass
            finally:
                self._queue.task_done()

    def _send_sync(self, event: Dict[str, Any]) -> None:
        body = json.dumps(event).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_token}",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                # Possibile gestione del body di risposta se serve
                response_body = resp.read()
                print(f"[Panties] Event sent successfully: {resp.status}")
                print(f"[Panties] Response: {response_body.decode('utf-8')}")
        except urllib.error.HTTPError as e:
            # In produzione: log o metriche per codice HTTP
            # e.code, e.read()
            error_body = e.read().decode('utf-8') if e.fp else 'No error body'
            print(f"[Panties] HTTP Error {e.code}: {error_body}")
        except urllib.error.URLError as e:
            # Problemi di rete
            print(f"[Panties] URL Error: {e.reason}")

    def send(self, event: Dict[str, Any]) -> None:
        """
        Inserisce l'evento in coda per l'invio asincrono.

        Se la coda è piena, al momento scarta l'evento.
        In produzione potresti voler fare:
        - bloccare
        - o implementare una policy di drop con log/metriche.
        """
        try:
            self._queue.put_nowait(event)
        except queue.Full:
            # Droppa l'evento silenziosamente per ora
            # (Puoi aggiungere logging/metriche)
            pass
