from typing import Any, Dict, Optional


class SessionStore:
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}

    def get(self, session_id: str) -> Dict[str, Any]:
        return self._store.get(session_id, {}).copy()

    def update(self, session_id: str, values: Dict[str, Any]) -> Dict[str, Any]:
        current = self._store.get(session_id, {})
        current.update(values)
        self._store[session_id] = current
        return current.copy()

    def set_last_entities(
        self,
        session_id: str,
        task_id: Optional[str] = None,
        task_alias: Optional[str] = None,
        device_id: Optional[str] = None,
        printer_name: Optional[str] = None,
        job_id: Optional[str] = None,
        agent_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        values: Dict[str, Any] = {}
        if task_id:
            values["last_task_id"] = task_id
        if task_alias:
            values["last_task_alias"] = task_alias
        if device_id:
            values["last_device_id"] = device_id
        if printer_name:
            values["last_printer_name"] = printer_name
        if job_id:
            values["last_job_id"] = job_id
        if agent_name:
            values["last_agent_name"] = agent_name
        return self.update(session_id, values)