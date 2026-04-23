from functools import lru_cache

from app.services.backend_client import BackendClient
from app.memory.session_store import SessionStore
from app.config import settings


@lru_cache(maxsize=1)
def get_backend_client() -> BackendClient:
    return BackendClient(
        base_url=settings.backend_api_base,
        timeout_seconds=settings.backend_timeout_seconds,
    )


@lru_cache(maxsize=1)
def get_session_store() -> SessionStore:
    return SessionStore()