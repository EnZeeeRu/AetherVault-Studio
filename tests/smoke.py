#!/usr/bin/env python3
"""
tests/smoke.py — Automated integrity & unit smoke suite for AetherVault Studio.
Runs with 100% Python standard library (zero external server needed).
"""
import ast
import hashlib
import json
import py_compile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main() -> int:
    print("=== AetherVault Studio Automated Smoke Suite ===")

    # 1. Compile & AST-parse every Python file in root and avs/
    py_files = [ROOT / "manager.py", ROOT / "assistant_server.py"] + sorted((ROOT / "avs").glob("*.py"))
    for pf in py_files:
        assert pf.exists(), f"Missing required Python file: {pf}"
        py_compile.compile(str(pf), doraise=True)
        ast.parse(pf.read_text(encoding="utf-8"))
    print(f"[PASS 1/7] Syntax & AST check passed for {len(py_files)} Python files.")

    # 2. Verify zero deprecated files or stale references
    for dep in ("Manager.ps1", "Windows_Defender_Patch.bat"):
        assert not (ROOT / dep).exists(), f"Deprecated file still present: {dep}"
        for chk_f in (ROOT / "assistant_server.py", ROOT / "ui_studio.html", ROOT / "manager.py", ROOT / "manifest.json"):
            txt = chk_f.read_text(encoding="utf-8", errors="replace")
            assert dep not in txt, f"Deprecated reference '{dep}' found in {chk_f.name}"
    print("[PASS 2/7] Zero deprecated files or stale references found.")

    # 3. Import & unit-test every modular avs/ component
    import xml.etree.ElementTree as ET
    from avs import (
        bridges,
        contracts,
        hardware_monitor,
        language_tools,
        manual_assets,
        memory_graph,
        model_polish,
        platform_bridge,
        referee,
        tool_registry,
        toolbox,
        turn_pipeline,
        workbench,
    )

    assert contracts.clamp_text("abcdef", 64) == "abcdef"
    assert "Truncated" in contracts.clamp_text("x" * 120, 64)
    assert len(platform_bridge.get_initial_pc_roots(ROOT)) >= 1
    assert isinstance(toolbox.toolbox.help_text(), str) and len(toolbox.toolbox.help_text()) > 10
    assert isinstance(toolbox.toolbox.openai_schemas(), list)

    # Memory graph & mind-map
    dedup = memory_graph.deduplicate_memory_rows([
        {"id": 1, "category": "user_location", "fact": "Posadas, Misiones", "hits": 1},
        {"id": 2, "category": "user_location", "fact": "Old City", "hits": 1},
        {"id": 3, "category": "lore_note", "fact": "Bluesky modular architecture", "hits": 2},
    ])
    assert len(dedup["kept"]) == 2 and len(dedup["inactive_ids"]) == 1
    mm = memory_graph.KeywordMindMap()
    assert mm.rebuild_from_items([(r["fact"], r["hits"]) for r in dedup["kept"]]) > 0

    # Tool registry & trust gate
    reg = tool_registry.ToolRegistry()
    reg.register(contracts.ToolSpec(name="demo_safe", trust_tier="safe_auto", aliases=("ds",)), lambda x="ok": x)
    reg.register(contracts.ToolSpec(name="demo_full", trust_tier="full_pc"), lambda: "full_ok")
    assert reg.invoke("ds", {"x": "hi"}).summary == "hi"
    assert not reg.invoke("demo_full", {}, trust_level="safe_auto").ok
    assert reg.invoke("demo_full", {}, trust_level="full_pc").ok

    # Bridges, turn pipeline, referee & model-agnostic polisher
    rec = bridges.build_bluesky_post_record("Smoke test post!", "2026-11-23T15:00:00Z")
    assert rec["$type"] == "app.bsky.feed.post"
    assert turn_pipeline.bounded_rounds(12) == contracts.MAX_ROUNDS
    assert "*waves*" in model_polish.normalize_model_output("*waves* Hello!", is_assistant_mode=False)
    assert "*waves*" not in model_polish.normalize_model_output("*waves* Hello!", is_assistant_mode=True)
    assert model_polish.classify_model_family("gemma-4-E4B-it") == "compact_general"
    assert model_polish.classify_model_family("dolphin-3.0-8b") == "expressive_chat"
    assert referee.is_abrupt_reply("This is a longer sentence that cuts off abruptly with")
    assert "specs" in hardware_monitor.get_full_hardware_report()

    # Language tools, offline lore-safe spellcheck & locale packs
    assert language_tools.detect_language("¿Qué clima hace hoy en Posadas?") == "es"
    assert language_tools.detect_language("What is the weather like today?") == "en"
    sc_res = language_tools.spellcheck_text("teh AetherVault lore with Zyrkathia", lang="en", custom_words=["zyrkathia"])
    assert sc_res["ok"] and "the AetherVault lore with Zyrkathia" == sc_res["corrected"]
    en_loc = language_tools.load_locale_pack(ROOT / "locales", "en")
    es_loc = language_tools.load_locale_pack(ROOT / "locales", "es")
    assert en_loc.get("meta", {}).get("code") == "en" and es_loc.get("meta", {}).get("code") == "es"
    assert en_loc.get("ui", {}).get("btn_send") and es_loc.get("ui", {}).get("btn_send")

    # Visual manual assets (10 EN + 10 ES + valid XML SVGs) & logo SVG
    assert len(manual_assets.get_manual_sections("en")) == 10
    assert len(manual_assets.get_manual_sections("es")) == 10
    for sec in manual_assets.get_manual_sections("en"):
        if sec.get("svg"):
            ET.fromstring(sec["svg"])
    ET.fromstring((ROOT / "aethervault_logo.svg").read_text(encoding="utf-8"))
    assert (ROOT / "AetherVault_Studio_Manual.pdf").read_bytes().startswith(b"%PDF-")
    print("[PASS 3/7] All 13 modular avs/ components, locales, SVG manual diagrams & PDF verified.")

    # 4. Verify isolated subprocess Workbench execution + Safe Auto gate
    wb_ok = workbench.run_workbench_subprocess("print(6 * 7)", ROOT / ".temp_cache", port=8000, token="smoke", timeout_sec=10, trust_level="safe_auto")
    assert wb_ok["ok"] and "42" in str(wb_ok["output"]), f"Workbench failed: {wb_ok}"
    wb_blk = workbench.run_workbench_subprocess("import os; os.system('echo nope')", ROOT / ".temp_cache", port=8000, token="smoke", timeout_sec=10, trust_level="safe_auto")
    assert not wb_blk["ok"], f"Expected Safe Auto gate to block os.system: {wb_blk}"
    print("[PASS 4/7] Isolated subprocess Workbench & Safe Auto gate passed.")

    # 5. Verify Bootstrapper (manager.py) dynamic version & repo defaults
    import manager
    rt_ver = manager.detect_runtime_version()
    assert rt_ver and rt_ver != "unhydrated", f"Unexpected runtime version: {rt_ver}"
    assert manager.get_configured_github_repo(), "GitHub repo default should be non-empty"
    assert {"Launch.bat", "Launch.sh", "manager.py"} == manager.FROZEN_BOOTSTRAP_FILES
    # Verify CRLF-tolerant Git blob SHA-1 matcher & Python syntax gate
    lf_sample = b"print('ok')\n"
    crlf_sample = b"print('ok')\r\n"
    lf_blob_sha = manager._git_blob_sha1(lf_sample)
    assert manager._matches_git_blob_sha(crlf_sample, lf_blob_sha, "avs/test.py")
    assert manager._verify_python_bytes(b"x = 1 + 2\n", "ok.py")[0]
    assert not manager._verify_python_bytes(b"def broken(:\n", "bad.py")[0]
    assert (ROOT / ".gitattributes").exists(), "Missing .gitattributes"
    print(f"[PASS 5/7] Bootstrapper (manager.py) + Commit-Pinned Tree Sync & Syntax Gate verified (runtime v{rt_ver}).")

    # 6. Verify ui_studio.html integrity
    ui_txt = (ROOT / "ui_studio.html").read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in ui_txt and "</html>" in ui_txt
    for dom_id in (
        "cfg-bsky-handle", "cfg-bsky-pass", "cfg-bsky-enabled", "cfg-tg-token", "cfg-sp-id",
        "quick-lang-select", "spellcheck-btn", "spellcheck-bar", "cfg-ui-lang", "cfg-speech-locale",
        "cfg-translate-bridge", "cfg-spellcheck-enabled", "cfg-argos-from", "cfg-argos-to", "manual-toc-bar"
    ):
        assert f'id="{dom_id}"' in ui_txt, f"Missing UI DOM element: {dom_id}"
    print("[PASS 6/7] ui_studio.html DOM & structure verified.")

    # 7. Verify manifest.json SHA-256 checksums for every file present on disk
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    files_map = manifest.get("files") or {}
    assert files_map, "manifest.json has no files listed"
    checked = 0
    for rel_path, expected_sha in files_map.items():
        fp = ROOT / rel_path
        assert fp.exists(), f"File listed in manifest.json missing on disk: {rel_path}"
        actual_sha = hashlib.sha256(fp.read_bytes()).hexdigest()
        assert actual_sha == expected_sha, f"SHA-256 mismatch for {rel_path}"
        checked += 1
    print(f"[PASS 7/7] manifest.json (v{manifest.get('version')}) verified ({checked} SHA-256 checksums matched).")

    print("=== ALL 7 SMOKE CHECKS PASSED! ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
