from typing import Optional

from app.graph.state import OrchestratorState
from app.tools.tasks import (
    get_task,
    get_task_by_alias,
    get_task_summary,
    get_task_summary_by_alias,
)
from app.tools.messages import get_messages_for_task
from app.tools.task_ams_details import (
    get_task_ams_details_by_task,
    get_task_ams_details_by_task_alias,
)
from app.tools.printers import (
    list_printers,
    get_printer,
    get_printer_by_name,
    get_printer_timeline,
    get_printer_timeline_by_name,
    get_running_printers,
)
from app.tools.scheduling import get_queue_preview, get_scheduler_control
from app.dependencies import get_session_store
from app.llm.formatters.convai_formatter import build_convai_response


class ExplanationAgent:
    name = "ExplanationAgent"
    description = "Explains task failures, printer states, telemetry summaries, and live operations."
    allowed_tools = [
        "list_printers",
        "get_printer",
        "get_printer_by_name",
        "get_printer_timeline",
        "get_printer_timeline_by_name",
        "get_running_printers",
        "get_task",
        "get_task_by_alias",
        "get_task_summary",
        "get_task_summary_by_alias",
        "get_messages_for_task",
        "get_task_ams_details_by_task",
        "get_task_ams_details_by_task_alias",
        "get_queue_preview",
        "get_scheduler_control",
    ]

    async def run(self, state: OrchestratorState) -> dict:
        session_id = state.get("session_id", "default-session")
        session_store = get_session_store()
        session_memory = session_store.get(session_id)

        user_input = state.get("user_input", "").lower()
        entities = state.get("extracted_entities", {})

        task_alias = entities.get("task_alias") or session_memory.get("last_task_alias")
        task_id = entities.get("task_id") or session_memory.get("last_task_id")
        device_id = entities.get("device_id") or session_memory.get("last_device_id")
        printer_name = entities.get("printer_name") or session_memory.get("last_printer_name")

        asks_for_printer_of_previous = any(
            phrase in user_input
            for phrase in [
                "which printer",
                "what printer",
                "which device",
                "what device",
                "what printer was that on",
                "which printer was that on",
            ]
        )

        used_tools: list[str] = []
        facts: list[str] = []
        tool_results: dict = {}
        reasoning_summary = ""
        user_response = ""
        recommended_next_action: Optional[str] = None
        grounded = False
        confidence = 0.25

        resolved_task_id = None
        resolved_task_alias = None
        resolved_device_id = None
        resolved_printer_name = None

        # -------------------------
        # Special follow-up: "Which printer was that on?"
        # -------------------------
        if asks_for_printer_of_previous and (task_alias or task_id):
            task = None

            if task_alias:
                task = await get_task_by_alias(task_alias)
                used_tools.append("get_task_by_alias")
                resolved_task_alias = task_alias
            elif task_id:
                task = await get_task(task_id)
                used_tools.append("get_task")
                resolved_task_id = str(task_id)

            tool_results["task"] = task

            if task:
                grounded = True
                confidence = 0.97
                resolved_task_id = str(task.get("externalTaskId"))
                resolved_task_alias = task.get("taskAlias")
                resolved_device_id = task.get("deviceId")
                resolved_printer_name = task.get("deviceName")

                facts.append(f"Task ID is {resolved_task_id}.")
                if resolved_task_alias:
                    facts.append(f"Task alias is {resolved_task_alias}.")
                facts.append(f"Device is {resolved_printer_name} ({resolved_device_id}).")

                reasoning_summary = f"That task was on printer {resolved_printer_name}."
                user_response = reasoning_summary
                recommended_next_action = (
                    "I can also explain why it failed or what happened on that printer next."
                )
            else:
                reasoning_summary = "I could not reload the previous task from the backend."
                user_response = reasoning_summary
                confidence = 0.2

        # -------------------------
        # 1. Task-focused explanation
        # -------------------------
        elif task_alias or task_id:
            task = None
            summary = None
            ams_details = []
            messages = []

            if task_alias:
                task = await get_task_by_alias(task_alias)
                summary = await get_task_summary_by_alias(task_alias)
                ams_details = await get_task_ams_details_by_task_alias(task_alias)

                used_tools.extend([
                    "get_task_by_alias",
                    "get_task_summary_by_alias",
                    "get_task_ams_details_by_task_alias",
                ])
                resolved_task_alias = task_alias

                if task:
                    resolved_task_id = str(task.get("externalTaskId"))
            else:
                task = await get_task(task_id)
                summary = await get_task_summary(task_id)
                ams_details = await get_task_ams_details_by_task(task_id)

                used_tools.extend([
                    "get_task",
                    "get_task_summary",
                    "get_task_ams_details_by_task",
                ])
                resolved_task_id = str(task_id)

                if task:
                    resolved_task_alias = task.get("taskAlias")

            if task and task.get("externalTaskId"):
                messages = await get_messages_for_task(str(task.get("externalTaskId")))
                used_tools.append("get_messages_for_task")

            tool_results["task"] = task
            tool_results["messages"] = messages
            tool_results["summary"] = summary
            tool_results["ams_details"] = ams_details

            if task:
                grounded = True
                confidence = 0.9

                resolved_task_id = str(task.get("externalTaskId"))
                resolved_task_alias = task.get("taskAlias")
                resolved_device_id = task.get("deviceId")
                resolved_printer_name = task.get("deviceName")

                facts.append(f"Task ID is {resolved_task_id}.")
                if resolved_task_alias:
                    facts.append(f"Task alias is {resolved_task_alias}.")
                facts.append(f"Device is {resolved_printer_name} ({resolved_device_id}).")
                facts.append(f"Task started at {task.get('startTimeUtc')}.")
                facts.append(f"Task ended at {task.get('endTimeUtc')}.")
                facts.append(f"Task failedType is {task.get('failedType')}.")

            latest_message = None
            if messages:
                grounded = True
                confidence = max(confidence, 0.95)
                messages = sorted(messages, key=lambda m: m.get("createTimeUtc", ""), reverse=True)
                latest_message = messages[0]

                facts.append(f"Latest message title: {latest_message.get('title')}.")
                facts.append(f"Latest message detail: {latest_message.get('detail')}.")

            if summary:
                grounded = True
                confidence = max(confidence, 0.92)
                facts.append(f"Task summary status is {summary.get('statusText')}.")
                facts.append(f"Telemetry available: {summary.get('hasTelemetry')}.")
                facts.append(f"Latest progress: {summary.get('latestProgressPercent')} percent.")

            if ams_details:
                grounded = True
                confidence = max(confidence, 0.92)
                facts.append(f"AMS material records: {len(ams_details)}.")

            if latest_message:
                reasoning_summary = (
                    f"Task {resolved_task_id} is best explained by its latest message: "
                    f"{latest_message.get('detail')}"
                )
                user_response = reasoning_summary
                recommended_next_action = (
                    "I can also check the related printer timeline or whether that printer is running right now."
                )
            elif summary:
                reasoning_summary = (
                    f"Task {resolved_task_id} has status {summary.get('statusText')}. "
                    f"{summary.get('message')}"
                )
                user_response = reasoning_summary
                recommended_next_action = (
                    "I can also check the linked printer if you want more context."
                )
            elif task:
                reasoning_summary = (
                    f"I found task {resolved_task_id}, but I do not see a linked message explaining it further yet."
                )
                user_response = reasoning_summary
                recommended_next_action = "Try asking me for the printer history."
            else:
                target = task_alias or task_id
                reasoning_summary = f"I could not find task {target}."
                user_response = reasoning_summary
                confidence = 0.15

        # -------------------------
        # 2. Printer-focused explanation
        # -------------------------
        elif device_id or printer_name:
            printer = None
            timeline = []

            if printer_name:
                printer = await get_printer_by_name(printer_name)
                timeline = await get_printer_timeline_by_name(printer_name)
                used_tools.extend(["get_printer_by_name", "get_printer_timeline_by_name"])
                resolved_printer_name = printer_name
            elif device_id:
                printer = await get_printer(device_id)
                timeline = await get_printer_timeline(device_id)
                used_tools.extend(["get_printer", "get_printer_timeline"])
                resolved_device_id = device_id

            tool_results["printer"] = printer
            tool_results["timeline"] = timeline

            if printer:
                grounded = True
                confidence = 0.92
                resolved_device_id = printer.get("deviceId")
                resolved_printer_name = printer.get("name")

                facts.append(f"Printer name is {resolved_printer_name}.")
                facts.append(f"Printer device ID is {resolved_device_id}.")
                facts.append(f"Printer online state is {printer.get('isOnline')}.")
                facts.append(f"Printer operational state is {printer.get('operationalState')}.")
                facts.append(f"Printer running state is {printer.get('isRunning')}.")

                latest_task = printer.get("latestTask")
                if latest_task:
                    facts.append(f"Latest task ID is {latest_task.get('externalTaskId')}.")
                    if latest_task.get("taskAlias"):
                        facts.append(f"Latest task alias is {latest_task.get('taskAlias')}.")

            latest_event = timeline[0] if timeline else None
            if latest_event:
                grounded = True
                confidence = max(confidence, 0.95)
                facts.append(f"Latest timeline event detail: {latest_event.get('detail')}.")

            if printer and latest_event:
                reasoning_summary = (
                    f"Printer {resolved_printer_name} is currently {printer.get('operationalState')}. "
                    f"The latest recorded event says: {latest_event.get('detail')}"
                )
                user_response = reasoning_summary
                recommended_next_action = "I can also check the latest task on this printer."
            elif printer:
                reasoning_summary = (
                    f"Printer {resolved_printer_name} is currently {printer.get('operationalState')}."
                )
                user_response = reasoning_summary
                recommended_next_action = "I can also check its latest task or timeline."
            else:
                target = printer_name or device_id
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
            confidence = 0.89

            facts.append(f"Visible printers: {printer_count}.")
            facts.append(f"Running printers: {running_count}.")
            facts.append(f"Queued scheduled jobs: {queued_count}.")
            facts.append(
                f"Scheduler paused: {scheduler_control.get('isPaused') if scheduler_control else None}."
            )

            if running:
                running_names = [p.get("name") for p in running[:5]]
                facts.append(f"Running printer names: {', '.join(running_names)}.")

            paused = scheduler_control.get("isPaused") if scheduler_control else None
            if paused:
                reasoning_summary = (
                    f"There are {running_count} printer(s) running right now, but the scheduler is paused."
                )
            else:
                reasoning_summary = (
                    f"There are {running_count} printer(s) running right now and {queued_count} scheduled job(s) waiting in queue preview."
                )

            user_response = reasoning_summary
            recommended_next_action = (
                "Ask me about a specific printer name, device ID, task ID, or task alias if you want more detail."
            )

        convai = build_convai_response(
            agent_name=self.name,
            reasoning_summary=reasoning_summary,
            recommended_next_action=recommended_next_action,
            grounded=grounded,
            confidence=confidence,
            facts=facts,
        )

        session_memory = session_store.set_last_entities(
            session_id=session_id,
            task_id=resolved_task_id,
            task_alias=resolved_task_alias,
            device_id=resolved_device_id,
            printer_name=resolved_printer_name,
            agent_name=self.name,
        )

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
            "convai": convai,
            "session_memory": session_memory,
            "debug": {
                "tool_call_count": len(used_tools),
                "resolved_entities": {
                    "task_id": resolved_task_id,
                    "task_alias": resolved_task_alias,
                    "device_id": resolved_device_id,
                    "printer_name": resolved_printer_name,
                },
            },
        }