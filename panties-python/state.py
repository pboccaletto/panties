# panties/state.py
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .client import PantiesClient

_client: Optional["PantiesClient"] = None


def set_client(client: "PantiesClient") -> None:
    global _client
    _client = client


def get_client() -> Optional["PantiesClient"]:
    return _client
