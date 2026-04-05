async def get_queue_state() -> dict:
    return {
        "queued_jobs": 3,
        "running_jobs": 1,
        "idle_printers": 2,
    }