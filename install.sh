#!/usr/bin/env bash
# Job Search OS — Installer
# Usage: bash install.sh

set -e

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RESET="\033[0m"

echo ""
echo -e "${BOLD}Job Search OS${RESET} — installer"
echo "─────────────────────────────────"

# ── Check Python ──────────────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
  echo "Error: python3 not found. Install Python 3.10+ first."
  exit 1
fi

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
  echo "Error: Python 3.10+ required (found $PY_VERSION)."
  exit 1
fi

echo -e "${GREEN}✓${RESET} Python $PY_VERSION"

# ── Install via pipx (preferred) or pip ───────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v pipx &>/dev/null; then
  echo -e "${GREEN}✓${RESET} pipx found — installing globally"
  pipx install "$SCRIPT_DIR" --force
  INSTALLED_VIA="pipx"
else
  echo -e "${YELLOW}→${RESET} pipx not found — installing into a local venv"
  cd "$SCRIPT_DIR"
  python3 -m venv .venv
  .venv/bin/pip install -e . -q
  INSTALLED_VIA="venv"
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}✓ Installed!${RESET}"
echo ""

if [ "$INSTALLED_VIA" = "pipx" ]; then
  echo -e "${BOLD}Quickstart:${RESET}"
  echo "  jsos init ~/my-job-search    # scaffold a new workspace"
  echo "  cd ~/my-job-search"
  echo "  jsos scrape --stage series-a"
  echo "  jsos score  --stage series-a"
  echo "  jsos list"
else
  echo -e "${BOLD}Quickstart:${RESET}"
  echo "  source $SCRIPT_DIR/.venv/bin/activate"
  echo "  jsos init ~/my-job-search    # scaffold a new workspace"
  echo "  cd ~/my-job-search"
  echo "  jsos scrape --stage series-a"
  echo "  jsos score  --stage series-a"
  echo "  jsos list"
  echo ""
  echo -e "${YELLOW}Tip:${RESET} install pipx for a system-wide install:"
  echo "  brew install pipx   # macOS"
  echo "  pip install pipx    # other"
  echo "  Then re-run: bash install.sh"
fi
echo ""
