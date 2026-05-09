# SysGuard V7.5 Release Notes

## Windows support

- Added Windows-aware runtime storage under `%LOCALAPPDATA%\SysGuard` for packaged builds.
- Added Windows startup persistence monitoring for Startup folders and common `Run` / `RunOnce` registry keys.
- Added best-effort Windows `.lnk` target resolution for Startup folder shortcuts.
- Added environment-variable expansion for Windows startup commands before behavior correlation.
- Added Windows review-worthy extensions such as `.exe`, `.msi`, `.ps1`, `.bat`, `.cmd`, `.scr`, `.vbs`, and `.js`.
- Added PE executable header detection alongside existing Mach-O detection.
- Added PowerShell launch and PyInstaller build helpers for Windows.
- Added a packaged-app fallback that opens the web panel if Tk cannot start.

## Cross-platform cleanup

- Generalized startup behavior labels so findings are not macOS-only.
- Preserved existing macOS LaunchAgent monitoring and DMG build flow.
- Added `requirements-dev.txt` for packaging dependencies.
