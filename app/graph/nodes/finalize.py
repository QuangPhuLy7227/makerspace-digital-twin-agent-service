from app.graph.state import OrchestratorState


def finalize(state: OrchestratorState) -> OrchestratorState:
    state["trace"].append({
        "node": "finalize",
        "grounded": state.get("grounded", False),
        "confidence": state.get("confidence", 0.0),
        "session_memory_keys": list(state.get("session_memory", {}).keys()),
    })
    return state