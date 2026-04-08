import os
import time
from collections import Counter
from datetime import datetime

from SysGuard.config import EVENTS_FILE, REPORTS_DIR
from SysGuard.core.allowlist import active_events
from SysGuard.core.reporter import load_json, summarize_events
from SysGuard.core.scorer import calculate_risk


def section(title):
    line = "=" * 64
    return f"{line}\n{title}\n{line}"


def format_kv_rows(rows):
    if not rows:
        return "  (none)"

    width = max(len(label) for label, _ in rows)
    return "\n".join(f"  {label.ljust(width)} : {value}" for label, value in rows)


def top_types(events, limit=5):
    counts = Counter(event.get("type") for event in events if event.get("type"))
    return counts.most_common(limit)


def risk_badge(level):
    if level == "HIGH":
        return "[ HIGH ]"
    if level == "MEDIUM":
        return "[ MEDIUM ]"
    return "[ LOW ]"


def finding_line(event):
    event_type = event.get("type", "unknown")
    target = event.get("target", "-")
    reason = event.get("details", {}).get("reason")
    if reason:
        return f"  - {event_type}: {target} | {reason}"
    return f"  - {event_type}: {target}"


def latest_report_path():
    if not os.path.exists(REPORTS_DIR):
        return None

    reports = [
        os.path.join(REPORTS_DIR, entry)
        for entry in os.listdir(REPORTS_DIR)
        if entry.endswith(".json")
    ]
    if not reports:
        return None

    return max(reports, key=os.path.getmtime)


def load_dashboard_state():
    events = load_json(EVENTS_FILE) or []
    summary = summarize_events(events)
    risk = calculate_risk(events)
    report_path = latest_report_path()
    latest_report = load_json(report_path) if report_path else None
    snapshot_summary = (latest_report or {}).get(
        "snapshot_summary",
        {"file_count": 0, "process_count": 0, "startup_count": 0},
    )

    return {
        "generated_at": datetime.now().isoformat(),
        "events": events,
        "summary": summary,
        "risk": risk,
        "report_path": report_path or "-",
        "snapshot_summary": snapshot_summary,
        "latest_report": latest_report,
    }


def build_dashboard_from_state(state):
    events = state["events"]
    summary = state["summary"]
    risk = state["risk"]
    snapshot_summary = state["snapshot_summary"]
    report_path = state["report_path"]

    visible_events = active_events(events)
    visible_findings = [
        event for event in visible_events if event.get("kind") in {"behavior", "correlation"}
    ]
    recent_findings = sorted(
        visible_findings,
        key=lambda item: item.get("timestamp", ""),
        reverse=True,
    )[:5]

    snapshot_rows = [
        ("Files", snapshot_summary.get("file_count", 0)),
        ("Processes", snapshot_summary.get("process_count", 0)),
        ("Startup Items", snapshot_summary.get("startup_count", 0)),
        ("Latest Report", report_path),
        ("Generated", state["generated_at"]),
    ]

    risk_rows = [
        ("Risk Level", f"{risk_badge(risk.get('level'))}"),
        ("Risk Score", risk.get("score", 0)),
        ("Raw Events", summary["kind_counts"].get("raw", 0)),
        ("Behavior Findings", summary["kind_counts"].get("behavior", 0)),
        ("Correlation Findings", summary["kind_counts"].get("correlation", 0)),
        ("Suppressed", summary.get("suppressed_count", 0)),
    ]

    top_type_rows = [(event_type, count) for event_type, count in top_types(visible_events)]

    blocks = [
        section("SYSGUARD V7 TERMINAL DASHBOARD"),
        format_kv_rows(snapshot_rows),
        "",
        section("RISK OVERVIEW"),
        format_kv_rows(risk_rows),
        "",
        section("TOP EVENT TYPES"),
        format_kv_rows(top_type_rows),
        "",
        section("RECENT FINDINGS"),
        "\n".join(finding_line(finding) for finding in recent_findings) if recent_findings else "  (none)",
    ]

    return "\n".join(blocks)


def build_dashboard(snapshot, events, risk, report_path, summary):
    state = {
        "generated_at": datetime.now().isoformat(),
        "events": events,
        "summary": summary,
        "risk": risk,
        "report_path": report_path,
        "snapshot_summary": {
            "file_count": len(snapshot.get("files", [])),
            "process_count": len(snapshot.get("processes", [])),
            "startup_count": len(snapshot.get("startup_items", [])),
        },
        "latest_report": None,
    }
    return build_dashboard_from_state(state)


def clear_screen():
    print("\033[2J\033[H", end="")


def run_terminal_dashboard(interval_seconds=2):
    try:
        while True:
            state = load_dashboard_state()
            clear_screen()
            print(build_dashboard_from_state(state))
            print()
            print(f"[INFO] Auto-refresh every {interval_seconds}s. Press Ctrl+C to exit.")
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("\n[INFO] Dashboard stopped.")
