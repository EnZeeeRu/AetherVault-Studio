#!/usr/bin/env python3
"""
AetherVault Studio — Permanent Cross-Platform Bootstrapper & Control Center (manager.py)
100% Python Standard Library (tkinter GUI + automatic CLI fallback on headless/SSH).
"""
import os
import sys
import time
import json
import ctypes
import shutil
import socket
import threading
import zipfile
import platform
import hashlib
import py_compile
import subprocess
import webbrowser
import urllib.request
from pathlib import Path

BOOTSTRAPPER_TAG = "Bootstrapper"
DEFAULT_GITHUB_REPO = "EnZeeeRu/AetherVault-Studio"
FROZEN_BOOTSTRAP_FILES = {"Launch.bat", "Launch.sh", "manager.py"}


def detect_runtime_version() -> str:
    """Dynamically reads the installed runtime version from manifest.json or assistant_server.py."""
    m_p = Path(__file__).parent.resolve() / "manifest.json"
    if m_p.exists():
        try:
            ver = str(json.loads(m_p.read_text(encoding="utf-8")).get("version") or "").strip()
            if ver:
                return ver
        except Exception:
            pass
    srv_p = Path(__file__).parent.resolve() / "assistant_server.py"
    if srv_p.exists():
        try:
            head = srv_p.read_text(encoding="utf-8", errors="ignore")[:8000]
            import re as _re
            m = _re.search(r'^APP_VERSION\s*=\s*["\']([^"\']+)["\']', head, flags=_re.MULTILINE)
            if m:
                return m.group(1).strip()
        except Exception:
            pass
    return "unhydrated"


APP_VERSION = detect_runtime_version()
SERVER_PORT = int(os.environ.get("AVS_PORT", "8000"))
ROOT_DIR = Path(__file__).parent.resolve()
VENV_DIR = ROOT_DIR / ".venv"
STOCK_VAULT = ROOT_DIR / "stock_vault"
WHEEL_STOCK = STOCK_VAULT / "wheels"
MODEL_STOCK = STOCK_VAULT / "models"
MODELS_DIR = ROOT_DIR / "models"
PDF_DIR = ROOT_DIR / "priority_pdfs"
LORE_DIR = PDF_DIR / "lore"
MEM_DIR = ROOT_DIR / "memory_vault"
CHAT_LOGS_DIR = ROOT_DIR / "chat_logs"
GEN_IMG_DIR = ROOT_DIR / "generated_images"
GEN_AUDIO_DIR = ROOT_DIR / "generated_audio"
ASSETS_DIR = ROOT_DIR / "custom_assets"
BACKUPS_DIR = ROOT_DIR / "workspace_backups"
TEMP_CACHE = ROOT_DIR / ".temp_cache"

IS_WINDOWS = (os.name == "nt")

VULKAN_WHEEL_URL = "https://abetlen.github.io/llama-cpp-python/whl/vulkan"
CPU_WHEEL_URL = "https://abetlen.github.io/llama-cpp-python/whl/cpu"

CORE_PACKAGES = [
    "fastapi", "uvicorn", "python-multipart", "pymupdf", "huggingface_hub",
    "ddgs", "spotipy", "requests", "pillow", "psutil", "beautifulsoup4", "pyautogui"
]

QUICK_MODELS = [
    ("Gemma-4-E4B-it Unsloth GGUF (~5.0 GB - DEFAULT Offline Brain & Tool Master)",
     "unsloth/gemma-4-E4B-it-GGUF",
     "gemma-4-E4B-it-Q4_K_M.gguf"),
    ("Gemma-4-E2B-it Unsloth GGUF (~3.2 GB - Fast Edge Gemma 4)",
     "unsloth/gemma-4-E2B-it-GGUF",
     "gemma-4-E2B-it-Q4_K_M.gguf"),
    ("Gemma-4-12B-it Unsloth GGUF (~7.5 GB - Mid/High Rig Gemma 4)",
     "unsloth/gemma-4-12b-it-GGUF",
     "gemma-4-12b-it-Q4_K_M.gguf"),
    ("Gemma-4-26B-A4B-it MoE Unsloth GGUF (~15.5 GB - 4B Active MoE Gemma 4)",
     "unsloth/gemma-4-26B-A4B-it-GGUF",
     "gemma-4-26B-A4B-it-UD-Q4_K_M.gguf"),
    ("DeepSeek-R1-Distill-Qwen-1.5B Uncensored (~1.1 GB - Best for 2015 Laptops)",
     "mradermacher/DeepSeek-R1-Distill-Qwen-1.5B-uncensored-GGUF",
     "DeepSeek-R1-Distill-Qwen-1.5B-uncensored.Q4_K_M.gguf"),
    ("DeepSeek-R1-Distill-Qwen-7B Uncensored (~4.7 GB - Uncensored Reasoning)",
     "mradermacher/DeepSeek-R1-Distill-Qwen-7B-uncensored-GGUF",
     "DeepSeek-R1-Distill-Qwen-7B-uncensored.Q4_K_M.gguf"),
    ("Qwen2.5-1.5B-Instruct (~1.1 GB - Ultra-Fast Everyday Chat)",
     "bartowski/Qwen2.5-1.5B-Instruct-GGUF",
     "Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"),
    ("Qwen2.5-3B-Instruct (~2.1 GB - Sweet Spot for 8GB-16GB RAM Laptops)",
     "bartowski/Qwen2.5-3B-Instruct-GGUF",
     "Qwen2.5-3B-Instruct-Q4_K_M.gguf"),
    ("Qwen2.5-Coder-7B-Instruct (~4.7 GB - SOTA Local Coding & Self-Repair)",
     "bartowski/Qwen2.5-Coder-7B-Instruct-GGUF",
     "Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf"),
    ("Qwen2.5-Coder-3B-Instruct (~2.1 GB - Fast Lightweight Coding)",
     "bartowski/Qwen2.5-Coder-3B-Instruct-GGUF",
     "Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf"),
]


# =====================================================================
# CORE SHARED BACKEND LOGIC (Used by both Desktop GUI and Terminal CLI)
# =====================================================================
def ensure_dirs():
    for d in (
        STOCK_VAULT, WHEEL_STOCK, MODEL_STOCK, MODELS_DIR, PDF_DIR, LORE_DIR,
        MEM_DIR, CHAT_LOGS_DIR, GEN_IMG_DIR, GEN_AUDIO_DIR, ASSETS_DIR,
        BACKUPS_DIR, TEMP_CACHE
    ):
        d.mkdir(parents=True, exist_ok=True)


