import os
from datetime import datetime

from SysGuard.config import (
    BEHAVIOR_LOOKBACK_SECONDS,
    DOWNLOADS_DIR,
    INTERACTIVE_PARENT_NAMES,
    PYTHON_PROCESS_NAMES,
    REVIEW_WORTHY_EXTENSIONS,
    SCRIPT_EXTENSIONS,
    SHORT_LIVED_PROCESS_SECONDS,
    TMP_DIRECTORIES,
    TRACKED_DIRECTORY_EXTENSIONS,
    USER_HOME_DIR,
)
from SysGuard.core.file_inspector import inspect_file


def parse_timestamp(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def normalize_path(path):
    if not path:
        return None
    return os.path.normcase(os.path.normpath(path))


def normalize_name(value):
    if not value:
        return ""
    return str(value).strip().lower()


def is_under_directory(path, directory):
    normalized_path = normalize_path(path)
    normalized_directory = normalize_path(directory)
    if not normalized_path or not normalized_directory:
        return False

    try:
        common_path = os.path.commonpath([normalized_path, normalized_directory])
    except ValueError:
        return False

    return common_path == normalized_directory


def is_under_any_directory(path, directories):
    return any(is_under_directory(path, directory) for directory in directories)


def has_extension(path, extensions):
    normalized_path = (path or "").lower()
    return any(normalized_path.endswith(extension) for extension in extensions)


def is_review_worthy_path(path):
    return has_extension(path, REVIEW_WORTHY_EXTENSIONS)


def is_tracked_directory(path):
    return has_extension(path, TRACKED_DIRECTORY_EXTENSIONS)


def is_script_path(path):
    return has_extension(path, SCRIPT_EXTENSIONS)


def get_event_time(event, default_time):
    return parse_timestamp(event.get("timestamp")) or default_time


def within_lookback(older_time, newer_time):
    if not older_time or not newer_time:
        return False

    delta = (newer_time - older_time).total_seconds()
    return 0 <= delta <= BEHAVIOR_LOOKBACK_SECONDS


def behavior_event(event_type, target, event_time, details):
    return {
        "type": event_type,
        "target": target,
        "timestamp": event_time.isoformat(),
        "kind": "behavior",
        "details": details,
    }


def extract_startup_targets(event):
    targets = []
    for value in [event.get("program"), *(event.get("program_arguments") or [])]:
        normalized_value = normalize_path(value)
        if normalized_value:
            targets.append(normalized_value)
    return targets


def find_recent_event(history, event_type, predicate, event_time):
    for event in reversed(history):
        if event.get("type") != event_type:
            continue
        if not predicate(event):
            continue

        history_time = parse_timestamp(event.get("timestamp"))
        if within_lookback(history_time, event_time):
            return event

    return None


def find_recent_new_file(history, target_path, event_time):
    normalized_target = normalize_path(target_path)
    if not normalized_target:
        return None

    def matches(event):
        event_target = event.get("target")
        normalized_event_target = normalize_path(event_target)
        if normalized_event_target == normalized_target:
            return True
        if is_tracked_directory(event_target) and is_under_directory(normalized_target, normalized_event_target):
            return True
        return False

    return find_recent_event(history, "new_file", matches, event_time)


def has_recent_downloads_new_file(history, target_path, event_time):
    matched_event = find_recent_new_file(history, target_path, event_time)
    if not matched_event:
        return None

    matched_target = matched_event.get("target")
    if not is_under_directory(matched_target, DOWNLOADS_DIR):
        return None
    if not is_review_worthy_path(matched_target):
        return None

    return matched_event


def is_interactive_parent(parent_name):
    return normalize_name(parent_name) in {normalize_name(name) for name in INTERACTIVE_PARENT_NAMES}


def is_python_process(event):
    process_name = normalize_name(event.get("target"))
    exe_name = normalize_name(os.path.basename(event.get("exe") or ""))
    names = {normalize_name(name) for name in PYTHON_PROCESS_NAMES}
    return process_name in names or exe_name in names


def extract_script_from_cmdline(cmdline):
    if not cmdline:
        return None

    for arg in cmdline[1:]:
        if not arg or str(arg).startswith("-"):
            continue
        normalized_arg = normalize_path(arg)
        if normalized_arg and is_script_path(normalized_arg):
            return normalized_arg

    return None


def extract_app_bundle_path(path):
    normalized_path = normalize_path(path)
    if not normalized_path:
        return None

    parts = normalized_path.split(os.sep)
    current_parts = []
    for part in parts:
        if not part:
            continue
        current_parts.append(part)
        if part.lower().endswith(".app"):
            prefix = os.sep if normalized_path.startswith(os.sep) else ""
            return prefix + os.sep.join(current_parts)

    return normalized_path if normalized_path.lower().endswith(".app") else None


def process_duration_seconds(start_event, end_event_time):
    create_time = start_event.get("create_time")
    if create_time:
        try:
            return max(0, end_event_time.timestamp() - float(create_time))
        except (TypeError, ValueError):
            pass

    start_time = parse_timestamp(start_event.get("timestamp"))
    if not start_time:
        return None

    return max(0, (end_event_time - start_time).total_seconds())


def detect_new_file_behaviors(history, event, event_time):
    target = event.get("target")
    findings = []

    if is_under_directory(target, DOWNLOADS_DIR) and is_review_worthy_path(target):
        findings.append(
            behavior_event(
                "review_worthy_download",
                target,
                event_time,
                {
                    "reason": "New executable-like file appeared in Downloads.",
                    "review_worthy": True,
                },
            )
        )

    for inspection in inspect_file(target):
        findings.append(
            behavior_event(
                inspection["type"],
                inspection["target"],
                event_time,
                inspection["details"],
            )
        )

    return findings


def detect_deleted_file_behaviors(history, event, event_time):
    target = event.get("target")
    matched_event = find_recent_new_file(history, target, event_time)
    if not matched_event:
        return []

    return [
        behavior_event(
            "rapid_file_disappearance",
            target,
            event_time,
            {
                "reason": "File was created and deleted within a short window.",
                "created_at": matched_event.get("timestamp"),
                "deleted_at": event_time.isoformat(),
            },
        )
    ]


def detect_new_process_behaviors(history, event, event_time):
    process_path = event.get("exe")
    results = []

    matched_event = has_recent_downloads_new_file(history, process_path, event_time)
    if process_path and is_under_directory(process_path, DOWNLOADS_DIR) and matched_event:
        results.append(
            behavior_event(
                "downloads_process_execution",
                process_path,
                event_time,
                {
                    "reason": "Recently created file in Downloads is now running as a process.",
                    "process_name": event.get("target"),
                    "pid": event.get("pid"),
                    "created_at": matched_event.get("timestamp"),
                },
            )
        )

    app_bundle_path = extract_app_bundle_path(process_path)
    if app_bundle_path and is_under_directory(app_bundle_path, DOWNLOADS_DIR):
        results.append(
            behavior_event(
                "downloads_app_execution",
                app_bundle_path,
                event_time,
                {
                    "reason": "Application bundle from Downloads is running.",
                    "process_name": event.get("target"),
                    "pid": event.get("pid"),
                },
            )
        )

    if process_path and is_under_any_directory(process_path, TMP_DIRECTORIES):
        results.append(
            behavior_event(
                "tmp_binary_execution",
                process_path,
                event_time,
                {
                    "reason": "Process is executing from a temporary directory.",
                    "process_name": event.get("target"),
                    "pid": event.get("pid"),
                },
            )
        )

    if is_python_process(event):
        script_path = extract_script_from_cmdline(event.get("cmdline") or [])
        if script_path and not is_interactive_parent(event.get("parent_name")):
            results.append(
                behavior_event(
                    "unattended_python_script",
                    script_path,
                    event_time,
                    {
                        "reason": "Python script started without an obviously interactive parent process.",
                        "process_name": event.get("target"),
                        "parent_name": event.get("parent_name"),
                        "pid": event.get("pid"),
                    },
                )
            )

    return results


def detect_terminated_process_behaviors(history, event, event_time):
    pid = event.get("pid")
    if pid is None:
        return []

    start_event = find_recent_event(
        history,
        "new_process",
        lambda candidate: candidate.get("pid") == pid,
        event_time,
    )
    if not start_event:
        return []

    duration_seconds = process_duration_seconds(start_event, event_time)
    if duration_seconds is None or duration_seconds > SHORT_LIVED_PROCESS_SECONDS:
        return []

    return [
        behavior_event(
            "short_lived_process",
            event.get("exe") or event.get("target"),
            event_time,
            {
                "reason": "Process started and terminated within a short window.",
                "process_name": event.get("target"),
                "pid": pid,
                "duration_seconds": round(duration_seconds, 2),
            },
        )
    ]


def detect_startup_behaviors(history, event, event_time):
    startup_targets = extract_startup_targets(event)
    findings = []

    for startup_target in startup_targets:
        matched_event = find_recent_new_file(history, startup_target, event_time)
        if not matched_event:
            continue

        findings.append(
            behavior_event(
                "startup_file_link",
                startup_target,
                event_time,
                {
                    "reason": "New startup item references a recently created file.",
                    "startup_item": event.get("target"),
                    "created_at": matched_event.get("timestamp"),
                },
            )
        )
        break

    if event.get("keep_alive") is True:
        findings.append(
            behavior_event(
                "launch_agent_keep_alive",
                event.get("target"),
                event_time,
                {
                    "reason": "LaunchAgent keeps itself alive.",
                    "label": event.get("label"),
                },
            )
        )

    if event.get("run_at_load") is True:
        findings.append(
            behavior_event(
                "launch_agent_run_at_load",
                event.get("target"),
                event_time,
                {
                    "reason": "LaunchAgent is configured to run at load.",
                    "label": event.get("label"),
                },
            )
        )

    for startup_target in startup_targets:
        if is_under_directory(startup_target, USER_HOME_DIR):
            findings.append(
                behavior_event(
                    "launch_agent_user_path",
                    startup_target,
                    event_time,
                    {
                        "reason": "LaunchAgent executes a binary or script from the user directory.",
                        "startup_item": event.get("target"),
                    },
                )
            )
            break

    return findings


def detect_behavioral_events(history, new_events):
    behavioral_events = []
    working_history = list(history)

    for event in new_events:
        event_time = get_event_time(event, datetime.now())
        event_with_timestamp = {
            **event,
            "timestamp": event_time.isoformat(),
        }

        if event.get("type") == "new_file":
            behavioral_events.extend(detect_new_file_behaviors(working_history, event, event_time))

        if event.get("type") == "deleted_file":
            behavioral_events.extend(detect_deleted_file_behaviors(working_history, event, event_time))

        if event.get("type") == "new_process":
            behavioral_events.extend(detect_new_process_behaviors(working_history, event, event_time))

        if event.get("type") == "terminated_process":
            behavioral_events.extend(detect_terminated_process_behaviors(working_history, event, event_time))

        if event.get("type") == "new_startup_item":
            behavioral_events.extend(detect_startup_behaviors(working_history, event, event_time))

        working_history.append(event_with_timestamp)

    return behavioral_events
