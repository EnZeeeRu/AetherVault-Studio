<div align="center">
  <img src="aethervault_logo.svg" alt="AetherVault Studio Logo" width="130" />

  <h1>AetherVault Studio v5.0 — Evergreen</h1>
  <p><strong>100% Portable, Zero-Footprint Local AI &amp; PC Workbench Workstation</strong></p>

  <p>
    <a href="https://github.com/EnZeeeRu/AetherVault-Studio/releases/tag/Evergreen">
      <img src="https://img.shields.io/badge/Release-v5.0%20Evergreen-7c3aed?style=for-the-badge&logo=github" alt="Release v5.0" />
    </a>
    <img src="https://img.shields.io/badge/Python-3.10%2B-38bdf8?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+" />
    <img src="https://img.shields.io/badge/Code%20License-MIT-10b981?style=for-the-badge" alt="MIT License" />
    <img src="https://img.shields.io/badge/Assets%20%26%20Docs-CC%20BY--NC%204.0-f59e0b?style=for-the-badge" alt="CC BY-NC 4.0" />
  </p>

  <p>
    <a href="https://github.com/EnZeeeRu/AetherVault-Studio/releases/tag/Evergreen"><strong>⬇️ Download 3-File Bootstrapper</strong></a>
    &nbsp;•&nbsp;
    <a href="#-quick-start">Quick Start</a>
    &nbsp;•&nbsp;
    <a href="#-key-features">Features</a>
    &nbsp;•&nbsp;
    <a href="#-manager-console-commands">Console Commands</a>
    &nbsp;•&nbsp;
    <a href="#-privacy-transparency--disclaimer">Privacy and Transparency</a>
    &nbsp;•&nbsp;
    <a href="#-license--attribution">License</a>
  </p>
</div>

---

## ✨ Key Features

| Module | What It Does |
| :--- | :--- |
| **🧠 Gemma 4 + Zero-Drop Brain** | Runs local `.gguf` models (Gemma 4 E4B default, Vulkan GPU or Safe CPU) or routes through your own BYOK Cloud API waterfall with automatic local failsafe. |
| **🐍 Live Python Workbench** | Sandboxed &amp; killable subprocess execution (`vault.*`) for file I/O, web/news search, live weather, Spotify, and OSWorld desktop control. |
| **🧩 Hot-Reload `custom_tools/`** | Drop in `.py` plugins—or let the model author, sandbox-test, and hot-reload its own permanent tools without restarting the server. |
| **📊 SpecPulse Hardware Telemetry** | Deep hardware inventory with a **64-bit Windows Registry VRAM reader** (bypassing the 4 GB WMI cap) plus live CPU, RAM, and GPU load monitoring. |
| **🔌 OpenAI `/v1` &amp; MCP Server** | Connects seamlessly to external tools (VS Code, scripts, remote clients) via `/v1/chat/completions`, `/v1/models`, and JSON-RPC 2.0 `/mcp`. |
| **🔄 Locked 3-File OTA Sync** | Distribute just 3 tiny files (`Launch.bat`, `Launch.sh`, `manager.py`). Auto-hydrates &amp; updates with SHA-256 verification while preserving all local data. |

---

## 🚀 Quick Start

1. Download **`AetherVault_Studio_v5.0_3_Evergreen.zip`** from the [Evergreen Release Page](https://github.com/EnZeeeRu/AetherVault-Studio/releases/tag/Evergreen).
2. Extract the 3 files (`Launch.bat`, `Launch.sh`, `manager.py`) into any empty folder.
3. Double-click **`Launch.bat`** (Windows) or run **`./Launch.sh`** (macOS / Linux).
4. Click **1. Launch AetherVault Server**—`manager.py` automatically downloads the verified core files, builds an isolated `.venv`, and opens the Studio UI in your browser.

---

## 💻 Manager Console Commands

Type any of these directly into the **Manager Console** (`>` bar):

| Command | Action |
| :--- | :--- |
| `/help` | Show all available console commands |
| `/status` | Live model, GPU, RAM, workspace mode &amp; trust level |
| `/specs` | Deep hardware inventory (64-bit VRAM, CPU, live GPU load) |
| `/stop` | Immediately halt an active generation loop |
| `/inject <cat> \| <fact>` | Save a fact directly into the Priority #1 SQLite Memory Vault |
| `/toggle <key> <val>` | Flip Studio toggles live (e.g. `/toggle workbench_trust full_pc`) |
| `/py <code>` | Execute Python in the killable subprocess Workbench |
| `/pip <package>` | Install any custom PyPI library into `.venv` |
| `/log [keyword] [lines]` | Tail `error_audit.log` locally (works offline) |
| `/update` | 1-click SHA-256 verified OTA sync from `EnZeeeRu/AetherVault-Studio` |
| `/restart` | Cleanly stop &amp; relaunch `assistant_server.py` |

---

## 📜 License &amp; Attribution

* **Source Code:** Licensed under the **[MIT License](LICENSE)**.
* **Branding, Artwork (`aethervault_logo.svg`), Manual PDF &amp; Documentation:** Licensed under **[Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/)** — credit **Enzeru (`EnZeeeRu`)**; non-commercial use only.
* **Third-Party Packages &amp; Models:** All Python libraries, APIs, and downloaded `.gguf` weights remain the property of their respective authors and license holders.

---

## 🛡️ Privacy, Transparency & Disclaimer

AetherVault Studio is built to be **100% yours**.

* **Zero Telemetry & No Phone-Home:** There are **no** analytics, tracking pixels, crash reporters, or hidden connections back to the creator (`EnZeeeRu`). Your chats, memories (`memory_core.db`), profile card, models, and custom tools stay strictly on your local machine.
* **Transparent Network Access:** The only outbound network requests the app ever makes are the ones **you** explicitly trigger or configure—such as downloading models from Hugging Face, running `/update` against this public GitHub repo, using live web/weather search, or connecting your own BYOK API keys / Spotify / Telegram. Flip **Offline Mode** ON in the Studio UI to cut all outbound network calls completely.
* **Your Environment, Your Rules:** Once downloaded, this workspace belongs entirely to you. Modify it, break it, extend it with `custom_tools/`, or run whatever local models you choose.
* **No Liability ("AS IS"):** Per the **MIT License**, this software is provided *"as is"*, without warranty of any kind. The creator (`EnZeeeRu`) assumes **no responsibility or liability** for any outputs generated by AI models, code executed in the Python Workbench, desktop actions performed via OSWorld, or any other use or misuse of this software. You are solely responsible for what you run and build with it.

<div align="center">
  <sub>Made with ❤️ in Argentina by <strong>Enzeru</strong>, in collaboration with Google Gemini.</sub>
</div>
