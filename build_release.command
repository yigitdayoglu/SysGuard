#!/bin/zsh
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

cd "$PROJECT_ROOT"
./scripts/build_app_bundle.sh
./scripts/build_dmg.sh
open "$PROJECT_ROOT/release"
