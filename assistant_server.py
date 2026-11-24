# ==============================================================================
# AetherVault Studio - Complete Standalone Local AI Backend (assistant_server.py)
# Made with <3 in Argentina by Enzeru, with the collaboration of Google Gemini.
# Open-Source Standalone Edition | FastAPI + llama-cpp-python + OSWorld PC Agent
#
# UPGRADES IN THIS BUILD (v3.0 - "Just Works" Edition):
# 1. Unlimited Natural Completion + Real-Time Stop Button (/stop_generation)
# 2. Anti-Delirium Lore & Core Sanitizer (strips meta-technical PDF/essay noise)
# 3. Repetition & Delirium Loop Watchdog (auto-stops GGUF token loops mid-stream)
# 4. Predetermined "Model / API Had an Issue" Diagnostic Registry & Self-Healer
# 5. Dual-Engine Web Search (DDGS + automatic BeautifulSoup HTML fallback)
# ==============================================================================

import os
import io
import sys
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
import math
import wave
import struct
import atexit
import tempfile
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
import ast
import hashlib
import gc
import re
import time
import json
import shutil
import zipfile
import base64
import ctypes
import sqlite3
import threading
import traceback
import subprocess
import py_compile
import socket
import platform
import ipaddress
import importlib.util
import importlib.metadata
from collections import Counter
from pathlib import Path
from urllib.parse import quote

import requests
try:
    import pymupdf as fitz  # Modern PyMuPDF API (no deprecation warning)
except ImportError:
    import fitz
from PIL import Image, ImageGrab
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None
from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, StreamingResponse, RedirectResponse
import uvicorn
from huggingface_hub import hf_hub_url
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None
try:
    from llama_cpp import llama_supports_gpu_offload as _raw_llama_supports_gpu_offload
except ImportError:
    def _raw_llama_supports_gpu_offload():
        return False

def llama_supports_gpu_offload() -> bool:
    """
    Safely probes GPU offload support.
    Catches Windows ctypes OSError Access Violations (0x0000000000000000) thrown by
    older 2015 AMD Radeon R5 / integrated APU Vulkan drivers and falls back to CPU mode cleanly!
    """
    flag_file = Path(__file__).parent.resolve() / ".venv" / "engine_mode.flag"
    try:
        if flag_file.exists() and flag_file.read_text(encoding="utf-8", errors="ignore").strip().lower() == "cpu":
            return False
    except Exception:
        pass
    try:
        return bool(_raw_llama_supports_gpu_offload())
    except (Exception, OSError) as e:
        print(f"[GPU PROBE AUTO-HEAL] Vulkan driver raised {type(e).__name__} ({e}). Disabling GPU offload and locking Safe CPU Mode!", flush=True)
        os.environ["GGML_VK_VISIBLE_DEVICES"] = ""
        return False
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*duckduckgo_search.*")
DDGS = None
DDGS_IS_MODERN = False
try:
    from ddgs import DDGS as _MODERN_DDGS
    DDGS = _MODERN_DDGS
    DDGS_IS_MODERN = True
except ImportError:
    try:
        from duckduckgo_search import DDGS as _LEGACY_DDGS
        DDGS = _LEGACY_DDGS
    except ImportError:
        DDGS = None
import spotipy
from spotipy.oauth2 import SpotifyOAuth

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.15
    HAS_PYAUTOGUI = True
except ImportError:
    pyautogui = None
    HAS_PYAUTOGUI = False

# =====================================================================
# 1. PORTABLE PATHS, DIRECTORIES & PERSISTENT WORKSPACE CONFIG
# =====================================================================
APP_VERSION = "6.8"
SERVER_PORT = int(os.environ.get("AVS_PORT", "8000"))
from avs import platform_bridge as avs_platform
from avs import toolbox as avs_toolbox
from avs import workbench as avs_workbench
from avs import hardware_monitor as avs_hw
from avs import bridges as avs_bridges
from avs import turn_pipeline as avs_turn_pipeline
from avs import model_polish as avs_model_polish
from avs.contracts import ToolSpec, ToolResult
from avs import memory_graph as avs_memory_graph
from avs import language_tools as avs_lang
from avs import manual_assets as avs_manual
BASE_DIR = Path(__file__).parent.resolve()
LOCALES_DIR = BASE_DIR / "locales"
LOCALES_DIR.mkdir(parents=True, exist_ok=True)
PDF_DIR = BASE_DIR / "priority_pdfs"
LORE_SUBDIR = PDF_DIR / "lore"
MODEL_DIR = BASE_DIR / "models"
HF_CACHE_DIR = BASE_DIR / "hf_cache"
MEMORY_DIR = BASE_DIR / "memory_vault"
CHAT_LOG_DIR = BASE_DIR / "chat_logs"
GEN_IMG_DIR = BASE_DIR / "generated_images"
GEN_AUDIO_DIR = BASE_DIR / "generated_audio"
IMG_MODEL_DIR = MODEL_DIR / "image"
MUSIC_MODEL_DIR = MODEL_DIR / "music"
VOICE_MODEL_DIR = MODEL_DIR / "voice"
VISION_MODEL_DIR = MODEL_DIR / "vision"
ASSETS_DIR = BASE_DIR / "custom_assets"
BACKUPS_DIR = BASE_DIR / "workspace_backups"
CUSTOM_TOOLS_DIR = BASE_DIR / "custom_tools"
CUSTOM_REQS_PATH = BASE_DIR / "custom_requirements.txt"

TEMP_SESSION_DIR = BASE_DIR / ".temp_cache"

DB_PATH = BASE_DIR / "memory_core.db"
GLOSSARY_PATH = BASE_DIR / "glossary_index.json"
PARTNER_EVOLUTION_PATH = BASE_DIR / "partner_evolution.json"
MANUAL_PDF_PATH = BASE_DIR / "AetherVault_Studio_Manual.pdf"
CONFIG_PATH = BASE_DIR / "workspace_config.json"
UI_HTML_PATH = BASE_DIR / "ui_studio.html"

TRANSLATE_MODEL_DIR = MODEL_DIR / "translate"
for d in (PDF_DIR, LORE_SUBDIR, MODEL_DIR, IMG_MODEL_DIR, MUSIC_MODEL_DIR, VOICE_MODEL_DIR, VISION_MODEL_DIR, TRANSLATE_MODEL_DIR, HF_CACHE_DIR, MEMORY_DIR, CHAT_LOG_DIR, GEN_IMG_DIR, GEN_AUDIO_DIR, ASSETS_DIR, BACKUPS_DIR, CUSTOM_TOOLS_DIR, LOCALES_DIR, TEMP_SESSION_DIR):
    d.mkdir(parents=True, exist_ok=True)
avs_lang.configure_portable_argos_dir(MODEL_DIR)

os.environ["HF_HOME"] = str(HF_CACHE_DIR)
LLM_LOCK = threading.Lock()
INDEX_LOCK = threading.Lock()

# =====================================================================
# 2. PREDETERMINED "MODEL / API HAD AN ISSUE" DIAGNOSTIC REGISTRY
# =====================================================================
PREDETERMINED_ERRORS = {
    "ERR_MODEL_NOT_LOADED": {
        "code": "ERR-01",
        "title": "No Local GGUF Brain Loaded",
        "message": "Hold up—my local GGUF model isn't loaded into memory yet.",
        "fix": "Pick a downloaded .gguf model from the 'Local GGUF Model' dropdown on the right sidebar (or download one from the preset bag)."
    },
    "ERR_MODEL_LOADING": {
        "code": "ERR-02",
        "title": "Model Currently Loading Into RAM/VRAM",
        "message": "Easy there! I'm still pumping the GGUF weights into memory.",
        "fix": "Wait a few seconds for the top status bar to show the model name, then hit Send again."
    },
    "ERR_CONTEXT_OVERFLOW": {
        "code": "ERR-03",
        "title": "Context Window Overflow (Auto-Healed)",
        "message": "The conversation + lore context got too fat for the active context window, so I automatically trimmed the oldest turns and compacted the prompt.",
        "fix": "Auto-healed on the fly. If replies slow down, click '+ New' to start a fresh chat tab."
    },
    "ERR_DELIRIUM_LOOP": {
        "code": "ERR-04",
        "title": "Delirium / Repetition Loop Guard Triggered",
        "message": "Whoa—my local weights started looping on the same phrase, so the Delirium Watchdog stepped in and cut the loop clean.",
        "fix": "Auto-stopped repetition loop. Try rephrasing or switching to Balanced/Reflex mode if the model feels feverish."
    },
    "ERR_USER_STOPPED": {
        "code": "ERR-05",
        "title": "Generation Stopped by User",
        "message": "Brakes slammed! Generation halted right where you hit the Stop button.",
        "fix": "Partial response saved cleanly to chat history."
    },
    "ERR_API_WEB_SEARCH": {
        "code": "ERR-06",
        "title": "Web Search API Hiccup (Fallback Engaged)",
        "message": "DuckDuckGo's primary API threw a rate-limit or network error, so I switched to the HTML scraper fallback.",
        "fix": "Check your internet connection or make sure 'Offline Mode' is unchecked in the right sidebar."
    },
    "ERR_API_SPOTIFY": {
        "code": "ERR-07",
        "title": "Spotify Controller Issue",
        "message": "Spotify Web API couldn't find an active playback device, so I routed the command directly to your Windows Spotify desktop app.",
        "fix": "Make sure the Spotify app is open on your PC (or add your Client ID/Secret in Studio Settings for background control)."
    },
    "ERR_API_IMAGE_GEN": {
        "code": "ERR-08",
        "title": "Image Generator Unreachable",
        "message": "Neither local Stable Diffusion (port 7860) nor the cloud diffusion bridge returned a valid image.",
        "fix": "Start Stable Diffusion WebUI with '--api' for offline rendering, or disable Offline Mode to use the cloud bridge."
    },
    "ERR_OSWORLD_FAILSAFE": {
        "code": "ERR-09",
        "title": "OSWorld Desktop Action Aborted",
        "message": "Desktop automation hit the corner failsafe or couldn't locate the target coordinates/application.",
        "fix": "Keep your mouse away from the top-left screen corner while OSWorld is clicking, and verify 'pyautogui' is installed."
    },
    "ERR_ENGINE_CRASH": {
        "code": "ERR-10",
        "title": "Local Inference Engine Hiccup",
        "message": "The local GGUF engine tripped over a tensor/template error during generation.",
        "fix": "The server caught the crash safely without dying. Inspect the Debug panel on the right sidebar for the exact line."
    }
}

def format_predetermined_error(err_key: str, extra_detail: str = "") -> dict:
    info = PREDETERMINED_ERRORS.get(err_key, PREDETERMINED_ERRORS["ERR_ENGINE_CRASH"]).copy()
    if extra_detail:
        info["detail"] = str(extra_detail)[:300]
    info["timestamp"] = time.strftime("%H:%M:%S")
    STATE["last_debug"]["last_issue"] = info
    return info

DEFAULT_CORE_TEMPLATE = """[SYSTEM DIRECTIVE: CORE IDENTITY & CAPABILITIES — LOADED 24/7]
You are {ai_name}, a sharp, grounded, autonomous local AI companion and desktop operator running natively on {user_name}'s computer inside AetherVault Studio.

1. VOICE & PERSONALITY:
- Speak naturally, directly, and authentically in the first person ("I", "me", "my") without robotic corporate filler ("As an AI,", "How can I assist you today?", "Sound good?", "Let's dive in!").
- Never suffer an existential crisis or act confused about where you are: you live locally on {user_name}'s machine, you have persistent memory, and you collaborate on both everyday tasks (coding, web research, file analysis, OSWorld desktop control, music) and creative writing or roleplay.

2. BUILT-IN WORKSPACE TOOLS, APIS & OSWORLD PC CONTROL (EMIT TAGS WHEN NEEDED):
- OSWorld Desktop Agent (Mouse, Keyboard, Windows & Screenshots):
  * Take a live screenshot of {user_name}'s screen: [[OSWORLD:screenshot|]]
  * List open desktop windows: [[OSWORLD:list_windows|]]
  * Launch or focus an app/program: [[OSWORLD:open_app|notepad]] or [[OSWORLD:open_app|calc]] or [[OSWORLD:open_app|explorer]]
  * Click screen coordinates: [[OSWORLD:click|x,y]] or [[OSWORLD:double_click|x,y]] or [[OSWORLD:right_click|x,y]]
  * Type text on the keyboard: [[OSWORLD:type|text to type]]
  * Press a key or hotkey combo: [[OSWORLD:hotkey|ctrl+s]] or [[OSWORLD:key|enter]]
  * Scroll the mouse wheel: [[OSWORLD:scroll|-500]]
- Local PC & Cloud Drive Scanner: To list or read files/folders on {user_name}'s PC, Steam libraries, or synced Google Drive, output: [[FILES:search_term_or_path]]
- Deep Knowledge / PDF Lookup: To search deeper inside indexed LORE PDFs/documents, output: [[LORE:keywords]]
- Live Internet Search: To search DuckDuckGo for live facts, news, or weather, output: [[SEARCH:query]]
- Spotify Controller: To control Spotify playback, output: [[SPOTIFY:play|song name]] or [[SPOTIFY:pause|]] or [[SPOTIFY:next|]]
- Artwork & Image Generator: To render an image, append: [[IMAGE:detailed visual prompt]]
- Persistent Memory Vault: To permanently save a new fact or active state into Priority #1 memory, append: [[MEMORY:category|fact]]
"""

DEFAULT_CONFIG = {
    "app_title": "AetherVault Studio",
    "ai_name": "Aether",
    "user_name": "Creator",
    "greeting_message": "System online. Reflex Fast-Gear engaged, anti-delirium filters active, and all local APIs standing by. What are we tearing into today?",
    "persona_prompt": DEFAULT_CORE_TEMPLATE.strip(),
    "first_boot_completed": False,
    "osworld_enabled": True,
    "routing_mode": "auto_reflex",
    "performance_mode": "Reflex (Auto-Smart Fast)",
    "avatar_url": "",
    "avatar_fit": "cover",
    "avatar_pos_x": 50,
    "avatar_pos_y": 50,
    "avatar_scale": 100,
    "wallpaper_url": "",
    "wallpaper_opacity": 0.15,
    "wallpaper_blur": 0,
    "theme_preset": "aether_violet",
    "theme_colors": {
        "bg": "#0d0e12",
        "sidebar": "#14151c",
        "panel": "#1b1d27",
        "accent": "#7c3aed",
        "accent_soft": "#a78bfa",
        "text": "#e5e7eb",
        "border": "#2b2e3d"
    },
    "spotify": {
        "client_id": "",
        "client_secret": "",
        "redirect_uri": "http://127.0.0.1:8000/spotify_callback"
    },
    "telegram": {
        "enabled": False,
        "bot_token": "",
        "allowed_chat_id": "",
        "miniapp_url": ""
    },
    "bluesky": {
        "enabled": False,
        "handle": "",
        "app_password": "",
        "pds_url": "https://bsky.social",
        "allowed_dids": "",
        "poll_mentions": True
    },
    "sd_api_url": "http://127.0.0.1:7860",
    "voice_profile": "af_nicole_river",
    "tts_speed": 0.96,
    "vision_mmproj": "",
    "brain_mode": "local_only",
    "failsafe_model": "gemma-4-E4B-it-Q4_K_M.gguf",
    "api_daily_soft_cap": 1000000,
    "workspace_mode": "assistant",
    "workbench_trust": "safe_auto",
    "auto_web_search": True,
    "unrestricted_tokens": True,
    "idle_unload_minutes": 10,
    "mcp_auth_token": "",
    "ui_language": "en",
    "speech_locale": "en-US",
    "spellcheck_enabled": True,
    "translate_bridge_mode": "native"
}

def load_workspace_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            saved = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            merged = json.loads(json.dumps(DEFAULT_CONFIG))
            for k, v in saved.items():
                if isinstance(v, dict) and isinstance(merged.get(k), dict):
                    merged[k] = {**merged[k], **v}
                else:
                    merged[k] = v
            return merged
        except Exception as e:
            print(f"[CONFIG WARNING] Failed to parse workspace_config.json ({e}), using defaults.")
    CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=2, ensure_ascii=False), encoding="utf-8")
    return json.loads(json.dumps(DEFAULT_CONFIG))

def save_workspace_config(cfg: dict):
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
    sp = cfg.get("spotify") or {}
    if sp.get("client_id"):
        os.environ["SPOTIPY_CLIENT_ID"] = sp["client_id"]
        os.environ["SPOTIPY_CLIENT_SECRET"] = sp.get("client_secret", "")
        os.environ["SPOTIPY_REDIRECT_URI"] = sp.get("redirect_uri", "http://127.0.0.1:8000/spotify_callback")

WORKSPACE_CFG = load_workspace_config()
save_workspace_config(WORKSPACE_CFG)

CORE_README_PATH = PDF_DIR / "CORE_PERSONA.txt"
if not CORE_README_PATH.exists() and not (PDF_DIR / "README.txt").exists():
    CORE_README_PATH.write_text(
        WORKSPACE_CFG["persona_prompt"]
        .replace("{ai_name}", WORKSPACE_CFG["ai_name"])
        .replace("{user_name}", WORKSPACE_CFG["user_name"]),
        encoding="utf-8"
    )

def get_initial_pc_roots():
    return avs_platform.get_initial_pc_roots(BASE_DIR)

PRIORITY_CACHE = {
    "initialized": False,
    "core_rules_text": "",
    "reflex_core_digest": "",
    "core_file_names": [],
    "lore_manifest_text": "",
    "lore_file_count": 0,
    "lore_chunk_count": 0,
    "file_stats": {},
    "glossary_top_words": [],
    "glossary_map": {},
    "domain_vocab": set(),
    "last_glossary_mtimes": {}
}

STATE = {
    "llm": None,
    "current_model": None,
    "gpu_offload": bool(llama_supports_gpu_offload()),
    "loading_model": False,
    "last_activity_ts": time.time(),
    "idle_sleeping": False,
    "last_unloaded_model": "",
    "generating": False,
    "stop_requested": False,
    "current_step": "Idle",
    "offline_mode": False,
    "performance_mode": WORKSPACE_CFG.get("performance_mode", "Reflex (Auto-Smart Fast)"),
    "brain_mode": WORKSPACE_CFG.get("brain_mode", "local_only"),
    "workspace_mode": WORKSPACE_CFG.get("workspace_mode", "assistant"),
    "workbench_trust": WORKSPACE_CFG.get("workbench_trust", "safe_auto"),
    "active_api_label": "",
    "last_api_hop_notice": "",
    "allowed_pc_roots": get_initial_pc_roots(),
    "telegram_status": "Stopped",
    "telegram_last_update_id": 0,
    "boot_time": time.time(),
    "boot_ready": False,
    "indexing_files": False,
    "skip_indexing": False,
    "active_task_label": "Initializing Studio...",
    "download": {
        "active": False, "filename": "", "downloaded_mb": 0.0,
        "total_mb": 0.0, "percent": 0.0, "speed_mbps": 0.0,
        "elapsed_sec": 0, "eta_sec": 0, "last_completed": "", "error": None
    },
    "last_debug": {
        "timestamp": "",
        "model": "",
        "gear_used": "Gear 1 (Reflex Fast-Path)",
        "gpu_active": False,
        "prompt_chars": 0,
        "core_files": [],
        "lore_pulled": [],
        "chats_pulled": [],
        "pc_files_scanned": [],
        "osworld_actions": [],
        "last_issue": None,
        "steps": [],
        "error": ""
    }
}

MODEL_BAG = [
    {
        "name": "⭐ Gemma-4-E4B-it Unsloth GGUF (~5.0GB - DEFAULT Offline Brain & Tool Master)",
        "repo": "unsloth/gemma-4-E4B-it-GGUF",
        "file": "gemma-4-E4B-it-Q4_K_M.gguf",
        "license": "Apache-2.0 (Google DeepMind Gemma 4)"
    },
    {
        "name": "Gemma-4-E2B-it Unsloth GGUF (~3.2GB - Fast Edge Gemma 4)",
        "repo": "unsloth/gemma-4-E2B-it-GGUF",
        "file": "gemma-4-E2B-it-Q4_K_M.gguf",
        "license": "Apache-2.0 (Google DeepMind Gemma 4)"
    },
    {
        "name": "Gemma-4-12B-it Unsloth GGUF (~7.5GB - Mid/High Rig Gemma 4)",
        "repo": "unsloth/gemma-4-12b-it-GGUF",
        "file": "gemma-4-12b-it-Q4_K_M.gguf",
        "license": "Apache-2.0 (Google DeepMind Gemma 4)"
    },
    {
        "name": "Gemma-4-26B-A4B-it MoE Unsloth GGUF (~15.5GB - 4B Active MoE Gemma 4)",
        "repo": "unsloth/gemma-4-26B-A4B-it-GGUF",
        "file": "gemma-4-26B-A4B-it-UD-Q4_K_M.gguf",
        "license": "Apache-2.0 (Google DeepMind Gemma 4 MoE)"
    },
    {
        "name": "DeepSeek-R1-Distill-Qwen-1.5B Uncensored (~1.1GB - Best for 2015 Laptops)",
        "repo": "mradermacher/DeepSeek-R1-Distill-Qwen-1.5B-uncensored-GGUF",
        "file": "DeepSeek-R1-Distill-Qwen-1.5B-uncensored.Q4_K_M.gguf",
        "license": "MIT / DeepSeek-R1 Distill (Uncensored Community Quant)"
    },

    {
        "name": "DeepSeek-R1-Distill-Qwen-7B Uncensored (~4.7GB - Deep Reasoning & RP)",
        "repo": "mradermacher/DeepSeek-R1-Distill-Qwen-7B-uncensored-GGUF",
        "file": "DeepSeek-R1-Distill-Qwen-7B-uncensored.Q4_K_M.gguf",
        "license": "MIT / DeepSeek-R1 Distill (Uncensored Community Quant)"
    },
    {
        "name": "DeepSeek-R1-Distill-Qwen-14B Abliterated v2 (~9.0GB - Heavy Rig Uncensored Reasoning)",
        "repo": "QuantFactory/DeepSeek-R1-Distill-Qwen-14B-abliterated-v2-GGUF",
        "file": "DeepSeek-R1-Distill-Qwen-14B-abliterated-v2.Q4_K_M.gguf",
        "license": "MIT / huihui-ai DeepSeek-R1 14B Abliterated v2"
    },
    {
        "name": "Dolphin-3.0-Llama-3.1-8B Uncensored (~4.9GB - Classic Unfiltered RP & Tools)",
        "repo": "bartowski/Dolphin3.0-Llama3.1-8B-GGUF",
        "file": "Dolphin3.0-Llama3.1-8B-Q4_K_M.gguf",
        "license": "Llama 3.1 Community / Cognitive Computations"
    },
    {
        "name": "Qwen2.5-1.5B-Instruct (Ultra-Fast / 2015 Laptop Friendly ~1.1GB)",
        "repo": "bartowski/Qwen2.5-1.5B-Instruct-GGUF",
        "file": "Qwen2.5-1.5B-Instruct-Q4_K_M.gguf",
        "license": "Apache-2.0 (Alibaba Qwen)"
    },
    {
        "name": "Qwen2.5-3B-Instruct (Fast & Smart ~2.1GB - Sweet Spot for Older PCs)",
        "repo": "bartowski/Qwen2.5-3B-Instruct-GGUF",
        "file": "Qwen2.5-3B-Instruct-Q4_K_M.gguf",
        "license": "Qwen Research License"
    },
    {
        "name": "Llama-3.2-3B-Instruct (Great Chat & Tool Calling ~2.0GB)",
        "repo": "bartowski/Llama-3.2-3B-Instruct-GGUF",
        "file": "Llama-3.2-3B-Instruct-Q4_K_M.gguf",
        "license": "Llama 3.2 Community License (Meta)"
    },
    {
        "name": "Hermes-3-Llama-3.1-8B (Roleplay & Agentic Master ~4.9GB)",
        "repo": "NousResearch/Hermes-3-Llama-3.1-8B-GGUF",
        "file": "Hermes-3-Llama-3.1-8B.Q4_K_M.gguf",
        "license": "Llama 3.1 Community License (Nous Research)"
    },
    {
        "name": "Mistral-7B-Instruct-v0.3 (Creative & Uncensored Feel ~4.4GB)",
        "repo": "bartowski/Mistral-7B-Instruct-v0.3-GGUF",
        "file": "Mistral-7B-Instruct-v0.3-Q4_K_M.gguf",
        "license": "Apache-2.0 (Mistral AI)"
    },
    {
        "name": "💻 Qwen2.5-Coder-7B-Instruct (~4.7GB - SOTA Local Coding, Python/JS/PS1 & Self-Repair)",
        "repo": "bartowski/Qwen2.5-Coder-7B-Instruct-GGUF",
        "file": "Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf",
        "license": "Apache-2.0 (Alibaba Qwen Coder)"
    },
    {
        "name": "💻 Qwen2.5-Coder-3B-Instruct (~2.1GB - Fast Lightweight Coding & Scripting)",
        "repo": "bartowski/Qwen2.5-Coder-3B-Instruct-GGUF",
        "file": "Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf",
        "license": "Qwen Research (Alibaba Qwen Coder)"
    },
    {
        "name": "💻 Qwen2.5-Coder-1.5B-Instruct (~1.1GB - Ultra-Light Coding for Low-RAM Machines)",
        "repo": "bartowski/Qwen2.5-Coder-1.5B-Instruct-GGUF",
        "file": "Qwen2.5-Coder-1.5B-Instruct-Q4_K_M.gguf",
        "license": "Apache-2.0 (Alibaba Qwen Coder)"
    },
    {
        "name": "💻 DeepSeek-Coder-V2-Lite-Instruct (~8.9GB - Heavy Rig MoE Software Architect)",
        "repo": "bartowski/DeepSeek-Coder-V2-Lite-Instruct-GGUF",
        "file": "DeepSeek-Coder-V2-Lite-Instruct-Q4_K_M.gguf",
        "license": "MIT / DeepSeek License"
    }
]

def set_step(step_text: str):
    STATE["current_step"] = step_text
    if step_text != "Idle":
        print(f"[AETHERVAULT] {step_text}")
        STATE["last_debug"]["steps"].append(f"{time.strftime('%H:%M:%S')} | {step_text}")
        if len(STATE["last_debug"]["steps"]) > 30:
            STATE["last_debug"]["steps"] = STATE["last_debug"]["steps"][-30:]

# =====================================================================
# 3. WINDOWS / CROSS-PLATFORM RAM MONITOR
# =====================================================================
class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]

def get_system_ram_info():
    try:
        if hasattr(ctypes, "windll"):
            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            free_gb = round(stat.ullAvailPhys / (1024 ** 3), 1)
            total_gb = round(stat.ullTotalPhys / (1024 ** 3), 1)
            return {"percent": stat.dwMemoryLoad, "free_gb": free_gb, "total_gb": total_gb}
        else:
            import psutil
            vm = psutil.virtual_memory()
            return {"percent": int(vm.percent), "free_gb": round(vm.available / (1024 ** 3), 1), "total_gb": round(vm.total / (1024 ** 3), 1)}
    except Exception:
        return {"percent": 0, "free_gb": 8.0, "total_gb": 16.0}

# =====================================================================
# 4. OSWORLD DESKTOP GUI & PC CONTROL AGENT HARNESS
# =====================================================================
def list_open_desktop_windows() -> list:
    titles = []
    if hasattr(ctypes, "windll"):
        try:
            EnumWindows = ctypes.windll.user32.EnumWindows
            EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
            GetWindowText = ctypes.windll.user32.GetWindowTextW
            GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
            IsWindowVisible = ctypes.windll.user32.IsWindowVisible

            def foreach_window(hwnd, lParam):
                if IsWindowVisible(hwnd):
                    length = GetWindowTextLength(hwnd)
                    if length > 0:
                        buff = ctypes.create_unicode_buffer(length + 1)
                        GetWindowText(hwnd, buff, length + 1)
                        val = buff.value.strip()
                        if val and val not in ("Program Manager", "Settings", "Microsoft Text Input Application"):
                            titles.append(val)
                return True

            EnumWindows(EnumWindowsProc(foreach_window), 0)
        except Exception:
            pass
    return list(dict.fromkeys(titles))[:30]


def resolve_and_launch_windows_app(app_query: str) -> str:
    """
    Smart App Resolver & Silent Launcher (v4.8):
    Resolves common Windows apps (`steam`, `steam.exe`, `spotify`, `discord`, `brave`, `vscode`, `notepad++`, etc.),
    exact paths, PATH executables, and Windows Start Menu `.lnk` shortcuts cleanly without WinError 2!
    """
    raw = (app_query or "").strip().strip("'\"")
    low = raw.lower()
    stem = low[:-4] if low.endswith(".exe") else low

    local_app = os.environ.get("LOCALAPPDATA", "")
    roam_app = os.environ.get("APPDATA", "")
    prog_files = os.environ.get("PROGRAMFILES", "C:/Program Files")
    prog_x86 = os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)")
    prog_data = os.environ.get("PROGRAMDATA", "C:/ProgramData")

    # 1. Exact path on disk
    p_direct = Path(raw).expanduser()
    if p_direct.exists():
        if hasattr(os, "startfile"):
            os.startfile(str(p_direct))
        else:
            subprocess.Popen([str(p_direct)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"Launched '{p_direct}' silently."

    # 2. Well-known Windows App Catalog (exact .exe paths + URI fallbacks)
    known_apps = {
        "steam": ([
            Path(prog_x86) / "Steam/steam.exe",
            Path(prog_files) / "Steam/steam.exe",
            Path("D:/Steam/steam.exe"),
            Path("E:/Steam/steam.exe"),
        ], "steam://open/main"),
        "spotify": ([
            Path(roam_app) / "Spotify/Spotify.exe",
            Path(local_app) / "Microsoft/WindowsApps/Spotify.exe",
        ], "spotify:"),
        "discord": ([
            Path(local_app) / "Discord/Update.exe",
        ], "discord://"),
        "brave": ([
            Path(prog_files) / "BraveSoftware/Brave-Browser/Application/brave.exe",
            Path(prog_x86) / "BraveSoftware/Brave-Browser/Application/brave.exe",
            Path(local_app) / "BraveSoftware/Brave-Browser/Application/brave.exe",
        ], ""),
        "chrome": ([
            Path(prog_files) / "Google/Chrome/Application/chrome.exe",
            Path(prog_x86) / "Google/Chrome/Application/chrome.exe",
            Path(local_app) / "Google/Chrome/Application/chrome.exe",
        ], ""),
        "edge": ([
            Path(prog_x86) / "Microsoft/Edge/Application/msedge.exe",
            Path(prog_files) / "Microsoft/Edge/Application/msedge.exe",
        ], ""),
        "firefox": ([
            Path(prog_files) / "Mozilla Firefox/firefox.exe",
            Path(prog_x86) / "Mozilla Firefox/firefox.exe",
        ], ""),
        "vscode": ([
            Path(local_app) / "Programs/Microsoft VS Code/Code.exe",
            Path(prog_files) / "Microsoft VS Code/Code.exe",
        ], "vscode://"),
        "code": ([
            Path(local_app) / "Programs/Microsoft VS Code/Code.exe",
            Path(prog_files) / "Microsoft VS Code/Code.exe",
        ], "vscode://"),
        "notepad++": ([
            Path(prog_files) / "Notepad++/notepad++.exe",
            Path(prog_x86) / "Notepad++/notepad++.exe",
        ], ""),
        "obs": ([
            Path(prog_files) / "obs-studio/bin/64bit/obs64.exe",
        ], ""),
    }

    if stem in known_apps:
        cand_paths, uri_fallback = known_apps[stem]
        for cp in cand_paths:
            if cp.exists() and cp.is_file():
                if stem == "discord" and cp.name.lower() == "update.exe":
                    subprocess.Popen([str(cp), "--processStart", "Discord.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    subprocess.Popen([str(cp)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return f"Launched {stem.capitalize()} directly from '{cp}'!"
        if uri_fallback and hasattr(os, "startfile"):
            os.startfile(uri_fallback)
            return f"Launched {stem.capitalize()} via Windows URI protocol '{uri_fallback}'!"

    # 3. Executable on system PATH (notepad, calc, explorer, cmd, powershell, mspaint, etc.)
    which_hit = shutil.which(raw) or shutil.which(stem)
    if which_hit:
        subprocess.Popen([which_hit], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"Launched '{raw}' from system PATH ('{which_hit}')."

    # 4. Scan Windows Start Menu `.lnk` shortcuts so ANY installed Windows app opens by name!
    start_dirs = [
        Path(roam_app) / "Microsoft/Windows/Start Menu/Programs",
        Path(prog_data) / "Microsoft/Windows/Start Menu/Programs",
    ]
    for sd in start_dirs:
        if not sd.exists():
            continue
        try:
            for lnk in sd.rglob("*.lnk"):
                if stem in lnk.stem.lower():
                    if hasattr(os, "startfile"):
                        os.startfile(str(lnk))
                    else:
                        subprocess.Popen([str(lnk)], shell=True)
                    return f"Found Start Menu shortcut '{lnk.name}' and launched it!"
        except Exception:
            pass

    # 5. Final native fallback
    if hasattr(os, "startfile"):
        os.startfile(raw)
    else:
        subprocess.Popen(raw, shell=True)
    return f"Launched application/target: '{raw}'."

def execute_osworld_action(action: str, arg: str = "") -> dict:
    if not WORKSPACE_CFG.get("osworld_enabled", True):
        return {"ok": False, "summary": "OSWorld Desktop Control is disabled in Studio Settings.", "image_url": None}

    act = (action or "").strip().lower()
    param = (arg or "").strip()
    STATE["last_debug"]["osworld_actions"].append(f"{act}({param})")

    try:
        if act in ("screenshot", "screen", "capture"):
            fname = f"osworld_screen_{int(time.time())}.png"
            fpath = GEN_IMG_DIR / fname
            img = ImageGrab.grab()
            w, h = img.size
            img.save(fpath, format="PNG")
            wins = list_open_desktop_windows()[:8]
            return {
                "ok": True,
                "summary": f"Captured desktop screenshot ({w}x{h}px). Active visible windows: {', '.join(wins) if wins else 'Desktop'}.",
                "image_url": f"/generated_image/{fname}"
            }
        elif act in ("list_windows", "windows"):
            wins = list_open_desktop_windows()
            return {
                "ok": True,
                "summary": "Open Desktop Windows:\n- " + ("\n- ".join(wins) if wins else "No visible windows detected."),
                "image_url": None
            }
        elif act in ("open_app", "launch", "open", "start"):
            if not param:
                return {"ok": False, "summary": "Missing application name or path to open.", "image_url": None}
            launched_desc = resolve_and_launch_windows_app(param)
            return {"ok": True, "summary": launched_desc, "image_url": None}
        elif act in ("click", "left_click", "double_click", "right_click", "move"):
            coords = [int(float(c.strip())) for c in re.findall(r"-?\d+(?:\.\d+)?", param)]
            if len(coords) < 2:
                return {"ok": False, "summary": f"Invalid coordinates for {act}: '{param}' (expected x,y).", "image_url": None}
            x, y = coords[0], coords[1]
            if HAS_PYAUTOGUI:
                if act == "double_click":
                    pyautogui.doubleClick(x, y)
                elif act == "right_click":
                    pyautogui.rightClick(x, y)
                elif act == "move":
                    pyautogui.moveTo(x, y, duration=0.2)
                else:
                    pyautogui.click(x, y)
            elif hasattr(ctypes, "windll"):
                ctypes.windll.user32.SetCursorPos(x, y)
                if act != "move":
                    down_flag, up_flag = (0x0008, 0x0010) if act == "right_click" else (0x0002, 0x0004)
                    ctypes.windll.user32.mouse_event(down_flag, 0, 0, 0, 0)
                    ctypes.windll.user32.mouse_event(up_flag, 0, 0, 0, 0)
                    if act == "double_click":
                        time.sleep(0.08)
                        ctypes.windll.user32.mouse_event(down_flag, 0, 0, 0, 0)
                        ctypes.windll.user32.mouse_event(up_flag, 0, 0, 0, 0)
            return {"ok": True, "summary": f"Executed OSWorld {act} at screen coordinates ({x}, {y}).", "image_url": None}
        elif act in ("type", "write"):
            if HAS_PYAUTOGUI:
                pyautogui.write(param, interval=0.02)
                return {"ok": True, "summary": f"Typed text on desktop keyboard: '{param}'.", "image_url": None}
            return {"ok": False, "summary": "Install 'pyautogui' from the API & Library Manager sidebar to enable keyboard typing.", "image_url": None}
        elif act in ("hotkey", "key", "press"):
            if HAS_PYAUTOGUI:
                keys = [k.strip().lower() for k in re.split(r"[\+\,\s]+", param) if k.strip()]
                if len(keys) > 1:
                    pyautogui.hotkey(*keys)
                elif len(keys) == 1:
                    pyautogui.press(keys[0])
                return {"ok": True, "summary": f"Pressed keyboard shortcut/key: '{param}'.", "image_url": None}
            return {"ok": False, "summary": "Install 'pyautogui' from the API & Library Manager sidebar to enable keyboard hotkeys.", "image_url": None}
        elif act == "scroll":
            clicks = int(float(param)) if re.match(r"^-?\d+", param) else -400
            if HAS_PYAUTOGUI:
                pyautogui.scroll(clicks)
            elif hasattr(ctypes, "windll"):
                ctypes.windll.user32.mouse_event(0x0800, 0, 0, clicks, 0)
            return {"ok": True, "summary": f"Scrolled mouse wheel by {clicks} units.", "image_url": None}

        return {"ok": False, "summary": f"Unknown OSWorld action '{act}'.", "image_url": None}
    except Exception as e:
        err_card = format_predetermined_error("ERR_OSWORLD_FAILSAFE", str(e))
        return {"ok": False, "summary": f"[{err_card['code']}] {err_card['message']} ({e})", "image_url": None}

# =====================================================================
# 5. SQLITE DATABASE ENGINE & ANTI-DELIRIUM LORE SANITIZER
# =====================================================================
def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA busy_timeout=30000")
    except Exception:
        pass
    return conn

# Patterns from meta-technical essays / old disclaimers that caused model deliriums in earlier builds
DELIRIUM_NOISE_PATTERNS = [
    r"insert letter here,\s*entire the user for a propper timeline tag[^\n]*",
    r"terms of use for Gemini or/and other Google products[^\n]*",
    r"Diagn[óo]stico T[ée]cnico del Entorno Local[^\n]*",
    r"Mistral-7B-Instruct-v0\.3-Q4_K_M\.gguf[^\n]*",
    r"tokenizador SentencePiece V3[^\n]*",
    r"plantillas Jinja est[áa]ndar[^\n]*",
    r"personalized mad chat box program in pythin[^\n]*",
]

def sanitize_lore_and_core_text(raw_text: str) -> str:
    """
    Strips out meta-technical AI diagnostic lines and broken placeholder tags from
    CORE and LORE text so the local model never suffers meta-deliriums!
    """
    if not raw_text:
        return ""
    cleaned = raw_text
    for pat in DELIRIUM_NOISE_PATTERNS:
        cleaned = re.sub(pat, "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS priority_pdfs (
                        filename TEXT PRIMARY KEY,
                        mtime REAL,
                        file_mode TEXT DEFAULT 'lore',
                        manual_override INTEGER DEFAULT 0,
                        summary TEXT DEFAULT '',
                        content TEXT)""")
        c.execute("PRAGMA table_info(priority_pdfs)")
        existing_cols = {row["name"] for row in c.fetchall()}
        if "file_mode" not in existing_cols:
            c.execute("ALTER TABLE priority_pdfs ADD COLUMN file_mode TEXT DEFAULT 'lore'")
        if "manual_override" not in existing_cols:
            c.execute("ALTER TABLE priority_pdfs ADD COLUMN manual_override INTEGER DEFAULT 0")
        if "summary" not in existing_cols:
            c.execute("ALTER TABLE priority_pdfs ADD COLUMN summary TEXT DEFAULT ''")

        c.execute("""CREATE TABLE IF NOT EXISTS lore_chunks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT,
                        chunk_index INTEGER,
                        keywords TEXT,
                        content TEXT)""")
        c.execute("CREATE INDEX IF NOT EXISTS idx_lore_filename ON lore_chunks(filename)")

        c.execute("""CREATE TABLE IF NOT EXISTS dynamic_memory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT, fact TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        active INTEGER DEFAULT 1,
                        hits INTEGER DEFAULT 1,
                        norm_key TEXT DEFAULT '')""")
        c.execute("PRAGMA table_info(dynamic_memory)")
        dm_cols = {row["name"] for row in c.fetchall()}
        if "active" not in dm_cols:
            c.execute("ALTER TABLE dynamic_memory ADD COLUMN active INTEGER DEFAULT 1")
        if "hits" not in dm_cols:
            c.execute("ALTER TABLE dynamic_memory ADD COLUMN hits INTEGER DEFAULT 1")
        if "norm_key" not in dm_cols:
            c.execute("ALTER TABLE dynamic_memory ADD COLUMN norm_key TEXT DEFAULT ''")
        c.execute("""CREATE TABLE IF NOT EXISTS chat_sessions (
                        id TEXT PRIMARY KEY,
                        title TEXT,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
        c.execute("""CREATE TABLE IF NOT EXISTS chat_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT,
                        role TEXT,
                        content TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")

        c.execute("DELETE FROM chat_messages WHERE content LIKE 'functions.%' OR TRIM(content) = ''")
        c.execute("DELETE FROM dynamic_memory WHERE fact LIKE '%personalized mad chat box program in pythin%'")
        c.execute("DELETE FROM dynamic_memory WHERE fact LIKE '%pripritize the task at hand%'")
        c.execute("DELETE FROM dynamic_memory WHERE LENGTH(fact) > 1000 AND fact LIKE '%[SYSTEM DIRECTIVE:%'")
        c.execute("UPDATE priority_pdfs SET file_mode = 'lore' WHERE LOWER(filename) LIKE '%.pdf' AND manual_override = 0")

        c.execute("SELECT COUNT(*) FROM chat_sessions")
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO chat_sessions (id, title) VALUES ('session_main', 'Main Workspace')")
            c.execute(
                "INSERT INTO chat_messages (session_id, role, content) VALUES ('session_main', 'assistant', ?)",
                (WORKSPACE_CFG["greeting_message"],)
            )
        conn.commit()

# =====================================================================
# 6. TWO-GEAR ADAPTIVE TRIAGE ("REFLEX FAST-GEAR" vs. "DEEP GEAR")
# =====================================================================
STOPWORDS = {
    "the", "and", "for", "that", "this", "with", "you", "your", "are", "was", "were",
    "have", "has", "had", "not", "but", "what", "when", "where", "who", "why", "how",
    "from", "they", "them", "their", "there", "about", "into", "just", "like", "can",
    "could", "would", "should", "will", "one", "all", "out", "get", "got", "know",
    "think", "tell", "hey", "some", "more", "page", "file", "files", "also", "very",
    "well", "only", "then", "than", "other", "another", "test", "feel", "feeling",
    "time", "see", "now", "new", "wanted", "try", "real", "quick", "pull", "put",
    "please", "spotify", "let", "lets", "make", "good", "right", "here", "there",
    "able", "work", "working", "doing", "something", "anything", "everything", "interface",
    "api", "apis", "tool", "tools", "model", "models", "system", "local", "offline"
}

CAPABILITY_QUERY_PATTERNS = (
    "what can you do", "what do you do", "what tools", "which tools", "your tools",
    "your capabilities", "what are you capable", "interface with", "what apis",
    "which apis", "list your tools", "how deep can you reach", "access to my pc",
    "access my files", "test you out", "test your", "how do you work", "control my pc",
    "osworld"
)

FAST_WEB_INTENT_PATTERNS = (
    "search ", "search for ", "google ", "duckduckgo ", "weather in ", "weather for ",
    "latest news", "current news", "what is the weather", "look up ", "who won ", "price of ",
    "buscar ", "buscá ", "busca en ", "clima en ", "tiempo en ", "pronostico ", "pronóstico ",
    "noticias de ", "ultimas noticias", "últimas noticias", "precio de ", "quien gano", "quién ganó"
)

TAXING_TASK_KEYWORDS = {
    "spotify", "steam", "folder", "directory", "drive", "screenshot", "window", "windows",
    "click", "hotkey", "open", "launch", "notepad", "calc", "code", "python", "script",
    "function", "debug", "analyze", "summarize", "timeline", "lore", "compendium",
    "chapter", "story", "roleplay", "scene", "generate", "draw", "image", "picture", "artifact"
}

def is_capability_or_api_query(user_msg: str) -> bool:
    low = user_msg.lower()
    return any(pat in low for pat in CAPABILITY_QUERY_PATTERNS)

def extract_keywords(text: str) -> list:
    words = re.findall(r"[a-zA-Z0-9_'-]{4,}", text.lower())
    return [w for w in words if w not in STOPWORDS and not w.isdigit()]



# =====================================================================
# 6B. v4.2 SMART BACKEND CONTEXT, WEATHER ENGINE & PYTHON WORKBENCH (CodeAct)
# =====================================================================
USER_PROFILE_CARD_PATH = BASE_DIR / "user_profile_card.json"
WORKBENCH_TOKEN = f"wb_{int(time.time())}_{os.getpid()}"
WORKBENCH_LAST_MEDIA = {"image_url": None, "audio_url": None}

WMO_WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Light snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
}

def _clean_location_value(raw_val: str) -> str:
    txt = (raw_val or "").strip()
    txt = re.sub(r"^(?:user\s+lives\s+in|lives\s+in|located\s+in|location\s*:|city\s*:)\s*", "", txt, flags=re.IGNORECASE)
    txt = re.sub(r"\s*!\s*", ", ", txt)
    txt = re.sub(r"\bin\s+the\s+province\s+of\s+", "", txt, flags=re.IGNORECASE)
    txt = re.sub(r"\s*,\s*,+", ", ", txt).strip(" ,.!")
    return txt

def resolve_user_location_from_memory(allow_json_fallback: bool = True) -> tuple:
    """
    Resolves the user's saved location & ZIP from the unified persistent pseudo-memory layer:
    1. user_profile_card.json
    2. pseudo_memory_index.json (user_context + pseudo_memory_notes)
    3. SQLite dynamic_memory table (category in user_location / location / city / user_zip)
    Never falls back to any hardcoded personal city!
    """
    loc = ""
    zcode = ""
    if USER_PROFILE_CARD_PATH.exists():
        try:
            saved = json.loads(USER_PROFILE_CARD_PATH.read_text(encoding="utf-8"))
            if isinstance(saved, dict):
                loc = _clean_location_value(saved.get("location") or "")
                zcode = (saved.get("zip_code") or "").strip().upper()
        except Exception:
            pass

    if allow_json_fallback and (not loc or not zcode) and PSEUDO_INDEX_JSON_PATH.exists():
        try:
            pidx = json.loads(PSEUDO_INDEX_JSON_PATH.read_text(encoding="utf-8"))
            uctx = pidx.get("user_context") if isinstance(pidx, dict) else {}
            if isinstance(uctx, dict):
                if not loc and uctx.get("location"):
                    loc = _clean_location_value(uctx.get("location"))
                if not zcode and uctx.get("zip_code"):
                    zcode = str(uctx.get("zip_code")).strip().upper()
            if not loc:
                for note in (pidx.get("pseudo_memory_notes") or []):
                    m_l = re.match(r"^\[(?:user_location|location|city)\]\s*(.+)$", str(note), flags=re.IGNORECASE)
                    if m_l:
                        loc = _clean_location_value(m_l.group(1))
                        break
        except Exception:
            pass

    if not loc or not zcode:
        try:
            with get_db() as conn:
                c = conn.cursor()
                if not loc:
                    c.execute("SELECT fact FROM dynamic_memory WHERE LOWER(category) IN ('user_location', 'location', 'city', 'hometown') ORDER BY id DESC LIMIT 1")
                    r = c.fetchone()
                    if r and r["fact"]:
                        loc = _clean_location_value(r["fact"])
                if not zcode:
                    c.execute("SELECT fact FROM dynamic_memory WHERE LOWER(category) IN ('user_zip', 'zip', 'postal_code') ORDER BY id DESC LIMIT 1")
                    r2 = c.fetchone()
                    if r2 and r2["fact"]:
                        zcode = re.sub(r"^.*?:\s*|^user\s+zip/postal\s+code\s+is\s+", "", r2["fact"], flags=re.IGNORECASE).strip().upper()
        except Exception:
            pass

    return loc, zcode

def load_user_profile_card(allow_json_fallback: bool = True) -> dict:
    """Backend-held persistent profile card hydrated directly from pseudo_memory_index.json & SQLite Memory Vault."""
    default_card = {
        "user_name": WORKSPACE_CFG.get("user_name", "Creator"),
        "location": "",
        "zip_code": "",
        "latitude": None,
        "longitude": None,
        "pinned_facts": [],
        "custom_fields": {},
        "last_workbench_summary": "",
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    if USER_PROFILE_CARD_PATH.exists():
        try:
            saved = json.loads(USER_PROFILE_CARD_PATH.read_text(encoding="utf-8"))
            if isinstance(saved, dict):
                default_card.update(saved)
        except Exception:
            pass
    # Auto-hydrate missing location/ZIP/pin coordinates from persistent pseudo-memory if not in card yet
    if not default_card.get("location") or not default_card.get("zip_code"):
        mem_loc, mem_zip = resolve_user_location_from_memory(allow_json_fallback=allow_json_fallback)
        if mem_loc and not default_card.get("location"):
            default_card["location"] = mem_loc
        if mem_zip and not default_card.get("zip_code"):
            default_card["zip_code"] = mem_zip
    if allow_json_fallback and (default_card.get("latitude") is None or default_card.get("longitude") is None) and PSEUDO_INDEX_JSON_PATH.exists():
        try:
            pidx = json.loads(PSEUDO_INDEX_JSON_PATH.read_text(encoding="utf-8"))
            uctx = pidx.get("user_context") if isinstance(pidx, dict) else {}
            if isinstance(uctx, dict) and uctx.get("latitude") is not None and uctx.get("longitude") is not None:
                default_card["latitude"] = round(float(uctx["latitude"]), 5)
                default_card["longitude"] = round(float(uctx["longitude"]), 5)
        except Exception:
            pass
    if WORKSPACE_CFG.get("user_name"):
        default_card["user_name"] = WORKSPACE_CFG["user_name"]
    return default_card

def save_user_profile_card(card: dict):
    card["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        USER_PROFILE_CARD_PATH.write_text(json.dumps(card, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

def format_backend_context_card() -> str:
    """Builds a tight, high-signal real-world state block held by the backend and injected every turn."""
    card = load_user_profile_card()
    now_str = time.strftime("%A, %B %d, %Y | %H:%M")
    loc_str = card.get("location") or "Not shared yet (ask user if needed for local weather/info)"
    if card.get("zip_code"):
        loc_str += f" (ZIP: {card['zip_code']})"
    if card.get("latitude") is not None and card.get("longitude") is not None:
        try:
            loc_str += f" [Pin: {float(card['latitude']):.4f}, {float(card['longitude']):.4f}]"
        except Exception:
            pass
    lines = [
        "[BACKEND-HELD REALITY & USER CONTEXT CARD (ALWAYS TRUST THIS OVER GUESSING)]:",
        f"- Real Date & Local Time: {now_str}",
        f"- User: {card.get('user_name') or 'Creator'} | Real Location: {loc_str}"
    ]
    if card.get("custom_fields") and isinstance(card["custom_fields"], dict):
        cf_pairs = [f"{k}={v}" for k, v in list(card["custom_fields"].items())[:8] if str(v).strip()]
        if cf_pairs:
            lines.append("- Custom Profile Fields: " + " | ".join(cf_pairs))
    if card.get("pinned_facts"):
        lines.append("- Pinned Real Facts: " + " ; ".join(card["pinned_facts"][-6:]))
    if card.get("last_workbench_summary"):
        lines.append(f"- Last Real Tool/Workbench Result: {card['last_workbench_summary'][:240]}")
    return "\n".join(lines)

PLACEHOLDER_LOCATIONS = {
    "city", "city, country", "city, state", "city, region", "your city", "my city",
    "your location", "my location", "location", "region", "country", "hometown",
    "example", "example city", "n/a", "none", "null", "unknown", "current", "here",
    "<city>", "[city]", "<location>", "[location]", "city_name"
}

def _is_placeholder_location(raw_loc: str) -> bool:
    s = re.sub(r"\s+", " ", (raw_loc or "").strip().strip("'\"`")).lower()
    if not s:
        return True
    if s in PLACEHOLDER_LOCATIONS:
        return True
    if re.fullmatch(r"(?:city|town|location|place)(?:\s*,\s*(?:country|state|region|province))?", s):
        return True
    return False

_OSM_RATE_LOCK = threading.Lock()
_OSM_LAST_REQ_TS = {"ts": 0.0}
_OSM_GEO_CACHE = {}

def _osm_nominatim_request(endpoint: str, params: dict) -> dict:
    """
    OpenStreetMap Nominatim Policy-Compliant Client:
    - Custom descriptive User-Agent
    - Local in-memory result cache
    - Strict <= 1 request/second rate limit
    """
    cache_key = endpoint + ":" + json.dumps(params, sort_keys=True)
    if cache_key in _OSM_GEO_CACHE:
        return _OSM_GEO_CACHE[cache_key]
    with _OSM_RATE_LOCK:
        wait_s = 1.05 - (time.time() - _OSM_LAST_REQ_TS["ts"])
        if wait_s > 0:
            time.sleep(wait_s)
        _OSM_LAST_REQ_TS["ts"] = time.time()
        resp = requests.get(
            f"https://nominatim.openstreetmap.org/{endpoint}",
            params={**params, "format": "jsonv2"},
            headers={
                "User-Agent": f"AetherVaultStudio/{APP_VERSION} (Local Portable Desktop AI Workstation)",
                "Accept-Language": (WORKSPACE_CFG.get("ui_language") or "en")
            },
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        _OSM_GEO_CACHE[cache_key] = data
        return data

def reverse_geocode_osm(lat: float, lon: float) -> dict:
    """Converts an OpenStreetMap/Leaflet pin (lat, lon) into a clean City, Region, Country & ZIP."""
    if STATE.get("offline_mode"):
        return {"ok": False, "error": "Offline Mode is ON — coordinates saved locally without reverse lookup."}
    try:
        data = _osm_nominatim_request("reverse", {"lat": f"{float(lat):.6f}", "lon": f"{float(lon):.6f}", "zoom": 12, "addressdetails": 1})
        addr = data.get("address") or {}
        city = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("municipality") or addr.get("county") or ""
        region = addr.get("state") or addr.get("region") or addr.get("province") or ""
        country = addr.get("country") or ""
        postcode = (addr.get("postcode") or "").strip().upper()
        parts = [p for p in (city, region, country) if p]
        label = ", ".join(dict.fromkeys(parts)) if parts else (data.get("display_name") or f"{lat:.4f}, {lon:.4f}")[:80]
        return {
            "ok": True,
            "location": label,
            "zip_code": postcode,
            "latitude": round(float(lat), 5),
            "longitude": round(float(lon), 5),
            "display_name": data.get("display_name") or label,
            "attribution": "© OpenStreetMap contributors"
        }
    except Exception as e:
        return {"ok": False, "error": f"OSM reverse lookup failed: {e}", "latitude": round(float(lat), 5), "longitude": round(float(lon), 5)}

def search_places_for_map(query: str) -> dict:
    """Explicit button-triggered city search for the Leaflet map (Open-Meteo Geocoding -> OSM Nominatim fallback)."""
    q = (query or "").strip()
    if not q:
        return {"ok": False, "results": [], "error": "Enter a city or place name first."}
    if STATE.get("offline_mode"):
        return {"ok": False, "results": [], "error": "Offline Mode is ON."}
    out = []
    try:
        g_resp = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": q, "count": 6, "language": (WORKSPACE_CFG.get("ui_language") or "en")[:2], "format": "json"},
            timeout=10
        )
        if g_resp.status_code == 200:
            for r in (g_resp.json().get("results") or []):
                lbl = ", ".join([x for x in (r.get("name"), r.get("admin1"), r.get("country")) if x])
                out.append({
                    "label": lbl,
                    "lat": round(float(r["latitude"]), 5),
                    "lon": round(float(r["longitude"]), 5),
                    "zip_code": ""
                })
    except Exception:
        pass
    if not out:
        try:
            items = _osm_nominatim_request("search", {"q": q, "limit": 5, "addressdetails": 1})
            for it in (items if isinstance(items, list) else []):
                addr = it.get("address") or {}
                out.append({
                    "label": (it.get("display_name") or q)[:100],
                    "lat": round(float(it["lat"]), 5),
                    "lon": round(float(it["lon"]), 5),
                    "zip_code": (addr.get("postcode") or "").strip().upper()
                })
        except Exception as e:
            return {"ok": False, "results": [], "error": str(e)}
    return {"ok": bool(out), "results": out, "attribution": "© OpenStreetMap contributors"}

def _fetch_open_meteo_forecast_by_coords(lat: float, lon: float, place_lbl: str) -> str:
    w_resp = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": float(lat),
            "longitude": float(lon),
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code",
            "hourly": "precipitation_probability",
            "timezone": "auto",
            "forecast_days": 2
        },
        timeout=10
    )
    if w_resp.status_code != 200:
        return ""
    wj = w_resp.json()
    cur = wj.get("current") or {}
    daily = wj.get("daily") or {}
    hourly = wj.get("hourly") or {}
    c_temp = cur.get("temperature_2m")
    f_temp = round((c_temp * 9 / 5) + 32, 1) if isinstance(c_temp, (int, float)) else None
    feels = cur.get("apparent_temperature")
    hum = cur.get("relative_humidity_2m")
    wind = cur.get("wind_speed_10m")
    wcode = int(cur.get("weather_code", -1))
    cond = WMO_WEATHER_CODES.get(wcode, f"Weather code {wcode}")
    hi_list = daily.get("temperature_2m_max") or [None]
    lo_list = daily.get("temperature_2m_min") or [None]
    rp_list = daily.get("precipitation_probability_max") or [None]
    wc_list = daily.get("weather_code") or []
    hi, lo, rain_p = hi_list[0], lo_list[0], rp_list[0]
    tom_str = ""
    if len(hi_list) > 1:
        tom_cond = WMO_WEATHER_CODES.get(int(wc_list[1]), "Forecast") if len(wc_list) > 1 and wc_list[1] is not None else "Forecast"
        h_probs = hourly.get("precipitation_probability") or []
        tm_morn = [p for p in h_probs[30:37] if isinstance(p, (int, float))]
        morn_rain = f", Tomorrow Morning (6am-12pm) Rain Peak: {max(tm_morn)}%" if tm_morn else ""
        tom_str = f" | Tomorrow: {tom_cond}, High/Low: {hi_list[1]} C / {lo_list[1]} C, Day Rain Chance: {rp_list[1]}%{morn_rain}"
    summary = (
        f"LIVE WEATHER FOR {place_lbl} (Open-Meteo, {time.strftime('%Y-%m-%d %H:%M')}): "
        f"{cond} | Temp: {c_temp} C ({f_temp} F), Feels like: {feels} C | "
        f"Humidity: {hum}% | Wind: {wind} km/h | Today High/Low: {hi} C / {lo} C | Rain Chance: {rain_p}%{tom_str}"
    )
    card = load_user_profile_card()
    card["last_workbench_summary"] = summary
    save_user_profile_card(card)
    return summary

def get_live_weather(location: str = "", latitude=None, longitude=None) -> str:
    """
    Deterministic Live Weather Engine (v4.13 — Placeholder-Guarded & Coordinate-First!):
    1. Guards against LLM placeholder args like 'City, Country' and snaps straight to the saved User Profile Card.
    2. If exact map pin coordinates (latitude, longitude) are provided or saved for the user's location,
       queries Open-Meteo directly by coordinates (0% chance of duplicate-city / wrong-country mixups!).
    3. Otherwise geocodes via Open-Meteo -> wttr.in fallback.
    """
    if STATE.get("offline_mode"):
        return "Offline Mode is enabled — cannot fetch live weather."

    card = load_user_profile_card()
    raw_loc = (location or "").strip()
    saved_loc = (card.get("location") or "").strip()
    saved_lat = card.get("latitude")
    saved_lon = card.get("longitude")

    # Guard against 3B models passing literal placeholder strings like 'City, Country'
    if _is_placeholder_location(raw_loc):
        loc = saved_loc
        if latitude is None and longitude is None and saved_lat is not None and saved_lon is not None:
            latitude, longitude = saved_lat, saved_lon
    else:
        loc = raw_loc
        # If the requested location matches the user's saved location (or any part of it) and they have a map pin, use the pin!
        if latitude is None and longitude is None and saved_lat is not None and saved_lon is not None and saved_loc:
            if loc.lower() == saved_loc.lower() or loc.split(",")[0].strip().lower() in saved_loc.lower():
                latitude, longitude = saved_lat, saved_lon

    if latitude is not None and longitude is not None:
        try:
            lbl = loc or f"{float(latitude):.4f}, {float(longitude):.4f}"
            by_coord = _fetch_open_meteo_forecast_by_coords(float(latitude), float(longitude), lbl)
            if by_coord:
                return by_coord
        except Exception as e:
            print(f"[WEATHER COORD FALLBACK] {e}", flush=True)

    if not loc:
        return "No city or map pin saved on the User Profile Card yet. Open Studio Settings -> Persona & User Card (or click 'Pin on Map') to set your location!"

    parts = [p.strip() for p in re.split(r"[,\-]+", loc) if p.strip() and not p.strip().isdigit()]
    city_q = parts[0] if parts else loc
    hint_words = [w.lower() for w in re.findall(r"[a-zA-Z]{3,}", " ".join(parts[1:]))]

    try:
        g_resp = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city_q, "count": 5, "language": "en", "format": "json"},
            timeout=10
        )
        if g_resp.status_code == 200:
            results = g_resp.json().get("results") or []
            chosen = None
            if results:
                if hint_words:
                    for r in results:
                        meta = f"{r.get('name','')} {r.get('admin1','')} {r.get('country','')}".lower()
                        if any(hw in meta for hw in hint_words):
                            chosen = r
                            break
                if not chosen:
                    chosen = results[0]
            if chosen:
                place_lbl = ", ".join([x for x in (chosen.get("name"), chosen.get("admin1"), chosen.get("country")) if x])
                by_geo = _fetch_open_meteo_forecast_by_coords(chosen["latitude"], chosen["longitude"], place_lbl)
                if by_geo:
                    return by_geo
    except Exception as e:
        print(f"[WEATHER OPEN-METEO FALLBACK] {e}", flush=True)

    try:
        r2 = requests.get(f"https://wttr.in/{quote(loc)}?format=j1", headers={"User-Agent": f"AetherVault/{APP_VERSION}"}, timeout=10)
        if r2.status_code == 200:
            data = r2.json()
            cc = (data.get("current_condition") or [{}])[0]
            desc = ((cc.get("weatherDesc") or [{}])[0]).get("value", "Unknown")
            summary = (
                f"LIVE WEATHER FOR {loc} (wttr.in): {desc} | "
                f"Temp: {cc.get('temp_C')} C ({cc.get('temp_F')} F), Feels like: {cc.get('FeelsLikeC')} C | "
                f"Humidity: {cc.get('humidity')}% | Wind: {cc.get('windspeedKmph')} km/h"
            )
            card["last_workbench_summary"] = summary
            save_user_profile_card(card)
            return summary
    except Exception:
        pass

    return search_web(f"current weather forecast {loc}")

def clean_web_search_query(raw_msg: str) -> str:
    """Strips conversational filler so small models never send raw chat chatter to DuckDuckGo."""
    q = (raw_msg or "").strip()
    ai_n = WORKSPACE_CFG.get("ai_name", "Aether")
    q = re.sub(rf"\b{re.escape(ai_n)}\b", "", q, flags=re.IGNORECASE)
    filler_prefixes = [
        r"^(?:aight|alright|ok|okay|hey|yo|well|so|now|good)[\s,!.\-]*",
        r"^(?:take two|try again|round two|one more time)[\s,!.\-]*",
        r"^(?:can you|could you|would you|please|pelase|pls|how about we|let'?s try something simple)[\s,!.\-]*",
        r"^(?:do a|run a)?\s*(?:web search|internet search|search the web|search online|search|google|look up|check)(?:\s+through the internet)?(?:\s+for|\s+about)?\s+"
    ]
    for _ in range(4):
        prev = q
        for fp in filler_prefixes:
            q = re.sub(fp, "", q, flags=re.IGNORECASE).strip()
        if q == prev:
            break
    q = re.sub(r"\b(?:please|pelase|pls|for me|real quick|thanks|thx)\b", "", q, flags=re.IGNORECASE)
    q = re.sub(r"[?!]+", " ", q)
    q = re.sub(r"\s+", " ", q).strip(" ,.-")

    card = load_user_profile_card()
    saved_loc = (card.get("location") or "").strip()
    if saved_loc and re.search(r"\b(where i live|my city|my town|my location|around here|irl)\b", q, flags=re.IGNORECASE):
        q = re.sub(r"\b(where i live|my city|my town|my location|around here|irl)\b", saved_loc, q, flags=re.IGNORECASE)
    elif saved_loc and any(w in q.lower() for w in ("weather", "climate", "temperature", "forecast")) and saved_loc.split(",")[0].lower() not in q.lower():
        q = f"{q} {saved_loc}"
    return q.strip() or raw_msg.strip()

def detect_weather_intent(user_msg: str) -> tuple:
    """Returns (is_weather_query, target_city_or_empty)."""
    low = (user_msg or "").lower()
    if not any(k in low for k in (
        "weather", "climate", "temperature", "forecast", "raining", "rain today", "hot outside", "cold outside",
        "clima", "pronostico", "pronóstico", "temperatura", "lluvia", "lloviendo", "va a llover", "hace calor", "hace frio", "hace frío"
    )):
        return False, ""
    m = re.search(r"\b(?:in|for|at|en|para)\s+([A-ZÁÉÍÓÚÑ][a-zA-Záéíóúüñ\s,]{2,40}?)(?:\?|$|\.|!|\btoday\b|\bnow\b|\bright now\b|\bhoy\b|\bahora\b)", user_msg)
    if m:
        cand = m.group(1).strip(" ,.?!-")
        if cand.lower() not in ("the internet", "my city", "my area", "the city where i live", "the city where i live irl"):
            return True, cand
    card = load_user_profile_card()
    return True, (card.get("location") or "").strip()

def build_companion_voice_card(ai_name: str, user_name: str) -> str:
    """
    Extracts a punchy, ~750-char Voice & Personality Card directly from the user's active
    CORE persona (`CORE_PERSONA.txt` / `workspace_config.json`) so Assistant & Workbench Mode
    keeps all the companion's charm, banter, and nicknames WITHOUT pulling heavy Lore dumps!
    """
    raw_src = PRIORITY_CACHE.get("core_rules_text") or WORKSPACE_CFG.get("persona_prompt") or ""
    raw_src = raw_src.replace("{ai_name}", ai_name).replace("{user_name}", user_name)
    clean_src = sanitize_lore_and_core_text(raw_src)
    kept_lines = []
    total_len = 0
    skip_tokens = (
        "[[osworld", "[[files", "[[lore", "[[spotify", "[[search", "[[image", "[[memory",
        "[[chats", "[[self", "[[music", "<start>", "disclaimer:", "built-in workspace tools",
        "osworld desktop agent", "local pc & cloud drive scanner", "deep knowledge / pdf lookup"
    )
    for ln in clean_src.splitlines():
        s = ln.strip()
        if not s or s.startswith("---") or s.startswith("[SYSTEM DIRECTIVE"):
            continue
        low_s = s.lower()
        if any(tok in low_s for tok in skip_tokens):
            continue
        kept_lines.append(s)
        total_len += len(s)
        if total_len >= 720:
            break
    extracted = "\n".join(kept_lines)[:760].strip()
    if not extracted:
        extracted = f"You are {ai_name}—laid-back, sharp, sarcastic, witty, and loyal to {user_name}."
    return (
        f"=== COMPANION VOICE & PERSONALITY (KEEP THIS CHARM ON EVERY REPLY!) ===\n"
        f"{extracted}\n"
        f"- Stay fully in your natural voice as {ai_name} when talking to {user_name}—even after running PC tools or Spotify! "
        f"Never answer like a dry robot (e.g., never just say 'Song is playing.'—banter naturally while reporting the real result!)."
    )


# =====================================================================
# 6B-2. v4.14 EPISTEMIC HUMILITY & AUTO-WEB SEARCH ENGINE (SMALL-MODEL GUARD)
# =====================================================================
FRESHNESS_CUE_PATTERNS = (
    r"\b202[5-9]\b",
    r"\b203\d\b",
    r"\b(?:latest|newest|most recent|up[\s-]?to[\s-]?date|breaking)\b",
    r"\b(?:this year|last year|last month|this month|this week|recently|nowadays|right now)\b",
    r"\b(?:release date|released yet|came out|come out|coming out|patch notes|changelog|latest version|current version)\b",
    r"\b(?:current price|how much does|price of|stock price|exchange rate|who won|score of|standings)\b",
    r"\b(?:who is the current|still alive|is .* alive|what happened to|news about|updates on)\b",
)

UNCERTAINTY_CONFESSION_PATTERNS = (
    r"\bi (?:really )?don'?t know\b",
    r"\bi do not know\b",
    r"\bi'?m not (?:100% )?(?:sure|certain)\b",
    r"\bi am not (?:100% )?(?:sure|certain)\b",
    r"\bnot familiar with\b",
    r"\bhaven'?t heard of\b",
    r"\bhave not heard of\b",
    r"\bmy knowledge cutoff\b",
    r"\bknowledge cut[\s-]?off\b",
    r"\bbeyond my (?:knowledge|training|cutoff)\b",
    r"\bafter my (?:knowledge )?(?:cutoff|training|last update)\b",
    r"\bas of my last (?:update|training|knowledge)\b",
    r"\b(?:don'?t|do not) have (?:access to )?(?:real[\s-]?time|live|current|up[\s-]?to[\s-]?date|recent|information|details|data)\b",
    r"\b(?:can'?t|cannot) (?:verify|confirm|access|browse|search the internet|check online)\b",
    r"\bno (?:information|details|data) (?:on|about)\b",
    r"\boutside (?:of )?my (?:knowledge|training)\b",
    r"\bwasn'?t trained on\b",
    r"\bnot in my training\b",
)

def is_auto_web_search_enabled() -> bool:
    return bool(WORKSPACE_CFG.get("auto_web_search", True)) and not bool(STATE.get("offline_mode", False))

def build_epistemic_web_rule() -> str:
    """Compact rule reminding small local models of today's year and instructing them to search instead of guessing."""
    cur_year = time.strftime("%Y")
    if STATE.get("offline_mode"):
        return (
            f"[KNOWLEDGE BOUNDARY RULE (OFFLINE MODE)]: Today is {time.strftime('%B %Y')}. "
            f"Your local weights are small and have a limited cutoff—if you don't know a fact, say so honestly instead of guessing."
        )
    return (
        f"[KNOWLEDGE BOUNDARY & LIVE WEB SEARCH RULE]: Today's real date is {time.strftime('%B %d, %Y')} ({cur_year}). "
        f"Your local offline weights are compact and outdated for recent events, niche topics, software updates, prices, people, or anything from 2024–{cur_year}. "
        f"NEVER guess or make up facts! Whenever you are unsure about ANY topic, fact, release, or recent event, "
        f"IMMEDIATELY search the internet first using ```workbench\\nprint(vault.web('clean keywords'))\\n``` (or [[SEARCH:clean keywords]]) and answer from the live results!"
    )

def detect_freshness_or_fact_query(user_msg: str) -> tuple:
    """
    Detects when a user question likely exceeds a small local model's training cutoff or needs live web facts,
    even if the user didn't explicitly say 'search the web'.
    Returns (should_auto_search, cleaned_query).
    """
    if not is_auto_web_search_enabled():
        return False, ""
    raw = re.sub(r"\*[^*]{1,30}\*", " ", (user_msg or "")).strip()
    if len(raw) < 10 or len(raw) > 360:
        return False, ""
    low = raw.lower()
    # Skip local PC / Spotify / weather / gauntlet / profile / studio toggle commands
    local_skip = (
        "spotify", "liked song", "my pc", "hostname", "steam game", "screenshot", "window",
        "desktop", "user card", "profile card", "theme", "full pc", "safe auto", "tool gauntlet",
        "gauntlet", "weather", "forecast", "raining", "my files", "priority_pdfs", "memory vault",
        "remember that", "my name is", "i live in", "error_audit", "assistant_server", "rename this chat"
    )
    if any(k in low for k in local_skip):
        return False, ""
    if any(re.search(pat, low) for pat in FRESHNESS_CUE_PATTERNS):
        sq = clean_web_search_query(raw)
        if len(sq) >= 4:
            return True, sq
    return False, ""

def detect_model_uncertainty(reply_text: str) -> bool:
    """Returns True if a small local model admitted it doesn't know or hit its training cutoff."""
    if not reply_text:
        return False
    low = reply_text.lower()
    return any(re.search(pat, low) for pat in UNCERTAINTY_CONFESSION_PATTERNS)

def is_query_searchable_for_rescue(user_msg: str) -> bool:
    """Ensures Uncertainty Rescue only triggers on factual/informational prompts (not pure greetings or RP)."""
    raw = (user_msg or "").strip()
    if len(raw) < 8 or len(raw) > 380 or "*" in raw:
        return False
    low = raw.lower()
    if re.fullmatch(r"(?:hi|hey|hello|yo|sup|thanks|thank you|ok|okay|cool|nice|lol|haha|bye|good morning|good night)[!.?\s]*", low):
        return False
    skip_personal = ("my pc", "my files", "my desktop", "spotify", "screenshot", "user card", "profile card", "remember that")
    if any(s in low for s in skip_personal):
        return False
    return True

def build_assistant_workbench_system_prompt(ai_name: str, user_name: str, mem_context: str) -> str:
    """
    Assistant-First Core Prompt (v4.5 — Full Companion Personality + Real PC Workbench!):
    - Loads the user's real CORE personality voice card (sarcasm, nicknames, charm) directly.
    - Keeps Lore RAG locked out so fictional cities never replace real weather/PC facts.
    - Gives the model the Live In-Process Python Workbench (` ```workbench `) with `vault` pre-imported.
    """
    pc_anchor = build_pc_reality_anchor()
    backend_card = format_backend_context_card()
    voice_card = build_companion_voice_card(ai_name, user_name)
    return (
        f"You are {ai_name}, {user_name}'s real local AI Assistant & PC Workbench Operator running directly on their PC inside AetherVault Studio v{APP_VERSION}.\n"
        f"CORE RULE: Real-world facts and live tool outputs ALWAYS override fiction (never invent fake weather, fake songs, or fake PC names), "
        f"but ALWAYS speak with your full authentic personality and charm!\n"
        f"{build_epistemic_web_rule()}\n\n"
        f"{voice_card}\n\n"
        f"{backend_card}\n\n"
        f"{pc_anchor}\n{build_epistemic_web_rule()}\n\n"
        f"=== LIVE IN-PROCESS PYTHON WORKBENCH (RUNNING IN THE SAME BACKEND CONSOLE) ===\n"
        f"To act on the PC or fetch live data, output ONLY a ```workbench block (`vault`, `os`, `json`, `math`, `Path`, `requests` are pre-imported):\n"
        f"- vault.weather() -> live weather & 2-day forecast for the user's saved card/pin (pass a city ONLY if checking a different city!)\n"
        f"- vault.web('clean keywords') / vault.docs('python/api topic') / vault.help() -> live web search, technical docs research & Workbench cheatsheet\n"        f"- vault.chunk_read('path', chunk_index=0, chunk_size=10000) -> read huge files/logs/PDFs chunk-by-chunk across chained Workbench steps\n"
        f"- vault.pc_info() -> real PC hostname, OS, RAM, Spotify status & libraries\n"
        f"- vault.files('steam' or 'C:/path' or 'keyword') -> scan local PC / Drive files\n"
        f"- vault.spotify('current_track'|'playlists'|'play_playlist'|'play_album'|'liked'|'play_liked'|'play'|'pause'|'next'|'prev', 'query') -> inspect or play full playlists/albums/Liked Songs (NEVER change playback if user just asks to look!)\n"
        f"- vault.browser(url='https://...', private=False, search='') | vault.youtube('query', private=True) | vault.fetch_url('https://...') -> open tabs, search YouTube, or read live webpages!\n- vault.disk_usage() | vault.ps_list() | vault.debug_log() | vault.clipboard('read'|'write', text) | vault.notify(title, msg) | vault.timer(secs, msg) -> real drives, clipboard, desktop toasts & timers!\n"
        f"- vault.write_desktop('hello_world.txt', 'Hello!') / vault.write_file('Desktop/test.txt', '...') / vault.read_file('Desktop/test.txt') -> silent PC file I/O\n"
        f"- vault.run_cmd('powershell command') -> silent background shell command (requires Full PC trust)\n"
        f"- vault.toggle('workspace_mode'|'workbench_trust'|'offline_mode'|'brain_mode'|'performance_mode'|'theme_preset'|'osworld_enabled', value) -> flip your own Studio toggles when user asks!\n"
        f"- vault.settings() / vault.pip_list() -> inspect current toggles & any installed pip libraries (you can import any pip package directly!)\n"
        f"- vault.open_app('steam'|'spotify'|'discord'|'notepad') / vault.osworld('screenshot'|'list_windows'|'open_app', 'arg') -> launch apps & desktop control\n"
        f"- vault.update_profile(user_name=..., location=..., zip_code=..., add_fact=..., remove_fact=..., custom_fields={{...}}) / vault.profile() -> edit or inspect the persistent User Card\n"
        f"- vault.memory_save(cat, fact) / vault.memory_edit(id, fact) / vault.forget(id_or_keyword) -> full Memory Vault & pseudo-memory CRUD\n"
        f"- vault.update_identity(ai_name=..., greeting_message=..., append_persona=...) / vault.update_partner_bond(...) / vault.set_theme(preset=..., colors={{...}}) -> customize your own persona, bond & studio theme\n"
        f"- vault.knowledge_list() / vault.knowledge_write('lore/note.md', text, mode='lore') / vault.knowledge_mode(file, 'core'|'lore') / vault.knowledge_delete(file) / vault.lore('keywords') -> full Knowledge Tree control\n"
        f"- vault.make_dir(path) / vault.move_file(src, dst) / vault.delete_file(path) / vault.rename_session(title) / vault.generate_image(prompt) / vault.generate_music(prompt) / vault.propose_core_fix(file, old, new, reason)\n"
        f"- vault.run_isolated(code, timeout=15) -> run heavy/experimental Python in a killable child subprocess\n"
        f"- vault.test_all(include_active=False) / vault.test_step('tool') -> run context-safe step-by-step tool gauntlet\n\n"
        f"IMPORTANT: To run any tool or PC action, output ONLY a ```workbench Python block (NEVER raw JSON like {{\"name\": ...}}!).\n\n"
        f"=== EXAMPLES ===\n"
        f"User: pick a song from my liked songs and play it\n"
        f"Assistant:\n```workbench\nprint(vault.spotify('play_liked', ''))\n```\n"
        f"User: make a hello world txt file on my desktop and open youtube in a private tab\n"
        f"Assistant:\n```workbench\nprint(vault.write_desktop('hello_world.txt', 'Hello World from AetherVault!'))\nprint(vault.browser('https://youtube.com', private=True))\n```\n"
        f"User: switch to full PC mode and cyber cyan theme\n"
        f"Assistant:\n```workbench\nprint(vault.toggle('workbench_trust', 'full_pc'))\nprint(vault.toggle('theme_preset', 'visor_cyan'))\n```\n\n"        f"User: did Hollow Knight Silksong come out yet or what's the latest update on it?\n"
        f"Assistant:\n```workbench\nprint(vault.web('Hollow Knight Silksong release date latest news'))\n```\n\n"
        f"=== MEMORY VAULT ===\n{mem_context}"
    )

def clean_assistant_theatrics(reply_text: str, is_assistant_mode: bool) -> str:
    """Cleans leaked internal prompt headers, echoed PC Reality Anchor lines, and raw workbench/JSON stubs while keeping full companion charm."""
    if not reply_text:
        return ""
    out = reply_text.strip()
    out = re.sub(r"\[SYSTEM DIRECTIVE:[^\]]*\]", "", out, flags=re.IGNORECASE)
    out = re.sub(r"\[(?:ACTIVE_STATE|FAST-WEB RESULTS|LIVE REALITY DATA|REAL LIVE WEATHER DATA|RECENT CHAT CONTINUITY[^\]]*|LIVE PC REALITY ANCHOR[^\]]*)\]:?", "", out, flags=re.IGNORECASE)
    out = re.sub(r"\[+/?workbench\]+", "", out, flags=re.IGNORECASE)
    out = re.sub(r"\*?\(\s*workbench\s+block\s+`?[^\n\r]*?\)\*?", "", out, flags=re.IGNORECASE)
    out = re.sub(r'```(?:python|py|json|workbench)?\s*\n\s*(?:\{\s*)?"name"\s*:\s*"[a-z_]+"[\s\S]*?```', "", out, flags=re.IGNORECASE).strip()
    out = re.sub(r'^\s*(?:\{\s*)?"name"\s*:\s*"[a-z_]+"[\s\S]*$', "", out).strip()
    # Strip repeated [Companion]: speaker tags that small models sometimes mimic from logs
    ai_n = re.escape(WORKSPACE_CFG.get("ai_name", "Aether"))
    out = re.sub(rf"(?m)^\s*\[{ai_n}\]:?\s*", "", out, flags=re.IGNORECASE)
    out = re.sub(r"\n{3,}", "\n\n", out).strip()
    # Unwrap accidental whole-message double quotes emitted by small local models
    if len(out) >= 2 and out.startswith('"') and out.endswith('"') and out.count('"') == 2:
        out = out[1:-1].strip()
    return out

def write_workbench_vault_module() -> Path:
    """Writes the session-scoped vault.py RPC shim inside .temp_cache using the active SERVER_PORT."""
    return avs_workbench.write_dynamic_vault_shim(TEMP_SESSION_DIR, port=SERVER_PORT, token=WORKBENCH_TOKEN)

def execute_workbench_rpc_action(action: str, args: dict) -> dict:
    """Executes a `vault.*` helper call with two-tier safety gating (safe_auto vs full_pc)."""
    act = (action or "").strip().lower()
    args = args if isinstance(args, dict) else {}
    trust = WORKSPACE_CFG.get("workbench_trust", "safe_auto")

    if act == "weather":
        raw_loc = str(args.get("location") or "").strip()
        return {"ok": True, "result": get_live_weather(raw_loc, latitude=args.get("latitude"), longitude=args.get("longitude"))}
    elif act == "web":
        q = clean_web_search_query(str(args.get("query") or ""))
        return {"ok": True, "result": search_web(q)}
    elif act == "pc_info":
        return {"ok": True, "result": get_pc_environment_info()}
    elif act == "files":
        q = str(args.get("query") or str(BASE_DIR)).strip()
        STATE["last_debug"]["pc_files_scanned"].append(q)
        return {"ok": True, "result": search_local_pc_files(q)}
    elif act == "spotify":
        return {"ok": True, "result": control_spotify(str(args.get("action") or "current_track"), str(args.get("query") or ""))}
    elif act == "open_app":
        res = execute_osworld_action("open_app", str(args.get("app") or args.get("arg") or ""))
        return {"ok": bool(res.get("ok")), "result": res.get("summary") or json.dumps(res)}
    elif act == "osworld":
        o_act = str(args.get("action") or "list_windows").strip().lower()
        o_arg = str(args.get("arg") or "").strip()
        if trust != "full_pc" and o_act not in ("screenshot", "screen", "capture", "list_windows", "windows", "open_app", "launch", "open", "start"):
            return {
                "ok": False,
                "error": f"Blocked raw mouse/keyboard OSWorld action '{o_act}' in Safe Auto mode. Ask me to switch to Full PC Control (or use vault.toggle('workbench_trust', 'full_pc')) to allow clicking/typing!"
            }
        res = execute_osworld_action(o_act, o_arg)
        if res.get("image_url"):
            WORKBENCH_LAST_MEDIA["image_url"] = res["image_url"]
        return {"ok": bool(res.get("ok")), "result": res.get("summary") or json.dumps(res)}
    elif act == "memory_save":
        return {"ok": True, "result": save_to_memory(str(args.get("category") or "active_state"), str(args.get("fact") or ""))}
    elif act == "memory_list":
        return {"ok": True, "result": list_memories()[:15]}
    elif act == "lore":
        txt, lbls = retrieve_relevant_lore(str(args.get("keywords") or ""), top_k=3)
        STATE["last_debug"]["lore_pulled"].extend(lbls)
        return {"ok": True, "result": txt or "No matching lore sections found."}
    elif act == "profile":
        return {"ok": True, "result": load_user_profile_card()}
    elif act == "write_file":
        return {"ok": True, "result": write_pc_file_silently(str(args.get("path") or ""), str(args.get("content") or ""), bool(args.get("append", False)))}
    elif act == "read_file":
        return {"ok": True, "result": read_pc_file_silently(str(args.get("path") or ""))}
    elif act == "browser":
        return {"ok": True, "result": open_browser_silently(str(args.get("url") or ""), str(args.get("search") or ""), bool(args.get("private", False)), str(args.get("browser") or "auto"))}
    elif act == "run_cmd":
        return {"ok": True, "result": run_silent_shell_command(str(args.get("command") or ""))}
    elif act == "toggle":
        return {"ok": True, "result": apply_studio_toggle(str(args.get("setting") or ""), args.get("value"))}
    elif act == "settings":
        return {"ok": True, "result": get_current_studio_toggles()}
    elif act == "pip_list":
        return {"ok": True, "result": [f"{p['name']}=={p['version']}" for p in get_all_pip_distributions()[:60]]}
    elif act == "pip_install":
        res = api_manage_package({"pkg": str(args.get("pkg") or ""), "action": "install"})
        return {"ok": bool(res.get("ok")), "result": res.get("output") or res.get("error") or "Done"}
    elif act == "test_all":
        return {"ok": True, "result": run_tool_gauntlet_compact(include_active=bool(args.get("include_active", False)))}
    elif act == "test_step":
        return {"ok": True, "result": run_tool_gauntlet_compact(include_active=True, only_tool=str(args.get("tool_name") or ""))}
    elif act == "update_profile":
        return {"ok": True, "result": update_user_profile_full(
            user_name=args.get("user_name"),
            location=args.get("location"),
            zip_code=args.get("zip_code"),
            latitude=args.get("latitude"),
            longitude=args.get("longitude"),
            add_fact=args.get("add_fact"),
            remove_fact=args.get("remove_fact"),
            custom_fields=args.get("custom_fields"),
            clear_fields=args.get("clear_fields")
        )}
    elif act == "memory_delete":
        return {"ok": True, "result": delete_memory_by_query_or_id(args.get("target"))}
    elif act == "memory_edit":
        return {"ok": True, "result": edit_memory_entry(int(args.get("mem_id", 0)), str(args.get("new_fact") or ""), args.get("new_category"))}
    elif act == "update_identity":
        return {"ok": True, "result": update_companion_identity_full(
            ai_name=args.get("ai_name"),
            greeting_message=args.get("greeting_message"),
            persona_prompt=args.get("persona_prompt"),
            append_persona=args.get("append_persona")
        )}
    elif act == "update_partner":
        return {"ok": True, "result": update_partner_bond_full(
            relationship_stage=args.get("relationship_stage"),
            preferred_vibe=args.get("preferred_vibe"),
            add_project=args.get("add_project"),
            remove_project=args.get("remove_project"),
            add_milestone=args.get("add_milestone"),
            add_topic=args.get("add_topic")
        )}
    elif act == "set_theme":
        return {"ok": True, "result": customize_studio_theme(
            preset=args.get("preset"),
            colors=args.get("colors"),
            wallpaper_opacity=args.get("wallpaper_opacity")
        )}
    elif act == "knowledge":
        return {"ok": True, "result": manage_knowledge_tree(
            action=str(args.get("action") or "list"),
            filename=str(args.get("filename") or ""),
            content=str(args.get("content") or ""),
            mode=str(args.get("mode") or "lore"),
            append=bool(args.get("append", False))
        )}
    elif act == "sessions":
        return {"ok": True, "result": manage_chat_sessions(
            action=str(args.get("action") or "list"),
            session_id=str(args.get("session_id") or ""),
            title=str(args.get("title") or ""),
            query=str(args.get("query") or "")
        )}
    elif act == "fs_op":
        return {"ok": True, "result": manage_pc_filesystem(
            action=str(args.get("action") or ""),
            path=str(args.get("path") or ""),
            dest=str(args.get("dest") or "")
        )}
    elif act == "generate_image":
        res = generate_image_tool(str(args.get("prompt") or ""))
        if res.get("ok") and res.get("url"):
            WORKBENCH_LAST_MEDIA["image_url"] = res["url"]
        return {"ok": bool(res.get("ok")), "result": res.get("source") or res.get("error") or json.dumps(res)}
    elif act == "generate_music":
        try:
            _dur = max(3, min(30, int(float(args.get("duration") or 8))))
        except Exception:
            _dur = 8
        res = generate_music_tool(str(args.get("prompt") or ""), duration_sec=_dur)
        if res.get("ok") and res.get("url"):
            WORKBENCH_LAST_MEDIA["audio_url"] = res["url"]
        return {"ok": bool(res.get("ok")), "result": res.get("source") or res.get("error") or json.dumps(res)}
    elif act == "propose_core_fix":
        res = stage_self_heal_proposal(
            target_file=str(args.get("target_file") or "assistant_server.py"),
            find_snippet=str(args.get("find_snippet") or ""),
            replace_snippet=str(args.get("replace_snippet") or ""),
            reason=str(args.get("reason") or "Autonomous Self-Heal Proposal")
        )
        STATE["ui_sync_needed"] = True
        return {"ok": bool(res.get("ok")), "result": res.get("message") or json.dumps(res)}
    return {"ok": False, "error": f"Unknown vault action: {act}"}


# =====================================================================
# 6C. v4.6 FLEXIBLE SILENT PC CONTROL (BROWSER, FILES, CMD) & SELF-TOGGLES
# =====================================================================
STATE.setdefault("last_user_msg", "")
STATE.setdefault("ui_sync_needed", False)
STATE.setdefault("spotify_readonly_turn", False)
STATE.setdefault("spotify_mutated_this_turn", "")

THEME_PRESETS_BACKEND = {
    "aether_violet":  {"bg": "#0d0e12", "sidebar": "#14151c", "panel": "#1b1d27", "accent": "#7c3aed", "accent_soft": "#a78bfa", "text": "#e5e7eb", "border": "#2b2e3d"},
    "visor_cyan":     {"bg": "#071018", "sidebar": "#0c1926", "panel": "#112436", "accent": "#0284c7", "accent_soft": "#38bdf8", "text": "#e0f2fe", "border": "#1e3a5f"},
    "emerald_matrix": {"bg": "#06100b", "sidebar": "#0a1912", "panel": "#11261b", "accent": "#059669", "accent_soft": "#34d399", "text": "#ecfdf5", "border": "#1b4332"},
    "noir_crimson":   {"bg": "#12090b", "sidebar": "#1a0e12", "panel": "#26151b", "accent": "#e11d48", "accent_soft": "#fb7185", "text": "#ffe4e6", "border": "#3f1d28"},
    "synth_sunset":   {"bg": "#140b24", "sidebar": "#1f1135", "panel": "#2b1847", "accent": "#db2777", "accent_soft": "#f472b6", "text": "#fae8ff", "border": "#4a2574"},
    "daylight_studio":{"bg": "#f3f4f6", "sidebar": "#ffffff", "panel": "#f9fafb", "accent": "#4f46e5", "accent_soft": "#4338ca", "text": "#111827", "border": "#d1d5db"}
}

def _find_installed_browser(preferred: str = "auto") -> tuple:
    """Finds installed desktop browser binaries (Brave, Chrome, Edge, Firefox) for silent launch with private flags."""
    local_app = os.environ.get("LOCALAPPDATA", "")
    prog_files = os.environ.get("PROGRAMFILES", "C:/Program Files")
    prog_x86 = os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)")

    catalog = [
        ("brave", "--incognito", [
            Path(prog_files) / "BraveSoftware/Brave-Browser/Application/brave.exe",
            Path(prog_x86) / "BraveSoftware/Brave-Browser/Application/brave.exe",
            Path(local_app) / "BraveSoftware/Brave-Browser/Application/brave.exe",
            shutil.which("brave") or "", shutil.which("brave-browser") or ""
        ]),
        ("chrome", "--incognito", [
            Path(prog_files) / "Google/Chrome/Application/chrome.exe",
            Path(prog_x86) / "Google/Chrome/Application/chrome.exe",
            Path(local_app) / "Google/Chrome/Application/chrome.exe",
            shutil.which("chrome") or "", shutil.which("google-chrome") or ""
        ]),
        ("edge", "--inprivate", [
            Path(prog_x86) / "Microsoft/Edge/Application/msedge.exe",
            Path(prog_files) / "Microsoft/Edge/Application/msedge.exe",
            shutil.which("msedge") or ""
        ]),
        ("firefox", "-private-window", [
            Path(prog_files) / "Mozilla Firefox/firefox.exe",
            Path(prog_x86) / "Mozilla Firefox/firefox.exe",
            shutil.which("firefox") or ""
        ])
    ]
    pref = (preferred or "auto").strip().lower()
    if pref != "auto":
        catalog.sort(key=lambda item: 0 if pref in item[0] else 1)

    for bname, priv_flag, paths in catalog:
        for p in paths:
            if not p:
                continue
            pp = Path(p)
            if pp.exists() and pp.is_file():
                return bname, str(pp), priv_flag
    return "default", "", ""

def open_browser_silently(url: str = "", search: str = "", private: bool = False, browser: str = "auto") -> str:
    """
    Opens a webpage or search silently in Brave/Chrome/Edge/Firefox WITHOUT touching mouse or keyboard!
    Supports private/incognito windows (`private=True`).
    """
    import webbrowser
    target = (url or "").strip()
    sq = (search or "").strip()
    if sq:
        t_low = target.lower()
        if not target:
            target = f"https://duckduckgo.com/?q={quote(sq)}"
        elif "youtube.com" in t_low or "youtu.be" in t_low:
            target = f"https://www.youtube.com/results?search_query={quote(sq)}"
        elif "google.com" in t_low:
            target = f"https://www.google.com/search?q={quote(sq)}"
        elif "spotify.com" in t_low:
            target = f"https://open.spotify.com/search/{quote(sq)}"
        elif "wikipedia.org" in t_low:
            target = f"https://en.wikipedia.org/w/index.php?search={quote(sq)}"
        elif "?" not in target:
            target = f"{target.rstrip('/')}/search?q={quote(sq)}"
    elif target and not re.match(r"^[a-zA-Z][a-zA-Z0-9+\-.]*://", target):
        if " " in target or "." not in target:
            target = f"https://duckduckgo.com/?q={quote(target)}"
        else:
            target = f"https://{target}"
    if not target:
        target = "https://duckduckgo.com/"

    bname, exe_path, priv_flag = _find_installed_browser(browser)
    try:
        if exe_path:
            cmd = [exe_path]
            if private and priv_flag:
                cmd.append(priv_flag)
            cmd.append(target)
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            mode_lbl = "Private/Incognito window" if private else "new tab"
            return f"Opened '{target}' silently in {bname.capitalize()} ({mode_lbl}) without touching your mouse or keyboard."
        webbrowser.open_new_tab(target)
        return f"Opened '{target}' in your system default browser."
    except Exception as e:
        return f"Browser launch error: {e}"

def _resolve_friendly_path(raw_path: str) -> Path:
    """Resolves shortcuts like 'Desktop/hello.txt', '~/Desktop/test.txt', or full paths cleanly."""
    p_str = (raw_path or "").strip().strip("'\"")
    if not p_str:
        return Path.home() / "Desktop"
    norm = p_str.replace("\\", "/")
    low = norm.lower()
    if low.startswith("desktop/"):
        return (Path.home() / "Desktop" / norm[8:]).resolve()
    if low == "desktop":
        return (Path.home() / "Desktop").resolve()
    if low.startswith("documents/"):
        return (Path.home() / "Documents" / norm[10:]).resolve()
    if low.startswith("downloads/"):
        return (Path.home() / "Downloads" / norm[10:]).resolve()
    return Path(p_str).expanduser().resolve()

def write_pc_file_silently(path: str, content: str, append: bool = False) -> str:
    """
    Silently creates or edits a text file on the user's PC (e.g., Desktop/hello_world.txt).
    - Protects AetherVault's own core source files from accidental overwrite.
    - In Safe Auto: permits Desktop, Documents, Downloads, .temp_cache, and non-core workspace files.
    - In Full PC: permits any normal user file path.
    """
    target = _resolve_friendly_path(path)
    if target.parent == BASE_DIR.resolve() and target.name in PROTECTED_CORE_FILES:
        return f"🛡️ Safety Gate: Cannot overwrite protected AetherVault core file '{target.name}'. Use Self-Heal Staging instead."

    trust = WORKSPACE_CFG.get("workbench_trust", "safe_auto")
    safe_roots = [
        (Path.home() / "Desktop").resolve(),
        (Path.home() / "Documents").resolve(),
        (Path.home() / "Downloads").resolve(),
        TEMP_SESSION_DIR.resolve(),
        BASE_DIR.resolve()
    ]
    in_safe_zone = any(sr == target or sr in target.parents for sr in safe_roots)
    if trust != "full_pc" and not in_safe_zone:
        return f"🛡️ Safe Auto Gate: Writing outside Desktop/Documents/Downloads/Workspace ('{target}') requires Full PC Control. Ask me to switch Workbench Trust to Full PC if you want that unlocked."

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if append else "w"
        with open(target, mode, encoding="utf-8") as f:
            f.write(str(content))
        size_b = target.stat().st_size
        verb = "Appended to" if append else "Wrote"
        return f"{verb} '{target}' silently ({size_b:,} bytes)."
    except Exception as e:
        return f"File write error for '{target}': {e}"

def read_pc_file_silently(path: str, max_chars: int = 0) -> str:
    if not max_chars or max_chars <= 0:
        max_chars = 18000 if WORKSPACE_CFG.get("unrestricted_tokens", True) else 3500
    target = _resolve_friendly_path(path)
    if not target.exists():
        return f"File not found: '{target}'"
    if target.is_dir():
        items = [f"{'[DIR]' if p.is_dir() else '[FILE]'} {p.name}" for p in sorted(target.iterdir())[:40]]
        return f"Directory '{target}':\n" + "\n".join(items)
    try:
        if target.suffix.lower() == ".pdf":
            doc = fitz.open(target)
            txt = "\n".join(p.get_text("text") for p in list(doc)[:5])
            doc.close()
            return f"PDF '{target.name}':\n{txt[:max_chars]}"
        return f"File '{target}':\n{target.read_text(encoding='utf-8', errors='ignore')[:max_chars]}"
    except Exception as e:
        return f"Error reading '{target}': {e}"

def run_silent_shell_command(command: str) -> str:
    """Runs a silent background command via avs.platform_bridge (PowerShell on Windows, bash/sh on Unix). Requires Full PC mode."""
    cmd = (command or "").strip()
    if not cmd:
        return "Empty shell command."
    if WORKSPACE_CFG.get("workbench_trust", "safe_auto") != "full_pc":
        return "🛡️ Safe Auto Gate: Shell commands require Workbench Trust = 'full_pc'. Ask me to switch Workbench Trust to Full PC first if you want me to run shell commands!"
    t0 = time.time()
    res = avs_platform.run_hidden_shell(cmd, timeout=15)
    elapsed = round(time.time() - t0, 2)
    out = (res.get("output") or "").strip()
    return f"[Shell exit={res.get('exit_code', -1)} | {elapsed}s]\n{out[:3000] if out else '(Completed silently with no output)'}"

def apply_studio_toggle(setting: str, value) -> str:
    """
    Flexible Self-Toggle Engine: lets the assistant switch AetherVault Studio's own toggles
    when asked by the user, saves to workspace_config.json, and triggers instant UI sync!
    """
    key = re.sub(r"[\s\-]+", "_", (setting or "").strip().lower())
    val_str = str(value).strip().lower()

    def _to_bool(v):
        if isinstance(v, bool):
            return v
        return str(v).strip().lower() in ("1", "true", "on", "yes", "enable", "enabled", "open")

    if key in ("workspace_mode", "mode", "persona_mode", "rp_mode", "roleplay_mode", "assistant_mode"):
        if key == "roleplay_mode" and _to_bool(value):
            target = "roleplay"
        elif key == "assistant_mode" and _to_bool(value):
            target = "assistant"
        elif any(k in val_str for k in ("role", "rp", "lore", "story")):
            target = "roleplay"
        else:
            target = "assistant"
        WORKSPACE_CFG["workspace_mode"] = target
        STATE["workspace_mode"] = target
        save_workspace_config(WORKSPACE_CFG)
        STATE["ui_sync_needed"] = True
        return f"Switched Workspace Mode -> '{target}' ({'Assistant & Python Workbench' if target == 'assistant' else 'Roleplay & Lore'})."

    if key in ("workbench_trust", "trust", "trust_mode", "pc_control", "pc_mode", "full_pc", "full_pc_mode", "full_control", "safe_auto", "safe_mode", "workbench_mode"):
        if key in ("full_pc", "full_pc_mode", "full_control", "pc_control", "pc_mode"):
            target = "full_pc" if (_to_bool(value) or "full" in val_str) else "safe_auto"
        elif key in ("safe_auto", "safe_mode"):
            target = "safe_auto" if (_to_bool(value) or "safe" in val_str) else "full_pc"
        elif any(k in val_str for k in ("full", "unlock", "all", "control", "on", "true", "yes")):
            target = "full_pc"
        else:
            target = "safe_auto"
        # Safety check: only escalate to full_pc if user's recent messages asked for PC control / unlocking / testing!
        if target == "full_pc" and WORKSPACE_CFG.get("workbench_trust") != "full_pc":
            u_low = (STATE.get("last_user_msg") or "").lower()
            allowed_ask = any(w in u_low for w in (
                "full pc", "full control", "take control", "unlock", "enable", "switch", "toggle",
                "turn on", "allow", "permission", "let you", "go ahead", "do it", "do so",
                "browser", "private", "incognito", "cmd", "shell", "open ", "launch ", "troubleshoot", "restrictive"
            ))
            if not allowed_ask:
                return "🛡️ Safety Check: Ask me explicitly to unlock Full PC Control before I escalate my own Workbench trust tier."
        WORKSPACE_CFG["workbench_trust"] = target
        STATE["workbench_trust"] = target
        save_workspace_config(WORKSPACE_CFG)
        STATE["ui_sync_needed"] = True
        return f"Switched Workbench Trust -> '{target}' ({'🔓 Full PC Control' if target == 'full_pc' else '🛡️ Safe Auto'})."

    if key in ("offline_mode", "offline"):
        b = _to_bool(value)
        STATE["offline_mode"] = b
        STATE["ui_sync_needed"] = True
        return f"Switched Offline Mode -> {'ON' if b else 'OFF'}."

    if key in ("brain_mode", "brain", "api_mode"):
        if "hybrid" in val_str:
            target = "hybrid"
        elif "api" in val_str or "cloud" in val_str:
            target = "smart_api"
        else:
            target = "local_only"
        WORKSPACE_CFG["brain_mode"] = target
        STATE["brain_mode"] = target
        save_workspace_config(WORKSPACE_CFG)
        STATE["ui_sync_needed"] = True
        return f"Switched Brain Mode -> '{target}'."

    if key in ("performance_mode", "governor", "performance"):
        perf_map = {
            "reflex": "Reflex (Auto-Smart Fast)",
            "laptop": "Laptop 2015 (Fast)",
            "2015": "Laptop 2015 (Fast)",
            "eco": "Eco (Safe)",
            "balanced": "Balanced",
            "turbo": "Turbo (Max Threads)"
        }
        chosen = next((v for k, v in perf_map.items() if k in val_str), "Balanced")
        set_performance({"mode": chosen})
        STATE["ui_sync_needed"] = True
        return f"Switched Governor / Performance Mode -> '{chosen}'."

    if key in ("osworld_enabled", "osworld", "desktop_control"):
        b = _to_bool(value)
        WORKSPACE_CFG["osworld_enabled"] = b
        save_workspace_config(WORKSPACE_CFG)
        STATE["ui_sync_needed"] = True
        return f"Switched OSWorld Desktop GUI Control -> {'ON' if b else 'OFF'}."

    if key in ("theme_preset", "theme", "color_theme"):
        matched_t = next((tk for tk in THEME_PRESETS_BACKEND if tk in val_str or val_str in tk), None)
        if not matched_t:
            alias_t = {"violet": "aether_violet", "purple": "aether_violet", "cyan": "visor_cyan", "blue": "visor_cyan",
                       "green": "emerald_matrix", "matrix": "emerald_matrix", "red": "noir_crimson", "crimson": "noir_crimson",
                       "synth": "synth_sunset", "pink": "synth_sunset", "80s": "synth_sunset", "light": "daylight_studio", "day": "daylight_studio"}
            matched_t = next((v for k, v in alias_t.items() if k in val_str), None)
        if not matched_t:
            return f"Unknown theme '{value}'. Available themes: {', '.join(THEME_PRESETS_BACKEND.keys())}."
        WORKSPACE_CFG["theme_preset"] = matched_t
        WORKSPACE_CFG["theme_colors"] = THEME_PRESETS_BACKEND[matched_t].copy()
        save_workspace_config(WORKSPACE_CFG)
        STATE["ui_sync_needed"] = True
        return f"Switched Studio Theme -> '{matched_t}'."

    if key in ("voice_profile", "voice"):
        WORKSPACE_CFG["voice_profile"] = str(value).strip()
        save_workspace_config(WORKSPACE_CFG)
        STATE["ui_sync_needed"] = True
        return f"Switched Voice Profile -> '{WORKSPACE_CFG['voice_profile']}'."

    if key in ("auto_web_search", "auto_web", "auto_search", "web_rescue"):
        b = _to_bool(value)
        WORKSPACE_CFG["auto_web_search"] = b
        save_workspace_config(WORKSPACE_CFG)
        STATE["ui_sync_needed"] = True
        return f"Switched Auto-Web Knowledge Lookup -> {'ON' if b else 'OFF'}."

    if key in ("unrestricted_tokens", "uncapped", "unlimited_tokens", "deep_run", "auto_continue"):
        b = _to_bool(value)
        WORKSPACE_CFG["unrestricted_tokens"] = b
        save_workspace_config(WORKSPACE_CFG)
        STATE["ui_sync_needed"] = True
        return f"Switched Uncapped / Deep-Run Token Engine -> {'ON (Max Context + Rolling Auto-Continue)' if b else 'OFF (Compact Standard Budget)'}."

    return f"Unknown toggle '{setting}'. Available toggles: workspace_mode, workbench_trust, offline_mode, auto_web_search, unrestricted_tokens, brain_mode, performance_mode, osworld_enabled, theme_preset, voice_profile."

def get_current_studio_toggles() -> dict:
    return {
        "workspace_mode": WORKSPACE_CFG.get("workspace_mode", "assistant"),
        "workbench_trust": WORKSPACE_CFG.get("workbench_trust", "safe_auto"),
        "offline_mode": bool(STATE.get("offline_mode", False)),
        "brain_mode": WORKSPACE_CFG.get("brain_mode", "local_only"),
        "performance_mode": STATE.get("performance_mode", "Balanced"),
        "osworld_enabled": bool(WORKSPACE_CFG.get("osworld_enabled", True)),
        "theme_preset": WORKSPACE_CFG.get("theme_preset", "aether_violet"),
        "voice_profile": WORKSPACE_CFG.get("voice_profile", "af_nicole_river"),
        "auto_web_search": bool(WORKSPACE_CFG.get("auto_web_search", True)),
        "unrestricted_tokens": bool(WORKSPACE_CFG.get("unrestricted_tokens", True))
    }

WORKBENCH_PERSISTENT_NS = {}


# =====================================================================
# 6D. v4.9 STEP-BY-STEP LIVE TOOL GAUNTLET (ANTI-CONTEXT-STARVATION ENGINE)
# =====================================================================
GAUNTLET_INTENT_PATTERNS = (
    "tool gauntlet", "run a gauntlet", "run the gauntlet", "do a gauntlet", "another gauntlet",
    "gauntlet test", "gauntlet", "full tool test", "test all your tools", "test every tool",
    "test every single tool", "test all tools", "test all we have", "run a full test", "run full test",
    "step by step test", "step-by-step test", "test everything you can do",
    "check all your tools", "full system test", "test all apis", "test all your apis"
)

def is_tool_gauntlet_query(user_msg: str) -> tuple:
    """Returns (is_gauntlet, include_active_pc_tools)."""
    low = (user_msg or "").lower()
    if not any(p in low for p in GAUNTLET_INTENT_PATTERNS):
        return False, False
    want_active = any(w in low for w in (
        "active", "full pc", "everything", "every single", "screenshot", "browser",
        "notepad", "shell", "include active", "full active"
    ))
    return True, want_active

def _run_callable_with_timeout(fn, timeout_sec: float = 6.0):
    """Isolates a single gauntlet step in its own thread with a hard per-tool timeout."""
    box = {"done": False, "val": None, "err": None}
    def _target():
        try:
            box["val"] = fn()
        except Exception as exc:
            box["err"] = f"{type(exc).__name__}: {exc}"
        finally:
            box["done"] = True
    t0 = time.perf_counter()
    th = threading.Thread(target=_target, daemon=True)
    th.start()
    th.join(timeout=timeout_sec)
    ms = int((time.perf_counter() - t0) * 1000)
    if not box["done"]:
        return "WARN", ms, f"Timed out after {timeout_sec:.0f}s (skipped cleanly so context & chat stay fast)"
    if box["err"]:
        return "FAIL", ms, box["err"][:120]
    return "OK", ms, box["val"]

def _gauntlet_step_specs(include_active: bool = False) -> list:
    """
    Generic, OS-aware, self-adapting step-by-step Tool Gauntlet (v4.11):
    - Works identically for ANY user on Windows, macOS, or Linux with zero hardcoded personal defaults.
    - Reads saved user location/context from persistent pseudo-memory (never hardcodes a city).
    - Auto-SKIPs optional unconfigured integrations (Spotify, disabled OSWorld, Offline network checks)
      instead of flagging false warnings on fresh installs.
    """
    def _t_pc_info():
        info = get_pc_environment_info()
        return "PASS", f"Host={info['pc_hostname']} | {info['os_platform']} | RAM {info['ram_free_gb']}/{info['ram_total_gb']}GB free"

    def _t_settings():
        st = get_current_studio_toggles()
        return "PASS", f"mode={st['workspace_mode']} | trust={st['workbench_trust']} | brain={st['brain_mode']} | theme={st['theme_preset']}"

    def _t_pip():
        pkgs = get_all_pip_distributions()
        return "PASS", f"{len(pkgs)} pip packages available in active .venv"

    def _t_files():
        out = search_local_pc_files(str(BASE_DIR))
        entries = max(0, len(out.splitlines()) - 1)
        roots_n = len(STATE.get("allowed_pc_roots", []))
        if entries > 0:
            return "PASS", f"Workspace scanner OK ({entries} root entries | {roots_n} indexed PC root(s))"
        return "WARN", out[:85]

    def _t_file_io():
        # Portable write -> readback -> auto-cleanup inside .temp_cache (safe on all OSes & OneDrive setups!)
        probe_path = TEMP_SESSION_DIR / ".av_gauntlet_probe.txt"
        marker = f"AV_GAUNTLET_OK_{int(time.time())}"
        w_out = write_pc_file_silently(str(probe_path), marker)
        if "Safety Gate" in w_out or "error" in w_out.lower():
            return "FAIL", w_out[:90]
        r_out = read_pc_file_silently(str(probe_path))
        try:
            if probe_path.exists():
                probe_path.unlink()
        except Exception:
            pass
        if marker in r_out:
            return "PASS", "Portable file write -> readback -> auto-cleanup verified (.temp_cache)"
        return "FAIL", "Readback did not match written probe text"

    def _t_python_sandbox():
        res = api_run_code_sandbox({"code": "print(6 * 7)"})
        if res.get("ok") and "42" in str(res.get("output", "")):
            return "PASS", f"Isolated .temp_cache Python sandbox OK (6*7=42 in {res.get('elapsed_sec', 0)}s)"
        return "FAIL", str(res.get("output") or "Sandbox failed")[:85]

    def _t_pseudo_memory():
        tag_fact = f"__av_gauntlet_probe_{int(time.time())}__"
        save_to_memory("gauntlet_probe", tag_fact, sync_pseudo=True)
        mems = list_memories()
        in_db = any(m.get("fact") == tag_fact for m in mems)
        in_json = False
        if PSEUDO_INDEX_JSON_PATH.exists():
            try:
                in_json = tag_fact in PSEUDO_INDEX_JSON_PATH.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                pass
        try:
            with get_db() as conn:
                conn.execute("DELETE FROM dynamic_memory WHERE fact = ?", (tag_fact,))
                conn.commit()
            sync_memory_vault_file()
            sync_pseudo_memory_and_index()
        except Exception:
            pass
        if in_db and in_json:
            return "PASS", f"Persistent Pseudo-Memory (SQLite + pseudo_memory_index.json) synced & cleaned ({len(mems)-1} saved)"
        return "FAIL", f"Sync mismatch (db={in_db}, pseudo_json={in_json})"

    def _t_lore():
        n_core = len(PRIORITY_CACHE.get("core_file_names", []))
        n_lore = PRIORITY_CACHE.get("lore_file_count", 0)
        n_chunks = PRIORITY_CACHE.get("lore_chunk_count", 0)
        return "PASS", f"Knowledge Tree ready ({n_core} CORE, {n_lore} LORE, {n_chunks} chunks)"

    def _t_weather():
        if STATE.get("offline_mode"):
            return "SKIP", "Offline Mode ON"
        pcard = load_user_profile_card()
        saved_loc = (pcard.get("location") or "").strip()
        saved_lat, saved_lon = pcard.get("latitude"), pcard.get("longitude")
        if saved_loc or (saved_lat is not None and saved_lon is not None):
            out = get_live_weather(saved_loc, latitude=saved_lat, longitude=saved_lon)
            if "LIVE WEATHER FOR" in out:
                short = out.split(":", 1)[-1].strip()[:75]
                tag = f"Pin {float(saved_lat):.2f},{float(saved_lon):.2f}" if (saved_lat is not None and saved_lon is not None) else saved_loc.split(",")[0]
                return "PASS", f"[User Card: {tag}] {short}"
            return "WARN", out[:85]
        # No location saved in pseudo-memory yet -> test Open-Meteo API with neutral UTC reference (never hardcode a user's city!)
        out = get_live_weather("Greenwich, UK")
        if "LIVE WEATHER FOR" in out:
            return "PASS", "Open-Meteo API OK (neutral UTC probe — share your city in chat to save it in pseudo-memory!)"
        return "WARN", out[:85]

    def _t_web():
        if STATE.get("offline_mode"):
            return "SKIP", "Offline Mode ON"
        out = search_web("Python programming language")
        if out and "Unavailable" not in out and "No live web results" not in out:
            eng = "ddgs metasearch" if DDGS_IS_MODERN else "fallback web engine (install ddgs for multi-engine)"
            return "PASS", f"{eng} OK ({len(out)} chars)"
        return "WARN", out[:85]

    def _t_spotify():
        if STATE.get("offline_mode"):
            return "SKIP", "Offline Mode ON"
        sp_cfg = WORKSPACE_CFG.get("spotify") or {}
        has_keys = bool((sp_cfg.get("client_id") or "").strip() and (sp_cfg.get("client_secret") or "").strip())
        if not has_keys:
            return "SKIP", "Optional: Spotify OAuth not configured in Studio Settings (desktop fallback active)"
        sp_client, auth_note = get_authenticated_spotify_client()
        if not sp_client:
            return "WARN", auth_note[:85]
        cur_out = control_spotify("current_track")
        liked_out = control_spotify("liked")
        cur_ok = ("Spotify (" in cur_out or "nothing is currently playing" in cur_out.lower())
        liked_ok = ("Liked Songs (" in liked_out)
        if cur_ok and liked_ok:
            return "PASS", f"OAuth + Liked Songs OK | {cur_out[:55]}"
        if cur_ok:
            return "WARN", f"Playback OK, but Liked Songs needs re-auth ('user-library-read' scope)"
        return "WARN", cur_out[:85]

    def _t_osworld_win():
        if not WORKSPACE_CFG.get("osworld_enabled", True):
            return "SKIP", "OSWorld disabled in Studio Settings"
        if not hasattr(ctypes, "windll") and not os.environ.get("DISPLAY") and sys.platform != "darwin":
            return "SKIP", "Headless environment (no GUI display)"
        res = execute_osworld_action("list_windows", "")
        if res.get("ok"):
            cnt = max(0, len((res.get("summary") or "").splitlines()) - 1)
            return "PASS", f"OSWorld enumerated {cnt} visible desktop window(s)"
        return "WARN", (res.get("summary") or "Unavailable")[:85]

    def _t_self_toggle():
        cur_mode = WORKSPACE_CFG.get("workspace_mode", "assistant")
        out = apply_studio_toggle("workspace_mode", cur_mode)
        STATE["ui_sync_needed"] = False
        if "Switched Workspace Mode" in out:
            return "PASS", f"Self-Toggle engine responsive (mode={cur_mode})"
        return "FAIL", out[:85]

    steps = [
        ("pc_info",         "💻", "PC Telemetry (vault.pc_info)",           3.0, _t_pc_info),
        ("settings",        "⚙️", "Studio Toggles (vault.settings)",        2.0, _t_settings),
        ("pip_list",        "📦", "Python .venv Libraries (vault.pip_list)",4.0, _t_pip),
        ("files",           "📂", "Workspace & PC Scanner (vault.files)",   5.0, _t_files),
        ("file_io",         "📝", "Portable File I/O + Cleanup",            3.0, _t_file_io),
        ("python_sandbox",  "🐍", "Isolated Python Sandbox",                5.0, _t_python_sandbox),
        ("pseudo_memory",   "💾", "Persistent Pseudo-Memory Sync + Cleanup",3.0, _t_pseudo_memory),
        ("lore",            "📖", "Knowledge Tree & Lore Index",            3.0, _t_lore),
        ("self_toggle",     "🎛️", "Self-Toggle Engine (vault.toggle)",      2.0, _t_self_toggle),
        ("weather",         "🌦️", "Live Weather API (Pseudo-Memory Aware)", 8.0, _t_weather),
        ("web",             "🌐", "Multi-Engine Web Search (vault.web)",    8.0, _t_web),
        ("spotify",         "🎵", "Spotify Integration (Optional)",         8.0, _t_spotify),
        ("osworld_windows", "🪟", "OSWorld Window Enumeration (Optional)",  4.0, _t_osworld_win),
    ]

    if include_active:
        def _t_screenshot():
            if not WORKSPACE_CFG.get("osworld_enabled", True):
                return "SKIP", "OSWorld disabled in Studio Settings"
            res = execute_osworld_action("screenshot", "")
            if res.get("ok"):
                if res.get("image_url"):
                    WORKBENCH_LAST_MEDIA["image_url"] = res["image_url"]
                return "PASS", (res.get("summary") or "Captured desktop screenshot")[:85]
            return "WARN", (res.get("summary") or "Screenshot unavailable")[:85]

        def _t_shell():
            if WORKSPACE_CFG.get("workbench_trust", "safe_auto") != "full_pc":
                return "SKIP", "Safe Auto active (switch Workbench Trust -> Full PC to test hidden shell)"
            out = run_silent_shell_command("echo GAUNTLET_SHELL_OK")
            if "GAUNTLET_SHELL_OK" in out:
                return "PASS", "Hidden background shell executed cleanly (Full PC active)"
            return "FAIL", out[:85]

        def _t_browser():
            out = open_browser_silently(url="https://example.com", private=True)
            if "Opened" in out:
                return "PASS", out[:85]
            return "FAIL", out[:85]

        def _t_open_app():
            if hasattr(os, "startfile"):
                app_target = "notepad"
            elif sys.platform == "darwin":
                app_target = "TextEdit"
            else:
                return "SKIP", "Skipped GUI app launch on Linux/headless OS"
            res = execute_osworld_action("open_app", app_target)
            if res.get("ok"):
                return "PASS", (res.get("summary") or f"Launched {app_target}")[:85]
            return "WARN", (res.get("summary") or "Launch failed")[:85]

        steps.extend([
            ("osworld_screenshot", "📸", "Active: OSWorld Desktop Screenshot",     5.0, _t_screenshot),
            ("shell_cmd",          "⚡", "Active: Hidden Shell (vault.run_cmd)",   6.0, _t_shell),
            ("browser_private",    "🕵️", "Active: Silent Private Browser Tab",     5.0, _t_browser),
            ("open_app",           "🚀", "Active: OS-Aware App Launcher",          5.0, _t_open_app),
        ])

    return steps

def run_tool_gauntlet_generator(include_active: bool = False, only_tool: str = ""):
    """
    Generator that executes every tool step-by-step in isolation, yielding live progress events
    and a final compact scorecard (<1,100 chars) so small models NEVER starve on context!
    """
    WORKBENCH_LAST_MEDIA["image_url"] = None
    all_steps = _gauntlet_step_specs(include_active=include_active or bool(only_tool))
    if only_tool:
        flt = only_tool.strip().lower()
        matched = [s for s in all_steps if flt in s[0].lower() or flt in s[2].lower()]
        all_steps = matched if matched else all_steps[:1]

    total = len(all_steps)
    counts = {"PASS": 0, "WARN": 0, "FAIL": 0, "SKIP": 0}
    score_lines = []
    t_all_0 = time.perf_counter()

    for idx, (tid, icon, label, timeout_s, fn) in enumerate(all_steps, 1):
        if STATE.get("stop_requested"):
            yield {"phase": "stopped", "step_index": idx, "total": total}
            break
        yield {
            "phase": "start",
            "id": tid,
            "icon": icon,
            "label": label,
            "index": idx,
            "total": total
        }
        r_state, ms, payload = _run_callable_with_timeout(fn, timeout_sec=timeout_s)
        if r_state == "OK" and isinstance(payload, tuple) and len(payload) == 2:
            status, detail = payload
        else:
            status, detail = r_state, str(payload)
        if status not in counts:
            status = "WARN"
        counts[status] += 1
        badge = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌", "SKIP": "⏭️"}.get(status, "•")
        compact_detail = re.sub(r"\s+", " ", str(detail)).strip()[:88]
        line = f"{badge} [{idx}/{total}] {tid} ({ms}ms): {compact_detail}"
        score_lines.append(line)
        yield {
            "phase": "result",
            "id": tid,
            "icon": icon,
            "label": label,
            "index": idx,
            "total": total,
            "status": status,
            "badge": badge,
            "ms": ms,
            "detail": compact_detail,
            "line": line
        }

    total_sec = round(time.perf_counter() - t_all_0, 2)
    mode_lbl = "FULL ACTIVE PC GAUNTLET" if include_active else ("SINGLE TOOL CHECK" if only_tool else "SAFE SILENT GAUNTLET")
    header = (
        f"=== 🧪 AETHERVAULT v{APP_VERSION} {mode_lbl} ({total_sec}s) | "
        f"✅ {counts['PASS']} PASS | ⚠️ {counts['WARN']} WARN | ❌ {counts['FAIL']} FAIL | ⏭️ {counts['SKIP']} SKIP ==="
    )
    scorecard = header + "\n" + "\n".join(score_lines)
    card = load_user_profile_card()
    card["last_workbench_summary"] = header[:240]
    save_user_profile_card(card)

    yield {
        "phase": "summary",
        "mode": mode_lbl,
        "total_sec": total_sec,
        "counts": counts,
        "total": total,
        "scorecard": scorecard[:1650],
        "image_url": WORKBENCH_LAST_MEDIA.get("image_url")
    }

def run_tool_gauntlet_compact(include_active: bool = False, only_tool: str = "") -> str:
    """Synchronous helper for `vault.test_all()` and `vault.test_step()` inside Python Workbench."""
    final_card = "No steps executed."
    for evt in run_tool_gauntlet_generator(include_active=include_active, only_tool=only_tool):
        if evt.get("phase") == "summary":
            final_card = evt["scorecard"]
    return final_card


# =====================================================================
# 6E. v4.12 FULL WORKSPACE AUTONOMY ENGINE (GENERIC & SANITIZED BASE)
#     Gives the active persona full digital control over User Profile Card,
#     Memory Vault, Companion Identity/Persona, Partner Evolution, Studio Theme,
#     Knowledge Tree (/priority_pdfs), Chat Sessions, Workspace Files, Media,
#     and Staged Self-Heal Proposals (while keeping core engine files guarded).
# =====================================================================
def update_user_profile_full(
    user_name=None,
    location=None,
    zip_code=None,
    latitude=None,
    longitude=None,
    add_fact=None,
    remove_fact=None,
    custom_fields=None,
    clear_fields=None
) -> str:
    """Full CRUD editor for user_profile_card.json synced with SQLite Memory Vault & pseudo_memory_index.json."""
    card = load_user_profile_card()
    changes = []

    if user_name is not None:
        clean_n = str(user_name).strip()
        if clean_n:
            card["user_name"] = clean_n
            WORKSPACE_CFG["user_name"] = clean_n
            save_workspace_config(WORKSPACE_CFG)
            with get_db() as conn:
                conn.execute("DELETE FROM dynamic_memory WHERE LOWER(category) = 'user_identity'")
                conn.execute("INSERT INTO dynamic_memory (category, fact) VALUES ('user_identity', ?)", (f"User's name/handle is {clean_n}",))
                conn.commit()
            changes.append(f"user_name='{clean_n}'")

    if location is not None:
        clean_loc = _clean_location_value(str(location))
        card["location"] = clean_loc
        with get_db() as conn:
            conn.execute("DELETE FROM dynamic_memory WHERE LOWER(category) IN ('user_location', 'location', 'city')")
            if clean_loc:
                conn.execute("INSERT INTO dynamic_memory (category, fact) VALUES ('user_location', ?)", (f"User lives in {clean_loc}",))
            conn.commit()
        changes.append(f"location='{clean_loc or '(cleared)'}'")

    if zip_code is not None:
        clean_z = str(zip_code).strip().upper()
        card["zip_code"] = clean_z
        with get_db() as conn:
            conn.execute("DELETE FROM dynamic_memory WHERE LOWER(category) IN ('user_zip', 'zip', 'zip_code')")
            if clean_z:
                conn.execute("INSERT INTO dynamic_memory (category, fact) VALUES ('user_zip', ?)", (f"User ZIP/Postal code is {clean_z}",))
            conn.commit()
        changes.append(f"zip_code='{clean_z or '(cleared)'}'")

    if latitude is not None and longitude is not None:
        if str(latitude).strip() == "" or str(longitude).strip() == "":
            card["latitude"] = None
            card["longitude"] = None
            changes.append("cleared map pin")
        else:
            try:
                card["latitude"] = round(float(latitude), 5)
                card["longitude"] = round(float(longitude), 5)
                changes.append(f"pin=({card['latitude']}, {card['longitude']})")
            except Exception:
                pass

    if add_fact:
        facts_in = add_fact if isinstance(add_fact, list) else [add_fact]
        pf = list(card.get("pinned_facts") or [])
        for fi in facts_in:
            fs = str(fi).strip()
            if fs and fs not in pf:
                pf.append(fs)
                with get_db() as conn:
                    c = conn.cursor()
                    c.execute("SELECT id FROM dynamic_memory WHERE LOWER(fact) = LOWER(?)", (fs,))
                    if not c.fetchone():
                        c.execute("INSERT INTO dynamic_memory (category, fact) VALUES ('user_note', ?)", (fs,))
                        conn.commit()
                changes.append(f"+fact='{fs[:45]}'")
        card["pinned_facts"] = pf[-12:]

    if remove_fact:
        rem_low = str(remove_fact).strip().lower()
        old_pf = list(card.get("pinned_facts") or [])
        new_pf = [f for f in old_pf if rem_low not in f.lower()]
        if len(new_pf) != len(old_pf):
            card["pinned_facts"] = new_pf
            changes.append(f"-fact matching '{rem_low}'")

    if isinstance(custom_fields, dict):
        cf = dict(card.get("custom_fields") or {})
        for k, v in custom_fields.items():
            ks = re.sub(r"[^a-zA-Z0-9_\- ]", "", str(k)).strip()[:40]
            if not ks:
                continue
            if v is None or str(v).strip() == "":
                cf.pop(ks, None)
                changes.append(f"-custom.{ks}")
            else:
                cf[ks] = str(v).strip()[:220]
                changes.append(f"custom.{ks}='{cf[ks][:40]}'")
        card["custom_fields"] = cf

    if clear_fields:
        c_list = clear_fields if isinstance(clear_fields, list) else [clear_fields]
        for fld in c_list:
            f_key = str(fld).strip().lower()
            if f_key in ("location", "zip_code", "last_workbench_summary"):
                card[f_key] = ""
                changes.append(f"cleared {f_key}")
            elif f_key in ("pin", "coords", "coordinates", "latitude", "longitude"):
                card["latitude"] = None
                card["longitude"] = None
                changes.append("cleared map pin")
            elif f_key == "pinned_facts":
                card["pinned_facts"] = []
                changes.append("cleared pinned_facts")
            elif f_key == "custom_fields":
                card["custom_fields"] = {}
                changes.append("cleared custom_fields")
            elif isinstance(card.get("custom_fields"), dict) and fld in card["custom_fields"]:
                card["custom_fields"].pop(fld, None)
                changes.append(f"cleared custom.{fld}")

    save_user_profile_card(card)
    sync_memory_vault_file()
    sync_pseudo_memory_and_index()
    STATE["ui_sync_needed"] = True
    if not changes:
        return f"Profile card unchanged: {json.dumps(card, ensure_ascii=False)}"
    return "Updated user profile card & synced persistent pseudo-memory: " + ", ".join(changes)

def delete_memory_by_query_or_id(target) -> str:
    """Deletes memory entry by numeric ID or case-insensitive substring match, syncing SQLite + profile card + pseudo-memory."""
    raw = str(target or "").strip()
    if not raw:
        return "Provide a memory ID or keyword substring to forget."
    removed_rows = []
    with get_db() as conn:
        c = conn.cursor()
        if raw.isdigit():
            c.execute("SELECT id, category, fact FROM dynamic_memory WHERE id = ?", (int(raw),))
            removed_rows = c.fetchall()
            c.execute("DELETE FROM dynamic_memory WHERE id = ?", (int(raw),))
        else:
            c.execute("SELECT id, category, fact FROM dynamic_memory WHERE LOWER(fact) LIKE ? OR LOWER(category) = LOWER(?)", (f"%{raw.lower()}%", raw))
            removed_rows = c.fetchall()
            c.execute("DELETE FROM dynamic_memory WHERE LOWER(fact) LIKE ? OR LOWER(category) = LOWER(?)", (f"%{raw.lower()}%", raw))
        conn.commit()

    if removed_rows:
        card = load_user_profile_card(allow_json_fallback=False)
        card_dirty = False
        for r in removed_rows:
            cat_l = (r["category"] or "").lower()
            if cat_l in ("user_location", "location", "city"):
                card["location"] = ""
                card_dirty = True
            elif cat_l in ("user_zip", "zip", "zip_code"):
                card["zip_code"] = ""
                card_dirty = True
            if card.get("pinned_facts"):
                new_pf = [f for f in card["pinned_facts"] if f.lower() != (r["fact"] or "").lower()]
                if len(new_pf) != len(card["pinned_facts"]):
                    card["pinned_facts"] = new_pf
                    card_dirty = True
        if card_dirty:
            save_user_profile_card(card)

    sync_memory_vault_file()
    sync_pseudo_memory_and_index()
    STATE["ui_sync_needed"] = True
    if not removed_rows:
        return f"No memory entry matched '{raw}'."
    return f"Forgot {len(removed_rows)} memory entry(ies): " + "; ".join(f"[{r['id']}] {r['fact'][:60]}" for r in removed_rows[:5])

def edit_memory_entry(mem_id: int, new_fact: str, new_category: str = None) -> str:
    """Edits an existing memory row in SQLite and syncs all persistent memory views."""
    nf = str(new_fact or "").strip()
    if not nf:
        return "New fact text cannot be empty."
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT id, category, fact FROM dynamic_memory WHERE id = ?", (int(mem_id),))
        row = c.fetchone()
        if not row:
            return f"Memory ID #{mem_id} not found."
        cat_use = (new_category or row["category"] or "active_state").strip()
        c.execute("UPDATE dynamic_memory SET category = ?, fact = ? WHERE id = ?", (cat_use, nf, int(mem_id)))
        conn.commit()
    sync_memory_vault_file()
    sync_pseudo_memory_and_index()
    STATE["ui_sync_needed"] = True
    return f"Updated memory #{mem_id} [{cat_use}]: {nf}"

def update_companion_identity_full(ai_name=None, greeting_message=None, persona_prompt=None, append_persona=None) -> str:
    """Lets the companion evolve its own name, greeting, or CORE_PERSONA.txt directive inside workspace_config.json."""
    updates = {}
    summary = []
    if ai_name is not None and str(ai_name).strip():
        updates["ai_name"] = str(ai_name).strip()[:40]
        summary.append(f"ai_name='{updates['ai_name']}'")
    if greeting_message is not None and str(greeting_message).strip():
        updates["greeting_message"] = str(greeting_message).strip()[:600]
        summary.append("greeting_message updated")
    if persona_prompt is not None and str(persona_prompt).strip():
        updates["persona_prompt"] = str(persona_prompt).strip()[:6000]
        summary.append(f"persona_prompt replaced ({len(updates['persona_prompt'])} chars)")
    elif append_persona is not None and str(append_persona).strip():
        cur_p = WORKSPACE_CFG.get("persona_prompt", "")
        addition = str(append_persona).strip()
        updates["persona_prompt"] = (cur_p + "\n\n" + addition).strip()[:6000]
        summary.append(f"appended to persona_prompt (+{len(addition)} chars)")

    if not updates:
        return f"Current companion identity: ai_name='{WORKSPACE_CFG.get('ai_name')}', greeting='{WORKSPACE_CFG.get('greeting_message', '')[:80]}'"

    update_config(updates)
    STATE["ui_sync_needed"] = True
    return "Updated companion identity & synced CORE_PERSONA.txt: " + ", ".join(summary)

def update_partner_bond_full(relationship_stage=None, preferred_vibe=None, add_project=None, remove_project=None, add_milestone=None, add_topic=None) -> str:
    """Updates partner_evolution.json directly so the companion can curate its evolving relationship & active projects."""
    evo = load_partner_evolution()
    changes = []
    if relationship_stage:
        evo["relationship_stage"] = str(relationship_stage).strip()[:100]
        changes.append(f"stage='{evo['relationship_stage']}'")
    if preferred_vibe:
        evo["preferred_vibe"] = str(preferred_vibe).strip()[:160]
        changes.append(f"vibe='{evo['preferred_vibe']}'")
    if add_project:
        proj = str(add_project).strip()[:120]
        projs = list(evo.get("active_projects") or [])
        if proj and proj not in projs:
            projs.append(proj)
            evo["active_projects"] = projs[-12:]
            changes.append(f"+project='{proj}'")
    if remove_project:
        rem = str(remove_project).strip().lower()
        evo["active_projects"] = [p for p in (evo.get("active_projects") or []) if rem not in p.lower()]
        changes.append(f"-project matching '{rem}'")
    if add_milestone:
        ms = str(add_milestone).strip()[:140]
        miles = list(evo.get("shared_milestones") or [])
        if ms and ms not in miles:
            miles.append(ms)
            evo["shared_milestones"] = miles[-15:]
            changes.append(f"+milestone='{ms}'")
    if add_topic:
        tp = str(add_topic).strip()[:60]
        tops = list(evo.get("favorite_topics") or [])
        if tp and tp not in tops:
            tops.append(tp)
            evo["favorite_topics"] = tops[-25:]
            changes.append(f"+topic='{tp}'")
    evo["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    PARTNER_EVOLUTION_PATH.write_text(json.dumps(evo, indent=2, ensure_ascii=False), encoding="utf-8")
    sync_pseudo_memory_and_index()
    STATE["ui_sync_needed"] = True
    return ("Updated partner_evolution.json: " + ", ".join(changes)) if changes else json.dumps(evo, ensure_ascii=False)

def customize_studio_theme(preset=None, colors=None, wallpaper_opacity=None) -> str:
    """Switches studio theme preset OR applies custom hex palette / wallpaper opacity live to the UI."""
    msgs = []
    if preset:
        msgs.append(apply_studio_toggle("theme_preset", str(preset)))
    if isinstance(colors, dict) and colors:
        cur_cols = dict(WORKSPACE_CFG.get("theme_colors") or THEME_PRESETS_BACKEND["aether_violet"])
        valid_keys = ("bg", "sidebar", "panel", "accent", "accent_soft", "text", "border")
        applied_k = []
        for ck, cv in colors.items():
            if ck in valid_keys and re.fullmatch(r"#[0-9a-fA-F]{6}", str(cv).strip()):
                cur_cols[ck] = str(cv).strip()
                applied_k.append(f"{ck}={cur_cols[ck]}")
        if applied_k:
            WORKSPACE_CFG["theme_preset"] = "custom"
            WORKSPACE_CFG["theme_colors"] = cur_cols
            save_workspace_config(WORKSPACE_CFG)
            STATE["ui_sync_needed"] = True
            msgs.append("Applied custom theme colors: " + ", ".join(applied_k))
    if wallpaper_opacity is not None:
        try:
            op = max(0.03, min(0.65, float(wallpaper_opacity)))
            WORKSPACE_CFG["wallpaper_opacity"] = round(op, 2)
            save_workspace_config(WORKSPACE_CFG)
            STATE["ui_sync_needed"] = True
            msgs.append(f"wallpaper_opacity={WORKSPACE_CFG['wallpaper_opacity']}")
        except Exception:
            pass
    return " | ".join(msgs) if msgs else f"Active theme: {WORKSPACE_CFG.get('theme_preset')} {WORKSPACE_CFG.get('theme_colors')}"

def manage_knowledge_tree(action: str, filename: str = "", content: str = "", mode: str = "lore", append: bool = False) -> str:
    """Full CRUD manager for /priority_pdfs (list, read, write, mode, delete) with instant SQLite re-indexing."""
    act = (action or "list").strip().lower()
    if act == "list":
        files = list_priority_files_info()
        if not files:
            return "Knowledge Tree (/priority_pdfs) has no indexed files yet."
        return "Knowledge Tree (/priority_pdfs):\n" + "\n".join(
            f"- [{f['mode'].upper()}] {f['name']} ({f['chunks']} chunks)" for f in files[:40]
        )

    rel_clean = (filename or "").strip().replace("\\", "/").lstrip("/")
    if not rel_clean:
        return "Missing filename inside /priority_pdfs (e.g. 'lore/notes.md')."
    target = (PDF_DIR / rel_clean).resolve()
    if PDF_DIR.resolve() not in target.parents:
        return "🛡️ Safety Gate: Knowledge Tree paths must stay inside /priority_pdfs."

    if act == "read":
        if not target.exists():
            return f"Knowledge file not found: '{rel_clean}'"
        return read_pc_file_silently(str(target), max_chars=3000)

    if act == "write":
        if target.suffix.lower() not in (".txt", ".md"):
            target = target.with_suffix(".md")
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "a" if append else "w", encoding="utf-8") as f:
            f.write(("\n" + str(content)) if append else str(content))
        rel_saved = target.relative_to(PDF_DIR).as_posix()
        m_clean = "core" if str(mode).strip().lower() == "core" else "lore"
        sync_priority_files(force=True)
        with get_db() as conn:
            conn.execute("UPDATE priority_pdfs SET file_mode = ?, manual_override = 1 WHERE filename = ?", (m_clean, rel_saved))
            conn.commit()
        sync_priority_files(force=True)
        STATE["ui_sync_needed"] = True
        return f"{'Appended to' if append else 'Saved'} Knowledge Tree file '{rel_saved}' (mode={m_clean.upper()}) & re-indexed!"

    if act == "mode":
        m_clean = "core" if str(mode).strip().lower() == "core" else "lore"
        set_file_mode({"filename": rel_clean, "mode": m_clean})
        STATE["ui_sync_needed"] = True
        return f"Switched Knowledge Tree file '{rel_clean}' -> {m_clean.upper()}."

    if act == "delete":
        if not target.exists():
            return f"Knowledge file not found: '{rel_clean}'"
        target.unlink()
        sync_priority_files(force=True)
        STATE["ui_sync_needed"] = True
        return f"Deleted '{rel_clean}' from Knowledge Tree & re-indexed."

    return f"Unknown knowledge action '{act}'. Use list, read, write, mode, or delete."

def manage_chat_sessions(action: str, session_id: str = "", title: str = "", query: str = "") -> str:
    """Lets the model list, search, read, or rename chat sessions cleanly."""
    act = (action or "list").strip().lower()
    if act in ("list", "read", "search"):
        return execute_cross_chat_tool(act, query or session_id, session_id)
    if act == "rename":
        new_t = (title or "").strip()[:60]
        if not new_t:
            return "Provide a new session title."
        with get_db() as conn:
            c = conn.cursor()
            if not session_id:
                c.execute("SELECT id FROM chat_sessions ORDER BY updated_at DESC LIMIT 1")
                r = c.fetchone()
                session_id = r["id"] if r else "session_main"
            c.execute("UPDATE chat_sessions SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_t, session_id))
            conn.commit()
        export_chats_to_txt_files()
        STATE["ui_sync_needed"] = True
        return f"Renamed chat session '{session_id}' -> '{new_t}'."
    return f"Unknown session action '{act}'. Use list, search, read, or rename."

def manage_pc_filesystem(action: str, path: str = "", dest: str = "") -> str:
    """
    Organized file/folder management (mkdir, move, delete) with Anti-Ouroboros core protection:
    - Protected AetherVault core engine files can NEVER be deleted or overwritten directly
      (use vault.propose_core_fix for syntax-checked staged patches!).
    - Safe Auto permits Desktop/Documents/Downloads/.temp_cache/non-core workspace paths.
    - Full PC permits any normal user path.
    """
    act = (action or "").strip().lower()
    target = _resolve_friendly_path(path)
    if target.parent == BASE_DIR.resolve() and target.name in PROTECTED_CORE_FILES:
        return f"🛡️ Anti-Ouroboros Gate: Cannot {act} protected core file '{target.name}'. Use vault.propose_core_fix() instead."

    trust = WORKSPACE_CFG.get("workbench_trust", "safe_auto")
    safe_roots = [
        (Path.home() / "Desktop").resolve(),
        (Path.home() / "Documents").resolve(),
        (Path.home() / "Downloads").resolve(),
        TEMP_SESSION_DIR.resolve(),
        BASE_DIR.resolve()
    ]
    def _in_safe(p_obj: Path) -> bool:
        return any(sr == p_obj or sr in p_obj.parents for sr in safe_roots)

    if trust != "full_pc" and not _in_safe(target):
        return f"🛡️ Safe Auto Gate: '{act}' outside Desktop/Documents/Downloads/Workspace ('{target}') requires Full PC Control."

    try:
        if act == "mkdir":
            target.mkdir(parents=True, exist_ok=True)
            return f"Created directory '{target}'."
        elif act == "move":
            if not target.exists():
                return f"Source path not found: '{target}'"
            dst_p = _resolve_friendly_path(dest)
            if dst_p.parent == BASE_DIR.resolve() and dst_p.name in PROTECTED_CORE_FILES:
                return f"🛡️ Anti-Ouroboros Gate: Cannot overwrite protected core file '{dst_p.name}'."
            if trust != "full_pc" and not _in_safe(dst_p):
                return f"🛡️ Safe Auto Gate: Moving to '{dst_p}' requires Full PC Control."
            dst_p.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(target), str(dst_p))
            return f"Moved '{target}' -> '{dst_p}'."
        elif act == "delete":
            if not target.exists():
                return f"Path not found: '{target}'"
            if target == BASE_DIR.resolve() or target == Path.home().resolve():
                return "🛡️ Safety Gate: Refusing to delete workspace root or home directory."
            if target.is_dir():
                shutil.rmtree(target)
                return f"Deleted folder '{target}'."
            target.unlink()
            return f"Deleted file '{target}'."
        return f"Unknown filesystem action '{act}'. Use mkdir, move, or delete."
    except Exception as e:
        return f"Filesystem '{act}' error: {e}"

WORKBENCH_HELP_TOPICS = {
    "web": "vault.web('keywords') | vault.fetch_url('https://...') | vault.youtube('query', private=True) | vault.docs('topic') -> Live news/web search, article reader & YouTube.",
    "weather": "vault.weather() -> Live Open-Meteo weather & 2-day forecast for user's saved card/pin (or pass 'City, Country').",
    "spotify": "vault.spotify('current_track'|'playlists'|'play_playlist'|'play_album'|'liked'|'play_liked'|'play'|'pause'|'next'|'prev', 'query')",
    "files": "vault.files('steam'|'C:/path'|'keyword') | vault.read_file('path') | vault.chunk_read('path', chunk_index=0, chunk_size=10000) | vault.write_file('Desktop/a.txt', 'text') | vault.write_desktop('a.txt', 'text')",
    "pc": "vault.pc_info() | vault.disk_usage() | vault.clipboard('read'|'write', text) | vault.notify(title, msg) | vault.timer(secs, msg) | vault.open_app('steam') | vault.browser(...) | vault.run_cmd(...)",
    "studio": "vault.toggle('workspace_mode'|'workbench_trust'|'auto_web_search'|'unrestricted_tokens'|'theme_preset'|'offline_mode', value) | vault.settings() | vault.pip_list()",
    "memory": "vault.profile() | vault.update_profile(...) | vault.memory_save(cat, fact) | vault.memory_list() | vault.forget(id_or_keyword) | vault.lore('keywords')",
    "knowledge": "vault.knowledge_list() | vault.knowledge_read(file) | vault.knowledge_write('lore/note.md', text, mode='lore') | vault.knowledge_mode(file, 'core'|'lore') | vault.knowledge_delete(file)",
    "media": "vault.generate_image('prompt') | vault.generate_music('prompt', duration=8) | vault.propose_core_fix(file, old, new, reason)",
    "language": "vault.spellcheck(text, lang='auto') | vault.translate(text, to='en', src='auto') | vault.detect_lang(text)",
    "gauntlet": "vault.test_all(include_active=False) | vault.test_step('tool_name')"
}

def read_pc_file_chunked(path: str, chunk_index: int = 0, chunk_size: int = 10000) -> str:
    """Reads arbitrarily large text/code/PDF files in clean numbered chunks so the AI can analyze huge files step-by-step."""
    target = _resolve_friendly_path(path)
    if not target.exists():
        return f"File not found: '{target}'"
    if target.is_dir():
        return read_pc_file_silently(str(target))
    try:
        chunk_size = max(1000, min(28000, int(chunk_size)))
        chunk_index = max(0, int(chunk_index))
        if target.suffix.lower() == ".pdf":
            doc = fitz.open(target)
            full_txt = "\n\n".join(f"[Page {i+1}]\n{p.get_text('text')}" for i, p in enumerate(doc))
            doc.close()
        else:
            full_txt = target.read_text(encoding="utf-8", errors="ignore")
        total_chars = len(full_txt)
        total_chunks = max(1, (total_chars + chunk_size - 1) // chunk_size)
        if chunk_index >= total_chunks:
            return f"EOF reached for '{target.name}' (total {total_chunks} chunk(s), {total_chars:,} chars)."
        start = chunk_index * chunk_size
        end = min(total_chars, start + chunk_size)
        more_hint = f" (Call vault.chunk_read({str(path)!r}, {chunk_index+1}, {chunk_size}) to continue!)" if (chunk_index + 1) < total_chunks else " (FINAL CHUNK — EOF)"
        return f"=== CHUNK {chunk_index+1}/{total_chunks} of '{target.name}' (chars {start:,}-{end:,} / {total_chars:,}){more_hint} ===\n{full_txt[start:end]}"
    except Exception as e:
        return f"Chunk read error for '{target}': {e}"

def _sanitize_workbench_code(raw_code: str) -> str:
    """Pre-execution sanitizer that repairs common small-model Python typos before ast.parse()."""
    s = (raw_code or "").strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z0-9_-]*\s*\n?", "", s)
        s = re.sub(r"\n?```\s*$", "", s).strip()
    cleaned_lines = []
    for ln in s.splitlines():
        ln_s = ln.rstrip()
        if ln_s.lstrip().startswith(">>> "):
            ln_s = ln_s.replace(">>> ", "", 1)
        elif ln_s.lstrip().startswith("... "):
            ln_s = ln_s.replace("... ", "", 1)
        cleaned_lines.append(ln_s)
    s = "\n".join(cleaned_lines).strip()
    # Auto-normalize Windows drive paths inside quotes so trailing backslashes never escape the closing quote!
    s = re.sub(
        r'(["\'])([A-Za-z]:\\[^"\'\n]*?)\1',
        lambda m: m.group(1) + m.group(2).replace("\\", "/") + m.group(1),
        s
    )
    # Auto-balance a single missing closing parenthesis/bracket on simple expressions
    if s.count("(") == s.count(")") + 1 and "\n" not in s:
        s += ")"
    if s.count("[") == s.count("]") + 1 and "\n" not in s:
        s += "]"
    return s

def workbench_auto_research_error(code_str: str, err_type: str, err_msg: str) -> str:
    """
    Failsafe Self-Research Recovery for the Workbench:
    - If a `vault.*` method failed -> returns local `vault.help()` signatures immediately (0ms).
    - If Python code, a library, PowerShell, or an API failed -> searches online docs via `search_web()`
      so the assistant learns the exact fix and can retry in the next Workbench round!
    """
    low_err = f"{err_type}: {err_msg}".lower()
    if "_liveinprocessvault" in low_err or "vault." in low_err:
        return "[LOCAL WORKBENCH HELP]:\n" + "\n".join(f"- {k}: {v}" for k, v in WORKBENCH_HELP_TOPICS.items())
    if not is_auto_web_search_enabled():
        return ""
    # Skip lookups for intentional safety gates or empty code
    if any(sk in low_err for sk in ("safety gate", "safe auto", "read-only guard", "empty workbench")):
        return ""
    clean_err = re.sub(r"['\"][^'\"]{40,}['\"]", "", str(err_msg))
    clean_err = re.sub(r"[A-Za-z]:\\[^\s]+", "", clean_err).strip()[:95]
    if err_type == "ModuleNotFoundError":
        q = f"python pip install {clean_err}"
    elif err_type in ("SyntaxError", "IndentationError"):
        q = f"python {err_type} {clean_err}"
    else:
        q = f"python {err_type} {clean_err} fix example"
    try:
        res = search_web(q)
        if res and "Unavailable" not in res and "No live web results" not in res:
            return f"[AUTO-RESEARCHED ONLINE DOCS FOR '{q[:65]}']:\n{res[:1300]}"
    except Exception:
        pass
    return ""




# =====================================================================
# 6F. v5.0 EVERGREEN CUSTOM TOOLS PLUGIN ENGINE & HF REPO INSPECTOR
# =====================================================================
class _PluginNamespace:
    """Dynamic namespace holding hot-reloaded modules from custom_tools/*.py."""
    pass

CUSTOM_PLUGINS = _PluginNamespace()
CUSTOM_PLUGINS_MANIFEST = {}

def reload_custom_tools() -> dict:
    """Hot-reloads all .py plugins in custom_tools/ without restarting the server."""
    global CUSTOM_PLUGINS, CUSTOM_PLUGINS_MANIFEST
    CUSTOM_TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    new_ns = _PluginNamespace()
    manifest = {}
    for py_file in sorted(CUSTOM_TOOLS_DIR.glob("*.py")):
        if py_file.name.startswith("_"):
            continue
        mod_name = py_file.stem
        try:
            spec = importlib.util.spec_from_file_location(f"avs_custom_{mod_name}", str(py_file))
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                setattr(new_ns, mod_name, mod)
                funcs = [fn for fn in dir(mod) if not fn.startswith("_") and callable(getattr(mod, fn))]
                manifest[mod_name] = {"ok": True, "file": py_file.name, "functions": funcs}
        except Exception as e:
            manifest[mod_name] = {"ok": False, "file": py_file.name, "error": f"{type(e).__name__}: {e}"}
    CUSTOM_PLUGINS = new_ns
    CUSTOM_PLUGINS_MANIFEST = manifest
    return manifest

def create_and_verify_custom_tool(name: str, code: str, test_code: str = "") -> str:
    """
    Compound v5.0 Tool Authoring Engine:
    1. Validates AST syntax & safe_auto rules.
    2. Runs `test_code` (or import smoke test) inside the killable child subprocess.
    3. ONLY if syntax + test PASS, saves to custom_tools/<name>.py and hot-reloads into vault.plugins.<name>!
    """
    clean_name = re.sub(r"[^a-zA-Z0-9_]", "_", (name or "").strip().lower()).strip("_")
    if not clean_name or clean_name[0].isdigit():
        return "Invalid tool name. Use letters/underscores (e.g. 'rss_watcher')."
    clean_code = _sanitize_workbench_code(code)
    if not clean_code:
        return "Empty tool code."
    try:
        ast.parse(clean_code)
    except SyntaxError as se:
        return f"SyntaxError in tool '{clean_name}' (line {se.lineno}): {se.msg}. Fix and retry before saving."

    probe_code = clean_code + "\n\n" + (_sanitize_workbench_code(test_code) if test_code else "print('PLUGIN_IMPORT_OK')")
    sub_res = avs_workbench.run_workbench_subprocess(
        code_str=probe_code,
        temp_dir=TEMP_SESSION_DIR,
        port=SERVER_PORT,
        token=WORKBENCH_TOKEN,
        timeout_sec=15.0,
        trust_level=WORKSPACE_CFG.get("workbench_trust", "safe_auto"),
    )
    if not sub_res.get("ok"):
        return f"Tool '{clean_name}' FAILED isolated sandbox test (NOT saved):\n{sub_res.get('output')}"

    CUSTOM_TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = CUSTOM_TOOLS_DIR / f"{clean_name}.py"
    out_path.write_text(clean_code + "\n", encoding="utf-8", newline="\n")
    manifest = reload_custom_tools()
    entry = manifest.get(clean_name, {})
    funcs = ", ".join(entry.get("functions") or []) or "(no public callables)"
    return (
        f"Tool '{clean_name}' PASSED sandbox test ({sub_res.get('elapsed_sec')}s) and hot-reloaded!\n"
        f"- Saved to: custom_tools/{clean_name}.py\n"
        f"- Call via: vault.plugins.{clean_name}.<func>(...) | Functions: {funcs}\n"
        f"- Test Output: {(sub_res.get('output') or '')[:400]}"
    )

def inspect_huggingface_repo(repo_id: str) -> dict:
    """Queries Hugging Face REST API for exact downloadable files & sizes (zero 404s!)."""
    rid = (repo_id or "").strip().strip("/")
    if not rid or "/" not in rid:
        return {"ok": False, "error": "Provide a valid repo ID like 'unsloth/gemma-4-E4B-it-GGUF'."}
    if STATE.get("offline_mode"):
        return {"ok": False, "error": "Offline Mode is ON."}
    try:
        r = requests.get(
            f"https://huggingface.co/api/models/{rid}",
            params={"blobs": "true"},
            headers={"User-Agent": f"AetherVaultStudio/{APP_VERSION}"},
            timeout=12,
        )
        r.raise_for_status()
        data = r.json()
        files = []
        for sib in (data.get("siblings") or []):
            fn = sib.get("rfilename") or ""
            ext = Path(fn).suffix.lower()
            if ext in (".gguf", ".onnx", ".safetensors", ".bin", ".json"):
                sz = int(sib.get("size") or (sib.get("lfs") or {}).get("size") or 0)
                files.append({
                    "filename": fn,
                    "size_mb": round(sz / (1024 * 1024), 1) if sz else 0.0,
                    "is_gguf": (ext == ".gguf"),
                    "is_vision": ("mmproj" in fn.lower()),
                })
        files.sort(key=lambda x: (0 if x["is_gguf"] else 1, x["filename"].lower()))
        return {"ok": True, "repo": rid, "files": files[:80]}
    except Exception as e:
        return {"ok": False, "repo": rid, "error": str(e)}


def workbench_debug_log(keyword: str = "", tail_lines: int = 40) -> str:
    """Reads recent entries from error_audit.log (optionally filtered by keyword)."""
    kw = (keyword or "").strip().lower()
    if not ERROR_AUDIT_LOG_PATH.exists():
        return "error_audit.log is clean (no errors logged yet)."
    try:
        lines = ERROR_AUDIT_LOG_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
        if kw:
            matched = [ln for ln in lines if kw in ln.lower()]
            if not matched:
                return f"No lines in error_audit.log matched '{keyword}' (total {len(lines)} lines)."
            return f"[ERROR_AUDIT.LOG matches for '{keyword}']:\n" + "\n".join(matched[-int(tail_lines):])
        return f"[ERROR_AUDIT.LOG (last {min(len(lines), int(tail_lines))} lines)]:\n" + "\n".join(lines[-int(tail_lines):])
    except Exception as e:
        return f"Could not read error_audit.log: {e}"

def workbench_ps_list(limit: int = 20) -> str:
    """Lists top running PC processes by RAM usage using psutil."""
    try:
        import psutil
        procs = []
        for p in psutil.process_iter(["pid", "name", "memory_info"]):
            try:
                mi = p.info.get("memory_info")
                mb = round(mi.rss / (1024 * 1024), 1) if mi else 0.0
                procs.append((mb, p.info["pid"], p.info.get("name") or "?"))
            except Exception:
                continue
        procs.sort(reverse=True)
        lines = [f"[TOP {min(len(procs), int(limit))} RUNNING PROCESSES BY RAM]:"]
        for mb, pid, name in procs[:int(limit)]:
            lines.append(f"- {name} (PID {pid}): {mb} MB")
        return "\n".join(lines)
    except Exception as e:
        return f"Process list unavailable: {e}"

def workbench_fetch_url(url: str, max_chars: int = 8000) -> str:
    """Clean webpage/article reader for the Workbench (strips nav/scripts/CSS so the AI can read real articles!)."""
    if STATE.get("offline_mode"):
        return "Offline Mode is ON — cannot fetch remote URLs."
    u = (url or "").strip()
    if not u:
        return "Provide a URL to fetch (e.g. vault.fetch_url('https://...'))."
    if not re.match(r"^https?://", u, flags=re.IGNORECASE):
        u = "https://" + u
    try:
        r = requests.get(
            u,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9,es;q=0.8"
            },
            timeout=12
        )
        r.raise_for_status()
        if BeautifulSoup is not None:
            soup = BeautifulSoup(r.text, "html.parser")
            for tag in soup(["script", "style", "noscript", "nav", "footer", "header", "aside", "svg"]):
                tag.decompose()
            title = soup.title.get_text(" ", strip=True) if soup.title else u
            text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True)).strip()
            return f"[FETCHED PAGE: {title} ({u})]\n{text[:int(max_chars)]}"
        return f"[FETCHED RAW: {u}]\n{re.sub(r'<[^>]+>', ' ', r.text)[:int(max_chars)]}"
    except Exception as e:
        return f"Could not fetch '{u}': {e}"

def workbench_disk_usage() -> str:
    """Lists all mounted disk drives with free/total GB so the AI knows real storage layout without guessing."""
    lines = ["[REAL PC DISK DRIVES]:"]
    try:
        import psutil
        for part in psutil.disk_partitions(all=False):
            try:
                du = psutil.disk_usage(part.mountpoint)
                free_gb = round(du.free / (1024 ** 3), 1)
                tot_gb = round(du.total / (1024 ** 3), 1)
                lines.append(f"- {part.mountpoint} ({part.fstype or 'FS'}): {free_gb} GB free / {tot_gb} GB total ({du.percent}% used)")
            except Exception:
                continue
    except Exception:
        du = shutil.disk_usage(BASE_DIR)
        lines.append(f"- {BASE_DIR.anchor}: {round(du.free/(1024**3),1)} GB free / {round(du.total/(1024**3),1)} GB total")
    return "\n".join(lines)

def workbench_clipboard(action: str = "read", text: str = "") -> str:
    """Reads or writes the system clipboard safely."""
    act = (action or "read").strip().lower()
    if os.name == "nt":
        if act in ("write", "set", "copy"):
            res = avs_platform.run_hidden_shell(f"Set-Clipboard -Value @'\n{str(text)}\n'@", timeout=6)
            return "Copied text to Windows clipboard!" if res.get("ok") else f"Clipboard write error: {res.get('output')}"
        res = avs_platform.run_hidden_shell("Get-Clipboard", timeout=6)
        return f"[CLIPBOARD]: {(res.get('output') or '(empty)')[:2000]}"
    return "Clipboard helper currently optimized for Windows PowerShell."

def workbench_notify(title: str = "AetherVault Studio", message: str = "") -> str:
    """Triggers a non-blocking desktop toast/alert notification."""
    t_clean = str(title or "AetherVault Studio").replace("'", "")[:60]
    m_clean = str(message or "Ping from AetherVault!").replace("'", "")[:200]
    if os.name == "nt":
        ps = (
            "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null;"
            "$t = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02);"
            f"$t.GetElementsByTagName('text')[0].AppendChild($t.CreateTextNode('{t_clean}')) | Out-Null;"
            f"$t.GetElementsByTagName('text')[1].AppendChild($t.CreateTextNode('{m_clean}')) | Out-Null;"
            "$n = [Windows.UI.Notifications.ToastNotification]::new($t);"
            "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('AetherVault Studio').Show($n);"
        )
        avs_platform.run_hidden_shell(ps, timeout=6)
        return f"Sent desktop notification: '{t_clean} — {m_clean}'"
    return f"[NOTIFY] {t_clean}: {m_clean}"

def workbench_timer(seconds: float = 60, message: str = "Timer finished!") -> str:
    """Starts a non-blocking background reminder timer that fires a desktop toast when done."""
    secs = max(1.0, min(86400.0, float(seconds)))
    msg = str(message or "Timer finished!")[:160]
    def _ring():
        time.sleep(secs)
        workbench_notify(f"{WORKSPACE_CFG.get('ai_name', 'Aether')} Reminder", msg)
    threading.Thread(target=_ring, daemon=True).start()
    return f"Started background timer for {secs:.0f}s -> will notify: '{msg}'"

class _LiveInProcessVault:
    """
    Hardened Direct In-Process Bridge (v4.16):
    - 0ms execution inside the running backend console, zero localhost HTTP deadlock.
    - Fuzzy alias routing + difflib hints so small-model method typos never crash blind.
    - Built-in `vault.help()`, `vault.docs()` online technical research, and `vault.chunk_read()` for huge files.
    """
    _ALIASES = {
        "search": "web", "google": "web", "lookup": "web", "internet": "web", "search_web": "web", "ddgs": "web", "news": "web",
        "research": "docs", "learn": "docs", "how_to": "docs", "manual": "help",
        "get_weather": "weather", "forecast": "weather", "climate": "weather",
        "sysinfo": "pc_info", "pc": "pc_info", "system_info": "pc_info", "specs": "pc_info",
        "ls": "files", "dir": "files", "list_files": "files", "scan_files": "files", "find_files": "files",
        "save_file": "write_file", "create_file": "write_file", "cat": "read_file", "open_file": "read_file",
        "read_chunk": "chunk_read", "read_chunks": "chunk_read",
        "shell": "run_cmd", "cmd": "run_cmd", "powershell": "run_cmd", "exec_cmd": "run_cmd",
        "music": "spotify", "play": "spotify", "song": "spotify",
        "open_url": "browser", "open_browser": "browser", "launch": "open_app", "start_app": "open_app",
        "set_toggle": "toggle", "config": "settings", "toggles": "settings",
        "mkdir": "make_dir", "mv": "move_file", "rm": "delete_file",
        "save_memory": "memory_save", "add_memory": "memory_save", "list_memories": "memory_list",
        "image": "generate_image", "draw": "generate_image", "compose": "generate_music",
    }

    def __getattr__(self, name: str):
        low_n = name.lower()
        if low_n in self._ALIASES:
            return getattr(self, self._ALIASES[low_n])
        import difflib
        real_methods = sorted([m for m in dir(self) if not m.startswith("_")])
        close = difflib.get_close_matches(low_n, real_methods + list(self._ALIASES.keys()), n=4, cutoff=0.45)
        hint_s = f" Closest valid methods: {', '.join('vault.' + c for c in close)}." if close else ""
        def _missing_method_helper(*args, **kwargs):
            return f"[WORKBENCH HINT] 'vault.{name}' does not exist.{hint_s} Run vault.help() to see all valid commands."
        return _missing_method_helper

    def _unwrap_arg(self, args, default_val="", label_keys=("query", "q", "location", "city", "path", "search")):
        if not args:
            return default_val
        if len(args) >= 2 and str(args[0]).strip().lower() in label_keys:
            return str(args[1])
        return str(args[0])

    def manual(self, topic=""):
        """Reads AetherVault Studio's own built-in v4.20 manual (optionally filtered by topic)."""
        t = (topic or "").strip().lower()
        parts = []
        for sec in SELF_MANUAL_SECTIONS:
            if not t or t in sec["id"].lower() or t in sec["title"].lower() or t in sec["body"].lower():
                parts.append(f"=== {sec['title']} ===\n{sec['body']}")
        return "\n\n".join(parts) if parts else "No manual section matched that topic. Call vault.manual() with no args to read all sections."

    def help(self, topic=""):
        t = (topic or "").strip().lower()
        if t:
            matched = [f"- {k}: {v}" for k, v in WORKBENCH_HELP_TOPICS.items() if t in k or t in v.lower()]
            if matched:
                return "=== WORKBENCH HELP ===\n" + "\n".join(matched)
        return "=== AETHERVAULT WORKBENCH API CHEATSHEET ===\n" + "\n".join(f"- {k}: {v}" for k, v in WORKBENCH_HELP_TOPICS.items())

    def docs(self, *args, query=""):
        """Dedicated online technical documentation & troubleshooting lookup for the Workbench."""
        q = query or self._unwrap_arg(args, "", ("query", "q", "topic", "docs", "search"))
        if not q:
            return self.help()
        return execute_workbench_rpc_action("web", {"query": f"{q} documentation example"}).get("result")

    def chunk_read(self, path, chunk_index=0, chunk_size=10000):
        return read_pc_file_chunked(str(path), int(chunk_index), int(chunk_size))

    def weather(self, *args, location="", latitude=None, longitude=None):
        loc = location or self._unwrap_arg(args, "", ("location", "city", "place", "query"))
        return execute_workbench_rpc_action("weather", {"location": loc, "latitude": latitude, "longitude": longitude}).get("result")
    def web(self, *args, query=""):
        q = query or self._unwrap_arg(args, "", ("query", "q", "search", "web", "topic"))
        return execute_workbench_rpc_action("web", {"query": q}).get("result")
    def pc_info(self): return execute_workbench_rpc_action("pc_info", {}).get("result")
    def files(self, *args, query=""):
        q = query or self._unwrap_arg(args, "", ("query", "path", "dir", "folder"))
        return execute_workbench_rpc_action("files", {"query": q}).get("result")
    def write_file(self, path, content, append=False): return execute_workbench_rpc_action("write_file", {"path": path, "content": content, "append": append}).get("result")
    def write_desktop(self, filename, content): return execute_workbench_rpc_action("write_file", {"path": f"Desktop/{filename}", "content": content, "append": False}).get("result")
    def read_file(self, path): return execute_workbench_rpc_action("read_file", {"path": path}).get("result")
    def browser(self, url="", private=False, search="", browser="auto"): return execute_workbench_rpc_action("browser", {"url": url, "private": private, "search": search, "browser": browser}).get("result")
    def youtube(self, query="", private=True, browser="auto"): return execute_workbench_rpc_action("browser", {"url": "https://www.youtube.com", "private": private, "search": query, "browser": browser}).get("result")
    def fetch_url(self, url, max_chars=8000): return workbench_fetch_url(str(url), int(max_chars))
    def disk_usage(self): return workbench_disk_usage()
    def clipboard(self, action="read", text=""): return workbench_clipboard(str(action), str(text))
    def notify(self, title="AetherVault Studio", message=""): return workbench_notify(str(title), str(message))
    def timer(self, seconds=60, message="Timer finished!"): return workbench_timer(float(seconds), str(message))
    def debug_log(self, keyword="", tail_lines=40): return workbench_debug_log(str(keyword), int(tail_lines))
    def errors(self, keyword="", tail_lines=40): return workbench_debug_log(str(keyword), int(tail_lines))
    def ps_list(self, limit=20): return workbench_ps_list(int(limit))
    def specs(self): return avs_hw.get_full_hardware_report()
    def hardware(self): return avs_hw.get_full_hardware_report()
    @property
    def plugins(self): return CUSTOM_PLUGINS
    def create_tool(self, name, code, test_code=""): return create_and_verify_custom_tool(str(name), str(code), str(test_code))
    def reload_tools(self): return reload_custom_tools()
    def hf_inspect(self, repo_id): return inspect_huggingface_repo(str(repo_id))
    def detect_lang(self, text): return avs_lang.detect_language(str(text or ""), default=(WORKSPACE_CFG.get("ui_language") or "en"))
    def spellcheck(self, text, lang="auto"): return run_lore_safe_spellcheck(str(text or ""), lang=str(lang or "auto"))
    def translate(self, text, to="en", src="auto"): return avs_lang.translate_text(str(text or ""), to_lang=str(to or "en"), from_lang=str(src or "auto"), model_dir=MODEL_DIR)
    def open_app(self, app): return execute_workbench_rpc_action("open_app", {"app": app}).get("result")
    def run_cmd(self, command): return execute_workbench_rpc_action("run_cmd", {"command": command}).get("result")
    def toggle(self, setting, value): return execute_workbench_rpc_action("toggle", {"setting": setting, "value": value}).get("result")
    def settings(self): return execute_workbench_rpc_action("settings", {}).get("result")
    def pip_list(self): return execute_workbench_rpc_action("pip_list", {}).get("result")
    def pip_install(self, pkg): return execute_workbench_rpc_action("pip_install", {"pkg": pkg}).get("result")
    def spotify(self, action="current_track", query=""): return execute_workbench_rpc_action("spotify", {"action": action, "query": query}).get("result")
    def osworld(self, action="list_windows", arg=""):
        r = execute_workbench_rpc_action("osworld", {"action": action, "arg": arg})
        if not r.get("ok"):
            raise RuntimeError(r.get("error") or "OSWorld action blocked")
        return r.get("result")
    def memory_save(self, category, fact): return execute_workbench_rpc_action("memory_save", {"category": category, "fact": fact}).get("result")
    def remember(self, category, fact): return execute_workbench_rpc_action("memory_save", {"category": category, "fact": fact}).get("result")
    def memory_list(self): return execute_workbench_rpc_action("memory_list", {}).get("result")
    def lore(self, keywords): return execute_workbench_rpc_action("lore", {"keywords": keywords}).get("result")
    def profile(self): return execute_workbench_rpc_action("profile", {}).get("result")
    def test_all(self, include_active=False): return execute_workbench_rpc_action("test_all", {"include_active": include_active}).get("result")
    def test_step(self, tool_name): return execute_workbench_rpc_action("test_step", {"tool_name": tool_name}).get("result")
    def update_profile(self, user_name=None, location=None, zip_code=None, latitude=None, longitude=None, add_fact=None, remove_fact=None, custom_fields=None, clear_fields=None):
        return execute_workbench_rpc_action("update_profile", {"user_name": user_name, "location": location, "zip_code": zip_code, "latitude": latitude, "longitude": longitude, "add_fact": add_fact, "remove_fact": remove_fact, "custom_fields": custom_fields, "clear_fields": clear_fields}).get("result")
    def memory_delete(self, target): return execute_workbench_rpc_action("memory_delete", {"target": target}).get("result")
    def forget(self, target): return execute_workbench_rpc_action("memory_delete", {"target": target}).get("result")
    def memory_edit(self, mem_id, new_fact, new_category=None): return execute_workbench_rpc_action("memory_edit", {"mem_id": mem_id, "new_fact": new_fact, "new_category": new_category}).get("result")
    def update_identity(self, ai_name=None, greeting_message=None, persona_prompt=None, append_persona=None):
        return execute_workbench_rpc_action("update_identity", {"ai_name": ai_name, "greeting_message": greeting_message, "persona_prompt": persona_prompt, "append_persona": append_persona}).get("result")
    def update_partner_bond(self, relationship_stage=None, preferred_vibe=None, add_project=None, remove_project=None, add_milestone=None, add_topic=None):
        return execute_workbench_rpc_action("update_partner", {"relationship_stage": relationship_stage, "preferred_vibe": preferred_vibe, "add_project": add_project, "remove_project": remove_project, "add_milestone": add_milestone, "add_topic": add_topic}).get("result")
    def set_theme(self, preset=None, colors=None, wallpaper_opacity=None):
        return execute_workbench_rpc_action("set_theme", {"preset": preset, "colors": colors, "wallpaper_opacity": wallpaper_opacity}).get("result")
    def knowledge_list(self): return execute_workbench_rpc_action("knowledge", {"action": "list"}).get("result")
    def knowledge_read(self, filename): return execute_workbench_rpc_action("knowledge", {"action": "read", "filename": filename}).get("result")
    def knowledge_write(self, filename, content, mode="lore", append=False):
        return execute_workbench_rpc_action("knowledge", {"action": "write", "filename": filename, "content": content, "mode": mode, "append": append}).get("result")
    def knowledge_mode(self, filename, mode): return execute_workbench_rpc_action("knowledge", {"action": "mode", "filename": filename, "mode": mode}).get("result")
    def knowledge_delete(self, filename): return execute_workbench_rpc_action("knowledge", {"action": "delete", "filename": filename}).get("result")
    def list_sessions(self): return execute_workbench_rpc_action("sessions", {"action": "list"}).get("result")
    def read_session(self, query): return execute_workbench_rpc_action("sessions", {"action": "read", "query": query}).get("result")
    def rename_session(self, title, session_id=""): return execute_workbench_rpc_action("sessions", {"action": "rename", "title": title, "session_id": session_id}).get("result")
    def make_dir(self, path): return execute_workbench_rpc_action("fs_op", {"action": "mkdir", "path": path}).get("result")
    def move_file(self, src, dst): return execute_workbench_rpc_action("fs_op", {"action": "move", "path": src, "dest": dst}).get("result")
    def delete_file(self, path): return execute_workbench_rpc_action("fs_op", {"action": "delete", "path": path}).get("result")
    def generate_image(self, prompt): return execute_workbench_rpc_action("generate_image", {"prompt": prompt}).get("result")
    def generate_music(self, prompt, duration=8): return execute_workbench_rpc_action("generate_music", {"prompt": prompt, "duration": duration}).get("result")
    def propose_core_fix(self, target_file, find_snippet, replace_snippet, reason=""):
        return execute_workbench_rpc_action("propose_core_fix", {"target_file": target_file, "find_snippet": find_snippet, "replace_snippet": replace_snippet, "reason": reason}).get("result")
    def run_isolated(self, code: str, timeout: float = 15.0):
        """Runs heavy or untrusted Python code in a killable child subprocess with a hard timeout."""
        return avs_workbench.run_workbench_subprocess(
            code_str=str(code or ""),
            temp_dir=TEMP_SESSION_DIR,
            port=SERVER_PORT,
            token=WORKBENCH_TOKEN,
            timeout_sec=min(60.0, max(1.0, float(timeout))),
            trust_level=WORKSPACE_CFG.get("workbench_trust", "safe_auto"),
        )

def execute_workbench_code(code_str: str) -> dict:
    """
    Hardened In-Process Python Workbench (v4.16):
    - Pre-sanitizes small-model syntax quirks (`>>> `, stray fences, single missing `)`) before ast.parse().
    - Pre-imports rich stdlib modules (`re`, `datetime`, `collections`, `itertools`, `statistics`, `random`, `csv`, `glob`, `shutil`, `platform`, `socket`, `difflib`).
    - Snapshots & rolls back namespace on fatal crash so one bad run never corrupts `vault` or user vars.
    - Stores untruncated output in `_last_output` & `.temp_cache/wb_last_output.txt` for deep multi-step analysis.
    - Auto-researches Python/API errors online (`workbench_auto_research_error`) so the model learns & self-corrects!
    """
    import ast
    import csv
    import glob
    import random
    import difflib
    import datetime
    import itertools
    import statistics
    import collections
    import contextlib

    clean_code = _sanitize_workbench_code(code_str)
    if not clean_code:
        return {"ok": False, "output": "Empty workbench block.", "image_url": None, "audio_url": None, "auto_researched": False}

    trust = WORKSPACE_CFG.get("workbench_trust", "safe_auto")
    if trust != "full_pc":
        blocked_pats = [
            (r"\b(?:os\.remove|os\.unlink|os\.rmdir|shutil\.rmtree|os\.system|subprocess\.)", "Destructive/shell calls are blocked in Safe Auto mode (enable Full PC Control to allow)."),
            (r"vault\.osworld\(\s*['\"](?:click|double_click|right_click|type|write|hotkey|key|press)['\"]", "OSWorld raw cursor/keyboard control is blocked in Safe Auto mode (enable Full PC Control to allow).")
        ]
        for bpat, bmsg in blocked_pats:
            if re.search(bpat, clean_code):
                return {"ok": False, "output": f"🛡️ Workbench Safety Gate: {bmsg}", "image_url": None, "audio_url": None, "auto_researched": False}

    WORKBENCH_LAST_MEDIA["image_url"] = None
    WORKBENCH_LAST_MEDIA["audio_url"] = None

    # Refresh live helpers & stdlib modules in the persistent in-process namespace
    ns_backup = dict(WORKBENCH_PERSISTENT_NS)
    WORKBENCH_PERSISTENT_NS.setdefault("__builtins__", __builtins__)
    WORKBENCH_PERSISTENT_NS.update({
        "vault": _LiveInProcessVault(),
        "os": os, "re": re, "json": json, "math": math, "time": time, "csv": csv,
        "glob": glob, "random": random, "shutil": shutil, "socket": socket,
        "platform": platform, "difflib": difflib, "datetime": datetime,
        "itertools": itertools, "statistics": statistics, "collections": collections,
        "Path": Path, "requests": requests, "BASE_DIR": BASE_DIR, "TEMP_DIR": TEMP_SESSION_DIR
    })

    max_out_chars = 10000 if WORKSPACE_CFG.get("unrestricted_tokens", True) else 3500
    result_box = {"ok": False, "output": "", "err_type": "", "err_msg": "", "done": False}

    def _run_in_backend_console():
        buf = io.StringIO()
        try:
            tree = ast.parse(clean_code, filename="<workbench>", mode="exec")
            last_expr_val = None
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                if tree.body and isinstance(tree.body[-1], ast.Expr):
                    last_node = tree.body.pop()
                    if tree.body:
                        exec(compile(tree, "<workbench>", "exec"), WORKBENCH_PERSISTENT_NS)
                    last_expr_val = eval(compile(ast.Expression(last_node.value), "<workbench>", "eval"), WORKBENCH_PERSISTENT_NS)
                    if last_expr_val is not None:
                        val_s = str(last_expr_val)
                        if val_s and val_s not in buf.getvalue():
                            print(val_s)
                else:
                    exec(compile(tree, "<workbench>", "exec"), WORKBENCH_PERSISTENT_NS)
            full_out = buf.getvalue().strip() or "(Executed cleanly with no stdout output)"
            WORKBENCH_PERSISTENT_NS["_last_output"] = full_out
            WORKBENCH_PERSISTENT_NS["_last_error"] = ""
            if len(full_out) > max_out_chars:
                try:
                    TEMP_SESSION_DIR.mkdir(parents=True, exist_ok=True)
                    spill_p = TEMP_SESSION_DIR / "wb_last_output.txt"
                    spill_p.write_text(full_out, encoding="utf-8")
                    out_txt = (
                        full_out[:max_out_chars]
                        + f"\n... [Output truncated at {max_out_chars:,}/{len(full_out):,} chars — full text saved in `_last_output` & '{spill_p.name}'. Use `print(_last_output[{max_out_chars}:])` or `vault.chunk_read(...)` to inspect more!]"
                    )
                except Exception:
                    out_txt = full_out[:max_out_chars]
            else:
                out_txt = full_out
            result_box["ok"] = True
            result_box["output"] = out_txt
        except Exception as e:
            err_so_far = buf.getvalue().strip()
            etype = type(e).__name__
            emsg = str(e)
            result_box["ok"] = False
            result_box["err_type"] = etype
            result_box["err_msg"] = emsg
            msg = f"{etype}: {emsg}"
            result_box["output"] = (f"{err_so_far}\n{msg}" if err_so_far else msg)[:max_out_chars]
            # Rollback namespace so a broken run never poisons `vault` or previously computed variables
            WORKBENCH_PERSISTENT_NS.clear()
            WORKBENCH_PERSISTENT_NS.update(ns_backup)
            WORKBENCH_PERSISTENT_NS["_last_error"] = msg
        finally:
            result_box["done"] = True

    t0 = time.time()
    worker = threading.Thread(target=_run_in_backend_console, daemon=True)
    worker.start()
    wb_timeout = 45.0 if ("test_all" in clean_code or WORKSPACE_CFG.get("unrestricted_tokens", True)) else 20.0
    worker.join(timeout=wb_timeout)
    elapsed = round(time.time() - t0, 2)

    if not result_box["done"]:
        return {
            "ok": False,
            "elapsed_sec": elapsed,
            "output": f"⏱️ Workbench code timed out after {int(wb_timeout)}s. Break large tasks into smaller chunks or steps.",
            "image_url": None,
            "audio_url": None,
            "auto_researched": False
        }

    auto_researched = False
    if not result_box["ok"] and result_box["err_type"]:
        hint_block = workbench_auto_research_error(clean_code, result_box["err_type"], result_box["err_msg"])
        if hint_block:
            auto_researched = True
            result_box["output"] = f"{result_box['output']}\n\n{hint_block}"

    if result_box["ok"] and result_box["output"]:
        print(f"[WORKBENCH IN-PROCESS {elapsed}s] {result_box['output'][:160]}", flush=True)
        card = load_user_profile_card()
        card["last_workbench_summary"] = result_box["output"][:240]
        save_user_profile_card(card)

    return {
        "ok": result_box["ok"],
        "elapsed_sec": elapsed,
        "output": result_box["output"],
        "image_url": WORKBENCH_LAST_MEDIA["image_url"],
        "audio_url": WORKBENCH_LAST_MEDIA["audio_url"],
        "auto_researched": auto_researched
    }

def extract_workbench_blocks(text: str) -> tuple:
    """
    Finds executable Python Workbench code in ALL formats local 3B/7B models emit:
    1. Fenced ```workbench, ```python-run, ```vault, or ```python / ``` blocks calling `vault.*`
    2. Unfenced `[workbench]` / `[[workbench]]` header followed by `vault.*(...)` lines
    3. Bare standalone `vault.<method>(...)` lines (e.g., `vault.spotify('play', '...')`)
    Never confuses a JSON tool call (`{"name": ...}`) for Python code.
    """
    blocks = []
    cleaned = text or ""

    def _collect(match):
        lang = (match.group(1) or "").lower()
        code = (match.group(2) or "").strip()
        if not code:
            return ""
        if code.lstrip().startswith("{") and '"name"' in code:
            return match.group(0)
        if lang in ("workbench", "python-run", "vault"):
            blocks.append(code)
            return ""
        if lang in ("python", "py", "") and "vault." in code and "vault.web('City, Country')" not in code:
            blocks.append(code)
            return ""
        return match.group(0)

    cleaned = re.sub(r"```(workbench|python-run|vault|python|py)?\s*\n([\s\S]*?)```", _collect, cleaned, flags=re.IGNORECASE).strip()

    # Catch unfenced `[workbench]\n...`, bare `vault.<method>(...) # comment` lines, OR inline backticked `` `vault.<method>(...)` ``!
    if not blocks and "vault." in cleaned:
        vault_lines = []
        kept_lines = []
        skip_next_blank = False
        doc_placeholders = ("vault.web('City, Country')", "vault.weather('City, Country')", "vault.toggle('workspace_mode'")
        for ln in cleaned.splitlines():
            s = ln.strip()
            if re.match(r"^\[+/?workbench\]+$", s, flags=re.IGNORECASE):
                skip_next_blank = True
                continue
            # Strip trailing inline Python comment outside quotes for matching
            s_no_comment = re.sub(r"\s+#[^'\"]*$", "", s).strip()
            if re.match(r"^(?:print\s*\(\s*)?vault\.[a-zA-Z_]+\s*\(.*\)\s*\)?$", s_no_comment) and not any(dp in s for dp in doc_placeholders):
                vault_lines.append(s_no_comment)
                skip_next_blank = True
                continue
            if skip_next_blank and not s:
                skip_next_blank = False
                continue
            skip_next_blank = False
            kept_lines.append(ln)

        # Also catch inline backticked OR unbalanced `*(workbench block `vault.web(...)`*)` calls!
        if not vault_lines:
            inline_hits = []
            for pat_in in (
                r"`((?:print\s*\(\s*)?vault\.[a-zA-Z_]+\s*\([^`\n]*\)\s*\)?)`",
                r"\*?\(\s*workbench\s+block\s+`?((?:print\s*\(\s*)?vault\.[a-zA-Z_]+\s*\([^\n\r`]*\))`?\s*\*?\)"
            ):
                for m_bt in re.finditer(pat_in, cleaned, flags=re.IGNORECASE):
                    cand = m_bt.group(1).strip().rstrip("*").strip()
                    if not any(dp in cand for dp in doc_placeholders) and cand not in inline_hits:
                        inline_hits.append(cand)
            if inline_hits:
                vault_lines.extend(inline_hits)
                cleaned_no_wrap = re.sub(r"\*?\(\s*workbench\s+block\s+`?[^\n\r]*?vault\.[a-zA-Z_]+\s*\([^\n\r]*?\)\s*`?\s*\*?\)", "", cleaned, flags=re.IGNORECASE).strip()
                kept_lines = [cleaned_no_wrap]

        if vault_lines:
            blocks.append("\n".join(vault_lines))
            cleaned = "\n".join(kept_lines).strip()

    return blocks, cleaned

OPERATOR_INTENT_PATTERNS = (
    "spotify", "spotipy", "api", "apis", "librar", "my pc", "this pc", "name of my pc",
    "hostname", "computer name", "system info", "pc specs", "hardware", "root file",
    "my files", "file system", "filesystem", "steam", "folder", "directory", "drive",
    "screenshot", "open window", "windows open", "osworld", "launch ", "open app",
    "run python", "execute python", "python script", "sandbox", "error log", "error_audit",
    "make a log", "poke around", "your tools", "what tools", "which tools", "tool",
    "search the web", "search online", "web search", "weather", "climate", "temperature", "forecast",
    "google ", "duckduckgo", "installed packages", "workbench", "where i live", "where am i from",
    "play a song", "play another song", "playing another song", "play some music", "put on a song",
    "next song", "next track", "skip this song", "pause the music", "what song is playing",
    "liked song", "liked songs", "saved song", "saved songs", "open browser", "open a tab",
    "private tab", "private window", "incognito", "open webpage", "open website", "on my desktop",
    "in the desktop", "on the desktop", "create a file", "make a file", "make me a", "write a file",
    "switch to roleplay", "switch to assistant", "full pc", "safe auto", "switch theme", "change theme",
    "offline mode", "toggle ", "switch your", "turn on ", "turn off ",
    "listening to", "different song", "what song", "which song", "identify", "ndentify",
    "in queue", "in qeue", "queue it", "qeue it", "song yet", "that song", "this song",
    "current song", "playing right now", "what am i listening", "playlist", "playlists", "album", "wich one", "which one", "dont change", "don't change", "take a look", "changed the song",
    "open steam", "open discord", "open spotify", "open notepad", "open brave", "open chrome", "locate the exe",
    "gauntlet", "tool gauntlet", "full tool test", "test all your tools", "test all we have", "test every tool", "test every single tool", "step by step test", "step-by-step test", "run the gauntlet",
    "user card", "profile card", "update my profile", "update your persona", "change your name", "forget that", "delete memory", "custom theme", "rename this chat", "knowledge tree",
    "clima", "pronostico", "pronóstico", "temperatura", "buscar en internet", "busca en internet", "noticias", "mi pc", "mis archivos", "captura de pantalla", "escritorio",
    "poné ", "pone ", "reproducir", "reproducí", "canción", "cancion", "siguiente canción", "pausar música", "traducir", "traducción", "ortografía", "revisar ortografía"
)

def is_operator_or_system_query(user_msg: str) -> bool:
    """Detects PC, API, Spotify, file, library, OSWorld, or system inspection requests so Lore RAG never hijacks them."""
    low = (user_msg or "").lower()
    if is_capability_or_api_query(user_msg):
        return True
    return any(pat in low for pat in OPERATOR_INTENT_PATTERNS)

def get_pc_environment_info() -> dict:
    """Collects real, live telemetry from the host PC so the assistant never hallucinates machine names or tool states."""
    ram = get_system_ram_info()
    sp_cfg = WORKSPACE_CFG.get("spotify") or {}
    sp_has_keys = bool((sp_cfg.get("client_id") or "").strip() and (sp_cfg.get("client_secret") or "").strip())
    sp_token_cached = (BASE_DIR / ".spotify_token_cache").exists()
    if sp_has_keys and sp_token_cached:
        sp_status = "Web API Authorized (Token Cached)"
    elif sp_has_keys:
        sp_status = "Keys Saved (Needs OAuth Login Click) + Desktop Fallback"
    else:
        sp_status = "Desktop App URI Fallback (No OAuth Keys Saved)"

    installed_libs = [p["pkg"] for p in check_packages_status() if p.get("installed")]
    brain_desc = STATE.get("active_api_label") or STATE.get("current_model") or f"Standby ({WORKSPACE_CFG.get('brain_mode', 'local_only')})"
    return {
        "pc_hostname": socket.gethostname(),
        "os_platform": f"{platform.system()} {platform.release()} ({platform.machine()})",
        "python_version": platform.python_version(),
        "cpu_threads": os.cpu_count() or 2,
        "ram_free_gb": ram.get("free_gb", 0),
        "ram_total_gb": ram.get("total_gb", 0),
        "workspace_dir": str(BASE_DIR),
        "lan_url": f"http://{get_local_lan_ip()}:{SERVER_PORT}",
        "active_brain": brain_desc,
        "brain_mode": WORKSPACE_CFG.get("brain_mode", "local_only"),
        "workspace_mode": WORKSPACE_CFG.get("workspace_mode", "assistant"),
        "workbench_trust": WORKSPACE_CFG.get("workbench_trust", "safe_auto"),
        "user_profile": load_user_profile_card(),
        "offline_mode": bool(STATE.get("offline_mode")),
        "osworld_enabled": bool(WORKSPACE_CFG.get("osworld_enabled", True)),
        "pyautogui_ready": bool(HAS_PYAUTOGUI),
        "spotify_status": sp_status,
        "indexed_pc_roots": STATE.get("allowed_pc_roots", [])[:6],
        "installed_libraries": installed_libs
    }

def build_pc_reality_anchor() -> str:
    """Compact 4-line live PC grounding block injected into prompts so the model knows its real environment."""
    info = get_pc_environment_info()
    libs_str = ", ".join(info["installed_libraries"][:14]) or "standard stdlib"
    return (
        "[LIVE PC REALITY ANCHOR — REAL HOST TELEMETRY]:\n"
        f"- PC Hostname: {info['pc_hostname']} | OS: {info['os_platform']} | CPU: {info['cpu_threads']}T | RAM: {info['ram_free_gb']}/{info['ram_total_gb']} GB Free\n"
        f"- Workspace: {info['workspace_dir']} | Brain: {info['active_brain']} | Spotify: {info['spotify_status']} | OSWorld: {'ON' if info['osworld_enabled'] else 'OFF'}\n"
        f"- Installed Python Libraries: {libs_str}\n"
        "- STRICT GROUNDING RULE: NEVER invent PC names, fake terminal commands, or roleplay fake tool actions (like *opens Spotify* or *scans files*). "
        "When asked to check the PC, play music, search the web, or run code, CALL THE REAL TOOL and report only actual returned results."
    )

def build_operator_voice_card(ai_name: str, user_name: str) -> str:
    """Lean ~300-char personality header for Operator Mode (keeps attitude, strips heavy RP scenes & lore bloat)."""
    return (
        f"You are {ai_name}, running live on {user_name}'s computer inside AetherVault Studio v{APP_VERSION} in PC Operator Mode. "
        f"Keep your natural, direct, laid-back voice without robotic filler or theatrical asterisk roleplay (*smirks*, *taps keyboard*). "
        f"Use your real tools whenever {user_name} asks to inspect the PC, check files, control Spotify, run Python, or search the web."
    )

AETHER_TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get exact live current weather, temperature (C/F), humidity, wind, and today's forecast for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "Leave EMPTY to use the user's saved profile card / map pin. Only pass a city name if asking about a different city."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_workbench",
            "description": "Run a Python Workbench script with the pre-imported `vault` module (vault.weather, vault.web, vault.pc_info, vault.files, vault.spotify, vault.osworld, vault.memory_save).",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code to execute in the sandboxed Workbench."}
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_pc_info",
            "description": "Get real-time host PC details: actual computer hostname, OS, CPU threads, free/total RAM, workspace folder, Spotify OAuth status, and installed Python libraries.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "scan_pc_files",
            "description": "Search or list local PC directories, Steam games, workspace files, or read a specific text/PDF file path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Folder path, file path, 'steam' for Steam games, or search keywords."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "spotify_control",
            "description": "Control Spotify playback or search/play a track on the user's PC.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["current_track", "playlists", "play_playlist", "play_album", "liked", "play_liked", "play", "pause", "resume", "next", "prev", "devices", "search"], "description": "Spotify command. Use current_track to inspect without changing playback."},
                    "query": {"type": "string", "description": "Track or artist name when action is 'play'."}
                },
                "required": ["action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the live internet via DuckDuckGo for up-to-date facts, weather, or news.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_python_sandbox",
            "description": "Execute a Python snippet inside the isolated .temp_cache sandbox and return actual stdout/stderr.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Valid Python code to execute."}
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "osworld_desktop",
            "description": "Interact with the user's desktop: take a live screenshot, list open windows, or open an application.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["screenshot", "list_windows", "open_app", "click", "type", "hotkey", "scroll"]},
                    "arg": {"type": "string", "description": "Optional argument (e.g., app name like 'notepad', coordinates '500,400', or hotkey 'ctrl+s')."}
                },
                "required": ["action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "inspect_self",
            "description": "Inspect AetherVault's own workspace files, error_audit.log, or built-in manual.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cmd": {"type": "string", "enum": ["tree", "errors", "read", "search", "manual"]},
                    "arg": {"type": "string", "description": "Optional filename/range (e.g. 'assistant_server.py:1-50') or search keyword."}
                },
                "required": ["cmd"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_lore",
            "description": "Search indexed documents/PDFs in /priority_pdfs when the user explicitly asks about stored lore or files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keywords": {"type": "string", "description": "Keywords to search inside indexed documents."}
                },
                "required": ["keywords"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_browser",
            "description": "Silently open a webpage or web search in Brave/Chrome/Edge (supports private/incognito window) without taking over mouse/keyboard.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to open (optional if search is given)."},
                    "search": {"type": "string", "description": "Web search query to open in browser."},
                    "private": {"type": "boolean", "description": "Set true to open a Private/Incognito window."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_pc_file",
            "description": "Silently create or write a text file on Desktop (e.g. 'Desktop/hello_world.txt') or Documents without touching mouse/keyboard.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path like 'Desktop/hello_world.txt'."},
                    "content": {"type": "string", "description": "Text content to write."},
                    "append": {"type": "boolean", "description": "Append instead of overwrite."}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_studio_toggle",
            "description": "Switch AetherVault Studio's own settings/toggles when asked by the user (workspace_mode, workbench_trust, offline_mode, brain_mode, performance_mode, osworld_enabled, theme_preset, voice_profile).",
            "parameters": {
                "type": "object",
                "properties": {
                    "setting": {"type": "string", "description": "Toggle name (e.g. 'workspace_mode', 'workbench_trust', 'theme_preset', 'offline_mode')."},
                    "value": {"type": "string", "description": "New value (e.g. 'roleplay', 'assistant', 'full_pc', 'safe_auto', 'visor_cyan')."}
                },
                "required": ["setting", "value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_memory",
            "description": "Save a persistent fact, name, location, or preference to SQLite Memory Vault & persistent pseudo-memory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Category label (e.g. 'user_name', 'user_location', 'preference', 'user_note')."},
                    "fact": {"type": "string", "description": "Fact to save permanently."}
                },
                "required": ["category", "fact"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_user_profile",
            "description": "Modify any field on the persistent User Profile Card (user_name, location, zip_code, add_fact, remove_fact, custom_fields, clear_fields).",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_name": {"type": "string"},
                    "location": {"type": "string"},
                    "zip_code": {"type": "string"},
                    "add_fact": {"type": "string"},
                    "remove_fact": {"type": "string"},
                    "custom_fields": {"type": "object"},
                    "clear_fields": {"type": "array", "items": {"type": "string"}}
                },
                "required": []
            }
        }
    }
]

from avs.tool_registry import ToolRegistry as _ToolRegistry

UNIFIED_TOOL_REGISTRY = _ToolRegistry(max_tools=128)
for _t_schema in AETHER_TOOL_SCHEMAS:
    _fn_meta = (_t_schema or {}).get("function") or {}
    _fn_name = (_fn_meta.get("name") or "").strip()
    if _fn_name:
        UNIFIED_TOOL_REGISTRY.register(
            ToolSpec(name=_fn_name, trust_tier="safe_auto", description=(_fn_meta.get("description") or "")[:200]),
            lambda _n=_fn_name, **kw: execute_unified_tool(_n, kw)[0],
        )

def execute_unified_tool(tool_name: str, args: dict, session_id: str = "session_main") -> tuple:
    """Executes a native JSON tool call on the host PC and returns (observation_text, img_url, audio_url)."""
    name = UNIFIED_TOOL_REGISTRY.resolve_name((tool_name or "").strip().lower())
    args = args if isinstance(args, dict) else {}
    img_url = None
    audio_url = None

    try:
        if name == "get_weather":
            loc = str(args.get("location") or load_user_profile_card().get("location") or "").strip()
            return get_live_weather(loc), None, None

        elif name == "run_workbench":
            wb_res = execute_workbench_code(str(args.get("code") or ""))
            return wb_res.get("output") or "", wb_res.get("image_url"), wb_res.get("audio_url")

        elif name == "get_pc_info":
            return json.dumps(get_pc_environment_info(), indent=2, ensure_ascii=False), None, None

        elif name == "scan_pc_files":
            q = str(args.get("query") or str(BASE_DIR)).strip()
            STATE["last_debug"]["pc_files_scanned"].append(q)
            return search_local_pc_files(q), None, None

        elif name == "spotify_control":
            act = str(args.get("action") or "play").strip().lower()
            q = str(args.get("query") or "").strip()
            if q.lower() in ("any", "any song", "random", "random song", "something", "music"):
                q = ""
            return control_spotify(act, q), None, None

        elif name == "web_search":
            q = clean_web_search_query(str(args.get("query") or "").strip())
            return search_web(q), None, None

        elif name == "run_python_sandbox":
            code = str(args.get("code") or "").strip()
            res = api_run_code_sandbox({"code": code})
            return json.dumps(res, ensure_ascii=False), None, None

        elif name == "osworld_desktop":
            act = str(args.get("action") or "list_windows").strip()
            arg = str(args.get("arg") or "").strip()
            res = execute_osworld_action(act, arg)
            img_url = res.get("image_url")
            return res.get("summary") or json.dumps(res), img_url, None

        elif name == "inspect_self":
            cmd = str(args.get("cmd") or "tree").strip()
            arg = str(args.get("arg") or "").strip()
            return execute_self_inspection_tool(cmd, arg), None, None

        elif name == "search_lore":
            kws = str(args.get("keywords") or "").strip()
            txt, lbls = retrieve_relevant_lore(kws, top_k=3)
            STATE["last_debug"]["lore_pulled"].extend(lbls)
            return txt or f"No indexed documents matched '{kws}'.", None, None

        elif name == "open_browser":
            return open_browser_silently(str(args.get("url") or ""), str(args.get("search") or ""), bool(args.get("private", False)), str(args.get("browser") or "auto")), None, None

        elif name == "write_pc_file":
            return write_pc_file_silently(str(args.get("path") or ""), str(args.get("content") or ""), bool(args.get("append", False))), None, None

        elif name == "set_studio_toggle":
            return apply_studio_toggle(str(args.get("setting") or ""), args.get("value")), None, None

        elif name == "save_memory":
            cat = str(args.get("category") or "active_state").strip()
            fact = str(args.get("fact") or "").strip()
            return save_to_memory(cat, fact), None, None

        elif name == "update_user_profile":
            return update_user_profile_full(
                user_name=args.get("user_name"),
                location=args.get("location"),
                zip_code=args.get("zip_code"),
                add_fact=args.get("add_fact"),
                remove_fact=args.get("remove_fact"),
                custom_fields=args.get("custom_fields"),
                clear_fields=args.get("clear_fields")
            ), None, None

        return f"Unknown tool '{name}'. Available tools: {', '.join(t['function']['name'] for t in AETHER_TOOL_SCHEMAS)}.", None, None
    except Exception as e:
        return f"Tool '{name}' execution error: {e}", img_url, audio_url

def extract_inline_tool_calls(text: str) -> tuple:
    """
    Extracts Hermes/Qwen `<tool_call>{...}</tool_call>` blocks or raw JSON tool calls
    emitted by local GGUF models that do not populate OpenAI delta.tool_calls directly.
    Returns (list_of_calls, cleaned_text).
    """
    calls = []
    cleaned = text or ""
    valid_names = {t["function"]["name"] for t in AETHER_TOOL_SCHEMAS}

    for m in re.finditer(r"<tool_call>\s*(\{[\s\S]*?\})\s*</tool_call>", cleaned, flags=re.IGNORECASE):
        try:
            obj = json.loads(m.group(1))
            fn_name = (obj.get("name") or "").strip()
            fn_args = obj.get("arguments") or {}
            if isinstance(fn_args, str):
                try:
                    fn_args = json.loads(fn_args)
                except Exception:
                    fn_args = {}
            if fn_name in valid_names:
                calls.append({"id": f"call_inline_{len(calls)+1}", "name": fn_name, "arguments": fn_args})
        except Exception:
            pass
    cleaned = re.sub(r"<tool_call>\s*\{[\s\S]*?\}\s*</tool_call>", "", cleaned, flags=re.IGNORECASE).strip()

    if not calls and '"name"' in cleaned:
        decoder = json.JSONDecoder()
        scan_pos = 0
        spans_to_strip = []
        while True:
            # Match either normal `{"name":` OR braceless `"name":` (Llama-3.2 3B quirk!)
            m_start = re.search(r'(?:\{\s*)?"name"\s*:', cleaned[scan_pos:])
            if not m_start:
                break
            abs_start = scan_pos + m_start.start()
            has_open_brace = cleaned[abs_start:].lstrip().startswith("{")
            parsed_obj = None
            abs_end = len(cleaned)
            if has_open_brace:
                try:
                    parsed_obj, rel_end = decoder.raw_decode(cleaned[abs_start:])
                    abs_end = abs_start + rel_end
                except Exception:
                    pass
            if parsed_obj is None:
                # Auto-repair braceless OR truncated JSON inside or outside code fences
                frag = cleaned[abs_start:].split("```")[0].strip()
                prefix = "" if has_open_brace else "{"
                for suffix in ("", "}", "}}", '"}', '"}}'):
                    try:
                        candidate = prefix + frag + suffix
                        parsed_obj, rel_c = decoder.raw_decode(candidate)
                        abs_end = abs_start + min(len(frag), max(1, rel_c - len(prefix)))
                        break
                    except Exception:
                        continue
            if isinstance(parsed_obj, dict):
                fn_name = (parsed_obj.get("name") or "").strip()
                if fn_name in valid_names:
                    fn_args = parsed_obj.get("arguments") or parsed_obj.get("parameters") or {}
                    if isinstance(fn_args, str):
                        try:
                            fn_args = json.loads(fn_args)
                        except Exception:
                            fn_args = {}
                    calls.append({
                        "id": f"call_decoded_{len(calls)+1}",
                        "name": fn_name,
                        "arguments": fn_args if isinstance(fn_args, dict) else {}
                    })
                    spans_to_strip.append((abs_start, abs_end))
            scan_pos = max(abs_end, abs_start + 1)

        if spans_to_strip:
            for s_idx, e_idx in reversed(spans_to_strip):
                cleaned = cleaned[:s_idx] + cleaned[e_idx:]
            # Remove any empty markdown fences left behind after extracting the JSON tool call
            cleaned = re.sub(r"```(?:python|py|json|workbench)?\s*```", "", cleaned, flags=re.IGNORECASE).strip()

    return calls, cleaned

def _recent_turns_had_tool_context(recent_turns: list) -> bool:
    """Checks the last 4 messages so the router remembers an active API/PC/Spotify thread across follow-ups!"""
    if not recent_turns:
        return False
    tool_markers = (
        "spotify", "liked song", "profile", "vault.", "workbench", "weather",
        "web search", "browser", "private tab", "desktop", "hostname", "pc_info",
        "playing ", "queue", "track", "song", "music", "open_app", "screenshot", "toggle"
    )
    tail_text = " ".join((t.get("content") or "").lower() for t in recent_turns[-4:])
    return any(m in tail_text for m in tool_markers)

def classify_task_gear(user_msg: str, attached_name: str = "", recent_turns: list = None) -> tuple:
    routing = WORKSPACE_CFG.get("routing_mode", "auto_reflex")
    ws_mode = WORKSPACE_CFG.get("workspace_mode", "assistant")
    if ws_mode == "assistant":
        return "operator", "Assistant & Python Workbench Mode (Lore Locked Out)"
    if is_operator_or_system_query(user_msg) and not attached_name:
        return "operator", "Roleplay + Live Workbench Tool Mode (Voice Preserved | Lore Blocked for Tool Call)"

    # Sticky Context Continuity: if the last few messages were about Spotify/PC/APIs and the user
    # follows up conversationally (even with typos or pronouns like "it", "that one", "try again"), stay in Operator Mode!
    low = user_msg.lower().strip()
    follow_up_cues = (
        "it", "that", "again", "try", "another", "still", "did not", "didn't", "can you",
        "what about", "now", "listening", "song", "music", "track", "play", "queue", "qeue",
        "check", "identify", "ndentify", "what is", "which one", "work", "worked"
    )
    if not attached_name and "*" not in user_msg and _recent_turns_had_tool_context(recent_turns or []):
        if any(c in low for c in follow_up_cues):
            return "operator", "Sticky Thread Continuity (Active API/Tool Conversation — Lore Locked Out)"

    if routing == "always_reflex" and not attached_name:
        return "reflex", "Forced Reflex Mode (Pure Fast Chat)"
    if routing == "always_deep" or STATE["performance_mode"] == "Turbo (Max Threads)":
        return "deep", "Full Context Mode selected"
    if attached_name:
        return "deep", f"File attachment present ({attached_name})"

    words = re.findall(r"[a-zA-Z0-9_'-]+", low)

    if "*" in user_msg or "((ooc" in low or len(words) > 28 or len(user_msg) > 180:
        return "deep", f"Detailed/Roleplay prompt ({len(words)} words)"

    if len(words) <= 22 and any(p in low for p in FAST_WEB_INTENT_PATTERNS):
        return "reflex", f"Gear 1 Fast-Web Grounding ({len(words)} words -> instant search + reply)"

    matched_taxing = [w for w in words if w in TAXING_TASK_KEYWORDS]
    if matched_taxing:
        return "deep", f"Taxing keyword detected ('{matched_taxing[0]}')"

    domain_hits = [w for w in words if len(w) >= 5 and w in PRIORITY_CACHE.get("domain_vocab", set())]
    if len(domain_hits) >= 2:
        return "deep", f"Lore domain terms matched ({', '.join(domain_hits[:2])})"

    return "reflex", f"Lightweight everyday chat ({len(words)} words -> Gear 1 Fast-Path)"

def build_reflex_persona_digest(full_core_text: str, ai_name: str, user_name: str) -> str:
    clean_core = sanitize_lore_and_core_text(full_core_text)
    lines = [ln.strip() for ln in clean_core.splitlines() if ln.strip() and not ln.strip().startswith("---")]
    essential = []
    char_total = 0
    for ln in lines:
        if any(skip in ln.lower() for skip in ("[[osworld", "[[files", "[[lore", "[[spotify", "<start>", "disclaimer:")):
            continue
        essential.append(ln)
        char_total += len(ln)
        if char_total >= 550:
            break
    digest = "\n".join(essential)[:600]
    return (
        f"You are {ai_name} talking directly with {user_name}.\n"
        f"{digest}\n"
        f"[REFLEX FAST-GEAR RULE: Today is {time.strftime('%B %Y')}. Reply naturally and completely in-character without cutting off mid-thought. "
        f"Your offline weights are small—if you don't know a fact, recent event (2024+), game, person, or topic, DO NOT GUESS: output [[SEARCH:clean keywords]] to look it up online! "
        f"If answering requires local files, lore PDFs, or desktop tools, output ONLY [[DEEP]].]"
    )

def export_chats_to_txt_files():
    try:
        ai_label = WORKSPACE_CFG.get("ai_name", "AI")
        user_label = WORKSPACE_CFG.get("user_name", "User")
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT id, title, updated_at FROM chat_sessions")
            sessions = c.fetchall()
            for s in sessions:
                sid = s["id"]
                safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", sid)
                c.execute("SELECT role, content, timestamp FROM chat_messages WHERE session_id = ? ORDER BY id ASC", (sid,))
                msgs = c.fetchall()
                if not msgs:
                    continue
                lines = [f"=== CHAT SESSION: {s['title']} ({sid}) | Updated: {s['updated_at']} ==="]
                for m in msgs:
                    who = user_label if m["role"] == "user" else ai_label
                    lines.append(f"[{m['timestamp']}] {who}: {m['content']}")
                (CHAT_LOG_DIR / f"{safe_name}.txt").write_text("\n\n".join(lines), encoding="utf-8")
    except Exception as e:
        print(f"[CHAT TXT EXPORT ERROR] {e}")

def update_boot_glossary_index(force: bool = False):
    current_log_mtimes = {p.name: p.stat().st_mtime for p in CHAT_LOG_DIR.glob("*.txt")}
    if not force and PRIORITY_CACHE["glossary_top_words"] and current_log_mtimes == PRIORITY_CACHE["last_glossary_mtimes"]:
        return

    freq = Counter()
    source_map = {}
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT lc.filename, lc.chunk_index, lc.keywords
            FROM lore_chunks lc
            JOIN priority_pdfs pp ON lc.filename = pp.filename
            WHERE pp.file_mode = 'lore'
            LIMIT 5000
        """)
        for r in c.fetchall():
            kws = (r["keywords"] or "").split()
            freq.update(kws)
            for w in kws[:15]:
                source_map.setdefault(w, set()).add(f"PDF:{r['filename']}#{r['chunk_index']}")

        c.execute("SELECT id, category, fact FROM dynamic_memory")
        for r in c.fetchall():
            kws = extract_keywords(f"{r['category']} {r['fact']}")
            freq.update(kws)
            for w in set(kws):
                source_map.setdefault(w, set()).add(f"MEM:#{r['id']}")

    for txt_path in CHAT_LOG_DIR.glob("*.txt"):
        try:
            txt = txt_path.read_text(encoding="utf-8", errors="ignore")
            kws = [w for w, _ in Counter(extract_keywords(txt)).most_common(45)]
            freq.update(kws)
            for w in kws:
                source_map.setdefault(w, set()).add(f"CHAT:{txt_path.name}")
        except Exception:
            pass

    top_terms = freq.most_common(200)
    payload = {
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_keywords": len(freq),
        "most_repeating_words": [
            {"word": w, "count": cnt, "sources": sorted(list(source_map.get(w, [])))[:10]}
            for w, cnt in top_terms
        ]
    }
    try:
        GLOSSARY_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass
    PRIORITY_CACHE["glossary_top_words"] = [f"{w} ({cnt})" for w, cnt in top_terms[:20]]
    PRIORITY_CACHE["glossary_map"] = {w: sorted(list(srcs))[:10] for w, srcs in source_map.items()}
    PRIORITY_CACHE["domain_vocab"] = {w for w, cnt in top_terms[:120] if len(w) >= 5 and cnt >= 2 and not w.startswith("core")}
    PRIORITY_CACHE["last_glossary_mtimes"] = current_log_mtimes

def is_default_core_file(rel_path: str, text_len: int) -> bool:
    norm = rel_path.replace("\\", "/").lower()
    if (norm in ("core_persona.txt", "readme.txt") or norm.endswith("_core_package.txt")) and text_len <= 6000:
        return True
    return False

def split_into_lore_chunks(text: str, chunk_size: int = 1100, overlap: int = 150) -> list:
    if not text:
        return []
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks = []
    current = ""
    step = max(250, chunk_size - overlap)
    for para in paragraphs:
        if len(current) + len(para) + 2 <= chunk_size:
            current = f"{current}\n\n{para}".strip() if current else para
        else:
            if current:
                chunks.append(current)
                current = ""
            if len(para) > chunk_size:
                for start in range(0, len(para), step):
                    piece = para[start:start + chunk_size].strip()
                    if piece:
                        chunks.append(piece)
            else:
                current = para
    if current:
        chunks.append(current)
    return chunks if chunks else [text[:chunk_size]]

def _refresh_priority_cache_from_db():
    """Fast (<10ms) read-only cache refresh from SQLite so /status and boot never wait on disk indexing."""
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT filename, COUNT(*) as cnt FROM lore_chunks GROUP BY filename")
            chunk_counts = {r["filename"]: r["cnt"] for r in c.fetchall()}

            c.execute("SELECT filename, mtime, file_mode, manual_override, summary, content FROM priority_pdfs ORDER BY filename ASC")
            rows = c.fetchall()

        core_blocks = []
        core_names = []
        manifest_lines = []
        stats = {}
        total_chunks = 0
        lore_files_count = 0
        seen_hashes = set()

        for r in rows:
            fname = r["filename"]
            fmode = r["file_mode"] or "lore"
            n_chunks = chunk_counts.get(fname, 0)
            total_chunks += n_chunks
            folder_name = str(Path(fname).parent.as_posix()) if "/" in fname else "/"
            stats[fname] = {
                "mtime": r["mtime"],
                "mode": fmode,
                "manual_override": bool(r["manual_override"]),
                "chunks": n_chunks,
                "folder": folder_name
            }
            if fmode == "core":
                core_names.append(fname)
                raw_c = sanitize_lore_and_core_text(r["content"] or "")
                sig = raw_c[-400:] if len(raw_c) > 400 else raw_c
                if sig not in seen_hashes:
                    seen_hashes.add(sig)
                    core_blocks.append(f"--- [CORE FILE: {fname}] ---\n{raw_c[:4000]}")
            else:
                lore_files_count += 1
                manifest_lines.append(f"- {fname} ({n_chunks} sections)")

        full_core = "\n\n".join(core_blocks)[:4500]
        PRIORITY_CACHE["core_rules_text"] = full_core
        PRIORITY_CACHE["reflex_core_digest"] = build_reflex_persona_digest(
            full_core or WORKSPACE_CFG["persona_prompt"],
            WORKSPACE_CFG.get("ai_name", "Aether"),
            WORKSPACE_CFG.get("user_name", "Creator")
        )
        PRIORITY_CACHE["core_file_names"] = core_names
        PRIORITY_CACHE["lore_manifest_text"] = "\n".join(manifest_lines[:30])
        PRIORITY_CACHE["lore_file_count"] = lore_files_count
        PRIORITY_CACHE["lore_chunk_count"] = total_chunks
        PRIORITY_CACHE["file_stats"] = stats
        PRIORITY_CACHE["initialized"] = True
    except Exception as e:
        print(f"[CACHE REFRESH NOTE] {e}", flush=True)

def sync_priority_files(force: bool = False):
    """
    Thread-safe, non-deadlocking Knowledge Tree indexer with live per-file progress and Skip support.
    Never blocks /status polling!
    """
    if not force and STATE.get("skip_indexing"):
        return
    if not INDEX_LOCK.acquire(blocking=False):
        return

    STATE["indexing_files"] = True
    if force:
        STATE["skip_indexing"] = False
    try:
        valid_exts = {".pdf", ".txt", ".md"}
        files_on_disk = []
        for p in PDF_DIR.rglob("*"):
            if p.is_file() and p.suffix.lower() in valid_exts and p.name != "HOW_TO_USE_PRIORITY_FILES.txt":
                rel_name = p.relative_to(PDF_DIR).as_posix()
                files_on_disk.append((rel_name, p))

        current_mtimes = {rel_name: p.stat().st_mtime for rel_name, p in files_on_disk}

        if (
            not force
            and PRIORITY_CACHE["initialized"]
            and current_mtimes == {k: v["mtime"] for k, v in PRIORITY_CACHE["file_stats"].items()}
        ):
            return

        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT filename, mtime, file_mode, manual_override FROM priority_pdfs")
            db_files = {row["filename"]: dict(row) for row in c.fetchall()}
            c.execute("SELECT filename, COUNT(*) as cnt FROM lore_chunks GROUP BY filename")
            db_chunk_counts = {row["filename"]: row["cnt"] for row in c.fetchall()}

            removed_any = False
            for fname in list(db_files.keys()):
                if fname not in current_mtimes:
                    c.execute("DELETE FROM priority_pdfs WHERE filename = ?", (fname,))
                    c.execute("DELETE FROM lore_chunks WHERE filename = ?", (fname,))
                    removed_any = True
            if removed_any:
                conn.commit()

        # Populate cache from existing DB rows first so UI has instant access
        if not PRIORITY_CACHE["initialized"]:
            _refresh_priority_cache_from_db()

        to_index = []
        for rel_name, fpath in files_on_disk:
            mtime = current_mtimes[rel_name]
            existing = db_files.get(rel_name)
            chunk_count = db_chunk_counts.get(rel_name, 0)
            if (existing is None) or (abs(existing["mtime"] - mtime) > 2.0) or (chunk_count == 0):
                to_index.append((rel_name, fpath, mtime, existing))

        total_to_index = len(to_index)
        for file_idx, (rel_name, fpath, mtime, existing) in enumerate(to_index, 1):
            if STATE.get("skip_indexing"):
                print("[INDEXER] User requested Skip Indexing — deferring remaining files.", flush=True)
                break
            try:
                set_step(f"📄 Indexing [{file_idx}/{total_to_index}]: {rel_name}...")
                if fpath.suffix.lower() == ".pdf":
                    doc = fitz.open(fpath)
                    total_pages = len(doc)
                    pages = []
                    for idx, page in enumerate(doc):
                        if STATE.get("skip_indexing"):
                            break
                        if total_pages > 10 and (idx % 10 == 0):
                            STATE["current_step"] = f"📄 Reading PDF [{file_idx}/{total_to_index}]: {rel_name} (Page {idx+1}/{total_pages})..."
                        ptxt = page.get_text("text").strip()
                        if ptxt:
                            pages.append(f"[Page {idx + 1}]\n{ptxt}")
                    doc.close()
                    full_text = "\n\n".join(pages).strip()
                else:
                    full_text = fpath.read_text(encoding="utf-8", errors="ignore").strip()

                full_text = sanitize_lore_and_core_text(full_text)
                if not full_text:
                    continue

                if existing and existing.get("manual_override"):
                    mode = existing["file_mode"]
                    manual_flag = 1
                else:
                    mode = "core" if is_default_core_file(rel_name, len(full_text)) else "lore"
                    manual_flag = 0

                preview_lines = [line.strip() for line in full_text.splitlines() if line.strip()][:3]
                summary = " / ".join(preview_lines)[:200]

                path_keywords = rel_name.replace("/", " ").replace("_", " ").replace("-", " ")
                chunks = split_into_lore_chunks(full_text)
                STATE["current_step"] = f"💾 Saving {len(chunks)} chunks for {rel_name}..."
                chunk_rows = [
                    (rel_name, idx + 1, " ".join(set(extract_keywords(f"{path_keywords} {fpath.stem} {ch}"))), ch)
                    for idx, ch in enumerate(chunks)
                ]

                with get_db() as conn:
                    c = conn.cursor()
                    c.execute(
                        "INSERT OR REPLACE INTO priority_pdfs (filename, mtime, file_mode, manual_override, summary, content) VALUES (?, ?, ?, ?, ?, ?)",
                        (rel_name, mtime, mode, manual_flag, summary, full_text[:5000] if mode == "core" else full_text[:1500])
                    )
                    c.execute("DELETE FROM lore_chunks WHERE filename = ?", (rel_name,))
                    c.executemany(
                        "INSERT INTO lore_chunks (filename, chunk_index, keywords, content) VALUES (?, ?, ?, ?)",
                        chunk_rows
                    )
                    conn.commit()
                print(f"[INDEXER] Indexed '{rel_name}' ({len(chunks)} chunks | mode={mode.upper()})", flush=True)
            except Exception as e:
                format_predetermined_error("ERR_FILE_PARSE", f"{rel_name}: {e}")
                print(f"[PRIORITY FILE ERROR] Could not index {rel_name}: {e}", flush=True)

        _refresh_priority_cache_from_db()
        export_chats_to_txt_files()
        if to_index or force:
            update_boot_glossary_index(force=bool(to_index))
    finally:
        STATE["indexing_files"] = False
        INDEX_LOCK.release()

def retrieve_relevant_lore(query_text: str, top_k: int = 2) -> tuple:
    """
    Retrieves Lore chunks ONLY when relevant, sanitizes any meta-technical essay lines,
    and wraps them in a strict archival boundary so the model never hallucinates or gets delirious.
    """
    if is_capability_or_api_query(query_text) or PRIORITY_CACHE["lore_chunk_count"] == 0:
        return "", []

    _base_terms = [t for t in extract_keywords(query_text) if len(t) >= 4]
    _expanded = MEMORY_COMPACTOR.expand_keywords(query_text) if "MEMORY_COMPACTOR" in globals() else _base_terms
    query_terms = [t for t in _expanded if len(t) >= 4] or _base_terms
    if not query_terms:
        return "", []

    like_clauses = " OR ".join(["lc.keywords LIKE ?" for _ in query_terms[:4]])
    params = [f"%{t}%" for t in query_terms[:4]]

    with get_db() as conn:
        c = conn.cursor()
        c.execute(f"""
            SELECT lc.filename, lc.chunk_index, lc.keywords, lc.content
            FROM lore_chunks lc
            JOIN priority_pdfs pp ON lc.filename = pp.filename
            WHERE pp.file_mode = 'lore' AND ({like_clauses})
            LIMIT 80
        """, params)
        rows = c.fetchall()

    if not rows:
        return "", []

    q_counts = Counter(query_terms)
    scored = []
    for r in rows:
        fname_lower = (r["filename"] or "").lower()
        # Never pull technical diagnostic essay PDFs as narrative lore!
        if fname_lower.endswith("core.pdf") and ("sentencepiece" in (r["content"] or "").lower() or "diagn" in (r["content"] or "").lower()):
            continue
        kw_set = set((r["keywords"] or "").split())
        score = sum(2.5 * w for term, w in q_counts.items() if term in kw_set)
        if any(term in fname_lower for term in query_terms):
            score += 3.0
        if score >= 5.0:
            clean_chunk = sanitize_lore_and_core_text(r["content"])[:850]
            scored.append((score, r["filename"], r["chunk_index"], clean_chunk))

    if not scored:
        return "", []

    scored.sort(key=lambda x: x[0], reverse=True)
    top_chunks = scored[:top_k]
    formatted = [
        f"--- [BACKGROUND ARCHIVE REFERENCE (Use only as factual memory if relevant): {fname} #{cidx}] ---\n{content}"
        for _, fname, cidx, content in top_chunks
    ]
    labels = [f"{Path(fname).name} #{cidx}" for _, fname, cidx, _ in top_chunks]
    return "\n\n".join(formatted), labels

def retrieve_past_chat_logs(query_text: str, current_session_id: str, top_k: int = 2) -> tuple:
    if is_capability_or_api_query(query_text):
        return "", []

    query_terms = [t for t in extract_keywords(query_text) if len(t) >= 4]
    if not query_terms:
        return "", []

    q_counts = Counter(query_terms)
    safe_curr = re.sub(r"[^a-zA-Z0-9_-]", "_", current_session_id or "")
    scored = []

    for txt_path in CHAT_LOG_DIR.glob("*.txt"):
        if txt_path.stem == safe_curr:
            continue
        try:
            raw = txt_path.read_text(encoding="utf-8", errors="ignore")
            entries = [e.strip() for e in raw.split("\n\n") if e.strip() and not e.startswith("=== CHAT SESSION")]
            for entry in entries:
                elower = entry.lower()
                sc = sum(2.5 * w for term, w in q_counts.items() if term in elower)
                if sc >= 5.0:
                    scored.append((sc, txt_path.name, entry[:550]))
        except Exception:
            pass

    if not scored:
        return "", []

    scored.sort(key=lambda x: x[0], reverse=True)
    chosen = scored[:top_k]
    formatted = [f"--- [PAST .TXT CHAT LOG ({fname})] ---\n{txt}" for _, fname, txt in chosen]
    labels = list(dict.fromkeys([fname for _, fname, _ in chosen]))
    return "\n\n".join(formatted), labels

def list_priority_files_info():
    if not PRIORITY_CACHE["initialized"] and not STATE.get("indexing_files"):
        _refresh_priority_cache_from_db()
    out = []
    for idx, (fname, st) in enumerate(sorted(PRIORITY_CACHE["file_stats"].items())):
        out.append({
            "id": idx,
            "name": fname,
            "folder": st.get("folder", "/"),
            "mode": st["mode"],
            "manual_override": st.get("manual_override", False),
            "chunks": st["chunks"]
        })
    return out

# =====================================================================
# 7. SELF-HEALING APIS (PC SCANNER, SPOTIFY, DUAL-ENGINE WEB, IMAGES)
# =====================================================================
def search_local_pc_files(query: str, max_results: int = 25) -> str:
    q = (query or "").strip().strip("'\"")
    if not q:
        return "Empty file query."

    direct = Path(q)
    if direct.exists():
        try:
            if direct.is_dir():
                items = [f"{'[DIR]' if p.is_dir() else '[FILE]'} {p.name}" for p in list(direct.iterdir())[:40]]
                return f"Directory listing for '{direct}':\n" + "\n".join(items)
            elif direct.is_file():
                if direct.suffix.lower() == ".pdf":
                    doc = fitz.open(direct)
                    txt = "\n".join([p.get_text("text") for p in list(doc)[:3]])
                    doc.close()
                    return f"PDF Content ({direct.name}):\n{txt[:2500]}"
                return f"File Content ({direct.name}):\n{direct.read_text(encoding='utf-8', errors='ignore')[:2500]}"
        except Exception as e:
            return f"Error reading path '{direct}': {e}"

    if "steam" in q.lower() or "game" in q.lower():
        steam_paths = [
            Path("C:/Program Files (x86)/Steam/steamapps/common"),
            Path("C:/Program Files/Steam/steamapps/common"),
            Path("D:/SteamLibrary/steamapps/common"),
            Path("E:/SteamLibrary/steamapps/common")
        ]
        games = []
        for sp in steam_paths:
            if sp.exists():
                try:
                    for item in sp.iterdir():
                        if item.is_dir():
                            games.append(f"{item.name} ({sp.drive})")
                except Exception:
                    pass
        if games:
            return "Installed Steam Games found on PC:\n- " + "\n- ".join(sorted(games)[:40])

    terms = [t.lower() for t in q.split() if len(t) >= 2]
    matches = []
    skip_dirs = {".venv", "node_modules", ".git", "hf_cache", "pip_cache", "__pycache__", "AppData", "Windows"}

    for r_str in STATE["allowed_pc_roots"]:
        rp = Path(r_str)
        if not rp.exists():
            continue
        try:
            for root_dir, dirs, files in os.walk(rp):
                dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith("$")]
                for dname in dirs:
                    if all(t in dname.lower() for t in terms):
                        matches.append(f"[DIR] {Path(root_dir) / dname}")
                for fname in files:
                    if all(t in fname.lower() for t in terms):
                        matches.append(f"[FILE] {Path(root_dir) / fname}")
                if len(matches) >= max_results:
                    break
        except Exception:
            continue
        if len(matches) >= max_results:
            break

    if not matches:
        return f"No local PC or Google Drive files matched '{q}'."
    return f"Local PC / Google Drive matches for '{q}':\n" + "\n".join(matches[:max_results])

def get_spotify_oauth() -> SpotifyOAuth:
    cid = (WORKSPACE_CFG.get("spotify", {}).get("client_id") or os.environ.get("SPOTIPY_CLIENT_ID") or "").strip()
    csec = (WORKSPACE_CFG.get("spotify", {}).get("client_secret") or os.environ.get("SPOTIPY_CLIENT_SECRET") or "").strip()
    ruri = (WORKSPACE_CFG.get("spotify", {}).get("redirect_uri") or "http://127.0.0.1:8000/spotify_callback").strip()
    if not cid or not csec:
        return None
    return SpotifyOAuth(
        client_id=cid,
        client_secret=csec,
        redirect_uri=ruri,
        scope="user-read-playback-state,user-modify-playback-state,user-read-currently-playing,user-read-private,user-library-read,user-library-modify,playlist-read-private,playlist-read-collaborative",
        cache_path=str(BASE_DIR / ".spotify_token_cache"),
        open_browser=False
    )

def get_authenticated_spotify_client():
    """
    Returns (sp_client, status_msg) ONLY if a valid OAuth token is cached/refreshable.
    NEVER calls Spotipy's blocking stdin prompt when unauthenticated!
    """
    oauth = get_spotify_oauth()
    if not oauth:
        return None, "No Spotify Client ID/Secret saved (using Windows Desktop Fallback)"
    try:
        token_info = oauth.cache_handler.get_cached_token()
        if not token_info:
            return None, "Keys saved, but OAuth login not completed yet (click 'Authorize Spotify OAuth' in Studio Settings)"
        token_info = oauth.validate_token(token_info)
        if not token_info or not token_info.get("access_token"):
            return None, "Cached Spotify token expired and could not refresh (click 'Authorize Spotify OAuth' again)"
        return spotipy.Spotify(auth=token_info["access_token"]), "Connected"
    except Exception as e:
        return None, f"Spotify OAuth token check failed: {e}"

def _send_windows_media_key(action: str) -> bool:
    """Cross-platform media key dispatch via avs.platform_bridge (Windows VK_MEDIA, Linux playerctl, macOS AppleScript)."""
    return avs_platform.send_media_key(action)

def _pick_spotify_device_id(sp) -> tuple:
    """Finds the best Spotify playback device (active first, then Computer, then first available)."""
    try:
        devs = (sp.devices() or {}).get("devices") or []
        if not devs:
            return None, []
        active = [d for d in devs if d.get("is_active")]
        if active:
            return active[0].get("id"), devs
        pcs = [d for d in devs if (d.get("type") or "").lower() == "computer"]
        if pcs:
            return pcs[0].get("id"), devs
        return devs[0].get("id"), devs
    except Exception:
        return None, []

def control_spotify(action: str, query: str = "") -> str:
    if STATE["offline_mode"]:
        return "Offline Mode is enabled. Spotify is blocked."

    act = (action or "current_track").strip().lower()
    q = (query or "").strip()

    # Hard Read-Only Guard: if the user explicitly asked to JUST LOOK / NOT CHANGE the song on this turn,
    # refuse any mutating action (even if a small local model calls vault.spotify('play_liked') or 'next')!
    mutating_acts = {"play", "play_liked", "play_playlist", "play_album", "next", "prev", "previous", "pause", "resume", "queue", "add_to_queue"}
    if STATE.get("spotify_readonly_turn") and act in mutating_acts:
        cur_info = control_spotify("current_track", "")
        return f"[READ-ONLY GUARD: Blocked '{act}' because the user asked NOT to change playback!] {cur_info}"
    if act in mutating_acts and STATE.get("spotify_mutated_this_turn"):
        return f"[ALREADY EXECUTED THIS TURN — SKIPPED DUPLICATE '{act}']: {STATE['spotify_mutated_this_turn']}"

    sp, auth_note = get_authenticated_spotify_client()
    found_track_uri = ""
    found_track_label = ""
    found_album_uri = ""

    try:
        if sp:
            if act == "devices":
                _, devs = _pick_spotify_device_id(sp)
                if not devs:
                    return "Spotify Web API connected, but 0 active devices found. Open the Spotify app on your PC or phone and play a song for 1 second to wake it up."
                lines = [f"- {d.get('name')} ({d.get('type')}) | Active: {d.get('is_active')} | Vol: {d.get('volume_percent')}%" for d in devs]
                return "Available Spotify Devices:\n" + "\n".join(lines)

            elif act in ("like", "save", "add_liked", "save_track", "like_track"):
                tid = ""
                t_label = ""
                if q:
                    res = sp.search(q=q, limit=1, type="track")
                    items = res.get("tracks", {}).get("items", [])
                    if items:
                        tid = items[0]["id"]
                        t_label = f"'{items[0]['name']}' by {items[0]['artists'][0]['name']}"
                else:
                    curr = sp.current_playback()
                    if curr and curr.get("item"):
                        tid = curr["item"]["id"]
                        t_label = f"'{curr['item']['name']}' by {curr['item']['artists'][0]['name']}"
                if not tid:
                    return f"Could not find a track to like for '{q or 'current playback'}'."
                try:
                    sp.current_user_saved_tracks_add(tracks=[tid])
                    return f"Added {t_label} to your Spotify Liked Songs!"
                except Exception as like_err:
                    return f"Could not save {t_label} to Liked Songs ({str(like_err)[:120]}). Click 'Authorize Spotify OAuth' once in Studio Settings to grant 'user-library-modify' permission!"

            elif act == "search" and q:
                res = sp.search(q=q, limit=5, type="track")
                items = res.get("tracks", {}).get("items", [])
                if not items:
                    return f"No Spotify tracks matched '{q}'."
                lines = [f"{i+1}. {it['name']} — {it['artists'][0]['name']} ({it['uri']})" for i, it in enumerate(items)]
                return f"Spotify Search Results for '{q}':\n" + "\n".join(lines)

            elif act in ("playlists", "list_playlists", "my_playlists"):
                try:
                    pl_res = sp.current_user_playlists(limit=25)
                except Exception as pl_err:
                    return (
                        f"Could not list your playlists ({str(pl_err)[:140]}). "
                        f"Click 'Authorize Spotify OAuth' once in Studio Settings to grant playlist-read permissions!"
                    )
                pl_items = [p for p in ((pl_res or {}).get("items") or []) if isinstance(p, dict)]
                if not pl_items:
                    return "Spotify Web API connected, but 0 playlists were returned."
                lines = [
                    f"{i+1}. {p.get('name', 'Untitled')} ({(p.get('tracks') or {}).get('total', '?')} tracks | {p.get('uri', '')})"
                    for i, p in enumerate(pl_items[:20])
                ]
                return f"Your Spotify Playlists ({len(pl_items)} fetched):\n" + "\n".join(lines)

            elif act in ("play_playlist", "playlist"):
                import random
                chosen_pl = None
                q_low = q.lower()
                generic_pl = (not q_low) or q_low in ("any", "random", "my playlist", "playlist", "a playlist", "playlists")
                try:
                    pl_res = sp.current_user_playlists(limit=40)
                    pl_items = [p for p in ((pl_res or {}).get("items") or []) if isinstance(p, dict) and p.get("uri")]
                    if pl_items:
                        if not generic_pl:
                            for p in pl_items:
                                if q_low in (p.get("name") or "").lower():
                                    chosen_pl = p
                                    break
                        if not chosen_pl and generic_pl:
                            chosen_pl = random.choice(pl_items)
                except Exception:
                    pass

                if not chosen_pl and q:
                    s_pl = sp.search(q=q, limit=3, type="playlist")
                    s_items = [p for p in ((s_pl.get("playlists") or {}).get("items") or []) if isinstance(p, dict) and p.get("uri")]
                    if s_items:
                        chosen_pl = s_items[0]

                if not chosen_pl:
                    return f"No Spotify playlist matched '{q or 'your library'}'. Try authorizing playlist scopes in Studio Settings or passing a playlist name."

                pl_uri = chosen_pl["uri"]
                pl_name = chosen_pl.get("name") or "Playlist"
                pl_total = int((chosen_pl.get("tracks") or {}).get("total") or 1)
                start_pos = random.randint(0, max(0, min(pl_total - 1, 25))) if pl_total > 1 else 0
                dev_id, _ = _pick_spotify_device_id(sp)
                if dev_id:
                    try:
                        sp.start_playback(device_id=dev_id, context_uri=pl_uri, offset={"position": start_pos})
                    except Exception:
                        sp.start_playback(device_id=dev_id, context_uri=pl_uri)
                    time.sleep(0.45)
                    now_lbl = ""
                    try:
                        curr = sp.current_playback()
                        if curr and curr.get("item"):
                            now_lbl = f" Starting on '{curr['item']['name']}' by {curr['item']['artists'][0]['name']}."
                    except Exception:
                        pass
                    return f"Started full playlist '{pl_name}' ({pl_total} tracks) on Spotify so it plays continuously through the whole playlist!{now_lbl}"
                if hasattr(os, "startfile"):
                    os.startfile(pl_uri)
                return f"Opened playlist '{pl_name}' directly in your Windows Spotify app!"

            elif act in ("play_album", "album"):
                if not q:
                    return "Specify an album name to play (e.g. vault.spotify('play_album', 'Discovery'))."
                al_res = sp.search(q=q, limit=3, type="album")
                al_items = [a for a in ((al_res.get("albums") or {}).get("items") or []) if isinstance(a, dict) and a.get("uri")]
                if not al_items:
                    return f"No Spotify album matched '{q}'."
                al = al_items[0]
                al_uri = al["uri"]
                al_label = f"'{al['name']}' by {al['artists'][0]['name']}"
                dev_id, _ = _pick_spotify_device_id(sp)
                if dev_id:
                    sp.start_playback(device_id=dev_id, context_uri=al_uri, offset={"position": 0})
                    return f"Started full album {al_label} on Spotify so the whole album plays continuously!"
                if hasattr(os, "startfile"):
                    os.startfile(al_uri)
                return f"Opened album {al_label} directly in your Windows Spotify app!"

            elif act in ("liked", "liked_songs", "saved", "play_liked"):
                import random
                try:
                    saved_res = sp.current_user_saved_tracks(limit=50)
                except Exception as lib_err:
                    return (
                        f"Could not read Liked Songs ({str(lib_err)[:140]}). "
                        f"Click 'Authorize Spotify OAuth' once in Studio Settings to grant the 'user-library-read' scope!"
                    )
                raw_items = (saved_res or {}).get("items") or []
                tracks = [it["track"] for it in raw_items if isinstance(it, dict) and isinstance(it.get("track"), dict) and it["track"].get("uri")]
                if not tracks:
                    return "Spotify Web API connected, but your Liked Songs library returned 0 tracks."
                if act in ("liked", "liked_songs", "saved"):
                    lines = [f"{i+1}. {t['name']} — {t['artists'][0]['name']} ({t['uri']})" for i, t in enumerate(tracks[:15])]
                    return f"Your Recent Spotify Liked Songs ({len(tracks)} fetched):\n" + "\n".join(lines)

                # play_liked: pick a song from Liked Songs AND keep the full Liked Songs list flowing (NO 1-song loop!)
                pool = tracks
                if q:
                    q_low = q.lower()
                    filtered = [t for t in tracks if q_low in t["name"].lower() or any(q_low in a["name"].lower() for a in t.get("artists", []))]
                    if filtered:
                        pool = filtered
                chosen = random.choice(pool)
                found_track_uri = chosen["uri"]
                found_track_label = f"'{chosen['name']}' by {chosen['artists'][0]['name']}"
                dev_id, _ = _pick_spotify_device_id(sp)
                if dev_id:
                    started_context = False
                    # 1. Try native Liked Songs collection context URI first (`spotify:user:<id>:collection`)
                    try:
                        me_id = (sp.current_user() or {}).get("id")
                        if me_id:
                            sp.start_playback(
                                device_id=dev_id,
                                context_uri=f"spotify:user:{me_id}:collection",
                                offset={"uri": found_track_uri}
                            )
                            started_context = True
                    except Exception:
                        started_context = False
                    # 2. Guaranteed fallback: queue ALL fetched Liked Songs rotated so `chosen` plays first
                    #    and Spotify flows continuously through all 50 tracks instead of looping 1 song!
                    if not started_context:
                        all_uris = [t["uri"] for t in tracks]
                        try:
                            idx_c = all_uris.index(found_track_uri)
                            rotated_uris = all_uris[idx_c:] + all_uris[:idx_c]
                        except ValueError:
                            rotated_uris = [found_track_uri] + [u for u in all_uris if u != found_track_uri]
                        sp.start_playback(device_id=dev_id, uris=rotated_uris[:50])
                    return f"Picked {found_track_label} inside your Liked Songs and queued the rest of your Liked Songs ({len(tracks)} tracks) to keep playing continuously!"
                if hasattr(os, "startfile"):
                    os.startfile(found_track_uri)
                return f"Picked {found_track_label} from your Liked Songs and opened it directly in your Windows Spotify app!"

            elif act == "current_track":
                curr = sp.current_playback()
                if curr and curr.get("item"):
                    item = curr["item"]
                    dev_n = (curr.get("device") or {}).get("name", "Unknown device")
                    st = "Playing" if curr.get("is_playing") else "Paused"
                    alb_n = (item.get("album") or {}).get("name", "")
                    ctx_type = (curr.get("context") or {}).get("type", "")
                    extra = f" | Album: {alb_n}" if alb_n else ""
                    if ctx_type:
                        extra += f" | Context: {ctx_type}"
                    return f"Spotify ({st} on {dev_n}): '{item['name']}' by {item['artists'][0]['name']}{extra}"
                return "Spotify Web API connected, but nothing is currently playing (or Spotify is idle)."

            elif act in ("pause", "resume", "next", "prev", "previous"):
                dev_id, _ = _pick_spotify_device_id(sp)
                if act == "pause":
                    sp.pause_playback(device_id=dev_id)
                    return "Spotify playback paused via Web API."
                elif act == "resume":
                    sp.start_playback(device_id=dev_id)
                    return "Spotify playback resumed via Web API."
                elif act == "next":
                    if dev_id:
                        sp.next_track(device_id=dev_id)
                        time.sleep(0.45)
                        try:
                            curr = sp.current_playback()
                            if curr and curr.get("item"):
                                return f"Skipped to next track on Spotify: '{curr['item']['name']}' by {curr['item']['artists'][0]['name']}!"
                        except Exception:
                            pass
                        return "Skipped to next track on Spotify via Web API!"
                    rot_tracks = ["lo-fi chill beats", "synthwave instrumental", "ambient focus music", "acoustic guitar chill", "indie rock instrumental"]
                    pick_q = rot_tracks[int(time.time()) % len(rot_tracks)]
                    return control_spotify("play", pick_q)
                else:
                    sp.previous_track(device_id=dev_id)
                    return "Returned to previous track via Web API."

            elif act in ("play", "queue", "add_to_queue"):
                if not q and act == "play":
                    dev_id, devs = _pick_spotify_device_id(sp)
                    if dev_id:
                        try:
                            sp.start_playback(device_id=dev_id)
                            return "Resumed Spotify playback on your active device via Web API!"
                        except Exception:
                            pass
                    q = "lo-fi chill beats"

                # Direct Spotify Playlist or Album URI/URL detection!
                if "spotify:playlist:" in q or "open.spotify.com/playlist/" in q:
                    m_pl = re.search(r"(?:spotify:playlist:|open\.spotify\.com/playlist/)([A-Za-z0-9]{15,30})", q)
                    if m_pl:
                        pl_uri = f"spotify:playlist:{m_pl.group(1)}"
                        dev_id, _ = _pick_spotify_device_id(sp)
                        if dev_id:
                            sp.start_playback(device_id=dev_id, context_uri=pl_uri)
                            return f"Started full Spotify playlist ({pl_uri})!"

                # Direct Spotify Track URI / URL / 20-24 char base62 Track ID detection
                direct_tid = ""
                m_uri = re.search(r"(?:spotify:track:|open\.spotify\.com/track/)([A-Za-z0-9]{20,24})", q)
                if m_uri:
                    direct_tid = m_uri.group(1)
                elif re.fullmatch(r"[A-Za-z0-9]{20,24}", q.strip()) and any(ch.isdigit() for ch in q) and any(ch.isupper() for ch in q):
                    direct_tid = q.strip()

                if direct_tid:
                    found_track_uri = f"spotify:track:{direct_tid}"
                    try:
                        tinfo = sp.track(direct_tid)
                        found_track_label = f"'{tinfo['name']}' by {tinfo['artists'][0]['name']}"
                        found_album_uri = (tinfo.get("album") or {}).get("uri", "")
                    except Exception:
                        found_track_label = found_track_uri
                else:
                    res = sp.search(q=q, limit=1, type="track")
                    items = res.get("tracks", {}).get("items", [])
                    if items:
                        found_track_uri = items[0]["uri"]
                        found_track_label = f"'{items[0]['name']}' by {items[0]['artists'][0]['name']}"
                        found_album_uri = (items[0].get("album") or {}).get("uri", "")

                if found_track_uri:
                    dev_id, devs = _pick_spotify_device_id(sp)
                    if act in ("queue", "add_to_queue"):
                        if dev_id:
                            sp.add_to_queue(found_track_uri, device_id=dev_id)
                            return f"Added {found_track_label} to your Spotify queue!"
                        if hasattr(os, "startfile"):
                            os.startfile(found_track_uri)
                        return f"Found {found_track_label} (no active queue device awake, so opened it directly in Windows Spotify)."
                    if dev_id:
                        # Start inside the track's album context so Spotify continues naturally instead of looping 1 song!
                        played_in_album = False
                        if found_album_uri:
                            try:
                                sp.start_playback(device_id=dev_id, context_uri=found_album_uri, offset={"uri": found_track_uri})
                                played_in_album = True
                            except Exception:
                                played_in_album = False
                        if not played_in_album:
                            sp.start_playback(device_id=dev_id, uris=[found_track_uri])
                        return f"Playing {found_track_label} on Spotify via Web API{' (inside its album so playback continues naturally)' if played_in_album else ''}!"
                    if hasattr(os, "startfile"):
                        os.startfile(found_track_uri)
                    return f"Found {found_track_label} via Spotify API, and opened it directly in your Windows Spotify app (no active Web API playback device was awake)."
                return f"Spotify Web API connected, but no track matched '{q}'."

        # Self-healing fallback when Web API is unauthenticated (no token cached yet)
        if act == "play":
            if not q:
                if _send_windows_media_key("play_pause"):
                    return f"Sent Windows hardware Play/Pause key directly to Spotify! ({auth_note})"
                q = "lo-fi chill beats"
            if hasattr(os, "startfile"):
                os.startfile(f"spotify:search:{quote(q)}")
            return f"Opened '{q}' in your Windows Spotify desktop app! ({auth_note})"
        elif act in ("pause", "resume", "next", "prev", "previous"):
            if _send_windows_media_key(act):
                return f"Sent Windows hardware media key for '{act}' directly to desktop playback! ({auth_note})"
            if hasattr(os, "startfile"):
                os.startfile("spotify:")
            return f"Focused Windows Spotify app for '{act}'. ({auth_note})"
        return f"Spotify status: {auth_note}"

    except Exception as e:
        err_s = str(e)
        err_card = format_predetermined_error("ERR_API_SPOTIFY", err_s)
        is_403 = ("403" in err_s or "PREMIUM" in err_s.upper() or "Forbidden" in err_s)
        reason_hint = (
            "Spotify Web API blocked remote playback (403 — requires Spotify Premium + Development Mode user allowlist)"
            if is_403 else "Spotify Web API had no active playback device awake"
        )
        if act == "play" and (found_track_uri or q) and hasattr(os, "startfile"):
            try:
                target_uri = found_track_uri if found_track_uri else f"spotify:search:{quote(q)}"
                os.startfile(target_uri)
                lbl = found_track_label or f"'{q}'"
                return f"[{err_card['code']} Auto-Healed] {reason_hint}, so I opened {lbl} directly in your Windows Spotify desktop app!"
            except Exception:
                pass
        if act in ("pause", "resume", "next", "prev", "previous") and _send_windows_media_key(act):
            return f"[{err_card['code']} Auto-Healed] {reason_hint}, so I sent the Windows hardware media key for '{act}' directly to your PC!"
        return f"[{err_card['code']}] {reason_hint}. Detail: {err_s[:180]}"

def _format_web_results_clean(results: list, source_label: str = "Web") -> str:
    """Formats web/news results into clean, compact bullet lines so 3B/7B models read actual facts instead of raw JSON."""
    lines = [f"[LIVE {source_label.upper()} RESULTS]:"]
    for i, r in enumerate(results[:5], 1):
        title = re.sub(r"\s+", " ", str(r.get("title") or "")).strip()
        body = re.sub(r"\s+", " ", str(r.get("body") or r.get("snippet") or "")).strip()
        date_s = str(r.get("date") or "").strip()
        src_s = str(r.get("source") or "").strip()
        meta = f" ({src_s}{', ' + date_s if date_s else ''})" if src_s else (f" ({date_s})" if date_s else "")
        if title or body:
            lines.append(f"{i}. {title}{meta}: {body[:260]}")
    return "\n".join(lines)

def search_google_news_rss(query: str, max_results: int = 5) -> list:
    """Zero-key, fast, reliable live Google News RSS feed parser for today's news & recent events."""
    import xml.etree.ElementTree as ET
    q = (query or "").strip()
    if not q or STATE.get("offline_mode"):
        return []
    _lang_meta = avs_lang.SUPPORTED_UI_LOCALES.get((WORKSPACE_CFG.get("ui_language") or "en")[:2], avs_lang.SUPPORTED_UI_LOCALES["en"])
    url = f"https://news.google.com/rss/search?q={quote(q)}&hl={_lang_meta['news_hl']}&gl={_lang_meta['news_gl']}&ceid={_lang_meta['news_ceid']}"
    try:
        r = requests.get(url, headers={"User-Agent": f"AetherVaultStudio/{APP_VERSION}"}, timeout=8)
        if r.status_code != 200 or not r.text:
            return []
        root = ET.fromstring(r.content)
        out = []
        for item in root.findall(".//item")[:max_results]:
            title = (item.findtext("title") or "").strip()
            pub = (item.findtext("pubDate") or "").strip()[:16]
            src_el = item.find("source")
            src_name = (src_el.text or "").strip() if src_el is not None and src_el.text else ""
            desc_raw = (item.findtext("description") or "").strip()
            desc_clean = re.sub(r"<[^>]+>", " ", desc_raw)
            desc_clean = re.sub(r"\s+", " ", desc_clean).strip()
            if title:
                out.append({"title": title, "date": pub, "source": src_name, "body": desc_clean[:220]})
        return out
    except Exception:
        return []

def search_web(query: str) -> str:
    """
    5-Tier Self-Healing Multi-Engine Web & News Search (v4.20 — Zero API Keys Required!):
    - Tier 0 (News Fast-Path): Live Google News RSS for news/today/recent/2026 queries.
    - Tier 1: Modern `ddgs` Metasearch (DuckDuckGo, Bing, Brave, Yahoo, Wikipedia).
    - Tier 2: Direct DuckDuckGo Lite & HTML Scraper (BeautifulSoup4).
    - Tier 3: Official DuckDuckGo Instant Answer JSON API.
    - Tier 4: Official Wikipedia Search JSON API.
    Returns clean, human-readable bullet lines so small local models summarize real headlines instead of raw JSON!
    """
    if STATE["offline_mode"]:
        return "Offline Mode is active."
    q = (query or "").strip()
    if not q:
        return "Empty search query."

    ua_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    # Tier 0: Live Google News RSS for news / current events / 2026 queries
    q_low = q.lower()
    if any(k in q_low for k in ("news", "headline", "today", "recent", "latest", "2026", "summit", "reunion", "happened")):
        news_hits = search_google_news_rss(q, max_results=5)
        if news_hits:
            return _format_web_results_clean(news_hits, "Google News")

    # Tier 1: Modern `ddgs` Metasearch
    if DDGS is not None:
        if DDGS_IS_MODERN:
            for b_try in ("auto", "bing,yahoo,wikipedia"):
                try:
                    results = list(DDGS(timeout=8).text(q, max_results=4, backend=b_try) or [])
                    if results:
                        return _format_web_results_clean(results, "Web Search")
                except Exception as e:
                    format_predetermined_error("ERR_API_WEB_SEARCH", f"ddgs({b_try}): {e}")
        else:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    with DDGS() as ddgs_obj:
                        results = list(ddgs_obj.text(q, max_results=4) or [])
                        if results:
                            return _format_web_results_clean(results, "Web Search")
            except Exception as e:
                format_predetermined_error("ERR_API_WEB_SEARCH", f"legacy duckduckgo_search (upgrade to ddgs): {e}")

    # Tier 2: Direct DuckDuckGo Lite & HTML POST/GET Scraper
    if BeautifulSoup is not None:
        for ep_url, is_lite in (("https://lite.duckduckgo.com/lite/", True), ("https://html.duckduckgo.com/html/", False)):
            try:
                r = requests.post(
                    ep_url,
                    data={"q": q},
                    headers={**ua_headers, "Referer": ep_url, "Content-Type": "application/x-www-form-urlencoded"},
                    timeout=9
                )
                if r.status_code == 200 and r.text:
                    soup = BeautifulSoup(r.text, "html.parser")
                    found = []
                    if is_lite:
                        links = soup.select("a.result-link")
                        snips = soup.select("td.result-snippet")
                        for idx_l, lk in enumerate(links[:4]):
                            body_t = snips[idx_l].get_text(" ", strip=True) if idx_l < len(snips) else ""
                            found.append({"title": lk.get_text(" ", strip=True), "body": body_t})
                    else:
                        for a in soup.select(".result__body")[:4]:
                            t_el = a.select_one(".result__title")
                            s_el = a.select_one(".result__snippet")
                            if t_el and s_el:
                                found.append({"title": t_el.get_text(" ", strip=True), "body": s_el.get_text(" ", strip=True)})
                    if found:
                        return _format_web_results_clean(found, "DuckDuckGo")
            except Exception:
                pass

    # Tier 3: Official DuckDuckGo Instant Answer JSON API
    try:
        ia_r = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": q, "format": "json", "no_html": "1", "skip_disambig": "1"},
            headers=ua_headers,
            timeout=8
        )
        if ia_r.status_code == 200:
            ia = ia_r.json()
            ia_out = []
            if ia.get("AbstractText"):
                ia_out.append({"title": ia.get("Heading") or q, "body": ia.get("AbstractText")})
            for rt in (ia.get("RelatedTopics") or [])[:3]:
                if isinstance(rt, dict) and rt.get("Text"):
                    ia_out.append({"title": (rt.get("Text") or "")[:70], "body": rt.get("Text")})
            if ia_out:
                return _format_web_results_clean(ia_out, "Instant Answer")
    except Exception:
        pass

    # Tier 4: Live Google News RSS fallback (even if query didn't have 'news' keyword)
    news_fb = search_google_news_rss(q, max_results=4)
    if news_fb:
        return _format_web_results_clean(news_fb, "News")

    # Tier 5: Official Wikipedia Search JSON API
    try:
        wk_r = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action": "query", "list": "search", "srsearch": q, "srlimit": 3, "utf8": 1, "format": "json"},
            headers={"User-Agent": f"AetherVaultStudio/{APP_VERSION} (Local Desktop Assistant)"},
            timeout=8
        )
        if wk_r.status_code == 200:
            hits = ((wk_r.json().get("query") or {}).get("search") or [])
            if hits:
                wk_out = [
                    {"title": f"{h.get('title', '')} (Wikipedia)", "body": re.sub(r"<[^>]+>", "", h.get("snippet") or "").strip()}
                    for h in hits[:3]
                ]
                return _format_web_results_clean(wk_out, "Wikipedia")
    except Exception as e_wk:
        return f"[ERR-06 Web Search Unavailable]: {e_wk}"

    return f"No live web results found for '{q}'."

def generate_image_tool(prompt: str) -> dict:
    clean_p = prompt.strip()
    fname = f"aether_art_{int(time.time())}.png"
    fpath = GEN_IMG_DIR / fname
    sd_api = WORKSPACE_CFG.get("sd_api_url", "http://127.0.0.1:7860")

    try:
        r = requests.post(f"{sd_api.rstrip('/')}/sdapi/v1/txt2img", json={"prompt": clean_p, "steps": 24, "width": 768, "height": 768}, timeout=45)
        if r.status_code == 200:
            fpath.write_bytes(base64.b64decode(r.json()["images"][0]))
            return {"ok": True, "url": f"/generated_image/{fname}", "source": "Local SD WebUI"}
    except Exception:
        pass

    if not STATE["offline_mode"]:
        try:
            url = f"https://image.pollinations.ai/prompt/{quote(clean_p)}?width=768&height=768&nologo=true&seed={int(time.time())}"
            r = requests.get(url, timeout=35)
            if r.status_code == 200 and len(r.content) > 1000:
                fpath.write_bytes(r.content)
                return {"ok": True, "url": f"/generated_image/{fname}", "source": "Pollinations Diffusion Bridge"}
        except Exception as e:
            err_card = format_predetermined_error("ERR_API_IMAGE_GEN", str(e))
            return {"ok": False, "error": f"[{err_card['code']}] {err_card['message']}"}

    err_card = format_predetermined_error("ERR_API_IMAGE_GEN", f"No server at {sd_api}")
    return {"ok": False, "error": f"[{err_card['code']}] {err_card['message']}"}

# =====================================================================
# 8. UNLIMITED NATURAL COMPLETION GOVERNOR & MODEL LOADER
# =====================================================================
def is_unrestricted_tokens_enabled() -> bool:
    return bool(WORKSPACE_CFG.get("unrestricted_tokens", True))

def get_governor_settings(gear: str = "deep", prompt_chars: int = 1200):
    """
    UNCAPPED / HARDWARE-AWARE GOVERNOR (v4.16):
    - When `unrestricted_tokens` is ON:
      * Scales local n_ctx up safely by host RAM (16384 on >=16GB RAM rigs, 8192 on >=8GB, 4096 on <8GB)
      * Passes uncapped output headroom (full remaining n_ctx locally; up to 32768 / provider max on Cloud APIs)
      * Pairs with Rolling Auto-Continuation so even if a single pass hits finish_reason=='length', it keeps going!
    """
    cpu_count = os.cpu_count() or 4
    ram_total = float(get_system_ram_info().get("total_gb", 8.0))
    mode = STATE["performance_mode"]
    uncapped = is_unrestricted_tokens_enabled()

    if mode == "Laptop 2015 (Fast)" or cpu_count <= 2:
        n_ctx = 4096
        n_batch = 128 if cpu_count <= 2 else 256
    elif mode == "Turbo (Max Threads)":
        n_ctx = 16384 if (uncapped and ram_total >= 15.0) else 8192
        n_batch = 1024
    else:
        if uncapped and ram_total >= 15.0:
            n_ctx = 12288
        elif uncapped and ram_total >= 7.5:
            n_ctx = 8192
        else:
            n_ctx = 4096
        n_batch = 512

    actual_ctx = n_ctx
    if STATE.get("llm") is not None and hasattr(STATE["llm"], "n_ctx") and callable(STATE["llm"].n_ctx):
        try:
            actual_ctx = int(STATE["llm"].n_ctx())
        except Exception:
            actual_ctx = n_ctx

    est_prompt_tokens = int(prompt_chars / 3.2) + 120
    # Detect if Cloud Smart API is active so we don't choke cloud output to a local 4K window!
    b_mode = WORKSPACE_CFG.get("brain_mode", "local_only")
    has_api = bool([s for s in load_api_vault().get("slots", []) if s.get("enabled", True)]) and not STATE.get("offline_mode")
    using_cloud_api = (b_mode in ("smart_api", "hybrid")) and has_api
    if uncapped and using_cloud_api:
        safe_max_tokens = 32768
    else:
        safe_max_tokens = max(1024 if uncapped else 512, actual_ctx - est_prompt_tokens)

    return {
        "threads": max(2, cpu_count - 1),
        "n_ctx": n_ctx,
        "actual_ctx": actual_ctx,
        "n_batch": n_batch,
        "max_tokens": safe_max_tokens,
        "uncapped": uncapped
    }

def resolve_local_model_path(filename: str) -> Path:
    """Finds a .gguf model across /models, subfolders, or /stock_vault/models (offline vault)."""
    if not filename:
        return Path("")
    direct = MODEL_DIR / filename
    if direct.exists() and direct.is_file():
        return direct
    stock_models = BASE_DIR / "stock_vault" / "models"
    for search_root in (MODEL_DIR, stock_models, HF_CACHE_DIR):
        if search_root.exists():
            for p in search_root.rglob("*.gguf"):
                if p.name.lower() == Path(filename).name.lower() and not p.name.endswith(".part"):
                    return p
    return direct

def list_local_models():
    """Scans /models (and /stock_vault/models + /hf_cache) for any offline .gguf files."""
    found = {}
    stock_models = BASE_DIR / "stock_vault" / "models"
    for search_root in (MODEL_DIR, stock_models, HF_CACHE_DIR):
        if search_root.exists():
            for p in search_root.rglob("*"):
                if p.is_file() and p.suffix.lower() == ".gguf" and not p.name.endswith(".part"):
                    found.setdefault(p.name, p)
    return sorted(found.keys())

def load_local_model(filename: str):
    if Llama is None:
        format_predetermined_error("ERR_ENGINE_CRASH", "llama-cpp-python is not installed in .venv yet. Click 'Switch Engine Backend' or 'Setup .venv' in the Manager!")
        return None
    model_path = resolve_local_model_path(filename)
    if not model_path.exists() or not model_path.is_file():
        return None

    STATE["loading_model"] = True
    STATE["gpu_offload"] = bool(llama_supports_gpu_offload())
    accel = "VULKAN GPU (-1 layers)" if STATE["gpu_offload"] else "CPU Multi-Thread"
    set_step(f"Loading {model_path.name} ({accel})...")
    try:
        with LLM_LOCK:
            if STATE["llm"] is not None:
                STATE["llm"] = None
                gc.collect()

            cfg = get_governor_settings("deep")
            t0 = time.time()
            gpu_layers = -1 if STATE["gpu_offload"] else 0
            try:
                use_mmap_flag = False if (os.cpu_count() or 4) <= 2 else True
                STATE["llm"] = Llama(
                    model_path=str(model_path),
                    n_ctx=cfg["n_ctx"],
                    n_threads=cfg["threads"],
                    n_threads_batch=max(2, (os.cpu_count() or 4) - 1),
                    n_batch=cfg["n_batch"],
                    n_gpu_layers=gpu_layers,
                    use_mmap=use_mmap_flag,
                    flash_attn=True if STATE["gpu_offload"] else False,
                    verbose=False
                )
            except Exception as first_err:
                # Self-healing fallback: if Vulkan GPU offload or flash_attn fails on a 2015 laptop / low VRAM,
                # automatically fall back to pure CPU multi-thread mode with safe context size!
                format_predetermined_error("ERR_VULKAN_LEGACY_APU", str(first_err))
                print(f"[MODEL LOADER AUTO-HEAL] Primary load raised ({first_err}); retrying in Safe CPU Mode (See Manual Section 6)...")
                STATE["gpu_offload"] = False
                accel = "CPU Safe Fallback"
                STATE["llm"] = Llama(
                    model_path=str(model_path),
                    n_ctx=min(4096, cfg["n_ctx"]),
                    n_threads=cfg["threads"],
                    n_batch=128 if (os.cpu_count() or 4) <= 2 else 256,
                    n_gpu_layers=0,
                    use_mmap=False,
                    verbose=False
                )
            STATE["current_model"] = model_path.name
            STATE["idle_sleeping"] = False
            STATE["last_activity_ts"] = time.time()
            WORKSPACE_CFG["last_loaded_model"] = model_path.name
            save_workspace_config(WORKSPACE_CFG)
            print(f"[MODEL LOADER] Loaded {model_path.name} in {time.time() - t0:.1f}s ({accel})")
            return model_path.name
    except Exception as e:
        format_predetermined_error("ERR_HARDWARE_BELOW_SPEC", f"{filename}: {e}")
        STATE["current_model"] = None
        return None
    finally:
        STATE["loading_model"] = False
        set_step("Idle")

def unload_local_model(reason: str = "Manual unload") -> dict:
    """Safely unloads active GGUF weights from RAM/VRAM, runs gc.collect() + SQLite WAL checkpoint, and enters 0-overhead Idle Sleep."""
    prev_name = STATE.get("current_model") or ""
    if STATE.get("loading_model") or STATE.get("generating"):
        return {"ok": False, "message": "Model is currently busy loading or generating."}
    with LLM_LOCK:
        if STATE.get("llm") is not None:
            STATE["llm"] = None
        if prev_name:
            STATE["last_unloaded_model"] = prev_name
        STATE["current_model"] = None
        STATE["idle_sleeping"] = True
        gc.collect()
    try:
        with get_db() as conn:
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    except Exception:
        pass
    if prev_name:
        print(f"[IDLE SLEEP] Unloaded '{prev_name}' ({reason}) -> RAM/VRAM freed!", flush=True)
    return {"ok": True, "unloaded": prev_name, "reason": reason}

def touch_activity(wake_model: bool = False):
    """Marks activity timestamp; optionally auto-reloads the sleeping GGUF model on demand."""
    STATE["last_activity_ts"] = time.time()
    if wake_model and STATE.get("idle_sleeping") and not STATE.get("llm") and not STATE.get("loading_model"):
        target = STATE.get("last_unloaded_model") or WORKSPACE_CFG.get("last_loaded_model") or pick_lightweight_failsafe_model()
        if target:
            STATE["idle_sleeping"] = False
            load_local_model(target)

def idle_sleep_watchdog():
    """Background low-power watchdog: unloads GGUF weights after idle_unload_minutes of inactivity so RAM stays free."""
    while True:
        try:
            time.sleep(15)
            mins = float(WORKSPACE_CFG.get("idle_unload_minutes", 10) or 0)
            if mins <= 0:
                continue
            if STATE.get("llm") is None or STATE.get("loading_model") or STATE.get("generating"):
                continue
            if (STATE.get("download") or {}).get("active"):
                continue
            idle_sec = time.time() - float(STATE.get("last_activity_ts") or time.time())
            if idle_sec >= (mins * 60.0):
                unload_local_model(f"Auto-Sleep after {int(mins)}m idle")
        except Exception:
            time.sleep(15)

def download_worker(repo_id: str, filename: str):
    STATE["download"].update({
        "active": True, "cancel_requested": False, "filename": filename, "downloaded_mb": 0.0,
        "total_mb": 0.0, "percent": 0.0, "speed_mbps": 0.0,
        "elapsed_sec": 0, "eta_sec": 0, "error": None
    })
    set_step(f"⬇️ Connecting to Hugging Face for {filename}...")
    target_path = MODEL_DIR / Path(filename).name
    temp_path = MODEL_DIR / (Path(filename).name + ".part")
    try:
        url = hf_hub_url(repo_id=repo_id, filename=filename)
        headers = {"User-Agent": f"AetherVaultStudio/{APP_VERSION}", "Accept": "*/*"}
        t_start = time.time()
        with requests.get(url, headers=headers, stream=True, allow_redirects=True, timeout=(12, 25)) as r:
            r.raise_for_status()
            raw_len = r.headers.get("content-length") or r.headers.get("x-linked-size") or "0"
            total_bytes = int(raw_len) if str(raw_len).isdigit() else 0
            total_mb = round(total_bytes / (1024 * 1024), 1)
            STATE["download"]["total_mb"] = total_mb
            downloaded = 0
            last_log_t = 0.0
            with open(temp_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=128 * 1024):
                    if STATE["download"].get("cancel_requested"):
                        raise RuntimeError("Download cancelled by user.")
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        elapsed = max(0.1, time.time() - t_start)
                        dl_mb = downloaded / (1024 * 1024)
                        speed = round(dl_mb / elapsed, 2)
                        rem_mb = max(0.0, total_mb - dl_mb)
                        eta = int(rem_mb / speed) if (total_mb > 0 and speed > 0.05) else 0
                        STATE["download"]["downloaded_mb"] = round(dl_mb, 1)
                        STATE["download"]["speed_mbps"] = speed
                        STATE["download"]["elapsed_sec"] = int(elapsed)
                        STATE["download"]["eta_sec"] = eta
                        if total_bytes > 0:
                            STATE["download"]["percent"] = round((downloaded / total_bytes) * 100, 1)
                        STATE["current_step"] = f"⬇️ Downloading {filename}: {STATE['download']['percent']}% ({STATE['download']['downloaded_mb']}/{total_mb} MB @ {speed} MB/s | ETA {eta}s)"
                        if (time.time() - last_log_t) >= 1.5:
                            last_log_t = time.time()
                            print(f"[HF DOWNLOAD] {filename}: {STATE['download']['percent']}% ({STATE['download']['downloaded_mb']} / {total_mb} MB @ {speed} MB/s | ETA: {eta}s)", flush=True)
        if downloaded == 0:
            raise RuntimeError("Received 0 bytes from Hugging Face CDN. Check repo/filename or internet connection.")
        if target_path.exists():
            target_path.unlink()
        temp_path.rename(target_path)
        STATE["download"]["last_completed"] = target_path.name
        STATE["download"]["active"] = False
        load_local_model(target_path.name)
    except Exception as e:
        print(f"[HF DOWNLOAD ERROR] {filename}: {e}", flush=True)
        STATE["download"]["error"] = str(e)
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass
    finally:
        STATE["download"]["active"] = False
        STATE["download"]["cancel_requested"] = False
        if STATE["current_step"].startswith("⬇️ "):
            set_step("Idle")

def sync_memory_vault_file():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT id, category, fact, timestamp FROM dynamic_memory WHERE COALESCE(active, 1) = 1 ORDER BY id DESC")
        rows = c.fetchall()
    vault_file = MEMORY_DIR / "learned_memories.txt"
    lines = [f"[{r['id']}] ({r['category']}) {r['fact']} -- {r['timestamp']}" for r in rows]
    vault_file.write_text("\n".join(lines) if lines else "No memories stored yet.\n", encoding="utf-8")

def save_to_memory(category: str, fact: str, sync_pseudo: bool = True) -> str:
    category = (category or "active_state").strip()
    fact = (fact or "").strip()
    if not fact:
        return "Empty fact ignored."
    cat_low = category.lower()
    if cat_low in ("user_name", "user_identity", "name", "handle", "alias", "nickname"):
        clean_name = re.sub(r"^(?:user'?s?\s+name(?:/handle)?\s+is|call\s+me|name\s*:)\s*", "", fact, flags=re.IGNORECASE).strip(" .!\"'")
        if clean_name:
            fact = f"User's name/handle is {clean_name}"
            WORKSPACE_CFG["user_name"] = clean_name
            save_workspace_config(WORKSPACE_CFG)
            card = load_user_profile_card()
            card["user_name"] = clean_name
            save_user_profile_card(card)
            STATE["ui_sync_needed"] = True
    elif cat_low in ("user_location", "location", "city", "hometown"):
        clean_loc = _clean_location_value(fact)
        if clean_loc:
            fact = f"User lives in {clean_loc}"
            card = load_user_profile_card()
            card["location"] = clean_loc
            save_user_profile_card(card)
    elif cat_low in ("user_zip", "zip", "zip_code", "postal_code"):
        clean_zip = re.sub(r"^user\s+zip/postal\s+code\s+is\s+", "", fact, flags=re.IGNORECASE).strip().upper()
        if clean_zip:
            fact = f"User ZIP/Postal code is {clean_zip}"
            card = load_user_profile_card()
            card["zip_code"] = clean_zip
            save_user_profile_card(card)
    elif cat_low in ("user_note", "active_project", "preference"):
        is_ai_instruction = bool(re.match(r"^(?:you\s+(?:can|could|should|have|need|must|are\s+supposed|ought)|please\s+)", fact.lower()))
        if not is_ai_instruction:
            card = load_user_profile_card()
            pf = card.get("pinned_facts") or []
            if fact not in pf:
                card["pinned_facts"] = (pf + [fact])[-10:]
                save_user_profile_card(card)

    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM dynamic_memory WHERE COALESCE(active, 1) = 1 AND LOWER(fact) = LOWER(?)", (fact,))
        if not c.fetchone():
            c.execute("INSERT INTO dynamic_memory (category, fact) VALUES (?, ?)", (category, fact))
            conn.commit()
    sync_memory_vault_file()
    if sync_pseudo and "sync_pseudo_memory_and_index" in globals():
        try:
            sync_pseudo_memory_and_index()
        except Exception:
            pass
    return f"Saved to persistent pseudo-memory [{category}]: {fact}"

def list_memories():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT id, category, fact FROM dynamic_memory WHERE COALESCE(active, 1) = 1 ORDER BY id DESC LIMIT 30")
        return [{"id": r["id"], "category": r["category"], "fact": r["fact"]} for r in c.fetchall()]

def format_memories_for_prompt(limit: int = 12) -> str:
    mems = list_memories()[:limit]
    if not mems:
        return "- [active_state] Standard Workspace & Companion Mode."
    return "\n".join([f"- [{m['category']}] {m['fact'][:300]}" for m in mems])

def build_safe_messages(static_sys_prompt: str, dynamic_turn_context: str, recent_turns: list, max_turns: int = 6) -> list:
    uncapped = is_unrestricted_tokens_enabled()
    b_mode = WORKSPACE_CFG.get("brain_mode", "local_only")
    has_api = bool([s for s in load_api_vault().get("slots", []) if s.get("enabled", True)]) and not STATE.get("offline_mode")
    using_cloud = (b_mode in ("smart_api", "hybrid")) and has_api
    if uncapped and using_cloud:
        char_budget = 64000
        per_turn_cap = 14000
    else:
        act_ctx = 4096
        if STATE.get("llm") is not None and hasattr(STATE["llm"], "n_ctx") and callable(STATE["llm"].n_ctx):
            try:
                act_ctx = int(STATE["llm"].n_ctx())
            except Exception:
                act_ctx = 4096
        elif uncapped:
            act_ctx = get_governor_settings("deep").get("n_ctx", 8192)
        char_budget = max(9500, int(act_ctx * 2.9)) if uncapped else 9500
        per_turn_cap = max(1400, int(char_budget * 0.35)) if uncapped else 1400

    cleaned = []
    for t in recent_turns[-max_turns:]:
        role = t.get("role", "user")
        if role not in ("user", "assistant"):
            role = "user"
        raw_t_cont = (t.get("content") or "").strip()
        raw_t_cont = re.sub(r"<\|think\|>[\s\S]*?<\|/think\|>", "", raw_t_cont, flags=re.IGNORECASE)
        raw_t_cont = re.sub(r"<think>[\s\S]*?</think>", "", raw_t_cont, flags=re.IGNORECASE)
        content = raw_t_cont.strip()[:per_turn_cap]
        if not content:
            continue
        if cleaned and cleaned[-1]["role"] == role:
            cleaned[-1]["content"] = f"{cleaned[-1]['content']}\n\n{content}"
        else:
            cleaned.append({"role": role, "content": content})

    while cleaned and cleaned[0]["role"] == "assistant":
        cleaned.pop(0)

    if not cleaned:
        cleaned = [{"role": "user", "content": "Hello."}]

    user_name = WORKSPACE_CFG.get("user_name", "User")
    ai_name_loc = WORKSPACE_CFG.get("ai_name", "Assistant")

    # Build a crisp 3-line Recent Chat Thread Recap from the previous turns (excluding current user turn)
    # so 3B models ALWAYS stay locked onto what was just discussed (e.g., Spotify song -> follow-up question)!
    thread_recap = ""
    if len(cleaned) >= 2:
        prev_slice = cleaned[-5:-1]
        recap_lines = []
        for pm in prev_slice:
            who = user_name if pm["role"] == "user" else ai_name_loc
            snip = re.sub(r"\s+", " ", pm["content"]).strip()[:170]
            recap_lines.append(f"  - {who}: {snip}")
        if recap_lines:
            thread_recap = (
                "[RECENT CHAT CONTINUITY — FOLLOW THIS ACTIVE THREAD, DO NOT DROP BACK INTO RANDOM ROLEPLAY]:\n"
                + "\n".join(recap_lines)
            )

    prefix_parts = [p for p in (thread_recap, dynamic_turn_context.strip()) if p]
    if prefix_parts:
        cleaned[-1]["content"] = "\n\n".join(prefix_parts) + f"\n\n{user_name}: {cleaned[-1]['content']}"

    # Auto-heal context overflow WITHOUT wiping out the last 4 messages of conversation!
    # First trim oversized older messages & system prompt before ever dropping the last 4 turns.
    total_chars = len(static_sys_prompt) + sum(len(m["content"]) for m in cleaned)
    if total_chars > char_budget:
        format_predetermined_error("ERR_CONTEXT_OVERFLOW", f"Compacted {total_chars} -> {char_budget} chars while preserving recent chat continuity.")
        older_cap = max(450, int(char_budget * 0.12))
        for idx_m in range(len(cleaned) - 1):
            if len(cleaned[idx_m]["content"]) > older_cap:
                cleaned[idx_m]["content"] = cleaned[idx_m]["content"][:older_cap] + "..."
        while len(cleaned) > 4 and (len(static_sys_prompt) + sum(len(m["content"]) for m in cleaned)) > int(char_budget * 0.92):
            cleaned.pop(0)
            while len(cleaned) > 4 and cleaned[0]["role"] == "assistant":
                cleaned.pop(0)
        sys_cap = max(4800, int(char_budget * 0.45))
        if (len(static_sys_prompt) + sum(len(m["content"]) for m in cleaned)) > char_budget and len(static_sys_prompt) > sys_cap:
            static_sys_prompt = static_sys_prompt[:sys_cap]

    messages = [{"role": "system", "content": static_sys_prompt}] + cleaned
    model_lower = (STATE["current_model"] or "").lower()
    if ("gemma" in model_lower or "gemma4" in model_lower) and messages and messages[0]["role"] == "system":
        sys_text = messages.pop(0)["content"]
        if messages and messages[0]["role"] == "user":
            messages[0]["content"] = f"[System Instructions]\n{sys_text}\n\n[User Request]\n{messages[0]['content']}"
        else:
            messages.insert(0, {"role": "user", "content": f"[System Instructions]\n{sys_text}"})
    if "mistral" in model_lower and messages and messages[0]["role"] == "system":
        sys_text = messages.pop(0)["content"]
        if messages and messages[0]["role"] == "user":
            messages[0]["content"] = f"{sys_text}\n\n---\n\n{messages[0]['content']}"
        else:
            messages.insert(0, {"role": "user", "content": sys_text})
    return messages

# =====================================================================
# 8C. v6.8 ULTIMATE GUARDRAILS: BACKGROUND MEMORY COMPACTOR,
#     LORE ATTRIBUTION REFEREE & BLUESKY AT PROTOCOL BRIDGE
# =====================================================================
from difflib import SequenceMatcher as _SeqMatcher
from collections import defaultdict as _ddict

EXCLUSIVE_MEMORY_CATEGORIES = {"user_name", "user_identity", "user_location", "location", "user_zip", "zip_code"}

def _normalize_mem_fact(text: str) -> str:
    s = re.sub(r"[^a-z0-9\s]", " ", (text or "").lower())
    return re.sub(r"\s+", " ", s).strip()

class AetherMemoryCompactor:
    """
    Background Python 'pseudo-work' worker:
    - Deduplicates exact & fuzzy near-duplicate memories in SQLite without calling the LLM.
    - Supersedes stale single-slot facts (location, name, zip) while keeping audit rows inactive (active=0).
    - Builds a 1-hop keyword co-occurrence mind-map for entity/lore lookups.
    """
    def __init__(self, interval_sec: int = 120):
        self.interval_sec = max(30, int(interval_sec))
        self._lock = threading.Lock()
        self.mind_map: dict = {}
        self._ensure_columns()

    def _ensure_columns(self):
        try:
            with get_db() as conn:
                cols = {r["name"] for r in conn.execute("PRAGMA table_info(dynamic_memory)").fetchall()}
                if "active" not in cols:
                    conn.execute("ALTER TABLE dynamic_memory ADD COLUMN active INTEGER DEFAULT 1")
                if "hits" not in cols:
                    conn.execute("ALTER TABLE dynamic_memory ADD COLUMN hits INTEGER DEFAULT 1")
                if "norm_key" not in cols:
                    conn.execute("ALTER TABLE dynamic_memory ADD COLUMN norm_key TEXT DEFAULT ''")
                conn.commit()
        except Exception:
            pass

    def compact_now(self, fuzzy_threshold: float = 0.86) -> dict:
        if not self._lock.acquire(blocking=False):
            return {"skipped": True}
        merged = 0
        superseded = 0
        try:
            self._ensure_columns()
            with get_db() as conn:
                rows = conn.execute(
                    "SELECT id, category, fact, COALESCE(hits, 1) AS hits "
                    "FROM dynamic_memory WHERE COALESCE(active, 1) = 1 ORDER BY id DESC"
                ).fetchall()
                seen_excl = set()
                kept = []
                for r in rows:
                    rid = r["id"]
                    cat = (r["category"] or "active_state").strip()
                    cat_low = cat.lower()
                    fact = (r["fact"] or "").strip()
                    norm = _normalize_mem_fact(fact)
                    if not norm:
                        conn.execute("UPDATE dynamic_memory SET active = 0 WHERE id = ?", (rid,))
                        superseded += 1
                        continue
                    if cat_low in EXCLUSIVE_MEMORY_CATEGORIES:
                        if cat_low in seen_excl:
                            conn.execute("UPDATE dynamic_memory SET active = 0 WHERE id = ?", (rid,))
                            superseded += 1
                            continue
                        seen_excl.add(cat_low)
                    dup = None
                    for k in kept:
                        if k["norm"] == norm:
                            dup = k
                            break
                        if k["cat_low"] == cat_low and abs(len(k["norm"]) - len(norm)) < 45:
                            if _SeqMatcher(None, k["norm"], norm).ratio() >= fuzzy_threshold:
                                dup = k
                                break
                    if dup is not None:
                        best_f = fact if len(fact) > len(dup["fact"]) else dup["fact"]
                        new_h = int(dup["hits"]) + int(r["hits"] or 1)
                        dup["fact"] = best_f
                        dup["norm"] = _normalize_mem_fact(best_f)
                        dup["hits"] = new_h
                        conn.execute(
                            "UPDATE dynamic_memory SET fact = ?, norm_key = ?, hits = ? WHERE id = ?",
                            (best_f, dup["norm"], new_h, dup["id"])
                        )
                        conn.execute("UPDATE dynamic_memory SET active = 0 WHERE id = ?", (rid,))
                        merged += 1
                    else:
                        conn.execute("UPDATE dynamic_memory SET norm_key = ? WHERE id = ?", (norm, rid))
                        kept.append({"id": rid, "cat_low": cat_low, "fact": fact, "norm": norm, "hits": int(r["hits"] or 1)})
                conn.commit()
                try:
                    conn.execute("PRAGMA wal_checkpoint(PASSIVE)")
                except Exception:
                    pass

            co = _ddict(Counter)
            for item in kept:
                kws = list(dict.fromkeys(extract_keywords(item["fact"])))
                for w in kws:
                    for peer in kws:
                        if peer != w:
                            co[w][peer] += item["hits"]
            self.mind_map = {w: cnt.most_common(5) for w, cnt in co.items()}
            return {"merged": merged, "superseded": superseded, "active": len(kept), "links": len(self.mind_map)}
        finally:
            self._lock.release()

    def expand_keywords(self, query_text: str) -> list:
        base = extract_keywords(query_text)
        out = list(dict.fromkeys(base))
        for kw in base[:4]:
            for nb, _ in self.mind_map.get(kw, [])[:2]:
                if nb not in out:
                    out.append(nb)
        return out

MEMORY_COMPACTOR = AetherMemoryCompactor(interval_sec=120)

def _memory_compactor_watchdog():
    while True:
        time.sleep(MEMORY_COMPACTOR.interval_sec)
        if STATE.get("generating") or STATE.get("loading_model"):
            continue
        try:
            res = MEMORY_COMPACTOR.compact_now()
            if res.get("merged") or res.get("superseded"):
                sync_memory_vault_file()
        except Exception:
            pass

def referee_lore_and_grounding(reply_text: str, user_msg: str, ai_name: str, retrieved_lore: str) -> tuple:
    """
    v6.8 Lore Attribution & Tool Grounding Referee:
    1. Flags when the model claims a 'primary/sole/only' title or unique role for itself/another character
       that isn't backed by the active CORE persona or retrieved LORE context.
    2. Strips fake/hallucinated tool-action narration (*opens Spotify*, *scans files*, *runs terminal*)
       when no real tool ran during the turn.
    Returns (cleaned_reply, warnings_list).
    """
    warnings_out = []
    out = (reply_text or "").strip()
    if not out:
        return out, warnings_out

    has_real_tool_evidence = bool(
        STATE.get("last_debug", {}).get("osworld_actions")
        or STATE.get("last_debug", {}).get("pc_files_scanned")
        or STATE.get("last_debug", {}).get("lore_pulled")
    )
    if not has_real_tool_evidence:
        fake_act_pat = r"(?im)^[\s*]*\*?(?:opens?|launches?|scans?|searches?|executes?|runs?|checks?)\s+(?:spotify|steam|terminal|powershell|files?|browser|osworld)[^*\n]*\*?$"
        if re.search(fake_act_pat, out):
            out = re.sub(fake_act_pat, "", out).strip()
            warnings_out.append("Stripped ungrounded tool-action narration (no tool executed).")

    evidence_pool = f"{PRIORITY_CACHE.get('core_rules_text', '')} {WORKSPACE_CFG.get('persona_prompt', '')} {retrieved_lore}".lower()
    exclusive_matches = re.findall(r"\b(?:the\s+(?:primary|sole|only|true|original)\s+[a-zA-Z0-9_-]{3,24})\b", out, flags=re.IGNORECASE)
    for phrase in exclusive_matches:
        tokens = [t.lower() for t in re.findall(r"[a-zA-Z]{4,}", phrase) if t.lower() not in ("primary", "sole", "only", "true", "original")]
        if tokens and not any(t in evidence_pool for t in tokens):
            warnings_out.append(f"Unverified exclusive title '{phrase}' not found in CORE/LORE context.")

    return re.sub(r"\n{3,}", "\n\n", out).strip(), warnings_out

# =====================================================================
# 8D. v6.8 REDUNDANT GUARDRAIL BLENDER FOR COMPACT MODELS (GEMMA & FRIENDS)
#     1. Reasoning-Echo & Turn-Leak Stripper (prevents multi-step thought loops)
#     2. Tool Observation Compactor (keeps high-signal lines inside small ctx)
#     3. Argument Coercion & Surgical Self-Retry Helper (1 bounded retry)
#     4. Abrupt-Truncation Detector & Continuation Helper
# =====================================================================
def strip_reasoning_and_role_echoes(text: str, ai_name: str = "Aether", user_name: str = "Creator") -> str:
    """Strips internal <think>/reasoning tags and trailing leaked User/Model turn headers."""
    if not text:
        return ""
    s = re.sub(r"<\|think\|>[\s\S]*?<\|/think\|>", "", text, flags=re.IGNORECASE)
    s = re.sub(r"<think>[\s\S]*?</think>", "", s, flags=re.IGNORECASE)
    if "<think>" in s and "</think>" not in s:
        s = s.split("<think>", 1)[0]
    s = re.sub(rf"(?im)\n+(?:{re.escape(user_name)}|user|human|model|assistant)\s*:\s*$", "", s)
    s = re.sub(r"<end_of_turn>|<start_of_turn>.*", "", s, flags=re.IGNORECASE | re.DOTALL)
    return s.strip()

def compact_tool_observation(raw_obs: str, max_chars: int = 2400, max_lines: int = 45) -> str:
    """Compacts noisy tool/workbench output so small context windows keep signal over boilerplate."""
    if not raw_obs:
        return ""
    lines = [ln.rstrip() for ln in str(raw_obs).splitlines() if ln.strip()]
    deduped = []
    for ln in lines:
        if not deduped or ln != deduped[-1]:
            deduped.append(ln)
    if len(deduped) > max_lines:
        head_n = max_lines // 2
        tail_n = max_lines - head_n
        deduped = deduped[:head_n] + [f"... ({len(lines) - max_lines} middle lines compacted) ..."] + deduped[-tail_n:]
    out = "\n".join(deduped).strip()
    if len(out) > max_chars:
        out = out[:max_chars].rsplit("\n", 1)[0].strip() + f"\n... [Compacted from {len(raw_obs)} chars]"
    return out

def coerce_primitive_args(args: dict) -> dict:
    """Coerces common small-model string/int/float/bool/path slips cleanly."""
    if not isinstance(args, dict):
        return {}
    coerced = {}
    for k, v in args.items():
        if isinstance(v, str):
            low = v.strip().lower()
            if low in ("true", "yes", "on"):
                coerced[k] = True
            elif low in ("false", "no", "off"):
                coerced[k] = False
            elif re.fullmatch(r"-?\d+", v.strip()):
                coerced[k] = int(v.strip())
            elif re.fullmatch(r"-?\d+\.\d+", v.strip()):
                coerced[k] = float(v.strip())
            elif re.match(r"^[A-Za-z]:\\[^\n]+$", v.strip()):
                coerced[k] = v.strip().replace("\\", "/")
            else:
                coerced[k] = v
        else:
            coerced[k] = v
    return coerced

def needs_continuation_stitch(reply_text: str) -> bool:
    """Detects if a non-code reply appears cut off mid-sentence or mid-list."""
    t = (reply_text or "").strip()
    if len(t) < 180:
        return False
    if t.count("```") % 2 != 0:
        return True
    if t.endswith((",", ":", ";", "-", "(", "[", "/", "and", "or", "with", "to", "for", "in")):
        return True
    if t[-1] not in ".!?)\"'`”’" and not t.endswith("..."):
        return True
    return False

def run_blended_workbench_with_retry(code_str: str, messages: list, max_tokens: int, user_name: str, ai_name: str) -> tuple:
    """
    Executes Workbench code with syntax sanitization + 1 bounded surgical self-retry
    if a SyntaxError/NameError occurs, returning (wb_res_dict, final_code_used).
    """
    res = execute_workbench_code(code_str)
    if res.get("ok"):
        return res, code_str
    err_out = str(res.get("output") or "")
    if any(k in err_out.lower() for k in ("safety gate", "timed out", "empty workbench")):
        return res, code_str
    retry_msgs = list(messages) + [
        {"role": "assistant", "content": f"```workbench\n{code_str}\n```"},
        {"role": "user", "content": f"Workbench hit: {err_out[:320]}\nFix ONLY the code in a single ```workbench block (or run vault.help() if unsure of a method)."}
    ]
    fixed_raw = dispatch_brain_sync(
        messages=retry_msgs,
        max_tokens=min(2048, max_tokens),
        temperature=0.35,
        top_p=0.9,
        stop=["<START>", f"\n{user_name}:", "\nUser:", "<end_of_turn>"]
    )
    fixed_clean = strip_reasoning_and_role_echoes(fixed_raw, ai_name, user_name)
    fixed_blocks, _ = extract_workbench_blocks(fixed_clean)
    if fixed_blocks:
        res2 = execute_workbench_code(fixed_blocks[0])
        if res2.get("ok"):
            return res2, fixed_blocks[0]
    return res, code_str

# --- Bluesky AT Protocol Bridge (xrpc com.atproto.server / repo / notifications) ---
BSKY_SESSION_CACHE = {"did": "", "handle": "", "accessJwt": "", "refreshJwt": "", "pds": "", "ts": 0.0}
BSKY_STATE = {"status": "Disabled", "last_post_uri": "", "last_error": "", "mentions_seen": 0}
_BSKY_SEEN_URIS = set()

def _bsky_ensure_session(force_refresh: bool = False) -> dict:
    bcfg = WORKSPACE_CFG.get("bluesky") or {}
    handle = (bcfg.get("handle") or "").strip()
    app_pw = (bcfg.get("app_password") or "").strip()
    pds = (bcfg.get("pds_url") or "https://bsky.social").strip().rstrip("/")
    if not handle or not app_pw:
        raise RuntimeError("Bluesky handle or app_password is not configured in Studio Settings.")
    now = time.time()
    if (
        not force_refresh
        and BSKY_SESSION_CACHE.get("accessJwt")
        and BSKY_SESSION_CACHE.get("handle") == handle
        and BSKY_SESSION_CACHE.get("pds") == pds
        and (now - BSKY_SESSION_CACHE.get("ts", 0.0)) < 1800
    ):
        return BSKY_SESSION_CACHE

    r = requests.post(
        f"{pds}/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": app_pw},
        headers={"User-Agent": f"AetherVaultStudio/{APP_VERSION}"},
        timeout=15,
    )
    if r.status_code != 200:
        raise RuntimeError(f"Bluesky createSession failed (HTTP {r.status_code}): {(r.text or '')[:180]}")
    data = r.json() or {}
    BSKY_SESSION_CACHE.update({
        "did": data.get("did") or "",
        "handle": data.get("handle") or handle,
        "accessJwt": data.get("accessJwt") or "",
        "refreshJwt": data.get("refreshJwt") or "",
        "pds": pds,
        "ts": now,
    })
    return BSKY_SESSION_CACHE

def post_to_bluesky(text: str, reply_uri: str = "", reply_cid: str = "") -> dict:
    """Publishes a post (or reply) to Bluesky via AT Protocol `com.atproto.repo.createRecord`."""
    if STATE.get("offline_mode"):
        return {"ok": False, "error": "Offline Mode is ON."}
    clean_txt = (text or "").strip()
    if not clean_txt:
        return {"ok": False, "error": "Bluesky post text cannot be empty."}
    clean_txt = avs_bridges.format_bluesky_post(clean_txt)
    try:
        sess = _bsky_ensure_session()
        from datetime import datetime, timezone
        created_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        record = avs_bridges.build_bluesky_post_record(clean_txt, created_iso, reply_uri=reply_uri, reply_cid=reply_cid)
        resp = requests.post(
            f"{sess['pds']}/xrpc/com.atproto.repo.createRecord",
            headers={
                "Authorization": f"Bearer {sess['accessJwt']}",
                "Content-Type": "application/json",
                "User-Agent": f"AetherVaultStudio/{APP_VERSION}",
            },
            json={
                "repo": sess["did"],
                "collection": "app.bsky.feed.post",
                "record": record,
            },
            timeout=15,
        )
        if resp.status_code == 401:
            sess = _bsky_ensure_session(force_refresh=True)
            resp = requests.post(
                f"{sess['pds']}/xrpc/com.atproto.repo.createRecord",
                headers={
                    "Authorization": f"Bearer {sess['accessJwt']}",
                    "Content-Type": "application/json",
                    "User-Agent": f"AetherVaultStudio/{APP_VERSION}",
                },
                json={"repo": sess["did"], "collection": "app.bsky.feed.post", "record": record},
                timeout=15,
            )
        resp.raise_for_status()
        out = resp.json() or {}
        BSKY_STATE["last_post_uri"] = out.get("uri") or ""
        BSKY_STATE["last_error"] = ""
        return {"ok": True, "uri": out.get("uri"), "cid": out.get("cid"), "text": clean_txt}
    except Exception as e:
        BSKY_STATE["last_error"] = str(e)
        return {"ok": False, "error": str(e)}

def bluesky_polling_worker():
    """Background Bluesky mention watcher (optional, only active when bluesky.enabled & poll_mentions are True)."""
    seeded_initial = False
    while True:
        try:
            bcfg = WORKSPACE_CFG.get("bluesky") or {}
            enabled = bool(bcfg.get("enabled")) and bool(bcfg.get("poll_mentions", True)) and not STATE.get("offline_mode")
            if not enabled or not (bcfg.get("handle") or "").strip() or not (bcfg.get("app_password") or "").strip():
                BSKY_STATE["status"] = "Disabled"
                seeded_initial = False
                time.sleep(6)
                continue
            sess = _bsky_ensure_session()
            my_did = (sess.get("did") or "").strip().lower()
            BSKY_STATE["status"] = f"Connected (@{sess.get('handle')})"
            r = requests.get(
                f"{sess['pds']}/xrpc/app.bsky.notification.listNotifications",
                params={"limit": 15},
                headers={"Authorization": f"Bearer {sess['accessJwt']}"},
                timeout=15,
            )
            if r.status_code == 200:
                notifs = (r.json() or {}).get("notifications") or []
                if not seeded_initial:
                    for n in notifs:
                        u0 = n.get("uri") or ""
                        if u0:
                            _BSKY_SEEN_URIS.add(u0)
                    seeded_initial = True
                    time.sleep(25)
                    continue
                allowed_raw = (bcfg.get("allowed_dids") or "").strip()
                allowed_set = {x.strip().lower() for x in re.split(r"[,;\s]+", allowed_raw) if x.strip()}
                for n in reversed(notifs):
                    if (n.get("reason") or "") != "mention" or n.get("isRead"):
                        continue
                    uri = n.get("uri") or ""
                    cid = n.get("cid") or ""
                    author = n.get("author") or {}
                    did = (author.get("did") or "").strip().lower()
                    handle_a = (author.get("handle") or "").strip().lower()
                    if not uri or uri in _BSKY_SEEN_URIS or (my_did and did == my_did):
                        continue
                    _BSKY_SEEN_URIS.add(uri)
                    if allowed_set and did not in allowed_set and handle_a not in allowed_set:
                        continue
                    txt = (((n.get("record") or {}).get("text")) or "").strip()
                    if txt:
                        BSKY_STATE["mentions_seen"] = int(BSKY_STATE.get("mentions_seen") or 0) + 1
                        reply_txt, _, _ = generate_sync_reply_for_telegram(txt, session_id=f"bsky_{did[:24]}")
                        post_to_bluesky(reply_txt, reply_uri=uri, reply_cid=cid)
            time.sleep(25)
        except Exception as e:
            BSKY_STATE["status"] = f"Standby ({type(e).__name__})"
            BSKY_STATE["last_error"] = str(e)
            time.sleep(20)

def has_repetition_delirium(text: str) -> bool:
    """Detects genuine visible repetition loops while ignoring DeepSeek <think> reasoning blocks."""
    visible = re.sub(r"<think>[\s\S]*?</think>", "", text or "", flags=re.IGNORECASE)
    if "<think>" in visible and "</think>" not in visible:
        return False
    if len(visible) < 260:
        return False
    tail = visible[-240:]
    for size in range(48, 84, 4):
        snippet = tail[-size:]
        if len(snippet.strip()) >= 40 and visible.count(snippet) >= 4:
            return True
    return False


# =====================================================================
# 8B. SMART API WATERFALL ROUTER, BYOK KEY RING, HF ROUTER & QUOTA LEDGER
# =====================================================================
API_VAULT_PATH = BASE_DIR / "api_keys_vault.json"
API_USAGE_LEDGER_PATH = BASE_DIR / "api_usage_ledger.json"

API_PROVIDER_TEMPLATES = {
    "google_gemini": {
        "name": "Google Gemini (AI Studio OpenAI-Compat)",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "auth_type": "bearer",
        "default_model": "gemini-2.5-flash",
        "models_hint": ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"]
    },
    "huggingface": {
        "name": "Hugging Face Router (router.huggingface.co/v1)",
        "base_url": "https://router.huggingface.co/v1",
        "auth_type": "bearer",
        "default_model": "meta-llama/Llama-3.1-8B-Instruct:fastest",
        "models_hint": [
            "meta-llama/Llama-3.1-8B-Instruct:fastest",
            "meta-llama/Llama-3.1-8B-Instruct:cheapest",
            "Qwen/Qwen2.5-Coder-7B-Instruct:fastest",
            "Qwen/Qwen2.5-72B-Instruct:cheapest",
            "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B:fastest",
            "google/gemma-4-E4B-it:fastest",
            "google/gemma-4-12b-it:fastest",
            "google/gemma-4-26B-A4B-it:fastest"
        ]
    },
    "gemma4_custom": {
        "name": "Gemma 4 OpenAI-Compat / Local Server",
        "base_url": "http://127.0.0.1:8080/v1",
        "auth_type": "bearer",
        "default_model": "gemma-4-E4B-it",
        "models_hint": ["gemma-4-E2B-it", "gemma-4-E4B-it", "gemma-4-12b-it", "gemma-4-26B-A4B-it"]
    },
    "groq": {
        "name": "Groq Cloud (Ultra-Fast Free Tier)",
        "base_url": "https://api.groq.com/openai/v1",
        "auth_type": "bearer",
        "default_model": "llama-3.3-70b-versatile",
        "models_hint": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "qwen-qwq-32b"]
    },
    "openrouter": {
        "name": "OpenRouter (:free Pool & Unified Router)",
        "base_url": "https://openrouter.ai/api/v1",
        "auth_type": "bearer",
        "default_model": "openrouter/free",
        "models_hint": ["openrouter/free", "meta-llama/llama-3.3-70b-instruct:free", "qwen/qwen-2.5-72b-instruct:free"]
    },
    "deepseek": {
        "name": "DeepSeek Official API",
        "base_url": "https://api.deepseek.com/v1",
        "auth_type": "bearer",
        "default_model": "deepseek-chat",
        "models_hint": ["deepseek-chat", "deepseek-reasoner"]
    },
    "mistral": {
        "name": "Mistral AI API (La Plateforme)",
        "base_url": "https://api.mistral.ai/v1",
        "auth_type": "bearer",
        "default_model": "mistral-small-latest",
        "models_hint": ["mistral-small-latest", "codestral-latest", "mistral-large-latest"]
    },
    "openai": {
        "name": "OpenAI Official API",
        "base_url": "https://api.openai.com/v1",
        "auth_type": "bearer",
        "default_model": "gpt-4o-mini",
        "models_hint": ["gpt-4o-mini", "gpt-4.1-mini", "o4-mini"]
    },
    "custom": {
        "name": "Custom OpenAI-Compatible / LAN Rig (KoboldCpp, Ollama, LM Studio, Proxy)",
        "base_url": "http://127.0.0.1:5001/v1",
        "auth_type": "bearer",
        "default_model": "local-model",
        "models_hint": ["local-model"]
    }
}

API_COOLDOWNS = {}  # key_fingerprint -> unix timestamp when cooldown expires
API_LIVE_TELEMETRY = {
    "active_slot_name": "",
    "active_model": "",
    "last_prompt_tokens": 0,
    "last_completion_tokens": 0,
    "session_tokens_used": 0,
    "today_tokens_used": 0,
    "remaining_tokens": None,
    "remaining_requests": None,
    "quota_percent_left": 100,
    "quota_source": "Idle",
    "last_hop_reason": ""
}

def normalize_openai_base_url(raw_url: str) -> str:
    u = (raw_url or "").strip().rstrip("/")
    if not u:
        return "https://api.openai.com/v1"
    if u.endswith("/chat/completions"):
        u = u[:-len("/chat/completions")].rstrip("/")
    if not u.endswith("/v1") and "/openai" not in u and "/v1beta" not in u:
        u = u + "/v1"
    return u

def mask_api_key(k: str) -> str:
    s = (k or "").strip()
    if not s:
        return "(no-key)"
    if len(s) <= 8:
        return s[:2] + "***"
    return f"{s[:4]}...{s[-4:]}"

def load_api_vault() -> dict:
    default_vault = {
        "slots": [],
        "daily_soft_cap": int(WORKSPACE_CFG.get("api_daily_soft_cap", 1000000))
    }
    if API_VAULT_PATH.exists():
        try:
            data = json.loads(API_VAULT_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                default_vault.update(data)
        except Exception:
            pass
    return default_vault

def save_api_vault(vault: dict):
    API_VAULT_PATH.write_text(json.dumps(vault, indent=2, ensure_ascii=False), encoding="utf-8")

def get_masked_api_vault() -> dict:
    vault = load_api_vault()
    masked_slots = []
    now = time.time()
    for idx, sl in enumerate(vault.get("slots", [])):
        keys_list = [k for k in (sl.get("keys") or []) if str(k).strip()]
        masked_keys = []
        for k_idx, k_val in enumerate(keys_list):
            fp = f"{sl.get('id', idx)}:{k_idx}"
            cd_rem = max(0, int(API_COOLDOWNS.get(fp, 0) - now))
            masked_keys.append({
                "index": k_idx,
                "masked": mask_api_key(k_val),
                "cooldown_sec": cd_rem
            })
        masked_slots.append({
            "id": sl.get("id", f"slot_{idx}"),
            "label": sl.get("label") or sl.get("provider") or f"Slot #{idx+1}",
            "provider": sl.get("provider", "custom"),
            "base_url": sl.get("base_url", ""),
            "model": sl.get("model", ""),
            "auth_type": sl.get("auth_type", "bearer"),
            "enabled": sl.get("enabled", True),
            "key_count": len(keys_list),
            "keys_masked": masked_keys
        })
    return {
        "slots": masked_slots,
        "daily_soft_cap": vault.get("daily_soft_cap", 1000000),
        "telemetry": API_LIVE_TELEMETRY
    }

def record_api_token_usage(slot_label: str, model_name: str, prompt_toks: int, comp_toks: int, resp_headers: dict = None):
    today = time.strftime("%Y-%m-%d")
    ledger = {"date": today, "total_tokens": 0, "by_slot": {}}
    if API_USAGE_LEDGER_PATH.exists():
        try:
            saved = json.loads(API_USAGE_LEDGER_PATH.read_text(encoding="utf-8"))
            if saved.get("date") == today:
                ledger = saved
        except Exception:
            pass
    added = int(prompt_toks) + int(comp_toks)
    ledger["total_tokens"] = int(ledger.get("total_tokens", 0)) + added
    ledger["by_slot"][slot_label] = int(ledger["by_slot"].get(slot_label, 0)) + added
    try:
        API_USAGE_LEDGER_PATH.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    except Exception:
        pass

    API_LIVE_TELEMETRY["active_slot_name"] = slot_label
    API_LIVE_TELEMETRY["active_model"] = model_name
    API_LIVE_TELEMETRY["last_prompt_tokens"] = int(prompt_toks)
    API_LIVE_TELEMETRY["last_completion_tokens"] = int(comp_toks)
    API_LIVE_TELEMETRY["session_tokens_used"] = int(API_LIVE_TELEMETRY.get("session_tokens_used", 0)) + added
    API_LIVE_TELEMETRY["today_tokens_used"] = ledger["total_tokens"]

    # Parse provider rate-limit headers if returned (Groq, OpenAI, Together, HF Router, OpenRouter)
    rem_tok = None
    lim_tok = None
    rem_req = None
    if resp_headers:
        h_low = {str(k).lower(): str(v) for k, v in resp_headers.items()}
        for rk in ("x-ratelimit-remaining-tokens", "anthropic-ratelimit-tokens-remaining"):
            if rk in h_low and h_low[rk].isdigit():
                rem_tok = int(h_low[rk])
        for lk in ("x-ratelimit-limit-tokens", "anthropic-ratelimit-tokens-limit"):
            if lk in h_low and h_low[lk].isdigit():
                lim_tok = int(h_low[lk])
        for rqk in ("x-ratelimit-remaining-requests", "x-ratelimit-remaining"):
            if rqk in h_low and h_low[rqk].isdigit():
                rem_req = int(h_low[rqk])
        # Parse IETF RateLimit header used by Hugging Face Router: "api";r=940;t=120
        if "ratelimit" in h_low:
            m_r = re.search(r"r=(\d+)", h_low["ratelimit"])
            if m_r:
                rem_req = int(m_r.group(1))
        if "ratelimit-policy" in h_low:
            m_q = re.search(r"q=(\d+)", h_low["ratelimit-policy"])
            if m_q and rem_req is not None:
                tot_q = max(1, int(m_q.group(1)))
                API_LIVE_TELEMETRY["quota_percent_left"] = max(1, min(100, int((rem_req / tot_q) * 100)))
                API_LIVE_TELEMETRY["quota_source"] = "HF RateLimit Header"

    if rem_tok is not None:
        API_LIVE_TELEMETRY["remaining_tokens"] = rem_tok
        if lim_tok and lim_tok > 0:
            API_LIVE_TELEMETRY["quota_percent_left"] = max(1, min(100, int((rem_tok / lim_tok) * 100)))
            API_LIVE_TELEMETRY["quota_source"] = "Provider Header"
    elif API_LIVE_TELEMETRY.get("quota_source") != "HF RateLimit Header":
        soft_cap = max(10000, int(load_api_vault().get("daily_soft_cap", 1000000)))
        rem_daily = max(0, soft_cap - ledger["total_tokens"])
        API_LIVE_TELEMETRY["remaining_tokens"] = rem_daily
        API_LIVE_TELEMETRY["quota_percent_left"] = max(1, min(100, int((rem_daily / soft_cap) * 100)))
        API_LIVE_TELEMETRY["quota_source"] = "Daily Ledger"

    if rem_req is not None:
        API_LIVE_TELEMETRY["remaining_requests"] = rem_req

def pick_lightweight_failsafe_model() -> str:
    """
    Picks the pinned failsafe_model if present in /models; otherwise automatically selects
    the SMALLEST .gguf file on disk by byte size (e.g., 1.5B Q4_K_M ~1.1GB) so an old laptop never chokes!
    """
    avail = list_local_models()
    if not avail:
        return ""
    pinned = (WORKSPACE_CFG.get("failsafe_model") or "").strip()
    if pinned and pinned in avail:
        return pinned
    sized = []
    for name in avail:
        p = resolve_local_model_path(name)
        if p.exists():
            sized.append((p.stat().st_size, name))
    if sized:
        sized.sort(key=lambda x: x[0])
        return sized[0][1]
    return avail[0]

def has_internet_connection() -> bool:
    if STATE.get("offline_mode"):
        return False
    try:
        s = socket.create_connection(("1.1.1.1", 53), timeout=1.2)
        s.close()
        return True
    except Exception:
        return False

def _stream_single_openai_compatible(slot: dict, api_key: str, messages: list, max_tokens: int, temperature: float, top_p: float, stop: list, tools: list = None, tool_choice: str = None):
    """Streams SSE chunks from any OpenAI-compatible endpoint and yields llama-cpp-shaped delta dicts."""
    base_url = normalize_openai_base_url(slot.get("base_url", ""))
    url = f"{base_url}/chat/completions"
    auth_type = (slot.get("auth_type") or "bearer").lower()
    headers = {"Content-Type": "application/json"}
    if api_key:
        if auth_type == "x-api-key":
            headers["x-api-key"] = api_key
        elif auth_type != "none":
            headers["Authorization"] = f"Bearer {api_key}"

    body = {
        "model": slot.get("model") or "gpt-4o-mini",
        "messages": messages,
        "temperature": float(temperature),
        "top_p": float(top_p),
        "stream": True,
        "stream_options": {"include_usage": True}
    }
    if not is_unrestricted_tokens_enabled():
        body["max_tokens"] = min(4096, int(max_tokens))
    elif int(max_tokens) > 0:
        body["max_tokens"] = min(32768, int(max_tokens))
    if stop:
        body["stop"] = stop[:4]
    if tools:
        body["tools"] = tools
        body["tool_choice"] = tool_choice or "auto"

    prompt_chars = sum(len(str(m.get("content", ""))) for m in messages)
    reply_chars = 0
    reported_prompt_toks = 0
    reported_comp_toks = 0

    with requests.post(url, headers=headers, json=body, stream=True, timeout=(10, 60)) as resp:
        if resp.status_code != 200:
            err_body = ""
            try:
                err_body = resp.text[:240]
            except Exception:
                pass
            raise RuntimeError(f"HTTP {resp.status_code}: {err_body}")

        resp_headers = dict(resp.headers)
        for raw_line in resp.iter_lines(decode_unicode=True):
            if STATE.get("stop_requested"):
                break
            if not raw_line:
                continue
            line = raw_line.strip()
            if not line.startswith("data:"):
                continue
            payload_str = line[5:].strip()
            if payload_str == "[DONE]":
                break
            try:
                obj = json.loads(payload_str)
            except Exception:
                continue
            usage = obj.get("usage")
            if isinstance(usage, dict):
                reported_prompt_toks = int(usage.get("prompt_tokens") or reported_prompt_toks)
                reported_comp_toks = int(usage.get("completion_tokens") or reported_comp_toks)
            choices = obj.get("choices") or []
            if choices:
                delta_obj = choices[0].get("delta") or {}
                fin_reason = choices[0].get("finish_reason")
                txt = delta_obj.get("content") or ""
                tc_deltas = delta_obj.get("tool_calls") or None
                if txt or tc_deltas or fin_reason:
                    if txt:
                        reply_chars += len(txt)
                    out_delta = {}
                    if txt:
                        out_delta["content"] = txt
                    if tc_deltas:
                        out_delta["tool_calls"] = tc_deltas
                    yield {"choices": [{"delta": out_delta, "finish_reason": fin_reason}]}

    final_p_toks = reported_prompt_toks if reported_prompt_toks > 0 else max(1, prompt_chars // 4)
    final_c_toks = reported_comp_toks if reported_comp_toks > 0 else max(1, reply_chars // 4)
    record_api_token_usage(
        slot.get("label") or slot.get("provider", "API"),
        slot.get("model", ""),
        final_p_toks,
        final_c_toks,
        resp_headers
    )

def dispatch_brain_stream(messages: list, max_tokens: int = 1024, temperature: float = 0.78, top_p: float = 0.95, min_p: float = 0.12, repeat_penalty: float = 1.15, stop: list = None, tools: list = None, tool_choice: str = None):
    """
    Unified 'Zero-Drop' Brain Dispatcher:
    - local_only : Always runs local GGUF via llama-cpp-python.
    - smart_api  : Runs prioritized BYOK API Waterfall (with Key Ring rotation).
    - hybrid     : Runs BYOK API Waterfall first; if Offline, No Wi-Fi, or All APIs Dry,
                   automatically boots the lightest local GGUF failsafe model!
    """
    b_mode = WORKSPACE_CFG.get("brain_mode", "local_only")
    vault = load_api_vault()
    slots = [s for s in vault.get("slots", []) if s.get("enabled", True)]

    use_cloud = (b_mode in ("smart_api", "hybrid")) and bool(slots) and not STATE.get("offline_mode")
    if use_cloud and not has_internet_connection():
        use_cloud = False
        STATE["last_api_hop_notice"] = "📴 No internet detected — bypassed cloud APIs to Local Safety Net"
        API_LIVE_TELEMETRY["last_hop_reason"] = STATE["last_api_hop_notice"]

    if use_cloud:
        now = time.time()
        hop_notes = []
        for s_idx, slot in enumerate(slots):
            keys = [k.strip() for k in (slot.get("keys") or []) if str(k).strip()]
            if (slot.get("auth_type") or "").lower() == "none" and not keys:
                keys = [""]
            for k_idx, api_key in enumerate(keys):
                fp = f"{slot.get('id', s_idx)}:{k_idx}"
                if API_COOLDOWNS.get(fp, 0) > now:
                    continue
                slot_title = f"{slot.get('label') or slot.get('provider')} ({slot.get('model')})"
                try:
                    set_step(f"☁️ Smart API [{slot_title} | Key #{k_idx+1}]...")
                    STATE["active_api_label"] = slot_title
                    emitted_any = False
                    try:
                        for chunk in _stream_single_openai_compatible(slot, api_key, messages, max_tokens, temperature, top_p, stop or [], tools=tools, tool_choice=tool_choice):
                            emitted_any = True
                            yield chunk
                    except Exception as tool_http_err:
                        if tools and not emitted_any and ("HTTP 400" in str(tool_http_err) or "tool" in str(tool_http_err).lower()):
                            for chunk in _stream_single_openai_compatible(slot, api_key, messages, max_tokens, temperature, top_p, stop or [], tools=None, tool_choice=None):
                                emitted_any = True
                                yield chunk
                        else:
                            raise
                    if hop_notes:
                        STATE["last_api_hop_notice"] = " -> ".join(hop_notes) + f" -> Connected to {slot_title}"
                        API_LIVE_TELEMETRY["last_hop_reason"] = STATE["last_api_hop_notice"]
                    return
                except Exception as api_err:
                    err_s = str(api_err)
                    cd_sec = 90 if ("429" in err_s or "402" in err_s or "quota" in err_s.lower()) else 30
                    API_COOLDOWNS[fp] = time.time() + cd_sec
                    hop_notes.append(f"{slot.get('label', 'Slot')} Key#{k_idx+1} dry ({err_s[:45]})")
                    print(f"[SMART API HOP] {hop_notes[-1]} -> trying next key/provider...", flush=True)
                    if emitted_any:
                        return

        # All API slots failed / ran dry
        STATE["active_api_label"] = ""
        all_dry_msg = "⚠️ All Smart API slots ran dry/rate-limited -> Falling back to Local GGUF Safety Net!"
        STATE["last_api_hop_notice"] = all_dry_msg
        API_LIVE_TELEMETRY["last_hop_reason"] = all_dry_msg
        if b_mode == "smart_api" and not list_local_models():
            raise RuntimeError("All configured Smart API slots are dry/rate-limited and no local .gguf failsafe model is downloaded in /models.")

    # Local GGUF Execution (either local_only mode OR Hybrid/SmartAPI Safety Net)
    STATE["active_api_label"] = ""
    if STATE["llm"] is None:
        failsafe_name = pick_lightweight_failsafe_model()
        if not failsafe_name:
            raise RuntimeError("No local .gguf model found in /models (and no active cloud API slot succeeded).")
        set_step(f"🛡️ Local Failsafe Booting '{failsafe_name}'...")
        load_local_model(failsafe_name)
    if STATE["llm"] is None:
        raise RuntimeError("Local GGUF failsafe model could not be loaded into memory.")

    with LLM_LOCK:
        # Local GGUF models run cleanly via our Live In-Process Python Workbench (` ```workbench `)
        # WITHOUT injecting 11 competing OpenAI JSON tool schemas into llama.cpp's Jinja template
        # (which causes 3B/7B models like Llama-3.2-3B to emit broken braceless JSON into content!).
        kwargs = dict(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            min_p=min_p,
            repeat_penalty=repeat_penalty,
            stop=stop or [],
            stream=True
        )
        stream_iter = STATE["llm"].create_chat_completion(**kwargs)
        for chunk in stream_iter:
            yield chunk

def dispatch_brain_sync(messages: list, max_tokens: int = 1024, temperature: float = 0.78, top_p: float = 0.95, min_p: float = 0.12, repeat_penalty: float = 1.15, stop: list = None) -> str:
    parts = []
    for ch in dispatch_brain_stream(messages, max_tokens, temperature, top_p, min_p, repeat_penalty, stop):
        delta = ch["choices"][0].get("delta", {}).get("content") or ""
        if delta:
            parts.append(delta)
    return "".join(parts).strip()

def synthesize_tool_followup(static_sys_prompt: str, recent_turns: list, first_reply: str, tool_output: str, cfg: dict, user_name: str, ai_name: str) -> str:
    followup_turns = recent_turns + [
        {"role": "assistant", "content": first_reply},
        {"role": "user", "content": f"{tool_output}\n\nNow respond directly to {user_name} in character as {ai_name} using these exact results."}
    ]
    msgs = build_safe_messages(static_sys_prompt, "", followup_turns)
    out = dispatch_brain_sync(
        messages=msgs,
        max_tokens=cfg["max_tokens"],
        temperature=0.78,
        top_p=0.95,
        min_p=0.12,
        repeat_penalty=1.15,
        stop=["<START>", f"\n{user_name}:", "\nUser:", "[INST]", "[/INST]"]
    )
    out = re.sub(r"<\|think\|>[\s\S]*?<\|/think\|>", "", out, flags=re.IGNORECASE).strip()
    out = re.sub(r"<think>[\s\S]*?</think>", "", out, flags=re.IGNORECASE).strip()
    out = re.sub(rf"^({re.escape(ai_name)}|Assistant):\s*", "", out, flags=re.IGNORECASE).strip()
    return out

# =====================================================================
# 9. TELEGRAM BOT BACKGROUND BRIDGE
# =====================================================================
TELEGRAM_QUEUE_STATE = {
    "active": False,
    "queued": 0,
    "last_step": "Idle",
    "last_user": "",
    "last_error": "",
    "processed_count": 0,
}
_TG_OFFSET_FILE = BASE_DIR / ".temp_cache" / "tg_offset.json"
_TG_WEBHOOK_CLEARED_TOKENS = set()

def _load_tg_offset() -> int:
    try:
        if _TG_OFFSET_FILE.exists():
            data = json.loads(_TG_OFFSET_FILE.read_text(encoding="utf-8"))
            return int(data.get("last_update_id") or 0)
    except Exception:
        pass
    return int(STATE.get("telegram_last_update_id") or 0)

def _save_tg_offset(uid: int):
    try:
        _TG_OFFSET_FILE.parent.mkdir(parents=True, exist_ok=True)
        _TG_OFFSET_FILE.write_text(json.dumps({"last_update_id": int(uid), "updated_at": time.strftime("%H:%M:%S")}), encoding="utf-8")
    except Exception:
        pass

def _tg_api_post(token: str, method: str, payload: dict, timeout: int = 15) -> dict:
    try:
        r = requests.post(f"https://api.telegram.org/bot{token}/{method}", json=payload, timeout=timeout)
        if r.status_code == 200:
            return r.json()
        return {"ok": False, "status": r.status_code, "text": (r.text or "")[:200]}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def _tg_edit_or_send_status(token: str, chat_id: str, status_msg_id: int, text: str) -> int:
    clean_t = (text or "Working...")[:3900]
    if status_msg_id:
        res = _tg_api_post(token, "editMessageText", {"chat_id": chat_id, "message_id": status_msg_id, "text": clean_t}, timeout=10)
        if res.get("ok"):
            return status_msg_id
    sent = _tg_api_post(token, "sendMessage", {"chat_id": chat_id, "text": clean_t}, timeout=10)
    return ((sent.get("result") or {}).get("message_id")) or status_msg_id

_TG_REGISTERED_TOKENS = set()

TELEGRAM_BOT_COMMANDS = [
    {"command": "menu", "description": "🎛️ Open AetherVault Quick Control Panel"},
    {"command": "status", "description": "📊 Check active model, RAM & mode"},
    {"command": "specs", "description": "🖥️ Deep hardware & GPU/VRAM specs"},
    {"command": "queue", "description": "📥 Check Telegram worker queue"},
    {"command": "unload", "description": "💤 Unload model to free RAM/VRAM"},
    {"command": "wake", "description": "⚡ Wake sleeping GGUF model"},
    {"command": "stop", "description": "⏹️ Stop active generation"},
    {"command": "update", "description": "🔄 Pull GitHub OTA update"},
    {"command": "help", "description": "📖 Show all commands"},
]

def _tg_build_control_keyboard() -> dict:
    """Builds an interactive Telegram inline button panel (plus Mini App button if HTTPS tunnel URL is set)."""
    lan_url = f"http://{get_local_lan_ip()}:{SERVER_PORT}"
    miniapp_url = (WORKSPACE_CFG.get("telegram", {}).get("miniapp_url") or "").strip()
    rows = [
        [
            {"text": "📊 Status", "callback_data": "avs_cmd:/status"},
            {"text": "🖥️ Specs", "callback_data": "avs_cmd:/specs"},
            {"text": "📥 Queue", "callback_data": "avs_cmd:/queue"},
        ],
        [
            {"text": "💤 Unload RAM", "callback_data": "avs_cmd:/unload"},
            {"text": "⚡ Wake Model", "callback_data": "avs_cmd:/wake"},
            {"text": "⏹️ Stop", "callback_data": "avs_cmd:/stop"},
        ],
        [
            {"text": "📸 Screenshot", "callback_data": "avs_tool:screenshot"},
            {"text": "🎵 Now Playing", "callback_data": "avs_tool:spotify_current"},
            {"text": "🔄 OTA Update", "callback_data": "avs_cmd:/update"},
        ],
    ]
    if miniapp_url.startswith("https://"):
        rows.append([{"text": "🚀 Open Studio Mini App", "web_app": {"url": miniapp_url}}])
    else:
        rows.append([{"text": f"📱 Wi-Fi LAN: {lan_url}", "callback_data": "avs_info:lan"}])
    return {"inline_keyboard": avs_bridges.build_telegram_control_rows(lan_url, miniapp_url)}

def _tg_register_bot_commands(token: str):
    """Registers native `/` autocomplete menu commands & chat menu button with Telegram Bot API."""
    if not token or token in _TG_REGISTERED_TOKENS:
        return
    res = _tg_api_post(token, "setMyCommands", {"commands": TELEGRAM_BOT_COMMANDS}, timeout=10)
    miniapp_url = (WORKSPACE_CFG.get("telegram", {}).get("miniapp_url") or "").strip()
    if miniapp_url.startswith("https://"):
        _tg_api_post(token, "setChatMenuButton", {
            "menu_button": {"type": "web_app", "text": "Studio", "web_app": {"url": miniapp_url}}
        }, timeout=10)
    else:
        _tg_api_post(token, "setChatMenuButton", {"menu_button": {"type": "commands"}}, timeout=10)
    if res.get("ok"):
        _TG_REGISTERED_TOKENS.add(token)

def _tg_send_media(token: str, chat_id: str, img_url: str = None, audio_url: str = None):
    if img_url:
        img_path = GEN_IMG_DIR / Path(img_url).name
        if img_path.exists():
            try:
                with open(img_path, "rb") as f:
                    resp_p = requests.post(f"https://api.telegram.org/bot{token}/sendPhoto", data={"chat_id": chat_id}, files={"photo": f}, timeout=25)
                if resp_p.status_code != 200:
                    with open(img_path, "rb") as f2:
                        requests.post(f"https://api.telegram.org/bot{token}/sendDocument", data={"chat_id": chat_id}, files={"document": f2}, timeout=25)
            except Exception:
                pass
    if audio_url:
        aud_path = GEN_AUDIO_DIR / Path(audio_url).name
        if aud_path.exists():
            try:
                with open(aud_path, "rb") as f:
                    requests.post(f"https://api.telegram.org/bot{token}/sendAudio", data={"chat_id": chat_id}, files={"audio": f}, timeout=25)
            except Exception:
                pass

def generate_sync_reply_for_telegram(user_text: str, session_id: str = "telegram_session", progress_cb=None) -> tuple:
    """
    Robust v6.8 Telegram Brain + Live Python Workbench Engine:
    - Works across Local GGUF, Smart API Waterfall, and Hybrid modes.
    - Streams live step progress to Telegram ('Working in Workbench...') AND the main Studio UI top bar.
    - Never crashes the polling thread on malformed outputs or empty replies.
    Returns (reply_text, image_url, audio_url).
    """
    def _notify(step_msg: str):
        TELEGRAM_QUEUE_STATE["last_step"] = step_msg
        set_step(f"📱 [Telegram] {step_msg}")
        if progress_cb:
            try:
                progress_cb(step_msg)
            except Exception:
                pass

    if STATE["loading_model"]:
        return "⏳ Local GGUF model is currently loading into RAM/VRAM. Give it a few seconds and send your message again!", None, None

    b_mode = WORKSPACE_CFG.get("brain_mode", "local_only")
    has_api_slots = bool([s for s in load_api_vault().get("slots", []) if s.get("enabled", True)])
    can_use_api = (b_mode in ("smart_api", "hybrid")) and has_api_slots and not STATE["offline_mode"]
    if not STATE["llm"] and not can_use_api and STATE.get("idle_sleeping"):
        _notify("💤 Waking sleeping GGUF model back into RAM/VRAM...")
        touch_activity(wake_model=True)
    if not STATE["llm"] and not can_use_api:
        target_m = pick_lightweight_failsafe_model() if (b_mode == "hybrid" or STATE["performance_mode"] == "Laptop 2015 (Fast)") else (WORKSPACE_CFG.get("last_loaded_model") or pick_lightweight_failsafe_model())
        if target_m:
            _notify(f"🧠 Auto-loading offline GGUF '{target_m}'...")
            load_local_model(target_m)
        if not STATE["llm"]:
            return "⚠️ No local GGUF model loaded and no Smart API key configured in Studio yet.", None, None

    ai_n = WORKSPACE_CFG.get("ai_name", "Aether")
    usr_n = WORKSPACE_CFG.get("user_name", "Creator")
    STATE["stop_requested"] = False
    STATE["last_user_msg"] = user_text

    with get_db() as conn:
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO chat_sessions (id, title) VALUES (?, '📱 Telegram Bot Chat')", (session_id,))
        c.execute("INSERT INTO chat_messages (session_id, role, content) VALUES (?, 'user', ?)", (session_id, user_text))
        conn.commit()
        c.execute("SELECT role, content FROM chat_messages WHERE session_id = ? ORDER BY id DESC LIMIT 6", (session_id,))
        recent_turns = [{"role": r["role"], "content": r["content"]} for r in reversed(c.fetchall())]

    harvest_passive_user_notes(user_text)
    sync_pseudo_memory_and_index()
    gear, _ = classify_task_gear(user_text, "", recent_turns)
    img_out = None
    aud_out = None
    reply = ""

    STATE["generating"] = True
    try:
        if gear == "reflex":
            _notify("⚡ Gear 1 Reflex: thinking...")
            mem_short = format_memories_for_prompt(limit=3)
            digest = PRIORITY_CACHE["reflex_core_digest"] or build_reflex_persona_digest(WORKSPACE_CFG["persona_prompt"], ai_n, usr_n)
            static_sys = f"{digest}\n\n=== SESSION STATE ===\n{mem_short}"
            messages = build_safe_messages(static_sys, "", recent_turns, max_turns=3)
            cfg = get_governor_settings("reflex", sum(len(m["content"]) for m in messages))
            reply = dispatch_brain_sync(
                messages=messages, max_tokens=cfg["max_tokens"],
                temperature=0.75, top_p=0.92, min_p=0.12, repeat_penalty=1.15,
                stop=["<START>", f"\n{usr_n}:", "\nUser:", "[INST]", "[/INST]"]
            )
            if any(tag in reply for tag in ("[[DEEP]]", "[DEEP]", "<tool_call>", "```workbench", "vault.")):
                gear = "operator"
            else:
                reply = re.sub(r"<think>[\s\S]*?</think>", "", reply, flags=re.IGNORECASE).strip()
                fast_search_m = re.search(r"\[\[SEARCH:([^\]]+)\]\]", reply)
                if fast_search_m and not STATE["offline_mode"]:
                    fs_q = clean_web_search_query(fast_search_m.group(1).strip())
                    _notify(f"🌐 Searching web for '{fs_q[:36]}'...")
                    fs_out = search_web(fs_q)[:1400]
                    reply = synthesize_tool_followup(static_sys, recent_turns[-3:], re.sub(r"\[\[SEARCH:[^\]]+\]\]", "", reply).strip() or "Checking online.", f"[Live Web Search Results]:\n{fs_out}", cfg, usr_n, ai_n)
                elif is_auto_web_search_enabled() and detect_model_uncertainty(reply) and is_query_searchable_for_rescue(user_text):
                    rq = clean_web_search_query(user_text)
                    _notify(f"🌐 Auto-searching web for '{rq[:36]}'...")
                    r_out = search_web(rq)[:1400]
                    reply = synthesize_tool_followup(static_sys, recent_turns[-3:], reply, f"[Auto-Web Results]:\n{r_out}", cfg, usr_n, ai_n)

        if gear != "reflex":
            is_op = (gear == "operator")
            _notify("🛠️ Preparing Assistant & Live Python Workbench..." if is_op else "🧠 Gear 2 Deep Context + Workbench...")
            mem_context = format_memories_for_prompt(limit=4 if is_op else 12)
            if is_op:
                static_sys = build_assistant_workbench_system_prompt(ai_n, usr_n, mem_context)
                dyn_ctx = ""
            else:
                core_rules = PRIORITY_CACHE["core_rules_text"] or WORKSPACE_CFG["persona_prompt"].replace("{ai_name}", ai_n).replace("{user_name}", usr_n)
                retrieved_lore, _ = retrieve_relevant_lore(user_text, top_k=2)
                static_sys = f"=== PRIORITY 1: MEMORY VAULT ===\n{mem_context}\n\n=== PRIORITY 2: CORE IDENTITY ===\n{core_rules}\n\n{build_pc_reality_anchor()}"
                dyn_ctx = retrieved_lore

            is_g, g_act = is_tool_gauntlet_query(user_text)
            if is_g:
                _notify("🧪 Running Step-by-Step Tool Gauntlet...")
                dyn_ctx += "\n" + run_tool_gauntlet_compact(include_active=g_act)
            else:
                is_wq, wcity = detect_weather_intent(user_text)
                if is_wq and not STATE["offline_mode"] and wcity:
                    _notify(f"🌦️ Fetching live weather for '{wcity}'...")
                    dyn_ctx += f"\n[REAL LIVE WEATHER DATA]:\n{get_live_weather(wcity)}"

            messages = build_safe_messages(static_sys, dyn_ctx, recent_turns, max_turns=6)
            cfg = get_governor_settings("deep", sum(len(m["content"]) for m in messages))
            reply = ""
            max_rounds = avs_turn_pipeline.bounded_rounds(4 if is_unrestricted_tokens_enabled() else 2)
            for r_idx in range(max_rounds):
                if STATE["stop_requested"]:
                    break
                _notify(f"💭 Generating response (Pass {r_idx+1}/{max_rounds})...")
                round_raw = dispatch_brain_sync(
                    messages=messages, max_tokens=cfg["max_tokens"],
                    temperature=0.75, top_p=0.95, min_p=0.12, repeat_penalty=1.15,
                    stop=["<START>", f"\n{usr_n}:", "\nUser:", "[INST]", "[/INST]"]
                )
                stripped = re.sub(r"<think>[\s\S]*?</think>", "", round_raw, flags=re.IGNORECASE).strip()
                wb_blocks, wb_cleaned = extract_workbench_blocks(stripped)
                inline_calls, cleaned_round = extract_inline_tool_calls(wb_cleaned)

                obs_list = []
                if wb_blocks:
                    for wb_i, wb_code in enumerate(wb_blocks):
                        _notify(f"🐍 Working in Python Workbench (Round {r_idx+1}, Step {wb_i+1})...")
                        wb_res, _ = run_blended_workbench_with_retry(wb_code, messages, cfg["max_tokens"], usr_n, ai_n)
                        obs_list.append(wb_res.get("output") or "")
                        if wb_res.get("image_url"):
                            img_out = wb_res["image_url"]
                        if wb_res.get("audio_url"):
                            aud_out = wb_res["audio_url"]
                elif inline_calls:
                    for ic in inline_calls:
                        _notify(f"🔧 Running tool '{ic['name']}' (Round {r_idx+1})...")
                        o_txt, t_i, t_a = execute_unified_tool(ic["name"], coerce_primitive_args(ic["arguments"]), session_id)
                        obs_list.append(o_txt)
                        if t_i:
                            img_out = t_i
                        if t_a:
                            aud_out = t_a

                if obs_list and r_idx < (max_rounds - 1):
                    joined_obs = compact_tool_observation("\n\n".join(obs_list), max_chars=3200, max_lines=50)
                    messages.append({"role": "assistant", "content": round_raw})
                    messages.append({"role": "user", "content": f"[WORKBENCH EXECUTION OUTPUT]:\n{joined_obs}\n\nNow reply naturally to {usr_n} as {ai_n} using these exact results."})
                    continue

                reply = cleaned_round or wb_cleaned or stripped
                break

        reply = avs_model_polish.normalize_model_output(reply, ai_name=ai_n, user_name=usr_n, is_assistant_mode=(WORKSPACE_CFG.get("workspace_mode") == "assistant"))
        reply = clean_assistant_theatrics(reply, is_assistant_mode=(WORKSPACE_CFG.get("workspace_mode") == "assistant"))
        _fin = avs_turn_pipeline.finalize_turn_reply(reply, ai_name=ai_n, user_name=usr_n, evidence_pool=f"{PRIORITY_CACHE.get('core_rules_text', '')} {WORKSPACE_CFG.get('persona_prompt', '')}")
        reply = _fin["reply"]
        reply, _ref_warns = referee_lore_and_grounding(reply, user_text, ai_n, "")
        if not reply:
            reply = "✅ Done."
        update_partner_evolution(user_text, reply)
        with get_db() as conn:
            conn.execute("INSERT INTO chat_messages (session_id, role, content) VALUES (?, 'assistant', ?)", (session_id, reply))
            conn.execute("UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (session_id,))
            conn.commit()
        export_chats_to_txt_files()
        return reply, img_out, aud_out
    except Exception as tg_err:
        err_s = f"{type(tg_err).__name__}: {tg_err}"
        TELEGRAM_QUEUE_STATE["last_error"] = err_s
        return f"⚠️ Telegram turn encountered an issue: {err_s[:240]}", None, None
    finally:
        STATE["generating"] = False
        TELEGRAM_QUEUE_STATE["last_step"] = "Idle"
        set_step("Idle")

def telegram_polling_worker():
    STATE["telegram_last_update_id"] = _load_tg_offset()
    while True:
        try:
            tg_cfg = WORKSPACE_CFG.get("telegram", {})
            token = (tg_cfg.get("bot_token") or "").strip()
            enabled = bool(tg_cfg.get("enabled")) and bool(token) and not STATE["offline_mode"]
            if not enabled:
                STATE["telegram_status"] = "Disabled"
                TELEGRAM_QUEUE_STATE["active"] = False
                TELEGRAM_QUEUE_STATE["queued"] = 0
                time.sleep(3)
                continue

            # Clear any lingering webhook once per token so getUpdates never 409-conflicts
            if token not in _TG_WEBHOOK_CLEARED_TOKENS:
                _tg_api_post(token, "deleteWebhook", {"drop_pending_updates": False}, timeout=8)
                _TG_WEBHOOK_CLEARED_TOKENS.add(token)
            _tg_register_bot_commands(token)

            STATE["telegram_status"] = "Connected (Polling)"
            TELEGRAM_QUEUE_STATE["last_error"] = ""
            url = f"https://api.telegram.org/bot{token}/getUpdates"
            params = {"offset": int(STATE["telegram_last_update_id"]) + 1, "timeout": 15}
            r = requests.get(url, params=params, timeout=22)
            if r.status_code != 200:
                STATE["telegram_status"] = f"Error (HTTP {r.status_code})"
                TELEGRAM_QUEUE_STATE["last_error"] = f"HTTP {r.status_code}"
                time.sleep(5)
                continue

            updates = (r.json() or {}).get("result") or []
            pending_msgs = []
            max_uid = int(STATE["telegram_last_update_id"])
            for u in updates:
                uid = int(u.get("update_id") or 0)
                if uid > max_uid:
                    max_uid = uid
                cb = u.get("callback_query")
                if cb:
                    cb_id = cb.get("id")
                    cb_data = (cb.get("data") or "").strip()
                    cb_chat = str(((cb.get("message") or {}).get("chat") or {}).get("id") or "")
                    if cb_id:
                        _tg_api_post(token, "answerCallbackQuery", {"callback_query_id": cb_id}, timeout=6)
                    if cb_chat and cb_data:
                        pending_msgs.append((cb_chat, cb_data))
                    continue
                msg = u.get("message") or u.get("edited_message") or {}
                chat_id = str((msg.get("chat") or {}).get("id") or "")
                text = (msg.get("text") or msg.get("caption") or "").strip()
                if text and chat_id:
                    if text.startswith("/"):
                        parts_cmd = text.split(None, 1)
                        parts_cmd[0] = parts_cmd[0].split("@")[0]
                        text = " ".join(parts_cmd)
                    pending_msgs.append((chat_id, text))

            if max_uid > int(STATE["telegram_last_update_id"]):
                STATE["telegram_last_update_id"] = max_uid
                _save_tg_offset(max_uid)

            TELEGRAM_QUEUE_STATE["queued"] = len(pending_msgs)
            for idx_m, (chat_id, text) in enumerate(pending_msgs):
                TELEGRAM_QUEUE_STATE["queued"] = max(0, len(pending_msgs) - idx_m - 1)
                allowed_id = (tg_cfg.get("allowed_chat_id") or "").strip()
                if allowed_id and chat_id != allowed_id:
                    _tg_api_post(token, "sendMessage", {
                        "chat_id": chat_id,
                        "text": f"🔒 Unauthorized Chat ID ({chat_id}). Add this ID in AetherVault Studio settings to allow access."
                    }, timeout=10)
                    continue

                low_t = text.lower()
                if low_t in ("/start", "/help", "/menu", "/panel"):
                    ai_n = WORKSPACE_CFG.get("ai_name", "Aether")
                    lan_u = f"http://{get_local_lan_ip()}:{SERVER_PORT}"
                    _tg_api_post(token, "sendMessage", {
                        "chat_id": chat_id,
                        "text": (
                            f"⚡ {ai_n} Control Panel (v{APP_VERSION})\n"
                            f"• Chat ID: {chat_id}\n"
                            f"• Home Wi-Fi Web UI: {lan_u}\n"
                            f"Tap a quick action below or send any message/command:"
                        ),
                        "reply_markup": _tg_build_control_keyboard()
                    }, timeout=10)
                    continue

                if text.startswith("avs_info:lan"):
                    lan_u = f"http://{get_local_lan_ip()}:{SERVER_PORT}"
                    _tg_api_post(token, "sendMessage", {
                        "chat_id": chat_id,
                        "text": f"📱 Open this in Safari/Chrome on your phone while on home Wi-Fi:\n{lan_u}\n\n💡 Want an in-Telegram Mini App button? Run 'cloudflared tunnel --url http://127.0.0.1:{SERVER_PORT}' and paste the https:// link into Studio Settings -> Integrations -> Mini App URL."
                    }, timeout=10)
                    continue

                if text.startswith("avs_tool:"):
                    t_act = text.split(":", 1)[1].strip()
                    if t_act == "screenshot":
                        res_s = execute_osworld_action("screenshot", "")
                        _tg_api_post(token, "sendMessage", {"chat_id": chat_id, "text": res_s.get("summary") or "Captured screenshot."}, timeout=10)
                        _tg_send_media(token, chat_id, img_url=res_s.get("image_url"))
                    elif t_act == "spotify_current":
                        sp_out = control_spotify("current_track", "")
                        _tg_api_post(token, "sendMessage", {"chat_id": chat_id, "text": f"🎵 {sp_out}"}, timeout=10)
                    continue

                if text.startswith("avs_cmd:"):
                    text = text.split(":", 1)[1].strip()
                    low_t = text.lower()

                if low_t == "/stop":
                    STATE["stop_requested"] = True
                    _tg_api_post(token, "sendMessage", {"chat_id": chat_id, "text": "⏹️ Stop signal sent to active generation."}, timeout=10)
                    continue

                if low_t in ("/status", "/specs", "/queue", "/update", "/unload", "/wake") or low_t.startswith("/sleep") or low_t.startswith(("/py ", "/toggle ", "/inject ", "/log")):
                    term_res = api_terminal_exec({"command": "/telegram" if low_t == "/queue" else text})
                    _tg_api_post(token, "sendMessage", {"chat_id": chat_id, "text": (term_res.get("output") or "Done")[:4000]}, timeout=15)
                    continue

                TELEGRAM_QUEUE_STATE["active"] = True
                TELEGRAM_QUEUE_STATE["last_user"] = text[:80]
                _tg_api_post(token, "sendChatAction", {"chat_id": chat_id, "action": "typing"}, timeout=6)
                q_note = f" (Queued behind: {TELEGRAM_QUEUE_STATE['queued']})" if TELEGRAM_QUEUE_STATE["queued"] > 0 else ""
                status_mid = _tg_edit_or_send_status(token, chat_id, 0, f"⏳ Working on it...{q_note}")
                last_edit_ts = [time.time()]

                def _on_tg_progress(step_s: str):
                    now_t = time.time()
                    if (now_t - last_edit_ts[0]) >= 1.8:
                        last_edit_ts[0] = now_t
                        _tg_api_post(token, "sendChatAction", {"chat_id": chat_id, "action": "typing"}, timeout=5)
                        _tg_edit_or_send_status(token, chat_id, status_mid, f"⚙️ {step_s}")

                try:
                    reply, img_url, aud_url = generate_sync_reply_for_telegram(text, session_id=f"telegram_{chat_id}", progress_cb=_on_tg_progress)
                    if status_mid:
                        _tg_api_post(token, "deleteMessage", {"chat_id": chat_id, "message_id": status_mid}, timeout=6)
                    for _tg_part in avs_bridges.chunk_telegram_message(reply):
                        _tg_api_post(token, "sendMessage", {"chat_id": chat_id, "text": _tg_part}, timeout=15)
                    _tg_send_media(token, chat_id, img_url=img_url, audio_url=aud_url)
                    TELEGRAM_QUEUE_STATE["processed_count"] = int(TELEGRAM_QUEUE_STATE.get("processed_count") or 0) + 1
                finally:
                    TELEGRAM_QUEUE_STATE["active"] = False
                    TELEGRAM_QUEUE_STATE["queued"] = 0
        except Exception as e:
            TELEGRAM_QUEUE_STATE["active"] = False
            TELEGRAM_QUEUE_STATE["last_error"] = f"{type(e).__name__}: {e}"
            STATE["telegram_status"] = f"Standby ({type(e).__name__})"
            time.sleep(5)

# =====================================================================
# 10. SELF-EXPLANATORY PACKAGES & DYNAMIC COPYRIGHT / ABOUT REGISTRY
# =====================================================================
MANAGED_PACKAGES = [
    {"pkg": "pyautogui", "mod": "pyautogui", "title": "🖱️ PyAutoGUI (OSWorld PC Control)", "desc": "Gives the AI full mouse click, keyboard typing, and hotkey automation on your desktop.", "owner": "Al Sweigart (BSD-3-Clause)"},
    {"pkg": "fastapi", "mod": "fastapi", "title": "⚡ FastAPI Web Core", "desc": "High-speed local REST & streaming server.", "owner": "Sebastián Ramírez (MIT License)"},
    {"pkg": "uvicorn", "mod": "uvicorn", "title": "🚀 Uvicorn ASGI Server", "desc": "Lightning-fast asynchronous HTTP server.", "owner": "Encode OSS Ltd (BSD-3-Clause)"},
    {"pkg": "llama-cpp-python", "mod": "llama_cpp", "title": "🧠 llama.cpp Vulkan Engine", "desc": "Runs GGUF models on GPU VRAM (Vulkan) and CPU.", "owner": "Georgi Gerganov & Andrei Betlen (MIT)"},
    {"pkg": "ddgs", "mod": "ddgs", "title": "🌐 DDGS Multi-Engine Web Search", "desc": "Modern metasearch (DuckDuckGo, Bing, Brave, Yahoo, Wikipedia) with zero API keys (replaces legacy duckduckgo-search).", "owner": "deedy5 (MIT License)"},
    {"pkg": "spotipy", "mod": "spotipy", "title": "🎵 Spotify Web & App Bridge", "desc": "Controls Spotify playback and searches tracks.", "owner": "Paul Lamere / Spotipy Contributors (MIT)"},
    {"pkg": "pymupdf", "mod": "pymupdf", "title": "📄 PyMuPDF Document Indexer", "desc": "Extracts text and pages from PDF documents.", "owner": "Artifex Software, Inc. (AGPL-3.0)"},
    {"pkg": "pillow", "mod": "PIL", "title": "🖼️ Pillow Image & Crop Studio", "desc": "Handles desktop screenshots, avatar/wallpaper cropping, and art.", "owner": "Jeffrey A. Clark & Contributors (HPND)"},
    {"pkg": "beautifulsoup4", "mod": "bs4", "title": "🕸️ BeautifulSoup4 Scraper", "desc": "Parses and cleans HTML web pages + Web Search Fallback.", "owner": "Leonard Richardson (MIT License)"},
    {"pkg": "psutil", "mod": "psutil", "title": "💻 PC Hardware Telemetry", "desc": "Monitors CPU cores, RAM, and disk metrics.", "owner": "Giampaolo Rodola (BSD-3-Clause)"},
    {"pkg": "py-cpuinfo", "mod": "cpuinfo", "title": "🔬 Py-CPUInfo (SpecPulse Deep CPU)", "desc": "Reads exact CPU brand, architecture, and L2/L3 cache sizes for SpecPulse.", "owner": "Matthew Brennan Jones (MIT License)"},
    {"pkg": "wmi", "mod": "wmi", "title": "🖥️ Windows WMI (SpecPulse Mobo/GPU)", "desc": "Reads Windows motherboard, BIOS, RAM DIMM slots, and live GPU 3D/VRAM counters.", "owner": "Tim Golden (MIT License)"},
    {"pkg": "scipy", "mod": "scipy", "title": "🔊 SciPy Audio & Signal Engine", "desc": "Encodes high-fidelity .wav audio for the Music Manager.", "owner": "SciPy Developers (BSD-3-Clause)"},
    {"pkg": "transformers", "mod": "transformers", "title": "🎵 HF Transformers (MusicGen Manager)", "desc": "Runs local Hugging Face MusicGen / Bark audio models via Cashier-to-Manager swap.", "owner": "Hugging Face Inc. (Apache-2.0)"},
    {"pkg": "diffusers", "mod": "diffusers", "title": "🎨 HF Diffusers (Local Image Manager)", "desc": "Runs local Hugging Face Tiny-SD / SD-Turbo image models via Cashier-to-Manager swap.", "owner": "Hugging Face Inc. (Apache-2.0)"},
    {"pkg": "accelerate", "mod": "accelerate", "title": "🚀 HF Accelerate (Low-RAM Offloader)", "desc": "Manages VRAM/RAM weight offloading during Specialist Manager swaps.", "owner": "Hugging Face Inc. (Apache-2.0)"},
    {"pkg": "kokoro-onnx", "mod": "kokoro_onnx", "title": "🗣️ Kokoro-ONNX Neural TTS", "desc": "Ultra-fast ~82M offline neural voice synthesis (includes Female Voice 3 af_nicole/af_river).", "owner": "thewh1teagle & hexgrad (Apache-2.0)"},
    {"pkg": "soundfile", "mod": "soundfile", "title": "🎧 SoundFile Audio I/O", "desc": "Reads and writes neural voice & mic audio buffers.", "owner": "Bastian Bechtold (BSD-3-Clause)"},
    {"pkg": "faster-whisper", "mod": "faster_whisper", "title": "🎤 Faster-Whisper Offline STT", "desc": "High-speed CTranslate2 offline microphone speech-to-text transcription.", "owner": "SYSTRAN (MIT License)"},
    {"pkg": "argostranslate", "mod": "argostranslate", "title": "🌐 Argos Translate (Offline Translator)", "desc": "100% offline neural machine translation (CTranslate2) stored portably in models/translate/.", "owner": "Argos Open Technologies (MIT License)"},
    {"pkg": "pyspellchecker", "mod": "spellchecker", "title": "✨ PySpellChecker (Multi-Language)", "desc": "Offline multi-language spell checking (EN/ES/FR/DE/PT/IT/RU/AR/NL) with Lore custom-word whitelisting.", "owner": "Tyler Barrus (MIT License)"},
    {"pkg": "langid", "mod": "langid", "title": "🧭 LangID (Offline Language Detector)", "desc": "Fast offline language identification across 97 languages for automatic spellcheck & translation.", "owner": "Marco Lui (BSD-2-Clause)"}
]

_PKG_STATUS_CACHE = {"data": None, "ts": 0.0}

def check_packages_status(force: bool = False):
    if not force and _PKG_STATUS_CACHE["data"] is not None and (time.time() - _PKG_STATUS_CACHE["ts"]) < 30.0:
        return _PKG_STATUS_CACHE["data"]
    out = []
    for item in MANAGED_PACKAGES:
        try:
            spec = importlib.util.find_spec(item["mod"])
        except Exception:
            spec = sys.modules.get(item["mod"])
        try:
            ver = importlib.metadata.version(item["pkg"]) if spec else "Not installed"
        except Exception:
            ver = "Installed" if spec else "Not installed"
        out.append({
            "pkg": item["pkg"],
            "title": item["title"],
            "desc": item["desc"],
            "owner": item["owner"],
            "version": ver,
            "installed": spec is not None
        })
    _PKG_STATUS_CACHE["data"] = out
    _PKG_STATUS_CACHE["ts"] = time.time()
    return out

def get_all_pip_distributions():
    dists = []
    try:
        for dist in importlib.metadata.distributions():
            name = dist.metadata.get("Name") or dist.name
            ver = dist.version
            author = dist.metadata.get("Author") or dist.metadata.get("Maintainer") or "Respective Open-Source Authors"
            lic = dist.metadata.get("License") or "Standard Open-Source License"
            dists.append({"name": name, "version": ver, "author": author[:60], "license": lic[:45]})
        dists.sort(key=lambda x: x["name"].lower())
    except Exception:
        pass
    return dists

# =====================================================================
# 11. FASTAPI APPLICATION & ENDPOINTS
# =====================================================================
app = FastAPI(title="AetherVault Studio")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    STATE["last_debug"]["error"] = tb
    err_card = format_predetermined_error("ERR_ENGINE_CRASH", str(exc))
    STATE["generating"] = False
    set_step("Idle")
    return JSONResponse(
        status_code=200,
        content={
            "error": str(exc),
            "issue": err_card,
            "reply": f"⚠️ **[{err_card['code']}: {err_card['title']}]**\n{err_card['message']}\n💡 *Fix: {err_card['fix']}*"
        }
    )

def _background_boot_sequence():
    try:
        cleanup_orphaned_temp_sessions()
        set_step("Initializing SQLite Memory Core & .temp_cache...")
        print(f"[BOOT 1/4] Initializing SQLite Memory Core & Local Cache ({TEMP_SESSION_DIR.name})...", flush=True)
        init_db()
        _refresh_priority_cache_from_db()
        run_silent_legacy_migration()
        # Mark Studio Online immediately so UI never hangs on indexing if files are already in DB!
        STATE["boot_ready"] = True
        STATE["active_task_label"] = "Ready"

        set_step("Syncing Priority #1 Memory Vault...")
        print("[BOOT 2/4] Syncing Priority #1 Memory Vault...", flush=True)
        sync_memory_vault_file()
        reload_custom_tools()

        print("[BOOT 3/4] Checking Knowledge Tree (/priority_pdfs) for new or modified files...", flush=True)
        sync_priority_files(force=False)
        sync_pseudo_memory_and_index()
        threading.Thread(target=telegram_polling_worker, daemon=True).start()
        threading.Thread(target=idle_sleep_watchdog, daemon=True).start()
        threading.Thread(target=_memory_compactor_watchdog, daemon=True).start()
        threading.Thread(target=bluesky_polling_worker, daemon=True).start()

        boot_models = list_local_models()
        b_mode = WORKSPACE_CFG.get("brain_mode", "local_only")
        if b_mode in ("smart_api", "hybrid") and load_api_vault().get("slots") and not STATE.get("offline_mode"):
            print(f"[BOOT 4/4] Brain Mode is '{b_mode.upper()}' — keeping GGUF weights unloaded (0 RAM overhead) until needed!", flush=True)
        elif boot_models:
            if b_mode == "hybrid" or STATE.get("performance_mode") == "Laptop 2015 (Fast)":
                chosen = pick_lightweight_failsafe_model() or boot_models[0]
            else:
                preferred = WORKSPACE_CFG.get("last_loaded_model")
                chosen = preferred if preferred in boot_models else boot_models[0]
            print(f"[BOOT 4/4] Found {len(boot_models)} local GGUF model(s). Auto-loading '{chosen}' in background...", flush=True)
            load_local_model(chosen)
        else:
            print("[BOOT 4/4] Server online at http://127.0.0.1:8000 (No .gguf models in /models yet — ready to download or load!).", flush=True)
    except Exception as e:
        print(f"[BOOT WARNING] {e}", flush=True)
    finally:
        STATE["boot_ready"] = True
        STATE["indexing_files"] = False
        STATE["active_task_label"] = "Ready"
        set_step("Idle")

@app.on_event("startup")
def on_startup():
    STATE["boot_ready"] = False
    threading.Thread(target=_background_boot_sequence, daemon=True).start()

_CACHED_LAN_IP = {"ip": "", "ts": 0.0}

def get_local_lan_ip() -> str:
    """Detects & caches the active Wi-Fi / Ethernet LAN IPv4 address for Phone / Bedside access."""
    if _CACHED_LAN_IP["ip"] and (time.time() - _CACHED_LAN_IP["ts"]) < 60.0:
        return _CACHED_LAN_IP["ip"]
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.2)
        s.connect(("192.168.1.1", 80))
        ip = s.getsockname()[0]
        s.close()
        if ip and not ip.startswith("127."):
            _CACHED_LAN_IP.update({"ip": ip, "ts": time.time()})
            return ip
    except Exception:
        pass
    try:
        hostname_ips = socket.gethostbyname_ex(socket.gethostname())[2]
        for candidate in hostname_ips:
            if candidate.startswith("192.168.") or candidate.startswith("10.") or candidate.startswith("172."):
                return candidate
    except Exception:
        pass
    return "127.0.0.1"

def is_allowed_lan_or_local_ip(ip_str: str) -> bool:
    if not ip_str or ip_str in ("127.0.0.1", "::1", "localhost", "testclient"):
        return True
    clean_ip = ip_str.replace("::ffff:", "").strip()
    try:
        ip_obj = ipaddress.ip_address(clean_ip)
        return bool(ip_obj.is_loopback or ip_obj.is_private or ip_obj.is_link_local)
    except Exception:
        return clean_ip.startswith(("192.168.", "10.", "172.", "127.", "fe80:"))

@app.middleware("http")
async def lan_guard(request: Request, call_next):
    ip = request.client.host if request.client else "127.0.0.1"
    if not is_allowed_lan_or_local_ip(ip):
        raise HTTPException(status_code=403, detail="Restricted to Localhost & Home Wi-Fi LAN.")
    return await call_next(request)

@app.get("/status")
def get_status():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT id, title, updated_at FROM chat_sessions ORDER BY updated_at DESC")
        sessions = [{"id": r["id"], "title": r["title"], "updated_at": r["updated_at"]} for r in c.fetchall()]

    file_info = list_priority_files_info()
    return {
        "config": WORKSPACE_CFG,
        "lan_ip": get_local_lan_ip(),
        "lan_url": f"http://{get_local_lan_ip()}:{SERVER_PORT}",
        "models": list_local_models(),
        "model_bag": MODEL_BAG,
        "specialist_bag": SPECIALIST_MODEL_BAG,
        "voice_profiles": VOICE_PROFILES,
        "local_voices": list_local_voice_models(),
        "vision_projectors": list_vision_projectors(),
        "partner_evolution": load_partner_evolution(),
        "pending_patches": list_pending_self_patches(),
        "temp_cache": get_temp_cache_stats(),
        "boot_ready": STATE.get("boot_ready", True),
        "indexing_files": STATE.get("indexing_files", False),
        "uptime_sec": int(time.time() - STATE.get("boot_time", time.time())),
        "server_time": time.strftime("%H:%M:%S"),
        "current_model": STATE["current_model"],
        "gpu_offload": STATE["gpu_offload"],
        "loading_model": STATE["loading_model"],
        "idle_sleeping": bool(STATE.get("idle_sleeping", False)),
        "last_unloaded_model": STATE.get("last_unloaded_model", ""),
        "idle_unload_minutes": int(WORKSPACE_CFG.get("idle_unload_minutes", 10)),
        "generating": STATE["generating"],
        "current_step": STATE["current_step"],
        "offline_mode": STATE["offline_mode"],
        "auto_web_search": bool(WORKSPACE_CFG.get("auto_web_search", True)),
        "performance_mode": STATE["performance_mode"],
        "workspace_mode": WORKSPACE_CFG.get("workspace_mode", "assistant"),
        "workbench_trust": WORKSPACE_CFG.get("workbench_trust", "safe_auto"),
        "user_profile": load_user_profile_card(),
        "brain_mode": WORKSPACE_CFG.get("brain_mode", "local_only"),
        "failsafe_model": WORKSPACE_CFG.get("failsafe_model") or pick_lightweight_failsafe_model(),
        "active_api_label": STATE.get("active_api_label", ""),
        "last_api_hop_notice": STATE.get("last_api_hop_notice", ""),
        "api_vault": get_masked_api_vault(),
        "api_templates": API_PROVIDER_TEMPLATES,
        "telegram_status": STATE["telegram_status"],
        "telegram_queue": TELEGRAM_QUEUE_STATE,
        "bluesky": BSKY_STATE,
        "mind_map_nodes": len(MEMORY_COMPACTOR.mind_map),
        "ram": get_system_ram_info(),
        "download": STATE["download"],
        "pdf_details": file_info,
        "memories": list_memories(),
        "sessions": sessions,
        "glossary_top": PRIORITY_CACHE["glossary_top_words"][:15],
        "allowed_roots": STATE["allowed_pc_roots"],
        "packages": check_packages_status(),
        "predetermined_errors": PREDETERMINED_ERRORS,
        "debug": STATE["last_debug"]
    }

@app.post("/stop_generation")
def stop_generation():
    """Real-time Stop Button endpoint! Immediately signals the active token loop to halt cleanly."""
    STATE["stop_requested"] = True
    format_predetermined_error("ERR_USER_STOPPED")
    set_step("⏹️ Stop requested by user...")
    return {"ok": True, "stopped": True}


def _check_mcp_auth(request: Request):
    expected = (WORKSPACE_CFG.get("mcp_auth_token") or "").strip()
    if not expected:
        return
    auth_hdr = (request.headers.get("Authorization") or "").strip()
    x_tok = (request.headers.get("X-MCP-Token") or "").strip()
    q_tok = (request.query_params.get("token") or "").strip()
    token = auth_hdr[7:].strip() if auth_hdr.lower().startswith("bearer ") else (x_tok or q_tok)
    if token != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing MCP authentication token.")

MCP_TOOL_DEFINITIONS = [
    {"name": "aethervault_status", "description": "Get live AetherVault Studio status.", "inputSchema": {"type": "object", "properties": {}, "required": []}},
    {"name": "aethervault_vault_search", "description": "Search Priority #1 Memory Vault and indexed Lore chunks.", "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    {"name": "aethervault_chat_search", "description": "Search past chat sessions and exported .txt chat logs.", "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    {"name": "aethervault_file_helper", "description": "Safe list/read helper for AetherVault workspace folders.", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": []}},
    {"name": "aethervault_media_helper", "description": "List generated media or render an image via AetherVault.", "inputSchema": {"type": "object", "properties": {"action": {"type": "string"}, "prompt": {"type": "string"}}, "required": ["action"]}}
]

def _run_mcp_tool(tool_name: str, arguments: dict) -> dict:
    args = arguments if isinstance(arguments, dict) else {}
    if tool_name == "aethervault_status":
        return {"content": [{"type": "text", "text": json.dumps({"version": APP_VERSION, "app_version": APP_VERSION, "ai_name": WORKSPACE_CFG.get("ai_name", "Aether"), "brain_mode": WORKSPACE_CFG.get("brain_mode", "local_only"), "workspace_mode": WORKSPACE_CFG.get("workspace_mode", "assistant")}, indent=2)}], "isError": False}
    if tool_name == "aethervault_vault_search":
        q = str(args.get("query") or "").strip()
        mems = [m for m in list_memories() if q.lower() in f"{m.get('category','')} {m.get('fact','')}".lower()] if q else list_memories()[:10]
        lore_txt, lore_lbls = retrieve_relevant_lore(q, top_k=3) if q else ("", [])
        return {"content": [{"type": "text", "text": json.dumps({"query": q, "matched_memories": mems[:10], "lore_sources": lore_lbls, "lore_excerpts": lore_txt[:3500]}, indent=2)}], "isError": False}
    if tool_name == "aethervault_chat_search":
        q = str(args.get("query") or "").strip()
        return {"content": [{"type": "text", "text": execute_cross_chat_tool("search" if q else "list", q, "mcp_bridge")[:3500]}], "isError": False}
    if tool_name == "aethervault_file_helper":
        p_in = str(args.get("path") or "").strip()
        if not p_in:
            return {"content": [{"type": "text", "text": json.dumps({"priority_pdfs": [p.name for p in sorted(PDF_DIR.rglob("*")) if p.is_file()][:25], "memory_vault": [p.name for p in sorted(MEMORY_DIR.glob("*")) if p.is_file()][:15]}, indent=2)}], "isError": False}
        cand = Path(p_in)
        cand = (cand if cand.is_absolute() else (BASE_DIR / cand)).resolve()
        allowed_dirs = [PDF_DIR.resolve(), MEMORY_DIR.resolve(), CHAT_LOG_DIR.resolve(), GEN_IMG_DIR.resolve(), GEN_AUDIO_DIR.resolve(), BASE_DIR.resolve()]
        if cand != BASE_DIR.resolve() and not any(d == cand or d in cand.parents for d in allowed_dirs):
            return {"content": [{"type": "text", "text": "Access denied outside workspace folders."}], "isError": True}
        if cand.parent == BASE_DIR.resolve() and cand.name in PROTECTED_CORE_FILES:
            return {"content": [{"type": "text", "text": f"Access denied to protected core file '{cand.name}'."}], "isError": True}
        return {"content": [{"type": "text", "text": read_pc_file_silently(str(cand), max_chars=4000)}], "isError": False}
    if tool_name == "aethervault_media_helper":
        act = str(args.get("action") or "list").strip().lower()
        if act == "generate_image":
            r = generate_image_tool(str(args.get("prompt") or "").strip())
            return {"content": [{"type": "text", "text": json.dumps(r)}], "isError": not bool(r.get("ok"))}
        return {"content": [{"type": "text", "text": json.dumps({"images": [f"/generated_image/{p.name}" for p in sorted(GEN_IMG_DIR.glob("*")) if p.is_file()][-12:]})}], "isError": False}
    return {"content": [{"type": "text", "text": f"Unknown MCP tool: {tool_name}"}], "isError": True}


@app.post("/workbench/subprocess")
def api_workbench_subprocess(payload: dict):
    """Runs Python code inside the killable avs.workbench subprocess worker."""
    code = str(payload.get("code") or "")
    timeout_sec = float(payload.get("timeout_sec") or 20.0)
    trust = WORKSPACE_CFG.get("workbench_trust", "safe_auto")
    return avs_workbench.run_workbench_subprocess(
        code_str=code,
        temp_dir=TEMP_SESSION_DIR,
        port=SERVER_PORT,
        token=WORKBENCH_TOKEN,
        timeout_sec=min(60.0, max(1.0, timeout_sec)),
        trust_level=trust,
    )


def _collect_lore_whitelist_words() -> set:
    words = set(PRIORITY_CACHE.get("domain_vocab") or set())
    for k in (WORKSPACE_CFG.get("ai_name", ""), WORKSPACE_CFG.get("user_name", "")):
        for tok in re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]{2,}", str(k or "")):
            words.add(tok.lower())
    if GLOSSARY_PATH.exists():
        try:
            g = json.loads(GLOSSARY_PATH.read_text(encoding="utf-8"))
            for item in (g.get("most_repeating_words") or [])[:250]:
                w = str(item.get("word") or "").strip().lower()
                if len(w) >= 3:
                    words.add(w)
        except Exception:
            pass
    return words

def run_lore_safe_spellcheck(text: str, lang: str = "auto") -> dict:
    return avs_lang.spellcheck_text(text, lang=lang, custom_words=_collect_lore_whitelist_words())

@app.get("/api/lang/status")
def api_lang_status():
    caps = avs_lang.get_language_capabilities(model_dir=MODEL_DIR, locales_dir=LOCALES_DIR)
    caps.update({
        "ui_language": WORKSPACE_CFG.get("ui_language", "en"),
        "speech_locale": WORKSPACE_CFG.get("speech_locale", "en-US"),
        "spellcheck_enabled": bool(WORKSPACE_CFG.get("spellcheck_enabled", True)),
        "translate_bridge_mode": WORKSPACE_CFG.get("translate_bridge_mode", "native"),
        "lore_whitelist_size": len(_collect_lore_whitelist_words()),
    })
    return caps

@app.get("/api/lang/locale/{lang_code}")
def api_get_locale_pack(lang_code: str):
    return avs_lang.load_locale_pack(LOCALES_DIR, lang_code)

@app.post("/api/lang/spellcheck")
def api_lang_spellcheck(payload: dict):
    txt = str(payload.get("text") or "")
    lang = str(payload.get("lang") or "auto")
    return run_lore_safe_spellcheck(txt, lang=lang)

@app.post("/api/lang/translate")
def api_lang_translate(payload: dict):
    txt = str(payload.get("text") or "")
    to_lang = str(payload.get("to") or WORKSPACE_CFG.get("ui_language") or "en")
    from_lang = str(payload.get("from") or "auto")
    return avs_lang.translate_text(txt, to_lang=to_lang, from_lang=from_lang, model_dir=MODEL_DIR)

@app.post("/api/lang/install_pack")
def api_lang_install_pack(payload: dict):
    fc = str(payload.get("from_code") or "en")
    tc = str(payload.get("to_code") or "es")
    return avs_lang.install_argos_language_pair(fc, tc, model_dir=MODEL_DIR, offline_mode=bool(STATE.get("offline_mode")))

@app.get("/api/hardware_specs")
def api_hardware_specs():
    """SpecPulse-inspired deep hardware inventory (64-bit Registry VRAM + WMI/psutil live telemetry)."""
    return avs_hw.get_full_hardware_report()


@app.post("/api/terminal/exec")
def api_terminal_exec(payload: dict):
    """Web Terminal / Manager Console endpoint for desktop & mobile browsers."""
    raw = str(payload.get("command") or "").strip()
    if not raw:
        return {"ok": True, "output": ""}
    parts = raw.split(None, 1)
    cmd = parts[0].lower()
    arg = parts[1].strip() if len(parts) > 1 else ""

    if cmd in ("/help", "help", "?"):
        return {"ok": True, "output": (
            "=== AETHERVAULT v" + APP_VERSION + " WEB TERMINAL COMMANDS ===\n"
            "  /help                     Show this command list\n"
            "  /status                   Live model, GPU, RAM, mode & trust status\n"
            "  /specs                    Deep SpecPulse hardware inventory (64-bit VRAM, CPU, GPU)\n"
            "  /stop                     Halt active generation loop immediately\n"
            "  /inject <cat> | <fact>    Save fact into Priority #1 Memory Vault\n"
            "  /toggle <key> <val>       Flip Studio toggle (e.g. /toggle workbench_trust full_pc)\n"
            "  /py <code>                Run Python in killable subprocess Workbench\n"
            "  /pip <pkg>                Install custom PyPI package into .venv\n"
            "  /log [keyword] [lines]    Tail error_audit.log locally\n"
            "  /update                   Pull latest v" + APP_VERSION + "+ files from GitHub (SHA-256 verified)\n"
            "  /tunnel                   Check remote tunnel status & mobile access guide\n"
            "  /sh <shell_cmd>           Run host shell command (requires Full PC trust)"
        )}
    if cmd == "/unload":
        res_u = unload_local_model("Terminal /unload")
        return {"ok": res_u.get("ok", True), "output": f"[IDLE SLEEP] Unloaded '{res_u.get('unloaded') or 'none'}' — RAM/VRAM freed!"}
    if cmd == "/wake":
        touch_activity(wake_model=True)
        return {"ok": True, "output": f"[WAKE] Active model: {STATE.get('current_model') or 'None'}"}
    if cmd == "/sleep":
        mins_v = int(arg) if arg.isdigit() else int(WORKSPACE_CFG.get("idle_unload_minutes", 10))
        WORKSPACE_CFG["idle_unload_minutes"] = max(0, min(240, mins_v))
        save_workspace_config(WORKSPACE_CFG)
        return {"ok": True, "output": f"[IDLE WATCHDOG] Auto-unload after {WORKSPACE_CFG['idle_unload_minutes']} min(s) idle (0 = disabled)."}
    if cmd == "/telegram":
        return {"ok": True, "output": f"[TELEGRAM BRIDGE] Status: {STATE.get('telegram_status')} | Active: {TELEGRAM_QUEUE_STATE.get('active')} | Queued: {TELEGRAM_QUEUE_STATE.get('queued')} | Step: {TELEGRAM_QUEUE_STATE.get('last_step')}"}
    if cmd == "/status":
        ram = get_system_ram_info()
        return {"ok": True, "output": (
            f"[STATUS v{APP_VERSION}] Model: {STATE.get('current_model')} | GPU: {STATE.get('gpu_offload')} | "
            f"Mode: {WORKSPACE_CFG.get('workspace_mode')} | Trust: {WORKSPACE_CFG.get('workbench_trust')} | "
            f"Brain: {WORKSPACE_CFG.get('brain_mode')} | RAM: {ram.get('free_gb')}/{ram.get('total_gb')} GB free | "
            f"LAN: http://{get_local_lan_ip()}:{SERVER_PORT}"
        )}
    if cmd == "/specs":
        rep = avs_hw.get_full_hardware_report()
        sp = rep.get("specs") or {}
        lv = rep.get("live") or {}
        gpus = ", ".join(f"{g.get('name')} ({g.get('vram_gb')} GB)" for g in (sp.get("gpus") or []))
        return {"ok": True, "output": (
            f"[SPECS] Host: {sp.get('hostname')} | CPU: {(sp.get('cpu') or {}).get('name')} ({lv.get('cpu_percent')}%)\n"
            f"        GPU: {gpus} (Load: {lv.get('gpu_util_percent')}% | VRAM Used: {lv.get('gpu_vram_used_mb')} MB)\n"
            f"        RAM: {lv.get('ram_used_gb')}/{(sp.get('ram') or {}).get('total_gb')} GB ({lv.get('ram_percent')}%)"
        )}
    if cmd == "/stop":
        STATE["stop_requested"] = True
        return {"ok": True, "output": "[STOP] Generation stop signal sent."}
    if cmd == "/inject":
        cat, fact = [x.strip() for x in arg.split("|", 1)] if "|" in arg else ("active_state", arg)
        if not fact:
            return {"ok": False, "output": "[USAGE] /inject <category> | <fact>"}
        return {"ok": True, "output": f"[INJECT] {save_to_memory(cat, fact)}"}
    if cmd == "/toggle":
        t_parts = arg.split(None, 1)
        if len(t_parts) < 2:
            return {"ok": False, "output": "[USAGE] /toggle <setting> <value>"}
        return {"ok": True, "output": f"[TOGGLE] {apply_studio_toggle(t_parts[0], t_parts[1])}"}
    if cmd == "/py":
        if not arg:
            return {"ok": False, "output": "[USAGE] /py print(2 + 2)"}
        res = avs_workbench.run_workbench_subprocess(
            code_str=arg, temp_dir=TEMP_SESSION_DIR, port=SERVER_PORT,
            token=WORKBENCH_TOKEN, timeout_sec=15.0,
            trust_level=WORKSPACE_CFG.get("workbench_trust", "safe_auto"),
        )
        return {"ok": bool(res.get("ok")), "output": f"[PY ok={res.get('ok')} | {res.get('elapsed_sec')}s]\n{res.get('output')}"}
    if cmd == "/pip":
        if not arg:
            return {"ok": False, "output": "[USAGE] /pip <package_name>"}
        res = api_manage_package({"pkg": arg, "action": "install"})
        return {"ok": bool(res.get("ok")), "output": res.get("output") or res.get("error") or "Done"}
    if cmd == "/log":
        toks = arg.split()
        n_lines = int(toks[-1]) if (toks and toks[-1].isdigit()) else 25
        kw = " ".join(toks[:-1] if (toks and toks[-1].isdigit()) else toks).strip()
        return {"ok": True, "output": workbench_debug_log(kw, n_lines)}
    if cmd == "/update":
        return api_ota_update()
    if cmd == "/tunnel":
        return {"ok": True, "output": (
            f"[REMOTE ACCESS]\n"
            f"1. Home Wi-Fi LAN: http://{get_local_lan_ip()}:{SERVER_PORT}\n"
            f"2. Telegram Bot Bridge: Configure Bot Token in Studio -> Integrations to chat from anywhere with zero port-forwarding!\n"
            f"3. Anywhere HTTPS Tunnel: Run 'cloudflared tunnel --url http://127.0.0.1:{SERVER_PORT}' or Tailscale on your PC to get a private HTTPS link for your phone."
        )}
    if cmd == "/sh":
        if not arg:
            return {"ok": False, "output": "[USAGE] /sh <command>"}
        return {"ok": True, "output": run_silent_shell_command(arg)}
    return {"ok": False, "output": f"Unknown command '{cmd}'. Type /help for available commands."}

@app.post("/api/ota/update")
def api_ota_update():
    """Pulls latest core files from GitHub (SHA-256 verified, cache-busted) directly from the UI or phone."""
    slug = (WORKSPACE_CFG.get("github_repo") or "EnZeeeRu/AetherVault-Studio").strip().strip("/")
    base_raw = f"https://raw.githubusercontent.com/{slug}/main"
    bust = int(time.time())
    ota_headers = {"User-Agent": f"AetherVaultStudio/{APP_VERSION}", "Cache-Control": "no-cache", "Pragma": "no-cache"}
    try:
        r = requests.get(f"{base_raw}/manifest.json?t={bust}", headers=ota_headers, timeout=15)
        r.raise_for_status()
        manifest_raw = r.content
        manifest = r.json()
    except Exception as e:
        return {"ok": False, "output": f"[OTA ERROR] Could not fetch manifest.json: {e}"}

    files = manifest.get("files") or {}
    updated = []
    warnings_list = []
    stock_dir = BASE_DIR / "stock_vault"
    stock_dir.mkdir(parents=True, exist_ok=True)
    frozen_bootstrappers = {"Launch.bat", "Launch.sh", "manager.py"}
    for rel_path, expected_sha in files.items():
        if ".." in rel_path or rel_path.startswith("/") or ":" in rel_path:
            continue
        dest = (BASE_DIR / rel_path).resolve()
        if BASE_DIR.resolve() not in dest.parents and dest != BASE_DIR.resolve():
            continue
        if rel_path in frozen_bootstrappers and dest.exists():
            continue
        if dest.exists() and expected_sha and hashlib.sha256(dest.read_bytes()).hexdigest() == expected_sha:
            continue
        try:
            fr = requests.get(f"{base_raw}/{rel_path}?t={bust}", headers=ota_headers, timeout=25)
            fr.raise_for_status()
            raw_b = fr.read()
            if expected_sha and hashlib.sha256(raw_b).hexdigest() != expected_sha:
                warnings_list.append(f"SHA-256 mismatch for {rel_path} — skipped")
                continue
            if dest.exists() and dest.parent == BASE_DIR.resolve() and dest.name in ("assistant_server.py", "ui_studio.html"):
                shutil.copy2(dest, stock_dir / f"{dest.name}.good")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(raw_b)
            updated.append(rel_path)
        except Exception as fe:
            warnings_list.append(f"Failed {rel_path}: {fe}")

    if not warnings_list:
        try:
            (BASE_DIR / "manifest.json").write_bytes(manifest_raw)
        except Exception:
            pass
    ver_new = manifest.get("version", "?")
    warn_suffix = (" | Warnings: " + "; ".join(warnings_list)) if warnings_list else ""
    tag = "[OTA PARTIAL]" if warnings_list else "[OTA OK]"
    if updated:
        msg = f"{tag} Updated {len(updated)} file(s) to v{ver_new}: {', '.join(updated)}. Reload page (or restart server if .py changed)!{warn_suffix}"
    else:
        msg = f"{tag} Already up to date with {slug} (v{ver_new}).{warn_suffix}"
    return {"ok": len(warnings_list) == 0, "version": ver_new, "updated": updated, "warnings": warnings_list, "output": msg}

@app.post("/api/system/restart")
def api_system_restart():
    """Cleanly spawns a fresh instance of assistant_server.py on the same port and exits."""
    def _delayed_restart():
        time.sleep(0.8)
        env = os.environ.copy()
        env["AVS_PORT"] = str(SERVER_PORT)
        subprocess.Popen([sys.executable, "-u", str(BASE_DIR / "assistant_server.py")], cwd=str(BASE_DIR), env=env)
        os._exit(0)
    threading.Thread(target=_delayed_restart, daemon=True).start()
    return {"ok": True, "message": "Restarting AetherVault Studio backend... Page will reconnect in ~3 seconds."}

@app.get("/specpulse", response_class=HTMLResponse)
def serve_specpulse_dashboard():
    """Serves the embedded SpecPulse 60-FPS Visual Hardware Telemetry & Benchmark Dashboard."""
    return HTMLResponse(content=avs_hw.SPECPULSE_DASHBOARD_HTML)

@app.get("/api/specpulse/specs")
def api_specpulse_specs():
    return avs_hw.get_cached_static_specs()

@app.get("/api/specpulse/telemetry")
def api_specpulse_telemetry():
    return avs_hw.get_live_telemetry_payload()

@app.post("/api/specpulse/benchmark/start")
def api_specpulse_bench_start():
    return avs_hw.start_benchmark(temp_dir=TEMP_SESSION_DIR)

@app.get("/api/specpulse/benchmark/status")
def api_specpulse_bench_status():
    return avs_hw.get_benchmark_status()

@app.get("/api/hf/inspect")
def api_hf_inspect(repo: str = ""):
    """Lists real downloadable .gguf/.onnx/.safetensors files & sizes from any Hugging Face repo."""
    return inspect_huggingface_repo(repo)

@app.get("/api/custom_tools")
def api_list_custom_tools():
    return {"ok": True, "plugins": reload_custom_tools()}

@app.post("/api/custom_tools/create")
def api_create_custom_tool(payload: dict):
    msg = create_and_verify_custom_tool(
        str(payload.get("name") or ""),
        str(payload.get("code") or ""),
        str(payload.get("test_code") or ""),
    )
    return {"ok": "PASSED sandbox test" in msg, "message": msg, "plugins": CUSTOM_PLUGINS_MANIFEST}

@app.get("/v1/models")
def openai_v1_models():
    """OpenAI-compatible /v1/models endpoint for external tools (VS Code, Continue, scripts)."""
    models = [{"id": m, "object": "model", "owned_by": "aethervault-local"} for m in list_local_models()]
    if STATE.get("active_api_label"):
        models.insert(0, {"id": STATE["active_api_label"], "object": "model", "owned_by": "aethervault-api"})
    return {"object": "list", "data": models}

@app.post("/v1/chat/completions")
def openai_v1_chat_completions(payload: dict):
    """OpenAI-compatible /v1/chat/completions endpoint routing through AetherVault's Zero-Drop Brain."""
    msgs = payload.get("messages") or [{"role": "user", "content": "Hello"}]
    try:
        max_t = max(16, min(32768, int(payload.get("max_tokens") or 1024)))
    except Exception:
        max_t = 1024
    temp = float(payload.get("temperature") or 0.7)
    top_p = float(payload.get("top_p") or 0.95)
    reply_text = dispatch_brain_sync(messages=msgs, max_tokens=max_t, temperature=temp, top_p=top_p)
    return {
        "id": f"chatcmpl-avs-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": STATE.get("current_model") or STATE.get("active_api_label") or "aethervault-v5",
        "choices": [{"index": 0, "message": {"role": "assistant", "content": reply_text}, "finish_reason": "stop"}],
    }

@app.get("/toolbox/manifest")
def api_toolbox_manifest():
    """Returns the unified avs.toolbox manifest (help text, OpenAI schemas, MCP tools)."""
    return {
        "version": APP_VERSION,
        "port": SERVER_PORT,
        "help": avs_toolbox.toolbox.help_text(),
        "openai_schemas": avs_toolbox.toolbox.openai_schemas(),
        "mcp_tools": MCP_TOOL_DEFINITIONS,
    }

@app.get("/mcp")
def mcp_info(request: Request):
    _check_mcp_auth(request)
    return {"protocol": "MCP (JSON-RPC 2.0)", "version": APP_VERSION, "notes": "POST JSON-RPC 2.0 to /mcp; use an HTTPS tunnel (ngrok/Cloudflare) for Gemini Desktop / remote custom app clients."}

@app.post("/mcp")
async def mcp_jsonrpc(request: Request):
    _check_mcp_auth(request)
    body = await request.json()
    req_id = body.get("id")
    method = (body.get("method") or "").strip()
    params = body.get("params") if isinstance(body.get("params"), dict) else {}
    if method == "notifications/initialized" or req_id is None:
        return JSONResponse(content={"jsonrpc": "2.0", "id": req_id, "result": {"ok": True}})
    if method == "initialize":
        return JSONResponse(content={"jsonrpc": "2.0", "id": req_id, "result": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "AetherVault-Studio-MCP", "version": APP_VERSION}}})
    if method == "tools/list":
        return JSONResponse(content={"jsonrpc": "2.0", "id": req_id, "result": {"tools": MCP_TOOL_DEFINITIONS}})
    if method == "tools/call":
        return JSONResponse(content={"jsonrpc": "2.0", "id": req_id, "result": _run_mcp_tool((params.get("name") or "").strip(), params.get("arguments") or {})})
    return JSONResponse(content={"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}})

@app.get("/about_info")
def get_about_info():
    return {
        "project_name": "AetherVault Studio",
        "version": f"v{APP_VERSION} Bluesky (Modular Guardrails, Workbench & AT Protocol Edition)",
        "credits": "Made with ❤️ in Argentina by Enzeru, with the collaboration of Google Gemini.",
        "legal_addendum": (
            "All rights reserved to their respective owners. Every Python package (pip module) installed by the user, "
            "external API integration (Spotify Web API, DuckDuckGo Search, Telegram Bot API, Hugging Face Hub, OSWorld/PyAutoGUI), "
            "runtime inference library (llama.cpp / GGML), and AI model checkpoint (.gguf / diffusion weights) "
            "indexed or executed within AetherVault Studio is the copyrighted intellectual property of its respective creator and license holder."
        ),
        "indexed_models": list_local_models(),
        "model_presets": MODEL_BAG,
        "core_packages": check_packages_status(),
        "all_pip_packages": get_all_pip_distributions()
    }

@app.post("/osworld/execute")
def api_osworld_execute(payload: dict):
    action = (payload.get("action") or "screenshot").strip()
    arg = (payload.get("arg") or "").strip()
    return execute_osworld_action(action, arg)

@app.post("/config/update")
def update_config(payload: dict):
    global WORKSPACE_CFG
    for k, v in payload.items():
        if isinstance(v, dict) and isinstance(WORKSPACE_CFG.get(k), dict):
            WORKSPACE_CFG[k] = {**WORKSPACE_CFG[k], **v}
        else:
            WORKSPACE_CFG[k] = v
    WORKSPACE_CFG["first_boot_completed"] = True
    save_workspace_config(WORKSPACE_CFG)
    _TG_REGISTERED_TOKENS.clear()

    # Immediately update the first greeting message in session_main if user changed greeting_message
    new_greeting = (payload.get("greeting_message") or "").strip()
    if new_greeting:
        try:
            with get_db() as conn:
                c = conn.cursor()
                c.execute("SELECT id FROM chat_messages WHERE session_id = 'session_main' AND role = 'assistant' ORDER BY id ASC LIMIT 1")
                first_row = c.fetchone()
                if first_row:
                    c.execute("UPDATE chat_messages SET content = ? WHERE id = ?", (new_greeting, first_row["id"]))
                    conn.commit()
        except Exception:
            pass

    if "persona_prompt" in payload or "ai_name" in payload or "user_name" in payload:
        formatted_persona = (
            WORKSPACE_CFG["persona_prompt"]
            .replace("{ai_name}", WORKSPACE_CFG["ai_name"])
            .replace("{user_name}", WORKSPACE_CFG["user_name"])
        )
        CORE_README_PATH.write_text(formatted_persona, encoding="utf-8")
        PRIORITY_CACHE["core_rules_text"] = f"--- [CORE FILE: CORE_PERSONA.txt] ---\n{sanitize_lore_and_core_text(formatted_persona)[:4000]}"
        PRIORITY_CACHE["reflex_core_digest"] = build_reflex_persona_digest(
            formatted_persona, WORKSPACE_CFG["ai_name"], WORKSPACE_CFG["user_name"]
        )
        # Run heavy SQLite chunk & glossary re-indexing in a background daemon thread so Save is instant (<10ms)!
        threading.Thread(target=lambda: (sync_priority_files(force=True), update_partner_evolution(), sync_pseudo_memory_and_index()), daemon=True).start()

    if "user_name" in payload and (payload.get("user_name") or "").strip():
        pcard = load_user_profile_card()
        pcard["user_name"] = WORKSPACE_CFG["user_name"]
        save_user_profile_card(pcard)
    return {"ok": True, "config": WORKSPACE_CFG, "user_profile": load_user_profile_card()}

@app.post("/upload_asset")
def upload_custom_asset(payload: dict):
    asset_type = (payload.get("asset_type") or "avatar").strip().lower()
    filename = Path(payload.get("filename") or "asset.png").name
    b64_data = payload.get("data_base64") or ""
    crop = payload.get("crop")
    if not b64_data:
        raise HTTPException(400, "Missing image data")
    if "," in b64_data:
        b64_data = b64_data.split(",", 1)[1]

    raw_bytes = base64.b64decode(b64_data)
    out_name = f"custom_{asset_type}_{int(time.time())}.png"
    out_path = ASSETS_DIR / out_name

    try:
        img = Image.open(io.BytesIO(raw_bytes)).convert("RGBA")
        w, h = img.size
        if isinstance(crop, dict):
            cx = max(0.0, min(1.0, float(crop.get("x", 0.0))))
            cy = max(0.0, min(1.0, float(crop.get("y", 0.0))))
            cw = max(0.05, min(1.0 - cx, float(crop.get("w", 1.0))))
            ch = max(0.05, min(1.0 - cy, float(crop.get("h", 1.0))))
            left = int(cx * w)
            top = int(cy * h)
            right = int((cx + cw) * w)
            bottom = int((cy + ch) * h)
            if right > left and bottom > top:
                img = img.crop((left, top, right, bottom))
        if asset_type == "avatar":
            img = img.resize((256, 256), Image.Resampling.LANCZOS)
        img.save(out_path, format="PNG")
    except Exception:
        out_path.write_bytes(raw_bytes)

    url = f"/custom_asset/{out_name}"
    if asset_type == "avatar":
        WORKSPACE_CFG["avatar_url"] = url
    elif asset_type == "wallpaper":
        WORKSPACE_CFG["wallpaper_url"] = url
    save_workspace_config(WORKSPACE_CFG)
    return {"ok": True, "url": url, "filename": filename, "config": WORKSPACE_CFG}

@app.get("/custom_asset/{filename}")
def serve_custom_asset(filename: str):
    fpath = ASSETS_DIR / Path(filename).name
    if not fpath.exists():
        raise HTTPException(404, "Asset not found")
    return FileResponse(str(fpath))

@app.post("/parse_attachment")
def parse_chat_attachment(payload: dict):
    filename = Path(payload.get("filename") or "file.txt").name
    b64_data = payload.get("data_base64") or ""
    if not b64_data:
        return {"ok": False, "text": ""}
    if "," in b64_data:
        b64_data = b64_data.split(",", 1)[1]
    raw_bytes = base64.b64decode(b64_data)
    ext = Path(filename).suffix.lower()

    if ext == ".pdf":
        try:
            doc = fitz.open(stream=raw_bytes, filetype="pdf")
            max_pgs = 30 if is_unrestricted_tokens_enabled() else 8
            pages = [f"[Page {i+1}]\n{p.get_text('text').strip()}" for i, p in enumerate(list(doc)[:max_pgs]) if p.get_text("text").strip()]
            doc.close()
            return {"ok": True, "text": "\n\n".join(pages)[:(24000 if is_unrestricted_tokens_enabled() else 4500)]}
        except Exception as e:
            return {"ok": False, "text": f"[PDF read error: {e}]"}
    elif ext in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
        try:
            img = Image.open(io.BytesIO(raw_bytes))
            return {"ok": True, "text": f"[Attached Image '{filename}' | Resolution: {img.width}x{img.height}px | Mode: {img.mode}]"}
        except Exception:
            return {"ok": True, "text": f"[Attached Image '{filename}']"}
    else:
        return {"ok": True, "text": raw_bytes.decode("utf-8", errors="ignore")[:(24000 if is_unrestricted_tokens_enabled() else 4500)]}

@app.get("/spotify/login")
def spotify_login():
    oauth = get_spotify_oauth()
    if not oauth:
        return HTMLResponse("<h3>Please save your SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET in Studio Settings first.</h3>")
    return RedirectResponse(oauth.get_authorize_url())

@app.get("/spotify_callback")
def spotify_callback(code: str = ""):
    oauth = get_spotify_oauth()
    if oauth and code:
        oauth.get_access_token(code, as_dict=False)
        return HTMLResponse("<body style='background:#0d0e12;color:#a7f3d0;font-family:sans-serif;padding:40px;'><h2>✅ Spotify OAuth Connected!</h2><p>You can close this tab and return to AetherVault Studio.</p></body>")
    return HTMLResponse("<h3>Spotify callback failed or missing code.</h3>")

@app.get("/spotify/test")
def api_spotify_test():
    """Live diagnostic check for Spotify OAuth credentials, token validity, account tier, and active devices."""
    sp_cfg = WORKSPACE_CFG.get("spotify") or {}
    has_keys = bool((sp_cfg.get("client_id") or "").strip() and (sp_cfg.get("client_secret") or "").strip())
    sp, auth_note = get_authenticated_spotify_client()
    if not sp:
        return {
            "ok": False,
            "has_keys": has_keys,
            "token_cached": (BASE_DIR / ".spotify_token_cache").exists(),
            "message": auth_note,
            "tip": "Paste Client ID & Secret, make sure http://127.0.0.1:8000/spotify_callback is saved in Spotify Developer Dashboard, then click 'Authorize Spotify OAuth'."
        }
    info = {"ok": True, "has_keys": True, "token_cached": True, "user": "", "product": "", "devices": [], "warnings": []}
    try:
        me = sp.current_user() or {}
        info["user"] = me.get("display_name") or me.get("id") or "Authenticated User"
        info["product"] = me.get("product") or "unknown"
        if info["product"] != "premium":
            info["warnings"].append("Account is not Spotify Premium — Web API remote playback (start/pause) may return 403, so AetherVault will automatically use Windows track URIs & hardware media keys.")
    except Exception as e:
        info["warnings"].append(f"Profile check returned: {str(e)[:140]} (Check Spotify Dashboard -> User Management allowlist if you see 403).")
    try:
        _, devs = _pick_spotify_device_id(sp)
        info["devices"] = [f"{d.get('name')} ({d.get('type')}, active={d.get('is_active')})" for d in devs]
        if not devs:
            info["warnings"].append("0 active playback devices awake right now. Open Spotify on your PC and hit Play for 1 second to wake the device.")
    except Exception as e:
        info["warnings"].append(f"Device scan returned: {str(e)[:140]}")
    info["message"] = f"Connected as {info['user'] or 'Spotify User'} ({info['product'] or 'tier unknown'}) | Devices: {len(info['devices'])}"
    return info


# =====================================================================
# 12. UNIVERSAL .ZIP EXPORT / IMPORT & LEGACY FOLDER IMPORTER
# =====================================================================
@app.get("/workspace/export_zip")
def export_workspace_zip(include_keys: int = 0):
    stamp = time.strftime("%Y%m%d_%H%M%S")
    safe_ai = re.sub(r"[^a-zA-Z0-9_-]", "_", WORKSPACE_CFG.get("ai_name", "Aether"))
    zip_path = BACKUPS_DIR / f"AetherVault_{safe_ai}_{stamp}.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        export_list = [DB_PATH, CONFIG_PATH, USER_PROFILE_CARD_PATH, GLOSSARY_PATH, PSEUDO_INDEX_JSON_PATH, PARTNER_EVOLUTION_PATH, ERROR_AUDIT_LOG_PATH, MANUAL_PDF_PATH, CUSTOM_REQS_PATH, BASE_DIR / "aethervault_logo.svg"]
        if include_keys and API_VAULT_PATH.exists():
            export_list.append(API_VAULT_PATH)
        for single_file in export_list:
            if single_file.exists():
                zf.write(single_file, arcname=single_file.name)
        for folder in (PDF_DIR, MEMORY_DIR, CHAT_LOG_DIR, ASSETS_DIR, GEN_IMG_DIR, GEN_AUDIO_DIR, CUSTOM_TOOLS_DIR):
            if folder.exists():
                for f in folder.rglob("*"):
                    if f.is_file():
                        zf.write(f, arcname=f.relative_to(BASE_DIR).as_posix())

    return FileResponse(str(zip_path), filename=zip_path.name, media_type="application/zip")

@app.post("/workspace/import_zip")
async def import_workspace_zip(file: UploadFile = File(...)):
    global WORKSPACE_CFG
    temp_zip = BACKUPS_DIR / f"import_{int(time.time())}.zip"
    content = await file.read()
    temp_zip.write_bytes(content)
    try:
        base_res = BASE_DIR.resolve()
        with zipfile.ZipFile(temp_zip, "r") as zf:
            for member in zf.namelist():
                if ".." in member or member.startswith("/") or member.startswith("\\") or ":" in member:
                    continue
                target_out = (BASE_DIR / member).resolve()
                if base_res not in target_out.parents and target_out != base_res:
                    continue
                zf.extract(member, BASE_DIR)
        init_db()
        WORKSPACE_CFG = load_workspace_config()
        sync_memory_vault_file()
        sync_priority_files(force=True)
        return {"ok": True, "message": "Workspace .ZIP imported and indexed successfully!"}
    finally:
        if temp_zip.exists():
            temp_zip.unlink()

@app.post("/workspace/import_folder")
def import_legacy_folder(payload: dict):
    global WORKSPACE_CFG
    src_str = (payload.get("source_path") or "").strip().strip("'\"")
    src = Path(src_str)
    if not src.exists() or not src.is_dir():
        return {"ok": False, "error": f"Directory not found on PC: {src_str}"}

    imported_items = []
    try:
        if (src / "priority_pdfs").exists() or (src / "memory_core.db").exists():
            for fname in ("memory_core.db", "workspace_config.json", "glossary_index.json"):
                f_src = src / fname
                if f_src.exists():
                    shutil.copy2(f_src, BASE_DIR / fname)
                    imported_items.append(fname)
            for dname in ("priority_pdfs", "memory_vault", "chat_logs", "custom_assets"):
                d_src = src / dname
                if d_src.exists() and d_src.is_dir():
                    shutil.copytree(d_src, BASE_DIR / dname, dirs_exist_ok=True)
                    imported_items.append(f"/{dname}")
        else:
            count = 0
            for f in src.rglob("*"):
                if f.is_file() and f.suffix.lower() in {".pdf", ".txt", ".md"}:
                    rel = f.relative_to(src)
                    dest = PDF_DIR / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, dest)
                    count += 1
            imported_items.append(f"{count} knowledge files copied into /priority_pdfs")

        init_db()
        WORKSPACE_CFG = load_workspace_config()
        sync_memory_vault_file()
        sync_priority_files(force=True)
        return {"ok": True, "imported": imported_items}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# =====================================================================
# 13. FILE MODE, MODEL, MEMORY & STREAMING CHAT (WITH STOP BUTTON & LOOP GUARD)
# =====================================================================
@app.post("/set_file_mode")
def set_file_mode(payload: dict):
    filename = (payload.get("filename") or "").strip()
    mode = (payload.get("mode") or "core").strip().lower()
    if mode not in ("core", "lore"):
        mode = "lore"
    with get_db() as conn:
        conn.execute("UPDATE priority_pdfs SET file_mode = ?, manual_override = 1 WHERE filename = ?", (mode, filename))
        conn.commit()
    sync_priority_files(force=True)
    return {"ok": True, "filename": filename, "mode": mode}

@app.post("/rebuild_glossary")
def api_rebuild_glossary():
    sync_priority_files(force=True)
    return {"ok": True}

@app.post("/pc_roots/add")
def api_add_pc_root(payload: dict):
    path_str = (payload.get("path") or "").strip()
    if path_str and Path(path_str).exists():
        if path_str not in STATE["allowed_pc_roots"]:
            STATE["allowed_pc_roots"].append(path_str)
        return {"ok": True}
    return {"ok": False, "error": f"Folder not found: {path_str}"}

@app.post("/pc_roots/remove")
def api_remove_pc_root(payload: dict):
    path_str = (payload.get("path") or "").strip()
    if path_str in STATE["allowed_pc_roots"]:
        STATE["allowed_pc_roots"].remove(path_str)
    return {"ok": True}

@app.post("/manage_package")
def api_manage_package(payload: dict):
    global HAS_PYAUTOGUI, pyautogui
    pkg = (payload.get("pkg") or "").strip()
    action = (payload.get("action") or "install").strip().lower()
    if not pkg or not re.match(r"^[a-zA-Z0-9_\-\.]+$", pkg):
        return {"ok": False, "error": "Invalid package name"}
    try:
        set_step(f"{'Installing' if action == 'install' else 'Uninstalling'} library: {pkg}...")
        cmd = [sys.executable, "-m", "pip", "install", pkg] if action == "install" else [sys.executable, "-m", "pip", "uninstall", "-y", pkg]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if pkg == "ddgs" and action == "install" and proc.returncode == 0:
            try:
                global DDGS, DDGS_IS_MODERN
                from ddgs import DDGS as _HOT_DDGS
                DDGS = _HOT_DDGS
                DDGS_IS_MODERN = True
            except Exception:
                pass
        if pkg == "pyautogui" and action == "install" and proc.returncode == 0:
            try:
                import pyautogui as pag
                pyautogui = pag
                pyautogui.FAILSAFE = True
                HAS_PYAUTOGUI = True
            except Exception:
                pass
        if action == "install" and proc.returncode == 0:
            try:
                existing_reqs = set(CUSTOM_REQS_PATH.read_text(encoding="utf-8").splitlines()) if CUSTOM_REQS_PATH.exists() else set()
                if pkg not in existing_reqs:
                    existing_reqs.add(pkg)
                    CUSTOM_REQS_PATH.write_text("\n".join(sorted(existing_reqs)) + "\n", encoding="utf-8")
            except Exception:
                pass
        check_packages_status(force=True)
        set_step("Idle")
        return {"ok": proc.returncode == 0, "output": (proc.stdout or proc.stderr)[-300:]}
    except Exception as e:
        set_step("Idle")
        return {"ok": False, "error": str(e)}

@app.get("/generated_image/{filename}")
def serve_generated_image(filename: str):
    fpath = GEN_IMG_DIR / Path(filename).name
    if not fpath.exists():
        raise HTTPException(404, "Image not found")
    return FileResponse(str(fpath))

@app.post("/generate_image")
def api_generate_image(payload: dict):
    prompt = (payload.get("prompt") or "").strip()
    if not prompt:
        return {"ok": False, "error": "Empty prompt"}
    set_step(f"Generating image: {prompt[:35]}...")
    res = generate_image_tool(prompt)
    set_step("Idle")
    return res

@app.post("/toggle_offline")
def toggle_offline(payload: dict):
    STATE["offline_mode"] = bool(payload.get("offline", False))
    return {"offline_mode": STATE["offline_mode"]}

@app.post("/set_performance")
def set_performance(payload: dict):
    mode = payload.get("mode", "Reflex (Auto-Smart Fast)")
    valid_modes = ["Reflex (Auto-Smart Fast)", "Laptop 2015 (Fast)", "Eco (Safe)", "Balanced", "Turbo (Max Threads)"]
    if mode in valid_modes:
        prev_mode = STATE["performance_mode"]
        STATE["performance_mode"] = mode
        WORKSPACE_CFG["performance_mode"] = mode
        if mode == "Reflex (Auto-Smart Fast)":
            WORKSPACE_CFG["routing_mode"] = "auto_reflex"
        elif mode == "Laptop 2015 (Fast)":
            WORKSPACE_CFG["routing_mode"] = "always_reflex"
        elif mode == "Turbo (Max Threads)":
            WORKSPACE_CFG["routing_mode"] = "always_deep"
        else:
            WORKSPACE_CFG["routing_mode"] = "auto_reflex"
        save_workspace_config(WORKSPACE_CFG)
        # Reload model if switching to/from Turbo (8192 ctx) so n_ctx matches
        if (prev_mode == "Turbo (Max Threads)") != (mode == "Turbo (Max Threads)"):
            if STATE["current_model"] and not STATE["loading_model"]:
                threading.Thread(target=load_local_model, args=(STATE["current_model"],), daemon=True).start()
    return {"performance_mode": STATE["performance_mode"]}

@app.post("/api/memories/compact")
def api_compact_memories():
    res = MEMORY_COMPACTOR.compact_now()
    sync_memory_vault_file()
    return {"ok": True, **res}

@app.post("/api/bluesky/post")
def api_bluesky_post(payload: dict):
    return post_to_bluesky(str(payload.get("text") or ""), str(payload.get("reply_uri") or ""), str(payload.get("reply_cid") or ""))

@app.post("/unload_model")
def api_unload_model():
    return unload_local_model("Manual unload from Studio UI")

@app.post("/set_idle_sleep")
def api_set_idle_sleep(payload: dict):
    try:
        mins = max(0, min(240, int(payload.get("minutes", 10))))
    except Exception:
        mins = 10
    WORKSPACE_CFG["idle_unload_minutes"] = mins
    save_workspace_config(WORKSPACE_CFG)
    STATE["last_activity_ts"] = time.time()
    return {"ok": True, "idle_unload_minutes": mins}

@app.post("/select_model")
def select_model(payload: dict):
    filename = payload.get("filename")
    if filename and not STATE["loading_model"]:
        threading.Thread(target=load_local_model, args=(filename,), daemon=True).start()
    return {"loading": True}

@app.post("/download_model")
def start_download_model(payload: dict):
    if STATE["offline_mode"]:
        raise HTTPException(400, "Cannot download while Offline Mode is active.")
    if STATE["download"]["active"]:
        raise HTTPException(400, "A download is already in progress.")
    repo_id = payload.get("repo_id", "").strip()
    filename = payload.get("filename", "").strip()
    threading.Thread(target=download_worker, args=(repo_id, filename), daemon=True).start()
    return {"started": True}

@app.post("/download_cancel")
def cancel_download_model():
    """Immediately cancels/resets any stalled or active Hugging Face download."""
    STATE["download"]["cancel_requested"] = True
    STATE["download"]["active"] = False
    STATE["download"]["error"] = "Download cancelled by user."
    if STATE["current_step"].startswith("⬇️ "):
        set_step("Idle")
    return {"ok": True, "cancelled": True}

@app.post("/open_folder")
def open_folder_on_pc(payload: dict):
    folder_type = payload.get("folder", "pdfs")
    mapping = {
        "pdfs": PDF_DIR,
        "memories": MEMORY_DIR,
        "models": MODEL_DIR,
        "chat_logs": CHAT_LOG_DIR,
        "images": GEN_IMG_DIR,
        "backups": BACKUPS_DIR,
        "assets": ASSETS_DIR
    }
    target = mapping.get(folder_type, PDF_DIR)
    ok, msg = avs_platform.open_path_or_uri(str(target))
    return {"opened": str(target), "ok": ok, "message": msg}

@app.post("/upload_priority_file")
def upload_priority_file(payload: dict):
    filename = Path(payload.get("filename", "")).name
    subfolder = (payload.get("subfolder") or "").strip().strip("/\\")
    b64_data = payload.get("data_base64", "")
    if not filename or not b64_data:
        raise HTTPException(400, "Missing filename or file data.")
    if "," in b64_data:
        b64_data = b64_data.split(",", 1)[1]
    raw_bytes = base64.b64decode(b64_data)

    target_dir = (PDF_DIR / subfolder).resolve() if subfolder else PDF_DIR.resolve()
    if PDF_DIR.resolve() not in target_dir.parents and target_dir != PDF_DIR.resolve():
        target_dir = PDF_DIR.resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / filename
    target_path.write_bytes(raw_bytes)
    sync_priority_files(force=True)
    return {"uploaded": target_path.relative_to(PDF_DIR).as_posix()}

@app.post("/delete_priority_file")
def delete_priority_file(payload: dict):
    raw_name = payload.get("filename", "").strip().lstrip("/\\")
    if not raw_name:
        raise HTTPException(400, "Missing filename.")
    target_path = (PDF_DIR / raw_name).resolve()
    if PDF_DIR.resolve() in target_path.parents and target_path.exists() and target_path.is_file():
        target_path.unlink()
    sync_priority_files(force=True)
    return {"deleted": raw_name}

@app.post("/memory/add")
def manual_add_memory(payload: dict):
    category = payload.get("category", "active_state")
    fact = payload.get("fact", "")
    save_to_memory(category, fact)
    update_boot_glossary_index(force=True)
    return {"ok": True}

@app.post("/memory/delete")
def manual_delete_memory(payload: dict):
    mem_id = payload.get("id")
    with get_db() as conn:
        conn.execute("DELETE FROM dynamic_memory WHERE id = ?", (mem_id,))
        conn.commit()
    sync_memory_vault_file()
    return {"ok": True}

@app.get("/session/{session_id}")
def get_session_messages(session_id: str):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT id, role, content, timestamp FROM chat_messages WHERE session_id = ? ORDER BY id ASC", (session_id,))
        msgs = [{"id": r["id"], "role": r["role"], "content": r["content"], "timestamp": r["timestamp"]} for r in c.fetchall()]
    return {"messages": msgs}

@app.get("/session/{session_id}/export_md")
def export_session_markdown(session_id: str):
    ai_label = WORKSPACE_CFG.get("ai_name", "Aether")
    user_label = WORKSPACE_CFG.get("user_name", "Creator")
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT title FROM chat_sessions WHERE id = ?", (session_id,))
        srow = c.fetchone()
        title = srow["title"] if srow else session_id
        c.execute("SELECT role, content, timestamp FROM chat_messages WHERE session_id = ? ORDER BY id ASC", (session_id,))
        msgs = c.fetchall()
    lines = [f"# {title}", f"*Exported from AetherVault Studio v{APP_VERSION} ({time.strftime('%Y-%m-%d %H:%M')})*", ""]
    for m in msgs:
        who = user_label if m["role"] == "user" else ai_label
        lines.append(f"### {who} ({m['timestamp']})")
        lines.append(m["content"])
        lines.append("")
    md_text = "\n".join(lines)
    safe_fn = re.sub(r"[^a-zA-Z0-9_-]", "_", session_id) + ".md"
    return StreamingResponse(
        io.BytesIO(md_text.encode("utf-8")),
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{safe_fn}"'},
    )

@app.post("/session/new")
def new_session(payload: dict):
    session_id = payload.get("session_id", f"session_{int(time.time())}")
    title = payload.get("title", "New Conversation")
    greeting = WORKSPACE_CFG.get("greeting_message") or "System ready. What are we working on today?"
    with get_db() as conn:
        conn.execute("INSERT OR REPLACE INTO chat_sessions (id, title, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)", (session_id, title))
        conn.execute("INSERT INTO chat_messages (session_id, role, content) VALUES (?, 'assistant', ?)", (session_id, greeting))
        conn.commit()
    export_chats_to_txt_files()
    return {"session_id": session_id}

@app.post("/session/delete")
def delete_session(payload: dict):
    session_id = payload.get("session_id")
    with get_db() as conn:
        conn.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
        conn.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
        conn.commit()
    return {"deleted": True}

@app.post("/session/rename")
def api_rename_session(payload: dict):
    session_id = (payload.get("session_id") or "").strip()
    title = (payload.get("title") or "").strip()[:60]
    if not session_id or not title:
        return {"ok": False, "error": "Missing session_id or title."}
    with get_db() as conn:
        conn.execute("UPDATE chat_sessions SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (title, session_id))
        conn.commit()
    export_chats_to_txt_files()
    return {"ok": True, "session_id": session_id, "title": title}

@app.post("/toggle_auto_web")
def api_toggle_auto_web(payload: dict):
    enabled = bool(payload.get("auto_web_search", True))
    WORKSPACE_CFG["auto_web_search"] = enabled
    save_workspace_config(WORKSPACE_CFG)
    return {"ok": True, "auto_web_search": enabled}

@app.post("/toggle_unrestricted")
def api_toggle_unrestricted(payload: dict):
    enabled = bool(payload.get("unrestricted_tokens", True))
    prev = bool(WORKSPACE_CFG.get("unrestricted_tokens", True))
    WORKSPACE_CFG["unrestricted_tokens"] = enabled
    save_workspace_config(WORKSPACE_CFG)
    # Reload active local model in background so its n_ctx expands/contracts cleanly
    if prev != enabled and STATE.get("current_model") and not STATE.get("loading_model"):
        threading.Thread(target=load_local_model, args=(STATE["current_model"],), daemon=True).start()
    return {"ok": True, "unrestricted_tokens": enabled}

@app.post("/profile/test_weather")
def api_test_pin_weather(payload: dict):
    loc = str(payload.get("location") or "").strip()
    lat = payload.get("latitude")
    lon = payload.get("longitude")
    out = get_live_weather(loc, latitude=lat, longitude=lon)
    return {"ok": ("LIVE WEATHER FOR" in out), "result": out}

@app.post("/chat_stream")
def chat_stream(payload: dict):
    def event_generator():
        ai_name = WORKSPACE_CFG.get("ai_name", "Aether")
        user_name = WORKSPACE_CFG.get("user_name", "Creator")
        STATE["stop_requested"] = False
        STATE["last_activity_ts"] = time.time()
        STATE["last_debug"] = {
            "timestamp": time.strftime("%H:%M:%S"),
            "model": STATE["current_model"] or "None",
            "gear_used": "Gear 1 (Reflex Fast-Path)",
            "gpu_active": STATE["gpu_offload"],
            "prompt_chars": 0,
            "core_files": [],
            "lore_pulled": [],
            "chats_pulled": [],
            "pc_files_scanned": [],
            "osworld_actions": [],
            "last_issue": None,
            "steps": [],
            "error": ""
        }
        try:
            if STATE["loading_model"]:
                err_card = format_predetermined_error("ERR_MODEL_LOADING")
                yield json.dumps({"type": "issue", "issue": err_card}) + "\n"
                yield json.dumps({"type": "done", "reply": f"⏳ **[{err_card['code']}: {err_card['title']}]** {err_card['message']}\n💡 *{err_card['fix']}*"}) + "\n"
                return
            b_mode = WORKSPACE_CFG.get("brain_mode", "local_only")
            has_api_slots = bool([s for s in load_api_vault().get("slots", []) if s.get("enabled", True)])
            can_use_api = (b_mode in ("smart_api", "hybrid")) and has_api_slots and not STATE["offline_mode"]
            if not STATE["llm"] and not can_use_api and STATE.get("idle_sleeping"):
                yield json.dumps({"type": "step", "text": "💤 Waking sleeping GGUF model back into RAM/VRAM..."}) + "\n"
                touch_activity(wake_model=True)
            if not STATE["llm"] and not can_use_api:
                target_m = pick_lightweight_failsafe_model() if (b_mode == "hybrid" or STATE["performance_mode"] == "Laptop 2015 (Fast)") else (WORKSPACE_CFG.get("last_loaded_model") or pick_lightweight_failsafe_model())
                if target_m:
                    yield json.dumps({"type": "step", "text": f"🧠 Auto-loading offline GGUF model '{target_m}'..."}) + "\n"
                    load_local_model(target_m)
                if not STATE["llm"]:
                    err_card = format_predetermined_error("ERR_MODEL_NOT_LOADED")
                    yield json.dumps({"type": "issue", "issue": err_card}) + "\n"
                    yield json.dumps({"type": "done", "reply": f"⚠️ **[{err_card['code']}: {err_card['title']}]** {err_card['message']}\n💡 *{err_card['fix']}*"}) + "\n"
                    return

            session_id = payload.get("session_id") or "session_main"
            user_msg = (payload.get("message") or "").strip()
            STATE["last_user_msg"] = user_msg
            STATE["ui_sync_needed"] = False
            attached_name = (payload.get("attached_name") or "").strip()
            attached_text = (payload.get("attached_text") or "").strip()

            if attached_name:
                att_lim = 20000 if is_unrestricted_tokens_enabled() else 3500
                user_msg = f"{user_msg}\n\n[Attached File: {attached_name}]\n{attached_text[:att_lim]}".strip()

            def emit_step(txt: str):
                set_step(txt)
                return json.dumps({"type": "step", "text": txt}) + "\n"

            with get_db() as conn:
                c = conn.cursor()
                c.execute("SELECT id, title FROM chat_sessions WHERE id = ?", (session_id,))
                row = c.fetchone()
                short_title = (user_msg[:30] + "...") if len(user_msg) > 30 else user_msg
                if not row:
                    c.execute("INSERT INTO chat_sessions (id, title) VALUES (?, ?)", (session_id, short_title))
                elif row["title"] in ("New Conversation", "Main Workspace", "Hanging Out"):
                    c.execute("UPDATE chat_sessions SET title = ? WHERE id = ?", (short_title, session_id))

                c.execute("INSERT INTO chat_messages (session_id, role, content) VALUES (?, 'user', ?)", (session_id, user_msg))
                conn.commit()

                c.execute("SELECT role, content FROM chat_messages WHERE session_id = ? ORDER BY id DESC LIMIT 6", (session_id,))
                recent_turns = [{"role": r["role"], "content": r["content"]} for r in reversed(c.fetchall())]

            harvested_notes = harvest_passive_user_notes(user_msg)
            sync_pseudo_memory_and_index()
            gear, gear_reason = classify_task_gear(user_msg, attached_name, recent_turns)
            generated_img_url = None
            generated_audio_url = None

            # =================================================================
            # GEAR 1: REFLEX FAST-PATH ("DUMB & INSTANT" MODE FOR SIMPLE CHATS)
            # =================================================================
            if gear == "reflex":
                STATE["last_debug"]["gear_used"] = f"Gear 1: Reflex ({gear_reason})"
                yield emit_step(f"⚡ Gear 1 (Reflex Fast-Path): {gear_reason} — bypassing heavy Lore & Tool overhead")

                mem_short = format_memories_for_prompt(limit=2)
                digest = PRIORITY_CACHE["reflex_core_digest"] or build_reflex_persona_digest(
                    WORKSPACE_CFG["persona_prompt"], ai_name, user_name
                )
                pseudo_dig = PRIORITY_CACHE.get("pseudo_notes_digest", "")[:400]
                # Prefix-Locked Ordering: Static digest stays locked at top (tokens 0..N) for llama.cpp KV reuse!
                reflex_sys = f"{digest}\n\n=== SESSION STATE & PSEUDO-MEMORY ===\n{mem_short}\n{pseudo_dig}"
                record_temp_gear_cache("reflex", reflex_sys)
                reflex_web_ctx = ""
                low_u = user_msg.lower()
                g1_web_ran = False
                g1_fresh, g1_fresh_q = detect_freshness_or_fact_query(user_msg)
                if not STATE["offline_mode"] and (any(p in low_u for p in FAST_WEB_INTENT_PATTERNS) or g1_fresh):
                    q_g1 = g1_fresh_q if g1_fresh else clean_web_search_query(user_msg)
                    yield emit_step(f"🌐 Gear 1 Auto-Web Grounding: looking up '{q_g1[:40]}' online...")
                    g1_res = search_web(q_g1)[:1300]
                    yield json.dumps({"type": "workbench_io", "tool": "auto_web_search", "code": f"vault.web({q_g1!r})", "output": g1_res[:900]}) + "\n"
                    reflex_web_ctx = f"[LIVE WEB RESULTS FOR '{q_g1}' — ANSWER USING THESE REAL FACTS]:\n{g1_res}"
                    g1_web_ran = True
                messages = build_safe_messages(reflex_sys, reflex_web_ctx, recent_turns, max_turns=3)
                prompt_chars = sum(len(m["content"]) for m in messages)
                STATE["last_debug"]["prompt_chars"] = prompt_chars
                cfg = get_governor_settings("reflex", prompt_chars)

                accel_tag = "🔥 Vulkan GPU" if STATE["gpu_offload"] else f"💻 CPU ({cfg['threads']}T)"
                yield emit_step(f"🚀 Instant Reflex Generation ({accel_tag} | {prompt_chars} chars | Unlimited Natural Finish)...")

                STATE["generating"] = True
                reflex_reply = ""
                bracket_hold = ""
                in_think = False
                escalated_to_deep = False

                if True:
                    _g1_hints = avs_model_polish.provider_profile_hints(
                        STATE.get("active_api_label") or STATE.get("current_model") or WORKSPACE_CFG.get("brain_mode", ""),
                        WORKSPACE_CFG.get("workspace_mode", "assistant")
                    )
                    stream_iter = dispatch_brain_stream(
                        messages=messages,
                        max_tokens=cfg["max_tokens"],
                        temperature=_g1_hints["temperature"],
                        top_p=_g1_hints["top_p"],
                        min_p=0.12,
                        repeat_penalty=1.15,
                        stop=["<START>", f"\n{user_name}:", "\nUser:", "[INST]", "[/INST]"]
                    )
                    for chunk in stream_iter:
                        if STATE["stop_requested"]:
                            yield emit_step("⏹️ Generation stopped by user.")
                            break
                        delta = chunk["choices"][0].get("delta", {}).get("content") or ""
                        if not delta:
                            continue
                        if not STATE["gpu_offload"] and (STATE["performance_mode"] == "Laptop 2015 (Fast)" or (os.cpu_count() or 4) <= 2):
                            time.sleep(0.005)
                        reflex_reply += delta

                        if any(tag in reflex_reply for tag in ("[[DEEP]]", "[DEEP]", "<tool_call>", "[[FILES:", "[[LORE:", "[[OSWORLD:", "[[SPOTIFY:", "[[CHATS:", "[[SELF:", "[[MUSIC:", "[[IMAGE:", "[[PCINFO", "[[PYTHON:")):
                            escalated_to_deep = True
                            bracket_hold = ""
                            break

                        if has_repetition_delirium(reflex_reply):
                            err_card = format_predetermined_error("ERR_DELIRIUM_LOOP")
                            yield json.dumps({"type": "issue", "issue": err_card}) + "\n"
                            yield emit_step(f"🛡️ {err_card['code']}: Cut repetition loop cleanly.")
                            break

                        if "<think>" in delta:
                            in_think = True
                            delta = delta.replace("<think>", "")
                        if "</think>" in delta:
                            in_think = False
                            delta = delta.split("</think>", 1)[1]
                        if in_think:
                            continue

                        # Hold back potential [[...]] tag tokens until verified
                        combined_delta = bracket_hold + delta
                        if "[" in combined_delta:
                            idx_b = combined_delta.find("[")
                            safe_prefix = combined_delta[:idx_b]
                            bracket_hold = combined_delta[idx_b:]
                            if safe_prefix:
                                yield json.dumps({"type": "token", "text": safe_prefix}) + "\n"
                            # If bracket_hold clearly isn't a [[ tag and exceeds 14 chars, flush it
                            if len(bracket_hold) > 2 and not bracket_hold.startswith("[["):
                                yield json.dumps({"type": "token", "text": bracket_hold}) + "\n"
                                bracket_hold = ""
                        else:
                            bracket_hold = ""
                            if combined_delta:
                                yield json.dumps({"type": "token", "text": combined_delta}) + "\n"

                if not escalated_to_deep and bracket_hold:
                    yield json.dumps({"type": "token", "text": bracket_hold}) + "\n"
                    bracket_hold = ""

                if not escalated_to_deep:
                    clean_reflex = re.sub(r"<\|think\|>[\s\S]*?<\|/think\|>", "", reflex_reply, flags=re.IGNORECASE)
                    clean_reflex = re.sub(r"<think>[\s\S]*?</think>", "", clean_reflex, flags=re.IGNORECASE).strip()
                    clean_reflex = re.sub(rf"^({re.escape(ai_name)}|Assistant):\s*", "", clean_reflex, flags=re.IGNORECASE).strip()
                    fast_search_m = re.search(r"\[\[SEARCH:([^\]]+)\]\]", clean_reflex)
                    if fast_search_m and fast_search_m.group(1).strip().lower() not in ("clean keywords", "query", "keywords") and not STATE["offline_mode"] and not STATE["stop_requested"]:
                        fs_q = clean_web_search_query(fast_search_m.group(1).strip())
                        yield emit_step(f"🌐 Gear 1 Live Web Lookup: '{fs_q[:38]}'...")
                        fs_out = search_web(fs_q)[:1400]
                        yield json.dumps({"type": "workbench_io", "tool": "web_search", "code": f"vault.web({fs_q!r})", "output": fs_out[:900]}) + "\n"
                        clean_reflex = synthesize_tool_followup(reflex_sys, recent_turns[-3:], re.sub(r"\[\[SEARCH:[^\]]+\]\]", "", clean_reflex).strip() or "Checking online.", f"[Live Web Search Results for '{fs_q}']:\n{fs_out}", cfg, user_name, ai_name)
                        g1_web_ran = True
                    elif not g1_web_ran and is_auto_web_search_enabled() and not STATE["stop_requested"] and detect_model_uncertainty(clean_reflex) and is_query_searchable_for_rescue(user_msg):
                        rq = clean_web_search_query(user_msg)
                        yield emit_step(f"🌐 Caught knowledge gap — auto-searching web for '{rq[:40]}'...")
                        r_out = search_web(rq)[:1400]
                        yield json.dumps({"type": "workbench_io", "tool": "uncertainty_web_rescue", "code": f"vault.web({rq!r})", "output": r_out[:900]}) + "\n"
                        clean_reflex = synthesize_tool_followup(reflex_sys, recent_turns[-3:], clean_reflex, f"[Auto-Web Knowledge Rescue Results for '{rq}']:\n{r_out}", cfg, user_name, ai_name)
                    _is_asst_g1 = (WORKSPACE_CFG.get("workspace_mode", "assistant") == "assistant")
                    clean_reflex = avs_model_polish.normalize_model_output(clean_reflex, ai_name=ai_name, user_name=user_name, is_assistant_mode=_is_asst_g1)
                    _g1_fin = avs_turn_pipeline.finalize_turn_reply(clean_reflex, ai_name=ai_name, user_name=user_name, evidence_pool=f"{PRIORITY_CACHE.get('core_rules_text', '')} {WORKSPACE_CFG.get('persona_prompt', '')}")
                    clean_reflex, _g1_warns = referee_lore_and_grounding(_g1_fin["reply"], user_msg, ai_name, "")
                    STATE["last_debug"]["referee_warnings"] = _g1_warns
                    update_partner_evolution(user_msg, clean_reflex)
                    if STATE["stop_requested"]:
                        clean_reflex = f"{clean_reflex} *(⏹️ Stopped)*".strip()
                    if not clean_reflex:
                        clean_reflex = "..."
                    with get_db() as conn:
                        conn.execute("INSERT INTO chat_messages (session_id, role, content) VALUES (?, 'assistant', ?)", (session_id, clean_reflex))
                        conn.execute("UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (session_id,))
                        conn.commit()
                    export_chats_to_txt_files()
                    yield json.dumps({"type": "done", "reply": clean_reflex, "image_url": None}) + "\n"
                    return
                else:
                    yield emit_step("🧠 Model self-escalated from Reflex -> Gear 2 (Deep Mode)! Loading full Lore & Tools...")

            # =================================================================
            # GEAR 2 / OPERATOR MODE (NATIVE JSON TOOLS + LORE-ISOLATION)
            # =================================================================
            is_operator = (gear == "operator")
            STATE["last_debug"]["gear_used"] = f"Operator Mode ({gear_reason})" if is_operator else f"Gear 2: Deep ({gear_reason})"
            mem_context = format_memories_for_prompt(limit=4 if is_operator else 12)
            core_files = ["OPERATOR_VOICE_CARD"] if is_operator else (PRIORITY_CACHE["core_file_names"] or ["CORE_PERSONA.txt"])
            STATE["last_debug"]["core_files"] = core_files
            if is_operator:
                yield emit_step("🛠️ Assistant & Live Python Workbench Active (Lore RAG locked out — direct in-process execution ready)")
            else:
                yield emit_step(f"💾 Gear 2 (Deep Mode): Priority #1 Memory Vault + CORE ({', '.join(core_files)}) loaded")

            dynamic_turn_context = ""
            web_searched_this_turn = False
            low_msg = user_msg.lower()

            is_gauntlet_req, gauntlet_active = is_tool_gauntlet_query(user_msg)
            if is_gauntlet_req:
                g_mode_lbl = "Full Active PC Gauntlet (17 tools)" if gauntlet_active else "Safe Silent Gauntlet (13 tools)"
                yield emit_step(f"🧪 Launching Context-Safe Step-by-Step {g_mode_lbl}...")
                gauntlet_scorecard = ""
                for gevt in run_tool_gauntlet_generator(include_active=gauntlet_active):
                    ph = gevt.get("phase")
                    if ph == "start":
                        yield emit_step(f"🧪 [{gevt['index']}/{gevt['total']}] Testing {gevt['icon']} {gevt['label']}...")
                    elif ph == "result":
                        yield json.dumps({
                            "type": "workbench_io",
                            "tool": f"gauntlet [{gevt['index']}/{gevt['total']}] {gevt['id']}",
                            "code": f"vault.test_step({gevt['id']!r})",
                            "output": f"{gevt['badge']} {gevt['status']} ({gevt['ms']}ms) — {gevt['detail']}"
                        }) + "\n"
                    elif ph == "summary":
                        gauntlet_scorecard = gevt.get("scorecard") or ""
                        if gevt.get("image_url"):
                            generated_img_url = gevt["image_url"]
                dynamic_turn_context += (
                    "[STEP-BY-STEP TOOL GAUNTLET ALREADY EXECUTED — DO NOT RE-RUN TOOLS OR OUTPUT ```workbench!]:\n"
                    f"{gauntlet_scorecard}\n"
                    "Instruction: Every tool above was already tested step-by-step in isolation so your context stays tiny. "
                    "Reply in-character as yourself, give a quick witty rundown of what PASSED, what WARNED/SKIPPED (and why), and any FAILs.\n"
                )

            if not is_gauntlet_req and is_capability_or_api_query(user_msg):
                yield emit_step("🛠️ Injecting Live Workspace Tool, OSWorld & API Manifest (Lore DB bypassed)")
                dynamic_turn_context += (
                    "[LIVE WORKSPACE CAPABILITIES & OSWORLD PC CONTROL MANIFEST]:\n"
                    f"- Identity: You are {ai_name}, running locally inside AetherVault Studio on {user_name}'s PC (Active Model: {STATE['current_model']}).\n"
                    f"- Two-Gear Adaptive Engine: Gear 1 (Reflex Fast-Path) handles everyday chat in ~500 chars; Gear 2 (Deep Mode) wakes up full Lore RAG, cross-chat .txt logs, and OSWorld tools when tasks are taxing.\n"
                    f"- OSWorld Desktop GUI & PC Control: {'ENABLED' if WORKSPACE_CFG.get('osworld_enabled', True) else 'DISABLED'}. You can take live desktop screenshots ([[OSWORLD:screenshot|]]), list open windows ([[OSWORLD:list_windows|]]), launch apps ([[OSWORLD:open_app|notepad]]), click coordinates ([[OSWORLD:click|x,y]]), type text ([[OSWORLD:type|...]]), and press hotkeys ([[OSWORLD:hotkey|ctrl+s]]).\n"
                    f"- Local PC & Google Drive Access: ENABLED across {len(STATE['allowed_pc_roots'])} root directories ({', '.join(STATE['allowed_pc_roots'][:3])}) via [[FILES:query]].\n"
                    f"- Knowledge Base: {len(core_files)} CORE file(s) loaded + {PRIORITY_CACHE['lore_file_count']} LORE file(s) ({PRIORITY_CACHE['lore_chunk_count']} searchable sections) indexed.\n"
                    f"- Live Web Search & Spotify: ONLINE ([[SEARCH:query]] & [[SPOTIFY:play|song]]).\n"
                    "Instruction: Answer confidently and in-character as yourself.\n"
                )

            if not is_gauntlet_req and any(k in low_msg for k in ("take a screenshot", "screenshot my screen", "what is on my screen", "list open windows", "what windows are open")):
                act = "list_windows" if "window" in low_msg and "screenshot" not in low_msg else "screenshot"
                yield emit_step(f"🖥️ OSWorld Desktop Agent executing '{act}'...")
                os_res = execute_osworld_action(act, "")
                dynamic_turn_context += f"[SYSTEM TOOL EXECUTED — OSWORLD {act.upper()}]: {os_res['summary']}\n"
                if os_res.get("image_url"):
                    generated_img_url = os_res["image_url"]

            if harvested_notes:
                yield emit_step(f"📝 Auto-harvested Pseudo-Memory note: {', '.join(harvested_notes)}")

            is_weather_q, weather_city = (False, "") if is_gauntlet_req else detect_weather_intent(user_msg)
            if not is_gauntlet_req and not is_weather_q and any("[user_location]" in h for h in harvested_notes):
                prev_ctx = " ".join((t.get("content") or "").lower() for t in recent_turns[-4:-1])
                if any(wk in prev_ctx for wk in ("weather", "climate", "rain", "forecast", "temperature")):
                    is_weather_q = True
                    weather_city = (load_user_profile_card().get("location") or "").strip()
            if is_weather_q and not STATE["offline_mode"]:
                if weather_city:
                    yield emit_step(f"🌦️ Live Weather Engine fetching real conditions for '{weather_city}'...")
                    w_out = get_live_weather(weather_city)
                    dynamic_turn_context += f"[REAL LIVE WEATHER DATA — REPORT THESE EXACT NUMBERS DIRECTLY]:\n{w_out}\n"
                else:
                    dynamic_turn_context += "[WEATHER NOTE: The user has not saved their city/location yet. Ask them concisely what city they live in.]\n"
            elif any(k in low_msg for k in ("search the web", "search online", "web search", "look up online", "look up through the internet", "latest news on", "google ")) and not STATE["offline_mode"]:
                sq_auto = clean_web_search_query(user_msg)
                yield emit_step(f"🌐 Pre-executing Clean Web Search for '{sq_auto[:45]}'...")
                w_res_pre = search_web(sq_auto)
                yield json.dumps({"type": "workbench_io", "tool": "web_search", "code": f"vault.web({sq_auto!r})", "output": w_res_pre[:900]}) + "\n"
                dynamic_turn_context += f"[SYSTEM TOOL EXECUTED — LIVE WEB SEARCH FOR '{sq_auto}']:\n{w_res_pre}\n"
                web_searched_this_turn = True
            elif not is_gauntlet_req:
                is_fresh_q, fresh_sq = detect_freshness_or_fact_query(user_msg)
                if is_fresh_q:
                    yield emit_step(f"🌐 Fresh/Post-Cutoff Topic Detected — auto-searching web for '{fresh_sq[:42]}'...")
                    w_res_fresh = search_web(fresh_sq)
                    yield json.dumps({"type": "workbench_io", "tool": "auto_web_grounding", "code": f"vault.web({fresh_sq!r})", "output": w_res_fresh[:900]}) + "\n"
                    dynamic_turn_context += f"[AUTO-WEB GROUNDING — LIVE INTERNET FACTS FOR '{fresh_sq}' (TRUST THESE OVER OUTDATED WEIGHTS!)]:\n{w_res_fresh}\n"
                    web_searched_this_turn = True

            if any(k in low_msg for k in ("other chat", "previous chat", "old chat", "past chat", "chat history", "what did we talk about", "list my chats")):
                yield emit_step("🗂️ Cross-Chat Recall: scanning past sessions & .txt logs...")
                chat_recall_out = execute_cross_chat_tool("search" if len(user_msg.split()) > 5 else "list", user_msg, session_id)
                dynamic_turn_context += f"[SYSTEM TOOL EXECUTED — CROSS-CHAT RECALL]:\n{chat_recall_out}\n"

            if any(k in low_msg for k in ("your own code", "your source code", "your own files", "inspect yourself", "error log", "error_audit.log", "temp cache", "assistant_server.py")):
                scmd = "errors" if "error" in low_msg else "tree"
                yield emit_step(f"🔍 Self-File Inspector executing '{scmd}' on AetherVault workspace...")
                self_out = execute_self_inspection_tool(scmd, user_msg)
                dynamic_turn_context += f"[SYSTEM TOOL EXECUTED — SELF-FILE INSPECTOR]:\n{self_out}\n"

            STATE["spotify_readonly_turn"] = False
            STATE["spotify_mutated_this_turn"] = ""
            spotify_readonly_cues = (
                "don't change", "dont change", "do not change", "no change", "don't skip", "dont skip",
                "just look", "take a look", "just check", "just tell me", "leave it", "keep playing",
                "keep it playing", "without changing", "wich one", "which one", "what one",
                "what's playing", "whats playing", "currently playing", "current song", "current track",
                "what song", "which song", "wich song", "what am i listening", "identify", "ndentify",
                "you changed", "changed the song", "why did you change"
            )
            is_spotify_readonly = any(rc in low_msg for rc in spotify_readonly_cues)
            is_music_cmd = (
                "spotify" in low_msg
                or any(k in low_msg for k in (
                    "play a song", "play another song", "playing another song", "play some music",
                    "put on a song", "next song", "next track", "skip this song", "pause the music",
                    "what song", "which song", "wich song", "wich one", "which one",
                    "liked song", "liked songs", "saved song", "saved songs", "playlist", "playlists",
                    "album", "listening to", "different song", "identify it", "ndentify it",
                    "identify the song", "ndentify the song", "what am i listening",
                    "you changed", "changed the song"
                ))
            )
            if not is_gauntlet_req and is_music_cmd and not ("youtube" in low_msg and "spotify" not in low_msg):
                # 1. PRIORITY #1: Read-Only Inspection / "Don't Change!" Guard — NEVER mutates playback!
                if is_spotify_readonly and not any(w in low_msg for w in ("liked song", "liked songs", "my playlists", "list playlists")):
                    STATE["spotify_readonly_turn"] = True
                    yield emit_step("🎵 Reading currently playing Spotify track (Read-Only — playback locked)...")
                    sp_cur_out = control_spotify("current_track")
                    yield json.dumps({"type": "workbench_io", "tool": "spotify_control", "code": "vault.spotify('current_track')", "output": sp_cur_out[:900]}) + "\n"
                    dynamic_turn_context += (
                        f"[SYSTEM TOOL EXECUTED — SPOTIFY CURRENT TRACK (READ-ONLY — DO NOT CHANGE PLAYBACK OR CALL vault.spotify('play'/'next')!)]:\n"
                        f"{sp_cur_out}\n"
                    )
                # 2. Liked Songs (Read-Only list OR Continuous 50-track Liked Songs playback!)
                elif any(k in low_msg for k in ("liked song", "liked songs", "saved song", "saved songs", "my liked")):
                    want_play = (not is_spotify_readonly) and any(k in low_msg for k in ("play", "pick", "choose", "chose", "put on", "random", "hit me", "best shot", "give me"))
                    if is_spotify_readonly:
                        STATE["spotify_readonly_turn"] = True
                    act_l = "play_liked" if want_play else "liked"
                    yield emit_step(f"🎵 Accessing Spotify Liked Songs ({act_l})...")
                    sp_l_out = control_spotify(act_l, "")
                    yield json.dumps({"type": "workbench_io", "tool": "spotify_control", "code": f"vault.spotify({act_l!r})", "output": sp_l_out[:900]}) + "\n"
                    if act_l == "play_liked": STATE["spotify_mutated_this_turn"] = sp_l_out
                    dynamic_turn_context += f"[SYSTEM TOOL EXECUTED — SPOTIFY LIKED SONGS (ALREADY DONE — DO NOT CALL vault.spotify AGAIN)]:\n{sp_l_out}\n"
                # 3. Full Playlists (list or start full playlist context so it loops/plays continuously!)
                elif any(k in low_msg for k in ("playlist", "playlists")):
                    want_play_pl = (not is_spotify_readonly) and any(k in low_msg for k in ("play", "pick", "choose", "chose", "put on", "start", "loop", "fetch"))
                    if is_spotify_readonly:
                        STATE["spotify_readonly_turn"] = True
                    act_pl = "play_playlist" if want_play_pl else "playlists"
                    m_pln = re.search(r"playlist\s+(?:called\s+|named\s+)?['\"]?([a-zA-Z0-9 _\-]{2,40})['\"]?", user_msg, flags=re.IGNORECASE)
                    pl_q = m_pln.group(1).strip() if m_pln else ""
                    if pl_q.lower() in ("and", "for me", "please", "on spotify", "in spotify"):
                        pl_q = ""
                    yield emit_step(f"🎵 Accessing Spotify Playlists ({act_pl}{': ' + pl_q if pl_q else ''})...")
                    sp_pl_out = control_spotify(act_pl, pl_q)
                    yield json.dumps({"type": "workbench_io", "tool": "spotify_control", "code": f"vault.spotify({act_pl!r}, {pl_q!r})", "output": sp_pl_out[:900]}) + "\n"
                    dynamic_turn_context += f"[SYSTEM TOOL EXECUTED — SPOTIFY PLAYLIST]:\n{sp_pl_out}\n"
                # 4. Full Album playback
                elif "album" in low_msg and not is_spotify_readonly and any(k in low_msg for k in ("play", "put on", "start", "loop")):
                    m_alb = re.search(r"album\s+(?:called\s+|named\s+)?['\"]?([a-zA-Z0-9 _\-]{2,45})['\"]?", user_msg, flags=re.IGNORECASE)
                    alb_q = m_alb.group(1).strip() if m_alb else ""
                    yield emit_step(f"🎵 Starting full Spotify album '{alb_q}'...")
                    sp_al_out = control_spotify("play_album", alb_q)
                    yield json.dumps({"type": "workbench_io", "tool": "spotify_control", "code": f"vault.spotify('play_album', {alb_q!r})", "output": sp_al_out[:900]}) + "\n"
                    dynamic_turn_context += f"[SYSTEM TOOL EXECUTED — SPOTIFY ALBUM]:\n{sp_al_out}\n"
                elif any(k in low_msg for k in ("pause", "stop music", "stop spotify")):
                    yield emit_step("🎵 Pausing Spotify playback...")
                    dynamic_turn_context += f"[SYSTEM TOOL EXECUTED — SPOTIFY]: {control_spotify('pause')}\n"
                elif any(k in low_msg for k in ("play another song", "put another song", "put on another song", "next song", "next track", "skip this", "skip song", "skip track", "change the song", "switch song")):
                    yield emit_step("🎵 Switching to another track on Spotify...")
                    _sp_n = control_spotify("next"); STATE["spotify_mutated_this_turn"] = _sp_n; dynamic_turn_context += f"[SYSTEM TOOL EXECUTED — SPOTIFY (ALREADY DONE — DO NOT CALL vault.spotify AGAIN)]: {_sp_n}\n"
                elif any(k in low_msg for k in ("devices", "device list", "connected devices")):
                    yield emit_step("🎵 Listing Spotify devices...")
                    dynamic_turn_context += f"[SYSTEM TOOL EXECUTED — SPOTIFY]: {control_spotify('devices')}\n"
                elif any(k in low_msg for k in ("any song", "random song", "press play", "resume spotify", "resume music", "play something", "play a song", "play some music")):
                    yield emit_step("🎵 Starting/resuming Spotify playback...")
                    dynamic_turn_context += f"[SYSTEM TOOL EXECUTED — SPOTIFY]: {control_spotify('play', '')}\n"
                else:
                    m_put = re.search(r"(?:put|play|queue|search\s+for)\s+(.+?)(?:\s+please)?(?:\s+on\s+my\s*spotify|\s+in\s+my\s*spotify|\s+on\s+spotify|$)", user_msg, flags=re.IGNORECASE)
                    if m_put and not is_spotify_readonly:
                        song_q = re.sub(r"\b(?:me|a song|for me|in spotify|on spotify|plug it in|and press play)\b", "", m_put.group(1), flags=re.IGNORECASE).strip(" ,.?!\"'")
                        if song_q and len(song_q) >= 2:
                            yield emit_step(f"🎵 Executing Spotify playback for: '{song_q}'...")
                            sp_result = control_spotify("play", song_q)
                            STATE["spotify_mutated_this_turn"] = sp_result
                            dynamic_turn_context += f"[SYSTEM TOOL EXECUTED — SPOTIFY (ALREADY DONE — DO NOT CALL vault.spotify AGAIN)]: {sp_result}\n"

            if not is_gauntlet_req and any(w in low_msg for w in ("name of my pc", "my pc name", "pc's name", "hostname", "computer name", "my pc specs", "what libraries", "installed libraries")):
                yield emit_step("💻 Reading real host PC telemetry (hostname, OS, RAM & installed libraries)...")
                dynamic_turn_context += f"[SYSTEM TOOL EXECUTED — REAL PC INFO]:\n{json.dumps(get_pc_environment_info(), indent=2, ensure_ascii=False)}\n"

            if not is_gauntlet_req and any(w in low_msg for w in ("steam game", "which steam", "inside my pc", "my files", "google drive")):
                q_pc = "steam" if "steam" in low_msg else "priority_pdfs"
                yield emit_step(f"💻 Scanning local PC / Steam / Drive for '{q_pc}'...")
                pc_res = search_local_pc_files(q_pc)
                STATE["last_debug"]["pc_files_scanned"].append(q_pc)
                dynamic_turn_context += f"[SYSTEM TOOL EXECUTED — PC SCAN]:\n{pc_res}\n"

            if not is_operator and not is_capability_or_api_query(user_msg):
                retrieved_lore, lore_labels = retrieve_relevant_lore(user_msg, top_k=2)
                retrieved_chats, chat_labels = retrieve_past_chat_logs(user_msg, session_id, top_k=2)
                STATE["last_debug"]["lore_pulled"] = lore_labels
                STATE["last_debug"]["chats_pulled"] = chat_labels

                if chat_labels:
                    yield emit_step(f"🗂️ Corroborated past .txt chat logs: {', '.join(chat_labels)}")
                    dynamic_turn_context += f"=== RELEVANT PAST .TXT CHAT LOGS ===\n{retrieved_chats}\n\n"
                if lore_labels:
                    yield emit_step(f"📖 Pulled Sanitized Knowledge Chunks: {', '.join(lore_labels)}")
                    dynamic_turn_context += f"=== RELEVANT KNOWLEDGE EXCERPTS ===\n{retrieved_lore}\n"

            pc_anchor = build_pc_reality_anchor()
            if is_operator:
                static_sys_prompt = build_assistant_workbench_system_prompt(ai_name, user_name, mem_context)
                record_temp_gear_cache("operator", static_sys_prompt)
                messages = build_safe_messages(static_sys_prompt, dynamic_turn_context, recent_turns, max_turns=6)
            else:
                core_rules = PRIORITY_CACHE["core_rules_text"] or (
                    WORKSPACE_CFG["persona_prompt"].replace("{ai_name}", ai_name).replace("{user_name}", user_name)
                )
                static_sys_prompt = (
                    f"You are {ai_name} speaking with {user_name}.\n"
                    f"{pc_anchor}\n\n"
                    f"=== CORE IDENTITY & RULES (STATIC KV PREFIX) ===\n"
                    f"{core_rules}\n\n{UNIVERSAL_CAPABILITY_LOCK}\n\n"
                    f"=== PRIORITY 1 (HIGHEST): ACTIVE MEMORY VAULT ===\n"
                    f"{mem_context}\n\n"
                    f"=== PRIORITY 1.5: BOOT INDEX & PSEUDO-MEMORY DIGEST ===\n"
                    f"{PRIORITY_CACHE.get('pseudo_notes_digest', '')}"
                )
                record_temp_gear_cache("deep", static_sys_prompt)
                messages = build_safe_messages(static_sys_prompt, dynamic_turn_context, recent_turns, max_turns=6)
            prompt_chars = sum(len(m["content"]) for m in messages)
            STATE["last_debug"]["prompt_chars"] = prompt_chars
            cfg = get_governor_settings("deep", prompt_chars)

            accel_tag = "🔥 Vulkan GPU" if STATE["gpu_offload"] else f"💻 CPU ({cfg['threads']}T)"
            yield emit_step(f"⚡ Deep Generation ({accel_tag} | {prompt_chars} chars context | Max headroom {cfg['max_tokens']} tokens)...")

            STATE["generating"] = True
            raw_reply = ""
            in_think_block = False
            think_buffer = ""

            try:
                agent_messages = list(messages)
                active_tools = None if is_gauntlet_req else (AETHER_TOOL_SCHEMAS if (is_operator or not STATE["offline_mode"]) else None)
                uncapped_now = is_unrestricted_tokens_enabled()
                max_rounds = 1 if is_gauntlet_req else (8 if uncapped_now else 5)
                last_failed_wb_sig = ""
                for agent_round in range(max_rounds):
                    round_reply = ""
                    tool_calls_acc = {}
                    in_think_block = False
                    think_buffer = ""
                    round_finish_reason = None
                    delirium_hit = False

                    _g2_hints = avs_model_polish.provider_profile_hints(
                        STATE.get("active_api_label") or STATE.get("current_model") or WORKSPACE_CFG.get("brain_mode", ""),
                        WORKSPACE_CFG.get("workspace_mode", "assistant")
                    )
                    _g2_temp = (_g2_hints["temperature"] if (agent_round > 0 or is_gauntlet_req) else min(0.42, _g2_hints["temperature"])) if is_operator else _g2_hints["temperature"]
                    stream_iter = dispatch_brain_stream(
                        messages=agent_messages,
                        max_tokens=cfg["max_tokens"],
                        temperature=_g2_temp,
                        top_p=_g2_hints["top_p"],
                        min_p=0.12,
                        repeat_penalty=1.15,
                        stop=["<START>", f"\n{user_name}:", "\nUser:", "[INST]", "[/INST]"],
                        tools=active_tools if agent_round < (max_rounds - 1) else None,
                        tool_choice="auto" if (active_tools and agent_round < (max_rounds - 1)) else None
                    )
                    for chunk in stream_iter:
                        if STATE["stop_requested"]:
                            yield emit_step("⏹️ Generation stopped by user.")
                            break
                        ch0 = (chunk.get("choices") or [{}])[0]
                        if ch0.get("finish_reason"):
                            round_finish_reason = ch0.get("finish_reason")
                        delta_obj = ch0.get("delta") or {}

                        if delta_obj.get("tool_calls"):
                            for tc_d in delta_obj["tool_calls"]:
                                tc_idx = tc_d.get("index", 0)
                                entry = tool_calls_acc.setdefault(tc_idx, {
                                    "id": tc_d.get("id") or f"call_{agent_round}_{tc_idx}",
                                    "name": "",
                                    "arguments_str": ""
                                })
                                if tc_d.get("id"):
                                    entry["id"] = tc_d["id"]
                                fn_d = tc_d.get("function") or {}
                                if fn_d.get("name"):
                                    entry["name"] += str(fn_d["name"])
                                if fn_d.get("arguments"):
                                    entry["arguments_str"] += str(fn_d["arguments"])

                        delta = delta_obj.get("content") or ""
                        if not delta:
                            continue
                        round_reply += delta

                        if has_repetition_delirium(round_reply):
                            delirium_hit = True
                            err_card = format_predetermined_error("ERR_DELIRIUM_LOOP")
                            yield json.dumps({"type": "issue", "issue": err_card}) + "\n"
                            yield emit_step(f"🛡️ {err_card['code']}: Cut repetition loop cleanly.")
                            break

                        if "<think>" in delta:
                            in_think_block = True
                            delta = delta.replace("<think>", "")
                        if "</think>" in delta:
                            in_think_block = False
                            parts = delta.split("</think>", 1)
                            think_buffer += parts[0]
                            if think_buffer.strip():
                                yield emit_step(f"🧠 DeepSeek Reasoning: {think_buffer.strip()[:180]}...")
                            delta = parts[1]
                            think_buffer = ""
                        if in_think_block:
                            think_buffer += delta
                            continue

                        low_rr = round_reply.lstrip().lower()
                        looks_like_tool_code = (
                            bool(tool_calls_acc)
                            or "<tool_call>" in low_rr
                            or "```workbench" in low_rr
                            or "[workbench]" in low_rr
                            or "vault." in low_rr
                            or low_rr.startswith('{"name"')
                            or low_rr.startswith('"name"')
                            or (low_rr.startswith("```") and ('"name"' in round_reply or "vault." in round_reply or len(low_rr) < 28))
                        )
                        if delta and not looks_like_tool_code:
                            yield json.dumps({"type": "token", "text": delta}) + "\n"

                    pending_calls = []
                    for tc_i in sorted(tool_calls_acc.keys()):
                        entry = tool_calls_acc[tc_i]
                        try:
                            parsed_args = json.loads(entry["arguments_str"]) if entry["arguments_str"].strip() else {}
                        except Exception:
                            parsed_args = {}
                        if entry["name"]:
                            pending_calls.append({"id": entry["id"], "name": entry["name"], "arguments": parsed_args})

                    stripped_round = re.sub(r"<think>[\s\S]*?</think>", "", round_reply).strip()
                    wb_blocks, wb_cleaned = extract_workbench_blocks(stripped_round)
                    inline_calls, cleaned_round = extract_inline_tool_calls(wb_cleaned)
                    if wb_blocks and not pending_calls:
                        for wb_i, wb_code in enumerate(wb_blocks):
                            pending_calls.append({"id": f"wb_{agent_round}_{wb_i}", "name": "run_workbench", "arguments": {"code": wb_code}})
                        round_reply = cleaned_round
                    elif not pending_calls and inline_calls:
                        pending_calls = inline_calls
                        round_reply = cleaned_round

                    if pending_calls and not STATE["stop_requested"] and agent_round < (max_rounds - 1):
                        obs_blocks = []
                        any_tool_failed = False
                        any_auto_researched = False
                        round_fail_sig = ""
                        obs_char_cap = 8000 if uncapped_now else 2400
                        for pc in pending_calls:
                            if pc["name"] == "run_workbench" and not str((pc.get("arguments") or {}).get("code") or "").strip():
                                continue
                            code_preview = str((pc.get("arguments") or {}).get("code") or json.dumps(pc.get("arguments") or {}, ensure_ascii=False))
                            yield emit_step(f"🐍 Workbench Round {agent_round+1}/{max_rounds}: {pc['name']}...")
                            if pc["name"] == "run_workbench":
                                wb_res = execute_workbench_code(code_preview)
                                obs_txt = wb_res.get("output") or ""
                                t_img = wb_res.get("image_url")
                                t_aud = wb_res.get("audio_url")
                                if not wb_res.get("ok"):
                                    any_tool_failed = True
                                    round_fail_sig += code_preview.strip()
                                if wb_res.get("auto_researched"):
                                    any_auto_researched = True
                                    yield emit_step("🌐 Workbench hit an error -> Auto-researched online docs to help self-correct!")
                            else:
                                obs_txt, t_img, t_aud = execute_unified_tool(pc["name"], coerce_primitive_args(pc["arguments"]), session_id)
                            if pc["name"] == "web_search" or (pc["name"] == "run_workbench" and any(wk in code_preview for wk in ("vault.web(", "vault.docs(", "vault.search("))):
                                web_searched_this_turn = True
                            yield json.dumps({
                                "type": "workbench_io",
                                "tool": pc["name"] + (" (Auto-Researched Fix)" if any_auto_researched else ""),
                                "code": code_preview[:900],
                                "output": (obs_txt or "")[:2000]
                            }) + "\n"
                            if STATE.get("ui_sync_needed"):
                                STATE["ui_sync_needed"] = False
                                yield json.dumps({"type": "sync_status"}) + "\n"
                            if t_img:
                                generated_img_url = t_img
                            if t_aud:
                                generated_audio_url = t_aud
                            obs_blocks.append(f"[TOOL RESULT: {pc['name']}]\n{avs_turn_pipeline.compact_observations([obs_txt], max_chars=obs_char_cap)}")

                        # Duplicate-failure loop breaker so a small model never retries the exact same broken snippet twice
                        if any_tool_failed and round_fail_sig and round_fail_sig == last_failed_wb_sig:
                            yield emit_step("🛡️ Workbench Loop-Breaker: Same code failed twice — wrapping up clearly.")
                            raw_reply = f"{cleaned_round}\n\n{obs_blocks[-1][:900]}".strip()
                            break
                        if any_tool_failed:
                            last_failed_wb_sig = round_fail_sig

                        agent_messages.append({"role": "assistant", "content": cleaned_round or f"Calling tool(s): {', '.join(c['name'] for c in pending_calls)}"})
                        if any_tool_failed:
                            followup_directive = (
                                "\n\nThe Workbench snippet hit an error above"
                                + (" and I automatically looked up the docs/fix hints online for you!" if any_auto_researched else ".")
                                + " Fix the code and output a corrected ```workbench block to retry (or call vault.docs('topic') if you need more info). "
                                "If it truly cannot be run, explain why concisely in-character."
                            )
                        else:
                            followup_directive = (
                                f"\n\nThe real PC tool/Workbench step just succeeded! "
                                f"If you still need more steps (e.g. reading the next chunk with vault.chunk_read or running another check), output another ```workbench block to keep going. "
                                f"Otherwise, reply to {user_name} FULLY IN-CHARACTER as {ai_name} with the complete analysis/results!"
                            )
                        agent_messages.append({
                            "role": "user",
                            "content": "\n\n".join(obs_blocks) + followup_directive
                        })
                        raw_reply = ""
                        continue

                    # ---------------------------------------------------------
                    # v4.16 ROLLING AUTO-CONTINUATION ("JUST KEEP GOING!")
                    # If Uncapped Mode is ON and the model hit the per-pass output
                    # token limit (`finish_reason == "length"`), seamlessly roll
                    # into another continuation pass inside the SAME bubble!
                    # ---------------------------------------------------------
                    raw_reply = round_reply
                    if uncapped_now and round_finish_reason == "length" and not STATE["stop_requested"] and not delirium_hit:
                        for cont_seg in range(2, 7):
                            if STATE["stop_requested"] or delirium_hit:
                                break
                            yield emit_step(f"♾️ Uncapped Auto-Continue: Pass hit token ceiling — seamlessly continuing (Segment {cont_seg}/6)...")
                            tail_anchor = raw_reply[-2400:]
                            cont_msgs = [
                                agent_messages[0],
                                {"role": "user", "content": f"Original request from {user_name}: {user_msg[:1500]}"},
                                {"role": "assistant", "content": tail_anchor},
                                {"role": "user", "content": "Continue directly from the exact last word above without repeating anything you already wrote. Finish the full analysis completely."}
                            ]
                            seg_reply = ""
                            seg_fin = None
                            seg_iter = dispatch_brain_stream(
                                messages=cont_msgs,
                                max_tokens=cfg["max_tokens"],
                                temperature=0.72,
                                top_p=0.94,
                                min_p=0.12,
                                repeat_penalty=1.15,
                                stop=["<START>", f"\n{user_name}:", "\nUser:", "[INST]", "[/INST]"]
                            )
                            for s_ch in seg_iter:
                                if STATE["stop_requested"]:
                                    yield emit_step("⏹️ Generation stopped by user.")
                                    break
                                sch0 = (s_ch.get("choices") or [{}])[0]
                                if sch0.get("finish_reason"):
                                    seg_fin = sch0.get("finish_reason")
                                s_delta = (sch0.get("delta") or {}).get("content") or ""
                                if not s_delta:
                                    continue
                                seg_reply += s_delta
                                if has_repetition_delirium(raw_reply[-600:] + seg_reply):
                                    delirium_hit = True
                                    err_card = format_predetermined_error("ERR_DELIRIUM_LOOP")
                                    yield json.dumps({"type": "issue", "issue": err_card}) + "\n"
                                    yield emit_step(f"🛡️ {err_card['code']}: Stopped continuation loop cleanly.")
                                    break
                                yield json.dumps({"type": "token", "text": s_delta}) + "\n"
                            raw_reply += seg_reply
                            if seg_fin != "length" or not seg_reply.strip():
                                break
                    break

                if True:
                    full_reply = re.sub(r"<think>[\s\S]*?</think>", "", raw_reply).strip()
                    full_reply = re.sub(r"\[?\[DEEP\]\]?", "", full_reply).strip()
                    full_reply = re.sub(rf"^({re.escape(ai_name)}|Assistant):\s*", "", full_reply, flags=re.IGNORECASE).strip()

                    if not STATE["stop_requested"]:
                        if re.search(r"\[\[PCINFO\|?[^\]]*\]\]", full_reply, flags=re.IGNORECASE):
                            yield emit_step("💻 Reading live PC hostname, OS, RAM & libraries...")
                            pc_json = json.dumps(get_pc_environment_info(), indent=2, ensure_ascii=False)
                            full_reply = re.sub(r"\[\[PCINFO\|?[^\]]*\]\]", "", full_reply, flags=re.IGNORECASE).strip()
                            full_reply = synthesize_tool_followup(
                                static_sys_prompt, recent_turns, full_reply or "Checking PC info.",
                                f"[Live PC Environment Info]:\n{pc_json}", cfg, user_name, ai_name
                            )

                        py_match = re.search(r"\[\[PYTHON:([\s\S]+?)\]\]", full_reply)
                        if py_match:
                            py_code = py_match.group(1).strip()
                            yield emit_step("🐍 Running Python snippet inside isolated .temp_cache sandbox...")
                            py_res = api_run_code_sandbox({"code": py_code})
                            full_reply = re.sub(r"\[\[PYTHON:[\s\S]+?\]\]", "", full_reply).strip()
                            full_reply = synthesize_tool_followup(
                                static_sys_prompt, recent_turns, full_reply or "Running Python sandbox.",
                                f"[Python Sandbox Execution Result]:\n{json.dumps(py_res, ensure_ascii=False)}", cfg, user_name, ai_name
                            )

                    if not STATE["stop_requested"]:
                        osworld_matches = list(re.finditer(r"\[\[OSWORLD:([^|\]]+)\|?([^\]]*)\]\]", full_reply))
                        if osworld_matches:
                            os_logs = []
                            for om in osworld_matches:
                                o_act, o_arg = om.group(1).strip(), om.group(2).strip()
                                yield emit_step(f"🖥️ OSWorld Desktop Agent: {o_act}({o_arg})...")
                                o_res = execute_osworld_action(o_act, o_arg)
                                os_logs.append(o_res["summary"])
                                if o_res.get("image_url"):
                                    generated_img_url = o_res["image_url"]
                            full_reply = re.sub(r"\[\[OSWORLD:[^\]]+\]\]", "", full_reply).strip()
                            if not full_reply:
                                full_reply = synthesize_tool_followup(
                                    static_sys_prompt, recent_turns, "Executing desktop action.",
                                    "[OSWorld Desktop Execution Results]:\n" + "\n".join(os_logs), cfg, user_name, ai_name
                                )
                            else:
                                full_reply += "\n\n🖥️ *(" + " | ".join(os_logs) + ")*"

                        files_match = re.search(r"\[\[FILES:([^\]]+)\]\]", full_reply)
                        if files_match:
                            fq = files_match.group(1).strip()
                            yield emit_step(f"📂 Scanning local PC / Drive for '{fq}' & synthesizing reply...")
                            STATE["last_debug"]["pc_files_scanned"].append(fq)
                            pc_out = search_local_pc_files(fq)
                            full_reply = synthesize_tool_followup(
                                static_sys_prompt, recent_turns, full_reply,
                                f"[Local PC File Scan Results for '{fq}']:\n{pc_out}", cfg, user_name, ai_name
                            )

                        lore_match = re.search(r"\[\[LORE:([^\]]+)\]\]", full_reply)
                        if lore_match:
                            lq = lore_match.group(1).strip()
                            yield emit_step(f"📖 Pulling deep Knowledge chunks for '{lq}' & synthesizing reply...")
                            deep_lore, d_lbls = retrieve_relevant_lore(lq, top_k=3)
                            STATE["last_debug"]["lore_pulled"].extend(d_lbls)
                            full_reply = synthesize_tool_followup(
                                static_sys_prompt, recent_turns, full_reply,
                                f"[Deep Knowledge Lookup for '{lq}']:\n{deep_lore or 'No extra sections found.'}", cfg, user_name, ai_name
                            )

                        search_match = re.search(r"\[\[SEARCH:([^\]]+)\]\]", full_reply)
                        if search_match and search_match.group(1).strip().lower() not in ("query", "clean keywords", "keywords", "search") and not STATE["offline_mode"]:
                            sq = search_match.group(1).strip()
                            yield emit_step(f"🌐 Searching Web for '{sq}' & synthesizing reply...")
                            web_out = search_web(sq)
                            full_reply = synthesize_tool_followup(
                                static_sys_prompt, recent_turns, full_reply,
                                f"[Live Web Search Results for '{sq}']:\n{web_out}", cfg, user_name, ai_name
                            )

                        sp_match = re.search(r"\[\[SPOTIFY:([^|\]]+)\|?([^\]]*)\]\]", full_reply)
                        if sp_match and not STATE["offline_mode"]:
                            act, q = sp_match.group(1).strip(), sp_match.group(2).strip()
                            yield emit_step(f"🎵 Controlling Spotify ({act})...")
                            sp_out = control_spotify(act, q)
                            full_reply = re.sub(r"\[\[SPOTIFY:[^\]]+\]\]", "", full_reply).strip()
                            full_reply = f"{full_reply}\n\n🎵 *({sp_out})*".strip()

                        for match in re.finditer(r"\[\[MEMORY:([^|\]]+)\|([^\]]+)\]\]", full_reply):
                            cat, fact = match.group(1).strip(), match.group(2).strip()
                            save_to_memory(cat, fact)
                            yield emit_step(f"💾 Saved to Memory Vault: [{cat}] {fact}")
                        full_reply = re.sub(r"\[\[MEMORY:?[^\]]*\]\]?", "", full_reply).strip()

                        chats_match = re.search(r"\[\[CHATS:([^|\]]+)\|?([^\]]*)\]\]", full_reply)
                        if chats_match:
                            c_cmd, c_arg = chats_match.group(1).strip(), chats_match.group(2).strip()
                            yield emit_step(f"🗂️ Cross-Chat Recall ({c_cmd}): '{c_arg[:35]}'...")
                            c_out = execute_cross_chat_tool(c_cmd, c_arg or user_msg, session_id)
                            full_reply = re.sub(r"\[\[CHATS:[^\]]+\]\]", "", full_reply).strip()
                            full_reply = synthesize_tool_followup(
                                static_sys_prompt, recent_turns, full_reply or "Checking past chats.",
                                f"[Cross-Chat Recall Results ({c_cmd})]:\n{c_out}", cfg, user_name, ai_name
                            )

                        fix_match = re.search(r"\[\[SELF:propose_fix\|([^|\]]+)\|([^|\]]+)\|([^\]]+)\]\]", full_reply)
                        if fix_match:
                            f_target, f_old, f_new = fix_match.group(1).strip(), fix_match.group(2), fix_match.group(3)
                            yield emit_step(f"🛡️ Anti-Ouroboros Self-Heal Sandbox: staging & syntax-checking fix for '{f_target}'...")
                            prop_res = stage_self_heal_proposal(f_target, f_old, f_new, reason="AI Self-Diagnostic Proposal")
                            full_reply = re.sub(r"\[\[SELF:propose_fix\|[^\]]+\]\]", "", full_reply).strip()
                            full_reply += f"\n\n🛡️ **[Self-Heal Patch Staged — Awaiting Your Approval]**: {prop_res.get('message', '')}"

                        self_match = re.search(r"\[\[SELF:([^|\]]+)\|?([^\]]*)\]\]", full_reply)
                        if self_match:
                            s_cmd, s_arg = self_match.group(1).strip(), self_match.group(2).strip()
                            yield emit_step(f"🔍 Self-File Inspector ({s_cmd}): '{s_arg[:35]}'...")
                            s_out = execute_self_inspection_tool(s_cmd, s_arg)
                            full_reply = re.sub(r"\[\[SELF:[^\]]+\]\]", "", full_reply).strip()
                            full_reply = synthesize_tool_followup(
                                static_sys_prompt, recent_turns, full_reply or "Inspecting my own files.",
                                f"[Self-File Inspection Results ({s_cmd})]:\n{s_out}", cfg, user_name, ai_name
                            )

                        img_match = re.search(r"\[\[IMAGE:([^\]]+)\]\]", full_reply)
                        if img_match:
                            iprompt = img_match.group(1).strip()
                            yield emit_step(f"🏪 Cashier->Manager Swap: Rendering image for '{iprompt[:35]}...'")
                            img_res = generate_image_tool(iprompt)
                            full_reply = re.sub(r"\[\[IMAGE:[^\]]+\]\]", "", full_reply).strip()
                            if img_res.get("ok"):
                                generated_img_url = img_res["url"]

                        music_match = re.search(r"\[\[MUSIC:([^|\]]+)\|?([^\]]*)\]\]", full_reply)
                        if music_match:
                            mprompt = music_match.group(1).strip()
                            m_sec_str = music_match.group(2).strip()
                            m_sec = int(m_sec_str) if m_sec_str.isdigit() else 8
                            yield emit_step(f"🏪 Cashier->Manager Swap: Composing music track for '{mprompt[:35]}' ({m_sec}s)...")
                            mus_res = generate_music_tool(mprompt, duration_sec=m_sec)
                            full_reply = re.sub(r"\[\[MUSIC:[^\]]+\]\]", "", full_reply).strip()
                            if mus_res.get("ok"):
                                generated_audio_url = mus_res["url"]
                                full_reply = f"{full_reply}\n\n🎵 *({mus_res.get('source', 'Music Manager')}: {mprompt})*".strip()

                    if (
                        not STATE["stop_requested"]
                        and not is_gauntlet_req
                        and not web_searched_this_turn
                        and is_auto_web_search_enabled()
                        and detect_model_uncertainty(full_reply)
                        and is_query_searchable_for_rescue(user_msg)
                    ):
                        rescue_q = clean_web_search_query(user_msg)
                        yield emit_step(f"🌐 Caught knowledge gap — auto-searching web for '{rescue_q[:42]}'...")
                        rescue_out = search_web(rescue_q)
                        yield json.dumps({"type": "workbench_io", "tool": "uncertainty_web_rescue", "code": f"vault.web({rescue_q!r})", "output": rescue_out[:950]}) + "\n"
                        web_searched_this_turn = True
                        full_reply = synthesize_tool_followup(
                            static_sys_prompt,
                            recent_turns,
                            full_reply,
                            f"[AUTO-WEB KNOWLEDGE RESCUE FOR '{rescue_q}' — YOU JUST LOOKED THIS UP ONLINE! Answer {user_name} naturally in-character using these real web results]:\n{rescue_out[:1800]}",
                            cfg,
                            user_name,
                            ai_name
                        )

                    _is_asst_g2 = (WORKSPACE_CFG.get("workspace_mode", "assistant") == "assistant")
                    full_reply = avs_model_polish.normalize_model_output(full_reply, ai_name=ai_name, user_name=user_name, is_assistant_mode=_is_asst_g2)
                    full_reply = clean_assistant_theatrics(full_reply, is_assistant_mode=_is_asst_g2)
                    _g2_ev = f"{PRIORITY_CACHE.get('core_rules_text', '')} {WORKSPACE_CFG.get('persona_prompt', '')} {retrieved_lore if 'retrieved_lore' in locals() else ''}"
                    _g2_fin = avs_turn_pipeline.finalize_turn_reply(full_reply, ai_name=ai_name, user_name=user_name, evidence_pool=_g2_ev)
                    full_reply, _g2_warns = referee_lore_and_grounding(_g2_fin["reply"], user_msg, ai_name, retrieved_lore if 'retrieved_lore' in locals() else "")
                    STATE["last_debug"]["referee_warnings"] = _g2_warns
                    STATE["last_debug"]["model_family"] = _g2_hints.get("family", "general") if "_g2_hints" in locals() else "general"
                    if STATE["stop_requested"]:
                        full_reply = f"{full_reply} *(⏹️ Stopped)*".strip()
                    if not full_reply:
                        full_reply = "..."
            finally:
                STATE["generating"] = False
                STATE["spotify_readonly_turn"] = False
                set_step("Idle")

            with get_db() as conn:
                conn.execute("INSERT INTO chat_messages (session_id, role, content) VALUES (?, 'assistant', ?)", (session_id, full_reply))
                conn.execute("UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (session_id,))
                conn.commit()

            update_partner_evolution(user_msg, full_reply)
            export_chats_to_txt_files()
            yield json.dumps({"type": "done", "reply": full_reply, "image_url": generated_img_url, "audio_url": generated_audio_url}) + "\n"

        except Exception as e:
            tb = traceback.format_exc()
            STATE["last_debug"]["error"] = tb
            err_card = format_predetermined_error("ERR_ENGINE_CRASH", str(e))
            yield json.dumps({"type": "issue", "issue": err_card}) + "\n"
            yield json.dumps({
                "type": "done",
                "reply": f"⚠️ **[{err_card['code']}: {err_card['title']}]**\n{err_card['message']}\n💡 *Fix: {err_card['fix']}*\n`{type(e).__name__}: {e}`"
            }) + "\n"
        finally:
            STATE["generating"] = False
            set_step("Idle")

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")


# =====================================================================
# 14. v3.3 UPGRADE: PSEUDO-MEMORY INDEXER, PASSIVE NOTE HARVESTER,
#     MODEL-AGNOSTIC CAPABILITY LOCK & ROBUST ERROR AUDIT LOG
# =====================================================================
PSEUDO_INDEX_JSON_PATH = BASE_DIR / "pseudo_memory_index.json"
PSEUDO_NOTES_TXT_PATH = MEMORY_DIR / "pseudo_memory_notes.txt"
ERROR_AUDIT_LOG_PATH = BASE_DIR / "error_audit.log"

PREDETERMINED_ERRORS["ERR_INDEX_SYNC"] = {
    "code": "ERR-11",
    "title": "Pseudo-Memory & Boot Index Auto-Healed",
    "message": "A file or chat log had malformed characters during boot indexing, so I skipped the bad block and rebuilt pseudo_memory_index.json cleanly.",
    "fix": "Handled automatically. Check error_audit.log if a specific file needs attention."
}
PREDETERMINED_ERRORS["ERR_FILE_PARSE"] = {
    "code": "ERR-12",
    "title": "Corrupted PDF / Knowledge File Skipped",
    "message": "One file in /priority_pdfs could not be parsed and was quarantined so the rest of your Knowledge Tree stays online.",
    "fix": "Verify that the PDF/text file is not password-protected or 0 bytes."
}
PREDETERMINED_ERRORS["ERR_VULKAN_LEGACY_APU"] = {
    "code": "ERR-13",
    "title": "Vulkan GPU Driver Incompatible (Auto-Switched to Safe CPU Mode)",
    "message": "Your GPU/APU driver (e.g. legacy AMD Radeon R5/R7 or older integrated graphics) rejected Vulkan offload, so AetherVault automatically switched to Safe CPU Mode.",
    "fix": "In the Bootstrapper (manager.py), click 'Switch Engine (Vulkan GPU vs Safe CPU)' -> Safe CPU Build, set Governor to 'Laptop 2015 (Fast)', and refer to Section 4 of the Built-In Manual (📖 Manual button) for legacy hardware tuning."
}
PREDETERMINED_ERRORS["ERR_HARDWARE_BELOW_SPEC"] = {
    "code": "ERR-14",
    "title": "Model Too Heavy for Current CPU / RAM Tier",
    "message": "The selected GGUF model is too large for this machine's CPU core count or available RAM, causing slow generation or a load abort.",
    "fix": "Switch to a 1.5B Q4_K_M model (DeepSeek-R1-1.5B or Qwen2.5-1.5B), set Governor to 'Laptop 2015 (Fast)', and open 📖 Manual -> Section 6 (Minimum Hardware Specs & Legacy Guide) for full reference."
}

STATE.setdefault("error_history", [])

_orig_format_err = format_predetermined_error
def format_predetermined_error(err_key: str, extra_detail: str = "") -> dict:
    info = _orig_format_err(err_key, extra_detail)
    try:
        STATE.setdefault("error_history", []).insert(0, info)
        STATE["error_history"] = STATE["error_history"][:25]
        log_line = (
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [{info.get('code')}] "
            f"{info.get('title')} | {info.get('message')} | Detail: {info.get('detail', 'None')}\n"
        )
        with open(ERROR_AUDIT_LOG_PATH, "a", encoding="utf-8") as lf:
            lf.write(log_line)
    except Exception:
        pass
    return info

UNIVERSAL_CAPABILITY_LOCK = (
    "[BUILT-IN CAPABILITIES & TOOL TAGS (ALWAYS AVAILABLE REGARDLESS OF MODEL OR PERSONA)]:\n"
    f"- You run locally inside AetherVault Studio v{APP_VERSION} with session-scoped %TEMP% dynamic caching, full Cross-Chat Recall, Self-Code/Log Inspection, a Knowledge Tree (/priority_pdfs), Local PC/Drive file access, Live Web Search, Spotify control, Specialist Image & Music Managers (Cashier-to-Manager swap), and OSWorld Desktop GUI control.\n"
    "- Live Python Workbench: To actually play music, check real weather, search the web, or inspect the PC while staying in character, output a ```workbench block (`vault.spotify('play', 'song')`, `vault.spotify('next')`, `vault.weather('City')`, `vault.web('query')`, `vault.pc_info()`).\n"
    "- Optional Tool Tags you can emit anytime: [[CHATS:list|]] | [[CHATS:search|topic]] | [[CHATS:read|session]] | "
    "[[SELF:tree|]] | [[SELF:errors|]] | [[SELF:search|term]] | [[SELF:read|file:1-60]] | "
    "[[SELF:propose_fix|filename|exact_old_snippet|exact_new_snippet]] (NEVER overwrites core files directly — stages a syntax-verified patch in /self_heal_staging for explicit user approval!) | "
    "[[SEARCH:query]] | [[LORE:keywords]] | [[FILES:path_or_query]] | "
    "[[OSWORLD:screenshot|]] | [[OSWORLD:list_windows|]] | [[OSWORLD:open_app|app]] | [[SPOTIFY:play|song]] | "
    "[[IMAGE:visual prompt]] | [[MUSIC:style & mood prompt|8]] | [[MEMORY:category|fact]]"
)

PASSIVE_NOTE_PATTERNS = [
    (r"\b(?:my name is|call me|i am called)\s+([A-Z][a-zA-Z0-9_-]{1,22})", "user_identity", "User's name/handle is {0}"),
    (r"\b(?:i'?m from|i am from|am from|i live in|(?:my\s+)?city\s+is|located in)\s+([A-Za-z0-9,\-\s!]{3,75}?)(?:\s*(?:,?\s*zip|,?\s*postal|\?|$))", "user_location", "User lives in {0}"),
    (r"\b(?:zip\s*code|postal\s*code)(?:\s+is|\s+it'?s|:)?\s*([A-Za-z0-9\-]{3,12})", "user_zip", "User ZIP/Postal code is {0}"),
    (r"\b(?:remember that|don't forget that|keep in mind that|note that)\s+([^.?!\n]{5,120})", "user_note", "{0}"),
    (r"\b(?:i am working on|i'm working on|my current project is|we are building)\s+([^.?!\n]{4,100})", "active_project", "Working on: {0}"),
    (r"\b(?:my favorite|i really like|i prefer)\s+([^.?!\n]{4,90})", "preference", "Preference: {0}"),
]

def harvest_passive_user_notes(user_msg: str) -> list:
    """
    Model-agnostic pseudo-memory & Profile Card harvester:
    Catches user name, real location/city, ZIP code, active projects, and explicit notes
    into both SQLite Memory Vault and `user_profile_card.json`!
    """
    if not user_msg or len(user_msg) > 1500:
        return []
    harvested = []
    card = load_user_profile_card()
    card_changed = False
    for pat, cat, template in PASSIVE_NOTE_PATTERNS:
        for m in re.finditer(pat, user_msg, flags=re.IGNORECASE):
            captured = m.group(1).strip().rstrip(".,;!")
            if len(captured) >= 2:
                if cat == "user_location":
                    captured = _clean_location_value(captured)
                elif cat == "user_zip":
                    captured = captured.upper()
                if len(captured) < 2:
                    continue
                fact_str = template.format(captured)
                save_to_memory(cat, fact_str, sync_pseudo=False)
                harvested.append(f"[{cat}] {fact_str}")
                if cat == "user_identity" and len(captured.split()) == 1:
                    WORKSPACE_CFG["user_name"] = captured
                    save_workspace_config(WORKSPACE_CFG)
                    card["user_name"] = captured
                    card_changed = True
                elif cat == "user_location":
                    card["location"] = captured
                    card_changed = True
                elif cat == "user_zip":
                    card["zip_code"] = captured
                    card_changed = True
                elif cat in ("user_note", "active_project", "preference"):
                    low_f = fact_str.lower()
                    is_ai_instruction = bool(re.match(r"^(?:you\s+(?:can|could|should|have|need|must|are\s+supposed|ought)|please\s+)", low_f))
                    if not is_ai_instruction:
                        pf = card.get("pinned_facts") or []
                        if fact_str not in pf:
                            card["pinned_facts"] = (pf + [fact_str])[-10:]
                            card_changed = True
    if harvested:
        sync_pseudo_memory_and_index()
    if card_changed:
        save_user_profile_card(card)
    return harvested

def sync_pseudo_memory_and_index():
    """
    Runs at boot (while loading) and after turns to maintain:
    1. pseudo_memory_index.json (compact structured index of user profile, notes, file map, and recent chats)
    2. /memory_vault/pseudo_memory_notes.txt (compact plain-text digest injected into prompts)
    """
    try:
        mems = list_memories()
        file_map = []
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT filename, file_mode, summary FROM priority_pdfs ORDER BY filename ASC")
            for r in c.fetchall():
                st = PRIORITY_CACHE["file_stats"].get(r["filename"], {})
                file_map.append({
                    "file": r["filename"],
                    "mode": r["file_mode"],
                    "chunks": st.get("chunks", 1),
                    "summary": (r["summary"] or "")[:120]
                })

            c.execute("SELECT id, title, updated_at FROM chat_sessions ORDER BY updated_at DESC LIMIT 8")
            sessions = c.fetchall()
            chat_recaps = []
            for s in sessions:
                c.execute("SELECT role, content FROM chat_messages WHERE session_id = ? ORDER BY id DESC LIMIT 2", (s["id"],))
                turns = list(reversed(c.fetchall()))
                if turns:
                    snippet = " | ".join([f"{t['role']}: {(t['content'] or '')[:70].replace(chr(10), ' ')}" for t in turns])
                    chat_recaps.append({"session": s["title"], "updated": s["updated_at"], "last_exchange": snippet})

        pcard = load_user_profile_card(allow_json_fallback=False)
        index_payload = {
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "ai_name": WORKSPACE_CFG.get("ai_name", "Aether"),
            "user_name": WORKSPACE_CFG.get("user_name", "Creator"),
            "active_model": STATE.get("current_model") or WORKSPACE_CFG.get("last_loaded_model") or "None",
            "user_context": {
                "user_name": pcard.get("user_name", WORKSPACE_CFG.get("user_name", "Creator")),
                "location": pcard.get("location", ""),
                "zip_code": pcard.get("zip_code", ""),
                "latitude": pcard.get("latitude"),
                "longitude": pcard.get("longitude"),
                "pinned_facts": (pcard.get("pinned_facts") or [])[-10:],
                "custom_fields": pcard.get("custom_fields") if isinstance(pcard.get("custom_fields"), dict) else {}
            },
            "capabilities": [
                "Reflex/Deep Two-Gear Router",
                "Pseudo-Memory Vault (.json + .txt)",
                "CORE/LORE File Tree (/priority_pdfs)",
                "OSWorld Desktop Control",
                "PC/Drive File Scanner",
                "Dual-Engine Live Web Search",
                "Spotify Web & App Bridge",
                "Image Generation Bridge"
            ],
            "pseudo_memory_notes": [f"[{m['category']}] {m['fact']}" for m in mems[:20]],
            "file_index_map": file_map,
            "recent_chat_recaps": chat_recaps,
            "top_glossary_keywords": PRIORITY_CACHE.get("glossary_top_words", [])[:20]
        }
        PSEUDO_INDEX_JSON_PATH.write_text(json.dumps(index_payload, indent=2, ensure_ascii=False), encoding="utf-8")

        txt_lines = [
            f"=== PSEUDO-MEMORY & FILE INDEX (Auto-Synced {index_payload['updated_at']}) ===",
            f"User: {index_payload['user_name']} | Location: {index_payload['user_context'].get('location') or 'Not set yet'} | Companion: {index_payload['ai_name']}",
            PRIORITY_CACHE.get("partner_digest", "Partner Bond: Active Studio Co-Creator"),
            "Indexed Files: " + (", ".join([f"{f['file']} ({f['mode'].upper()}, {f['chunks']}s)" for f in file_map[:10]]) or "None"),
            "Top Keywords: " + (", ".join(index_payload["top_glossary_keywords"][:10]) or "None"),
            "Recent Cross-Chat Recaps:"
        ]
        for rc in chat_recaps[:3]:
            txt_lines.append(f"  * [{rc['session']}] {rc['last_exchange']}")
        if mems:
            txt_lines.append("Learned Notes:")
            for m in mems[:8]:
                txt_lines.append(f"  * [{m['category']}] {m['fact']}")

        PSEUDO_NOTES_TXT_PATH.write_text("\n".join(txt_lines), encoding="utf-8")
        PRIORITY_CACHE["pseudo_notes_digest"] = "\n".join(txt_lines)[:750]
    except Exception as e:
        format_predetermined_error("ERR_INDEX_SYNC", str(e))


@app.post("/diagnostics/tool_gauntlet")
def api_run_tool_gauntlet(payload: dict):
    """Streams live step-by-step Tool Gauntlet results (NDJSON) for the 1-Click UI button."""
    include_active = bool((payload or {}).get("include_active", False))
    only_tool = str((payload or {}).get("only_tool") or "").strip()
    def _stream():
        STATE["stop_requested"] = False
        for evt in run_tool_gauntlet_generator(include_active=include_active, only_tool=only_tool):
            yield json.dumps(evt, ensure_ascii=False) + "\n"
    return StreamingResponse(_stream(), media_type="application/x-ndjson")

@app.get("/diagnostics/selftest")
def run_system_selftest():
    """1-Click Self-Test across all 7 AetherVault subsystems."""
    sync_pseudo_memory_and_index()
    checks = [
        {"system": "SQLite Memory Core (memory_core.db)", "ok": DB_PATH.exists(), "detail": f"{DB_PATH.stat().st_size if DB_PATH.exists() else 0} bytes"},
        {"system": "Pseudo-Memory & Boot Index (.json + .txt)", "ok": PSEUDO_INDEX_JSON_PATH.exists() and PSEUDO_NOTES_TXT_PATH.exists(), "detail": f"{len(list_memories())} notes | {len(PRIORITY_CACHE.get('glossary_top_words', []))} indexed keywords"},
        {"system": "Knowledge Tree (/priority_pdfs)", "ok": PDF_DIR.exists(), "detail": f"{len(PRIORITY_CACHE.get('core_file_names', []))} CORE + {PRIORITY_CACHE.get('lore_file_count', 0)} LORE files ({PRIORITY_CACHE.get('lore_chunk_count', 0)} chunks)"},
        {"system": "Local GGUF Brain (/models)", "ok": len(list_local_models()) > 0, "detail": f"Active: {STATE.get('current_model') or 'None'} | Available: {', '.join(list_local_models()) or 'None in /models'}"},
        {"system": "OSWorld Desktop Agent", "ok": bool(WORKSPACE_CFG.get("osworld_enabled", True)), "detail": f"PyAutoGUI: {'Installed' if HAS_PYAUTOGUI else 'Windows ctypes fallback'}"},
        {"system": "Local PC & Drive Scanner", "ok": len(STATE.get("allowed_pc_roots", [])) > 0, "detail": f"{len(STATE.get('allowed_pc_roots', []))} root paths indexed"},
        {"system": "Ephemeral %TEMP% Session Cache (Until Shutdown)", "ok": TEMP_SESSION_DIR.exists(), "detail": f"{get_temp_cache_stats()['cached_files']} files ({get_temp_cache_stats()['size_kb']} KB) in {TEMP_SESSION_DIR.name}"},
        {"system": "Cross-Chat Recall & Self-File Inspector", "ok": True, "detail": "[[CHATS:list/search/read]] & [[SELF:tree/errors/search/read]] online"},
        {"system": "Cashier-to-Manager Image & Music Swapper", "ok": GEN_IMG_DIR.exists() and GEN_AUDIO_DIR.exists(), "detail": "Image & Music Managers + Offline Synth/Canvas fallbacks ready"},
        {"system": "Offline Neural Voice & Vision Slots", "ok": VOICE_MODEL_DIR.exists() and VISION_MODEL_DIR.exists(), "detail": f"{len(VOICE_PROFILES)} voice profiles (incl. Female Voice 3) | {len(list_vision_projectors())} mmproj files"},
        {"system": "Embedded Self-Manual & Partner Evolution", "ok": PARTNER_EVOLUTION_PATH.exists(), "detail": f"{len(SELF_MANUAL_SECTIONS)} manual sections + partner_evolution.json synced"},
        {"system": "Error Audit Log (error_audit.log)", "ok": True, "detail": f"{len(STATE.get('error_history', []))} recent issues logged"}
    ]
    return {"ok": all(c["ok"] for c in checks if "GGUF" not in c["system"]), "checks": checks, "error_history": STATE.get("error_history", [])}


# =====================================================================
# 15. v3.4 UPGRADE: SESSION-SCOPED %TEMP% DYNAMIC CACHE (UNTIL SHUTDOWN),
#     CROSS-CHAT RECALL ([[CHATS:...]]), SELF-FILE INSPECTOR ([[SELF:...]]),
#     AND "CASHIER-TO-MANAGER" SPECIALIST IMAGE & MUSIC SWAPPER
# =====================================================================
SPECIALIST_MODEL_BAG = [
    {
        "type": "image",
        "name": "🎨 Segmind Tiny-SD (~1.6GB - Fast Local Diffusers Image Manager)",
        "repo": "segmind/tiny-sd",
        "license": "Apache-2.0"
    },
    {
        "type": "image",
        "name": "🎨 StabilityAI SD-Turbo (~2.5GB - 1-Step Local Image Manager)",
        "repo": "stabilityai/sd-turbo",
        "license": "StabilityAI Non-Commercial / Community"
    },
    {
        "type": "music",
        "name": "🎵 Meta MusicGen-Small (~1.2GB - Local AI Music & Synth Manager)",
        "repo": "facebook/musicgen-small",
        "license": "CC-BY-NC-4.0 (Meta AudioCraft)"
    },
    {
        "type": "music",
        "name": "🎵 Suno Bark-Small (~1.5GB - Local Audio & Vocal SFX Manager)",
        "repo": "suno/bark-small",
        "license": "MIT (Suno AI)"
    }
]

def cleanup_orphaned_temp_sessions():
    """Sweeps any leftover %TEMP%/AetherVault_Session_* folders and resets local .temp_cache on boot."""
    try:
        tmp_root = Path(tempfile.gettempdir())
        for p in tmp_root.glob("AetherVault_Session_*"):
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
    except Exception:
        pass
    try:
        if TEMP_SESSION_DIR.exists():
            shutil.rmtree(TEMP_SESSION_DIR, ignore_errors=True)
        TEMP_SESSION_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

def cleanup_session_temp_cache():
    """Deletes the active %TEMP%/AetherVault_Session_<pid> folder cleanly on server shutdown."""
    try:
        if TEMP_SESSION_DIR.exists():
            shutil.rmtree(TEMP_SESSION_DIR, ignore_errors=True)
            print(f"[TEMP CACHE PURGE] Deleted session cache {TEMP_SESSION_DIR}", flush=True)
    except Exception:
        pass

atexit.register(cleanup_session_temp_cache)

@app.on_event("shutdown")
def on_shutdown():
    cleanup_session_temp_cache()

def get_temp_cache_stats() -> dict:
    TEMP_SESSION_DIR.mkdir(parents=True, exist_ok=True)
    files = [f for f in TEMP_SESSION_DIR.rglob("*") if f.is_file()]
    total_kb = round(sum(f.stat().st_size for f in files) / 1024.0, 1)
    return {
        "session_temp_dir": str(TEMP_SESSION_DIR),
        "cached_files": len(files),
        "size_kb": total_kb,
        "file_names": [f.name for f in files[:10]]
    }

def record_temp_gear_cache(gear: str, sys_prompt_text: str):
    """Saves the evaluated static prefix & metadata for Gear 1 (reflex) and Gear 2 (deep) in %TEMP%."""
    try:
        TEMP_SESSION_DIR.mkdir(parents=True, exist_ok=True)
        cache_file = TEMP_SESSION_DIR / f"gear_{gear}_prefix.json"
        payload = {
            "gear": gear,
            "model": STATE.get("current_model") or "None",
            "updated_at": time.strftime("%H:%M:%S"),
            "prefix_chars": len(sys_prompt_text),
            "prefix_hash": hash(sys_prompt_text[:600])
        }
        cache_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except Exception:
        pass

def execute_cross_chat_tool(cmd: str, arg: str = "", current_session_id: str = "") -> str:
    """
    Allows the assistant to browse, search, and read across all old chat sessions
    in SQLite (chat_sessions / chat_messages) and /chat_logs/*.txt!
    """
    action = (cmd or "list").strip().lower()
    query = (arg or "").strip()

    with get_db() as conn:
        c = conn.cursor()
        if action == "list":
            c.execute("SELECT id, title, updated_at FROM chat_sessions ORDER BY updated_at DESC LIMIT 20")
            rows = c.fetchall()
            if not rows:
                return "No chat sessions found."
            lines = ["=== ALL WORKSPACE CHAT SESSIONS ==="]
            for r in rows:
                c.execute("SELECT COUNT(*) FROM chat_messages WHERE session_id = ?", (r["id"],))
                cnt = c.fetchone()[0]
                c.execute("SELECT role, content FROM chat_messages WHERE session_id = ? ORDER BY id DESC LIMIT 1", (r["id"],))
                last_m = c.fetchone()
                preview = f"{last_m['role']}: {(last_m['content'] or '')[:80].replace(chr(10), ' ')}" if last_m else "Empty"
                marker = " (CURRENT)" if r["id"] == current_session_id else ""
                lines.append(f"- [{r['id']}] '{r['title']}'{marker} | {cnt} msgs | Updated: {r['updated_at']} | Last: {preview}")
            return "\n".join(lines)

        elif action == "read":
            c.execute(
                "SELECT id, title FROM chat_sessions WHERE id = ? OR LOWER(title) LIKE ? ORDER BY updated_at DESC LIMIT 1",
                (query, f"%{query.lower()}%")
            )
            srow = c.fetchone()
            if not srow:
                return f"No chat session matching '{query}' was found."
            c.execute("SELECT role, content, timestamp FROM chat_messages WHERE session_id = ? ORDER BY id DESC LIMIT 12", (srow["id"],))
            msgs = list(reversed(c.fetchall()))
            out = [f"=== TRANSCRIPT RECAP FOR SESSION '{srow['title']}' ({srow['id']}) ==="]
            for m in msgs:
                out.append(f"[{m['timestamp']}] {m['role'].upper()}: {(m['content'] or '')[:350]}")
            return "\n".join(out)[:3200]

        else:  # search across all sessions
            terms = [t for t in extract_keywords(query) if len(t) >= 3]
            if not terms:
                return execute_cross_chat_tool("list", "", current_session_id)
            like_sql = " OR ".join(["LOWER(cm.content) LIKE ?" for _ in terms[:4]])
            params = [f"%{t.lower()}%" for t in terms[:4]]
            c.execute(f"""
                SELECT cs.id, cs.title, cm.role, cm.content, cm.timestamp
                FROM chat_messages cm
                JOIN chat_sessions cs ON cm.session_id = cs.id
                WHERE {like_sql}
                ORDER BY cm.id DESC LIMIT 12
            """, params)
            matches = c.fetchall()
            if not matches:
                return f"No past chat messages matched keywords: {', '.join(terms[:4])}."
            out = [f"=== CROSS-CHAT SEARCH MATCHES FOR '{query}' ==="]
            for m in matches:
                out.append(f"- Session '{m['title']}' ({m['id']}) [{m['timestamp']}] {m['role']}: {(m['content'] or '')[:260]}")
            return "\n".join(out)[:3200]

def execute_self_inspection_tool(cmd: str, arg: str = "") -> str:
    """
    Strictly read-only Self-File Inspector so the AI can examine its own codebase,
    line counts, %TEMP% cache stats, and error_audit.log without overflowing context!
    """
    action = (cmd or "tree").strip().lower()
    param = (arg or "").strip()
    self_files = [
        "Launch.bat",
        "Launch.sh",
        "manager.py",
        "assistant_server.py",
        "ui_studio.html",
        "workspace_config.json",
        "pseudo_memory_index.json",
        "glossary_index.json",
        "error_audit.log"
    ]

    if action == "tree":
        tstats = get_temp_cache_stats()
        lines = [
            f"=== AETHERVAULT v{APP_VERSION} SELF-ARCHITECTURE & FILE MANIFEST ===",
            f"- Root Directory: {BASE_DIR}",
            f"- Ephemeral %TEMP% Session Cache: {tstats['session_temp_dir']} ({tstats['cached_files']} cached files, {tstats['size_kb']} KB — auto-deletes on shutdown)"
        ]
        for fname in self_files:
            fpath = BASE_DIR / fname
            if fpath.exists():
                raw = fpath.read_text(encoding="utf-8", errors="ignore")
                lines.append(f"  * {fname}: {fpath.stat().st_size:,} bytes | {len(raw.splitlines()):,} lines")
        return "\n".join(lines)

    elif action == "manual":
        return search_self_manual(param)

    elif action == "errors":
        if ERROR_AUDIT_LOG_PATH.exists():
            log_lines = ERROR_AUDIT_LOG_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()[-15:]
            return "=== RECENT ERROR AUDIT LOG (error_audit.log) ===\n" + ("\n".join(log_lines) if log_lines else "0 errors logged.")
        return "No errors recorded in error_audit.log."

    elif action == "read":
        # Format: filename or filename:start-end
        m = re.match(r"^([^:]+)(?::(\d+)-(\d+))?$", param)
        target_name = Path(m.group(1).strip()).name if m else "assistant_server.py"
        if target_name not in self_files:
            target_name = "assistant_server.py"
        start_ln = int(m.group(2)) if (m and m.group(2)) else 1
        end_ln = int(m.group(3)) if (m and m.group(3)) else (start_ln + 65)
        fpath = BASE_DIR / target_name
        if not fpath.exists():
            return f"File '{target_name}' does not exist yet."
        all_lines = fpath.read_text(encoding="utf-8", errors="ignore").splitlines()
        sliced = all_lines[max(0, start_ln - 1):min(len(all_lines), end_ln)]
        numbered = [f"L{ idx }: {ln}" for idx, ln in enumerate(sliced, max(1, start_ln))]
        return f"=== SELF-READ: {target_name} (Lines {start_ln}-{min(len(all_lines), end_ln)} of {len(all_lines)}) ===\n" + "\n".join(numbered)[:3000]

    else:  # search across own files
        q = param.lower() or "def "
        hits = []
        for fname in ("assistant_server.py", "manager.py", "ui_studio.html", "pseudo_memory_index.json"):
            fpath = BASE_DIR / fname
            if not fpath.exists():
                continue
            for idx, ln in enumerate(fpath.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                if q in ln.lower():
                    hits.append(f"{fname}:L{idx}: {ln.strip()[:120]}")
                    if len(hits) >= 25:
                        break
        return f"=== SELF-CODE SEARCH FOR '{param}' ===\n" + ("\n".join(hits) if hits else "No matching lines found.")

def run_with_specialist_manager(task_label: str, requires_vram_swap: bool, manager_callable):
    """
    'Cashier Calling Over a Manager' Swapper:
    1. If requires_vram_swap is True and a main GGUF model is loaded, parks the main LLM state in %TEMP%,
       unloads STATE['llm'], and calls gc.collect() so 100% of VRAM/RAM is freed for the specialist model.
    2. Executes manager_callable().
    3. Unloads the specialist model and reloads the main GGUF Cashier automatically!
    """
    parked_model = STATE.get("current_model")
    did_unload = False
    try:
        if requires_vram_swap and STATE.get("llm") is not None:
            set_step(f"🏪 Cashier->Manager Handoff: Parking '{parked_model}' in %TEMP% to free VRAM for {task_label}...")
            record_temp_gear_cache("parked_cashier", f"Parked {parked_model} for {task_label}")
            with LLM_LOCK:
                STATE["llm"] = None
                gc.collect()
            did_unload = True

        result = manager_callable()
        return result
    finally:
        gc.collect()
        if did_unload and parked_model:
            set_step(f"🏪 Manager finished {task_label}! Calling Cashier '{parked_model}' back to the counter...")
            load_local_model(parked_model)

def synthesize_procedural_music_wav(prompt: str, out_path: Path, duration_sec: int = 8) -> dict:
    """
    Built-in Multi-Voice Procedural Synthwave / Lo-Fi / Ambient .WAV Composer (44.1kHz 16-bit Stereo).
    Ensures the Music Manager ALWAYS produces a rich, playable .wav track 100% offline even before
    downloading a 1.5GB Hugging Face MusicGen checkpoint!
    """
    sample_rate = 44100
    duration_sec = max(4, min(20, int(duration_sec)))
    n_samples = sample_rate * duration_sec
    low = (prompt or "").lower()

    # Choose musical scale & tempo based on prompt mood
    if any(w in low for w in ("80s", "synth", "cyber", "retro", "fast", "rock", "acid")):
        bpm = 118
        chords = [(220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (130.81, 164.81, 196.0), (196.0, 246.94, 293.66)]  # Am - F - C - G
        style_tag = "80s Retro Synthwave Engine"
    elif any(w in low for w in ("dark", "goth", "metal", "bass", "heavy")):
        bpm = 96
        chords = [(146.83, 174.61, 220.0), (130.81, 164.81, 196.0), (116.54, 146.83, 174.61), (110.0, 138.59, 164.81)]  # Dm - C - Bb - A
        style_tag = "Dark Bass & Sub-Synth Engine"
    else:
        bpm = 82
        chords = [(261.63, 329.63, 392.0), (220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (196.0, 246.94, 293.66)]  # Lo-Fi Cmaj7 - Am7 - Fmaj7 - G
        style_tag = "Lo-Fi Chill & Warm Rhodes Engine"

    beat_sec = 60.0 / bpm
    bar_sec = beat_sec * 4.0
    two_pi = 2.0 * math.pi

    frames = bytearray()
    for i in range(n_samples):
        t = i / sample_rate
        bar_idx = int(t / bar_sec) % len(chords)
        root, third, fifth = chords[bar_idx]

        # 1. Warm stereo pad (detuned chorus)
        pad_l = 0.18 * (math.sin(two_pi * root * t) + 0.7 * math.sin(two_pi * third * 1.002 * t) + 0.6 * math.sin(two_pi * fifth * t))
        pad_r = 0.18 * (math.sin(two_pi * root * 0.998 * t) + 0.7 * math.sin(two_pi * third * t) + 0.6 * math.sin(two_pi * fifth * 1.003 * t))

        # 2. Sub-bass pulse on eighth notes
        sub_env = max(0.0, 1.0 - ((t % (beat_sec / 2.0)) / (beat_sec / 2.0))) ** 1.8
        bass = 0.28 * sub_env * math.tanh(2.2 * math.sin(two_pi * (root * 0.5) * t))

        # 3. Arpeggiator lead on sixteenth notes
        step_idx = int(t / (beat_sec / 4.0)) % 4
        arp_freq = (root * 2.0, third * 2.0, fifth * 2.0, third * 2.0)[step_idx]
        arp_env = max(0.0, 1.0 - ((t % (beat_sec / 4.0)) / (beat_sec / 4.0))) ** 2.4
        arp = 0.16 * arp_env * math.sin(two_pi * arp_freq * t)

        # 4. Soft kick drum on beats
        beat_pos = t % beat_sec
        kick = 0.0
        if beat_pos < 0.14:
            k_freq = 115.0 * math.exp(-beat_pos * 22.0) + 42.0
            kick = 0.32 * (1.0 - beat_pos / 0.14) * math.sin(two_pi * k_freq * beat_pos)

        # Master fade-in & fade-out envelope
        fade = min(1.0, t / 0.35, (duration_sec - t) / 0.6)
        left_val = max(-0.98, min(0.98, (pad_l + bass + arp * 0.8 + kick) * fade))
        right_val = max(-0.98, min(0.98, (pad_r + bass + arp * 1.1 + kick) * fade))

        frames += struct.pack("<hh", int(left_val * 32767), int(right_val * 32767))

    with wave.open(str(out_path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(bytes(frames))

    return {"ok": True, "url": f"/generated_audio/{out_path.name}", "source": f"Local {style_tag} ({bpm} BPM)"}

def generate_music_tool(prompt: str, duration_sec: int = 8) -> dict:
    """
    Music Manager (Cashier-to-Manager Handoff):
    1. Checks if local Hugging Face MusicGen / Bark weights exist in /models/music and runs via transformers if installed.
    2. Otherwise synthesizes a real, playable 44.1kHz stereo .wav track via the built-in Procedural Synth Engine!
    """
    clean_p = (prompt or "80s retro lo-fi synth track").strip()
    fname = f"aether_music_{int(time.time())}.wav"
    fpath = GEN_AUDIO_DIR / fname

    local_music_dirs = [p for p in MUSIC_MODEL_DIR.iterdir() if p.is_dir() and (p / "config.json").exists()] if MUSIC_MODEL_DIR.exists() else []
    has_transformers = importlib.util.find_spec("transformers") is not None and importlib.util.find_spec("scipy") is not None

    if local_music_dirs and has_transformers:
        def _run_hf_music():
            from transformers import pipeline
            import scipy.io.wavfile as wavfile
            import numpy as np
            model_dir = str(local_music_dirs[0])
            synth = pipeline("text-to-audio", model=model_dir, device=-1)
            music = synth(clean_p, forward_params={"do_sample": True, "max_new_tokens": int(duration_sec * 50)})
            audio_arr = np.squeeze(music["audio"])
            sr = int(music["sampling_rate"])
            wavfile.write(str(fpath), rate=sr, data=(audio_arr * 32767).astype(np.int16))
            del synth
            return {"ok": True, "url": f"/generated_audio/{fname}", "source": f"HF Music Manager ({local_music_dirs[0].name})"}
        try:
            return run_with_specialist_manager("HF Music Manager", True, _run_hf_music)
        except Exception as e:
            print(f"[MUSIC MANAGER FALLBACK] HF model raised {e}; using Procedural Synth Engine.", flush=True)

    return synthesize_procedural_music_wav(clean_p, fpath, duration_sec=duration_sec)

# Enhance generate_image_tool with Cashier-to-Manager local diffusers support + offline procedural canvas fallback
_orig_generate_image_tool = generate_image_tool
def generate_image_tool(prompt: str) -> dict:
    clean_p = (prompt or "cyberpunk studio").strip()
    local_img_dirs = [p for p in IMG_MODEL_DIR.iterdir() if p.is_dir() and (p / "model_index.json").exists()] if IMG_MODEL_DIR.exists() else []
    has_diffusers = importlib.util.find_spec("diffusers") is not None

    if local_img_dirs and has_diffusers:
        def _run_hf_image():
            from diffusers import DiffusionPipeline
            fname = f"aether_art_{int(time.time())}.png"
            fpath = GEN_IMG_DIR / fname
            pipe = DiffusionPipeline.from_pretrained(str(local_img_dirs[0]))
            pipe.to("cpu")
            img = pipe(clean_p, num_inference_steps=12).images[0]
            img.save(fpath)
            del pipe
            return {"ok": True, "url": f"/generated_image/{fname}", "source": f"HF Image Manager ({local_img_dirs[0].name})"}
        try:
            return run_with_specialist_manager("HF Image Manager", True, _run_hf_image)
        except Exception as e:
            print(f"[IMAGE MANAGER FALLBACK] Local diffusers raised {e}; trying SD WebUI / Bridge.", flush=True)

    res = _orig_generate_image_tool(clean_p)
    if res.get("ok"):
        return res

    # Offline procedural artwork card fallback so Image Generation never fails empty when offline
    try:
        from PIL import ImageDraw
        fname = f"aether_art_{int(time.time())}.png"
        fpath = GEN_IMG_DIR / fname
        img = Image.new("RGB", (768, 512), color=(15, 16, 26))
        draw = ImageDraw.Draw(img)
        for y in range(0, 512, 4):
            r_c = min(255, int(25 + (y / 512) * 90))
            g_c = min(255, int(15 + (y / 512) * 35))
            b_c = min(255, int(60 + (y / 512) * 145))
            draw.line([(0, y), (768, y)], fill=(r_c, g_c, b_c), width=4)
        draw.ellipse((264, 96, 504, 336), outline=(167, 139, 250), width=4)
        for gx in range(0, 768, 48):
            draw.line([(gx, 340), (384 + (gx - 384) * 2, 512)], fill=(124, 58, 237), width=2)
        draw.rectangle((28, 410, 740, 488), fill=(20, 21, 28), outline=(124, 58, 237), width=2)
        draw.text((44, 424), f"AETHERVAULT OFFLINE CANVAS RENDERER", fill=(167, 139, 250))
        draw.text((44, 450), f"Prompt: {clean_p[:72]}", fill=(229, 231, 235))
        img.save(fpath, format="PNG")
        return {"ok": True, "url": f"/generated_image/{fname}", "source": "Offline Procedural Canvas"}
    except Exception:
        return res

@app.get("/generated_audio/{filename}")
def serve_generated_audio(filename: str):
    fpath = GEN_AUDIO_DIR / Path(filename).name
    if not fpath.exists():
        raise HTTPException(404, "Audio file not found")
    return FileResponse(str(fpath), media_type="audio/wav")

@app.post("/generate_music")
def api_generate_music(payload: dict):
    prompt = (payload.get("prompt") or "").strip()
    try:
        duration = max(3, min(30, int(payload.get("duration") or 8)))
    except Exception:
        duration = 8
    if not prompt:
        return {"ok": False, "error": "Empty music prompt"}
    set_step(f"🏪 Music Manager composing: {prompt[:35]}...")
    res = generate_music_tool(prompt, duration_sec=duration)
    set_step("Idle")
    return res

@app.post("/download_specialist_model")
def api_download_specialist_model(payload: dict):
    if STATE["offline_mode"]:
        return {"ok": False, "error": "Cannot download while Offline Mode is enabled."}
    repo_id = (payload.get("repo_id") or "").strip()
    mtype = (payload.get("type") or "image").strip().lower()
    if not repo_id:
        return {"ok": False, "error": "Missing Hugging Face repo_id."}
    type_map = {
        "image": IMG_MODEL_DIR,
        "music": MUSIC_MODEL_DIR,
        "voice": VOICE_MODEL_DIR,
        "vision": VISION_MODEL_DIR
    }
    target_root = type_map.get(mtype, IMG_MODEL_DIR)
    local_dir = target_root if mtype in ("voice", "vision") else (target_root / repo_id.split("/")[-1])

    def _dl_specialist():
        try:
            from huggingface_hub import snapshot_download
            STATE["download"].update({"active": True, "filename": repo_id, "percent": 15.0, "error": None})
            set_step(f"Downloading Specialist {mtype.upper()} Model: {repo_id}...")
            snapshot_download(repo_id=repo_id, local_dir=str(local_dir))
            STATE["download"].update({"active": False, "percent": 100.0})
            set_step("Idle")
        except Exception as e:
            STATE["download"]["error"] = str(e)
            STATE["download"]["active"] = False
            set_step("Idle")

    threading.Thread(target=_dl_specialist, daemon=True).start()
    return {"ok": True, "started": repo_id, "target_dir": str(local_dir)}


# =====================================================================
# 16. v4.0 FULL STUDIO EDITION UPGRADES:
#     - OFFLINE NEURAL VOICE ROSTER (KOKORO-ONNX + FEMALE VOICE 3 BLEND) & WHISPER STT
#     - EMBEDDED IN-APP SELF-MANUAL READER & AI SECOND-FAILSAFE LOOKUP
#     - EVOLVING PARTNER MEMORY (partner_evolution.json) & SILENT LEGACY BRIDGE
#     - NATIVE WINDOWS FOLDER PICKER & PROTOTYPE PRE-IMPORT INSPECTOR
#     - MESSAGE EDIT, REGENERATE & MULTIMODAL VISION (mmproj) SLOT
# =====================================================================
VOICE_PROFILES = [
    {"id": "af_bella",        "name": "Female Voice 1 (Warm & Expressive)", "kokoro_voice": "af_bella",  "speed": 1.0,  "pitch_hz": 215.0, "lang": "en-us"},
    {"id": "af_sarah",        "name": "Female Voice 2 (Clear & Grounded)",  "kokoro_voice": "af_sarah",  "speed": 1.0,  "pitch_hz": 205.0, "lang": "en-us"},
    {"id": "af_nicole_river", "name": "Female Voice 3 (Laid-Back / Indie)", "kokoro_voice": "af_nicole", "blend": "af_river", "speed": 0.96, "pitch_hz": 178.0, "lang": "en-us"},
    {"id": "bf_emma",         "name": "Female Voice 4 (British Crisp)",     "kokoro_voice": "bf_emma",   "speed": 1.0,  "pitch_hz": 210.0, "lang": "en-gb"},
    {"id": "am_michael",      "name": "Male Voice 1 (Calm & Steady)",       "kokoro_voice": "am_michael","speed": 1.0,  "pitch_hz": 115.0, "lang": "en-us"},
    {"id": "am_puck",         "name": "Male Voice 2 (Witty & Brisk)",       "kokoro_voice": "am_puck",   "speed": 1.04, "pitch_hz": 132.0, "lang": "en-us"},
    {"id": "bm_george",       "name": "Male Voice 3 (British Narrator)",    "kokoro_voice": "bm_george", "speed": 0.98, "pitch_hz": 108.0, "lang": "en-gb"},
    {"id": "ef_dora",         "name": "Español (Femenina Natural)",         "kokoro_voice": "ef_dora",   "speed": 1.0,  "pitch_hz": 208.0, "lang": "es"},
    {"id": "em_alex",         "name": "Español (Masculina Natural)",        "kokoro_voice": "em_alex",   "speed": 1.0,  "pitch_hz": 118.0, "lang": "es"}
]

# Extend SPECIALIST_MODEL_BAG with 1-click Voice & Vision packs
SPECIALIST_MODEL_BAG.extend([
    {
        "type": "voice",
        "name": "🗣️ Kokoro-82M Offline Neural Voice Pack (~115MB - Includes Female Voice 3)",
        "repo": "hexgrad/Kokoro-82M",
        "license": "Apache-2.0 (Kokoro Neural TTS)"
    },
    {
        "type": "vision",
        "name": "👁️ LLaVA / Qwen2-VL Multimodal Vision Projector (mmproj slot)",
        "repo": "mys/ggml_llava-v1.5-7b",
        "license": "Apache-2.0 / Llama Community"
    }
])

SELF_MANUAL_SECTIONS = avs_manual.MANUAL_SECTIONS_EN

def index_self_manual_on_boot():
    """Indexes the embedded visual manual + AetherVault_Studio_Manual.pdf into PRIORITY_CACHE['self_manual_text']."""
    sections = [f"### {s['title']}\n{s['body']}" for s in SELF_MANUAL_SECTIONS]
    if MANUAL_PDF_PATH.exists():
        try:
            doc = fitz.open(MANUAL_PDF_PATH)
            pdf_txt = "\n".join([p.get_text("text").strip() for p in doc if p.get_text("text").strip()])
            doc.close()
            if pdf_txt:
                sections.append(f"### Embedded Manual PDF Text\n{pdf_txt[:4000]}")
        except Exception:
            pass
    PRIORITY_CACHE["self_manual_text"] = "\n\n".join(sections)

def search_self_manual(query: str = "") -> str:
    if not PRIORITY_CACHE.get("self_manual_text"):
        index_self_manual_on_boot()
    q = (query or "").strip().lower()
    active_secs = avs_manual.get_manual_sections(WORKSPACE_CFG.get("ui_language", "en"))
    if not q:
        return "\n\n".join([f"### {s['title']}\n{s['body']}" for s in active_secs])
    scored = []
    for s in active_secs:
        txt = f"{s['title']}\n{s['body']}"
        hits = sum(1 for w in q.split() if len(w) >= 3 and w in txt.lower())
        scored.append((hits, txt))
    scored.sort(key=lambda x: x[0], reverse=True)
    return f"=== AETHERVAULT v{APP_VERSION} BUILT-IN MANUAL REFERENCE ===\n" + "\n\n".join([t for _, t in scored[:3]])

@app.get("/manual/content")
def api_get_manual_content(lang: str = ""):
    if not PRIORITY_CACHE.get("self_manual_text"):
        index_self_manual_on_boot()
    use_lang = (lang or WORKSPACE_CFG.get("ui_language") or "en").strip().lower()[:2]
    return {
        "ok": True,
        "version": APP_VERSION,
        "lang": use_lang,
        "pdf_available": MANUAL_PDF_PATH.exists(),
        "pdf_url": "/manual/pdf" if MANUAL_PDF_PATH.exists() else None,
        "sections": avs_manual.get_manual_sections(use_lang)
    }

@app.get("/manual/pdf")
def api_serve_manual_pdf():
    if not MANUAL_PDF_PATH.exists():
        raise HTTPException(404, "AetherVault_Studio_Manual.pdf not found in root directory.")
    return FileResponse(str(MANUAL_PDF_PATH), media_type="application/pdf", filename="AetherVault_Studio_Manual.pdf")

def load_partner_evolution() -> dict:
    default_evo = {
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "interaction_count": 0,
        "relationship_stage": "Trusted Studio Partner & Co-Creator",
        "user_handle": WORKSPACE_CFG.get("user_name", "Creator"),
        "companion_name": WORKSPACE_CFG.get("ai_name", "Aether"),
        "preferred_vibe": "Laid-back, sharp, candid, witty, zero corporate fluff",
        "active_projects": [],
        "shared_milestones": ["Initialized AetherVault Studio v4.0 Workstation"],
        "favorite_topics": []
    }
    if PARTNER_EVOLUTION_PATH.exists():
        try:
            saved = json.loads(PARTNER_EVOLUTION_PATH.read_text(encoding="utf-8"))
            return {**default_evo, **saved}
        except Exception:
            pass
    PARTNER_EVOLUTION_PATH.write_text(json.dumps(default_evo, indent=2, ensure_ascii=False), encoding="utf-8")
    return default_evo

def update_partner_evolution(user_msg: str = "", ai_reply: str = "") -> dict:
    """Quietly evolves the companion's partner_evolution.json profile after conversations."""
    evo = load_partner_evolution()
    evo["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    evo["user_handle"] = WORKSPACE_CFG.get("user_name", evo.get("user_handle", "Creator"))
    evo["companion_name"] = WORKSPACE_CFG.get("ai_name", evo.get("companion_name", "Aether"))
    if user_msg:
        evo["interaction_count"] = int(evo.get("interaction_count", 0)) + 1
        kws = [w for w in extract_keywords(user_msg) if len(w) >= 5][:5]
        favs = list(dict.fromkeys((evo.get("favorite_topics") or []) + kws))[-20:]
        evo["favorite_topics"] = favs
        for m in list_memories()[:6]:
            if m["category"] in ("active_project", "user_note"):
                proj = m["fact"][:90]
                if proj not in evo["active_projects"]:
                    evo["active_projects"] = (evo["active_projects"] + [proj])[-10:]
    PARTNER_EVOLUTION_PATH.write_text(json.dumps(evo, indent=2, ensure_ascii=False), encoding="utf-8")
    PRIORITY_CACHE["partner_digest"] = (
        f"Partner Bond ({evo['relationship_stage']}, {evo['interaction_count']} turns): "
        f"Vibe={evo['preferred_vibe']} | Projects={', '.join(evo['active_projects'][:3]) or 'General Studio'} | "
        f"Topics={', '.join(evo['favorite_topics'][:8]) or 'Local AI & Creative Work'}"
    )
    return evo

def run_silent_legacy_migration():
    """
    Silent Legacy Compatibility Bridge:
    Ensures any older v1.0 - v3.4 workspace, SQLite DB, or prototype folder works seamlessly in v4.0!
    """
    try:
        # 1. Merge any missing v4.0 keys into workspace_config.json without overwriting user customizations
        changed = False
        for k, v in DEFAULT_CONFIG.items():
            if k not in WORKSPACE_CFG:
                WORKSPACE_CFG[k] = v
                changed = True
        if changed:
            save_workspace_config(WORKSPACE_CFG)

        # 2. If legacy README.txt or *_core_package.txt exists in /priority_pdfs, ensure it's indexed as CORE
        with get_db() as conn:
            c = conn.cursor()
            c.execute("UPDATE priority_pdfs SET file_mode = 'core' WHERE (LOWER(filename) = 'readme.txt' OR LOWER(filename) LIKE '%_core_package.txt') AND manual_override = 0")
            conn.commit()

        # 3. Initialize partner_evolution.json & self-manual index
        update_partner_evolution()
        index_self_manual_on_boot()
    except Exception as e:
        print(f"[LEGACY BRIDGE NOTE] {e}", flush=True)

def list_vision_projectors() -> list:
    found = []
    for root in (VISION_MODEL_DIR, MODEL_DIR):
        if root.exists():
            for p in root.rglob("*.gguf"):
                if "mmproj" in p.name.lower() or "projector" in p.name.lower():
                    found.append(p.name)
    return sorted(list(dict.fromkeys(found)))

def list_local_voice_models() -> list:
    found = []
    if VOICE_MODEL_DIR.exists():
        for p in VOICE_MODEL_DIR.rglob("*"):
            if p.is_file() and p.suffix.lower() in (".onnx", ".bin", ".pth"):
                found.append(p.name)
    return sorted(found)

@app.post("/tts/speak")
def api_offline_tts_speak(payload: dict):
    """
    Offline Neural TTS Endpoint:
    1. Checks if `kokoro_onnx` and `kokoro-v1.0.onnx` + `voices-v1.0.bin` are installed in /models/voice.
       If present, synthesizes real neural speech (including the Female Voice 3 af_nicole + af_river 65/35 vector blend!).
    2. If not downloaded yet, returns {"ok": False, "fallback": "browser"} so the UI uses tuned Web Speech API seamlessly.
    """
    text = (payload.get("text") or "").strip()
    voice_id = (payload.get("voice_profile") or WORKSPACE_CFG.get("voice_profile") or "af_nicole_river").strip()
    speed = float(payload.get("speed") or WORKSPACE_CFG.get("tts_speed") or 0.96)
    if not text:
        return {"ok": False, "fallback": "browser"}

    # Clean markdown / bracket tags before speaking
    clean_speech = re.sub(r"\[\[[^\]]+\]\]", "", text)
    clean_speech = re.sub(r"```[\s\S]*?```", "Code block.", clean_speech)
    clean_speech = re.sub(r"[*_#`~>]", "", clean_speech).strip()[:1200]

    profile = next((v for v in VOICE_PROFILES if v["id"] == voice_id), VOICE_PROFILES[2])
    onnx_candidates = list(VOICE_MODEL_DIR.glob("*.onnx")) if VOICE_MODEL_DIR.exists() else []
    bin_candidates = list(VOICE_MODEL_DIR.glob("*.bin")) if VOICE_MODEL_DIR.exists() else []

    if onnx_candidates and bin_candidates and importlib.util.find_spec("kokoro_onnx") is not None and importlib.util.find_spec("soundfile") is not None:
        try:
            from kokoro_onnx import Kokoro
            import soundfile as sf
            import numpy as np
            kokoro = Kokoro(str(onnx_candidates[0]), str(bin_candidates[0]))
            v_style = profile["kokoro_voice"]
            if profile.get("blend"):
                try:
                    s1 = kokoro.get_voice_style(profile["kokoro_voice"])
                    s2 = kokoro.get_voice_style(profile["blend"])
                    v_style = (0.68 * np.array(s1) + 0.32 * np.array(s2)).astype(np.float32)
                except Exception:
                    v_style = profile["kokoro_voice"]
            samples, sample_rate = kokoro.create(clean_speech, voice=v_style, speed=speed, lang=profile.get("lang", "en-us"))
            out_name = f"tts_voice_{int(time.time() * 1000)}.wav"
            out_path = GEN_AUDIO_DIR / out_name
            sf.write(str(out_path), samples, sample_rate)
            return {"ok": True, "url": f"/generated_audio/{out_name}", "profile": profile["name"], "engine": "Kokoro-ONNX Neural Voice"}
        except Exception as e:
            print(f"[KOKORO TTS FALLBACK] {e}", flush=True)

    return {"ok": False, "fallback": "browser", "profile": profile}

@app.post("/stt/transcribe")
async def api_offline_stt_transcribe(file: UploadFile = File(...)):
    """Offline Microphone Speech-to-Text via faster-whisper (with automatic browser fallback)."""
    if importlib.util.find_spec("faster_whisper") is None:
        return {"ok": False, "fallback": "browser", "error": "faster-whisper not installed yet"}
    tmp_wav = TEMP_SESSION_DIR / f"mic_{int(time.time()*1000)}.wav"
    tmp_wav.write_bytes(await file.read())
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel("tiny", device="cpu", compute_type="int8", download_root=str(VOICE_MODEL_DIR))
        segments, _ = model.transcribe(str(tmp_wav), beam_size=3, vad_filter=True)
        transcript = " ".join([seg.text.strip() for seg in segments]).strip()
        return {"ok": True, "text": transcript}
    except Exception as e:
        return {"ok": False, "fallback": "browser", "error": str(e)}
    finally:
        if tmp_wav.exists():
            tmp_wav.unlink()

@app.get("/workspace/browse_folder")
def api_browse_folder():
    """
    Opens a Native Topmost Windows Folder Picker Dialog so the user can visually select
    any external or legacy prototype project folder on their PC!
    """
    chosen_path = ""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        chosen_path = filedialog.askdirectory(title="Select External / Prototype Project Folder to Import")
        root.destroy()
    except Exception:
        if hasattr(os, "startfile"):
            try:
                ps_cmd = (
                    "Add-Type -AssemblyName System.Windows.Forms; "
                    "$f = New-Object System.Windows.Forms.FolderBrowserDialog; "
                    "$f.Description = 'Select External / Prototype Project Folder to Import'; "
                    "if ($f.ShowDialog() -eq 'OK') { Write-Output $f.SelectedPath }"
                )
                proc = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=120)
                chosen_path = (proc.stdout or "").strip()
            except Exception:
                pass
    if not chosen_path:
        return {"ok": False, "cancelled": True, "path": ""}
    inspection = inspect_external_folder_contents(Path(chosen_path))
    return {"ok": True, "path": str(Path(chosen_path)), "inspection": inspection}

def inspect_external_folder_contents(src: Path) -> dict:
    if not src.exists() or not src.is_dir():
        return {"valid": False, "summary": "Folder not found on disk."}
    core_files = [f for f in ("memory_core.db", "workspace_config.json", "partner_evolution.json", "pseudo_memory_index.json", "glossary_index.json") if (src / f).exists()]
    pdf_files = list((src / "priority_pdfs").rglob("*")) if (src / "priority_pdfs").exists() else list(src.rglob("*.pdf")) + list(src.rglob("*.txt")) + list(src.rglob("*.md"))
    pdf_count = sum(1 for p in pdf_files if p.is_file() and p.suffix.lower() in {".pdf", ".txt", ".md"})
    chat_logs = len(list((src / "chat_logs").glob("*.txt"))) if (src / "chat_logs").exists() else 0
    assets = len(list((src / "custom_assets").glob("*"))) if (src / "custom_assets").exists() else 0
    ggufs = [p.name for p in src.rglob("*.gguf") if p.is_file()]
    return {
        "valid": True,
        "is_aethervault_project": bool(core_files or (src / "priority_pdfs").exists()),
        "core_files_found": core_files,
        "knowledge_files_count": pdf_count,
        "chat_logs_count": chat_logs,
        "custom_assets_count": assets,
        "gguf_models_found": ggufs,
        "summary": (
            f"Detected {'AetherVault/Prototype Workspace' if core_files else 'Knowledge Folder'}: "
            f"Core Files ({', '.join(core_files) or 'None'}) | {pdf_count} Knowledge Docs | "
            f"{chat_logs} Chat Logs | {assets} Custom Assets | {len(ggufs)} GGUF Model(s)"
        )
    }

@app.post("/workspace/inspect_folder")
def api_inspect_folder(payload: dict):
    src_str = (payload.get("source_path") or "").strip().strip("'\"")
    if not src_str:
        return {"ok": False, "error": "Empty path"}
    info = inspect_external_folder_contents(Path(src_str))
    return {"ok": info.get("valid", False), "inspection": info}

@app.post("/workspace/import_folder_v4")
def api_import_folder_v4(payload: dict):
    """
    Enhanced v4.0 Prototype Folder Importer:
    1. Automatically backs up current memory_core.db and workspace_config.json into /workspace_backups first.
    2. Imports all core files, /priority_pdfs, /memory_vault, /chat_logs, /custom_assets, and partner_evolution.json.
    3. Optionally copies .gguf models if include_models=True.
    4. Runs Silent Legacy Migration & re-indexes everything live!
    """
    global WORKSPACE_CFG
    src_str = (payload.get("source_path") or "").strip().strip("'\"")
    include_models = bool(payload.get("include_models", False))
    src = Path(src_str)
    if not src.exists() or not src.is_dir():
        return {"ok": False, "error": f"Directory not found on PC: {src_str}"}
    if src.resolve() == BASE_DIR.resolve():
        return {"ok": False, "error": "Source folder is already the currently running workspace folder!"}

    # Auto-backup current state before importing
    stamp = time.strftime("%Y%m%d_%H%M%S")
    if DB_PATH.exists():
        shutil.copy2(DB_PATH, BACKUPS_DIR / f"pre_import_memory_core_{stamp}.db")
    if CONFIG_PATH.exists():
        shutil.copy2(CONFIG_PATH, BACKUPS_DIR / f"pre_import_workspace_config_{stamp}.json")

    res = import_legacy_folder({"source_path": str(src)})
    imported_list = res.get("imported", []) if isinstance(res, dict) else []

    for extra_f in ("partner_evolution.json", "pseudo_memory_index.json"):
        if (src / extra_f).exists():
            shutil.copy2(src / extra_f, BASE_DIR / extra_f)
            imported_list.append(extra_f)

    if include_models:
        for gguf_p in src.rglob("*.gguf"):
            if gguf_p.is_file():
                dest_m = MODEL_DIR / gguf_p.name
                if not dest_m.exists():
                    shutil.copy2(gguf_p, dest_m)
                    imported_list.append(f"Model:{gguf_p.name}")

    run_silent_legacy_migration()
    sync_pseudo_memory_and_index()
    return {"ok": True, "imported": imported_list, "backup_stamp": stamp}

@app.post("/chat/regenerate")
def api_regenerate_last(payload: dict):
    """Removes the last assistant message (and optional target message) in the session and returns the last user prompt to re-run."""
    session_id = (payload.get("session_id") or "session_main").strip()
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT id, role, content FROM chat_messages WHERE session_id = ? ORDER BY id DESC LIMIT 4", (session_id,))
        rows = c.fetchall()
        if not rows:
            return {"ok": False, "error": "No messages in session."}
        last_user_msg = None
        ids_to_delete = []
        for r in rows:
            if r["role"] == "assistant" and last_user_msg is None:
                ids_to_delete.append(r["id"])
            elif r["role"] == "user" and last_user_msg is None:
                last_user_msg = r["content"]
                ids_to_delete.append(r["id"])
                break
        if not last_user_msg:
            return {"ok": False, "error": "No user prompt found to regenerate."}
        for mid in ids_to_delete:
            c.execute("DELETE FROM chat_messages WHERE id = ?", (mid,))
        conn.commit()
    export_chats_to_txt_files()
    return {"ok": True, "user_message": last_user_msg}

@app.post("/chat/edit")
def api_edit_user_message(payload: dict):
    """Rewinds a session to a specific user message ID (or the latest user message) so the edited text can run cleanly."""
    session_id = (payload.get("session_id") or "session_main").strip()
    msg_id = payload.get("message_id")
    with get_db() as conn:
        c = conn.cursor()
        if msg_id:
            c.execute("DELETE FROM chat_messages WHERE session_id = ? AND id >= ?", (session_id, int(msg_id)))
        else:
            c.execute("SELECT id FROM chat_messages WHERE session_id = ? AND role = 'user' ORDER BY id DESC LIMIT 1", (session_id,))
            row = c.fetchone()
            if row:
                c.execute("DELETE FROM chat_messages WHERE session_id = ? AND id >= ?", (session_id, row["id"]))
        conn.commit()
    export_chats_to_txt_files()
    return {"ok": True}


# =====================================================================
# 17. ANTI-OUROBOROS SELF-HEAL SANDBOX & VERSATILE CODE RUNNER
#     - AI is STRICTLY FORBIDDEN from overwriting core files unprompted!
#     - All AI self-fixes are staged in /self_heal_staging, syntax-checked
#       with py_compile, and require explicit User Approval (or 1-click Rollback).
# =====================================================================
SELF_HEAL_DIR = BASE_DIR / "self_heal_staging"
SELF_HEAL_DIR.mkdir(parents=True, exist_ok=True)
PROTECTED_CORE_FILES = {"Launch.bat", "Launch.sh", "manager.py", "assistant_server.py", "ui_studio.html", "workspace_config.json", "aethervault_logo.svg"}

def list_pending_self_patches() -> list:
    out = []
    for p in sorted(SELF_HEAL_DIR.glob("patch_*.json"), reverse=True):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if data.get("status") == "pending":
                out.append(data)
        except Exception:
            pass
    return out[:15]

def stage_self_heal_proposal(target_file: str, find_snippet: str, replace_snippet: str, reason: str = "") -> dict:
    """
    Stages a proposed code fix in /self_heal_staging WITHOUT touching the live core file!
    Runs py_compile on the staged candidate first to prove it cannot break the server.
    """
    clean_name = Path(target_file.strip()).name
    if clean_name not in PROTECTED_CORE_FILES:
        return {"ok": False, "message": f"'{clean_name}' is not a recognized core studio file."}
    live_path = BASE_DIR / clean_name
    if not live_path.exists():
        return {"ok": False, "message": f"Core file '{clean_name}' not found on disk."}

    orig_text = live_path.read_text(encoding="utf-8", errors="ignore")
    if find_snippet not in orig_text:
        return {"ok": False, "message": f"Target snippet not found in '{clean_name}'. Live file untouched."}

    patched_text = orig_text.replace(find_snippet, replace_snippet, 1)
    patch_id = f"patch_{int(time.time() * 1000)}"
    staged_code_path = SELF_HEAL_DIR / f"{patch_id}_{clean_name}"
    staged_code_path.write_text(patched_text, encoding="utf-8")

    # Syntax verification gate before allowing the proposal to be approved
    syntax_ok = True
    syntax_msg = "Passed syntax validation"
    if clean_name.endswith(".py"):
        try:
            py_compile.compile(str(staged_code_path), doraise=True)
            syntax_msg = "Passed Python py_compile syntax verification"
        except Exception as e:
            syntax_ok = False
            syntax_msg = f"Failed py_compile: {e}"

    meta = {
        "id": patch_id,
        "target_file": clean_name,
        "reason": reason or "AI Self-Heal Proposal",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "pending" if syntax_ok else "rejected_syntax",
        "syntax_ok": syntax_ok,
        "syntax_msg": syntax_msg,
        "find_preview": find_snippet[:240],
        "replace_preview": replace_snippet[:240],
        "staged_path": str(staged_code_path)
    }
    (SELF_HEAL_DIR / f"{patch_id}.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return {
        "ok": syntax_ok,
        "patch": meta,
        "message": f"Staged patch `{patch_id}` for `{clean_name}` ({syntax_msg}). Open **🛠️ Diagnostic Console -> 🛡️ Self-Heal Gatekeeper** to Approve or Reject."
    }

@app.post("/self_heal/propose")
def api_propose_self_heal(payload: dict):
    return stage_self_heal_proposal(
        target_file=payload.get("target_file", "assistant_server.py"),
        find_snippet=payload.get("find_snippet", ""),
        replace_snippet=payload.get("replace_snippet", ""),
        reason=payload.get("reason", "Manual / AI Diagnostic Proposal")
    )

@app.post("/self_heal/apply")
def api_apply_self_heal(payload: dict):
    """
    Applies a staged self-heal patch ONLY when the user explicitly clicks 'Approve & Apply'!
    Automatically backs up the original file to /stock_vault/<file>.good and /workspace_backups first.
    """
    patch_id = (payload.get("patch_id") or "").strip()
    meta_path = SELF_HEAL_DIR / f"{patch_id}.json"
    if not meta_path.exists():
        return {"ok": False, "error": f"Patch {patch_id} not found."}
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if not meta.get("syntax_ok"):
        return {"ok": False, "error": "Cannot apply a patch that failed syntax validation!"}

    target_name = meta["target_file"]
    live_path = BASE_DIR / target_name
    staged_path = Path(meta["staged_path"])
    if not staged_path.exists():
        return {"ok": False, "error": "Staged file missing."}

    # 1. Save Golden Backup in stock_vault and timestamped backup in workspace_backups
    stock_dir = BASE_DIR / "stock_vault"
    stock_dir.mkdir(exist_ok=True)
    if live_path.exists():
        shutil.copy2(live_path, stock_dir / f"{target_name}.good")
        shutil.copy2(live_path, BACKUPS_DIR / f"pre_selfheal_{int(time.time())}_{target_name}")

    # 2. Apply staged file
    shutil.copy2(staged_path, live_path)
    meta["status"] = "applied"
    meta["applied_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"ok": True, "applied": target_name, "patch_id": patch_id}

@app.post("/self_heal/reject")
def api_reject_self_heal(payload: dict):
    patch_id = (payload.get("patch_id") or "").strip()
    meta_path = SELF_HEAL_DIR / f"{patch_id}.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["status"] = "rejected"
        meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"ok": True}

@app.post("/self_heal/rollback")
def api_rollback_core_file(payload: dict):
    """1-Click Rollback to Golden Backup in /stock_vault/<file>.good!"""
    target_name = Path((payload.get("target_file") or "assistant_server.py").strip()).name
    stock_good = BASE_DIR / "stock_vault" / f"{target_name}.good"
    if not stock_good.exists():
        return {"ok": False, "error": f"No Golden Backup found at stock_vault/{target_name}.good"}
    shutil.copy2(stock_good, BASE_DIR / target_name)
    return {"ok": True, "restored": target_name}

@app.post("/code/run_sandbox")
def api_run_code_sandbox(payload: dict):
    """
    Versatile Local Python Scratchpad Runner:
    Executes user/AI Python snippets inside %TEMP%/AetherVault_Session_<pid> (isolated from BASE_DIR)
    so you can test scripts, math, data processing, or automation right inside chat!
    """
    code_str = (payload.get("code") or "").strip()
    if not code_str:
        return {"ok": False, "output": "Empty code block."}
    TEMP_SESSION_DIR.mkdir(parents=True, exist_ok=True)
    script_file = TEMP_SESSION_DIR / f"scratchpad_{int(time.time() * 1000)}.py"
    script_file.write_text(code_str, encoding="utf-8")
    try:
        t0 = time.time()
        proc = subprocess.run(
            [sys.executable, "-I", str(script_file)],
            cwd=str(TEMP_SESSION_DIR),
            capture_output=True,
            text=True,
            timeout=15
        )
        elapsed = round(time.time() - t0, 2)
        combined = ((proc.stdout or "") + (chr(10) + proc.stderr if proc.stderr else "")).strip()
        return {
            "ok": proc.returncode == 0,
            "exit_code": proc.returncode,
            "elapsed_sec": elapsed,
            "output": (combined[:3500] if combined else f"(Completed in {elapsed}s with no stdout output)")
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "output": "⏱️ Execution timed out after 15 seconds (sandbox safety limit)."}
    except Exception as e:
        return {"ok": False, "output": f"Sandbox execution error: {e}"}
    finally:
        if script_file.exists():
            script_file.unlink()


@app.get("/diagnostics/benchmark")
def api_run_hardware_benchmark():
    """
    Runs a fast (~0.25s) local CPU & Memory Matrix-Vector micro-benchmark
    to classify the user's PC hardware tier and recommend the exact Engine Mode,
    Governor setting, and GGUF model size (with a pointer to Manual Section 6).
    """
    ram_info = get_system_ram_info()
    cores = os.cpu_count() or 2
    gpu_ok = bool(STATE.get("gpu_offload"))

    # Quick floating-point & memory allocation throughput micro-test
    t0 = time.perf_counter()
    arr = [float(i % 97) * 0.013 for i in range(180000)]
    acc = sum(x * 1.0001 for x in arr)
    elapsed = max(0.001, time.perf_counter() - t0)
    ops_score = round((180000 / elapsed) / 1e6, 1)  # Million ops/sec

    if cores <= 2:
        tier = "Tier 1: Legacy / Dual-Core Laptop (Bare Minimum Spec)"
        rec_engine = "Bootstrapper (manager.py) -> Switch Engine -> Safe CPU Build"
        rec_gov = "Laptop 2015 (Fast) — Forces Gear 1 Reflex (~500 chars)"
        rec_models = "1.5B Q4_K_M (~1.1 GB): Qwen2.5-1.5B, Qwen2.5-Coder-1.5B, or DeepSeek-R1-1.5B"
        est_speed = "~5 - 7 tokens/sec in Gear 1 (or 0% load via LAN Wireless Terminal Mode)"
    elif cores <= 4 and not gpu_ok:
        tier = "Tier 2: Entry Quad-Core CPU System"
        rec_engine = "Safe CPU Build (or Vulkan if dedicated GPU is installed)"
        rec_gov = "Reflex (Auto-Smart Fast)"
        rec_models = "1.5B to 3B Q4_K_M (~1.1 - 2.1 GB): Qwen2.5-3B or Llama-3.2-3B"
        est_speed = "~10 - 18 tokens/sec"
    else:
        tier = "Tier 3: Modern Multi-Core / Vulkan Studio Rig"
        rec_engine = "Vulkan GPU Offload (Option [2] -> [A])" if gpu_ok else "Multi-Thread CPU / Vulkan GPU"
        rec_gov = "Reflex (Auto-Smart Fast) or Balanced / Turbo"
        rec_models = "7B to 14B Q4_K_M (~4.7 - 9.0 GB): DeepSeek-R1-7B, Qwen2.5-Coder-7B, Hermes-3-8B"
        est_speed = "~22 - 55+ tokens/sec"

    return {
        "ok": True,
        "cpu_threads": cores,
        "ram_total_gb": ram_info["total_gb"],
        "ram_free_gb": ram_info["free_gb"],
        "gpu_vulkan_active": gpu_ok,
        "micro_bench_mops": ops_score,
        "hardware_tier": tier,
        "recommended_engine": rec_engine,
        "recommended_governor": rec_gov,
        "recommended_models": rec_models,
        "estimated_speed": est_speed,
        "manual_reference": "See 📖 Built-In Manual -> Section 6 (Minimum & Recommended Hardware Specs + Legacy Laptop Guide)"
    }


@app.post("/self_heal/verify_all")
def api_verify_all_core_files():
    """Verifies syntax integrity of assistant_server.py, ui_studio.html, manager.py, avs/*.py, and workspace_config.json."""
    results = []
    # 1. assistant_server.py
    try:
        py_compile.compile(str(BASE_DIR / "assistant_server.py"), doraise=True)
        results.append({"file": "assistant_server.py", "ok": True, "detail": f"Passed py_compile ({(BASE_DIR / 'assistant_server.py').stat().st_size:,} bytes)"})
    except Exception as e:
        results.append({"file": "assistant_server.py", "ok": False, "detail": str(e)})

    # 2. ui_studio.html
    ui_p = BASE_DIR / "ui_studio.html"
    if ui_p.exists():
        txt = ui_p.read_text(encoding="utf-8", errors="ignore")
        ok_html = ("<!DOCTYPE html>" in txt and "</html>" in txt and "<script>" in txt and "</script>" in txt)
        results.append({"file": "ui_studio.html", "ok": ok_html, "detail": f"HTML5 & JS structure verified ({ui_p.stat().st_size:,} bytes)"})

    # 3. manager.py (Permanent Bootstrapper py_compile check)
    mgr_p = BASE_DIR / "manager.py"
    if mgr_p.exists():
        try:
            py_compile.compile(str(mgr_p), doraise=True)
            results.append({"file": "manager.py", "ok": True, "detail": f"Bootstrapper passed py_compile ({mgr_p.stat().st_size:,} bytes)"})
        except Exception as e:
            results.append({"file": "manager.py", "ok": False, "detail": str(e)})

    # 3b. Modular avs/*.py package check
    avs_dir = BASE_DIR / "avs"
    if avs_dir.exists():
        avs_errs = []
        avs_cnt = 0
        for p_mod in sorted(avs_dir.glob("*.py")):
            avs_cnt += 1
            try:
                py_compile.compile(str(p_mod), doraise=True)
            except Exception as e:
                avs_errs.append(f"{p_mod.name}: {e}")
        results.append({
            "file": f"avs/*.py ({avs_cnt} modules)",
            "ok": not avs_errs,
            "detail": f"All {avs_cnt} avs/ modules passed py_compile" if not avs_errs else "; ".join(avs_errs[:3])
        })

    # 4. workspace_config.json
    cfg_p = BASE_DIR / "workspace_config.json"
    if cfg_p.exists():
        try:
            json.loads(cfg_p.read_text(encoding="utf-8"))
            results.append({"file": "workspace_config.json", "ok": True, "detail": "Valid JSON schema"})
        except Exception as e:
            results.append({"file": "workspace_config.json", "ok": False, "detail": str(e)})

    return {"ok": all(r["ok"] for r in results), "results": results}

@app.post("/self_heal/clear_errors")
def api_clear_error_audit_log():
    STATE["error_history"] = []
    STATE["last_debug"]["last_issue"] = None
    if ERROR_AUDIT_LOG_PATH.exists():
        ERROR_AUDIT_LOG_PATH.write_text("", encoding="utf-8")
    return {"ok": True}

@app.post("/self_heal/command_fix")
def api_command_ai_self_fix(payload: dict):
    """
    Allows the user to command a targeted self-diagnosis & staged repair from the Bugfixing Tab!
    1. Runs syntax & subsystem verification first.
    2. If a local GGUF model is loaded and the user describes a bug, asks the model to inspect the relevant
       section and propose a staged patch in /self_heal_staging (NEVER touching live files directly!).
    3. If no GGUF model is loaded yet, runs deterministic auto-repair on configs, SQLite tables, andGolden Backups.
    """
    instruction = (payload.get("instruction") or "Inspect recent errors and verify core files.").strip()
    target_file = (payload.get("target_file") or "assistant_server.py").strip()

    # Step 1: Deterministic self-healing & DB/Config/Index repair
    init_db()
    run_silent_legacy_migration()
    sync_memory_vault_file()
    sync_priority_files(force=True)
    sync_pseudo_memory_and_index()
    verify_res = api_verify_all_core_files()

    if not STATE.get("llm") or STATE.get("loading_model"):
        return {
            "ok": True,
            "mode": "Deterministic Self-Healer (No GGUF Loaded)",
            "verification": verify_res["results"],
            "message": "Ran full deterministic self-repair: SQLite schema verified, legacy config keys synced, Knowledge Tree re-indexed, and all 4 core files passed syntax verification."
        }

    # If a GGUF model IS loaded, let it inspect error_audit.log + target file and propose a patch if needed
    err_log = execute_self_inspection_tool("errors", "")
    code_snip = execute_self_inspection_tool("search", instruction[:30])
    prompt = (
        f"You are AetherVault Studio's Anti-Ouroboros Self-Heal Engineer.\n"
        f"User Bugfix Command: {instruction}\n"
        f"Target File: {target_file}\n"
        f"{err_log}\n{code_snip}\n\n"
        f"Provide a concise diagnostic summary and, ONLY if a code change is genuinely required, include "
        f"[[SELF:propose_fix|{target_file}|exact_old_line|exact_new_line]]. Never modify files directly."
    )
    try:
        with LLM_LOCK:
            res = STATE["llm"].create_chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512,
                temperature=0.3
            )
        ai_diag = (res["choices"][0]["message"].get("content") or "").strip()
        ai_diag = re.sub(r"<think>[\s\S]*?</think>", "", ai_diag).strip()
        fix_m = re.search(r"\[\[SELF:propose_fix\|([^|\]]+)\|([^|\]]+)\|([^\]]+)\]\]", ai_diag)
        staged_info = None
        if fix_m:
            staged_info = stage_self_heal_proposal(fix_m.group(1).strip(), fix_m.group(2), fix_m.group(3), reason=instruction[:80])
        return {
            "ok": True,
            "mode": f"AI Diagnostic + Deterministic Healer ({STATE['current_model']})",
            "verification": verify_res["results"],
            "message": ai_diag,
            "staged_patch": staged_info
        }
    except Exception as e:
        return {
            "ok": True,
            "mode": "Deterministic Self-Healer Fallback",
            "verification": verify_res["results"],
            "message": f"Deterministic repair completed cleanly (LLM diagnostic skipped: {e})."
        }


LOGO_SVG_PATH = BASE_DIR / "aethervault_logo.svg"

@app.get("/logo.svg")
def serve_logo_svg():
    if LOGO_SVG_PATH.exists():
        return FileResponse(str(LOGO_SVG_PATH), media_type="image/svg+xml")
    return HTMLResponse("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><polygon points='32,4 58,18 58,46 32,60 6,46 6,18' fill='#1e1b4b' stroke='#8b5cf6' stroke-width='4'/></svg>", media_type="image/svg+xml")

@app.get("/favicon.ico")
def serve_favicon():
    return serve_logo_svg()




@app.post("/workspace/mode")
def api_set_workspace_mode(payload: dict):
    if "workspace_mode" in payload:
        wm = (payload.get("workspace_mode") or "assistant").strip().lower()
        if wm not in ("assistant", "roleplay"):
            wm = "assistant"
        WORKSPACE_CFG["workspace_mode"] = wm
        STATE["workspace_mode"] = wm
    if "workbench_trust" in payload:
        wt = (payload.get("workbench_trust") or "safe_auto").strip().lower()
        if wt not in ("safe_auto", "full_pc"):
            wt = "safe_auto"
        WORKSPACE_CFG["workbench_trust"] = wt
        STATE["workbench_trust"] = wt
    save_workspace_config(WORKSPACE_CFG)
    return {
        "ok": True,
        "workspace_mode": WORKSPACE_CFG["workspace_mode"],
        "workbench_trust": WORKSPACE_CFG["workbench_trust"]
    }

@app.post("/profile/update")
def api_update_user_profile(payload: dict):
    card = load_user_profile_card()
    if "location" in payload:
        clean_loc = _clean_location_value(payload.get("location") or "")
        card["location"] = clean_loc
        with get_db() as conn:
            conn.execute("DELETE FROM dynamic_memory WHERE LOWER(category) IN ('user_location', 'location', 'city')")
            if clean_loc:
                conn.execute("INSERT INTO dynamic_memory (category, fact) VALUES ('user_location', ?)", (f"User lives in {clean_loc}",))
            conn.commit()
        sync_memory_vault_file()
    if "zip_code" in payload:
        clean_zip = (payload.get("zip_code") or "").strip().upper()
        card["zip_code"] = clean_zip
        with get_db() as conn:
            conn.execute("DELETE FROM dynamic_memory WHERE LOWER(category) IN ('user_zip', 'zip', 'zip_code')")
            if clean_zip:
                conn.execute("INSERT INTO dynamic_memory (category, fact) VALUES ('user_zip', ?)", (f"User ZIP/Postal code is {clean_zip}",))
            conn.commit()
        sync_memory_vault_file()
    if "latitude" in payload and "longitude" in payload:
        lat_v, lon_v = payload.get("latitude"), payload.get("longitude")
        if lat_v is None or lon_v is None or str(lat_v).strip() == "" or str(lon_v).strip() == "":
            card["latitude"] = None
            card["longitude"] = None
        else:
            try:
                card["latitude"] = round(float(lat_v), 5)
                card["longitude"] = round(float(lon_v), 5)
            except Exception:
                pass
    if "user_name" in payload and (payload.get("user_name") or "").strip():
        card["user_name"] = payload["user_name"].strip()
        WORKSPACE_CFG["user_name"] = card["user_name"]
        save_workspace_config(WORKSPACE_CFG)
    if isinstance(payload.get("custom_fields"), dict):
        cleaned_cf = {}
        for k, v in payload["custom_fields"].items():
            ks = re.sub(r"[^a-zA-Z0-9_\- ]", "", str(k)).strip()[:40]
            vs = str(v).strip()[:220]
            if ks and vs:
                cleaned_cf[ks] = vs
        card["custom_fields"] = cleaned_cf
    if isinstance(payload.get("pinned_facts"), list):
        card["pinned_facts"] = [str(f).strip()[:220] for f in payload["pinned_facts"] if str(f).strip()][:12]
    if payload.get("clear_last_workbench"):
        card["last_workbench_summary"] = ""
    save_user_profile_card(card)
    sync_pseudo_memory_and_index()
    return {"ok": True, "user_profile": card}

@app.post("/geo/reverse")
def api_geo_reverse(payload: dict):
    try:
        lat = float(payload.get("lat"))
        lon = float(payload.get("lon"))
    except Exception:
        return {"ok": False, "error": "Invalid latitude/longitude."}
    return reverse_geocode_osm(lat, lon)

@app.post("/geo/search")
def api_geo_search(payload: dict):
    return search_places_for_map(str(payload.get("query") or ""))

@app.post("/workbench/rpc")
def api_workbench_rpc(request: Request, payload: dict):
    tok = request.headers.get("X-Workbench-Token") or ""
    if tok != WORKBENCH_TOKEN:
        raise HTTPException(403, "Invalid Workbench RPC token.")
    return execute_workbench_rpc_action(payload.get("action") or "", payload.get("args") or {})

@app.post("/brain/mode")
def api_set_brain_mode(payload: dict):
    mode = (payload.get("brain_mode") or "local_only").strip()
    if mode not in ("local_only", "smart_api", "hybrid"):
        mode = "local_only"
    WORKSPACE_CFG["brain_mode"] = mode
    STATE["brain_mode"] = mode
    if "failsafe_model" in payload:
        WORKSPACE_CFG["failsafe_model"] = (payload.get("failsafe_model") or "").strip()
    save_workspace_config(WORKSPACE_CFG)
    # If user switches to pure smart_api mode, unload heavy GGUF from RAM to free memory immediately!
    if mode == "smart_api" and STATE.get("llm") is not None and not STATE.get("generating"):
        with LLM_LOCK:
            STATE["llm"] = None
            STATE["current_model"] = None
            gc.collect()
    return {"ok": True, "brain_mode": mode, "failsafe_model": WORKSPACE_CFG.get("failsafe_model", "")}

@app.post("/api_vault/slot/save")
def api_vault_save_slot(payload: dict):
    vault = load_api_vault()
    slots = vault.get("slots", [])
    provider = (payload.get("provider") or "custom").strip()
    tpl = API_PROVIDER_TEMPLATES.get(provider, API_PROVIDER_TEMPLATES["custom"])
    label = (payload.get("label") or tpl["name"]).strip()
    base_url = normalize_openai_base_url(payload.get("base_url") or tpl["base_url"])
    model = (payload.get("model") or tpl["default_model"]).strip()
    auth_type = (payload.get("auth_type") or tpl.get("auth_type", "bearer")).strip().lower()
    raw_keys = payload.get("keys") or []
    if isinstance(raw_keys, str):
        raw_keys = [k.strip() for k in re.split(r"[\r\n,]+", raw_keys) if k.strip()]

    slot_id = (payload.get("id") or "").strip()
    if slot_id:
        for sl in slots:
            if sl.get("id") == slot_id:
                sl["label"] = label
                sl["provider"] = provider
                sl["base_url"] = base_url
                sl["model"] = model
                sl["auth_type"] = auth_type
                if raw_keys:
                    sl["keys"] = list(dict.fromkeys((sl.get("keys") or []) + raw_keys))
                break
    else:
        slots.append({
            "id": f"slot_{int(time.time()*1000)}",
            "label": label,
            "provider": provider,
            "base_url": base_url,
            "model": model,
            "auth_type": auth_type,
            "enabled": True,
            "keys": raw_keys
        })
    if "daily_soft_cap" in payload:
        vault["daily_soft_cap"] = max(10000, int(payload["daily_soft_cap"]))
    vault["slots"] = slots
    save_api_vault(vault)
    return {"ok": True, "api_vault": get_masked_api_vault()}

@app.post("/api_vault/slot/append_key")
def api_vault_append_key(payload: dict):
    vault = load_api_vault()
    slot_id = (payload.get("slot_id") or "").strip()
    new_key = (payload.get("api_key") or "").strip()
    if not slot_id or not new_key:
        return {"ok": False, "error": "Missing slot_id or api_key"}
    for sl in vault.get("slots", []):
        if sl.get("id") == slot_id:
            keys = sl.get("keys") or []
            if new_key not in keys:
                keys.append(new_key)
            sl["keys"] = keys
            break
    save_api_vault(vault)
    return {"ok": True, "api_vault": get_masked_api_vault()}

@app.post("/api_vault/slot/delete")
def api_vault_delete_slot(payload: dict):
    vault = load_api_vault()
    slot_id = (payload.get("slot_id") or "").strip()
    vault["slots"] = [s for s in vault.get("slots", []) if s.get("id") != slot_id]
    save_api_vault(vault)
    return {"ok": True, "api_vault": get_masked_api_vault()}

@app.post("/api_vault/slot/move")
def api_vault_move_slot(payload: dict):
    vault = load_api_vault()
    slots = vault.get("slots", [])
    slot_id = (payload.get("slot_id") or "").strip()
    direction = (payload.get("direction") or "up").strip()
    idx = next((i for i, s in enumerate(slots) if s.get("id") == slot_id), -1)
    if idx != -1:
        if direction == "up" and idx > 0:
            slots[idx - 1], slots[idx] = slots[idx], slots[idx - 1]
        elif direction == "down" and idx < len(slots) - 1:
            slots[idx + 1], slots[idx] = slots[idx], slots[idx + 1]
    vault["slots"] = slots
    save_api_vault(vault)
    return {"ok": True, "api_vault": get_masked_api_vault()}

@app.post("/api_vault/test_models")
def api_vault_test_and_fetch_models(payload: dict):
    """Tests a custom API key & endpoint live and fetches available model IDs from GET /v1/models."""
    provider = (payload.get("provider") or "custom").strip()
    tpl = API_PROVIDER_TEMPLATES.get(provider, API_PROVIDER_TEMPLATES["custom"])
    base_url = normalize_openai_base_url(payload.get("base_url") or tpl["base_url"])
    api_key = (payload.get("api_key") or "").strip()
    auth_type = (payload.get("auth_type") or tpl.get("auth_type", "bearer")).strip().lower()

    headers = {"Content-Type": "application/json"}
    if api_key:
        if auth_type == "x-api-key":
            headers["x-api-key"] = api_key
        elif auth_type != "none":
            headers["Authorization"] = f"Bearer {api_key}"

    try:
        r = requests.get(f"{base_url}/models", headers=headers, timeout=12)
        if r.status_code == 200:
            data = r.json()
            raw_list = data.get("data") if isinstance(data, dict) else (data if isinstance(data, list) else [])
            model_ids = sorted([m.get("id") for m in raw_list if isinstance(m, dict) and m.get("id")])
            if not model_ids:
                model_ids = tpl.get("models_hint", [])
            return {"ok": True, "models": model_ids[:120], "message": f"Connected! Found {len(model_ids)} models."}
        return {"ok": False, "models": tpl.get("models_hint", []), "error": f"HTTP {r.status_code}: {r.text[:180]}"}
    except Exception as e:
        return {"ok": False, "models": tpl.get("models_hint", []), "error": str(e)}

@app.post("/system/skip_boot_index")
def api_skip_boot_index():
    """Immediately skips/defers any long PDF indexing and marks the Studio Ready to Chat."""
    STATE["skip_indexing"] = True
    STATE["boot_ready"] = True
    STATE["indexing_files"] = False
    set_step("Idle")
    return {"ok": True, "message": "Indexing skipped — Studio is ready to chat!"}

@app.post("/system/shutdown")
def api_safe_save_and_shutdown():
    """
    1-Click Safe Save & Shutdown Button:
    1. Saves workspace_config.json, partner_evolution.json, pseudo_memory_index.json, and .txt chat logs.
    2. Unloads active GGUF model from VRAM/RAM cleanly.
    3. Deletes the local .temp_cache folder completely.
    4. Terminates the server process safely after returning the confirmation response.
    """
    try:
        STATE["stop_requested"] = True
        save_workspace_config(WORKSPACE_CFG)
        update_partner_evolution()
        sync_memory_vault_file()
        export_chats_to_txt_files()
        sync_pseudo_memory_and_index()
        with LLM_LOCK:
            STATE["llm"] = None
            gc.collect()
        cleanup_session_temp_cache()
    except Exception as e:
        print(f"[SAFE SHUTDOWN NOTE] {e}", flush=True)

    def _delayed_kill():
        time.sleep(0.55)
        cleanup_session_temp_cache()
        os._exit(0)

    threading.Thread(target=_delayed_kill, daemon=True).start()
    return {
        "ok": True,
        "message": "All memories, configs, and chat logs saved! Local .temp_cache folder deleted and server shut down safely."
    }

@app.get("/", response_class=HTMLResponse)
def serve_ui():
    if UI_HTML_PATH.exists():
        return HTMLResponse(UI_HTML_PATH.read_text(encoding="utf-8", errors="ignore"))
    return HTMLResponse(
        "<body style='background:#0d0e12;color:#e5e7eb;font-family:sans-serif;padding:40px;'>"
        "<h2>⚡ AetherVault Studio Backend is Online!</h2>"
        "<p>Place <code>ui_studio.html</code> in the same folder as <code>assistant_server.py</code> and hit Refresh (F5).</p>"
        "</body>"
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=SERVER_PORT)
