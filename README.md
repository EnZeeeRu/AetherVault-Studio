<div align="center">
  <img src="aethervault_logo.svg" alt="AetherVault Studio Logo" width="130" />

  <h1>AetherVault Studio v5.1 — Evergreen</h1>
  <p><strong>100% Portable, Zero-Footprint Local AI, PC Workbench &amp; Hardware Telemetry Workstation</strong></p>

  <p>
    <a href="https://github.com/EnZeeeRu/AetherVault-Studio/releases/tag/Evergreen">
      <img src="https://img.shields.io/badge/Release-v5.1%20Evergreen-7c3aed?style=for-the-badge&logo=github" alt="Release v5.1" />
    </a>
    <img src="https://img.shields.io/badge/Python-3.10%2B-38bdf8?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+" />
    <img src="https://img.shields.io/badge/Code%20License-MIT-10b981?style=for-the-badge" alt="MIT License" />
    <img src="https://img.shields.io/badge/Assets%20%26%20Docs-CC%20BY--NC%204.0-f59e0b?style=for-the-badge" alt="CC BY-NC 4.0" />
  </p>

  <p>
    <a href="https://github.com/EnZeeeRu/AetherVault-Studio/releases/tag/Evergreen">
      <img src="https://img.shields.io/badge/%E2%AC%87%EF%B8%8F%20Download%20Launcher%20(3--File%20Bootstrapper)-7c3aed?style=for-the-badge" alt="Download Launcher" />
    </a>
    &nbsp;
    <a href="https://github.com/EnZeeeRu/AetherVault-Studio/raw/main/AetherVault_Studio_Manual.pdf">
      <img src="https://img.shields.io/badge/%F0%9F%93%96%20Download%20Manual%20(PDF)-0284c7?style=for-the-badge" alt="Download Manual PDF" />
    </a>
  </p>

  <p>
    <a href="#features">Features</a>
    &nbsp;•&nbsp;
    <a href="#specpulse">SpecPulse</a>
    &nbsp;•&nbsp;
    <a href="#quick-start">Quick Start</a>
    &nbsp;•&nbsp;
    <a href="#console-commands">Console Commands</a>
    &nbsp;•&nbsp;
    <a href="#transparency">Privacy &amp; Transparency</a>
    &nbsp;•&nbsp;
    <a href="#license">License</a>
  </p>
</div>

---

<a id="features"></a>
## ✨ Key Features

| Module | What It Does |
| :--- | :--- |
| **🧠 Gemma 4 + Zero-Drop Brain** | Runs local `.gguf` models (Gemma 4 E4B default, Vulkan GPU or Safe CPU) or routes through your own BYOK Cloud API waterfall with automatic local failsafe. |
| **🐍 Live Python Workbench** | Sandboxed &amp; killable subprocess execution (`vault.*`) for file I/O, web/news search, live weather, Spotify, and OSWorld desktop control. |
| **🧩 Hot-Reload `custom_tools/`** | Drop in `.py` plugins—or let the model author, sandbox-test, and hot-reload its own permanent tools without restarting the server. |
| **📊 SpecPulse Hardware Monitor** | Integrated 60-FPS visual hardware schematic, 64-bit VRAM telemetry, live waveforms, and built-in CPU/RAM/Storage benchmark suite. |
| **🔌 OpenAI `/v1` &amp; MCP Server** | Connects seamlessly to external tools (VS Code, scripts, remote clients) via `/v1/chat/completions`, `/v1/models`, and JSON-RPC 2.0 `/mcp`. |
| **🔄 Locked 3-File OTA Sync** | Distribute just 3 tiny files (`Launch.bat`, `Launch.sh`, `manager.py`). Auto-hydrates &amp; updates with SHA-256 verification while preserving all local data. |

---

<a id="specpulse"></a>
## 📊 SpecPulse :: Visual Hardware Telemetry &amp; Benchmark

Built directly into AetherVault Studio as a **zero-overhead on-demand overlay** (uses **0% CPU/GPU** when closed):

