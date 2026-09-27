#!/usr/bin/env bash
# Installs the render stack in a fresh Ubuntu cloud session. Safe to re-run.
# Usage: setup_cloud.sh [apt|python|node|all]   (steps are split so each fits a 10-minute command limit)
set -euo pipefail
cd "$(dirname "$0")/.."
STEP="${1:-all}"

install_apt() {
  export DEBIAN_FRONTEND=noninteractive
  local sudo=""; [ "$(id -u)" -ne 0 ] && sudo="sudo"
  $sudo apt-get update -qq || true
  $sudo apt-get install -y -qq --no-install-recommends \
    ffmpeg libcairo2-dev libpango1.0-dev pkg-config python3-dev python3-venv build-essential \
    texlive-latex-base texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended \
    texlive-science cm-super dvisvgm >/dev/null
  latex --version | head -1
  ffmpeg -version | head -1
}

install_python() {
  [ -d .venv ] || python3 -m venv .venv
  .venv/bin/pip install -q --upgrade pip
  .venv/bin/pip install -q -r requirements.txt
  .venv/bin/python -c "import manim; print('manim', manim.__version__)"
}

install_node() {
  (cd site && npm ci --no-audit --no-fund --loglevel=error)
  echo "site dependencies installed"
}

case "$STEP" in
  apt) install_apt ;;
  python) install_python ;;
  node) install_node ;;
  all) install_apt; install_python; install_node ;;
  *) echo "unknown step: $STEP" >&2; exit 2 ;;
esac
