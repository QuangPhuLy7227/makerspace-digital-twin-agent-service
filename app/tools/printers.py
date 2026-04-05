from typing import Optional


MOCK_PRINTERS = {
    "P1": {
        "id": "P1",
        "status": "IDLE",
        "active_task_id": None,
    },
    "P2": {
        "id": "P2",
        "status": "RUNNING",
        "active_task_id": "15",
    },
    "P3": {
        "id": "P3",
        "status": "QUEUED",
        "active_task_id": None,
    },
}


async def get_printer_status(printer_id: str) -> Optional[dict]:
    return MOCK_PRINTERS.get(printer_id)