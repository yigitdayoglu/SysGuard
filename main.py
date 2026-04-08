import argparse

from SysGuard.core.dashboard import build_dashboard, run_terminal_dashboard
from SysGuard.core.reporter import ensure_storage, summarize_events
from SysGuard.core.service import clear_events_history, clear_reports, perform_scan
from SysGuard.monitors.file_monitor import start_file_monitor
from SysGuard.ui.gui import run_gui
from SysGuard.ui.web import run_web_panel


def print_scan_summary(events):
    summary = summarize_events(events)
    kind_counts = summary["kind_counts"]
    suppressed_count = summary["suppressed_count"]
    top_findings = summary["top_findings"][:5]

    print(
        "[INFO] Event breakdown: "
        f"raw={kind_counts.get('raw', 0)}, "
        f"behavior={kind_counts.get('behavior', 0)}, "
        f"correlation={kind_counts.get('correlation', 0)}, "
        f"suppressed={suppressed_count}"
    )

    if top_findings:
        print("[INFO] Top findings:")
        for finding in top_findings:
            print(f"  - {finding.get('type')}: {finding.get('target')}")


def print_dashboard(snapshot, events, risk, report_path):
    summary = summarize_events(events)
    print()
    print(build_dashboard(snapshot, events, risk, report_path, summary))
    print()


def run_scan(start_monitor=True):
    result = perform_scan(start_monitor=False)

    if result["baseline_created"]:
        print("[INFO] Baseline created successfully.")
        print("[INFO] Run the program again after making a few file changes to detect events.")
        return

    print("[INFO] Scan complete.")
    print(f"[INFO] Events found: {len(result['events'])}")
    print(f"[INFO] Risk score: {result['risk']['score']} ({result['risk']['level']})")
    print(f"[INFO] Report saved to: {result['report_path']}")
    print_dashboard(result["snapshot"], result["events"], result["risk"], result["report_path"])
    print_scan_summary(result["events"])

    if start_monitor:
        print("[INFO] Starting live file monitor...")
        print("[INFO] Press Ctrl+C to stop monitoring.")
        start_file_monitor()


def build_parser():
    parser = argparse.ArgumentParser(description="SysGuard security monitor")
    subparsers = parser.add_subparsers(dest="command")

    scan_parser = subparsers.add_parser("scan", help="run scan and start monitor")
    scan_parser.add_argument("--no-monitor", action="store_true", help="run only one scan")

    dashboard_parser = subparsers.add_parser("dashboard", help="run terminal dashboard")
    dashboard_parser.add_argument("--interval", type=int, default=2, help="refresh interval in seconds")

    web_parser = subparsers.add_parser("web", help="run web panel")
    web_parser.add_argument("--host", default="127.0.0.1")
    web_parser.add_argument("--port", type=int, default=8765)

    subparsers.add_parser("gui", help="run desktop GUI")
    subparsers.add_parser("app", help="launch unified SysGuard app")
    subparsers.add_parser("clear-events", help="clear recorded events")
    subparsers.add_parser("clear-reports", help="clear saved reports")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command in {None, "scan"}:
        run_scan(start_monitor=not getattr(args, "no_monitor", False))
        return

    ensure_storage()

    if args.command == "dashboard":
        run_terminal_dashboard(interval_seconds=max(1, args.interval))
        return

    if args.command in {"gui", "app"}:
        run_gui()
        return

    if args.command == "web":
        run_web_panel(host=args.host, port=args.port)
        return

    if args.command == "clear-events":
        path = clear_events_history()
        print(f"[INFO] Cleared events: {path}")
        return

    if args.command == "clear-reports":
        removed = clear_reports()
        print(f"[INFO] Removed reports: {removed}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
