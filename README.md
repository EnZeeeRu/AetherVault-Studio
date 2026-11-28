<div align="center">
  <img src="aethervault_logo.svg" alt="AetherVault Studio Logo" width="126" />&nbsp;&nbsp;<img src="release_emblem.svg" alt="v7.1 Lamppost Release Emblem" width="126" />

  <h1>AetherVault Studio v7.1 — Lamppost</h1>
  <p><strong>100% Portable, Zero-Footprint Local AI, Vault Cloud &amp; DLNA Media Server, PC Workbench &amp; Hardware Telemetry Workstation</strong></p>

  <p>
    <a href="https://github.com/EnZeeeRu/AetherVault-Studio/releases">
      <img src="https://img.shields.io/badge/Release-v7.1%20Lamppost-f59e0b?style=for-the-badge&logo=github" alt="Release v7.1 Lamppost" />
    </a>
    <img src="https://img.shields.io/badge/Python-3.10%2B-38bdf8?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+" />
    <img src="https://img.shields.io/badge/OS-Windows%20%7C%20macOS%20%7C%20Linux-64748b?style=for-the-badge" alt="Windows | macOS | Linux" />
    <img src="https://img.shields.io/badge/Code%20License-MIT-10b981?style=for-the-badge" alt="MIT License" />
    <img src="https://img.shields.io/badge/Assets%20%26%20Docs-CC%20BY--NC%204.0-f59e0b?style=for-the-badge" alt="CC BY-NC 4.0" />
  </p>

  <p>
    <a href="https://github.com/EnZeeeRu/AetherVault-Studio/releases">
      <img src="https://img.shields.io/badge/%E2%AC%87%EF%B8%8F%20Download%20Bootstrapper%20(3--File%20Launcher)-7c3aed?style=for-the-badge" alt="Download Bootstrapper" />
    </a>
    &nbsp;
    <a href="https://github.com/EnZeeeRu/AetherVault-Studio/raw/main/AetherVault_Studio_Manual.pdf">
      <img src="https://img.shields.io/badge/%F0%9F%93%96%20Download%20Manual%20(PDF)-0284c7?style=for-the-badge" alt="Download Manual PDF" />
    </a>
  </p>

  <p>
    <a href="#features">Features</a>
    &nbsp;•&nbsp;
    <a href="#architecture">Modular Architecture</a>
    &nbsp;•&nbsp;
    <a href="#specpulse">SpecPulse</a>
    &nbsp;•&nbsp;
    <a href="#quick-start">Quick Start</a>
    &nbsp;•&nbsp;
    <a href="#console-commands">Console Commands</a>
    &nbsp;•&nbsp;
    <a href="#changelog">Changelog</a>
    &nbsp;•&nbsp;
    <a href="#transparency">Privacy &amp; Transparency</a>
    &nbsp;•&nbsp;
    <a href="#license">License</a>
  </p>
</div>

---

<a id="features"></a>
## ✨ Key Features (`v7.1 Lamppost`)

