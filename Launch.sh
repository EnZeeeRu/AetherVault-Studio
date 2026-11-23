#!/usr/bin/env bash
# AetherVault Studio — Permanent Cross-Platform Bootstrapper (macOS / Linux)
set -u
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

find_python() {
    if [ -x "$ROOT_DIR/.venv/bin/python" ]; then
        PY_CMD="$ROOT_DIR/.venv/bin/python"
        return 0
    fi
    for cand in python3.12 python3.11 python3.10 python3 python; do
        if command -v "$cand" >/dev/null 2>&1; then
            if "$cand" -c "import sys; assert sys.version_info >= (3, 10)" >/dev/null 2>&1; then
                PY_CMD="$(command -v "$cand")"
                return 0
            fi
        fi
    done
    return 1
}

PY_CMD=""
if ! find_python; then
    echo "======================================================================="
    echo " [AETHERVAULT STUDIO BOOTSTRAPPER] Python 3.10+ was not found."
    echo "======================================================================="
    INSTALL_CMD=""
    if command -v brew >/dev/null 2>&1; then
        INSTALL_CMD="brew install python@3.11"
    elif command -v apt-get >/dev/null 2>&1; then
        INSTALL_CMD="sudo apt-get update && sudo apt-get install -y python3 python3-venv python3-pip"
    elif command -v dnf >/dev/null 2>&1; then
        INSTALL_CMD="sudo dnf install -y python3 python3-pip"
    elif command -v pacman >/dev/null 2>&1; then
        INSTALL_CMD="sudo pacman -Sy --noconfirm python python-pip"
    elif command -v zypper >/dev/null 2>&1; then
        INSTALL_CMD="sudo zypper install -y python3 python3-pip"
    fi

    if [ -n "$INSTALL_CMD" ] && [ -t 0 ]; then
        printf "Install Python now via '%s'? (y/N): " "$INSTALL_CMD"
        read -r ans
        if [ "$ans" = "y" ] || [ "$ans" = "Y" ]; then
            sh -c "$INSTALL_CMD"
            find_python
        fi
    elif [ -n "$INSTALL_CMD" ]; then
        echo "[HINT] Install Python 3.10+ using: $INSTALL_CMD"
    fi

    if [ -z "$PY_CMD" ]; then
        echo "[ERROR] Python 3.10+ is required. Please install it and re-run ./Launch.sh"
        exit 1
    fi
fi

exec "$PY_CMD" "$ROOT_DIR/manager.py" "$@"
