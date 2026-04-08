#!/bin/zsh
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP_NAME="SysGuard"
DIST_APP="$PROJECT_ROOT/dist/${APP_NAME}.app"
ROOT_APP="$PROJECT_ROOT/${APP_NAME}.app"
ICON_FILE="$PROJECT_ROOT/assets/SysGuard.icns"
export PYINSTALLER_CONFIG_DIR="$PROJECT_ROOT/.pyinstaller"

cd "$PROJECT_ROOT"

rm -rf "$PROJECT_ROOT/build" "$PROJECT_ROOT/dist" "$PROJECT_ROOT/.pyinstaller" "$ROOT_APP"
./.venv/bin/python scripts/generate_visual_assets.py

./.venv/bin/python -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name "$APP_NAME" \
  --icon "$ICON_FILE" \
  --osx-bundle-identifier "com.yigitdayoglu.sysguard" \
  --hidden-import "tkinter" \
  --hidden-import "psutil" \
  --hidden-import "watchdog" \
  --hidden-import "watchdog.observers.fsevents" \
  --hidden-import "watchdog.observers.kqueue" \
  --hidden-import "watchdog.observers.polling" \
  --paths "$PROJECT_ROOT" \
  app_entry.py

/usr/libexec/PlistBuddy -c 'Set :CFBundleDisplayName SysGuard' "$DIST_APP/Contents/Info.plist" >/dev/null 2>&1 || \
  /usr/libexec/PlistBuddy -c 'Add :CFBundleDisplayName string SysGuard' "$DIST_APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c 'Set :CFBundleShortVersionString 7.4' "$DIST_APP/Contents/Info.plist" >/dev/null 2>&1 || \
  /usr/libexec/PlistBuddy -c 'Add :CFBundleShortVersionString string 7.4' "$DIST_APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c 'Set :CFBundleVersion 7.4' "$DIST_APP/Contents/Info.plist" >/dev/null 2>&1 || \
  /usr/libexec/PlistBuddy -c 'Add :CFBundleVersion string 7.4' "$DIST_APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c 'Set :LSApplicationCategoryType public.app-category.utilities' "$DIST_APP/Contents/Info.plist" >/dev/null 2>&1 || \
  /usr/libexec/PlistBuddy -c 'Add :LSApplicationCategoryType string public.app-category.utilities' "$DIST_APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c 'Set :LSMinimumSystemVersion 13.0' "$DIST_APP/Contents/Info.plist" >/dev/null 2>&1 || \
  /usr/libexec/PlistBuddy -c 'Add :LSMinimumSystemVersion string 13.0' "$DIST_APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c 'Set :NSHighResolutionCapable true' "$DIST_APP/Contents/Info.plist" >/dev/null 2>&1 || \
  /usr/libexec/PlistBuddy -c 'Add :NSHighResolutionCapable bool true' "$DIST_APP/Contents/Info.plist"

codesign --force --deep --sign - "$DIST_APP"
codesign --verify --deep --strict "$DIST_APP"

ditto "$DIST_APP" "$ROOT_APP"

echo "Built native app bundle at: $ROOT_APP"
