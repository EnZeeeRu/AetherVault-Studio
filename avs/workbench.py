"""
avs/workbench.py — Isolated, killable subprocess Python Workbench & dynamic `vault.py` RPC shim.
"""
import os
import re
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict

SAFE_AUTO_BLOCKED_PATTERNS = (
    (r"\b(?:os\.remove|os\.unlink|os\.rmdir|shutil\.rmtree|os\.system|subprocess\.)", "Destructive/shell calls are blocked in Safe Auto mode (switch Workbench Trust to Full PC to allow)."),
    (r"vault\.osworld\(\s*[\'\"](?:click|double_click|right_click|type|write|hotkey|key|press)[\'\"]", "Raw OSWorld mouse/keyboard control is blocked in Safe Auto mode."),
)


def write_dynamic_vault_shim(temp_dir: Path, port: int = 8000, token: str = "") -> Path:
    """Writes a session-scoped `vault.py` RPC client into `.temp_cache` pointing to the active backend port."""
    tdir = Path(temp_dir)
    tdir.mkdir(parents=True, exist_ok=True)
    shim_path = tdir / "vault.py"
    shim_lines = [
        '"""Session-scoped AetherVault Studio Workbench RPC shim (auto-generated)."""',
        "import json",
        "import urllib.request",
        "",
        f'_RPC_URL = "http://127.0.0.1:{int(port)}/workbench/rpc"',
        f"_TOKEN = {token!r}",
        "",
        "def _rpc(action: str, args: dict = None):",
        "    payload = json.dumps({'action': action, 'args': args or {}}).encode('utf-8')",
        "    req = urllib.request.Request(_RPC_URL, data=payload, headers={'Content-Type': 'application/json', 'X-Workbench-Token': _TOKEN}, method='POST')",
        "    with urllib.request.urlopen(req, timeout=30) as resp:",
        "        data = json.loads(resp.read().decode('utf-8', errors='replace'))",
        "    if not data.get('ok'):",
        "        raise RuntimeError(data.get('error') or f\"RPC '{action}' failed\")",
        "    return data.get('result')",
        "",
        "def weather(location='', latitude=None, longitude=None): return _rpc('weather', {'location': location, 'latitude': latitude, 'longitude': longitude})",
        "def web(query=''): return _rpc('web', {'query': query})",
        "def pc_info(): return _rpc('pc_info', {})",
        "def files(query=''): return _rpc('files', {'query': query})",
        "def spotify(action='current_track', query=''): return _rpc('spotify', {'action': action, 'query': query})",
        "def open_app(app=''): return _rpc('open_app', {'app': app})",
        "def osworld(action='list_windows', arg=''): return _rpc('osworld', {'action': action, 'arg': arg})",
        "def memory_save(category, fact): return _rpc('memory_save', {'category': category, 'fact': fact})",
        "def memory_list(): return _rpc('memory_list', {})",
        "def forget(target): return _rpc('memory_delete', {'target': target})",
        "def lore(keywords): return _rpc('lore', {'keywords': keywords})",
        "def profile(): return _rpc('profile', {})",
        "def write_file(path, content, append=False): return _rpc('write_file', {'path': path, 'content': content, 'append': append})",
        "def write_desktop(filename, content): return _rpc('write_file', {'path': f'Desktop/{filename}', 'content': content, 'append': False})",
        "def read_file(path): return _rpc('read_file', {'path': path})",
        "def browser(url='', private=False, search='', browser='auto'): return _rpc('browser', {'url': url, 'private': private, 'search': search, 'browser': browser})",
        "def run_cmd(command): return _rpc('run_cmd', {'command': command})",
        "def toggle(setting, value): return _rpc('toggle', {'setting': setting, 'value': value})",
        "def settings(): return _rpc('settings', {})",
        "def pip_list(): return _rpc('pip_list', {})",
        "def test_all(include_active=False): return _rpc('test_all', {'include_active': include_active})",
        "def test_step(tool_name): return _rpc('test_step', {'tool_name': tool_name})",
        "def generate_image(prompt): return _rpc('generate_image', {'prompt': prompt})",
        "def generate_music(prompt, duration=8): return _rpc('generate_music', {'prompt': prompt, 'duration': duration})",
    ]
    shim_path.write_text("\n".join(shim_lines) + "\n", encoding="utf-8", newline="\n")
    return shim_path


def run_workbench_subprocess(
    code_str: str,
    temp_dir: Path,
    port: int = 8000,
    token: str = "",
    timeout_sec: float = 20.0,
    trust_level: str = "safe_auto",
) -> Dict[str, object]:
    """Runs Python code in an isolated, killable child subprocess with `vault` pre-available on sys.path."""
    clean_code = (code_str or "").strip()
    if not clean_code:
        return {"ok": False, "exit_code": -1, "elapsed_sec": 0.0, "output": "Empty code block."}

    if (trust_level or "safe_auto").strip().lower() != "full_pc":
        for pat, msg in SAFE_AUTO_BLOCKED_PATTERNS:
            if re.search(pat, clean_code):
                return {"ok": False, "exit_code": -1, "elapsed_sec": 0.0, "output": f"[Safe Auto Gate] {msg}"}

    tdir = Path(temp_dir)
    tdir.mkdir(parents=True, exist_ok=True)
    write_dynamic_vault_shim(tdir, port=port, token=token)

    script_path = tdir / f"wb_sub_{int(time.time() * 1000)}_{os.getpid()}.py"
    preamble = (
        "import os, re, json, math, time\n"
        "from pathlib import Path\n"
        "import vault\n\n"
    )
    script_path.write_text(preamble + clean_code + "\n", encoding="utf-8", newline="\n")

    env = os.environ.copy()
    prev_pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{str(tdir.resolve())}{os.pathsep}{prev_pp}" if prev_pp else str(tdir.resolve())
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            [sys.executable, "-u", str(script_path)],
            cwd=str(tdir),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=max(1.0, min(60.0, float(timeout_sec))),
        )
        elapsed = round(time.perf_counter() - t0, 2)
        out = (proc.stdout or "").strip() or "(Executed cleanly with no stdout output)"
        return {
            "ok": proc.returncode == 0,
            "exit_code": int(proc.returncode),
            "elapsed_sec": elapsed,
            "output": out[:8000],
        }
    except subprocess.TimeoutExpired:
        elapsed = round(time.perf_counter() - t0, 2)
        return {
            "ok": False,
            "exit_code": -1,
            "elapsed_sec": elapsed,
            "output": f"Subprocess timed out and was killed after {timeout_sec:.0f}s.",
        }
    except Exception as e:
        elapsed = round(time.perf_counter() - t0, 2)
        return {
            "ok": False,
            "exit_code": -1,
            "elapsed_sec": elapsed,
            "output": f"{type(e).__name__}: {e}",
        }
    finally:
        try:
            script_path.unlink(missing_ok=True)
        except Exception:
            pass
