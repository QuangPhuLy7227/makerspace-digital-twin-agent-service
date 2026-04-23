from typing import Any, Dict, Optional


def _clean_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return " ".join(str(value).split()).strip()


def build_convai_response(
    agent_name: str,
    reasoning_summary: str,
    recommended_next_action: Optional[str],
    grounded: bool,
    confidence: float,
    facts: list[str],
) -> Dict[str, Any]:
    reasoning_summary = _clean_text(reasoning_summary)
    recommended_next_action = _clean_text(recommended_next_action)

    if not grounded:
        short_answer = "I’m not fully sure yet based on the current system data."
        spoken_answer = (
            "I found some partial information, but I can’t fully confirm the answer from the backend yet."
        )
        follow_up_prompt = "Try asking me about a specific task ID or printer."
        tone_hint = "careful_uncertain"
    else:
        short_answer = reasoning_summary or "Here’s what I found."
        spoken_answer = reasoning_summary or "Here’s what I found from the system."

        if recommended_next_action:
            follow_up_prompt = recommended_next_action
        else:
            follow_up_prompt = "I can check more details if you want."

        if confidence >= 0.9:
            tone_hint = "calm_confident"
        elif confidence >= 0.75:
            tone_hint = "calm_explanatory"
        else:
            tone_hint = "careful_explanatory"

    detail_bullets = facts[:4]

    return {
        "agent_name": agent_name,
        "short_answer": short_answer,
        "spoken_answer": spoken_answer,
        "follow_up_prompt": follow_up_prompt,
        "tone_hint": tone_hint,
        "detail_bullets": detail_bullets,
    }