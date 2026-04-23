from typing import Optional

from app.dependencies import get_backend_client


async def list_tasks() -> list[dict]:
    client = get_backend_client()
    data = await client.get("/api/tasks")
    return data if isinstance(data, list) else []


async def get_task(task_id: str) -> Optional[dict]:
    client = get_backend_client()
    return await client.try_get(f"/api/tasks/{task_id}")


async def get_task_by_alias(task_alias: str) -> Optional[dict]:
    client = get_backend_client()
    return await client.try_get(f"/api/tasks/by-alias/{task_alias}")


async def get_task_summary(task_id: str) -> Optional[dict]:
    client = get_backend_client()
    return await client.try_get(f"/api/tasks/{task_id}/summary")


async def get_task_summary_by_alias(task_alias: str) -> Optional[dict]:
    client = get_backend_client()
    return await client.try_get(f"/api/tasks/by-alias/{task_alias}/summary")