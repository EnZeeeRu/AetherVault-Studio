"""
avs/workbench.py — Killable Subprocess Python Workbench.
Runs user/AI Python snippets in an isolated child process using sys.executable so:
  - Infinite loops or hung C extensions are cleanly killed on timeout (no zombie threads).
  - Active server port is passed dynamically (never hardcoded to 8000).
  - Structured JSON output & error details are returned cleanly.
"""
import os
import re
import sys
import json
import time
import subprocess
from pathlib import Path


def sanitize_workbench_code(raw_code: str) -> str:
    """Repairs common small-model Python formatting quirks before execution."""
    s = (raw_code or "").strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z0-9_-]*\s*\n?", "", s)
        s = re.sub(r"\n?```\s*$", "", s).strip()
    cleaned = []
    for ln in s.splitlines():
        ln_s = ln.rstrip()
        if ln_s.lstrip().startswith(">>> "):
            ln_s = ln_s.replace(">>> ", "", 1)
        elif ln_s.lstrip().startswith("... "):
            ln_s = ln_s.replace("... ", "", 1)
        cleaned.append(ln_s)
    s = "\n".join(cleaned).strip()
    if s.count("(") == s.count(")") + 1 and "\n" not in s:
        s += ")"
    if s.count("[") == s.count("]") + 1 and "\n" not in s:
        s += "]"
    return s


def write_dynamic_vault_shim(temp_dir: Path, port: int, token: str) -> Path:
    """Writes a lightweight vault.py RPC client inside temp_dir pointing to the active server port."""
    temp_dir.mkdir(parents=True, exist_ok=True)
    shim_path = temp_dir / "vault.py"
    shim_lines = [
        "import json, urllib.request",
        f'_RPC_URL = "http://127.0.0.1:{int(port)}/workbench/rpc"',
        f"_TOKEN = {token!r}",
        "def _call(action, **kwargs):",
        '    data = json.dumps({"action": action, "args": kwargs}).encode("utf-8")',
        '    req = urllib.request.Request(_RPC_URL, data=data, headers={"Content-Type": "application/json", "X-Workbench-Token": _TOKEN}, method="POST")',
        "    with urllib.request.urlopen(req, timeout=25) as resp:",
        '        res = json.loads(resp.read().decode("utf-8"))',
        '        if not res.get("ok"): raise RuntimeError(res.get("error") or "Workbench RPC error")',
        '        return res.get("result")',
        "class _VaultProxy:",
        "    def __getattr__(self, name):",
        "        def _fn(*args, **kwargs):",
        '            if args and not kwargs: kwargs = {"query": args[0]} if len(args) == 1 else {"args": list(args)}',
        "            return _call(name, **kwargs)",
        "        return _fn",
        "_proxy = _VaultProxy()",
        "def __getattr__(name): return getattr(_proxy, name)",
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
    max_output_chars: int = 10000,
) -> dict:
    """
    Executes Python code in a killable child process.
    Returns: {ok, elapsed_sec, output, timed_out, exit_code}
    """
    clean_code = sanitize_workbench_code(code_str)
    if not clean_code:
        return {"ok": False, "elapsed_sec": 0.0, "output": "Empty workbench block.", "timed_out": False, "exit_code": -1}

    if trust_level != "full_pc":
        blocked = [
            (r"\b(?:os\.remove|os\.unlink|os\.rmdir|shutil\.rmtree|os\.system|subprocess\.)", "Destructive/shell calls blocked in safe_auto mode."),
        ]
        for pat, msg in blocked:
            if re.search(pat, clean_code):
                return {"ok": False, "elapsed_sec": 0.0, "output": f"Safety Gate: {msg}", "timed_out": False, "exit_code": -1}

    write_dynamic_vault_shim(temp_dir, port=port, token=token)
    script_path = temp_dir / f"wb_job_{int(time.time() * 1000)}.py"
    wrapped = (
        "import os, re, sys, json, math, time\n"
        "from pathlib import Path\n"
        "sys.path.insert(0, str(Path(__file__).parent))\n"
        "import vault\n\n"
        + clean_code
        + "\n"
    )
    script_path.write_text(wrapped, encoding="utf-8", newline="\n")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(temp_dir) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    env["PYTHONUNBUFFERED"] = "1"

    t0 = time.perf_counter()
    proc = subprocess.Popen(
        [sys.executable, "-I", str(script_path)],
        cwd=str(temp_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout_sec)
        elapsed = round(time.perf_counter() - t0, 2)
        combined = ((stdout or "") + ("\n" + stderr if stderr else "")).strip()
        if len(combined) > max_output_chars:
            combined = combined[:max_output_chars] + f"\n... [truncated at {max_output_chars:,} chars]"
        return {
            "ok": proc.returncode == 0,
            "elapsed_sec": elapsed,
            "output": combined or "(Executed cleanly with no stdout output)",
            "timed_out": False,
            "exit_code": proc.returncode,
        }
    except subprocess.TimeoutExpired:
        proc.kill()
        try:
            proc.communicate(timeout=2)
        except Exception:
            pass
        elapsed = round(time.perf_counter() - t0, 2)
        return {
            "ok": False,
            "elapsed_sec": elapsed,
            "output": f"Workbench subprocess killed cleanly after {timeout_sec:.1f}s timeout.",
            "timed_out": True,
            "exit_code": -9,
        }
    finally:
        try:
            if script_path.exists():
                script_path.unlink()
        except Exception:
            pass