def get_venv_python() -> Path:
    if IS_WINDOWS:
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.2)
        s.connect(("192.168.1.1", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, int(port)))
            return False
        except OSError:
            return True


def find_available_port(preferred: int, max_tries: int = 20) -> int:
    for offset in range(max_tries):
        cand = int(preferred) + offset
        if not is_port_in_use(cand):
            return cand
    return int(preferred)


def _auto_open_browser_when_ready(port: int, timeout_sec: float = 35.0):
    url = f"http://127.0.0.1:{int(port)}"
    status_url = f"{url}/status"
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(status_url, timeout=1.0) as resp:
                if resp.status == 200:
                    webbrowser.open(url)
                    return
        except Exception:
            pass
        time.sleep(0.5)


def check_python_syntax(script_path: Path, log_fn=print) -> bool:
    if not script_path.exists():
        return False
    try:
        py_compile.compile(str(script_path), doraise=True)
        return True
    except Exception as e:
        log_fn(f"[FAIL] Syntax error in {script_path.name}: {e}")
        return False


def sync_newer_golden_snapshots(log_fn=print) -> str:
    if not BACKUPS_DIR.exists():
        return "None"
    golden_dirs = sorted(
        [d for d in BACKUPS_DIR.iterdir() if d.is_dir() and d.name.startswith("golden_")],
        key=lambda p: p.name,
        reverse=True,
    )
    if not golden_dirs:
        return "None"
    latest = golden_dirs[0]
    synced = 0
    for src in latest.iterdir():
        if not src.is_file():
            continue
        if src.suffix == ".py" and not check_python_syntax(src, log_fn=log_fn):
            continue
        live_dest = ROOT_DIR / src.name
        stock_dest = STOCK_VAULT / f"{src.name}.good"
        should_apply = (not live_dest.exists()) or (src.stat().st_mtime > live_dest.stat().st_mtime + 1.0)
        if should_apply:
            shutil.copy2(src, live_dest)
            shutil.copy2(src, stock_dest)
            synced += 1
            log_fn(f"[GOLDEN SYNC] Updated {src.name} from {latest.name}")
    return f"{latest.name} ({synced} updated)" if synced else latest.name


def boot_stock_check(log_fn=print) -> str:
    ensure_dirs()
    snap_status = sync_newer_golden_snapshots(log_fn=log_fn)
    srv = ROOT_DIR / "assistant_server.py"
    stock_srv = STOCK_VAULT / "assistant_server.py.good"
    if srv.exists() and check_python_syntax(srv, log_fn=log_fn):
        shutil.copy2(srv, stock_srv)
    elif stock_srv.exists() and check_python_syntax(stock_srv, log_fn=log_fn):
        shutil.copy2(stock_srv, srv)
        log_fn("[RESTORED] Recovered valid assistant_server.py from stock_vault.")

    ui = ROOT_DIR / "ui_studio.html"
    stock_ui = STOCK_VAULT / "ui_studio.html.good"
    if ui.exists():
        shutil.copy2(ui, stock_ui)
    elif stock_ui.exists():
        shutil.copy2(stock_ui, ui)

    db = ROOT_DIR / "memory_core.db"
    if db.exists():
        shutil.copy2(db, STOCK_VAULT / "memory_core.db.bak")
    return snap_status


def run_streamed_cmd(cmd: list, env=None, log_fn=print) -> int:
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
        env=env,
    )
    if proc.stdout:
        for line in proc.stdout:
            log_fn(line.rstrip())
    return proc.wait()


def ensure_venv(log_fn=print) -> Path:
    vpy = get_venv_python()
    if not vpy.exists():
        log_fn(f"[VENV] Creating portable virtual environment at {VENV_DIR}...")
        run_streamed_cmd([sys.executable, "-m", "venv", str(VENV_DIR)], log_fn=log_fn)
    return vpy


def check_module_installed(vpy: Path, mod_name: str) -> bool:
    r = subprocess.run([str(vpy), "-W", "ignore", "-c", f"import {mod_name}"], capture_output=True)
    return r.returncode == 0


def install_llama_cpp(vpy: Path, mode: str = "auto", log_fn=print) -> bool:
    flag_file = VENV_DIR / "engine_mode.flag"
    if mode == "cpu":
        log_fn("[ENGINE] Installing 2015 Laptop Safe CPU llama-cpp-python wheel...")
        rc = run_streamed_cmd([
            str(vpy), "-m", "pip", "install", "llama-cpp-python",
            "--force-reinstall", "--no-cache-dir", "--prefer-binary",
            "--extra-index-url", CPU_WHEEL_URL, "--find-links", str(WHEEL_STOCK)
        ], log_fn=log_fn)
        if rc == 0:
            flag_file.write_text("cpu\n", encoding="utf-8")
            log_fn("[OK] CPU llama-cpp-python installed!")
            return True
        return False

    log_fn("[ENGINE] Attempting Vulkan GPU llama-cpp-python wheel...")
    rc = run_streamed_cmd([
        str(vpy), "-m", "pip", "install", "llama-cpp-python",
        "--prefer-binary", "--extra-index-url", VULKAN_WHEEL_URL, "--find-links", str(WHEEL_STOCK)
    ], log_fn=log_fn)
    if rc == 0 and check_module_installed(vpy, "llama_cpp"):
        flag_file.write_text("vulkan\n", encoding="utf-8")
        log_fn("[OK] Vulkan GPU llama-cpp-python ready!")
        return True

    log_fn("[AUTO-HEAL] Vulkan wheel unavailable for this Python/OS -> trying CPU prebuilt wheel...")
    rc2 = run_streamed_cmd([
        str(vpy), "-m", "pip", "install", "llama-cpp-python",
        "--prefer-binary", "--extra-index-url", CPU_WHEEL_URL, "--find-links", str(WHEEL_STOCK)
    ], log_fn=log_fn)
    if rc2 == 0 and check_module_installed(vpy, "llama_cpp"):
        flag_file.write_text("cpu\n", encoding="utf-8")
        log_fn("[OK] CPU llama-cpp-python ready!")
        return True

    log_fn("[WARN] Prebuilt wheel not found (e.g., Python 3.13+ has fewer wheels). Studio can still run in Smart API mode, or install Python 3.11/3.12 for local GGUF wheels.")
    return False


