from typing import Optional, Any

from app.dependencies import get_backend_client


async def create_scheduled_print_job(
    file_name: str,
    priority: int,
    allow_any_printer: bool = True,
    preferred_printer_id: Optional[str] = None,
) -> Optional[Any]:
    client = get_backend_client()
    payload = {
        "fileName": file_name,
        "priority": priority,
        "allowAnyPrinter": allow_any_printer,
    }
    if preferred_printer_id:
        payload["preferredPrinterId"] = preferred_printer_id

    return await client.try_post("/api/scheduled-print-jobs", payload=payload)


async def list_scheduled_print_jobs() -> list[dict]:
    client = get_backend_client()
    data = await client.get("/api/scheduled-print-jobs")
    return data if isinstance(data, list) else []


async def run_dispatch_cycle() -> Optional[Any]:
    client = get_backend_client()
    return await client.try_post("/api/scheduled-print-jobs/run-dispatch-cycle")


async def update_scheduled_job_priority(job_id: str, priority: int) -> Optional[Any]:
    client = get_backend_client()
    return await client.try_post(
        f"/api/scheduled-print-jobs/{job_id}/priority",
        payload={"priority": priority},
    )


async def get_queue_preview() -> list[dict]:
    client = get_backend_client()
    data = await client.try_get("/api/scheduled-print-jobs/queue-preview")
    return data if isinstance(data, list) else []


async def reconcile_scheduled_jobs() -> Optional[Any]:
    client = get_backend_client()
    return await client.try_post("/api/scheduled-print-jobs/reconcile")


async def set_scheduler_control(is_paused: bool, pause_reason: Optional[str]) -> Optional[Any]:
    client = get_backend_client()
    return await client.try_post(
        "/api/scheduled-print-jobs/scheduler-control",
        payload={
            "isPaused": is_paused,
            "pauseReason": pause_reason,
        },
    )


async def get_scheduler_control() -> Optional[dict]:
    client = get_backend_client()
    return await client.try_get("/api/scheduled-print-jobs/scheduler-control")