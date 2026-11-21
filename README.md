# AetherVault Studio v5.0 (Evergreen Definitive Edition)

100% portable, zero-footprint local AI & PC Workbench workstation with Gemma 4 default brain, SpecPulse-grade 64-bit hardware telemetry, hot-reloadable `custom_tools/` plugins, OpenAI-compatible `/v1` API, MCP server (`/mcp`), and 3-file GitHub OTA auto-updates.

## Quick Start (3-File Bootstrapper)
1. Download `Launch.bat` (Windows), `Launch.sh` (macOS/Linux), and `manager.py` into any folder.
2. Double-click `Launch.bat` (or run `./Launch.sh`).
3. In the Manager Console, run `/update` anytime for the latest version.

## Manager Console Slash-Commands
- `/help` — Show all commands
- `/status` — Live model, GPU, RAM, mode & trust status
- `/specs` — Deep SpecPulse hardware inventory (64-bit Registry VRAM, CPU, GPU load)
- `/stop` — Immediately halt an active generation loop
- `/inject <category> | <fact>` — Save a fact into Priority #1 SQLite Memory Vault
- `/toggle <setting> <value>` — Flip Studio toggles live
- `/py <code>` — Run Python in the killable subprocess Workbench
- `/pip <pkg>` — Install any custom PyPI library into `.venv`
- `/log [keyword] [lines]` — Tail `error_audit.log` locally
- `/repo <user/repo>` & `/update` — 1-click GitHub OTA sync