def ensure_environment(log_fn=print, force_install: bool = False) -> Path:
    vpy = ensure_venv(log_fn=log_fn)
    if force_install or not check_module_installed(vpy, "fastapi") or not check_module_installed(vpy, "uvicorn"):
        log_fn("[DEPS] Installing/verifying core Python packages...")
        run_streamed_cmd([str(vpy), "-m", "pip", "install", *CORE_PACKAGES, "--find-links", str(WHEEL_STOCK)], log_fn=log_fn)
    if force_install or not check_module_installed(vpy, "llama_cpp"):
        install_llama_cpp(vpy, mode="auto", log_fn=log_fn)
    return vpy


def stock_offline_vault(log_fn=print):
    """Restored Stock Offline Vault: caches .whl installers, golden scripts, and local GGUF models."""
    ensure_dirs()
    vpy = ensure_venv(log_fn=log_fn)
    log_fn("[STOCK VAULT] Backing up verified golden scripts...")
    for fname in ("assistant_server.py", "ui_studio.html"):
        src = ROOT_DIR / fname
        if src.exists():
            if fname.endswith(".py") and not check_python_syntax(src, log_fn=log_fn):
                continue
            shutil.copy2(src, STOCK_VAULT / f"{fname}.good")
    db = ROOT_DIR / "memory_core.db"
    if db.exists():
        shutil.copy2(db, STOCK_VAULT / "memory_core.db.bak")

    log_fn(f"[STOCK VAULT] Caching offline .whl installers into {WHEEL_STOCK}...")
    run_streamed_cmd([str(vpy), "-m", "pip", "download", *CORE_PACKAGES, "-d", str(WHEEL_STOCK)], log_fn=log_fn)
    run_streamed_cmd([
        str(vpy), "-m", "pip", "download", "llama-cpp-python",
        "--prefer-binary", "--extra-index-url", CPU_WHEEL_URL, "-d", str(WHEEL_STOCK)
    ], log_fn=log_fn)

    ggufs = list(MODELS_DIR.glob("*.gguf"))
    for idx, m in enumerate(ggufs, 1):
        dest = MODEL_STOCK / m.name
        if not dest.exists():
            log_fn(f"[STOCK VAULT] Backing up model [{idx}/{len(ggufs)}]: {m.name}...")
            shutil.copy2(m, dest)
    log_fn("[OK] Offline Stock Vault (wheels + golden scripts + local GGUF models) is stocked and ready!")


def restore_golden_backup(log_fn=print):
    restored = []
    for fname in ("assistant_server.py", "ui_studio.html"):
        src = STOCK_VAULT / f"{fname}.good"
        if src.exists():
            shutil.copy2(src, ROOT_DIR / fname)
            restored.append(fname)
    db_bak = STOCK_VAULT / "memory_core.db.bak"
    if db_bak.exists():
        shutil.copy2(db_bak, ROOT_DIR / "memory_core.db")
        restored.append("memory_core.db")
    log_fn(f"[OK] Restored from stock_vault: {', '.join(restored) if restored else 'nothing found yet'}")


def export_workspace_zip(log_fn=print) -> Path:
    ensure_dirs()
    stamp = time.strftime("%Y%m%d_%H%M%S")
    out_zip = BACKUPS_DIR / f"AetherVault_Profile_{stamp}.zip"
    targets = [
        "memory_core.db", "workspace_config.json", "user_profile_card.json",
        "glossary_index.json", "pseudo_memory_index.json", "partner_evolution.json",
        "priority_pdfs", "memory_vault", "chat_logs", "custom_assets",
        "generated_images", "generated_audio"
    ]
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in targets:
            p = ROOT_DIR / rel
            if p.is_file():
                zf.write(p, arcname=p.relative_to(ROOT_DIR).as_posix())
            elif p.is_dir():
                for f in p.rglob("*"):
                    if f.is_file():
                        zf.write(f, arcname=f.relative_to(ROOT_DIR).as_posix())
    log_fn(f"[OK] Exported portable workspace: {out_zip}")
    return out_zip


def import_workspace_zip(zip_path: Path, log_fn=print):
    if not zip_path.exists():
        log_fn(f"[ERROR] File not found: {zip_path}")
        return
    root_res = ROOT_DIR.resolve()
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.namelist():
            if ".." in member or member.startswith("/") or member.startswith("\\") or ":" in member:
                continue
            target_out = (ROOT_DIR / member).resolve()
            if root_res not in target_out.parents and target_out != root_res:
                continue
            zf.extract(member, ROOT_DIR)
    log_fn(f"[OK] Imported workspace .ZIP from {zip_path.name}!")


def download_model_file(repo: str, fname: str, log_fn=print, progress_fn=None):
    ensure_dirs()
    url = f"https://huggingface.co/{repo}/resolve/main/{fname}"
    dest = MODELS_DIR / fname
    part = dest.with_suffix(dest.suffix + ".part")
    log_fn(f"[DOWNLOAD] Connecting to {url} ...")
    req = urllib.request.Request(url, headers={"User-Agent": f"AetherVaultStudio/{APP_VERSION}"})
    t0 = time.time()
    downloaded = 0
    with urllib.request.urlopen(req, timeout=30) as resp, open(part, "wb") as out:
        total = int(resp.headers.get("Content-Length") or 0)
        last_tick = 0.0
        while True:
            chunk = resp.read(256 * 1024)
            if not chunk:
                break
            out.write(chunk)
            downloaded += len(chunk)
            now = time.time()
            if (now - last_tick) >= 0.4:
                last_tick = now
                elapsed = max(0.1, now - t0)
                mb = downloaded / (1024 * 1024)
                speed = mb / elapsed
                if total > 0:
                    pct = (downloaded / total) * 100.0
                    tot_mb = total / (1024 * 1024)
                    msg = f"[DOWNLOAD] {fname}: {pct:5.1f}% ({mb:.1f}/{tot_mb:.1f} MB @ {speed:.2f} MB/s)"
                    if progress_fn:
                        progress_fn(pct, msg)
                    else:
                        log_fn(msg)
    part.replace(dest)
    if progress_fn:
        progress_fn(100.0, f"[OK] Saved {dest.name}!")
    log_fn(f"[OK] Saved {dest.name} into /models!")



