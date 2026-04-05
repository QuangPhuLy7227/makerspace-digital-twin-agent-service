from app.graph.state import OrchestratorState


def classify_intent(state: OrchestratorState) -> OrchestratorState:
    text = state["user_input"].lower()

    if any(k in text for k in ["why", "what happened", "explain", "reason"]):
        intent = "explanation"
    elif any(k in text for k in ["retry", "recover", "requeue", "what next"]):
        intent = "recovery"
    elif any(k in text for k in ["inventory", "stock", "material", "tool"]):
        intent = "inventory"
    elif any(k in text for k in ["schedule", "assign", "best printer", "queue"]):
        intent = "schedule"
    else:
        intent = "explanation"

    state["intent"] = intent
    state["trace"].append({
        "node": "classify_intent",
        "intent": intent,
    })
    return state