from app.services.backend_client import BackendClient
from app.config import settings


def get_backend_client() -> BackendClient:
    return BackendClient(
        base_url=settings.backend_api_base,
        timeout_seconds=settings.backend_timeout_seconds,
    )