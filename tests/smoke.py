#!/usr/bin/env python3
"""
tests/smoke.py — Automated Smoke Test Suite for AetherVault Studio v4.20.
Verifies static syntax, encoding, launchers, avs/ core modules, killable subprocess
Workbench, golden_* snapshot sync, dynamic AVS_PORT parity, and UI/SVG integrity.
"""
import os
import sys
import ast
import time
import shutil
import tempfile
import py_compile
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def test_python_syntax():
    py_files = [
        ROOT / "assistant_server.py",
        ROOT / "manager.py",
        ROOT / "avs" / "__init__.py",
        ROOT / "avs" / "platform_bridge.py",
        ROOT / "avs" / "toolbox.py",
        ROOT / "avs" / "workbench.py",
        ROOT / "tests" / "smoke.py",
    ]
    for f in py_files:
        assert f.exists(), f"Missing {f}"
        py_compile.compile(str(f), doraise=True)
        ast.parse(f.read_text(encoding="utf-8"))
    print("  [PASS] Python syntax & AST (all 7 files)")


def test_launchers_and_ascii():
    sh_p = ROOT / "Launch.sh"
    sh_b = sh_p.read_bytes()
    assert b"\r\n" not in sh_b, "CRLF found in Launch.sh"
    if shutil.which("bash"):
        assert subprocess.run(["bash", "-n", str(sh_p)], capture_output=True, text=True).returncode == 0
    if shutil.which("sh"):
        assert subprocess.run(["sh", "-n", str(sh_p)], capture_output=True, text=True).returncode == 0

    bat_b = (ROOT / "Launch.bat").read_bytes()
    assert all(b <= 127 for b in bat_b), "Non-ASCII in Launch.bat"
    assert b"manager.py" in bat_b

    ps1_b = (ROOT / "Manager.ps1").read_bytes()
    assert all(b <= 127 for b in ps1_b), "Non-ASCII in Manager.ps1"
    ps1_s = ps1_b.decode("ascii")
    assert "Select model (0-10)" in ps1_s and "Gemma-4-26B-A4B-it" in ps1_s
    print("  [PASS] Launch.sh (LF/bash/sh), Launch.bat & Manager.ps1 (7-bit ASCII)")


def test_ui_svg_and_manual():
    ui_s = (ROOT / "ui_studio.html").read_text(encoding="utf-8")
    assert ui_s.count("<script") == ui_s.count("</script>")
    for needle in ('id="cfg-mcp-url"', 'id="cfg-mcp-token"', 'function testMcpHandshake()', 'function generateMcpToken()'):
        assert needle in ui_s, f"Missing {needle} in ui_studio.html"
    ET.fromstring((ROOT / "aethervault_logo.svg").read_text(encoding="utf-8"))
    pdf_b = (ROOT / "AetherVault_Studio_Manual.pdf").read_bytes()
    assert pdf_b.startswith(b"%PDF-") and b"%%EOF" in pdf_b
    print("  [PASS] ui_studio.html (/mcp card), aethervault_logo.svg & Manual PDF")


def test_avs_core_and_workbench():
    from avs import platform_bridge, toolbox as tb_mod, workbench as wb_mod

    roots = platform_bridge.get_initial_pc_roots(ROOT)
    assert str(ROOT.resolve()) in roots
    sh_res = platform_bridge.run_hidden_shell("echo AVS_SMOKE_SHELL", timeout=5)
    assert sh_res["ok"] and "AVS_SMOKE_SHELL" in sh_res["output"]

    reg = tb_mod.ToolRegistry()

    @reg.register("ping_tool", description="Ping test.", aliases=["pong"], mcp_exposed=True)
    def _ping(val: str = "ok"):
        return f"PONG:{val}"

    @reg.register("restricted_tool", description="Full PC test.", trust="full_pc")
    def _restricted():
        return "UNLOCKED"

    r1 = reg.call("pong", {"val": "42"})
    assert r1.ok and r1.summary == "PONG:42"
    r2 = reg.call("restricted_tool", trust_level="safe_auto")
    assert (not r2.ok) and "Safety Gate" in (r2.error or "")
    assert len(reg.mcp_tools()) == 1

    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        ok_r = wb_mod.run_workbench_subprocess("print(6 * 7)", temp_dir=tdp, port=8765, token="t1", timeout_sec=5.0)
        assert ok_r["ok"] and "42" in ok_r["output"]
        assert "127.0.0.1:8765/workbench/rpc" in (tdp / "vault.py").read_text(encoding="utf-8")

        kill_r = wb_mod.run_workbench_subprocess("while True:\n    pass", temp_dir=tdp, port=8765, timeout_sec=1.0)
        assert (not kill_r["ok"]) and kill_r["timed_out"] and kill_r["exit_code"] == -9

        gate_r = wb_mod.run_workbench_subprocess("import os; os.remove('x')", temp_dir=tdp, trust_level="safe_auto")
        assert (not gate_r["ok"]) and "Safety Gate" in gate_r["output"]
    print("  [PASS] avs/platform_bridge, avs/toolbox & avs/workbench (1s hard kill + dynamic port)")


