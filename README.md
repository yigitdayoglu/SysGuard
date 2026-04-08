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

## Download and install

### Option 1: Download the packaged macOS app

Download the installer image from:

- [Direct DMG download](https://github.com/yigitdayoglu/SysGuard/raw/main/release/SysGuard-7.4-macOS.dmg)
- [Repository file view](https://github.com/yigitdayoglu/SysGuard/blob/main/release/SysGuard-7.4-macOS.dmg)
- [Releases page](https://github.com/yigitdayoglu/SysGuard/releases)

After downloading:

1. Open the `.dmg`
2. Drag `SysGuard.app` into `Applications`
3. Open `Applications > SysGuard`

If macOS blocks the app the first time:

1. Right-click `SysGuard.app`
2. Choose `Open`
3. Confirm the dialog

Note:

- The app is ad-hoc signed for easy local distribution
- It is not notarized yet, so a first-launch warning on macOS is expected

### Option 2: Run from source

If you prefer to run the project directly:

```bash
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/python main.py app
```

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

## How people can use it

For normal users:

1. Download `release/SysGuard-7.4-macOS.dmg`
2. Install the app into `Applications`
3. Open SysGuard and allow any macOS permissions it asks for

For developers:

1. Clone the repository
2. Install dependencies
3. Run `main.py app`
4. Optionally build a native `.app` or `.dmg`

## Runtime storage

When running from source, SysGuard uses the local `storage/` folder.

When running as a packaged macOS app, SysGuard stores runtime data in:

`~/Library/Application Support/SysGuard`
