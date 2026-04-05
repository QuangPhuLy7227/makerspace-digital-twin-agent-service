from fastapi import APIRouter
from app.api.schemas.chat import ChatRequest, ChatResponse
from app.graph.flows.main_orchestrator import run_orchestrator
from app.utils.ids import new_request_id

router = APIRouter()

@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    request_id = new_request_id()

    state = {
        "request_id": request_id,
        "session_id": request.session_id or "default-session",
        "user_input": request.message,
        "convai_mode": request.convai_mode,
        "metadata": request.metadata,
        "trace": [],
        "errors": [],
        "tool_results": {},
    }

    final_state = await run_orchestrator(state)

    return ChatResponse(
        request_id=request_id,
        response=final_state.get("final_response", "I could not generate a response."),
        agent=final_state.get("selected_agent"),
        intent=final_state.get("intent"),
        grounded=final_state.get("grounded", False),
        confidence=final_state.get("confidence", 0.0),
        trace=final_state.get("trace", []),
        raw_agent_output=final_state.get("agent_output", {}),
    )