* **60-FPS Living Hardware Schematic:** Interactive PCB-style diagram showing real-time data flow between **CPU, RAM, GPU, Storage, and Motherboard**. Click any component block to inspect its full specs.
* **True 64-Bit GPU VRAM Reader:** Reads `HardwareInformation.qwMemorySize` directly from the Windows Registry to bypass the 4 GB 32-bit WMI `AdapterRAM` cap, alongside live GPU 3D/Compute load and dedicated VRAM usage.
* **Live Equalizer &amp; Waveforms:** Per-core CPU activity bars, real-time CPU &amp; Disk I/O waveforms, mounted partition usage, network throughput, and top memory processes.
* **Mini-Benchmark Reactor Suite:** Stress-tests Single-Core math, Multi-Core scaling, Memory bandwidth, and 128 MB Sequential Storage R/W (isolated inside `.temp_cache` with automatic cleanup).
* **How to Open:** Click **`📊 SpecPulse`** in the Studio sidebar (or on the Live SVG Hardware HUD card), pop it out at `/specpulse`, or run `/specs` in the Manager Console.

---

<a id="quick-start"></a>
## 🚀 Quick Start

1. Download **`AetherVault_Studio_v5.0_3_Evergreen.zip`** from the [Evergreen Release Page](https://github.com/EnZeeeRu/AetherVault-Studio/releases/tag/Evergreen).
2. Extract the 3 files (`Launch.bat`, `Launch.sh`, `manager.py`) into any empty folder.
3. Double-click **`Launch.bat`** (Windows) or run **`./Launch.sh`** (macOS / Linux).
4. Click **1. Launch AetherVault Server**—`manager.py` automatically downloads the verified core files, builds an isolated `.venv`, and opens the Studio UI in your browser.
5. Need the full guide? Grab the [AetherVault Studio Manual (PDF)](https://github.com/EnZeeeRu/AetherVault-Studio/raw/main/AetherVault_Studio_Manual.pdf) or click **📖 Manual** inside the app.

---

<a id="console-commands"></a>
## 💻 Manager Console Commands

Type any of these directly into the **Manager Console** (`>` bar):

| Command | Action |
| :--- | :--- |
| `/help` | Show all available console commands |
| `/status` | Live model, GPU, RAM, workspace mode &amp; trust level |
| `/specs` | Deep SpecPulse hardware inventory (64-bit VRAM, CPU, live GPU load) |
| `/stop` | Immediately halt an active generation loop |
| `/inject <cat> \| <fact>` | Save a fact directly into the Priority #1 SQLite Memory Vault |
| `/toggle <key> <val>` | Flip Studio toggles live (e.g. `/toggle workbench_trust full_pc`) |
| `/py <code>` | Execute Python in the killable subprocess Workbench |
| `/pip <package>` | Install any custom PyPI library into `.venv` |
| `/log [keyword] [lines]` | Tail `error_audit.log` locally (works offline) |
| `/update` | 1-click SHA-256 verified OTA sync from `EnZeeeRu/AetherVault-Studio` |
| `/restart` | Cleanly stop &amp; relaunch `assistant_server.py` |

---

<a id="transparency"></a>
## 🛡️ Privacy, Transparency &amp; Disclaimer

AetherVault Studio is built to be **100% yours**.

* **Zero Telemetry &amp; No Phone-Home:** There are **no** analytics, tracking pixels, crash reporters, or hidden connections back to the creator (`EnZeeeRu`). Your chats, memories (`memory_core.db`), profile card, models, and custom tools stay strictly on your local machine.
* **Transparent Network Access:** The only outbound network requests the app ever makes are the ones **you** explicitly trigger or configure—such as downloading models from Hugging Face, running `/update` against this public GitHub repo, using live web/weather search, or connecting your own BYOK API keys / Spotify / Telegram. Flip **Offline Mode** ON in the Studio UI to cut all outbound network calls completely.
* **Your Environment, Your Rules:** Once downloaded, this workspace belongs entirely to you. Modify it, break it, extend it with `custom_tools/`, or run whatever local models you choose.
* **No Liability ("AS IS"):** Per the **MIT License**, this software is provided *"as is"*, without warranty of any kind. The creator (`EnZeeeRu`) assumes **no responsibility or liability** for any outputs generated by AI models, code executed in the Python Workbench, desktop actions performed via OSWorld, or any other use or misuse of this software. You are solely responsible for what you run and build with it.

---

<a id="license"></a>
## 📜 License &amp; Attribution

* **Source Code:** Licensed under the **[MIT License](LICENSE)**.
* **Branding, Artwork (`aethervault_logo.svg`), Manual PDF &amp; Documentation:** Licensed under **[Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/)** — credit **Enzeru (`EnZeeeRu`)**; non-commercial use only.
* **Third-Party Packages &amp; Models:** All Python libraries, APIs, and downloaded `.gguf` weights remain the property of their respective authors and license holders.

<div align="center">
  <sub>Made with ❤️ in Argentina by <strong>Enzeru</strong>, in collaboration with Google Gemini.</sub>
</div>
