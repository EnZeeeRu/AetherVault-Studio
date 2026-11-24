"""
avs/platform_bridge.py — Cross-platform OS bridge for AetherVault Studio.
Supports Windows, macOS, and Linux with safe fallbacks and zero hard crashes.
"""
import os
import sys
import ctypes
import shutil
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

IS_WINDOWS = (os.name == "nt")
IS_MAC = (sys.platform == "darwin")
IS_LINUX = sys.platform.startswith("linux")


def get_initial_pc_roots(base_dir: Path) -> List[str]:
    """Returns sensible default local directories to allow file scanning."""
    roots: List[str] = []
    home = Path.home()
    candidates = [
        Path(base_dir).resolve(),
        home / "Desktop",
        home / "Documents",
        home / "Downloads",
    ]
    if IS_WINDOWS:
        for drv in ("G:/My Drive", "H:/My Drive", "C:/Program Files (x86)/Steam/steamapps/common", "D:/SteamLibrary/steamapps/common"):
            candidates.append(Path(drv))
    for p in candidates:
        try:
            if p.exists():
                s = str(p.resolve())
                if s not in roots:
                    roots.append(s)
        except Exception:
            pass
    return roots or [str(Path(base_dir).resolve())]


def run_hidden_shell(command: str, timeout: float = 15.0) -> Dict[str, object]:
    """Executes a background shell command without flashing a terminal window on Windows."""
    cmd = (command or "").strip()
    if not cmd:
        return {"ok": False, "exit_code": -1, "output": "Empty command."}
    try:
        kwargs = {
            "stdout": subprocess.PIPE,
            "stderr": subprocess.STDOUT,
            "text": True,
            "encoding": "utf-8",
            "errors": "replace",
            "timeout": max(1.0, float(timeout)),
        }
        if IS_WINDOWS:
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            kwargs["startupinfo"] = si
            kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
            args = ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", cmd]
        else:
            shell_bin = shutil.which("bash") or shutil.which("sh") or "/bin/sh"
            args = [shell_bin, "-c", cmd]
        proc = subprocess.run(args, **kwargs)
        return {
            "ok": proc.returncode == 0,
            "exit_code": int(proc.returncode),
            "output": (proc.stdout or "").strip(),
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "exit_code": -1, "output": f"Command timed out after {timeout}s."}
    except Exception as e:
        return {"ok": False, "exit_code": -1, "output": f"{type(e).__name__}: {e}"}


def send_media_key(action: str) -> bool:
    """Sends a cross-platform hardware/OS media key (play_pause, pause, resume, next, prev)."""
    act = (action or "").strip().lower()
    if IS_WINDOWS and hasattr(ctypes, "windll"):
        vk_map = {
            "play_pause": 0xB3,
            "pause": 0xB3,
            "resume": 0xB3,
            "play": 0xB3,
            "next": 0xB0,
            "prev": 0xB1,
            "previous": 0xB1,
            "stop": 0xB2,
        }
        vk = vk_map.get(act)
        if not vk:
            return False
        try:
            ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
            ctypes.windll.user32.keybd_event(vk, 0, 0x0002, 0)
            return True
        except Exception:
            return False

    if IS_MAC:
        script_map = {
            "play_pause": 'tell application "Spotify" to playpause',
            "pause": 'tell application "Spotify" to pause',
            "resume": 'tell application "Spotify" to play',
            "next": 'tell application "Spotify" to next track',
            "prev": 'tell application "Spotify" to previous track',
            "previous": 'tell application "Spotify" to previous track',
        }
        sc = script_map.get(act)
        if sc and shutil.which("osascript"):
            try:
                r = subprocess.run(["osascript", "-e", sc], capture_output=True, timeout=4)
                return r.returncode == 0
            except Exception:
                return False
        return False

    if IS_LINUX and shutil.which("playerctl"):
        p_map = {
            "play_pause": "play-pause",
            "pause": "pause",
            "resume": "play",
            "next": "next",
            "prev": "previous",
            "previous": "previous",
        }
        arg = p_map.get(act)
        if arg:
            try:
                r = subprocess.run(["playerctl", arg], capture_output=True, timeout=4)
                return r.returncode == 0
            except Exception:
                return False
    return False


def open_path_or_uri(target: str) -> Tuple[bool, str]:
    """Opens a local folder, file, or URI using the host OS default handler."""
    raw = (target or "").strip()
    if not raw:
        return False, "Empty path or URI."
    try:
        if IS_WINDOWS and hasattr(os, "startfile"):
            os.startfile(raw)
            return True, f"Opened '{raw}'."
        if IS_MAC:
            subprocess.Popen(["open", raw], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, f"Opened '{raw}'."
        opener = shutil.which("xdg-open")
        if opener:
            subprocess.Popen([opener, raw], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, f"Opened '{raw}'."
        return False, f"No OS file opener found on {platform.system()}."
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"
