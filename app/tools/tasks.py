from typing import Optional


MOCK_TASKS = {
    "42": {
        "id": "42",
        "status": "FAILED",
        "printer_id": "P1",
        "duration_seconds": 480,
    },
    "15": {
        "id": "15",
        "status": "RUNNING",
        "printer_id": "P2",
        "duration_seconds": 600,
    },
}

MOCK_TASK_HISTORY = {
    "42": [
        {"event_type": "QUEUED", "timestamp": "2026-04-04T14:00:00"},
        {"event_type": "RUNNING", "timestamp": "2026-04-04T14:03:00"},
        {"event_type": "STOPPED_WHILE_RUNNING", "timestamp": "2026-04-04T14:06:10"},
        {"event_type": "FAILED", "timestamp": "2026-04-04T14:06:10"},
    ],
    "15": [
        {"event_type": "QUEUED", "timestamp": "2026-04-04T15:00:00"},
        {"event_type": "RUNNING", "timestamp": "2026-04-04T15:02:00"},
    ],
}


async def get_task(task_id: str) -> Optional[dict]:
    return MOCK_TASKS.get(str(task_id))


async def get_task_history(task_id: str) -> list[dict]:
    return MOCK_TASK_HISTORY.get(str(task_id), [])