from app.graph.state import OrchestratorState


def synthesize_response(state: OrchestratorState) -> OrchestratorState:
    agent_output = state.get("agent_output", {})
    convai = agent_output.get("convai", {})

    if state.get("convai_mode") and convai:
        response = convai.get("spoken_answer") or agent_output.get("user_response", "")
    else:
        response = agent_output.get("user_response", "I could not produce an answer.")

    state["final_response"] = response
    state["convai"] = convai

    state["trace"].append({
        "node": "synthesize_response",
        "final_response_preview": response[:120],
        "convai_mode": state.get("convai_mode", False),
    })
    return state