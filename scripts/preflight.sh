#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "== Toolchain =="
for cmd in claude uv npx python3 curl; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "$cmd: $(command -v "$cmd")"
  else
    echo "$cmd: missing"
    exit 1
  fi
done

echo
echo "== Credentials =="
[ -n "${ANTHROPIC_API_KEY:-}" ] && echo "ANTHROPIC_API_KEY: present" || echo "ANTHROPIC_API_KEY: missing"
[ -n "${ZYTE_API_KEY:-}" ] && echo "ZYTE_API_KEY: present" || echo "ZYTE_API_KEY: missing"

if [ -z "${ZYTE_API_KEY:-}" ]; then
  echo "ZYTE_API_KEY is required for this Nike demo."
fi

echo
echo "== Claude plugins =="
claude plugin list | sed -n '1,120p'
if claude plugin list | grep -q "zyte-web-data@zyte-ai"; then
  echo "Zyte Web Data plugin: installed"
else
  echo "Zyte Web Data plugin: missing"
  echo "Run: ./scripts/install-zyte-plugin.sh"
fi

echo
echo "== Target feasibility =="
echo "Checking robots endpoint. Review disallowed paths before crawling."
set +e
ROBOTS="$(curl -L --max-time 20 https://www.nike.com/robots.txt 2>/dev/null)"
STATUS=$?
set -e

mkdir -p "$ROOT/outputs"
printf "%s\n" "$ROBOTS" > "$ROOT/outputs/robots-response.txt"

if [ "$STATUS" -ne 0 ]; then
  echo "robots.txt check failed with curl status $STATUS."
elif printf "%s" "$ROBOTS" | grep -qi "user-agent"; then
  echo "robots.txt returned a parseable robots file. Review outputs/robots-response.txt before crawling."
else
  echo "robots.txt returned unexpected content. Review outputs/robots-response.txt before crawling."
fi

echo
echo "Preflight complete."
