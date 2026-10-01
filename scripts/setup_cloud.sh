#!/usr/bin/env bash
# Session start in Claude Code on the web: make sure ffmpeg exists for assemble.py.
# Idempotent and silent when everything is already in place. Never touches a local laptop:
# it only does anything inside a Linux container.
set -u

have_ffmpeg() { command -v ffmpeg >/dev/null 2>&1 || [ -x "$HOME/.local/bin/ffmpeg" ]; }
add_path() {
  # Persist PATH for the rest of the session when the harness offers an env file.
  if [ -n "${CLAUDE_ENV_FILE:-}" ]; then echo "export PATH=\"$HOME/.local/bin:\$PATH\"" >> "$CLAUDE_ENV_FILE"; fi
}

[ "$(uname -s)" = "Linux" ] || exit 0
if have_ffmpeg; then
  [ -x "$HOME/.local/bin/ffmpeg" ] && add_path
  exit 0
fi

# 1) apt, the full ffmpeg with drawtext for cards and captions
if command -v apt-get >/dev/null 2>&1; then
  SUDO=""
  if [ "$(id -u)" -ne 0 ] && command -v sudo >/dev/null 2>&1; then SUDO="sudo -n"; fi
  if $SUDO apt-get update -qq >/dev/null 2>&1 && \
     DEBIAN_FRONTEND=noninteractive $SUDO apt-get install -y -qq ffmpeg fonts-dejavu-core >/dev/null 2>&1; then
    echo "video-lab: ffmpeg installed (apt)"
    exit 0
  fi
fi

# 2) a static ffmpeg from PyPI (no drawtext guaranteed: cards fall back to their placeholders)
PIP="python3 -m pip install -q --user imageio-ffmpeg"
if $PIP >/dev/null 2>&1 || $PIP --break-system-packages >/dev/null 2>&1; then
  BIN=$(python3 -c 'import imageio_ffmpeg as i; print(i.get_ffmpeg_exe())' 2>/dev/null)
  if [ -n "$BIN" ]; then
    mkdir -p "$HOME/.local/bin" && ln -sf "$BIN" "$HOME/.local/bin/ffmpeg"
    add_path
    echo "video-lab: ffmpeg installed (imageio-ffmpeg)"
    exit 0
  fi
fi

echo "video-lab: could not install ffmpeg. Generation works; previews need ffmpeg. Tell a facilitator."
exit 0
