#!/usr/bin/env bash
# Installs the render stack in a fresh Ubuntu cloud session. Safe to re-run.
set -euo pipefail
cd "$(dirname "$0")/.."

export DEBIAN_FRONTEND=noninteractive
SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"
$SUDO apt-get update -qq
$SUDO apt-get install -y -qq --no-install-recommends \
  ffmpeg libcairo2-dev libpango1.0-dev pkg-config python3-dev python3-venv build-essential \
  texlive-latex-base texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended \
  texlive-science cm-super dvisvgm >/dev/null

[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -r requirements.txt

(cd site && npm ci --no-audit --no-fund --loglevel=error)

.venv/bin/python -c "import manim; print('manim', manim.__version__)"
latex --version | head -1
ffmpeg -version | head -1
