from typing import Optional

from app.dependencies import get_backend_client


async def list_tasks() -> list[dict]:
    client = get_backend_client()
    data = await client.get("/api/tasks")
    return data if isinstance(data, list) else []


async def get_task(task_id: str) -> Optional[dict]:
    client = get_backend_client()
    return await client.try_get(f"/api/tasks/{task_id}")


async def get_task_summary(task_id: str) -> Optional[dict]:
    client = get_backend_client()
    return await client.try_get(f"/api/tasks/{task_id}/summary")