def get_configured_github_repo() -> str:
    cfg_p = ROOT_DIR / "workspace_config.json"
    if cfg_p.exists():
        try:
            data = json.loads(cfg_p.read_text(encoding="utf-8"))
            val = str(data.get("github_repo") or "").strip().strip("/")
            if val:
                return val
        except Exception:
            pass
    env_val = os.environ.get("AVS_GITHUB_REPO", "").strip().strip("/")
    if env_val:
        return env_val
    m_p = ROOT_DIR / "manifest.json"
    if m_p.exists():
        try:
            mv = str(json.loads(m_p.read_text(encoding="utf-8")).get("repo") or "").strip().strip("/")
            if mv:
                return mv
        except Exception:
            pass
    return DEFAULT_GITHUB_REPO


def set_configured_github_repo(repo_slug: str, log_fn=print):
    slug = (repo_slug or "").strip().strip("/")
    cfg_p = ROOT_DIR / "workspace_config.json"
    data = {}
    if cfg_p.exists():
        try:
            data = json.loads(cfg_p.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    data["github_repo"] = slug
    cfg_p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    log_fn(f"[GITHUB] Linked repository -> '{slug or '(none)'}'")


def sync_from_github_ota(repo_slug: str = "", log_fn=print, include_bootstrap: bool = False) -> bool:
    """
    Bootstrapper OTA Updater & Auto-Hydrator:
    Fetches manifest.json from GitHub, verifies SHA-256 checksums, snapshots runtime files
    to stock_vault, and updates runtime files WITHOUT overwriting frozen bootstrapper files
    (unless missing) or touching user data!
    """
    global APP_VERSION
    slug = (repo_slug or get_configured_github_repo()).strip().strip("/")
    if not slug or "/" not in slug:
        log_fn("[OTA] No GitHub repo configured. Run: /repo <username>/AetherVault-Studio")
        return False
    base_raw = f"https://raw.githubusercontent.com/{slug}/main"
    bust = int(time.time())
    ota_headers = {
        "User-Agent": f"AetherVaultStudio-Bootstrapper/{APP_VERSION}",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    manifest_url = f"{base_raw}/manifest.json?t={bust}"
    log_fn(f"[OTA] Checking {base_raw}/manifest.json ...")
    try:
        req = urllib.request.Request(manifest_url, headers=ota_headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            manifest_raw = resp.read()
            manifest = json.loads(manifest_raw.decode("utf-8"))
    except Exception as e:
        log_fn(f"[OTA ERROR] Could not fetch manifest.json: {e}")
        return False

    files = manifest.get("files") or {}
    updated = 0
    warn_count = 0
    for rel_path, expected_sha in files.items():
        if ".." in rel_path or rel_path.startswith("/") or ":" in rel_path:
            continue
        dest = (ROOT_DIR / rel_path).resolve()
        if ROOT_DIR.resolve() not in dest.parents and dest != ROOT_DIR.resolve():
            continue
        if rel_path in FROZEN_BOOTSTRAP_FILES and dest.exists() and not include_bootstrap:
            continue
        if dest.exists():
            cur_sha = hashlib.sha256(dest.read_bytes()).hexdigest()
            if expected_sha and cur_sha == expected_sha:
                continue
            if dest.parent == ROOT_DIR and dest.name in ("assistant_server.py", "ui_studio.html"):
                STOCK_VAULT.mkdir(parents=True, exist_ok=True)
                shutil.copy2(dest, STOCK_VAULT / f"{dest.name}.good")
        file_url = f"{base_raw}/{rel_path}?t={bust}"
        try:
            f_req = urllib.request.Request(file_url, headers=ota_headers)
            with urllib.request.urlopen(f_req, timeout=25) as f_resp:
                raw_bytes = f_resp.read()
            if expected_sha and hashlib.sha256(raw_bytes).hexdigest() != expected_sha:
                warn_count += 1
                log_fn(f"[OTA WARN] SHA-256 mismatch for {rel_path} — skipped!")
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(raw_bytes)
            updated += 1
            log_fn(f"[OTA] Updated {rel_path} ({len(raw_bytes):,} bytes)")
        except Exception as fe:
            warn_count += 1
            log_fn(f"[OTA WARN] Failed to download {rel_path}: {fe}")

    if warn_count == 0:
        try:
            (ROOT_DIR / "manifest.json").write_bytes(manifest_raw)
        except Exception:
            pass
    APP_VERSION = detect_runtime_version()
    if warn_count:
        log_fn(f"[OTA PARTIAL] Synced {updated} file(s) with {warn_count} warning(s) from {slug} (Runtime v{manifest.get('version', '?')}).")
    else:
        log_fn(f"[OTA OK] Sync complete from {slug} (Runtime v{manifest.get('version', '?')} | {updated} file(s) updated).")
    return warn_count == 0


REQUIRED_RUNTIME_FILES = (
    "assistant_server.py",
    "ui_studio.html",
    "aethervault_logo.svg",
    "AetherVault_Studio_Manual.pdf",
    "locales/en.json",
    "locales/es.json",
    "avs/__init__.py",
    "avs/platform_bridge.py",
    "avs/toolbox.py",
    "avs/workbench.py",
    "avs/hardware_monitor.py",
    "avs/contracts.py",
    "avs/memory_graph.py",
    "avs/referee.py",
    "avs/tool_registry.py",
    "avs/bridges.py",
    "avs/turn_pipeline.py",
    "avs/model_polish.py",
    "avs/language_tools.py",
    "avs/manual_assets.py",
)


def ensure_runtime_hydrated(log_fn=print) -> bool:
    """If launched as a bare bootstrapper or missing any required runtime/avs module, auto-hydrates via GitHub OTA."""
    missing = [rel for rel in REQUIRED_RUNTIME_FILES if not (ROOT_DIR / rel).exists()]
    if not missing:
        return True
    log_fn(f"[BOOTSTRAPPER] Missing {len(missing)} runtime file(s) ({', '.join(missing[:4])}) -> auto-hydrating from GitHub OTA...")
    sync_from_github_ota(log_fn=log_fn)
    still_missing = [rel for rel in REQUIRED_RUNTIME_FILES if not (ROOT_DIR / rel).exists()]
    if still_missing:
        log_fn(f"[BOOTSTRAPPER ERROR] Still missing required files after OTA: {', '.join(still_missing)}")
        return False
    return True


def cleanup_temp():
    if TEMP_CACHE.exists():
        shutil.rmtree(TEMP_CACHE, ignore_errors=True)


# =====================================================================
# NATIVE CROSS-PLATFORM DESKTOP GUI (tkinter, Dark AetherVault Theme)
# =====================================================================
def launch_desktop_gui(snap_info: str) -> bool:
    try:
        import tkinter as tk
        from tkinter import ttk, filedialog, simpledialog, messagebox
    except Exception:
        return False

    try:
        root = tk.Tk()
    except Exception:
        return False

    BG = "#0d0e12"
    SIDEBAR = "#14151c"
    PANEL = "#1b1d27"
    ACCENT = "#7c3aed"
    ACCENT_HOV = "#6d28d9"
    CYAN = "#38bdf8"
    GREEN = "#10b981"
    YELLOW = "#f59e0b"
    TEXT = "#e5e7eb"
    MUTED = "#9ca3af"

    root.title(f"AetherVault Studio — Bootstrapper & Control Center (Runtime v{APP_VERSION})")
    root.geometry("920x640")
    root.minsize(820, 560)
    root.configure(bg=BG)

    server_proc_holder = {"proc": None}

    def ui_log(msg: str):
        def _append():
            log_text.configure(state="normal")
            log_text.insert("end", str(msg) + "\n")
            log_text.see("end")
            log_text.configure(state="disabled")
        root.after(0, _append)

    def refresh_badges():
        vpy = get_venv_python()
        ggufs = list(MODELS_DIR.glob("*.gguf")) if MODELS_DIR.exists() else []
        flag_p = VENV_DIR / "engine_mode.flag"
        eng = flag_p.read_text(encoding="utf-8", errors="ignore").strip().upper() if flag_p.exists() else "AUTO"
        lan_ip = get_local_ip()
        venv_lbl.configure(text=f".venv: {'READY' if vpy.exists() else 'NOT CREATED'}", fg=GREEN if vpy.exists() else YELLOW)
        models_lbl.configure(text=f"Models: {len(ggufs)} GGUF(s)")
        engine_lbl.configure(text=f"Engine: {eng}")
        ver_now = detect_runtime_version()
        root.title(f"AetherVault Studio — Bootstrapper & Control Center (Runtime v{ver_now})")
        hdr_title_lbl.configure(text=f"AETHERVAULT STUDIO — BOOTSTRAPPER  (Runtime v{ver_now})")
        url_lbl.configure(text=f"Desktop: http://127.0.0.1:{SERVER_PORT}  |  LAN: http://{lan_ip}:{SERVER_PORT}")

    def run_bg(task_name: str, fn):
        def _worker():
            ui_log(f"\n--- {task_name} ---")
            try:
                fn()
            except Exception as e:
                ui_log(f"[ERROR] {e}")
            finally:
                root.after(0, refresh_badges)
        threading.Thread(target=_worker, daemon=True).start()

    # Header Banner
    hdr = tk.Frame(root, bg=SIDEBAR, padx=16, pady=12, highlightbackground="#2b2e3d", highlightthickness=1)
    hdr.pack(fill="x")
    hdr_title_lbl = tk.Label(hdr, text=f"AETHERVAULT STUDIO — BOOTSTRAPPER  (Runtime v{APP_VERSION})", font=("Segoe UI", 14, "bold"), bg=SIDEBAR, fg="#ffffff")
    hdr_title_lbl.pack(anchor="w")
    tk.Label(hdr, text=f"Made with <3 in Argentina by Enzeru  |  {platform.system()} ({platform.machine()})  |  Python {platform.python_version()}",
             font=("Segoe UI", 9), bg=SIDEBAR, fg=MUTED).pack(anchor="w", pady=(2, 6))

    # Status Pills Row
    pills = tk.Frame(hdr, bg=SIDEBAR)
    pills.pack(fill="x")
    venv_lbl = tk.Label(pills, text=".venv: ...", font=("Consolas", 9, "bold"), bg=PANEL, fg=GREEN, padx=8, pady=3)
    venv_lbl.pack(side="left", padx=(0, 6))
    models_lbl = tk.Label(pills, text="Models: ...", font=("Consolas", 9, "bold"), bg=PANEL, fg=CYAN, padx=8, pady=3)
    models_lbl.pack(side="left", padx=(0, 6))
    engine_lbl = tk.Label(pills, text="Engine: ...", font=("Consolas", 9, "bold"), bg=PANEL, fg="#c084fc", padx=8, pady=3)
    engine_lbl.pack(side="left", padx=(0, 6))
    tk.Label(pills, text=f"Golden Sync: {snap_info}", font=("Consolas", 9), bg=PANEL, fg=TEXT, padx=8, pady=3).pack(side="left")

    url_lbl = tk.Label(hdr, text="", font=("Consolas", 9), bg=SIDEBAR, fg=CYAN)
    url_lbl.pack(anchor="w", pady=(6, 0))

    # Main Split Body: Left Actions + Right Live Log Console
    body = tk.Frame(root, bg=BG, padx=14, pady=12)
    body.pack(fill="both", expand=True)

    left = tk.Frame(body, bg=BG, width=320)
    left.pack(side="left", fill="y", padx=(0, 12))
    left.pack_propagate(False)

    def make_btn(text, cmd, bg_c=PANEL, fg_c=TEXT, bold=False):
        b = tk.Button(
            left, text=text, command=cmd,
            bg=bg_c, fg=fg_c, activebackground=ACCENT_HOV, activeforeground="#ffffff",
            relief="flat", bd=0, padx=10, pady=8, anchor="w", cursor="hand2",
            font=("Segoe UI", 9, "bold" if bold else "normal")
        )
        b.pack(fill="x", pady=3)
        return b

    def on_launch_server():
        if server_proc_holder["proc"] and server_proc_holder["proc"].poll() is None:
            ui_log("[INFO] Server is already running!")
            return
        def _task():
            if not ensure_runtime_hydrated(log_fn=ui_log):
                return
            vpy = ensure_environment(log_fn=ui_log, force_install=False)
            srv = ROOT_DIR / "assistant_server.py"
            if not check_python_syntax(srv, log_fn=ui_log):
                return
            active_port = find_available_port(SERVER_PORT)
            if active_port != SERVER_PORT:
                ui_log(f"[PORT AUTO-RECOVERY] Port {SERVER_PORT} busy -> switched to {active_port}")
            env = os.environ.copy()
            env["PIP_CACHE_DIR"] = str(ROOT_DIR / "pip_cache")
            env["HF_HOME"] = str(ROOT_DIR / "hf_cache")
            env["PYTHONUNBUFFERED"] = "1"
            env["PYTHONIOENCODING"] = "utf-8"
            env["PYTHONUTF8"] = "1"
            env["AVS_PORT"] = str(active_port)
            active_port_box["port"] = active_port
            ui_log(f"[LAUNCH] Starting AetherVault Studio at http://127.0.0.1:{active_port} ...")
            threading.Thread(target=_auto_open_browser_when_ready, args=(active_port,), daemon=True).start()
            proc = subprocess.Popen(
                [str(vpy), "-u", str(srv)],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", bufsize=1, env=env
            )
            server_proc_holder["proc"] = proc
            if proc.stdout:
                for line in proc.stdout:
                    ui_log(line.rstrip())
            ui_log(f"[SERVER] Process exited with code {proc.wait()}.")
        run_bg("Launch AetherVault Server", _task)

    def on_stop_server():
        p = server_proc_holder.get("proc")
        if p and p.poll() is None:
            p.terminate()
            ui_log("[SERVER] Sent terminate signal to AetherVault Server.")
        else:
            ui_log("[INFO] No active server process running from this window.")

    def on_download_model():
        win = tk.Toplevel(root)
        win.title("Quick Model Downloader (1-11)")
        win.geometry("620x440")
        win.configure(bg=BG)
        tk.Label(win, text="Select a Starter, Coder, or Gemma 4 GGUF Model:", font=("Segoe UI", 10, "bold"), bg=BG, fg=TEXT).pack(anchor="w", padx=12, pady=8)
        lb = tk.Listbox(win, bg=PANEL, fg=TEXT, selectbackground=ACCENT, font=("Consolas", 9), height=12, bd=0, highlightthickness=1)
        for idx, (lbl, _, _) in enumerate(QUICK_MODELS, 1):
            lb.insert("end", f"[{idx:2d}] {lbl}")
        lb.insert("end", "[11] Custom Hugging Face Repo + .gguf Filename")
        lb.pack(fill="both", expand=True, padx=12, pady=4)

        def _start_dl():
            sel = lb.curselection()
            if not sel:
                return
            i = sel[0]
            if i == len(QUICK_MODELS):
                repo = simpledialog.askstring("Custom HF Repo", "Hugging Face Repo ID (e.g. unsloth/gemma-4-E4B-it-GGUF):", parent=win)
                fname = simpledialog.askstring("Custom GGUF File", "Exact .gguf Filename:", parent=win)
                if not repo or not fname:
                    return
            else:
                _, repo, fname = QUICK_MODELS[i]
            win.destroy()
            run_bg(f"Download {fname}", lambda: download_model_file(repo.strip(), fname.strip(), log_fn=ui_log))

        tk.Button(win, text="Download Selected Model", command=_start_dl, bg=ACCENT, fg="#fff", relief="flat", padx=12, pady=8, font=("Segoe UI", 9, "bold")).pack(pady=10)

    def on_export_zip():
        run_bg("Export Portable .ZIP", lambda: export_workspace_zip(log_fn=ui_log))

    def on_import_zip():
        p = filedialog.askopenfilename(title="Select AetherVault Workspace .ZIP", filetypes=[("ZIP Archives", "*.zip")])
        if p:
            run_bg("Import Portable .ZIP", lambda: import_workspace_zip(Path(p), log_fn=ui_log))

    def on_switch_engine():
        ans = messagebox.askyesnocancel(
            "Switch Engine Backend",
            "YES = Vulkan GPU Offload (Dedicated GPUs)\nNO = 2015 Laptop Safe CPU Build\nCANCEL = Abort"
        )
        if ans is None:
            return
        mode = "vulkan" if ans else "cpu"
        run_bg(f"Switch Engine -> {mode.upper()}", lambda: install_llama_cpp(ensure_venv(log_fn=ui_log), mode=mode, log_fn=ui_log))

    make_btn("1. Launch AetherVault Server", on_launch_server, bg_c=ACCENT, fg_c="#ffffff", bold=True)
    make_btn("   Stop Running Server", on_stop_server, bg_c="#3f1d28", fg_c="#fca5a5")
    make_btn("2. Setup / Verify .venv & Core Packages", lambda: run_bg("Verify Environment", lambda: ensure_environment(log_fn=ui_log, force_install=True)))
    make_btn("3. Quick-Download Models & Gemma 4 (1-11)", on_download_model)
    make_btn("4. Export Portable Workspace (.ZIP)", on_export_zip)
    make_btn("   Import Portable Workspace (.ZIP)", on_import_zip)
    make_btn("5. Stock Offline Vault (Wheels + Golden + Models)", lambda: run_bg("Stock Offline Vault", lambda: stock_offline_vault(log_fn=ui_log)), bg_c="#1e293b", fg_c=CYAN)
    make_btn("6. Switch Engine (Vulkan GPU vs Safe CPU)", on_switch_engine)
    make_btn("7. Restore Golden Backup", lambda: run_bg("Restore Golden Backup", lambda: restore_golden_backup(log_fn=ui_log)))
    make_btn("8. Check for GitHub OTA Updates (/update)", lambda: run_bg("GitHub OTA Update", lambda: sync_from_github_ota(log_fn=ui_log)), bg_c="#0f2922", fg_c=GREEN)
    make_btn("9. Run Automated Smoke Suite (tests/smoke.py)", lambda: run_bg("Smoke Suite", lambda: run_streamed_cmd([sys.executable, str(ROOT_DIR / "tests" / "smoke.py")], log_fn=ui_log)))

    # Right Live Output Console
    right = tk.Frame(body, bg=PANEL, highlightbackground="#2b2e3d", highlightthickness=1)
    right.pack(side="right", fill="both", expand=True)
    tk.Label(right, text="  LIVE CONSOLE & TELEMETRY OUTPUT", font=("Consolas", 9, "bold"), bg=SIDEBAR, fg=CYAN, anchor="w", pady=6).pack(fill="x")
    log_text = tk.Text(right, bg="#08090c", fg="#d1d5db", font=("Consolas", 9), relief="flat", bd=8, state="disabled", wrap="word")
    log_text.pack(fill="both", expand=True)

    # Interactive Manager Console Command Bar (/help, /status, /stop, /inject, /toggle, /py, /log, /clear, /restart)
    cmd_history = []
    hist_idx = {"i": 0}
    active_port_box = {"port": SERVER_PORT}

    cmd_bar = tk.Frame(right, bg=SIDEBAR, padx=6, pady=6)
    cmd_bar.pack(fill="x", side="bottom")
    tk.Label(cmd_bar, text=">", font=("Consolas", 10, "bold"), bg=SIDEBAR, fg=CYAN).pack(side="left", padx=(2, 4))
    cmd_entry = tk.Entry(cmd_bar, bg="#08090c", fg="#f3f4f6", insertbackground=CYAN, font=("Consolas", 9), relief="flat", bd=4)
    cmd_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

    def _api_req(method: str, path: str, payload=None):
        url = f"http://127.0.0.1:{active_port_box['port']}{path}"
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = {"Content-Type": "application/json"} if data is not None else {}
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))

    def run_console_command(event=None):
        raw = cmd_entry.get().strip()
        if not raw:
            return
        cmd_entry.delete(0, "end")
        cmd_history.append(raw)
        hist_idx["i"] = len(cmd_history)
        ui_log(f"> {raw}")

        parts = raw.split(None, 1)
        cmd = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        if cmd in ("/help", "help", "?"):
            ui_log(
                "=== MANAGER CONSOLE COMMANDS ===\n"
                "  /help                        Show this command list\n"
                "  /status                      Live server status (model, GPU, RAM, mode, trust)\n"
                "  /stop                        Halt active generation loop immediately\n"
                "  /inject <cat> | <fact>       Inject a fact into Priority #1 Memory Vault\n"
                "  /toggle <setting> <value>    Flip Studio toggle (e.g. /toggle workbench_trust full_pc)\n"
                "  /py <code>                   Run Python in killable subprocess Workbench\n"
                "  /log [keyword] [lines]       Tail error_audit.log locally (works offline/stopped)\n"
                "  /clear                       Clear console output\n"
                "  /specs                       Deep SpecPulse hardware specs (64-bit VRAM, CPU, RAM)\n"
                "  /pip <pkg>                   Install any custom PyPI package into .venv\n"
                "  /repo <user/repo>            Link GitHub repo for 1-click OTA updates\n"
                "  /update                      Pull latest core files from GitHub (preserves user data)\n"
                "  /restart                     Stop & relaunch assistant_server.py"
            )
        elif cmd == "/clear":
            log_text.configure(state="normal")
            log_text.delete("1.0", "end")
            log_text.configure(state="disabled")
        elif cmd == "/log":
            log_p = ROOT_DIR / "error_audit.log"
            if not log_p.exists():
                ui_log("[LOG] error_audit.log is clean (not created yet).")
                return
            toks = arg.split()
            n_lines = int(toks[-1]) if (toks and toks[-1].isdigit()) else 25
            kw = " ".join(toks[:-1] if (toks and toks[-1].isdigit()) else toks).strip().lower()
            lines = log_p.read_text(encoding="utf-8", errors="replace").splitlines()
            if kw:
                lines = [ln for ln in lines if kw in ln.lower()]
            ui_log("\n".join(lines[-n_lines:]) if lines else f"[LOG] No lines matched '{kw}'.")
        elif cmd == "/specs":
            def _sp():
                data = _api_req("GET", "/api/hardware_specs")
                sp = data.get("specs") or {}
                lv = data.get("live") or {}
                gpus = ", ".join(f"{g.get('name')} ({g.get('vram_gb')} GB)" for g in (sp.get("gpus") or []))
                ui_log(
                    f"[SPECS] Host: {sp.get('hostname')} | CPU: {(sp.get('cpu') or {}).get('name')} ({lv.get('cpu_percent')}%)\n"
                    f"        GPU: {gpus} (Load: {lv.get('gpu_util_percent')}% | VRAM Used: {lv.get('gpu_vram_used_mb')} MB)\n"
                    f"        RAM: {lv.get('ram_used_gb')}/{(sp.get('ram') or {}).get('total_gb')} GB ({lv.get('ram_percent')}%)"
                )
            run_bg("Console /specs", _sp)
        elif cmd == "/pip":
            if not arg:
                ui_log("[USAGE] /pip <package_name>")
                return
            run_bg(f"pip install {arg}", lambda: run_streamed_cmd([str(ensure_venv(log_fn=ui_log)), "-m", "pip", "install", arg], log_fn=ui_log))
        elif cmd == "/repo":
            set_configured_github_repo(arg, log_fn=ui_log)
        elif cmd == "/update":
            run_bg("GitHub OTA Update", lambda: sync_from_github_ota(arg, log_fn=ui_log))
        elif cmd == "/restart":
            on_stop_server()
            root.after(800, on_launch_server)
        elif cmd == "/status":
            def _st():
                st = _api_req("GET", "/status")
                ram = st.get("ram") or {}
                ui_log(
                    f"[STATUS] Model: {st.get('current_model')} | GPU: {st.get('gpu_offload')} | "
                    f"Mode: {st.get('workspace_mode')} | Trust: {st.get('workbench_trust')} | "
                    f"Brain: {st.get('brain_mode')} | RAM: {ram.get('free_gb')}/{ram.get('total_gb')} GB free | "
                    f"Step: {st.get('current_step')}"
                )
            run_bg("Console /status", _st)
        elif cmd == "/stop":
            run_bg("Console /stop", lambda: ui_log(f"[STOP] {_api_req('POST', '/stop_generation', {})}"))
        elif cmd == "/inject":
            if "|" in arg:
                cat, fact = [x.strip() for x in arg.split("|", 1)]
            else:
                cat, fact = "active_state", arg
            if not fact:
                ui_log("[USAGE] /inject <category> | <fact>")
                return
            run_bg("Console /inject", lambda: ui_log(f"[INJECT] {_api_req('POST', '/memory/add', {'category': cat, 'fact': fact})}"))
        elif cmd == "/toggle":
            t_parts = arg.split(None, 1)
            if len(t_parts) < 2:
                ui_log("[USAGE] /toggle <setting> <value>  (e.g. /toggle workbench_trust full_pc)")
                return
            k, v_raw = t_parts[0].strip(), t_parts[1].strip()
            v = True if v_raw.lower() == "true" else (False if v_raw.lower() == "false" else v_raw)
            run_bg("Console /toggle", lambda: ui_log(f"[TOGGLE] {k}={v} -> ok={_api_req('POST', '/config/update', {k: v}).get('ok')}"))
        elif cmd == "/py":
            if not arg:
                ui_log("[USAGE] /py print(2 + 2)")
                return
            def _py():
                res = _api_req("POST", "/workbench/subprocess", {"code": arg, "timeout_sec": 15})
                ui_log(f"[PY ok={res.get('ok')} | {res.get('elapsed_sec')}s]\n{res.get('output')}")
            run_bg("Console /py", _py)
        else:
            ui_log(f"[CONSOLE] Unknown command '{cmd}'. Type /help for available commands.")

    def _hist_up(event):
        if cmd_history and hist_idx["i"] > 0:
            hist_idx["i"] -= 1
            cmd_entry.delete(0, "end")
            cmd_entry.insert(0, cmd_history[hist_idx["i"]])
        return "break"

    def _hist_down(event):
        if cmd_history and hist_idx["i"] < len(cmd_history) - 1:
            hist_idx["i"] += 1
            cmd_entry.delete(0, "end")
            cmd_entry.insert(0, cmd_history[hist_idx["i"]])
        else:
            hist_idx["i"] = len(cmd_history)
            cmd_entry.delete(0, "end")
        return "break"

    cmd_entry.bind("<Return>", run_console_command)
    cmd_entry.bind("<Up>", _hist_up)
    cmd_entry.bind("<Down>", _hist_down)
    tk.Button(cmd_bar, text="Run", command=run_console_command, bg=ACCENT, fg="#fff", relief="flat", padx=10, pady=3, font=("Segoe UI", 8, "bold"), cursor="hand2").pack(side="right")

    refresh_badges()
    ui_log(f"AetherVault Studio Bootstrapper Ready (Installed Runtime: v{APP_VERSION}).")
    ui_log(f"Root Folder: {ROOT_DIR}")
    ui_log("Click '1. Launch AetherVault Server' to auto-verify packages and open the Studio UI.")

    def on_close():
        p = server_proc_holder.get("proc")
        if p and p.poll() is None:
            p.terminate()
        cleanup_temp()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()
    return True


# =====================================================================
# TERMINAL CLI FALLBACK (Used when --cli is passed or no GUI display)
# =====================================================================
def run_cli(snap_info: str) -> int:
    while True:
        lan_ip = get_local_ip()
        os_tag = f"{platform.system()} ({platform.machine()})"
        print("=======================================================================")
        print(f"   AETHERVAULT STUDIO — BOOTSTRAPPER (CLI)  |  Runtime v{detect_runtime_version()}")
        print(f"   Platform    : {os_tag} | Python {platform.python_version()}")
        print(f"   Root Folder : {ROOT_DIR}")
        print(f"   Golden Sync : {snap_info}")
        print(f"   Desktop URL : http://127.0.0.1:{SERVER_PORT}")
        print(f"   LAN / Phone : http://{lan_ip}:{SERVER_PORT}")
        print("-----------------------------------------------------------------------")
        print(" [1] Launch AetherVault Server (Auto-Verify Deps + Auto-Port + Browser)")
        print(" [2] Setup / Verify .venv & Core Python Packages + llama-cpp-python")
        print(" [3] Quick-Download Starter, Coder & Gemma 4 Models (1-11)")
        print(" [4] Export / Import Portable Workspace (.ZIP)")
        print(" [5] Stock Offline Vault (Cache .whl + Golden Scripts + Models)")
        print(" [6] Switch Engine Backend (Vulkan GPU vs. 2015 Laptop Safe CPU)")
        print(" [7] Restore Golden Backup (assistant_server.py + ui_studio.html + DB)")
        print(" [8] Check for GitHub OTA Runtime Updates (/update)")
        print(" [9] Run Automated Smoke Suite (tests/smoke.py)")
        print(" [0] Exit (Purges .temp_cache)")
        print("=======================================================================")
        try:
            sel = input("Select an option: ").strip()
        except EOFError:
            break

        if sel == "1":
            if not ensure_runtime_hydrated():
                continue
            vpy = ensure_environment(force_install=False)
            srv = ROOT_DIR / "assistant_server.py"
            if check_python_syntax(srv):
                active_port = find_available_port(SERVER_PORT)
                env = os.environ.copy()
                env["PIP_CACHE_DIR"] = str(ROOT_DIR / "pip_cache")
                env["HF_HOME"] = str(ROOT_DIR / "hf_cache")
                env["PYTHONUNBUFFERED"] = "1"
                env["PYTHONIOENCODING"] = "utf-8"
                env["PYTHONUTF8"] = "1"
                env["AVS_PORT"] = str(active_port)
                threading.Thread(target=_auto_open_browser_when_ready, args=(active_port,), daemon=True).start()
                subprocess.call([str(vpy), "-u", str(srv)], env=env)
        elif sel == "2":
            ensure_environment(force_install=True)
        elif sel == "3":
            for idx, (label, _, _) in enumerate(QUICK_MODELS, 1):
                print(f" [{idx:2d}] {label}")
            print(" [11] Custom Hugging Face Repo + .gguf Filename")
            print(" [ 0] Cancel")
            c = input("Select model (0-11): ").strip()
            if c.isdigit():
                n = int(c)
                if n == 11:
                    r = input("Repo ID: ").strip()
                    f = input("Filename: ").strip()
                    if r and f:
                        download_model_file(r, f)
                elif 1 <= n <= len(QUICK_MODELS):
                    _, r, f = QUICK_MODELS[n - 1]
                    download_model_file(r, f)
        elif sel == "4":
            c = input("[1] Export .ZIP  [2] Import .ZIP  [0] Cancel: ").strip()
            if c == "1":
                export_workspace_zip()
            elif c == "2":
                p = input("Path to .zip: ").strip().strip('"').strip("'")
                import_workspace_zip(Path(p))
        elif sel == "5":
            stock_offline_vault()
        elif sel == "6":
            c = input("[A] Vulkan GPU  [B] Safe CPU: ").strip().lower()
            if c in ("a", "b"):
                install_llama_cpp(ensure_venv(), mode="vulkan" if c == "a" else "cpu")
        elif sel == "7":
            restore_golden_backup()
        elif sel == "8":
            sync_from_github_ota()
        elif sel == "9":
            subprocess.call([sys.executable, str(ROOT_DIR / "tests" / "smoke.py")])
        elif sel == "0":
            cleanup_temp()
            return 0
    cleanup_temp()
    return 0


def main():
    os.chdir(ROOT_DIR)
    snap_info = boot_stock_check()
    if "--boot-check-only" in sys.argv:
        return 0
    force_cli = ("--cli" in sys.argv) or (not sys.stdin.isatty() and not IS_WINDOWS)
    if not force_cli:
        if launch_desktop_gui(snap_info):
            return 0
    return run_cli(snap_info)


if __name__ == "__main__":
    raise SystemExit(main())
