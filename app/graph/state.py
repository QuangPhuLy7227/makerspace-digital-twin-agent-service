from typing import TypedDict, Any, Dict, List, Optional


class OrchestratorState(TypedDict, total=False):
    request_id: str
    session_id: str
    user_input: str
    convai_mode: bool
    metadata: Dict[str, Any]

    intent: str
    selected_agent: str

    extracted_entities: Dict[str, Any]
    tool_results: Dict[str, Any]
    agent_output: Dict[str, Any]

    final_response: str
    confidence: float
    grounded: bool

    errors: List[str]
    trace: List[Dict[str, Any]]