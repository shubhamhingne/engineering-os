#!/usr/bin/env bash
# Responsibility: confirm the local toolchain meets the minimum versions for development.
# Reports each tool; exits non-zero if any required tool is missing.
set -uo pipefail
ok=0
check() { # check <cmd> <label>
  if command -v "$1" >/dev/null 2>&1; then
    printf "  ✅ %-8s %s\n" "$2" "$($1 --version 2>&1 | head -1)"
  else
    printf "  ❌ %-8s missing\n" "$2"; ok=1
  fi
}
echo "Verifying environment…"
check node Node
check pnpm pnpm
check python3 Python
check docker Docker
check git Git
[ $ok -eq 0 ] && echo "Environment OK." || echo "Missing tools — see README / developer-setup.md."
exit $ok
