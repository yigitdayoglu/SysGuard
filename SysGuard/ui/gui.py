import threading
import tkinter as tk
import webbrowser
from tkinter import messagebox

from SysGuard.config import APP_VERSION
from SysGuard.core.dashboard import load_dashboard_state
from SysGuard.core.humanize import summarize_recent_events, summarize_report, summarize_top_findings
from SysGuard.core.service import clear_events_history, clear_reports, perform_scan
from SysGuard.ui.web import run_web_panel


REFRESH_MS = 2000
WEB_HOST = "127.0.0.1"
WEB_PORT = 8765

COLORS = {
    "bg": "#08111d",
    "panel": "#101b2c",
    "panel_alt": "#162338",
    "border": "#27405f",
    "text": "#ecf4ff",
    "muted": "#8fa6c3",
    "accent": "#59d0ff",
    "good": "#4ade80",
    "warn": "#fbbf24",
    "bad": "#fb7185",
    "button": "#1d4ed8",
    "button_alt": "#1b2940",
}


def risk_color(level):
    if level == "HIGH":
        return COLORS["bad"]
    if level == "MEDIUM":
        return COLORS["warn"]
    return COLORS["good"]

def create_card(parent, title, value_var, subtitle_var=None, accent=None):
    frame = tk.Frame(parent, bg=COLORS["panel"], highlightbackground=COLORS["border"], highlightthickness=1)
    title_label = tk.Label(
        frame,
        text=title,
        bg=COLORS["panel"],
        fg=COLORS["muted"],
        font=("Helvetica", 10, "bold"),
    )
    title_label.pack(anchor="w", padx=14, pady=(12, 2))

    value_label = tk.Label(
        frame,
        textvariable=value_var,
        bg=COLORS["panel"],
        fg=accent or COLORS["text"],
        font=("Helvetica", 22, "bold"),
    )
    value_label.pack(anchor="w", padx=14)

    if subtitle_var is not None:
        subtitle_label = tk.Label(
            frame,
            textvariable=subtitle_var,
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Helvetica", 10),
        )
        subtitle_label.pack(anchor="w", padx=14, pady=(4, 12))
    else:
        tk.Frame(frame, bg=COLORS["panel"], height=18).pack()

    return frame


def create_text_panel(parent, title):
    frame = tk.Frame(parent, bg=COLORS["panel"], highlightbackground=COLORS["border"], highlightthickness=1)
    tk.Label(
        frame,
        text=title,
        bg=COLORS["panel"],
        fg=COLORS["text"],
        font=("Helvetica", 13, "bold"),
    ).pack(anchor="w", padx=14, pady=(12, 8))

    text = tk.Text(
        frame,
        bg=COLORS["panel_alt"],
        fg=COLORS["text"],
        insertbackground=COLORS["accent"],
        wrap="word",
        relief="flat",
        padx=12,
        pady=12,
        font=("Menlo", 11),
        highlightthickness=0,
    )
    text.pack(fill="both", expand=True, padx=14, pady=(0, 14))
    return frame, text


def create_action_button(parent, label, command, primary=False):
    background = COLORS["button"] if primary else COLORS["button_alt"]
    hover = "#2563eb" if primary else "#24364f"

    frame = tk.Frame(
        parent,
        bg=background,
        highlightbackground=COLORS["border"],
        highlightthickness=1 if not primary else 0,
        bd=0,
    )
    button_label = tk.Label(
        frame,
        text=label,
        bg=background,
        fg=COLORS["text"],
        padx=16,
        pady=10,
        cursor="hand2",
        font=("Helvetica", 11, "bold"),
    )
    button_label.pack()

    def set_bg(color):
        frame.configure(bg=color)
        button_label.configure(bg=color, fg=COLORS["text"])

    def on_enter(_event):
        set_bg(hover)

    def on_leave(_event):
        set_bg(background)

    def on_click(_event):
        command()

    for widget in (frame, button_label):
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        widget.bind("<Button-1>", on_click)

    return frame


