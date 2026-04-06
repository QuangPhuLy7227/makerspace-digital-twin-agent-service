from typing import Optional

from app.graph.state import OrchestratorState
from app.tools.tasks import get_task, get_task_summary
from app.tools.messages import get_messages_for_task
from app.tools.task_ams_details import get_task_ams_details_by_task
from app.tools.printers import (
    list_printers,
    get_printer,
    get_printer_timeline,
    get_running_printers,
)
from app.tools.scheduling import get_queue_preview, get_scheduler_control


class ExplanationAgent:
    name = "ExplanationAgent"
    description = "Explains task failures, printer states, telemetry summaries, and queue/scheduler behavior."
    allowed_tools = [
        "list_printers",
        "get_printer",
        "get_printer_timeline",
        "get_running_printers",
        "get_task",
        "get_task_summary",
        "get_messages_for_task",
        "get_task_ams_details_by_task",
        "get_queue_preview",
        "get_scheduler_control",
    ]

    async def run(self, state: OrchestratorState) -> dict:
        entities = state.get("extracted_entities", {})
        task_id = entities.get("task_id")
        device_id = entities.get("device_id")
        printer_name = entities.get("printer_name")

        used_tools: list[str] = []
        facts: list[str] = []
        tool_results: dict = {}
        reasoning_summary = ""
        user_response = ""
        recommended_next_action: Optional[str] = None
        grounded = False
        confidence = 0.25

        # -------------------------
        # 1. Task-focused explanation
        # -------------------------
        if task_id:
            task = await get_task(task_id)
            messages = await get_messages_for_task(task_id)
            summary = await get_task_summary(task_id)
            ams_details = await get_task_ams_details_by_task(task_id)

            used_tools.extend([
                "get_task",
                "get_messages_for_task",
                "get_task_summary",
                "get_task_ams_details_by_task",
            ])

            tool_results["task"] = task
            tool_results["messages"] = messages
            tool_results["summary"] = summary
            tool_results["ams_details"] = ams_details

            if task:
                grounded = True
                confidence = 0.88

                facts.append(f"Task {task_id} belongs to device {task.get('deviceId')}.")
                facts.append(f"Task {task_id} design title is {task.get('designTitle') or '(empty)'}.")
                facts.append(f"Task {task_id} started at {task.get('startTimeUtc')}.")
                facts.append(f"Task {task_id} ended at {task.get('endTimeUtc')}.")
                facts.append(f"Task {task_id} failedType is {task.get('failedType')}.")

            if summary:
                grounded = True
                confidence = max(confidence, 0.91)
                facts.append(f"Task {task_id} summary status is {summary.get('statusText')}.")
                facts.append(f"Task {task_id} telemetry availability is {summary.get('hasTelemetry')}.")
                facts.append(f"Task {task_id} latest progress is {summary.get('latestProgressPercent')} percent.")

            if ams_details:
                grounded = True
                confidence = max(confidence, 0.92)
                facts.append(f"Task {task_id} has {len(ams_details)} AMS detail record(s).")

            latest_message = None
            if messages:
                grounded = True
                confidence = max(confidence, 0.95)
                messages = sorted(messages, key=lambda m: m.get("createTimeUtc", ""), reverse=True)
                latest_message = messages[0]
                facts.append(
                    f"Latest task message says: {latest_message.get('detail', '(no detail)')}"
                )

            if latest_message:
                detail = latest_message.get("detail", "")
                title = latest_message.get("title", "")
                reasoning_summary = (
                    f"Task {task_id} is best explained by its latest message. "
                    f"{title}: {detail}"
                )
                user_response = reasoning_summary
                recommended_next_action = "Ask for the printer timeline or queue state if you want related operational context."
            elif summary:
                reasoning_summary = (
                    f"Task {task_id} has telemetry summary status {summary.get('statusText')}. "
                    f"{summary.get('message')}"
                )
                user_response = reasoning_summary
                recommended_next_action = "Ask for related messages if you want a clearer event narrative."
            elif task:
                reasoning_summary = (
                    f"I found task {task_id}, but there were no matching messages or summary details to explain it further."
                )
                user_response = reasoning_summary
                recommended_next_action = "Check printer history or expose more task-linked messages."
            else:
                reasoning_summary = f"I could not find task {task_id}."
                user_response = reasoning_summary
                confidence = 0.15

        # -------------------------
        # 2. Printer-focused explanation
        # -------------------------
        elif device_id or printer_name:
            printer = None
            resolved_device_id = device_id

            if resolved_device_id:
                printer = await get_printer(resolved_device_id)
                used_tools.append("get_printer")
            else:
                printers = await list_printers()
                used_tools.append("list_printers")
                tool_results["printers"] = printers

                match = next(
                    (p for p in printers if str(p.get("name", "")).lower() == str(printer_name).lower()),
                    None,
                )
                if match:
                    resolved_device_id = match.get("deviceId")
                    printer = match

            if resolved_device_id:
                timeline = await get_printer_timeline(resolved_device_id)
                used_tools.append("get_printer_timeline")
                tool_results["timeline"] = timeline
            else:
                timeline = []

            tool_results["printer"] = printer

            if printer:
                grounded = True
                confidence = 0.9
                facts.append(f"Printer {printer.get('name')} device id is {printer.get('deviceId')}.")
                facts.append(f"Printer online state is {printer.get('isOnline')}.")
                facts.append(f"Printer print status is {printer.get('printStatus')}.")
                facts.append(f"Printer operational state is {printer.get('operationalState')}.")
                facts.append(f"Printer isRunning is {printer.get('isRunning')}.")

            latest_event = timeline[0] if timeline else None
            if latest_event:
                grounded = True
                confidence = max(confidence, 0.94)
                facts.append(
                    f"Latest printer timeline event says: {latest_event.get('detail', '(no detail)')}"
                )

            if printer and latest_event:
                reasoning_summary = (
                    f"Printer {printer.get('name')} is currently {printer.get('operationalState')}. "
                    f"The latest recorded event was: {latest_event.get('detail')}"
                )
                user_response = reasoning_summary
                recommended_next_action = "Ask about a specific task on this printer if you want deeper detail."
            elif printer:
                reasoning_summary = (
                    f"Printer {printer.get('name')} is currently {printer.get('operationalState')}."
                )
                user_response = reasoning_summary
                recommended_next_action = "Ask for printer timeline or latest task/message if needed."
            else:
                target = resolved_device_id or printer_name
                reasoning_summary = f"I could not find printer {target}."
                user_response = reasoning_summary
                confidence = 0.15

        # -------------------------
        # 3. General operations explanation
        # -------------------------
        else:
            printers = await list_printers()
            running = await get_running_printers()
            queue_preview = await get_queue_preview()
            scheduler_control = await get_scheduler_control()

            used_tools.extend([
                "list_printers",
                "get_running_printers",
                "get_queue_preview",
                "get_scheduler_control",
            ])

            tool_results["printers"] = printers
            tool_results["running_printers"] = running
            tool_results["queue_preview"] = queue_preview
            tool_results["scheduler_control"] = scheduler_control

            printer_count = len(printers)
            running_count = len(running)
            queued_count = len(queue_preview)

            grounded = True
            confidence = 0.87

            facts.append(f"Total printers visible: {printer_count}.")
            facts.append(f"Currently running printers: {running_count}.")
            facts.append(f"Queue preview item count: {queued_count}.")
            facts.append(
                f"Scheduler paused state: {scheduler_control.get('isPaused') if scheduler_control else None}."
            )

            paused = scheduler_control.get("isPaused") if scheduler_control else None

            if paused:
                reasoning_summary = (
                    f"The scheduler is currently paused. There are {queued_count} queued scheduled job(s) "
                    f"and {running_count} running printer(s)."
                )
            else:
                reasoning_summary = (
                    f"There are {running_count} running printer(s), {queued_count} scheduled job(s) in queue preview, "
                    f"and the scheduler is currently active."
                )

            user_response = reasoning_summary
            recommended_next_action = "Ask about a specific task, printer, or scheduled job for a more detailed explanation."

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
                "resolved_entities": entities,
            },
        }