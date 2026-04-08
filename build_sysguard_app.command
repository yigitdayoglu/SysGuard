#!/bin/zsh
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

cd "$PROJECT_ROOT"
./scripts/build_app_bundle.sh
open "$PROJECT_ROOT/SysGuard.app"
