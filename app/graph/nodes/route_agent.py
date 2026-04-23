from app.graph.state import OrchestratorState


def route_agent(state: OrchestratorState) -> OrchestratorState:
    intent = state.get("intent", "explanation")

    mapping = {
        "explanation": "ExplanationAgent",
        "recovery": "RecoveryAgent",
        "inventory": "InventoryAgent",
        "schedule": "ScheduleAgent",
    }

    state["selected_agent"] = mapping.get(intent, "ExplanationAgent")
    state["trace"].append({
        "node": "route_agent",
        "selected_agent": state["selected_agent"],
    })
    return state