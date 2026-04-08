import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from SysGuard.config import APP_VERSION
from SysGuard.core.dashboard import load_dashboard_state
from SysGuard.core.humanize import summarize_recent_events, summarize_report, summarize_top_findings
from SysGuard.core.service import clear_events_history, clear_reports, perform_scan

def render_type_list(type_counts):
    items = list(type_counts.keys())[:4]
    if not items:
        return "None"
    return "<br>".join(html.escape(item) for item in items)


def render_html(message=""):
    state = load_dashboard_state()
    summary = state["summary"]
    risk = state["risk"]
    snapshot = state["snapshot_summary"]
    events_text = summarize_recent_events(state["events"][-50:])
    report_text = summarize_report(state["latest_report"])
    findings_text = summarize_top_findings(summary["top_findings"])

    banner = f'<div class="banner">{html.escape(message)}</div>' if message else ""
    risk_level = html.escape(risk.get("level", "LOW"))
    risk_class = f"risk-{risk.get('level', 'LOW').lower()}"

    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="3">
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
  <meta http-equiv="Pragma" content="no-cache">
  <meta http-equiv="Expires" content="0">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>SysGuard {APP_VERSION}</title>
  <style>
    :root {{
      --bg: #07111d;
      --bg-soft: #0d1a2a;
      --panel: rgba(17, 28, 45, 0.92);
      --panel-strong: #13233a;
      --text: #edf5ff;
      --muted: #8ea4c0;
      --line: rgba(125, 211, 252, 0.16);
      --accent: #67d6ff;
      --accent-strong: #0ea5e9;
      --good: #4ade80;
      --warn: #fbbf24;
      --bad: #fb7185;
      --shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
    }}
    * {{ box-sizing: border-box; }}
    html {{
      -webkit-text-size-adjust: 100%;
      text-size-adjust: 100%;
      font-size: 15px;
    }}
    body {{
      margin: 0;
      color: var(--text);
      font-family: "SF Pro Display", "Segoe UI", Helvetica, Arial, sans-serif;
      overflow-x: hidden;
      background:
        radial-gradient(circle at top left, rgba(14, 165, 233, 0.22), transparent 32%),
        radial-gradient(circle at top right, rgba(103, 214, 255, 0.14), transparent 24%),
        linear-gradient(180deg, #091422 0%, var(--bg) 58%);
    }}
    .wrap {{
      width: 100%;
      margin: 0 auto;
      padding: 18px 24px 28px;
    }}
    .hero {{
      display: grid;
      grid-template-columns: 1.5fr 1fr;
      gap: 14px;
      margin-bottom: 14px;
    }}
    .hero-main, .hero-side, .panel, .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 22px;
      box-shadow: var(--shadow);
    }}
    .hero-main {{
      padding: 20px;
    }}
    .eyebrow {{
      color: var(--accent);
      text-transform: uppercase;
      letter-spacing: 0.12em;
      font-size: 12px;
      font-weight: 700;
    }}
    h1 {{
      margin: 8px 0 6px;
      font-size: 2rem;
      line-height: 1.1;
    }}
    .hero-copy {{
      margin: 0;
      color: var(--muted);
      font-size: 0.98rem;
      line-height: 1.55;
      max-width: 60ch;
    }}
    .hero-side {{
      padding: 18px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      background:
        linear-gradient(160deg, rgba(103, 214, 255, 0.14), transparent 55%),
        var(--panel);
    }}
    .risk-chip {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 10px 14px;
      border-radius: 999px;
      font-weight: 700;
      width: fit-content;
      margin-bottom: 16px;
    }}
    .risk-high {{ background: rgba(251, 113, 133, 0.14); color: var(--bad); }}
    .risk-medium {{ background: rgba(251, 191, 36, 0.14); color: var(--warn); }}
    .risk-low {{ background: rgba(74, 222, 128, 0.14); color: var(--good); }}
    .hero-meta {{
      color: var(--muted);
      font-size: 0.92rem;
      line-height: 1.7;
      word-break: break-word;
      overflow-wrap: anywhere;
    }}
    .actions {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin: 0 0 14px;
    }}
    button {{
      border: 0;
      border-radius: 999px;
      padding: 9px 14px;
      font-weight: 700;
      cursor: pointer;
      color: #05111d;
      background: linear-gradient(135deg, var(--accent), #22d3ee);
      box-shadow: 0 10px 24px rgba(14, 165, 233, 0.28);
      font-size: 0.94rem;
    }}
    button.alt {{
      color: var(--text);
      background: #18263a;
      box-shadow: none;
      border: 1px solid var(--line);
    }}
    .banner {{
      background: rgba(74, 222, 128, 0.14);
      border: 1px solid rgba(74, 222, 128, 0.25);
      color: var(--text);
      padding: 14px 16px;
      border-radius: 16px;
      margin-bottom: 18px;
    }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin-bottom: 16px;
    }}
    .card {{
      padding: 14px;
    }}
    .label {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-weight: 700;
      overflow-wrap: anywhere;
    }}
    .value {{
      margin-top: 8px;
      font-size: 1.45rem;
      font-weight: 800;
      font-family: "SF Mono", Menlo, Monaco, monospace;
      word-break: break-word;
      overflow-wrap: anywhere;
      line-height: 1.2;
    }}
    .value.small {{
      font-size: 1rem;
    }}
    .layout {{
      display: grid;
      grid-template-columns: 1.2fr 1fr;
      gap: 14px;
    }}
    .stack {{
      display: grid;
      gap: 14px;
    }}
    .panel {{
      padding: 16px;
    }}
    h2 {{
      margin: 0 0 14px;
      font-size: 1.02rem;
    }}
    .snapshot-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }}
    .snapshot-box {{
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 16px;
      padding: 12px;
    }}
    .finding-list {{
      list-style: none;
      padding: 0;
      margin: 0;
      display: grid;
      gap: 10px;
    }}
    .finding-item {{
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 16px;
      padding: 12px;
    }}
    .finding-type {{
      color: var(--accent);
      font-family: "SF Mono", Menlo, Monaco, monospace;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 6px;
    }}
    .finding-target {{
      font-weight: 700;
      line-height: 1.4;
      margin-bottom: 6px;
      word-break: break-word;
      overflow-wrap: anywhere;
    }}
    .finding-reason {{
      color: var(--muted);
      line-height: 1.5;
      font-size: 0.9rem;
    }}
    .finding-empty {{
      color: var(--muted);
      padding: 10px 0;
    }}
    pre {{
      margin: 0;
      overflow: auto;
      white-space: pre-wrap;
      word-break: break-word;
      overflow-wrap: anywhere;
      color: #dce9fb;
      background: #0b1522;
      border-radius: 16px;
      padding: 16px;
      border: 1px solid rgba(255, 255, 255, 0.04);
      max-height: 480px;
      font-family: "SF Mono", Menlo, Monaco, monospace;
      font-size: 0.78rem;
    }}
    @media (max-width: 980px) {{
      .hero, .layout {{ grid-template-columns: 1fr; }}
      .snapshot-grid {{ grid-template-columns: 1fr; }}
      .wrap {{ width: 100%; padding: 14px; }}
      h1 {{ font-size: 1.45rem; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <section class="hero-main">
        <div class="eyebrow">Unified Visibility</div>
        <h1>SysGuard Security Control Surface {APP_VERSION}</h1>
        <p class="hero-copy">
          Review current device posture, launch on-demand scans, and move from
          raw activity to behavior and threat correlation without leaving the panel.
        </p>
      </section>
      <aside class="hero-side">
        <div class="risk-chip {risk_class}">Risk: {risk_level}</div>
        <div class="hero-meta">
          <div><strong>Score:</strong> {risk.get("score", 0)}</div>
          <div><strong>Latest report:</strong> {html.escape(str(state["report_path"]))}</div>
          <div><strong>Suppressed events:</strong> {summary.get("suppressed_count", 0)}</div>
        </div>
      </aside>
    </div>
    {banner}
    <form class="actions" method="post" action="/action">
      <button type="submit" name="name" value="scan">Quick Scan</button>
      <button type="submit" class="alt" name="name" value="clear-events">Clear Events</button>
      <button type="submit" class="alt" name="name" value="clear-reports">Clear Reports</button>
    </form>
    <section class="cards">
      <article class="card"><div class="label">Behavior Findings</div><div class="value">{summary["kind_counts"].get("behavior", 0)}</div></article>
      <article class="card"><div class="label">Correlation Findings</div><div class="value">{summary["kind_counts"].get("correlation", 0)}</div></article>
      <article class="card"><div class="label">Raw Events</div><div class="value">{summary["kind_counts"].get("raw", 0)}</div></article>
      <article class="card"><div class="label">Top Active Types</div><div class="value small">{render_type_list(summary["type_counts"])}</div></article>
    </section>
    <section class="layout">
      <div class="stack">
        <section class="panel">
          <h2>What Needs Attention</h2>
          <pre>{html.escape(findings_text)}</pre>
        </section>
        <section class="panel">
          <h2>Recent Activity Explained</h2>
          <pre>{html.escape(events_text)}</pre>
        </section>
      </div>
      <div class="stack">
        <section class="panel">
          <h2>System Snapshot</h2>
          <div class="snapshot-grid">
            <div class="snapshot-box"><div class="label">Files</div><div class="value">{snapshot.get("file_count", 0)}</div></div>
            <div class="snapshot-box"><div class="label">Processes</div><div class="value">{snapshot.get("process_count", 0)}</div></div>
            <div class="snapshot-box"><div class="label">Startup</div><div class="value">{snapshot.get("startup_count", 0)}</div></div>
          </div>
        </section>
        <section class="panel">
          <h2>Latest Report In Plain Language</h2>
          <pre>{html.escape(report_text)}</pre>
        </section>
      </div>
    </section>
  </div>
</body>
</html>"""


class SysGuardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path not in {"/", "/index.html"}:
            self.send_response(404)
            self.end_headers()
            return

        body = render_html().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/action":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(length).decode("utf-8")
        params = parse_qs(payload)
        action = (params.get("name") or [""])[0]

        message = "No action performed."
        if action == "scan":
            result = perform_scan(start_monitor=False)
            message = "Quick scan completed." if not result["baseline_created"] else "Baseline created."
        elif action == "clear-events":
            clear_events_history()
            message = "Recorded events cleared."
        elif action == "clear-reports":
            removed = clear_reports()
            message = f"Saved reports removed: {removed}"

        body = render_html(message=message).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def run_web_panel(host="127.0.0.1", port=8765):
    server = ThreadingHTTPServer((host, port), SysGuardHandler)
    print(f"[INFO] SysGuard web panel running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Web panel stopped.")
    finally:
        server.server_close()
