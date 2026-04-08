import os
import sys
import traceback
from datetime import datetime
from tkinter import Tk, messagebox

from SysGuard.config import LOGS_DIR
from SysGuard.core.reporter import ensure_storage
from SysGuard.ui.gui import run_gui


def write_crash_log(exc):
    try:
        ensure_storage()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        path = os.path.join(LOGS_DIR, f"app_crash_{timestamp}.log")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(f"SysGuard app crash at {datetime.now().isoformat()}\n\n")
            handle.write("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
        return path
    except Exception:
        return None


def show_error_dialog(message):
    root = Tk()
    root.withdraw()
    messagebox.showerror("SysGuard", message)
    root.destroy()


def main():
    try:
        ensure_storage()
        run_gui()
    except Exception as exc:
        log_path = write_crash_log(exc)
        details = f"\n\nCrash log: {log_path}" if log_path else ""
        show_error_dialog(
            "SysGuard could not start cleanly."
            f"{details}"
            "\n\nPlease reopen the app after checking the log."
        )
        raise


if __name__ == "__main__":
    main()
