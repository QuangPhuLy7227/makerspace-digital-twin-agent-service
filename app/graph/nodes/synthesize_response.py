from app.graph.state import OrchestratorState

def synthesize_response(state: OrchestratorState) -> OrchestratorState:
    agent_output = state.get("agent_output", {})
    response = agent_output.get("user_response", "I could not produce an answer.")

    if state.get("convai_mode"):
        response = f"{response}"

    state["final_response"] = response
    state["trace"].append({
        "node": "synthesize_response",
        "final_response_preview": response[:120],
    })
    return state