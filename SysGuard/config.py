import os
import sys
import tempfile

APP_VERSION = "V7.5"

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(PACKAGE_DIR)
PLATFORM = sys.platform
IS_MACOS = PLATFORM == "darwin"
IS_WINDOWS = PLATFORM.startswith("win")
USER_HOME_DIR = os.path.expanduser("~")


def _dedupe_existing(paths):
    seen = set()
    result = []
    for path in paths:
        if not path:
            continue
        expanded = os.path.expandvars(os.path.expanduser(path))
        normalized = os.path.normcase(os.path.normpath(expanded))
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append(expanded)
    return result


def _default_storage_dir():
    if getattr(sys, "frozen", False):
        if IS_WINDOWS:
            base_dir = (
                os.environ.get("LOCALAPPDATA")
                or os.environ.get("APPDATA")
                or USER_HOME_DIR
            )
            return os.path.join(base_dir, "SysGuard")
        if IS_MACOS:
            return os.path.join(
                os.path.expanduser("~/Library/Application Support"),
                "SysGuard",
            )
        return os.path.join(os.path.expanduser("~/.local/share"), "SysGuard")
    return os.path.join(PROJECT_ROOT, "storage")


STORAGE_DIR = _default_storage_dir()
LOGS_DIR = os.path.join(STORAGE_DIR, "logs")

WATCH_DIRECTORIES = _dedupe_existing([
    os.path.join(USER_HOME_DIR, "Desktop"),
    os.path.join(USER_HOME_DIR, "Downloads"),
    os.path.join(USER_HOME_DIR, "Documents"),
])
DOWNLOADS_DIR = os.path.expanduser("~/Downloads")
TMP_DIRECTORIES = _dedupe_existing([
    tempfile.gettempdir(),
    os.environ.get("TEMP"),
    os.environ.get("TMP"),
    "/tmp",
    "/private/tmp",
    r"C:\Windows\Temp",
])

if IS_WINDOWS:
    STARTUP_FILE_PATHS = _dedupe_existing([
        r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup",
        r"%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs\Startup",
    ])
elif IS_MACOS:
    STARTUP_FILE_PATHS = _dedupe_existing([
        "~/Library/LaunchAgents",
        "/Library/LaunchAgents",
        "/Library/LaunchDaemons",
    ])
else:
    STARTUP_FILE_PATHS = _dedupe_existing([
        "~/.config/autostart",
    ])

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
    "Thumbs.db",
    "desktop.ini",
    os.sep + ".tools" + os.sep,
    os.sep + ".venv" + os.sep,
    os.sep + "build" + os.sep,
    os.sep + "dist" + os.sep,
    os.sep + "storage" + os.sep,
]

REVIEW_WORTHY_EXTENSIONS = [
    ".app",
    ".dmg",
    ".pkg",
    ".sh",
    ".command",
    ".exe",
    ".msi",
    ".bat",
    ".cmd",
    ".ps1",
    ".scr",
    ".vbs",
    ".js",
]

TRACKED_DIRECTORY_EXTENSIONS = [".app"] if IS_MACOS else []

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
    "cmd",
    "cmd.exe",
    "PowerShell",
    "powershell",
    "powershell.exe",
    "pwsh",
    "pwsh.exe",
    "WindowsTerminal",
    "WindowsTerminal.exe",
    "explorer",
    "explorer.exe",
]

PYTHON_PROCESS_NAMES = [
    "python",
    "python3",
    "pythonw",
    "python.exe",
    "pythonw.exe",
]

SCRIPT_EXTENSIONS = [
    ".py",
    ".sh",
    ".command",
    ".bat",
    ".cmd",
    ".ps1",
    ".vbs",
    ".js",
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
    "startup_keep_alive": 35,
    "startup_run_at_load": 30,
    "startup_user_path": 35,
    "launch_agent_keep_alive": 35,
    "launch_agent_run_at_load": 30,
    "launch_agent_user_path": 35,
    "download_execute_persist_chain": 80,
}

HIGH_RISK_THRESHOLD = 40
MEDIUM_RISK_THRESHOLD = 20
