#!/bin/zsh
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP_NAME="SysGuard"
VERSION="7.4"
APP_PATH="$PROJECT_ROOT/${APP_NAME}.app"
RELEASE_DIR="$PROJECT_ROOT/release"
STAGE_DIR="$RELEASE_DIR/dmg-stage"
DMG_NAME="${APP_NAME}-${VERSION}-macOS.dmg"
TEMP_DMG="$RELEASE_DIR/${APP_NAME}-${VERSION}-temp.dmg"
FINAL_DMG="$RELEASE_DIR/$DMG_NAME"
VOLUME_NAME="Install ${APP_NAME}"
BACKGROUND_DIR="$STAGE_DIR/.background"
BACKGROUND_FILE="$BACKGROUND_DIR/background.png"
README_FILE="$STAGE_DIR/Install SysGuard.txt"

mkdir -p "$RELEASE_DIR" "$BACKGROUND_DIR"
rm -rf "$STAGE_DIR"
mkdir -p "$BACKGROUND_DIR"
rm -f "$TEMP_DMG" "$FINAL_DMG"

if [ ! -d "$APP_PATH" ]; then
  echo "Missing app bundle: $APP_PATH"
  exit 1
fi

cp -R "$APP_PATH" "$STAGE_DIR/"
cp "$PROJECT_ROOT/assets/dmg-background.png" "$BACKGROUND_FILE"
ln -s /Applications "$STAGE_DIR/Applications"

cat > "$README_FILE" <<EOF
SysGuard installation

1. Drag SysGuard.app into Applications.
2. Open SysGuard from Applications.
3. If macOS asks for permission, allow the security and file access prompts.

Storage location:
$HOME/Library/Application Support/SysGuard
EOF

hdiutil create \
  -volname "$VOLUME_NAME" \
  -srcfolder "$STAGE_DIR" \
  -ov \
  -format UDRW \
  "$TEMP_DMG" >/dev/null

hdiutil convert "$TEMP_DMG" -format UDZO -imagekey zlib-level=9 -ov -o "$FINAL_DMG" >/dev/null
rm -f "$TEMP_DMG"
rm -rf "$STAGE_DIR"

echo "Built DMG at: $FINAL_DMG"
