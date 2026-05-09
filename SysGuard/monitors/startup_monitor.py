import os
import plistlib

from SysGuard.config import IGNORED_PATH_PATTERNS, IS_MACOS, IS_WINDOWS, STARTUP_FILE_PATHS

if IS_WINDOWS:
    import winreg
else:
    winreg = None


WINDOWS_REGISTRY_STARTUP_KEYS = [
    ("HKCU", r"Software\Microsoft\Windows\CurrentVersion\Run"),
    ("HKCU", r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
    ("HKLM", r"Software\Microsoft\Windows\CurrentVersion\Run"),
    ("HKLM", r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
    ("HKLM", r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"),
]


def read_plist_safely(plist_path):
    try:
        with open(plist_path, "rb") as file:
            return plistlib.load(file)
    except Exception:
        return None


def should_ignore(path):
    return any(pattern in path for pattern in IGNORED_PATH_PATTERNS)


def expand_windows_command(value):
    if not isinstance(value, str):
        return value
    return os.path.expandvars(value)


def read_windows_shortcut_target(path):
    if not IS_WINDOWS or not path.lower().endswith(".lnk"):
        return None

    try:
        import pythoncom
        from win32com.shell import shell
    except ImportError:
        return None

    try:
        pythoncom.CoInitialize()
        shortcut = pythoncom.CoCreateInstance(
            shell.CLSID_ShellLink,
            None,
            pythoncom.CLSCTX_INPROC_SERVER,
            shell.IID_IShellLink,
        )
        persist_file = shortcut.QueryInterface(pythoncom.IID_IPersistFile)
        persist_file.Load(path)
        target, _find_data = shortcut.GetPath(shell.SLGP_UNCPRIORITY)
        arguments = shortcut.GetArguments()
        working_directory = shortcut.GetWorkingDirectory()
        return {
            "target": expand_windows_command(target),
            "arguments": arguments,
            "working_directory": expand_windows_command(working_directory),
        }
    except Exception:
        return None
    finally:
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass


def build_file_startup_item(full_path, name):
    if IS_MACOS:
        plist_data = read_plist_safely(full_path)
        return {
            "name": name,
            "path": full_path,
            "label": plist_data.get("Label") if plist_data else None,
            "program": plist_data.get("Program") if plist_data else None,
            "program_arguments": plist_data.get("ProgramArguments") if plist_data else None,
            "working_directory": plist_data.get("WorkingDirectory") if plist_data else None,
            "run_at_load": plist_data.get("RunAtLoad") if plist_data else None,
            "keep_alive": plist_data.get("KeepAlive") if plist_data else None,
            "startup_source": "launch_agent",
            "platform": "macos",
        }

    shortcut_target = read_windows_shortcut_target(full_path)
    program = shortcut_target.get("target") if shortcut_target else full_path
    arguments = shortcut_target.get("arguments") if shortcut_target else ""
    program_arguments = [program]
    if arguments:
        program_arguments.append(arguments)

    return {
        "name": name,
        "path": full_path,
        "label": name,
        "program": program,
        "program_arguments": program_arguments,
        "working_directory": (
            shortcut_target.get("working_directory")
            if shortcut_target and shortcut_target.get("working_directory")
            else os.path.dirname(full_path)
        ),
        "run_at_load": True,
        "keep_alive": None,
        "startup_source": "startup_folder",
        "platform": "windows" if IS_WINDOWS else "desktop",
    }


def get_file_startup_items():
    items = []

    for path in STARTUP_FILE_PATHS:
        if not os.path.exists(path):
            continue

        try:
            entries = os.listdir(path)
        except (OSError, PermissionError):
            continue

        for item in entries:
            full_path = os.path.join(path, item)
            if should_ignore(full_path) or not os.path.isfile(full_path):
                continue
            items.append(build_file_startup_item(full_path, item))

    return items


def registry_root(root_name):
    if root_name == "HKCU":
        return winreg.HKEY_CURRENT_USER
    if root_name == "HKLM":
        return winreg.HKEY_LOCAL_MACHINE
    return None


def get_registry_startup_items():
    if not IS_WINDOWS or winreg is None:
        return []

    items = []
    for root_name, key_path in WINDOWS_REGISTRY_STARTUP_KEYS:
        root = registry_root(root_name)
        if root is None:
            continue

        try:
            with winreg.OpenKey(root, key_path) as key:
                index = 0
                while True:
                    try:
                        name, value, _value_type = winreg.EnumValue(key, index)
                    except OSError:
                        break

                    command = expand_windows_command(value if isinstance(value, str) else str(value))
                    items.append({
                        "name": name,
                        "path": f"registry:{root_name}\\{key_path}:{name}",
                        "label": name,
                        "program": command,
                        "program_arguments": [command],
                        "working_directory": None,
                        "run_at_load": True,
                        "keep_alive": None,
                        "startup_source": f"{root_name}\\{key_path}",
                        "platform": "windows",
                    })
                    index += 1
        except OSError:
            continue

    return items


def get_startup_items():
    return get_file_startup_items() + get_registry_startup_items()
