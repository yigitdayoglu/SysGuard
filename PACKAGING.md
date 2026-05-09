# SysGuard Packaging

## Build the native macOS app

Run:

```bash
./build_sysguard_app.command
```

This generates a native macOS app bundle at `SysGuard.app`.

## Build the release DMG

Run:

```bash
./build_release.command
```

This will:

1. Generate visual assets
2. Build the native `SysGuard.app`
3. Ad-hoc sign the app
4. Build `release/SysGuard-7.5-macOS.dmg`

## Build the Windows executable

Run in PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\pip install -r requirements-dev.txt
.\build_windows_exe.ps1
```

This will:

1. Generate visual assets, including `assets\SysGuard.ico`
2. Build the desktop app with PyInstaller
3. Write `dist\SysGuard\SysGuard.exe`
4. Build `release\SysGuard-7.5-Windows.zip`

## Release assets

Publish operating-system-specific assets under the same GitHub release version:

- `SysGuard-7.5-macOS.dmg` for macOS
- `SysGuard-7.5-Windows.zip` for Windows

## Storage location

When the packaged app runs, SysGuard stores its runtime data in:

`~/Library/Application Support/SysGuard`

On Windows, the packaged app stores runtime data in:

`%LOCALAPPDATA%\SysGuard`

## Notes

- The DMG includes `SysGuard.app`, an `Applications` shortcut, and a short install guide.
- The app is ad-hoc signed for local distribution and testing.
- For public distribution outside your own machine, notarization is still recommended.
- Windows builds are unsigned unless you add a code-signing certificate to the release flow.
