from datetime import datetime

from SysGuard.config import BEHAVIOR_LOOKBACK_SECONDS
from SysGuard.core.behavior import normalize_path, parse_timestamp, within_lookback


def event_time(event):
    return parse_timestamp(event.get("timestamp")) or datetime.min


def same_target(left, right):
    normalized_left = normalize_path(left)
    normalized_right = normalize_path(right)
    return bool(normalized_left and normalized_right and normalized_left == normalized_right)


def recent_enough(reference_time, candidate_time):
    if not reference_time or not candidate_time:
        return False
    return within_lookback(reference_time, candidate_time) or within_lookback(candidate_time, reference_time)


def is_recent_duplicate(history, correlation_type, target, correlation_time):
    for event in reversed(history):
        if event.get("type") != correlation_type:
            continue
        if not same_target(event.get("target"), target):
            continue

        prior_time = parse_timestamp(event.get("timestamp"))
        if recent_enough(prior_time, correlation_time):
            return True

    return False


def correlation_event(event_type, target, event_time_value, details):
    return {
        "type": event_type,
        "target": target,
        "timestamp": event_time_value.isoformat(),
        "kind": "correlation",
        "details": details,
    }


def is_download_seed(event):
    return event.get("type") == "review_worthy_download"


def is_execution_stage(event, artifact_target):
    if event.get("type") not in {"downloads_process_execution", "downloads_app_execution"}:
        return False
    return same_target(event.get("target"), artifact_target)


def is_startup_stage(event, artifact_target):
    if event.get("type") != "startup_file_link":
        return False
    return same_target(event.get("target"), artifact_target)


def find_matching_event(events, predicate, reference_time):
    for event in events:
        candidate_time = parse_timestamp(event.get("timestamp"))
        if not recent_enough(reference_time, candidate_time):
            continue
        if predicate(event):
            return event
    return None


def involved_current_event(batch_events, *targets):
    batch_ids = {id(event) for event in batch_events}
    for event in targets:
        if id(event) in batch_ids:
            return True
    return False


def detect_correlation_events(history, batch_events):
    correlations = []
    combined_events = sorted(history + batch_events, key=event_time)

    for event in combined_events:
        if not is_download_seed(event):
            continue

        artifact_target = event.get("target")
        seed_time = parse_timestamp(event.get("timestamp"))
        if not artifact_target or not seed_time:
            continue

        execution_event = find_matching_event(
            combined_events,
            lambda candidate: is_execution_stage(candidate, artifact_target),
            seed_time,
        )
        if not execution_event:
            continue

        startup_event = find_matching_event(
            combined_events,
            lambda candidate: is_startup_stage(candidate, artifact_target),
            seed_time,
        )
        if not startup_event:
            continue

        correlation_time = max(
            seed_time,
            parse_timestamp(execution_event.get("timestamp")) or seed_time,
            parse_timestamp(startup_event.get("timestamp")) or seed_time,
        )

        if not involved_current_event(batch_events, event, execution_event, startup_event):
            continue

        if is_recent_duplicate(history, "download_execute_persist_chain", artifact_target, correlation_time):
            continue

        correlations.append(
            correlation_event(
                "download_execute_persist_chain",
                artifact_target,
                correlation_time,
                {
                    "reason": "Download, execution, and persistence behaviors were observed for the same artifact.",
                    "stages": [
                        {
                            "type": event.get("type"),
                            "timestamp": event.get("timestamp"),
                        },
                        {
                            "type": execution_event.get("type"),
                            "timestamp": execution_event.get("timestamp"),
                        },
                        {
                            "type": startup_event.get("type"),
                            "timestamp": startup_event.get("timestamp"),
                        },
                    ],
                    "lookback_seconds": BEHAVIOR_LOOKBACK_SECONDS,
                },
            )
        )

    return correlations
