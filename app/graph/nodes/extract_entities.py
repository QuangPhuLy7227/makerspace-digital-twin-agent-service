import re
from app.graph.state import OrchestratorState

TASK_PATTERN = re.compile(r"\btask\s*(\d+)\b", re.IGNORECASE)
PRINTER_PATTERN = re.compile(r"\bprinter\s*([a-zA-Z0-9\-_]+)\b", re.IGNORECASE)


def extract_entities(state: OrchestratorState) -> OrchestratorState:
    text = state["user_input"]
    entities = {}

    task_match = TASK_PATTERN.search(text)
    printer_match = PRINTER_PATTERN.search(text)

    if task_match:
        entities["task_id"] = task_match.group(1)

    if printer_match:
        entities["printer_id"] = printer_match.group(1)

    state["extracted_entities"] = entities
    state["trace"].append({
        "node": "extract_entities",
        "entities": entities,
    })
    return state