from typing import Protocol
from app.graph.state import OrchestratorState


class BaseAgent(Protocol):
    name: str
    description: str
    allowed_tools: list[str]

    async def run(self, state: OrchestratorState) -> dict:
        ...