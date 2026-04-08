from collections import Counter
from datetime import datetime

from SysGuard.config import (
    BASELINE_FILE,
    BROKEN_FILES_DIR,
    EVENTS_FILE,
    LOGS_DIR,
    REPORTS_DIR,
    STORAGE_DIR,
)
from SysGuard.core.allowlist import active_events, annotate_allowlist, ensure_allowlist_exists, load_allowlist
from SysGuard.core.behavior import detect_behavioral_events, parse_timestamp
from SysGuard.core.correlation import detect_correlation_events
from SysGuard.core.reporter_utils import load_json_file, save_json_file


def ensure_storage():
    import os

    os.makedirs(STORAGE_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(BASELINE_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(EVENTS_FILE), exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(BROKEN_FILES_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    ensure_allowlist_exists()


def save_json(path, data):
    save_json_file(path, data)


def load_json(path):
    return load_json_file(path)


def normalize_event(event, default_timestamp):
    return {
        **event,
        "timestamp": event.get("timestamp", default_timestamp),
        "kind": event.get("kind", "raw"),
    }


def event_signature(event):
    return (
        event.get("kind", "raw"),
        event.get("type"),
        event.get("target"),
        event.get("pid"),
        event.get("exe"),
        event.get("suppressed", False),
    )


def within_dedup_window(left_timestamp, right_timestamp):
    from SysGuard.config import EVENT_DEDUP_WINDOW_SECONDS

    left_time = parse_timestamp(left_timestamp)
    right_time = parse_timestamp(right_timestamp)
    if not left_time or not right_time:
        return False

    delta = abs((right_time - left_time).total_seconds())
    return delta <= EVENT_DEDUP_WINDOW_SECONDS


def deduplicate_events(existing_events, new_events):
    deduplicated = []
    comparison_pool = list(existing_events)

    for event in new_events:
        signature = event_signature(event)
        duplicate_found = False

        for existing_event in reversed(comparison_pool):
            if event_signature(existing_event) != signature:
                continue
            if within_dedup_window(existing_event.get("timestamp"), event.get("timestamp")):
                duplicate_found = True
                break

        if duplicate_found:
            continue

        deduplicated.append(event)
        comparison_pool.append(event)

    return deduplicated


def save_events(events):
    existing = load_json(EVENTS_FILE)
    if existing is None:
        existing = []

    timestamp = datetime.now().isoformat()
    normalized = [normalize_event(event, timestamp) for event in events]
    deduplicated = deduplicate_events(existing, normalized)

    if not deduplicated:
        return []

    save_json(EVENTS_FILE, existing + deduplicated)
    return deduplicated


def group_events_by_kind(events):
    grouped = {
        "raw": [],
        "behavior": [],
        "correlation": [],
    }

    for event in events:
        grouped.setdefault(event.get("kind", "raw"), []).append(event)

    return grouped


def summarize_events(events):
    grouped = group_events_by_kind(events)
    visible_events = active_events(events)
    type_counts = dict(Counter(event.get("type") for event in visible_events))
    kind_counts = {kind: len(active_events(items)) for kind, items in grouped.items()}
    suppressed_count = len([event for event in events if event.get("suppressed")])

    top_findings = sorted(
        [event for event in visible_events if event.get("kind") in {"behavior", "correlation"}],
        key=lambda item: item.get("timestamp", ""),
        reverse=True,
    )[:10]

    return {
        "kind_counts": kind_counts,
        "type_counts": type_counts,
        "suppressed_count": suppressed_count,
        "top_findings": top_findings,
    }


def record_events(events):
    allowlist = load_allowlist()
    existing = load_json(EVENTS_FILE)
    if existing is None:
        existing = []

    existing_active = active_events(existing)
    timestamp = datetime.now().isoformat()
    normalized_events = [normalize_event(event, timestamp) for event in events]
    normalized_events = annotate_allowlist(normalized_events, allowlist)
    normalized_events = deduplicate_events(existing, normalized_events)
    if not normalized_events:
        return []

    new_active_raw = active_events(normalized_events)

    behavioral_events = detect_behavioral_events(existing_active, new_active_raw)
    behavioral_events = annotate_allowlist(behavioral_events, allowlist)
    behavioral_events = deduplicate_events(existing + normalized_events, behavioral_events)
    behavioral_active = active_events(behavioral_events)

    correlation_events = detect_correlation_events(existing_active, new_active_raw + behavioral_active)
    correlation_events = annotate_allowlist(correlation_events, allowlist)
    correlation_events = deduplicate_events(existing + normalized_events + behavioral_events, correlation_events)

    all_events = normalized_events + behavioral_events + correlation_events
    save_events(all_events)
    return all_events


def save_report(snapshot, events, risk):
    import os

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_path = os.path.join(REPORTS_DIR, f"report_{timestamp}.json")
    grouped = group_events_by_kind(events)
    summary = summarize_events(events)

    report = {
        "created_at": datetime.now().isoformat(),
        "snapshot_summary": {
            "file_count": len(snapshot.get("files", [])),
            "process_count": len(snapshot.get("processes", [])),
            "startup_count": len(snapshot.get("startup_items", [])),
        },
        "event_summary": summary,
        "raw_events": grouped.get("raw", []),
        "behavior_findings": grouped.get("behavior", []),
        "correlation_findings": grouped.get("correlation", []),
        "events": events,
        "risk": risk,
    }

    save_json(report_path, report)
    return report_path
