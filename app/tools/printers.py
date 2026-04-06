from typing import Any, Optional

from app.dependencies import get_backend_client


async def list_printers() -> list[dict]:
    client = get_backend_client()
    data = await client.get("/api/printers")
    return data if isinstance(data, list) else []


async def get_printer(device_id: str) -> Optional[dict]:
    client = get_backend_client()
    return await client.try_get(f"/api/printers/{device_id}")


async def get_printer_firmware(device_id: str) -> Optional[dict]:
    client = get_backend_client()
    return await client.try_get(f"/api/printers/{device_id}/firmware")


async def get_printer_ams_units(device_id: str) -> list[dict]:
    client = get_backend_client()
    data = await client.try_get(f"/api/printers/{device_id}/ams-units")
    return data if isinstance(data, list) else []


async def get_printer_tasks(device_id: str) -> list[dict]:
    client = get_backend_client()
    data = await client.try_get(f"/api/printers/{device_id}/tasks")
    return data if isinstance(data, list) else []


async def get_printer_messages(device_id: str) -> list[dict]:
    client = get_backend_client()
    data = await client.try_get(f"/api/printers/{device_id}/messages")
    return data if isinstance(data, list) else []


async def get_printer_timeline(device_id: str) -> list[dict]:
    client = get_backend_client()
    data = await client.try_get(f"/api/printers/{device_id}/timeline")
    return data if isinstance(data, list) else []


async def get_running_printers() -> list[dict]:
    client = get_backend_client()
    data = await client.try_get("/api/printers/running")
    return data if isinstance(data, list) else []


async def get_printer_telemetry(device_id: str, minutes: int = 30) -> list[dict]:
    client = get_backend_client()
    data = await client.try_get(f"/api/printers/{device_id}/telemetry", params={"minutes": minutes})
    return data if isinstance(data, list) else []


async def simulate_printer_start(
    device_id: str,
    design_title: str,
    simulated_duration_seconds: int,
) -> Optional[Any]:
    client = get_backend_client()
    return await client.try_post(
        f"/api/printers/{device_id}/simulate/start",
        payload={
            "designTitle": design_title,
            "simulatedDurationSeconds": simulated_duration_seconds,
        },
    )


async def simulate_printer_stop(device_id: str) -> Optional[Any]:
    client = get_backend_client()
    return await client.try_post(f"/api/printers/{device_id}/simulate/stop")