#!/usr/bin/env bash
# Responsibility: top-level entry point — bootstrap a clone for a new contributor.
# Orchestrates environment verification, dev setup, and doc validation.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
echo "Bootstrapping Engineering OS…"
bash "$ROOT/tooling/scripts/setup-dev.sh"
echo "Done. See docs/10-testing/developer-setup.md to run the apps."
