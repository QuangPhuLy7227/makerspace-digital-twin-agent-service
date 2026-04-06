from typing import Optional

from app.dependencies import get_backend_client


async def list_messages() -> list[dict]:
    client = get_backend_client()
    data = await client.get("/api/messages")
    return data if isinstance(data, list) else []


async def get_message(message_id: str) -> Optional[dict]:
    client = get_backend_client()
    return await client.try_get(f"/api/messages/{message_id}")


async def get_messages_for_task(task_id: str) -> list[dict]:
    messages = await list_messages()
    return [m for m in messages if str(m.get("externalTaskId")) == str(task_id)]


async def get_latest_message_for_task(task_id: str) -> Optional[dict]:
    matches = await get_messages_for_task(task_id)
    if not matches:
        return None
    matches.sort(key=lambda m: m.get("createTimeUtc", ""), reverse=True)
    return matches[0]