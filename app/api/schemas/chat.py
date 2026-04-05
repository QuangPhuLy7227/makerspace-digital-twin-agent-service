from pydantic import BaseModel, Field
from typing import Optional, Any, Dict


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: Optional[str] = None
    convai_mode: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    request_id: str
    response: str
    agent: Optional[str] = None
    intent: Optional[str] = None
    grounded: bool = False
    confidence: float = 0.0
    trace: list[dict] = Field(default_factory=list)
    raw_agent_output: Dict[str, Any] = Field(default_factory=dict)