import os
import sys
import traceback
from datetime import datetime

from SysGuard.config import LOGS_DIR
from SysGuard.core.reporter import ensure_storage
from SysGuard.ui.web import run_web_panel


def write_exception_log(exc, prefix="app_crash"):
    try:
        ensure_storage()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        path = os.path.join(LOGS_DIR, f"{prefix}_{timestamp}.log")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(f"SysGuard {prefix} at {datetime.now().isoformat()}\n\n")
            handle.write("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
        return path
    except Exception:
        return None


def show_error_dialog(message):
    try:
        from tkinter import Tk, messagebox

        root = Tk()
        root.withdraw()
        messagebox.showerror("SysGuard", message)
        root.destroy()
    except Exception:
        print(message, file=sys.stderr)


def run_web_fallback():
    import threading
    import webbrowser

    host = "127.0.0.1"
    port = 8765
    threading.Thread(
        target=lambda: run_web_panel(host=host, port=port),
        daemon=True,
    ).start()
    webbrowser.open(f"http://{host}:{port}/?v=app-fallback")
    print(f"[INFO] SysGuard web panel fallback ready at http://{host}:{port}")

    try:
        while True:
            threading.Event().wait(3600)
    except KeyboardInterrupt:
        return


def main():
    ensure_storage()

    try:
        from SysGuard.ui.gui import run_gui
        run_gui()
    except Exception as gui_exc:
        write_exception_log(gui_exc, prefix="gui_fallback")
        try:
            run_web_fallback()
        except Exception as fallback_exc:
            log_path = write_exception_log(fallback_exc)
            details = f"\n\nCrash log: {log_path}" if log_path else ""
            show_error_dialog(
                "SysGuard could not start cleanly."
                f"{details}"
                "\n\nPlease reopen the app after checking the log."
            )
            raise


if __name__ == "__main__":
    main()
