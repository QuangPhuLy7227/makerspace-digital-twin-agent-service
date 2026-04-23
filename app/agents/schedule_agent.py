from typing import Optional

from app.graph.state import OrchestratorState
from app.tools.scheduling import (
    list_scheduled_print_jobs,
    get_queue_preview,
    get_scheduler_control,
)
from app.tools.printers import list_printers


class ScheduleAgent:
    name = "ScheduleAgent"
    description = "Explains scheduler state, queued print jobs, and queue preview behavior."
    allowed_tools = [
        "list_scheduled_print_jobs",
        "get_queue_preview",
        "get_scheduler_control",
        "list_printers",
    ]

    async def run(self, state: OrchestratorState) -> dict:
        entities = state.get("extracted_entities", {})
        job_id = entities.get("job_id")
        file_name = entities.get("file_name")

        used_tools: list[str] = []
        facts: list[str] = []
        tool_results: dict = {}
        reasoning_summary = ""
        user_response = ""
        recommended_next_action: Optional[str] = None
        grounded = False
        confidence = 0.25

        jobs = await list_scheduled_print_jobs()
        queue_preview = await get_queue_preview()
        scheduler_control = await get_scheduler_control()
        printers = await list_printers()

        used_tools.extend([
            "list_scheduled_print_jobs",
            "get_queue_preview",
            "get_scheduler_control",
            "list_printers",
        ])

        tool_results["jobs"] = jobs
        tool_results["queue_preview"] = queue_preview
        tool_results["scheduler_control"] = scheduler_control
        tool_results["printers"] = printers

        grounded = True
        confidence = 0.9

        paused = scheduler_control.get("isPaused") if scheduler_control else None
        pause_reason = scheduler_control.get("pauseReason") if scheduler_control else None

        facts.append(f"Scheduled jobs count: {len(jobs)}.")
        facts.append(f"Queue preview count: {len(queue_preview)}.")
        facts.append(f"Scheduler paused: {paused}.")
        if pause_reason:
            facts.append(f"Scheduler pause reason: {pause_reason}.")

        matched_job = None

        if job_id:
            matched_job = next((j for j in jobs if str(j.get("id")) == str(job_id)), None)

        if not matched_job and file_name:
            matched_job = next(
                (
                    j for j in jobs
                    if str(j.get("fileName", "")).lower() == str(file_name).lower()
                    or str(j.get("displayName", "")).lower() == str(file_name).lower()
                ),
                None,
            )

        if matched_job:
            facts.append(f"Matched scheduled job id: {matched_job.get('id')}.")
            facts.append(f"Matched scheduled job status: {matched_job.get('status')}.")
            facts.append(f"Matched scheduled job file: {matched_job.get('fileName')}.")
            facts.append(f"Matched scheduled job priority: {matched_job.get('priority')}.")
            facts.append(
                f"Matched scheduled job estimated start: {matched_job.get('estimatedStartAtUtc')}."
            )
            facts.append(
                f"Matched scheduled job estimated finish: {matched_job.get('estimatedFinishAtUtc')}."
            )

            compatibility_note = matched_job.get("compatibilityNote")
            decision_reason = matched_job.get("schedulerDecisionReason")
            assigned_printer_name = matched_job.get("assignedPrinterName")
            preferred_printer_name = matched_job.get("preferredPrinterName")

            if compatibility_note:
                facts.append(f"Compatibility note: {compatibility_note}")
            if decision_reason:
                facts.append(f"Scheduler decision reason: {decision_reason}")
            if assigned_printer_name:
                facts.append(f"Assigned printer: {assigned_printer_name}")
            if preferred_printer_name:
                facts.append(f"Preferred printer: {preferred_printer_name}")

            reasoning_summary = (
                f"Scheduled job {matched_job.get('displayName') or matched_job.get('fileName')} "
                f"is currently {matched_job.get('status')} with priority {matched_job.get('priority')}."
            )

            if compatibility_note:
                reasoning_summary += f" {compatibility_note}"

            if paused:
                reasoning_summary += " The scheduler is currently paused."
            else:
                reasoning_summary += (
                    f" Its estimated start time is {matched_job.get('estimatedStartAtUtc')} "
                    f"and estimated finish time is {matched_job.get('estimatedFinishAtUtc')}."
                )

            user_response = reasoning_summary
            recommended_next_action = (
                "Ask to raise priority, inspect queue preview, or run a dispatch cycle."
            )

        else:
            running_count = sum(1 for p in printers if p.get("isRunning"))
            online_count = sum(1 for p in printers if p.get("isOnline"))

            facts.append(f"Online printers: {online_count}.")
            facts.append(f"Running printers: {running_count}.")

            if queue_preview:
                first_job = queue_preview[0]
                facts.append(
                    f"Next queue preview job is {first_job.get('displayName') or first_job.get('fileName')}."
                )
                facts.append(f"Next queue preview job status is {first_job.get('status')}.")
                facts.append(
                    f"Next queue preview job estimated start is {first_job.get('estimatedStartAtUtc')}."
                )

            if paused:
                reasoning_summary = (
                    f"The scheduler is currently paused, and there are {len(queue_preview)} job(s) "
                    f"in queue preview."
                )
                if pause_reason:
                    reasoning_summary += f" Pause reason: {pause_reason}."
            else:
                reasoning_summary = (
                    f"The scheduler is active. There are {len(jobs)} scheduled job(s), "
                    f"{len(queue_preview)} job(s) in queue preview, and {running_count} running printer(s)."
                )

                if queue_preview:
                    first_job = queue_preview[0]
                    reasoning_summary += (
                        f" The next queued job appears to be "
                        f"{first_job.get('displayName') or first_job.get('fileName')}."
                    )

            user_response = reasoning_summary
            recommended_next_action = (
                "Ask about a specific scheduled job, queue preview, or scheduler pause state."
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
            "debug": {
                "tool_call_count": len(used_tools),
                "resolved_entities": entities,
            },
        }