from langgraph.graph import StateGraph, END
from app.graph.state import OrchestratorState
from app.graph.nodes.classify_intent import classify_intent
from app.graph.nodes.extract_entities import extract_entities
from app.graph.nodes.route_agent import route_agent
from app.graph.nodes.call_selected_agent import call_selected_agent
from app.graph.nodes.synthesize_response import synthesize_response
from app.graph.nodes.finalize import finalize


def build_graph():
    graph = StateGraph(OrchestratorState)

    graph.add_node("classify_intent", classify_intent)
    graph.add_node("extract_entities", extract_entities)
    graph.add_node("route_agent", route_agent)
    graph.add_node("call_selected_agent", call_selected_agent)
    graph.add_node("synthesize_response", synthesize_response)
    graph.add_node("finalize", finalize)

    graph.set_entry_point("classify_intent")
    graph.add_edge("classify_intent", "extract_entities")
    graph.add_edge("extract_entities", "route_agent")
    graph.add_edge("route_agent", "call_selected_agent")
    graph.add_edge("call_selected_agent", "synthesize_response")
    graph.add_edge("synthesize_response", "finalize")
    graph.add_edge("finalize", END)

    return graph.compile()


orchestrator_graph = build_graph()


async def run_orchestrator(initial_state: OrchestratorState) -> OrchestratorState:
    return await orchestrator_graph.ainvoke(initial_state)