| Module | What It Does |
| :--- | :--- |
| **✨ Modern Leo × Claude/Gemini UI (`avs/ui/`)** | Modular zero-build vanilla JS/CSS interface featuring a floating glassmorphic composer over your custom wallpaper, `/` Quick Actions &amp; custom `/skills` (`+ New`), unified `📎` media popover, inline multi-file thumbnail staging, full-window drag-and-drop + `Ctrl+V` paste, collapsible right controls drawer, and interactive zero-manual walkthroughs. |
| **🖼️ Full-Res Lossless Media &amp; Lightbox** | Preserves untouched full-resolution chat &amp; generated images in SQLite + `/custom_assets/chat_media/` across reloads, opens any image in a zoomable Media Lightbox, and upgrades Avatar (`512×512`) &amp; Wallpaper (`1920×1080+`) croppers with a **✨ Use Original** lossless bypass. |
| **☁️ Vault Cloud &amp; 📺 DLNA Media Server** | Built-in Nextcloud-style LAN file manager (`avs/cloud_files.py`) with Grid/List views, HTTP `206` byte-range streaming for every phone (iPhone Safari + Android Chrome), 1-click **Attach to Chat / Core / Lore**, and a toggleable pure-Python **DLNA / UPnP** server (`avs/dlna_server.py`) for **Roku Media Player** &amp; **VLC** (plus `.m3u` playlist fallback)—controllable from UI, Telegram, `manager.py`, or directly by the AI (`vault.toggle("dlna_enabled", True)`). |
| **✈️ Argo-Style Telegram Hub, Typing &amp; Stickers** | Guided 3-step setup (`Test &amp; Connect` + `Detect My Chat ID`), separated **✈️ Telegram Read-Only Mirror** (+ **↗️ Fork to Web Chat**), Argo-inspired compact in-place paginated menu &amp; chat switcher, 4-second context-aware `sendChatAction` animations (`typing`, `upload_photo`, `upload_document`, `record_voice`), emotion-mapped **Stickers** (`getStickerSet` pack import, `/addsticker`, anti-spam cooldown), and on-demand `🧠 Show Thought Process`. |
| **🧰 Robust FS Ops, App Relocation &amp; Introspect** | Cross-drive multi-threaded `robocopy`/`rsync` file ops (`avs/fs_ops.py`: `copy`, `move`, `rename`, `trash`, `relocate_app` with NTFS `mklink /J` junctions &amp; Windows `.lnk` shortcut rewriter) + live Workbench introspection (`avs/introspect.py`: `vault.inspect()`, `vault.api_probe()`, and automatic signature/method hints on errors). |
| **🧠 Evergreen-Speed Zero-Drop Brain** | Runs local `.gguf` models (**Gemma 4 E4B** default, native FP16 KV cache, static KV prefix lock, ~2.2 KB lean Operator prompt, post-turn background sync, Gear 1 Reflex) **or** BYOK Cloud API waterfall (Gemini, Groq, HF Router, OpenRouter, DeepSeek, Mistral, OpenAI, LAN rigs) with automatic local failsafe &amp; Idle Sleep RAM unloading. |
| **🌐 Cloud Lore Sync, i18n &amp; SpecPulse** | Sync `/priority_pdfs` via Nextcloud/WebDAV, Google Drive API v3, Google Doc/Drive URL pull, or local mirror; instant EN/ES localization + Lore-safe offline spellcheck + Argos Translate; and 60-FPS **SpecPulse** hardware telemetry + benchmark suite. |
| **🔄 Frozen 3-File Bootstrapper &amp; OTA Sync** | Distribute just 3 files (`Launch.bat`, `Launch.sh`, `manager.py`) with commit-pinned GitHub Tree Sync (ETag 304 + CRLF-safe + Python syntax gate) and SHA-256 `manifest.json` fallback. |

---

<a id="architecture"></a>
## 🧱 Modular Architecture (`avs/`)

AetherVault Studio `v7.1 Lamppost` cleanly separates its **3-File Bootstrapper** (`Launch.bat`, `Launch.sh`, `manager.py`) from its **Live Runtime** (`assistant_server.py`, `ui_studio.html`, `avs/ui/*`, and the modular `avs/` Python engines):

* **`avs/ui/`** — Zero-build browser ES/vanilla modules (`studio.css`, `media.js`, `composer.js`, `cloud.js`, `telegram.js`) served from `/avs_ui/` and synced automatically via OTA.
* **`avs/cloud_files.py` &amp; `avs/dlna_server.py`** — Nextcloud-style LAN drive with HTTP `206` byte-range streaming, `.m3u` playlist generator, and toggleable SSDP/UPnP `ContentDirectory:1` DLNA server for Roku TV &amp; VLC.
* **`avs/fs_ops.py` &amp; `avs/introspect.py`** — Native `robocopy`/`rsync` file operations, Recycle Bin trash, NTFS `mklink /J` app relocation, PowerShell `.lnk` shortcut engine, live Python/OpenAPI introspection, and automatic error signature hinting.
* **`avs/cloud_sync.py`** — Nextcloud/WebDAV, Google Drive API v3, 1-click Google Doc/Drive URL pull, and local mirror sync into `/priority_pdfs`.
* **`avs/contracts.py` / `memory_graph.py` / `referee.py` / `tool_registry.py` / `bridges.py` / `turn_pipeline.py` / `model_polish.py`** — Guardrail Blender, background SQLite memory compactor + 1-hop Keyword Mind-Map, Lore Attribution Referee, model-agnostic polisher, and Bluesky AT Protocol / Telegram helpers.
* **`avs/language_tools.py` / `manual_assets.py` / `platform_bridge.py` / `toolbox.py` / `workbench.py` / `hardware_monitor.py`** — EN/ES localization, Lore-safe offline spellcheck &amp; Argos Translate, illustrated bilingual manual, killable subprocess Workbench, and SpecPulse 60-FPS hardware telemetry.

