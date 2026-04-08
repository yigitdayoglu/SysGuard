import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from SysGuard.core.reporter import record_events
from SysGuard.config import IGNORED_PATH_PATTERNS, TRACKED_DIRECTORY_EXTENSIONS, WATCH_DIRECTORIES


class SysGuardFileHandler(FileSystemEventHandler):
    def _should_ignore(self, path):
        return any(pattern in path for pattern in IGNORED_PATH_PATTERNS)

    def _is_tracked_directory(self, path):
        normalized_path = path.lower()
        return any(normalized_path.endswith(extension) for extension in TRACKED_DIRECTORY_EXTENSIONS)

    def on_created(self, event):
        if self._should_ignore(event.src_path):
            return
        if event.is_directory and not self._is_tracked_directory(event.src_path):
            return

        record_events([{"type": "new_file", "target": event.src_path}])
        print(f"[FILE CREATED] {event.src_path}")

    def on_modified(self, event):
        if event.is_directory or self._should_ignore(event.src_path):
            return

        record_events([{"type": "modified_file", "target": event.src_path}])
        print(f"[FILE MODIFIED] {event.src_path}")

    def on_deleted(self, event):
        if self._should_ignore(event.src_path):
            return
        if event.is_directory and not self._is_tracked_directory(event.src_path):
            return

        record_events([{"type": "deleted_file", "target": event.src_path}])
        print(f"[FILE DELETED] {event.src_path}")


def start_file_monitor():
    observer = Observer()
    handler = SysGuardFileHandler()

    for directory in WATCH_DIRECTORIES:
        if os.path.exists(directory):
            observer.schedule(handler, directory, recursive=True)

    observer.start()
    print("[INFO] File monitor started.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("[INFO] File monitor stopped.")

    observer.join()
