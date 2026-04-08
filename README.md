# SysGuard

SysGuard is a macOS-focused security monitoring tool that starts from simple filesystem visibility and grows into behavior-aware detection, persistence analysis, threat correlation, and a packaged desktop experience.

## What it does

- Monitors sensitive user folders such as `Desktop`, `Downloads`, and `Documents`
- Builds a system baseline and detects changes over time
- Flags review-worthy downloads such as `.app`, `.dmg`, `.pkg`, and `.sh`
- Detects suspicious behavior chains like download -> execution -> persistence
- Inspects lightweight script and executable signals
- Tracks LaunchAgents and persistence-related settings
- Provides a terminal dashboard, desktop GUI, and web panel
- Ships as a native macOS `.app` with a distributable `.dmg`

## Project layout

- `main.py`: CLI entrypoint
- `app_entry.py`: packaged app launcher
- `SysGuard/`: core monitoring, scoring, UI, and reporting logic
- `scripts/`: build and packaging automation
- `assets/`: generated icon and visual assets

## Local development

Install dependencies:

```bash
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

Run the unified desktop app:

```bash
./.venv/bin/python main.py app
```

Run a one-time scan:

```bash
./.venv/bin/python main.py scan --no-monitor
```

## Packaging

Build the native app:

```bash
./build_sysguard_app.command
```

Build the release DMG:

```bash
./build_release.command
```

More packaging notes are available in [PACKAGING.md](PACKAGING.md).

## Runtime storage

When running from source, SysGuard uses the local `storage/` folder.

When running as a packaged macOS app, SysGuard stores runtime data in:

`~/Library/Application Support/SysGuard`
