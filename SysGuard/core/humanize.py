from collections import Counter


EVENT_LABELS = {
    "new_file": "new file",
    "modified_file": "modified file",
    "deleted_file": "deleted file",
    "new_process": "new process",
    "terminated_process": "terminated process",
    "new_startup_item": "new startup item",
    "removed_startup_item": "removed startup item",
    "review_worthy_download": "review-worthy download",
    "rapid_file_disappearance": "rapid file disappearance",
    "downloads_process_execution": "downloaded file execution",
    "downloads_app_execution": "downloaded app execution",
    "tmp_binary_execution": "temporary binary execution",
    "unattended_python_script": "background python script",
    "short_lived_process": "short-lived process",
    "small_executable": "small executable",
    "network_enabled_script": "script with download command",
    "base64_encoded_script": "script with base64 usage",
    "shell_script_detected": "shell script",
    "startup_file_link": "startup linked to a new file",
    "launch_agent_keep_alive": "persistent launch agent",
    "launch_agent_run_at_load": "auto-start launch agent",
    "launch_agent_user_path": "launch agent from user folder",
    "download_execute_persist_chain": "download -> execution -> persistence chain",
}


def pretty_event_type(event_type):
    return EVENT_LABELS.get(event_type, (event_type or "unknown").replace("_", " "))


def summarize_top_findings(findings):
    if not findings:
        return "No important security findings are active right now."

    parts = []
    for finding in findings[:5]:
        title = pretty_event_type(finding.get("type")).capitalize()
        target = finding.get("target", "an unknown target")
        reason = finding.get("details", {}).get("reason")
        if reason:
            parts.append(f"{title} involving {target}. {reason}")
        else:
            parts.append(f"{title} involving {target}.")
    return "\n\n".join(parts)


def summarize_recent_events(events):
    if not events:
        return "No new activity was recorded recently."

    counts = Counter(event.get("type") for event in events if event.get("type"))
    lines = []
    for event_type, count in counts.most_common(5):
        lines.append(f"- {count} {pretty_event_type(event_type)} event(s)")
    return "Recent activity summary:\n" + "\n".join(lines)


def summarize_report(report):
    if not report:
        return "No report has been created yet."

    snapshot = report.get("snapshot_summary", {})
    risk = report.get("risk", {})
    event_summary = report.get("event_summary", {})

    return (
        f"This report was created at {report.get('created_at', 'an unknown time')}.\n\n"
        f"The system snapshot included {snapshot.get('file_count', 0)} files, "
        f"{snapshot.get('process_count', 0)} running processes, and "
        f"{snapshot.get('startup_count', 0)} startup items.\n\n"
        f"Current risk is {risk.get('level', 'LOW')} with a score of {risk.get('score', 0)}.\n\n"
        f"Visible events in this report: raw={event_summary.get('kind_counts', {}).get('raw', 0)}, "
        f"behavior={event_summary.get('kind_counts', {}).get('behavior', 0)}, "
        f"correlation={event_summary.get('kind_counts', {}).get('correlation', 0)}, "
        f"suppressed={event_summary.get('suppressed_count', 0)}."
    )
