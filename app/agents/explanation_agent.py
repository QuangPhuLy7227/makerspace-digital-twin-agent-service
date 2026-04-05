from app.graph.state import OrchestratorState
from app.tools.tasks import get_task, get_task_history
from app.tools.printers import get_printer_status
from app.tools.scheduling import get_queue_state


class ExplanationAgent:
    name = "ExplanationAgent"
    description = "Explains task failures, printer states, and scheduling behavior."
    allowed_tools = [
        "get_task",
        "get_task_history",
        "get_printer_status",
        "get_queue_state",
    ]

    async def run(self, state: OrchestratorState) -> dict:
        entities = state.get("extracted_entities", {})
        task_id = entities.get("task_id")
        printer_id = entities.get("printer_id")

        used_tools = []
        facts = []
        reasoning_summary = ""
        user_response = ""
        recommended_next_action = None
        tool_results = {}
        grounded = False
        confidence = 0.4

        if task_id:
            task = await get_task(task_id)
            history = await get_task_history(task_id)

            used_tools.extend(["get_task", "get_task_history"])
            tool_results["task"] = task
            tool_results["task_history"] = history

            if task:
                grounded = True
                confidence = 0.9
                facts.append(f"Task {task_id} current status is {task['status']}.")
                if task.get("printer_id"):
                    facts.append(f"Task {task_id} is associated with printer {task['printer_id']}.")

            if history:
                grounded = True
                confidence = max(confidence, 0.92)
                for event in history:
                    facts.append(
                        f"Task {task_id} had event {event['event_type']} at {event['timestamp']}."
                    )

            failed_because_stopped = any(
                event["event_type"] == "STOPPED_WHILE_RUNNING" for event in history
            )

            if failed_because_stopped:
                reasoning_summary = (
                    f"Task {task_id} failed because it was stopped while in RUNNING state. "
                    f"In the current simulation, that marks the task as FAILED."
                )
                user_response = reasoning_summary
                recommended_next_action = (
                    f"Consider requeueing task {task_id} or sending it to RecoveryAgent next."
                )
            elif grounded:
                reasoning_summary = (
                    f"I found task information for task {task_id}, but I did not find the "
                    f'specific simulated failure pattern "stopped while running".'
                )
                user_response = reasoning_summary
                recommended_next_action = "Check more backend events or expose more failure history."
            else:
                reasoning_summary = f"I could not find task {task_id}."
                user_response = reasoning_summary
                confidence = 0.2

        elif printer_id:
            printer = await get_printer_status(printer_id)
            used_tools.append("get_printer_status")
            tool_results["printer"] = printer

            if printer:
                grounded = True
                confidence = 0.9
                facts.append(f"Printer {printer_id} current status is {printer['status']}.")
                facts.append(f"Printer {printer_id} active task is {printer.get('active_task_id')}.")
                reasoning_summary = f"Printer {printer_id} is currently {printer['status']}."
                user_response = reasoning_summary
                recommended_next_action = "Ask for queue state or printer history if needed."
            else:
                reasoning_summary = f"I could not find printer {printer_id}."
                user_response = reasoning_summary
                confidence = 0.2

        else:
            queue_state = await get_queue_state()
            used_tools.append("get_queue_state")
            tool_results["queue_state"] = queue_state

            if queue_state:
                grounded = True
                confidence = 0.85
                facts.append(f"There are {queue_state['queued_jobs']} queued jobs.")
                facts.append(f"There are {queue_state['running_jobs']} running jobs.")
                reasoning_summary = "I answered using the current queue summary because no task_id or printer_id was provided."
                user_response = (
                    f"Right now there are {queue_state['queued_jobs']} queued jobs and "
                    f"{queue_state['running_jobs']} running jobs."
                )
                recommended_next_action = "Ask about a specific task or printer for a more detailed explanation."
            else:
                reasoning_summary = "I could not get the queue state."
                user_response = reasoning_summary
                confidence = 0.2

        state["tool_results"] = tool_results

        return {
            "agent_name": self.name,
            "status": "success",
            "confidence": confidence,
            "grounded": grounded,
            "used_tools": used_tools,
            "facts": facts,
            "reasoning_summary": reasoning_summary,
            "recommended_next_action": recommended_next_action,
            "user_response": user_response,
            "debug": {
                "tool_call_count": len(used_tools),
            },
        }