def build_gui():
    root = tk.Tk()
    root.title(f"SysGuard App {APP_VERSION}")
    root.geometry("1220x840")
    root.configure(bg=COLORS["bg"])

    container = tk.Frame(root, bg=COLORS["bg"])
    container.pack(fill="both", expand=True, padx=18, pady=18)

    hero = tk.Frame(container, bg=COLORS["bg"])
    hero.pack(fill="x")

    tk.Label(
        hero,
        text=f"SysGuard Unified Console {APP_VERSION}",
        bg=COLORS["bg"],
        fg=COLORS["text"],
        font=("Helvetica", 28, "bold"),
    ).pack(anchor="w")

    tk.Label(
        hero,
        text="Security posture, findings, controls, and live visibility in one desktop view",
        bg=COLORS["bg"],
        fg=COLORS["muted"],
        font=("Helvetica", 12),
    ).pack(anchor="w", pady=(4, 16))

    action_row = tk.Frame(container, bg=COLORS["bg"])
    action_row.pack(fill="x", pady=(0, 14))

    status_var = tk.StringVar(value="Ready.")
    risk_value = tk.StringVar(value="LOW")
    risk_subtitle = tk.StringVar(value="Current security posture")
    score_value = tk.StringVar(value="0")
    score_subtitle = tk.StringVar(value="Composite risk score")
    behavior_value = tk.StringVar(value="0")
    behavior_subtitle = tk.StringVar(value="Behavior findings")
    correlation_value = tk.StringVar(value="0")
    correlation_subtitle = tk.StringVar(value="Threat correlations")
    report_var = tk.StringVar(value="Latest report: -")
    snapshot_var = tk.StringVar(value="Files 0 | Processes 0 | Startup 0")

    def make_button(label, command, primary=False):
        button = create_action_button(action_row, label, command, primary=primary)
        button.pack(side="left", padx=(0, 10))
        return button

    stats_grid = tk.Frame(container, bg=COLORS["bg"])
    stats_grid.pack(fill="x", pady=(0, 14))

    risk_card = create_card(stats_grid, "Risk Level", risk_value, risk_subtitle, accent=COLORS["bad"])
    score_card = create_card(stats_grid, "Risk Score", score_value, score_subtitle, accent=COLORS["accent"])
    behavior_card = create_card(stats_grid, "Behavior Findings", behavior_value, behavior_subtitle, accent=COLORS["warn"])
    correlation_card = create_card(stats_grid, "Correlation Findings", correlation_value, correlation_subtitle, accent=COLORS["good"])

    for column, widget in enumerate([risk_card, score_card, behavior_card, correlation_card]):
        widget.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 10, 0))
        stats_grid.grid_columnconfigure(column, weight=1)

    meta_panel = tk.Frame(container, bg=COLORS["panel"], highlightbackground=COLORS["border"], highlightthickness=1)
    meta_panel.pack(fill="x", pady=(0, 14))
    tk.Label(
        meta_panel,
        textvariable=report_var,
        bg=COLORS["panel"],
        fg=COLORS["text"],
        font=("Helvetica", 11, "bold"),
    ).pack(anchor="w", padx=14, pady=(12, 4))
    tk.Label(
        meta_panel,
        textvariable=snapshot_var,
        bg=COLORS["panel"],
        fg=COLORS["muted"],
        font=("Helvetica", 11),
    ).pack(anchor="w", padx=14, pady=(0, 4))
    tk.Label(
        meta_panel,
        textvariable=status_var,
        bg=COLORS["panel"],
        fg=COLORS["accent"],
        font=("Helvetica", 11),
    ).pack(anchor="w", padx=14, pady=(0, 12))

    content = tk.Frame(container, bg=COLORS["bg"])
    content.pack(fill="both", expand=True)
    content.grid_columnconfigure(0, weight=3)
    content.grid_columnconfigure(1, weight=2)
    content.grid_rowconfigure(0, weight=1)
    content.grid_rowconfigure(1, weight=1)

    findings_panel, findings_text = create_text_panel(content, "What Needs Attention")
    findings_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))

    events_panel, events_text = create_text_panel(content, "Recent Activity Explained")
    events_panel.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

    report_panel, reports_text = create_text_panel(content, "Latest Report In Plain Language")
    report_panel.grid(row=0, column=1, rowspan=2, sticky="nsew")

    web_server_started = {"value": False}

    def refresh_view():
        state = load_dashboard_state()
        summary = state["summary"]
        risk = state["risk"]
        snapshot_summary = state["snapshot_summary"]
        level = risk.get("level", "LOW")

        risk_value.set(level)
        risk_subtitle.set(f"Suppressed: {summary.get('suppressed_count', 0)}")
        score_value.set(str(risk.get("score", 0)))
        score_subtitle.set("Composite score from active findings")
        behavior_value.set(str(summary["kind_counts"].get("behavior", 0)))
        behavior_subtitle.set("Rule-based detections")
        correlation_value.set(str(summary["kind_counts"].get("correlation", 0)))
        correlation_subtitle.set("Multi-stage attack chains")
        report_var.set(f"Latest report: {state['report_path']}")
        snapshot_var.set(
            "Files {files} | Processes {processes} | Startup {startup}".format(
                files=snapshot_summary.get("file_count", 0),
                processes=snapshot_summary.get("process_count", 0),
                startup=snapshot_summary.get("startup_count", 0),
            )
        )

        risk_card.winfo_children()[1].configure(fg=risk_color(level))

        findings_text.delete("1.0", tk.END)
        findings_text.insert(tk.END, summarize_top_findings(summary["top_findings"]))

        events_text.delete("1.0", tk.END)
        events_text.insert(tk.END, summarize_recent_events(state["events"][-50:]))

        reports_text.delete("1.0", tk.END)
        reports_text.insert(tk.END, summarize_report(state["latest_report"]))

    def refresh():
        refresh_view()
        root.after(REFRESH_MS, refresh)

    def run_in_thread(fn, success_message):
        def worker():
            try:
                fn()
                root.after(0, lambda: status_var.set(success_message))
                root.after(0, refresh_view)
            except Exception as exc:
                root.after(0, lambda: status_var.set(f"Action failed: {exc}"))

        threading.Thread(target=worker, daemon=True).start()

    def quick_scan():
        status_var.set("Running quick scan...")
        run_in_thread(lambda: perform_scan(start_monitor=False), "Quick scan completed.")

    def clear_events():
        if not messagebox.askyesno("Clear Events", "Clear all recorded events?"):
            return
        status_var.set("Clearing events...")
        run_in_thread(clear_events_history, "Recorded events cleared.")

    def clear_saved_reports():
        if not messagebox.askyesno("Clear Reports", "Delete all saved reports?"):
            return
        status_var.set("Clearing reports...")
        run_in_thread(clear_reports, "Saved reports cleared.")

    def start_web():
        if not web_server_started["value"]:
            threading.Thread(
                target=lambda: run_web_panel(host=WEB_HOST, port=WEB_PORT),
                daemon=True,
            ).start()
            web_server_started["value"] = True
        webbrowser.open(f"http://{WEB_HOST}:{WEB_PORT}/?v={APP_VERSION}")
        status_var.set(f"Web panel ready at http://{WEB_HOST}:{WEB_PORT}")

    make_button("Refresh", refresh_view)
    make_button("Quick Scan", quick_scan, primary=True)
    make_button("Open Web Panel", start_web)
    make_button("Clear Events", clear_events)
    make_button("Clear Reports", clear_saved_reports)

    refresh()
    return root


def run_gui():
    app = build_gui()
    app.mainloop()
