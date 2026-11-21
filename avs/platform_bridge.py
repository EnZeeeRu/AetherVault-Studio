"""
avs/platform_bridge.py — Unified Cross-Platform OS Bridge (Windows / macOS / Linux).
Centralizes OS-specific paths, folder opening, media keys, and hidden shell execution.
"""
import os
import sys
import ctypes
import shutil
import subprocess
from pathlib import Path

IS_WINDOWS = (os.name == "nt")
IS_MAC = (sys.platform == "darwin")
IS_LINUX = sys.platform.startswith("linux")


def get_initial_pc_roots(base_dir: Path) -> list:
    """Auto-detects workspace, home, Steam, and cloud drive roots per OS."""
    home = Path.home()
    roots = [str(base_dir.resolve()), str(home)]
    if IS_WINDOWS:
        candidates = [
            Path("C:/Program Files (x86)/Steam/steamapps/common"),
            Path("D:/SteamLibrary/steamapps/common"),
            Path("E:/SteamLibrary/steamapps/common"),
            Path("G:/My Drive"),
            Path("G:/Mi unidad"),
            home / "Google Drive",
            home / "Desktop",
            home / "Documents",
        ]
    elif IS_MAC:
        candidates = [
            home / "Library/Application Support/Steam/steamapps/common",
            home / "Library/CloudStorage",
            home / "Desktop",
            home / "Documents",
        ]
    else:
        candidates = [
            home / ".local/share/Steam/steamapps/common",
            home / ".steam/steam/steamapps/common",
            home / "Desktop",
            home / "Documents",
        ]

    for p in candidates:
        try:
            if p.exists():
                roots.append(str(p.resolve()))
        except Exception:
            pass
    return list(dict.fromkeys(roots))


def open_path_or_uri(target: str) -> tuple:
    """Opens a local file, folder, or URI natively on Windows, macOS, or Linux."""
    t = str(target or "").strip()
    if not t:
        return False, "Empty target."
    try:
        if IS_WINDOWS and hasattr(os, "startfile"):
            os.startfile(t)
            return True, f"Opened '{t}' via Windows shell."
        if IS_MAC:
            subprocess.Popen(["open", t], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, f"Opened '{t}' via macOS open."
        subprocess.Popen(["xdg-open", t], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True, f"Opened '{t}' via xdg-open."
    except Exception as e:
        return False, f"Failed to open '{t}': {e}"


def send_media_key(action: str) -> bool:
    """Cross-platform media key helper (Windows VK_MEDIA, Linux playerctl, macOS AppleScript)."""
    act = (action or "").strip().lower()
    if IS_WINDOWS and hasattr(ctypes, "windll"):
        vk_map = {
            "pause": 0xB3, "play_pause": 0xB3, "resume": 0xB3,
            "next": 0xB0, "prev": 0xB1, "previous": 0xB1,
        }
        vk = vk_map.get(act)
        if not vk:
            return False
        try:
            ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
            ctypes.windll.user32.keybd_event(vk, 0, 2, 0)
            return True
        except Exception:
            return False

    if IS_LINUX and shutil.which("playerctl"):
        cmd_map = {
            "pause": "play-pause", "play_pause": "play-pause", "resume": "play-pause",
            "next": "next", "prev": "previous", "previous": "previous",
        }
        sub = cmd_map.get(act)
        if sub:
            try:
                subprocess.run(["playerctl", sub], timeout=3, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except Exception:
                return False

    if IS_MAC and shutil.which("osascript"):
        as_map = {
            "pause": "playpause", "play_pause": "playpause", "resume": "playpause",
            "next": "next track", "prev": "previous track", "previous": "previous track",
        }
        sub = as_map.get(act)
        if sub:
            try:
                subprocess.run(["osascript", "-e", f'tell application "Spotify" to {sub}'], timeout=3, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except Exception:
                return False

    return False


def run_hidden_shell(command: str, timeout: int = 15) -> dict:
    """Runs a silent background shell command using PowerShell on Windows or bash/sh on Unix."""
    cmd = (command or "").strip()
    if not cmd:
        return {"ok": False, "exit_code": -1, "output": "Empty shell command."}
    try:
        if IS_WINDOWS:
            ps_cmd = "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; $OutputEncoding = [System.Text.Encoding]::UTF8; " + cmd
            proc = subprocess.run(
                ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps_cmd],
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout
            )
        else:
            shell_bin = shutil.which("bash") or "/bin/sh"
            proc = subprocess.run(
                [shell_bin, "-c", cmd],
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout
            )
        out = ((proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")).strip()
        return {"ok": proc.returncode == 0, "exit_code": proc.returncode, "output": out[:4000]}
    except subprocess.TimeoutExpired:
        return {"ok": False, "exit_code": -1, "output": f"Shell command timed out after {timeout}s."}
    except Exception as e:
        return {"ok": False, "exit_code": -1, "output": f"Shell error: {e}"}
