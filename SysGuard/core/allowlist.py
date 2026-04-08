from SysGuard.config import ALLOWLIST_FILE
from SysGuard.core.behavior import normalize_name, normalize_path
from SysGuard.core.reporter_utils import load_json_file, save_json_file


DEFAULT_ALLOWLIST = {
    "exact_paths": [],
    "path_prefixes": [],
    "process_names": [],
    "startup_labels": [],
    "event_types": [],
}


def ensure_allowlist_exists():
    existing = load_json_file(ALLOWLIST_FILE)
    if existing is None:
        save_json_file(ALLOWLIST_FILE, DEFAULT_ALLOWLIST)


def load_allowlist():
    data = load_json_file(ALLOWLIST_FILE)
    if not isinstance(data, dict):
        return DEFAULT_ALLOWLIST.copy()

    allowlist = DEFAULT_ALLOWLIST.copy()
    for key in DEFAULT_ALLOWLIST:
        value = data.get(key, [])
        allowlist[key] = value if isinstance(value, list) else []
    return allowlist


def event_allowlist_reason(event, allowlist):
    event_type = event.get("type")
    if event_type in allowlist.get("event_types", []):
        return f"Matched allowlisted event type: {event_type}"

    candidate_paths = [
        event.get("target"),
        event.get("exe"),
        event.get("program"),
    ]

    for candidate_path in candidate_paths:
        target = normalize_path(candidate_path)
        if not target:
            continue

        for exact_path in allowlist.get("exact_paths", []):
            if normalize_path(exact_path) == target:
                return f"Matched allowlisted path: {exact_path}"

        for prefix in allowlist.get("path_prefixes", []):
            normalized_prefix = normalize_path(prefix)
            if normalized_prefix and target.startswith(normalized_prefix):
                return f"Matched allowlisted path prefix: {prefix}"

    process_candidates = [
        event.get("target"),
        event.get("details", {}).get("process_name"),
    ]

    for process_candidate in process_candidates:
        process_name = normalize_name(process_candidate)
        if not process_name:
            continue
        for allowed_name in allowlist.get("process_names", []):
            if normalize_name(allowed_name) == process_name:
                return f"Matched allowlisted process: {allowed_name}"

    label = normalize_name(event.get("label") or event.get("details", {}).get("label"))
    if label:
        for allowed_label in allowlist.get("startup_labels", []):
            if normalize_name(allowed_label) == label:
                return f"Matched allowlisted startup label: {allowed_label}"

    return None


def annotate_allowlist(events, allowlist):
    annotated = []
    for event in events:
        reason = event_allowlist_reason(event, allowlist)
        annotated.append(
            {
                **event,
                "suppressed": bool(reason),
                "allowlist_reason": reason,
            }
        )
    return annotated


def active_events(events):
    return [event for event in events if not event.get("suppressed")]
