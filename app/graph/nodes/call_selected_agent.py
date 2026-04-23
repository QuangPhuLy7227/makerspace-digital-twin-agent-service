from app.graph.state import OrchestratorState
from app.agents.explanation_agent import ExplanationAgent
from app.agents.schedule_agent import ScheduleAgent


async def call_selected_agent(state: OrchestratorState) -> OrchestratorState:
    selected = state.get("selected_agent")

    if selected == "ExplanationAgent":
        agent = ExplanationAgent()
        output = await agent.run(state)
    elif selected == "ScheduleAgent":
        agent = ScheduleAgent()
        output = await agent.run(state)
    else:
        output = {
            "agent_name": selected,
            "status": "not_implemented",
            "confidence": 0.2,
            "grounded": False,
            "used_tools": [],
            "facts": [],
            "reasoning_summary": f"{selected} is not implemented yet.",
            "recommended_next_action": "Implement this agent next.",
            "user_response": f"{selected} is not implemented yet.",
            "convai": None,
            "session_memory": state.get("session_memory", {}),
            "debug": {},
        }

    state["agent_output"] = output
    state["confidence"] = output.get("confidence", 0.0)
    state["grounded"] = output.get("grounded", False)

    # Explicitly promote these to top-level state
    state["convai"] = output.get("convai")
    state["session_memory"] = output.get("session_memory", state.get("session_memory", {}))

    state["trace"].append({
        "node": "call_selected_agent",
        "agent_name": output.get("agent_name"),
        "status": output.get("status"),
    })
    return state