---

<a id="specpulse"></a>
## 📊 SpecPulse :: Visual Hardware Telemetry &amp; Benchmark

Built directly into AetherVault Studio as a **zero-overhead on-demand overlay** (uses **0% CPU/GPU** when closed):

* **60-FPS Living Hardware Schematic:** Interactive PCB-style diagram showing real-time data flow between **CPU, RAM, GPU, Storage, and Motherboard**. Click any block to inspect specs.
* **True 64-Bit GPU VRAM Reader:** Reads `HardwareInformation.qwMemorySize` from the Windows Registry to bypass the 4 GB 32-bit WMI `AdapterRAM` cap, alongside live GPU 3D/Compute load &amp; dedicated VRAM usage.
* **Mini-Benchmark Reactor Suite:** Stress-tests Single-Core math, Multi-Core scaling, Memory bandwidth, and 128 MB Sequential Storage R/W inside isolated `.temp_cache` with automatic cleanup.

---

<a id="quick-start"></a>
## 🚀 Quick Start (Windows, macOS &amp; Linux / Unix)

1. Download **`AetherVault_Studio_v7.1_Lamppost_Bootstrapper.zip`** (`Launch.bat`, `Launch.sh`, `manager.py`) from the [Releases Page](https://github.com/EnZeeeRu/AetherVault-Studio/releases) — or grab the full repo archive.
2. Extract into any portable folder.
3. Launch using the command for your operating system:

| Platform | How to Start | Notes |
| :--- | :--- | :--- |
| **🪟 Windows** | Double-click **`Launch.bat`** | Auto-detects Python 3.10+ (or offers `winget` install) and opens the Bootstrapper &amp; Control Center. |
| **🍎 macOS** | Open Terminal and run:<br>`chmod +x Launch.sh && ./Launch.sh` | Auto-detects Python 3.10+ (or offers `brew install python@3.11`) and launches `manager.py`. |
| **🐧 Linux / Unix** | Open Terminal and run:<br>`chmod +x Launch.sh && ./Launch.sh` | Supports `apt`, `dnf`, `pacman`, and `zypper`. On headless servers/SSH, run `./Launch.sh --cli`. |

4. Click **1. Launch AetherVault Server**—`manager.py` auto-hydrates any missing runtime files from GitHub, builds `.venv`, and opens the Studio UI (`http://127.0.0.1:8000` / `http://<LAN_IP>:8000`).
5. Run `python tests/smoke.py` (or Option `9` in `manager.py`) anytime to run the full automated integrity suite.

---

<a id="console-commands"></a>
## 💻 Bootstrapper, Web Terminal &amp; Telegram Commands

| Command | Action |
| :--- | :--- |
| `/help` / `⌨️ Cmds` | Show searchable command cheat sheet (Terminal, Telegram, `vault.*`, Hotkeys) |
| `/status` / `/specs` | Live model, GPU/CPU, RAM, mode, LAN URL &amp; deep SpecPulse hardware specs |
| `/dlna on\|off` / `/cloud on\|off` | Toggle built-in DLNA/UPnP Media Server (Roku/VLC) or Vault Cloud LAN File Server |
| `/unload` / `/wake` / `/sleep N` | Free RAM/VRAM into Idle Sleep, wake GGUF model, or set idle auto-sleep minutes |
| `/inject <cat> \| <fact>` | Save a fact directly into Priority #1 SQLite Memory Vault |
| `/toggle <key> <val>` | Flip Studio toggles live (`workspace_mode`, `workbench_trust`, `dlna_enabled`, `cloud_enabled`, `theme_preset`) |
| `/py <code>` / `/pip <pkg>` | Run isolated subprocess Python or install a PyPI library into `.venv` |
| `/files` / `/getfile` / `/sync` / `/pullurl` | Manage `/priority_pdfs`, sync Nextcloud/Google Drive, or pull a shared link |
| `/menu` / `/thought` / `/addsticker <mood>` | Open Argo-style Telegram Hub, view thought trace on demand, or capture a Telegram sticker |
| `/update` / `/restart` / `/log` | Commit-pinned GitHub OTA sync, clean server restart, or offline `error_audit.log` tail |

---

<a id="changelog"></a>
## 📜 Changelog

### 🏮 `v7.1 — Lamppost` (Current Release)
* **Modern Flagship UI (`avs/ui/`):** Modular zero-build vanilla JS/CSS layer introducing a **Brave Leo-style floating glassmorphic composer** over your custom wallpaper, **`/` Quick Actions &amp; custom `/skills`** (`+ New`), unified **`📎`** media popover, inline multi-file thumbnail staging, full-window drag-and-drop &amp; `Ctrl+V` paste, collapsible desktop Studio Controls drawer, and interactive zero-manual walkthrough cards.
* **Lossless Full-Res Media &amp; Lightbox:** Untouched full-resolution chat &amp; generated images persisted in `/custom_assets/chat_media/` and SQLite across reloads, zoomable full-screen **Media Lightbox**, hi-DPI **`512×512`** Avatar &amp; **`1920×1080+`** Wallpaper croppers, plus **✨ Use Original** lossless bypass.
* **☁️ Vault Cloud &amp; 📺 Toggleable DLNA/UPnP (`avs/cloud_files.py`, `avs/dlna_server.py`):** Built-in Nextcloud-style LAN file server with Grid/List views, custom PC folder mounts, true **HTTP `206` Byte-Range** streaming for iOS Safari / Android Chrome / VLC, `.m3u` playlists, and a pure-Python **DLNA / UPnP Media Server** (`ssdp:alive` / `ssdp:byebye`) for **Roku Media Player &amp; VLC**—toggleable from UI, Telegram, `manager.py`, or directly by the AI (`vault.toggle("dlna_enabled", True/False)`).
* **✈️ Telegram Hub Overhaul:** Guided 3-step setup (`Test &amp; Connect` via `getMe`, 1-click `Detect My Chat ID`), separated **✈️ Telegram Read-Only Mirror** (+ **↗️ Fork to Web Chat**), **Argo-style compact paginated inline menu &amp; multi-thread chat switcher** (`editMessageText` in-place), 4-second context-aware `sendChatAction` animation heartbeat (`typing`, `upload_photo`, `upload_document`, `record_voice`), emotion-mapped **Telegram Stickers** (`getStickerSet` pack import, `/addsticker <mood>`, anti-spam cooldown), and inbound photo/document/lore drops.
* **🧰 Robust Filesystem, App Relocation &amp; Smarter Workbench (`avs/fs_ops.py`, `avs/introspect.py`):** Multi-threaded `robocopy`/`rsync` cross-drive copy/move, Recycle Bin trash, `relocate_app` with NTFS `mklink /J` junctions &amp; Windows PowerShell `.lnk` shortcut creator/rewriter, background job tracking, plus `vault.inspect()`, `vault.api_probe()`, and automatic nested signature/method hints on Workbench errors.
* **⚡ Evergreen-Speed Hot Path &amp; Cloud Lore Sync (`avs/cloud_sync.py`):** Native FP16 KV decode (`flash_attn=False`, `kv_cache_q8=False` defaults + config auto-heal), ~2.2 KB lean Operator prompt, static KV prefix lock, post-turn background memory sync, Gear 1 Reflex fast-path, Nextcloud/WebDAV + Google Drive + 1-click URL pull into `/priority_pdfs`, searchable `⌨️ Commands` tab, and custom `release_emblem.svg`.

<details>
<summary><strong>🦋 v6.0 – v6.8 — Bluesky (Modular Runtime, Guardrails, AT Protocol &amp; i18n)</strong></summary>

* Split runtime into modular `avs/` engines (`contracts`, `memory_graph`, `referee`, `tool_registry`, `bridges`, `turn_pipeline`, `model_polish`, `language_tools`, `manual_assets`).
* Added **Bluesky AT Protocol Bridge** (300-char post publishing &amp; optional mention auto-reply).
* Added **Background Memory Compactor &amp; 1-hop Keyword Mind-Map** (`AetherMemoryCompactor` with `active = 1` deduplication/superseding).
* Added **Guardrail Blender**, Lore Attribution Referee, and **Model-Agnostic Polisher** preserving Roleplay voice while keeping Assistant mode grounded.
* Added **Universal EN/ES Localization** (`locales/en.json`, `locales/es.json`), **Lore-Safe Offline Spellcheck** (`pyspellchecker` + `langid`), **Argos Translate** portable offline packs (`models/translate/`), and illustrated bilingual Visual Manual + 4-page vector PDF.
* Upgraded **User Profile Card** with OpenStreetMap/Leaflet pin-drop &amp; auto-cycling Pinned Facts rotator; removed deprecated `Manager.ps1` and `Windows_Defender_Patch.bat`.

</details>

<details>
<summary><strong>🌲 v5.0 – v5.6 — Evergreen (3-File Bootstrapper, SpecPulse &amp; Mobile/Telegram)</strong></summary>

* Introduced the permanent **3-File Bootstrapper** (`Launch.bat`, `Launch.sh`, `manager.py`) with auto-hydration, Stock Offline Vault, and SHA-256 GitHub OTA updates.
* Built **SpecPulse** 60-FPS PCB hardware telemetry monitor with true 64-bit Windows Registry VRAM detection and isolated CPU/RAM/Storage benchmark reactor.
* Added responsive mobile drawers (swipe-to-close + backdrop), integrated **Web Terminal &amp; 1-Click OTA Reload**, **Idle Sleep** automatic RAM/VRAM model unloading (`/unload`, `/wake`, `/sleep`), and native Telegram `/` slash commands + inline control panel.

</details>

<details>
<summary><strong>🏗️ v3.0 – v4.20 — Foundation &amp; Studio Core</strong></summary>

* Built **Two-Gear Adaptive Router** (Gear 1 Reflex vs. Gear 2 Deep), **Live Python Workbench (`vault.*`)** with killable subprocess isolation and Safe Auto vs. Full PC trust tiers, and hot-reload `custom_tools/` plugins.
* Added **Zero-Drop Smart API Waterfall** with rotating BYOK Key Rings, **OpenAI `/v1`** &amp; **MCP `/mcp`** servers, **Gemma 4** starter presets, **OSWorld** desktop agent, 5-tier zero-key web/news search, Spotify bridge, offline **Kokoro-ONNX TTS** &amp; **Whisper STT**, Anti-Ouroboros staged Self-Heal, official `aethervault_logo.svg`, and 1-file portable `.ZIP` workspace migration.

</details>

---

<a id="transparency"></a>
## 🛡️ Privacy, Transparency &amp; Disclaimer

AetherVault Studio is built to be **100% yours**.

* **Zero Telemetry &amp; No Phone-Home:** There are **no** analytics, tracking pixels, crash reporters, or hidden connections back to the creator (`EnZeeeRu`). Your chats, memories (`memory_core.db`), profile card, models, Vault Cloud files, and custom tools stay strictly on your local machine.
* **Transparent Network Access:** The only outbound network requests the app ever makes are the ones **you** explicitly trigger or configure—such as downloading models from Hugging Face, running `/update` against this public GitHub repo, using live web/weather search, or connecting your own BYOK API keys / Spotify / Telegram / Bluesky. Flip **Offline Mode** ON in the Studio UI to cut all outbound network calls completely.
* **No Liability ("AS IS"):** Per the **MIT License**, this software is provided *"as is"*, without warranty of any kind. You are solely responsible for what you run and build with it.

---

<a id="license"></a>
## 📜 License &amp; Attribution

* **Source Code:** Licensed under the **[MIT License](LICENSE)**.
* **Branding, Artwork (`aethervault_logo.svg`, `release_emblem.svg`), Manual PDF &amp; Documentation:** Licensed under **[Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/)** — credit **Enzeru (`EnZeeeRu`)**; non-commercial use only.
* **Third-Party Packages &amp; Models:** All Python libraries, APIs, and downloaded `.gguf` weights remain the property of their respective authors and license holders.

<div align="center">
  <sub>Made with ❤️ in Argentina by <strong>Enzeru</strong>, in collaboration with Google Gemini.</sub>
</div>
