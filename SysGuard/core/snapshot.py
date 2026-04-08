import os
from SysGuard.config import (
    IGNORED_PATH_PATTERNS,
    TRACKED_DIRECTORY_EXTENSIONS,
    WATCH_DIRECTORIES,
)
from SysGuard.monitors.process_monitor import get_running_processes
from SysGuard.monitors.startup_monitor import get_startup_items


def should_ignore_path(path):
    return any(pattern in path for pattern in IGNORED_PATH_PATTERNS)


def should_track_directory(path):
    normalized_path = path.lower()
    return any(normalized_path.endswith(extension) for extension in TRACKED_DIRECTORY_EXTENSIONS)


def get_files_snapshot():
    files = []

    for directory in WATCH_DIRECTORIES:
        if not os.path.exists(directory):
            continue

        for root, dirnames, filenames in os.walk(directory):
            for dirname in dirnames:
                full_path = os.path.join(root, dirname)
                if should_ignore_path(full_path) or not should_track_directory(full_path):
                    continue

                try:
                    stat = os.stat(full_path)
                    files.append({
                        "path": full_path,
                        "size": stat.st_size,
                        "modified_time": stat.st_mtime,
                    })
                except (FileNotFoundError, PermissionError):
                    continue

            for filename in filenames:
                full_path = os.path.join(root, filename)
                if should_ignore_path(full_path):
                    continue

                try:
                    stat = os.stat(full_path)
                    files.append({
                        "path": full_path,
                        "size": stat.st_size,
                        "modified_time": stat.st_mtime,
                    })
                except (FileNotFoundError, PermissionError):
                    continue

    return files


def build_system_snapshot():
    return {
        "files": get_files_snapshot(),
        "processes": get_running_processes(),
        "startup_items": get_startup_items(),
    }
