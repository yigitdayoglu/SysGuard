import os

from SysGuard.config import BASELINE_FILE, EVENTS_FILE, REPORTS_DIR
from SysGuard.core.detector import detect_changes
from SysGuard.core.reporter import ensure_storage, load_json, record_events, save_json, save_report
from SysGuard.core.scorer import calculate_risk
from SysGuard.core.snapshot import build_system_snapshot
from SysGuard.monitors.file_monitor import start_file_monitor


def perform_scan(start_monitor=False):
    ensure_storage()

    baseline = load_json(BASELINE_FILE)
    current_snapshot = build_system_snapshot()

    if baseline is None:
        save_json(BASELINE_FILE, current_snapshot)
        return {
            "baseline_created": True,
            "snapshot": current_snapshot,
            "events": [],
            "risk": {"score": 0, "level": "LOW"},
            "report_path": None,
        }

    events = detect_changes(baseline, current_snapshot)
    recorded_events = record_events(events) if events else []
    risk = calculate_risk(recorded_events)
    report_path = save_report(current_snapshot, recorded_events, risk)
    save_json(BASELINE_FILE, current_snapshot)

    if start_monitor:
        start_file_monitor()

    return {
        "baseline_created": False,
        "snapshot": current_snapshot,
        "events": recorded_events,
        "risk": risk,
        "report_path": report_path,
    }


def clear_events_history():
    ensure_storage()
    save_json(EVENTS_FILE, [])
    return EVENTS_FILE


def clear_reports():
    ensure_storage()
    removed = 0
    if not os.path.exists(REPORTS_DIR):
        return removed

    for entry in os.listdir(REPORTS_DIR):
        path = os.path.join(REPORTS_DIR, entry)
        if os.path.isfile(path) and entry.endswith(".json"):
            os.remove(path)
            removed += 1

    return removed