def test_manager_port_and_golden_sync():
    with tempfile.TemporaryDirectory() as td:
        sb = Path(td)
        for fn in ("Launch.sh", "manager.py", "ui_studio.html"):
            shutil.copy2(ROOT / fn, sb / fn)
        (sb / "assistant_server.py").write_text("print('OLD')\n", encoding="utf-8")
        gdir = sb / "workspace_backups" / "golden_20261120_150000"
        gdir.mkdir(parents=True)
        gf = gdir / "assistant_server.py"
        gf.write_text("print('SMOKE_GOLDEN_OK')\n", encoding="utf-8")
        os.utime(gf, (time.time() + 10, time.time() + 10))

        env = dict(**os.environ, AVS_PORT="8765")
        cmd = [sys.executable, str(sb / "manager.py"), "--cli"]
        r = subprocess.run(cmd, input="0\n", text=True, capture_output=True, env=env, timeout=10)
        assert r.returncode == 0, r.stderr
        assert "http://127.0.0.1:8765" in r.stdout
        assert "SMOKE_GOLDEN_OK" in (sb / "assistant_server.py").read_text(encoding="utf-8")
        assert not (sb / ".temp_cache").exists()
    print("  [PASS] manager.py (AVS_PORT=8765 + golden_* sync + .temp_cache cleanup)")




def test_port_conflict_recovery_and_custom_dl():
    import socket
    import manager as mgr_mod

    # Bind an ephemeral port to simulate a port conflict and confirm auto-bump!
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        s.listen(1)
        busy_port = s.getsockname()[1]
        assert mgr_mod.is_port_in_use(busy_port) is True
        bumped = mgr_mod.find_available_port(busy_port, max_tries=10)
        assert bumped > busy_port and not mgr_mod.is_port_in_use(bumped)

    mgr_s = (ROOT / "manager.py").read_text(encoding="utf-8")
    assert "Custom Hugging Face Repo" in mgr_s
    assert "Stock Offline Vault" in mgr_s
    assert "launch_desktop_gui" in mgr_s
    assert "Python.Python.3.11" in (ROOT / "Launch.bat").read_text(encoding="ascii")
    assert "find_python()" in (ROOT / "Launch.sh").read_text(encoding="utf-8")
    assert "Run Automated Smoke Suite (tests/smoke.py)" in mgr_s
    assert "exportCurrentChatMd()" in (ROOT / "ui_studio.html").read_text(encoding="utf-8")
    assert "/session/{session_id}/export_md" in (ROOT / "assistant_server.py").read_text(encoding="utf-8")
    assert "def run_isolated(" in (ROOT / "assistant_server.py").read_text(encoding="utf-8")
    print("  [PASS] QoL Gauntlet: port-conflict auto-recovery, custom HF menu, Export .MD & vault.run_isolated")


def main():
    print("=== AetherVault Studio v4.20 Automated Smoke Suite ===")
    test_python_syntax()
    test_launchers_and_ascii()
    test_ui_svg_and_manual()
    test_avs_core_and_workbench()
    test_manager_port_and_golden_sync()
    test_port_conflict_recovery_and_custom_dl()
    print("=== ALL SMOKE TESTS PASSED! ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
