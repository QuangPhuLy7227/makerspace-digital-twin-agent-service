from typing import Any, Dict, Optional
import httpx


class BackendClient:
    def __init__(self, base_url: str, timeout_seconds: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    async def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    async def post(self, path: str, payload: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(url, json=payload or {})
            response.raise_for_status()
            if response.content:
                return response.json()
            return {"status": "ok"}

    async def try_get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        try:
            return await self.get(path, params=params)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return None
            raise

    async def try_post(self, path: str, payload: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        try:
            return await self.post(path, payload=payload)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return None
            raise