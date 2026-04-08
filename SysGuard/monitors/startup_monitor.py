import os
import plistlib
from SysGuard.config import IGNORED_PATH_PATTERNS, MAC_STARTUP_PATHS


def read_plist_safely(plist_path):
    try:
        with open(plist_path, "rb") as file:
            data = plistlib.load(file)
            return data
    except Exception:
        return None


def get_startup_items():
    items = []

    for path in MAC_STARTUP_PATHS:
        if not os.path.exists(path):
            continue

        for item in os.listdir(path):
            full_path = os.path.join(path, item)

            # ignore macOS noise files
            if any(pattern in full_path for pattern in IGNORED_PATH_PATTERNS):
                continue

            if not os.path.isfile(full_path):
                continue

            plist_data = read_plist_safely(full_path)

            items.append({
                "name": item,
                "path": full_path,
                "label": plist_data.get("Label") if plist_data else None,
                "program": plist_data.get("Program") if plist_data else None,
                "program_arguments": plist_data.get("ProgramArguments") if plist_data else None,
                "working_directory": plist_data.get("WorkingDirectory") if plist_data else None,
                "run_at_load": plist_data.get("RunAtLoad") if plist_data else None,
                "keep_alive": plist_data.get("KeepAlive") if plist_data else None,
            })

    return items
