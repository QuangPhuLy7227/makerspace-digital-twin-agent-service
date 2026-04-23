import re
from app.graph.state import OrchestratorState


TASK_LABEL_PATTERN = re.compile(r"\btask\s*(\d+)\b", re.IGNORECASE)
LONG_NUMERIC_ID_PATTERN = re.compile(r"\b\d{9,20}\b")
DEVICE_ID_PATTERN = re.compile(r"\b[0-9A-Z]{12,20}\b")
JOB_GUID_PATTERN = re.compile(
    r"\b[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}\b"
)
FILE_NAME_PATTERN = re.compile(r"\b[\w\-.]+\.(?:3mf|stl|gcode|obj)\b", re.IGNORECASE)

# New
TASK_ALIAS_PATTERN = re.compile(r"\bPT-[A-Za-z0-9\-]+\b")
PRINTER_NAME_PATTERN = re.compile(
    r"\b(?:[A-F]\d{1,2}\s*-\s*[A-Za-z0-9 ]+|[A-F]\d{1,2}-[A-Za-z0-9 ]+|Lab-\s*[A-Za-z0-9 ]+|[A-Z]\d{1,2}-[A-Za-z0-9 ]+)\b"
)


def extract_entities(state: OrchestratorState) -> OrchestratorState:
    text = state["user_input"]
    entities = {}

    task_alias_match = TASK_ALIAS_PATTERN.search(text)
    if task_alias_match:
        entities["task_alias"] = task_alias_match.group(0)

    task_label_match = TASK_LABEL_PATTERN.search(text)
    if task_label_match:
        entities["task_id"] = task_label_match.group(1)

    if "task_id" not in entities and "task_alias" not in entities:
        long_num_match = LONG_NUMERIC_ID_PATTERN.search(text)
        if long_num_match:
            entities["task_id"] = long_num_match.group(0)

    device_match = DEVICE_ID_PATTERN.search(text)
    if device_match:
        entities["device_id"] = device_match.group(0)

    job_match = JOB_GUID_PATTERN.search(text)
    if job_match:
        entities["job_id"] = job_match.group(0)

    file_match = FILE_NAME_PATTERN.search(text)
    if file_match:
        entities["file_name"] = file_match.group(0)

    printer_name_match = PRINTER_NAME_PATTERN.search(text)
    if printer_name_match:
        entities["printer_name"] = printer_name_match.group(0).strip()

    state["extracted_entities"] = entities
    state["trace"].append({
        "node": "extract_entities",
        "entities": entities,
    })
    return state