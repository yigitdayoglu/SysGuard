#!/bin/zsh
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -x "./.venv/bin/python" ]; then
  exec "./.venv/bin/python" main.py app
else
  exec python3 main.py app
fi
