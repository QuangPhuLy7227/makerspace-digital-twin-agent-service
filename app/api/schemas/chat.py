from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: Optional[str] = None
    convai_mode: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConvAIResponsePayload(BaseModel):
    agent_name: Optional[str] = None
    short_answer: str = ""
    spoken_answer: str = ""
    follow_up_prompt: str = ""
    tone_hint: str = ""
    detail_bullets: List[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    request_id: str
    response: str
    agent: Optional[str] = None
    intent: Optional[str] = None
    grounded: bool = False
    confidence: float = 0.0
    trace: list[dict] = Field(default_factory=list)
    raw_agent_output: Dict[str, Any] = Field(default_factory=dict)
    convai: Optional[ConvAIResponsePayload] = None
    session_memory: Dict[str, Any] = Field(default_factory=dict)