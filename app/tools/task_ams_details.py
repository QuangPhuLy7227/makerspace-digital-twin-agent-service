from app.dependencies import get_backend_client


async def list_task_ams_details() -> list[dict]:
    client = get_backend_client()
    data = await client.get("/api/task-ams-details")
    return data if isinstance(data, list) else []


async def get_task_ams_details_by_task(task_id: str) -> list[dict]:
    client = get_backend_client()
    data = await client.try_get(f"/api/task-ams-details/by-task/{task_id}")
    return data if isinstance(data, list) else []


async def get_task_ams_details_by_task_alias(task_alias: str) -> list[dict]:
    client = get_backend_client()
    data = await client.try_get(f"/api/task-ams-details/by-task-alias/{task_alias}")
    return data if isinstance(data, list) else []