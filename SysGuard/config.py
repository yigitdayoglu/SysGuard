import os
import sys

APP_VERSION = "V7.4"

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))


def _default_storage_dir():
    if getattr(sys, "frozen", False):
        return os.path.join(
            os.path.expanduser("~/Library/Application Support"),
            "SysGuard",
        )
    project_root = os.path.dirname(PACKAGE_DIR)
    return os.path.join(project_root, "storage")


PROJECT_ROOT = os.path.dirname(PACKAGE_DIR)
STORAGE_DIR = _default_storage_dir()
LOGS_DIR = os.path.join(STORAGE_DIR, "logs")

WATCH_DIRECTORIES = [
    os.path.expanduser("~/Desktop"),
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Documents"),
]
DOWNLOADS_DIR = os.path.expanduser("~/Downloads")
TMP_DIRECTORIES = [
    "/tmp",
    "/private/tmp",
]
USER_HOME_DIR = os.path.expanduser("~")

MAC_STARTUP_PATHS = [
    os.path.expanduser("~/Library/LaunchAgents"),
    "/Library/LaunchAgents",
    "/Library/LaunchDaemons",
]

BASELINE_FILE = os.path.join(STORAGE_DIR, "baseline.json")
EVENTS_FILE = os.path.join(STORAGE_DIR, "events.json")
REPORTS_DIR = os.path.join(STORAGE_DIR, "reports")
BROKEN_FILES_DIR = os.path.join(STORAGE_DIR, "broken")
ALLOWLIST_FILE = os.path.join(STORAGE_DIR, "allowlist.json")

IGNORED_PATH_PATTERNS = [
    ".DS_Store",
    ".localized",
    ".Spotlight-V100",
    ".Trashes",
    "__pycache__",
]

REVIEW_WORTHY_EXTENSIONS = [
    ".app",
    ".dmg",
    ".pkg",
    ".sh",
]

TRACKED_DIRECTORY_EXTENSIONS = [
    ".app",
]

BEHAVIOR_LOOKBACK_SECONDS = 300
SHORT_LIVED_PROCESS_SECONDS = 120
SMALL_EXECUTABLE_SIZE_BYTES = 64 * 1024
EVENT_DEDUP_WINDOW_SECONDS = 3

INTERACTIVE_PARENT_NAMES = [
    "Terminal",
    "iTerm2",
    "iTermServer",
    "Warp",
    "Finder",
    "PyCharm",
    "Code",
    "Visual Studio Code",
]

PYTHON_PROCESS_NAMES = [
    "python",
    "python3",
    "pythonw",
]

SCRIPT_EXTENSIONS = [
    ".py",
    ".sh",
    ".command",
]

RISK_SCORES = {
    "new_file": 5,
    "modified_file": 8,
    "deleted_file": 10,
    "new_process": 4,
    "terminated_process": 2,
    "new_startup_item": 20,
    "removed_startup_item": 10,
    "review_worthy_download": 0,
    "rapid_file_disappearance": 35,
    "downloads_process_execution": 30,
    "startup_file_link": 35,
    "downloads_app_execution": 30,
    "tmp_binary_execution": 35,
    "unattended_python_script": 25,
    "short_lived_process": 20,
    "small_executable": 15,
    "network_enabled_script": 20,
    "base64_encoded_script": 20,
    "shell_script_detected": 5,
    "launch_agent_keep_alive": 35,
    "launch_agent_run_at_load": 30,
    "launch_agent_user_path": 35,
    "download_execute_persist_chain": 80,
}

HIGH_RISK_THRESHOLD = 40
MEDIUM_RISK_THRESHOLD = 20
