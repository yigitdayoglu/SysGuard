# SysGuard

SysGuard is a cross-platform desktop security monitoring tool that starts from simple filesystem visibility and grows into behavior-aware detection, persistence analysis, threat correlation, and a packaged desktop experience.

## What it does

- Monitors sensitive user folders such as `Desktop`, `Downloads`, and `Documents`
- Builds a system baseline and detects changes over time
- Flags review-worthy downloads such as `.app`, `.dmg`, `.pkg`, `.sh`, `.exe`, `.msi`, `.ps1`, `.bat`, and `.cmd`
- Detects suspicious behavior chains like download -> execution -> persistence
- Inspects lightweight script and executable signals
- Tracks macOS LaunchAgents and Windows startup folder / registry persistence
- Provides a terminal dashboard, desktop GUI, and web panel
- Ships with macOS app/DMG helpers and Windows executable build helpers

## Project layout

- `main.py`: CLI entrypoint
- `app_entry.py`: packaged app launcher
- `SysGuard/`: core monitoring, scoring, UI, and reporting logic
- `scripts/`: build and packaging automation
- `assets/`: generated icon and visual assets

## Download and install

### Option 1: Download the packaged macOS app

Download the installer image from:

- [Direct DMG download](https://github.com/yigitdayoglu/SysGuard/raw/main/release/SysGuard-7.5-macOS.dmg)
- [Repository file view](https://github.com/yigitdayoglu/SysGuard/blob/main/release/SysGuard-7.5-macOS.dmg)
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

### Option 2: Run from source on macOS or Linux

If you prefer to run the project directly:

```bash
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/python main.py app
```

### Option 3: Run from source on Windows

```powershell
py -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python main.py app
```

Or launch the desktop app with:

```powershell
.\start_sysguard.ps1
```

## Local development

Install runtime dependencies on macOS or Linux:

```bash
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

Install runtime dependencies on Windows:

```powershell
py -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

Run the unified desktop app:

```bash
./.venv/bin/python main.py app
```

Windows:

```powershell
.\.venv\Scripts\python main.py app
```

Run a one-time scan:

```bash
./.venv/bin/python main.py scan --no-monitor
```

Windows:

```powershell
.\.venv\Scripts\python main.py scan --no-monitor
```

## Packaging

Build the native macOS app:

```bash
./build_sysguard_app.command
```

Build the release DMG:

```bash
./build_release.command
```

More packaging notes are available in [PACKAGING.md](PACKAGING.md).

Build the Windows executable:

```powershell
.\.venv\Scripts\pip install -r requirements-dev.txt
.\build_windows_exe.ps1
```

The Windows build is written to `dist\SysGuard\SysGuard.exe`.

## How people can use it

For normal users:

1. On macOS, download `release/SysGuard-7.5-macOS.dmg`
2. Install the app into `Applications`
3. Open SysGuard and allow any macOS permissions it asks for
4. On Windows, run from source or build `dist\SysGuard\SysGuard.exe` with the Windows packaging command

For developers:

1. Clone the repository
2. Install dependencies
3. Run `main.py app`
4. Optionally build a native `.app`, `.dmg`, or Windows `.exe`

## Runtime storage

When running from source, SysGuard uses the local `storage/` folder.

When running as a packaged macOS app, SysGuard stores runtime data in:

`~/Library/Application Support/SysGuard`

When running as a packaged Windows app, SysGuard stores runtime data in:

`%LOCALAPPDATA%\SysGuard`
