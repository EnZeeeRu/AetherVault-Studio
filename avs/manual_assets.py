"""
avs/manual_assets.py — Complete Stylized Visual Manual Content & Inline SVG Architecture Diagrams.
Powers the in-app Visual Interactive Manual (EN + ES) and AI self-orientation via vault.manual().
"""
from __future__ import annotations

SVG_ARCHITECTURE = """<svg viewBox="0 0 720 205" width="100%" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="AetherVault Studio Layered Architecture">
  <defs>
    <linearGradient id="bgGrad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b1020"/><stop offset="100%" stop-color="#17122b"/>
    </linearGradient>
    <linearGradient id="vioGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#7c3aed"/><stop offset="100%" stop-color="#a855f7"/>
    </linearGradient>
    <linearGradient id="cyaGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0284c7"/><stop offset="100%" stop-color="#38bdf8"/>
    </linearGradient>
    <linearGradient id="emGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#059669"/><stop offset="100%" stop-color="#34d399"/>
    </linearGradient>
  </defs>
  <rect x="2" y="2" width="716" height="201" rx="12" fill="url(#bgGrad1)" stroke="#2e334d" stroke-width="1.5"/>
  <text x="20" y="26" fill="#a78bfa" font-family="Segoe UI,system-ui,sans-serif" font-size="11" font-weight="700" letter-spacing="1.2">AETHERVAULT STUDIO v6.8 BLUESKY :: 3-LAYER PORTABLE ARCHITECTURE</text>

  <!-- Layer 1: Frozen Bootstrapper -->
  <rect x="18" y="42" width="196" height="142" rx="10" fill="#14182a" stroke="#7c3aed" stroke-width="1.5"/>
  <rect x="18" y="42" width="196" height="26" rx="10" fill="url(#vioGrad)"/>
  <text x="116" y="59" text-anchor="middle" fill="#ffffff" font-family="Segoe UI,sans-serif" font-size="10.5" font-weight="700">1. FROZEN BOOTSTRAPPER</text>
  <text x="32" y="88" fill="#e5e7eb" font-family="Consolas,monospace" font-size="10">Launch.bat (Windows)</text>
  <text x="32" y="106" fill="#e5e7eb" font-family="Consolas,monospace" font-size="10">Launch.sh  (macOS/Linux)</text>
  <text x="32" y="124" fill="#c4b5fd" font-family="Consolas,monospace" font-size="10">manager.py (GUI + CLI)</text>
  <text x="32" y="148" fill="#9ca3af" font-family="Segoe UI,sans-serif" font-size="9.2">• Auto-hydrates via manifest</text>
  <text x="32" y="163" fill="#9ca3af" font-family="Segoe UI,sans-serif" font-size="9.2">• Builds portable .venv</text>
  <text x="32" y="177" fill="#9ca3af" font-family="Segoe UI,sans-serif" font-size="9.2">• SHA-256 OTA Runtime Sync</text>

  <!-- Arrow 1->2 -->
  <line x1="216" y1="113" x2="248" y2="113" stroke="#38bdf8" stroke-width="2.2"/>
  <polygon points="248,108 258,113 248,118" fill="#38bdf8"/>

  <!-- Layer 2: Modular Runtime -->
  <rect x="260" y="42" width="222" height="142" rx="10" fill="#14182a" stroke="#0284c7" stroke-width="1.5"/>
  <rect x="260" y="42" width="222" height="26" rx="10" fill="url(#cyaGrad)"/>
  <text x="371" y="59" text-anchor="middle" fill="#ffffff" font-family="Segoe UI,sans-serif" font-size="10.5" font-weight="700">2. LIVE STUDIO RUNTIME</text>
  <text x="274" y="88" fill="#bae6fd" font-family="Consolas,monospace" font-size="10">assistant_server.py (FastAPI)</text>
  <text x="274" y="105" fill="#e5e7eb" font-family="Consolas,monospace" font-size="10">ui_studio.html + locales/*.json</text>
  <rect x="272" y="114" width="198" height="60" rx="6" fill="#0c1120" stroke="#1e3a5f"/>
  <text x="280" y="129" fill="#38bdf8" font-family="Consolas,monospace" font-size="8.8">avs/ (13 Modular Engines):</text>
  <text x="280" y="143" fill="#cbd5e1" font-family="Consolas,monospace" font-size="8.2">contracts • memory_graph • referee</text>
  <text x="280" y="156" fill="#cbd5e1" font-family="Consolas,monospace" font-size="8.2">tool_registry • bridges • workbench</text>
  <text x="280" y="169" fill="#cbd5e1" font-family="Consolas,monospace" font-size="8.2">model_polish • language • specpulse</text>

  <!-- Arrow 2->3 -->
  <line x1="484" y1="113" x2="514" y2="113" stroke="#10b981" stroke-width="2.2"/>
  <polygon points="514,108 524,113 514,118" fill="#10b981"/>

  <!-- Layer 3: Portable Data Vaults -->
  <rect x="526" y="42" width="176" height="142" rx="10" fill="#14182a" stroke="#059669" stroke-width="1.5"/>
  <rect x="526" y="42" width="176" height="26" rx="10" fill="url(#emGrad)"/>
  <text x="614" y="59" text-anchor="middle" fill="#ffffff" font-family="Segoe UI,sans-serif" font-size="10.5" font-weight="700">3. YOUR LOCAL VAULTS</text>
  <text x="538" y="88" fill="#a7f3d0" font-family="Consolas,monospace" font-size="9.5">memory_core.db (SQLite)</text>
  <text x="538" y="105" fill="#e5e7eb" font-family="Consolas,monospace" font-size="9.5">priority_pdfs/ (CORE/LORE)</text>
  <text x="538" y="122" fill="#e5e7eb" font-family="Consolas,monospace" font-size="9.5">models/ (GGUF &amp; Argos)</text>
  <text x="538" y="139" fill="#e5e7eb" font-family="Consolas,monospace" font-size="9.5">custom_tools/ (Plugins)</text>
  <text x="538" y="156" fill="#e5e7eb" font-family="Consolas,monospace" font-size="9.5">stock_vault/ (Golden)</text>
  <text x="538" y="174" fill="#6ee7b7" font-family="Segoe UI,sans-serif" font-size="8.8">100% Private • Zero Cloud Lock</text>
</svg>"""

SVG_BRAIN_PIPELINE = """<svg viewBox="0 0 720 195" width="100%" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Two-Gear Adaptive Brain and Zero-Drop Waterfall">
  <rect x="2" y="2" width="716" height="191" rx="12" fill="#0b1020" stroke="#2e334d" stroke-width="1.5"/>
  <text x="20" y="25" fill="#38bdf8" font-family="Segoe UI,sans-serif" font-size="11" font-weight="700" letter-spacing="1.2">TWO-GEAR ADAPTIVE BRAIN &amp; ZERO-DROP WATERFALL PIPELINE</text>

  <!-- Input -->
  <rect x="18" y="72" width="105" height="60" rx="9" fill="#1b1d2e" stroke="#a78bfa" stroke-width="1.5"/>
  <text x="70" y="97" text-anchor="middle" fill="#fff" font-family="Segoe UI,sans-serif" font-size="10.5" font-weight="700">User Turn</text>
  <text x="70" y="114" text-anchor="middle" fill="#9ca3af" font-family="Segoe UI,sans-serif" font-size="8.5">Web / Voice / TG</text>

  <line x1="123" y1="102" x2="152" y2="102" stroke="#a78bfa" stroke-width="2"/>
  <polygon points="152,97 162,102 152,107" fill="#a78bfa"/>

  <!-- Gear Triage -->
  <rect x="164" y="42" width="154" height="52" rx="8" fill="#162135" stroke="#38bdf8" stroke-width="1.4"/>
  <text x="241" y="62" text-anchor="middle" fill="#38bdf8" font-family="Segoe UI,sans-serif" font-size="10" font-weight="700">GEAR 1 :: REFLEX</text>
  <text x="241" y="79" text-anchor="middle" fill="#cbd5e1" font-family="Segoe UI,sans-serif" font-size="8.5">Fast Chat • Auto-Web Rescue</text>

  <rect x="164" y="110" width="154" height="62" rx="8" fill="#1e1435" stroke="#a855f7" stroke-width="1.4"/>
  <text x="241" y="130" text-anchor="middle" fill="#d8b4fe" font-family="Segoe UI,sans-serif" font-size="10" font-weight="700">GEAR 2 :: DEEP / OPS</text>
  <text x="241" y="146" text-anchor="middle" fill="#cbd5e1" font-family="Segoe UI,sans-serif" font-size="8.4">Assistant: Workbench Only</text>
  <text x="241" y="160" text-anchor="middle" fill="#cbd5e1" font-family="Segoe UI,sans-serif" font-size="8.4">Roleplay: Full Lore + Voice</text>

  <line x1="318" y1="68" x2="352" y2="96" stroke="#38bdf8" stroke-width="1.8"/>
  <line x1="318" y1="140" x2="352" y2="110" stroke="#a855f7" stroke-width="1.8"/>

  <!-- Zero-Drop Brain Box -->
  <rect x="354" y="46" width="176" height="122" rx="10" fill="#11192c" stroke="#10b981" stroke-width="1.6"/>
  <text x="442" y="66" text-anchor="middle" fill="#34d399" font-family="Segoe UI,sans-serif" font-size="10" font-weight="700">ZERO-DROP DISPATCHER</text>
  <rect x="366" y="76" width="152" height="34" rx="6" fill="#0d2638" stroke="#0284c7"/>
  <text x="442" y="92" text-anchor="middle" fill="#e0f2fe" font-family="Segoe UI,sans-serif" font-size="9" font-weight="700">BYOK Cloud Waterfall</text>
  <text x="442" y="104" text-anchor="middle" fill="#7dd3fc" font-family="Segoe UI,sans-serif" font-size="8">Gemini • Groq • HF • OpenRouter</text>
  <text x="442" y="122" text-anchor="middle" fill="#fbbf24" font-family="Segoe UI,sans-serif" font-size="8.5" font-weight="700">↓ Auto-Failsafe if Offline/429 ↓</text>
  <rect x="366" y="128" width="152" height="30" rx="6" fill="#1c1534" stroke="#7c3aed"/>
  <text x="442" y="147" text-anchor="middle" fill="#ddd6fe" font-family="Segoe UI,sans-serif" font-size="9" font-weight="700">Local GGUF (Gemma 4 / Any)</text>

  <line x1="530" y1="106" x2="556" y2="106" stroke="#10b981" stroke-width="2"/>
  <polygon points="556,101 566,106 556,111" fill="#10b981"/>

  <!-- Guardrail Blender -->
  <rect x="568" y="46" width="134" height="122" rx="10" fill="#171628" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="635" y="66" text-anchor="middle" fill="#fbbf24" font-family="Segoe UI,sans-serif" font-size="9.8" font-weight="700">GUARDRAIL BLENDER</text>
  <text x="578" y="88" fill="#e5e7eb" font-family="Segoe UI,sans-serif" font-size="8.6">• Strips &lt;think&gt; echoes</text>
  <text x="578" y="105" fill="#e5e7eb" font-family="Segoe UI,sans-serif" font-size="8.6">• Lore Referee Check</text>
  <text x="578" y="122" fill="#e5e7eb" font-family="Segoe UI,sans-serif" font-size="8.6">• Mode-Aware Polish</text>
  <text x="578" y="139" fill="#e5e7eb" font-family="Segoe UI,sans-serif" font-size="8.6">• Idle Sleep Watchdog</text>
  <text x="578" y="156" fill="#a7f3d0" font-family="Segoe UI,sans-serif" font-size="8.6">✓ Clean Streamed Reply</text>
</svg>"""

SVG_WORKBENCH = """<svg viewBox="0 0 720 185" width="100%" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Python Workbench and Dual Trust Gate">
  <rect x="2" y="2" width="716" height="181" rx="12" fill="#0b1020" stroke="#2e334d" stroke-width="1.5"/>
  <text x="20" y="25" fill="#34d399" font-family="Segoe UI,sans-serif" font-size="11" font-weight="700" letter-spacing="1.2">LIVE PYTHON WORKBENCH (vault.*) &amp; TWO-TIER TRUST GATE</text>

  <rect x="18" y="42" width="212" height="124" rx="9" fill="#10221d" stroke="#10b981" stroke-width="1.5"/>
  <text x="124" y="62" text-anchor="middle" fill="#6ee7b7" font-family="Segoe UI,sans-serif" font-size="10.2" font-weight="700">SAFE AUTO TIER (Default)</text>
  <text x="30" y="82" fill="#e5e7eb" font-family="Consolas,monospace" font-size="8.8">vault.web() / vault.weather()</text>
  <text x="30" y="98" fill="#e5e7eb" font-family="Consolas,monospace" font-size="8.8">vault.spotify() / vault.pc_info()</text>
  <text x="30" y="114" fill="#e5e7eb" font-family="Consolas,monospace" font-size="8.8">vault.spellcheck() / translate()</text>
  <text x="30" y="130" fill="#e5e7eb" font-family="Consolas,monospace" font-size="8.8">Desktop/Docs/Workspace I/O</text>
  <text x="30" y="150" fill="#fca5a5" font-family="Segoe UI,sans-serif" font-size="8.4">Blocks os.system &amp; raw clicks</text>

  <rect x="252" y="42" width="216" height="124" rx="9" fill="#261812" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="360" y="62" text-anchor="middle" fill="#fcd34d" font-family="Segoe UI,sans-serif" font-size="10.2" font-weight="700">FULL PC CONTROL (Opt-In)</text>
  <text x="264" y="82" fill="#e5e7eb" font-family="Consolas,monospace" font-size="8.8">vault.run_cmd('powershell')</text>
  <text x="264" y="98" fill="#e5e7eb" font-family="Consolas,monospace" font-size="8.8">vault.osworld('click'|'type')</text>
  <text x="264" y="114" fill="#e5e7eb" font-family="Consolas,monospace" font-size="8.8">Full User Filesystem Ops</text>
  <text x="264" y="130" fill="#e5e7eb" font-family="Consolas,monospace" font-size="8.8">vault.run_isolated(code, 15s)</text>
  <text x="264" y="150" fill="#fde68a" font-family="Segoe UI,sans-serif" font-size="8.4">Core Engine Files ALWAYS Guarded</text>

  <rect x="490" y="42" width="212" height="124" rx="9" fill="#181530" stroke="#8b5cf6" stroke-width="1.5"/>
  <text x="596" y="62" text-anchor="middle" fill="#c4b5fd" font-family="Segoe UI,sans-serif" font-size="10.2" font-weight="700">HOT-RELOAD PLUGINS</text>
  <text x="502" y="84" fill="#e5e7eb" font-family="Consolas,monospace" font-size="8.8">custom_tools/*.py</text>
  <text x="502" y="102" fill="#e5e7eb" font-family="Consolas,monospace" font-size="8.8">vault.create_tool(name, code)</text>
  <text x="502" y="118" fill="#e5e7eb" font-family="Consolas,monospace" font-size="8.8">vault.plugins.&lt;mod&gt;.&lt;fn&gt;()</text>
  <text x="502" y="138" fill="#9ca3af" font-family="Segoe UI,sans-serif" font-size="8.4">• Sandbox-tested before saving</text>
  <text x="502" y="153" fill="#9ca3af" font-family="Segoe UI,sans-serif" font-size="8.4">• Zero server restart required</text>
</svg>"""

SVG_MULTILANG = """<svg viewBox="0 0 720 185" width="100%" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Universal Multi-Language and Offline Spellcheck Pipeline">
  <rect x="2" y="2" width="716" height="181" rx="12" fill="#0b1020" stroke="#2e334d" stroke-width="1.5"/>
  <text x="20" y="25" fill="#38bdf8" font-family="Segoe UI,sans-serif" font-size="11" font-weight="700" letter-spacing="1.2">UNIVERSAL MULTI-LANGUAGE, LORE-SAFE SPELLCHECK &amp; ARGOS TRANSLATE</text>

  <rect x="18" y="42" width="160" height="122" rx="9" fill="#15182e" stroke="#7c3aed" stroke-width="1.4"/>
  <text x="98" y="62" text-anchor="middle" fill="#c4b5fd" font-family="Segoe UI,sans-serif" font-size="9.8" font-weight="700">1. FULL UI LOCALES</text>
  <text x="28" y="82" fill="#e5e7eb" font-family="Consolas,monospace" font-size="8.8">locales/en.json</text>
  <text x="28" y="98" fill="#e5e7eb" font-family="Consolas,monospace" font-size="8.8">locales/es.json</text>
  <text x="28" y="118" fill="#9ca3af" font-family="Segoe UI,sans-serif" font-size="8.4">• Menus, Cards &amp; Tabs</text>
  <text x="28" y="134" fill="#9ca3af" font-family="Segoe UI,sans-serif" font-size="8.4">• Visual Manual (EN/ES)</text>
  <text x="28" y="150" fill="#9ca3af" font-family="Segoe UI,sans-serif" font-size="8.4">• Zero RAM overhead</text>

  <rect x="194" y="42" width="166" height="122" rx="9" fill="#102226" stroke="#06b6d4" stroke-width="1.4"/>
  <text x="277" y="62" text-anchor="middle" fill="#67e8f9" font-family="Segoe UI,sans-serif" font-size="9.8" font-weight="700">2. LORE-SAFE SPELL</text>
  <text x="204" y="82" fill="#e5e7eb" font-family="Consolas,monospace" font-size="8.7">pyspellchecker + langid</text>
  <text x="204" y="99" fill="#a7f3d0" font-family="Segoe UI,sans-serif" font-size="8.4">Auto-Whitelists:</text>
  <text x="204" y="114" fill="#cbd5e1" font-family="Segoe UI,sans-serif" font-size="8.3">• glossary_index.json</text>
  <text x="204" y="129" fill="#cbd5e1" font-family="Segoe UI,sans-serif" font-size="8.3">• Character &amp; Lore Names</text>
  <text x="204" y="146" fill="#cbd5e1" font-family="Segoe UI,sans-serif" font-size="8.3">• Native browser check</text>

  <rect x="376" y="42" width="160" height="122" rx="9" fill="#12241d" stroke="#10b981" stroke-width="1.4"/>
  <text x="456" y="62" text-anchor="middle" fill="#6ee7b7" font-family="Segoe UI,sans-serif" font-size="9.8" font-weight="700">3. SMART LOCALE OPS</text>
  <text x="386" y="82" fill="#e5e7eb" font-family="Segoe UI,sans-serif" font-size="8.5">• Mic: es-AR / en-US</text>
  <text x="386" y="99" fill="#e5e7eb" font-family="Segoe UI,sans-serif" font-size="8.5">• Bilingual Tool Router</text>
  <text x="386" y="116" fill="#e5e7eb" font-family="Segoe UI,sans-serif" font-size="8.5">• Localized News RSS</text>
  <text x="386" y="133" fill="#e5e7eb" font-family="Segoe UI,sans-serif" font-size="8.5">• Localized Map Search</text>
  <text x="386" y="150" fill="#a7f3d0" font-family="Segoe UI,sans-serif" font-size="8.4">Works 100% natively!</text>

  <rect x="552" y="42" width="150" height="122" rx="9" fill="#1f172b" stroke="#ec4899" stroke-width="1.4"/>
  <text x="627" y="62" text-anchor="middle" fill="#f9a8d4" font-family="Segoe UI,sans-serif" font-size="9.8" font-weight="700">4. ARGOS OFFLINE</text>
  <text x="562" y="82" fill="#e5e7eb" font-family="Consolas,monospace" font-size="8.6">models/translate/</text>
  <text x="562" y="99" fill="#cbd5e1" font-family="Segoe UI,sans-serif" font-size="8.4">• 1-click bubble translate</text>
  <text x="562" y="115" fill="#cbd5e1" font-family="Segoe UI,sans-serif" font-size="8.4">• Optional EN-GGUF Bridge</text>
  <text x="562" y="131" fill="#cbd5e1" font-family="Segoe UI,sans-serif" font-size="8.4">• vault.translate()</text>
  <text x="562" y="149" fill="#fbcfe8" font-family="Segoe UI,sans-serif" font-size="8.3">100% Offline CTranslate2</text>
</svg>"""

SVG_BRIDGES = """<svg viewBox="0 0 720 180" width="100%" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="External Bridges and SpecPulse Ecosystem">
  <rect x="2" y="2" width="716" height="176" rx="12" fill="#0b1020" stroke="#2e334d" stroke-width="1.5"/>
  <text x="20" y="25" fill="#a78bfa" font-family="Segoe UI,sans-serif" font-size="11" font-weight="700" letter-spacing="1.2">BRIDGES, OPEN APIs &amp; SPECPULSE TELEMETRY HUB</text>

  <rect x="260" y="64" width="200" height="66" rx="12" fill="#1e1538" stroke="#8b5cf6" stroke-width="2"/>
  <text x="360" y="92" text-anchor="middle" fill="#ffffff" font-family="Segoe UI,sans-serif" font-size="11.5" font-weight="700">AetherVault Core</text>
  <text x="360" y="110" text-anchor="middle" fill="#c4b5fd" font-family="Consolas,monospace" font-size="9">127.0.0.1:8000 | LAN</text>

  <!-- Left 3 Bridges -->
  <rect x="18" y="38" width="190" height="36" rx="7" fill="#0d2236" stroke="#0284c7"/>
  <text x="113" y="60" text-anchor="middle" fill="#bae6fd" font-family="Segoe UI,sans-serif" font-size="9.5" font-weight="700">Bluesky AT Protocol Bridge</text>
  <line x1="208" y1="56" x2="260" y2="84" stroke="#0284c7" stroke-width="1.6"/>

  <rect x="18" y="82" width="190" height="36" rx="7" fill="#0f2532" stroke="#38bdf8"/>
  <text x="113" y="104" text-anchor="middle" fill="#e0f2fe" font-family="Segoe UI,sans-serif" font-size="9.5" font-weight="700">Telegram Bot &amp; Mini App</text>
  <line x1="208" y1="100" x2="260" y2="98" stroke="#38bdf8" stroke-width="1.6"/>

  <rect x="18" y="126" width="190" height="36" rx="7" fill="#10261f" stroke="#10b981"/>
  <text x="113" y="148" text-anchor="middle" fill="#a7f3d0" font-family="Segoe UI,sans-serif" font-size="9.5" font-weight="700">Spotify Web + Media Keys</text>
  <line x1="208" y1="144" x2="260" y2="114" stroke="#10b981" stroke-width="1.6"/>

  <!-- Right 3 Bridges -->
  <rect x="512" y="38" width="190" height="36" rx="7" fill="#1a1732" stroke="#a855f7"/>
  <text x="607" y="60" text-anchor="middle" fill="#e9d5ff" font-family="Segoe UI,sans-serif" font-size="9.5" font-weight="700">MCP Server (/mcp RPC 2.0)</text>
  <line x1="460" y1="84" x2="512" y2="56" stroke="#a855f7" stroke-width="1.6"/>

  <rect x="512" y="82" width="190" height="36" rx="7" fill="#23182a" stroke="#ec4899"/>
  <text x="607" y="104" text-anchor="middle" fill="#fbcfe8" font-family="Segoe UI,sans-serif" font-size="9.5" font-weight="700">OpenAI /v1/chat/completions</text>
  <line x1="460" y1="98" x2="512" y2="100" stroke="#ec4899" stroke-width="1.6"/>

  <rect x="512" y="126" width="190" height="36" rx="7" fill="#142230" stroke="#06b6d4"/>
  <text x="607" y="148" text-anchor="middle" fill="#cffafe" font-family="Segoe UI,sans-serif" font-size="9.5" font-weight="700">SpecPulse 60-FPS Telemetry</text>
  <line x1="460" y1="114" x2="512" y2="144" stroke="#06b6d4" stroke-width="1.6"/>
</svg>"""

SVG_SELFHEAL = """<svg viewBox="0 0 720 140" width="100%" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Anti-Ouroboros Self-Heal and Golden Rollback">
  <rect x="2" y="2" width="716" height="136" rx="12" fill="#0b1020" stroke="#2e334d" stroke-width="1.5"/>
  <text x="20" y="25" fill="#fbbf24" font-family="Segoe UI,sans-serif" font-size="11" font-weight="700" letter-spacing="1.2">ANTI-OUROBOROS SELF-HEAL &amp; GOLDEN BACKUP FLOW</text>

  <rect x="18" y="46" width="142" height="72" rx="8" fill="#181c30" stroke="#7c3aed"/>
  <text x="89" y="70" text-anchor="middle" fill="#ddd6fe" font-family="Segoe UI,sans-serif" font-size="9.5" font-weight="700">1. Stage Proposal</text>
  <text x="89" y="88" text-anchor="middle" fill="#9ca3af" font-family="Segoe UI,sans-serif" font-size="8.2">vault.propose_core_fix</text>
  <text x="89" y="103" text-anchor="middle" fill="#9ca3af" font-family="Segoe UI,sans-serif" font-size="8.2">/self_heal_staging</text>

  <line x1="160" y1="82" x2="186" y2="82" stroke="#38bdf8" stroke-width="2"/>
  <polygon points="186,77 195,82 186,87" fill="#38bdf8"/>

  <rect x="197" y="46" width="142" height="72" rx="8" fill="#102232" stroke="#38bdf8"/>
  <text x="268" y="70" text-anchor="middle" fill="#bae6fd" font-family="Segoe UI,sans-serif" font-size="9.5" font-weight="700">2. Syntax Gate</text>
  <text x="268" y="88" text-anchor="middle" fill="#9ca3af" font-family="Segoe UI,sans-serif" font-size="8.2">py_compile + AST check</text>
  <text x="268" y="103" text-anchor="middle" fill="#9ca3af" font-family="Segoe UI,sans-serif" font-size="8.2">Zero blind overwrites</text>

  <line x1="339" y1="82" x2="365" y2="82" stroke="#fbbf24" stroke-width="2"/>
  <polygon points="365,77 374,82 365,87" fill="#fbbf24"/>

  <rect x="376" y="46" width="142" height="72" rx="8" fill="#251d12" stroke="#f59e0b"/>
  <text x="447" y="70" text-anchor="middle" fill="#fde68a" font-family="Segoe UI,sans-serif" font-size="9.5" font-weight="700">3. Human Approval</text>
  <text x="447" y="88" text-anchor="middle" fill="#9ca3af" font-family="Segoe UI,sans-serif" font-size="8.2">Approve / Reject in UI</text>
  <text x="447" y="103" text-anchor="middle" fill="#9ca3af" font-family="Segoe UI,sans-serif" font-size="8.2">Auto-saves .good backup</text>

  <line x1="518" y1="82" x2="544" y2="82" stroke="#10b981" stroke-width="2"/>
  <polygon points="544,77 553,82 544,87" fill="#10b981"/>

  <rect x="555" y="46" width="146" height="72" rx="8" fill="#10251e" stroke="#10b981"/>
  <text x="628" y="70" text-anchor="middle" fill="#a7f3d0" font-family="Segoe UI,sans-serif" font-size="9.5" font-weight="700">4. Golden Rollback</text>
  <text x="628" y="88" text-anchor="middle" fill="#9ca3af" font-family="Segoe UI,sans-serif" font-size="8.2">stock_vault/*.good</text>
  <text x="628" y="103" text-anchor="middle" fill="#9ca3af" font-family="Segoe UI,sans-serif" font-size="8.2">1-Click Safe Restore</text>
</svg>"""


MANUAL_SECTIONS_EN = [
    {
        "id": "overview",
        "badge": "ARCHITECTURE",
        "title": "1. System Map, Frozen Bootstrapper & Folder Layout",
        "summary": "How the permanent 3-file bootstrapper, modular avs/ runtime, and portable local vaults fit together.",
        "svg": SVG_ARCHITECTURE,
        "body": (
            "AetherVault Studio v6.8 Bluesky is a 100% portable, zero-footprint local AI, Python Workbench, AT Protocol bridge, and hardware telemetry workstation.\n"
            "FROZEN 3-FILE BOOTSTRAPPER (ENTRY LAYER):\n"
            "- Launch.bat (Windows) & Launch.sh (macOS/Linux): Detect Python 3.10+, offer automatic install (winget/brew/apt/dnf/pacman), and launch manager.py.\n"
            "- manager.py: Permanent Bootstrapper & Control Center (tkinter GUI + automatic CLI fallback). Dynamically reads runtime version from manifest.json, builds the isolated .venv, auto-hydrates missing runtime files on first boot, and pulls SHA-256-verified GitHub OTA updates without overwriting your frozen bootstrapper or personal data.\n"
            "LIVE STUDIO RUNTIME & MODULAR avs/ PACKAGE (13 MODULES):\n"
            "- assistant_server.py & ui_studio.html + locales/en.json & locales/es.json.\n"
            "- avs/ modules: contracts, memory_graph, referee, tool_registry, bridges, turn_pipeline, model_polish, language_tools, manual_assets, platform_bridge, toolbox, workbench, hardware_monitor.\n"
            "PORTABLE USER DATA (100% INCLUDED IN .ZIP EXPORT/IMPORT):\n"
            "- workspace_config.json, user_profile_card.json, memory_core.db, memory_vault/, priority_pdfs/, chat_logs/, models/ (GGUF + models/translate/ Argos packs), custom_tools/, custom_assets/, stock_vault/, and auto-purged .temp_cache/."
        ),
        "tip": "Run `python tests/smoke.py` (or Option 9 in manager.py) anytime to verify syntax, all avs/ modules, Workbench safety, and manifest.json SHA-256 checksums."
    },
    {
        "id": "brain_modes",
        "badge": "INFERENCE & MODES",
        "title": "2. Two-Gear Brain, Model-Agnostic Tuning & Workspace Modes",
        "summary": "Adaptive Reflex vs. Deep/Operator routing, BYOK Cloud Waterfall, Idle Sleep, and the Guardrail Blender.",
        "svg": SVG_BRAIN_PIPELINE,
        "body": (
            "DEFAULT OFFLINE BRAIN: gemma-4-E4B-it-Q4_K_M.gguf (~5.0 GB, Apache-2.0) — chosen for strong offline Python Workbench tool calling and smooth local inference. Swap in any .gguf (Qwen2.5, Llama 3.2, DeepSeek-R1, Hermes 3, Dolphin 3, Mistral) anytime; avs/model_polish.py automatically adapts sampling hints and output cleanup to the active model family.\n"
            "WORKSPACE MODES:\n"
            "- Assistant & Workbench Mode: Locks out Lore RAG so real PC/weather/web data always wins; strips <think> echoes and stage narration.\n"
            "- Roleplay & Lore Mode: Unlocks on-demand Lore retrieval from /priority_pdfs and preserves expressive narration & character voice.\n"
            "BRAIN MODES (ZERO-DROP DISPATCHER):\n"
            "- local_only: 100% offline local GGUF inference.\n"
            "- smart_api: Prioritized BYOK Cloud Waterfall (Google Gemini, Hugging Face Router, Groq, OpenRouter, DeepSeek, Mistral, OpenAI, Custom LAN) with rotating Key Rings.\n"
            "- hybrid: Uses Smart API first and drops smoothly to your local failsafe GGUF if offline or rate-limited.\n"
            "IDLE SLEEP WATCHDOG: Automatically unloads GGUF weights from RAM/VRAM after idle_unload_minutes (default 10m) and wakes transparently on your next message."
        ),
        "tip": "Use `/unload` to free RAM/VRAM instantly before launching a heavy game, and `/wake` (or just send a chat message) to reload automatically."
    },
    {
        "id": "workbench_guide",
        "badge": "CODEACT & PLUGINS",
        "title": "3. Live Python Workbench (vault.*), Trust Tiers & custom_tools/",
        "summary": "Execute real PC, web, weather, Spotify, language, and plugin actions safely via ```workbench blocks.",
        "svg": SVG_WORKBENCH,
        "body": (
            "NOTE TO THE RUNNING AI MODEL: Call vault.help() or vault.manual() inside a ```workbench block whenever you need exact method signatures.\n"
            "WEB, WEATHER, LANGUAGE & MEDIA:\n"
            "- vault.web('keywords') | vault.fetch_url('https://...') | vault.docs('topic') | vault.youtube('query', private=True)\n"
            "- vault.weather() : Live Open-Meteo 2-day forecast using the saved User Profile Card / map pin.\n"
            "- vault.spellcheck(text, lang='auto') | vault.translate(text, to='en', src='auto') | vault.detect_lang(text)\n"
            "- vault.spotify('current_track'|'playlists'|'play_playlist'|'play_album'|'liked'|'play_liked'|'play'|'pause'|'next'|'prev', 'query')\n"
            "PC, FILES, SYSTEM & ISOLATED SUBPROCESS:\n"
            "- vault.pc_info() | vault.specs() | vault.disk_usage() | vault.ps_list(20) | vault.debug_log() | vault.pip_list()\n"
            "- vault.files('steam'|'C:/path'|'keyword') | vault.read_file(path) | vault.chunk_read(path, 0, 10000)\n"
            "- vault.write_desktop('note.txt', text) | vault.write_file(path, text) | vault.open_app('steam'|'notepad') | vault.browser(url, private=True)\n"
            "- vault.clipboard('read'|'write', text) | vault.notify(title, msg) | vault.timer(secs, msg)\n"
            "- vault.run_cmd('powershell') [Full PC only] | vault.run_isolated(code, timeout=15)\n"
            "HOT-RELOAD PLUGINS & STUDIO CONTROL:\n"
            "- vault.create_tool(name, code, test_code) -> AST + sandbox-tested, then hot-reloaded at vault.plugins.<name>!\n"
            "- vault.toggle(setting, value) | vault.settings() | vault.profile() | vault.update_profile(...) | vault.test_all()"
        ),
        "tip": "Safe Auto protects destructive deletes, shell commands, and raw OSWorld mouse clicks until you explicitly unlock Full PC Control."
    },
    {
        "id": "multilanguage_spellcheck",
        "badge": "MULTI-LANGUAGE",
        "title": "4. Universal Multi-Language, Offline Spellcheck & Argos Translate",
        "summary": "Switch the entire Studio UI, mic recognition, search locale, lore-safe spellcheck, and offline neural translation.",
        "svg": SVG_MULTILANG,
        "body": (
            "1. FULL UI LOCALIZATION (locales/en.json & locales/es.json):\n"
            "- Use the 🌐 Language selector in the top bar (or Settings -> Bridges, Language & Voice) to switch the Studio interface, labels, tooltips, and Visual Manual between English and Español instantly—100% offline with zero RAM cost.\n"
            "2. LANGUAGE-AWARE MIC, ROUTERS & SEARCH:\n"
            "- Voice input (🎤) uses your selected speech_locale (e.g. en-US, es-AR, es-ES, pt-BR, fr-FR, de-DE, ja-JP) instead of forcing English.\n"
            "- Bilingual intent routing recognizes English and Spanish requests for weather (clima/pronóstico), Spotify (canción/música/pausar), web/news (buscar/noticias), and PC tools.\n"
            "- Google News RSS, Open-Meteo city search, and OpenStreetMap reverse lookups automatically follow your active Studio language.\n"
            "3. LORE-SAFE UNIVERSAL OFFLINE SPELLCHECK:\n"
            "- Click ✨ in the chat bar (or call vault.spellcheck(text)) to check spelling in 9+ languages via optional `pyspellchecker` + `langid` (with a built-in fallback if uninstalled).\n"
            "- Automatically whitelists your glossary_index.json, Knowledge Tree domain vocabulary, and persona names so fictional lore terms are NEVER overwritten!\n"
            "4. OFFLINE NEURAL TRANSLATION (ARGOS TRANSLATE):\n"
            "- Install `argostranslate` in API & Library Manager, then download language pairs (e.g. en->es, es->en) directly into portable `models/translate/`.\n"
            "- Translates any chat bubble via its 🌐 Translate button, works via vault.translate(), and supports an optional Argos Bridge mode for English-only GGUF models."
        ),
        "tip": "Keep Translate Bridge on 'Native Model Language' for multilingual brains like Gemma 4, Qwen 2.5, or Gemini; flip on 'Argos Offline Bridge' only when running an English-only GGUF."
    },
    {
        "id": "memory_profile_lore",
        "badge": "MEMORY & LORE",
        "title": "5. User Profile Card, OpenStreetMap Pin, Memory Compactor & Knowledge Tree",
        "summary": "Coordinate-locked weather, background SQLite memory deduplication, Keyword Mind-Map, and CORE vs. LORE files.",
        "svg": "",
        "body": (
            "USER PROFILE CARD & OPENSTREETMAP PIN:\n"
            "- Store your handle, city, ZIP, exact lat/lon pin (click map or search city via OpenStreetMap/Leaflet), custom fields, and Pinned Facts.\n"
            "- The sidebar card explicitly labels Handle, Map Pin, Location, Custom Fields, and a cycling Pinned Facts box (auto-rotates every 12s, pauses on hover, or step manually with ↻ Next).\n"
            "BACKGROUND MEMORY COMPACTOR & KEYWORD MIND-MAP (avs/memory_graph.py):\n"
            "- Deduplicates and supersedes stale single-slot facts (location, name, ZIP) in SQLite (active = 0) with zero LLM token cost.\n"
            "- Builds a bounded 1-hop keyword co-occurrence mind-map to expand search terms during Lore lookups.\n"
            "KNOWLEDGE TREE (/priority_pdfs):\n"
            "- Drop .pdf, .txt, or .md files into /priority_pdfs (or subfolders like /priority_pdfs/lore).\n"
            "- Toggle any file between CORE (always loaded 24/7) and LORE (chunked on-demand RAG, locked out in Assistant Mode so fiction never overrides real PC facts)."
        ),
        "tip": "AI-directed instructions (like 'remember that you can...') are automatically filtered out of Pinned Facts so only real user facts stick to your Profile Card."
    },
    {
        "id": "bridges_ecosystem",
        "badge": "BRIDGES & APIs",
        "title": "6. Bridges: Bluesky AT Protocol, Telegram Bot, MCP & OpenAI /v1",
        "summary": "Connect your local workstation to Bluesky, Telegram, VS Code, Gemini CLI, and home Wi-Fi devices.",
        "svg": SVG_BRIDGES,
        "body": (
            "BLUESKY AT PROTOCOL BRIDGE:\n"
            "- Configure Handle + Bluesky App Password (never your main password) in Studio Settings -> Integrations.\n"
            "- Publish posts (auto-formatted to 300 chars via POST /api/bluesky/post) and optionally auto-reply to new unread mentions from allowed handles/DIDs (historical mentions are safely seeded on boot so it never spams old threads).\n"
            "TELEGRAM BOT BRIDGE & MINI APP:\n"
            "- Paste your @BotFather token to chat, inspect PC status, capture screenshots, check Spotify, and run console commands from anywhere with zero port-forwarding.\n"
            "- Includes native slash command menu (/menu, /status, /specs, /unload, /wake, /update) and optional HTTPS Mini App button.\n"
            "MCP SERVER (/mcp) & OPENAI /v1:\n"
            "- JSON-RPC 2.0 /mcp endpoint (with optional Bearer token mcp_auth_token) exposes Memory Vault, Lore, Chat Search, safe files, and media tools to Gemini CLI or MCP clients.\n"
            "- /v1/models and /v1/chat/completions let external editors/scripts route straight through your Zero-Drop Brain."
        ),
        "tip": "On home Wi-Fi, open http://<LAN_IP>:8000 on your phone or tablet—external internet IPs are automatically blocked by lan_guard."
    },
    {
        "id": "specpulse_telemetry",
        "badge": "TELEMETRY",
        "title": "7. SpecPulse :: 60-FPS Visual Hardware Monitor & Benchmark",
        "summary": "Zero-overhead on-demand PCB hardware schematic, 64-bit VRAM detection, waveforms, and stress benchmarks.",
        "svg": "",
        "body": (
            "SpecPulse is embedded directly inside AetherVault Studio and consumes 0% CPU/GPU whenever closed.\n"
            "- 60-FPS Living Hardware Schematic: Interactive PCB diagram visualizing live data flow across CPU, RAM, GPU, Storage, and Motherboard. Click any block to inspect detailed hardware specs.\n"
            "- True 64-Bit GPU VRAM Reader: Reads HardwareInformation.qwMemorySize directly from Windows Registry to bypass the 4 GB 32-bit WMI AdapterRAM cap, plus live GPU 3D/Compute load & dedicated VRAM usage.\n"
            "- Mini-Benchmark Reactor Suite: Stress-tests Single-Core math, Multi-Core scaling, Memory bandwidth, and 128 MB sequential storage R/W inside isolated .temp_cache with automatic cleanup.\n"
            "- How to Open: Click 📊 SpecPulse in the sidebar or Live SVG HUD card, visit /specpulse, or run /specs in any console."
        ),
        "tip": "Install optional `py-cpuinfo` and `wmi` (Windows) from API & Library Manager for deepest CPU cache, motherboard, and DIMM telemetry."
    },
    {
        "id": "console_commands",
        "badge": "CONSOLE",
        "title": "8. Bootstrapper, Web Terminal & Telegram Console Commands",
        "summary": "Complete command reference shared across manager.py, Studio Web Terminal, and linked Telegram bots.",
        "svg": "",
        "body": (
            "Type any command into the Bootstrapper console bar, Studio 💻 Terminal tab, or linked Telegram bot:\n"
            "- /help : Show all available commands.\n"
            "- /status : Live model, GPU/CPU offload, RAM, mode, trust tier & LAN URL.\n"
            "- /specs : Deep SpecPulse hardware inventory (64-bit VRAM, CPU load, RAM).\n"
            "- /stop : Immediately halt an active generation or repetition loop.\n"
            "- /unload | /wake | /sleep [mins] : Free RAM/VRAM immediately, wake a sleeping GGUF, or set idle auto-sleep timeout (0 disables).\n"
            "- /inject <category> | <fact> : Save a fact straight into Priority #1 SQLite Memory Vault.\n"
            "- /toggle <setting> <value> : Flip toggles live (workspace_mode, workbench_trust, brain_mode, performance_mode, theme_preset, auto_web_search, unrestricted_tokens, osworld_enabled).\n"
            "- /py <code> : Execute Python in the killable subprocess Workbench without waking the LLM.\n"
            "- /pip <package> : Install any PyPI package into portable .venv.\n"
            "- /log [keyword] [lines] : Tail error_audit.log locally (works offline).\n"
            "- /telegram | /tunnel : Check Telegram worker queue or view Wi-Fi LAN / Cloudflare / Tailscale remote access tips.\n"
            "- /update | /restart : Pull cache-busted SHA-256-verified GitHub OTA updates or cleanly restart assistant_server.py."
        ),
        "tip": "In manager.py, press Up/Down arrows in the command bar to cycle through your recent console history."
    },
    {
        "id": "errors_selfheal",
        "badge": "TROUBLESHOOTING",
        "title": "9. Error Dictionary (ERR-01–ERR-14), Anti-Ouroboros Self-Heal & Legacy PCs",
        "summary": "Predetermined recovery registry, syntax-gated core patch staging, and 2015 laptop / legacy iGPU tuning.",
        "svg": SVG_SELFHEAL,
        "body": (
            "PREDETERMINED ERROR REGISTRY:\n"
            "- ERR-01 / ERR-02: No GGUF loaded or still loading -> pick/download a .gguf in sidebar or wait for top status bar.\n"
            "- ERR-03 / ERR-04: Context overflow or repetition loop -> auto-healed by prompt compactor / Delirium Watchdog.\n"
            "- ERR-05: Stopped by user -> partial reply saved cleanly.\n"
            "- ERR-06 / ERR-07 / ERR-08: Web Search / Spotify / Image API hiccup -> automatic multi-tier & desktop fallbacks engage.\n"
            "- ERR-09 / ERR-10: OSWorld corner failsafe or engine hiccup -> caught safely; inspect /log.\n"
            "- ERR-11 / ERR-12: Malformed boot index or unreadable PDF -> quarantined so the rest of your Knowledge Tree stays online.\n"
            "- ERR-13 / ERR-14 (Legacy Hardware): Older AMD/Intel iGPU Vulkan failure or low-RAM machine -> auto-switches to Safe CPU Mode. In manager.py choose Option 6 -> Safe CPU Build, pick a 1.5B–3B Q4_K_M GGUF, and select Governor 'Laptop 2015 (Fast)'.\n"
            "ANTI-OUROBOROS SELF-HEAL: Core files (assistant_server.py, ui_studio.html, manager.py) cannot be overwritten directly by the AI. Patches are staged in /self_heal_staging, verified with py_compile/AST, approved by you, and backed up into stock_vault/*.good."
        ),
        "tip": "If an experimental edit ever misbehaves, click 'Restore Golden Backup' in manager.py or Diagnostics -> Rollback (.good)."
    },
    {
        "id": "portable_privacy_license",
        "badge": "PORTABILITY & LEGAL",
        "title": "10. Portable .ZIP Migration, Zero-Telemetry Privacy & Licensing",
        "summary": "Move your entire studio in one .ZIP file with zero cloud lock-in and transparent dual licensing.",
        "svg": "",
        "body": (
            "PORTABLE .ZIP EXPORT & IMPORT:\n"
            "- Export packs memory_core.db, workspace_config.json, user_profile_card.json, pseudo_memory_index.json, glossary_index.json, partner_evolution.json, /priority_pdfs, /memory_vault, /chat_logs, /custom_assets (avatars/wallpapers), and generated media into one portable .zip.\n"
            "- API keys (api_keys_vault.json) are excluded from .ZIP exports by default unless you explicitly check 'Include my custom API keys'.\n"
            "ZERO TELEMETRY & PRIVACY GUARANTEE:\n"
            "- No analytics, tracking pixels, crash reporters, or hidden phone-home traffic. Flip Offline Mode ON to block 100% of outbound network calls.\n"
            "DUAL LICENSING & ATTRIBUTION:\n"
            "- Source Code: MIT License.\n"
            "- Branding, Logo (aethervault_logo.svg), Manual PDF & Documentation: Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) — credit Enzeru (EnZeeeRu).\n"
            "- Made with ❤️ in Argentina by Enzeru, in collaboration with Google Gemini."
        ),
        "tip": "Stock Offline Vault (Option 5 in manager.py) caches Python .whl installers, golden scripts, and local GGUFs so you can rebuild .venv completely offline."
    },
]

MANUAL_SECTIONS_ES = [
    {
        "id": "overview",
        "badge": "ARQUITECTURA",
        "title": "1. Mapa del Sistema, Bootstrapper Congelado y Estructura de Carpetas",
        "summary": "Cómo se conectan el lanzador permanente de 3 archivos, el runtime modular avs/ y tus bóvedas locales portables.",
        "svg": SVG_ARCHITECTURE,
        "body": (
            "AetherVault Studio v6.8 Bluesky es una estación de trabajo 100% portable y sin rastros de IA local, Python Workbench, puente AT Protocol y telemetría de hardware.\n"
            "BOOTSTRAPPER DE 3 ARCHIVOS (CAPA DE ENTRADA CONGELADA):\n"
            "- Launch.bat (Windows) y Launch.sh (macOS/Linux): Detectan Python 3.10+, ofrecen instalación automática y ejecutan manager.py.\n"
            "- manager.py: Centro de Control permanente (GUI tkinter + modo CLI automático). Lee la versión del runtime desde manifest.json, arma el entorno aislado .venv, auto-hidrata archivos faltantes al arrancar y descarga actualizaciones OTA verificadas con SHA-256 sin pisar tus datos personales.\n"
            "RUNTIME MODULAR (13 MÓDULOS EN avs/):\n"
            "- assistant_server.py, ui_studio.html, locales/en.json y locales/es.json.\n"
            "- Módulos avs/: contracts, memory_graph, referee, tool_registry, bridges, turn_pipeline, model_polish, language_tools, manual_assets, platform_bridge, toolbox, workbench, hardware_monitor.\n"
            "DATOS PORTABLES DEL USUARIO (INCLUIDOS EN .ZIP):\n"
            "- workspace_config.json, user_profile_card.json, memory_core.db, memory_vault/, priority_pdfs/, chat_logs/, models/ (GGUF y paquetes Argos en models/translate/), custom_tools/, custom_assets/, stock_vault/ y .temp_cache/ (se limpia automáticamente)."
        ),
        "tip": "Ejecutá `python tests/smoke.py` (u Opción 9 en manager.py) en cualquier momento para verificar sintaxis, módulos avs/, seguridad del Workbench y checksums SHA-256."
    },
    {
        "id": "brain_modes",
        "badge": "INFERENCIA Y MODOS",
        "title": "2. Cerebro de 2 Marchas, Afinación Multi-Modelo y Modos de Trabajo",
        "summary": "Enrutamiento Reflex vs. Profundo/Operador, Cascada BYOK Cloud, Idle Sleep y Guardrail Blender.",
        "svg": SVG_BRAIN_PIPELINE,
        "body": (
            "CEREBRO OFFLINE POR DEFECTO: gemma-4-E4B-it-Q4_K_M.gguf (~5.0 GB, Apache-2.0), elegido por su excelente precisión con herramientas del Workbench y fluidez local. Podés cambiar a cualquier .gguf (Qwen2.5, Llama 3.2, DeepSeek-R1, Hermes 3, Dolphin 3, Mistral); avs/model_polish.py adapta automáticamente los parámetros y la limpieza de salida.\n"
            "MODOS DE ESPACIO DE TRABAJO:\n"
            "- Modo Asistente y Workbench: Bloquea el Lore RAG para que los datos reales de tu PC/clima/web siempre tengan prioridad; limpia ecos <think> y narración escénica.\n"
            "- Modo Roleplay y Lore: Desbloquea recuperación bajo demanda desde /priority_pdfs y conserva la voz expresiva del personaje.\n"
            "MODOS DE CEREBRO (ZERO-DROP):\n"
            "- local_only: 100% offline con GGUF local.\n"
            "- smart_api: Cascada priorizada BYOK (Gemini, HF Router, Groq, OpenRouter, DeepSeek, Mistral, OpenAI, LAN local) con rotación de claves.\n"
            "- hybrid: Usa Smart API primero y cae automáticamente a tu GGUF local de respaldo si te quedás sin internet o cuota.\n"
            "IDLE SLEEP: Descarga automáticamente el GGUF de la RAM/VRAM tras idle_unload_minutes (10 min por defecto) y lo despierta en tu próximo mensaje."
        ),
        "tip": "Usá `/unload` para liberar RAM/VRAM al instante antes de abrir un juego pesado, y `/wake` (o mandá un mensaje) para volver a cargarlo."
    },
    {
        "id": "workbench_guide",
        "badge": "WORKBENCH Y PLUGINS",
        "title": "3. Python Workbench en Vivo (vault.*), Niveles de Confianza y custom_tools/",
        "summary": "Ejecutá acciones reales en tu PC, web, clima, Spotify, idioma y plugins seguros mediante bloques ```workbench.",
        "svg": SVG_WORKBENCH,
        "body": (
            "WEB, CLIMA, IDIOMA Y MULTIMEDIA:\n"
            "- vault.web('palabras') | vault.fetch_url('https://...') | vault.docs('tema') | vault.youtube('búsqueda', private=True)\n"
            "- vault.weather() : Pronóstico en vivo Open-Meteo (2 días) usando tu Tarjeta de Perfil / pin del mapa.\n"
            "- vault.spellcheck(texto, lang='auto') | vault.translate(texto, to='es', src='auto') | vault.detect_lang(texto)\n"
            "- vault.spotify('current_track'|'playlists'|'play_playlist'|'play_album'|'liked'|'play_liked'|'play'|'pause'|'next'|'prev', 'consulta')\n"
            "PC, ARCHIVOS, SISTEMA Y SUBPROCESO AISLADO:\n"
            "- vault.pc_info() | vault.specs() | vault.disk_usage() | vault.ps_list(20) | vault.debug_log() | vault.pip_list()\n"
            "- vault.files('steam'|'C:/ruta'|'palabra') | vault.read_file(ruta) | vault.chunk_read(ruta, 0, 10000)\n"
            "- vault.write_desktop('nota.txt', texto) | vault.write_file(ruta, texto) | vault.open_app('steam'|'notepad') | vault.browser(url, private=True)\n"
            "- vault.clipboard('read'|'write', texto) | vault.notify(título, msg) | vault.timer(seg, msg)\n"
            "- vault.run_cmd('powershell') [Solo Full PC] | vault.run_isolated(código, timeout=15)\n"
            "PLUGINS HOT-RELOAD Y CONTROL DEL ESTUDIO:\n"
            "- vault.create_tool(nombre, código, test_code) -> Valida sintaxis y sandbox antes de recargar en vault.plugins.<nombre>.\n"
            "- vault.toggle(ajuste, valor) | vault.settings() | vault.profile() | vault.update_profile(...) | vault.test_all()"
        ),
        "tip": "Safe Auto bloquea borrados destructivos, comandos de consola y clics directos de OSWorld hasta que habilites explícitamente Full PC Control."
    },
    {
        "id": "multilanguage_spellcheck",
        "badge": "MULTI-IDIOMA",
        "title": "4. Multi-Idioma Universal, Corrector Ortográfico Offline y Argos Translate",
        "summary": "Cambiá toda la interfaz, el micrófono, búsquedas locales, corrector respetuoso con tu Lore y traducción neural offline.",
        "svg": SVG_MULTILANG,
        "body": (
            "1. LOCALIZACIÓN COMPLETA DE LA INTERFAZ (locales/en.json y locales/es.json):\n"
            "- Usá el selector 🌐 en la barra superior (o Ajustes -> Puentes, Idioma y Voz) para cambiar botones, tarjetas, pestañas y este Manual Visual entre Inglés y Español al instante, 100% offline.\n"
            "2. MICRÓFONO, ENRUTADORES Y BÚSQUEDAS CONSCIENTES DEL IDIOMA:\n"
            "- El micrófono (🎤) usa tu speech_locale configurado (es-AR, es-ES, en-US, pt-BR, fr-FR, de-DE, ja-JP).\n"
            "- El enrutador bilingüe reconoce pedidos en español e inglés para clima, Spotify, noticias, web y herramientas del PC.\n"
            "- Google News RSS, Open-Meteo y OpenStreetMap siguen automáticamente tu idioma activo.\n"
            "3. CORRECTOR ORTOGRÁFICO OFFLINE RESPETUOSO CON TU LORE:\n"
            "- Tocá ✨ en la barra de chat (o usá vault.spellcheck(texto)) para revisar ortografía en 9+ idiomas con `pyspellchecker` + `langid` (con respaldo integrado si no están instalados).\n"
            "- Incluye automáticamente en la lista blanca tu glossary_index.json, vocabulario de Lore y nombres de personajes para nunca arruinar términos inventados.\n"
            "4. TRADUCCIÓN NEURAL OFFLINE (ARGOS TRANSLATE):\n"
            "- Instalá `argostranslate` desde el Gestor de APIs y descargá pares (ej. en->es, es->en) directo en `models/translate/`.\n"
            "- Traducí cualquier burbuja con 🌐 Traducir, usá vault.translate() o activá el Puente Argos opcional para modelos GGUF solo en inglés."
        ),
        "tip": "Dejá el Puente de Traducción en 'Idioma Nativo del Modelo' para modelos multilingües como Gemma 4, Qwen 2.5 o Gemini; activá 'Puente Argos Offline' solo para GGUFs solo-inglés."
    },
    {
        "id": "memory_profile_lore",
        "badge": "MEMORIA Y LORE",
        "title": "5. Tarjeta de Perfil, Mapa OpenStreetMap, Compactador de Memoria y Árbol de Conocimiento",
        "summary": "Clima por coordenadas exactas, deduplicación SQLite en segundo plano, Mapa Mental de palabras clave y archivos CORE vs. LORE.",
        "svg": "",
        "body": (
            "TARJETA DE PERFIL Y PIN OPENSTREETMAP:\n"
            "- Guardá tu nombre/alias, ciudad, código postal, pin exacto (lat/lon) en mapa interactivo, campos personalizados y Datos Fijados.\n"
            "- La tarjeta lateral etiqueta claramente Usuario, Pin Mapa, Ubicación, Campos Personalizados y un bloque rotativo de Datos Fijados (cambia cada 12s, se pausa al pasar el cursor y tiene botón ↻ Sig.).\n"
            "COMPACTADOR EN SEGUNDO PLANO Y MAPA MENTAL (avs/memory_graph.py):\n"
            "- Fusiona duplicados y reemplaza datos obsoletos de ranura única (ubicación, nombre, CP) en SQLite (active = 0) sin gastar tokens del LLM.\n"
            "- Construye un mapa mental de co-ocurrencia de 1 salto para potenciar la búsqueda de Lore.\n"
            "ÁRBOL DE CONOCIMIENTO (/priority_pdfs):\n"
            "- Arrastrá archivos .pdf, .txt o .md y cambiá cada uno entre CORE (cargado 24/7) y LORE (RAG bajo demanda, bloqueado en Modo Asistente)."
        ),
        "tip": "Las instrucciones dirigidas a la IA (como 'acordate de que podés...') se filtran automáticamente para no ensuciar tus Datos Fijados."
    },
    {
        "id": "bridges_ecosystem",
        "badge": "PUENTES Y APIs",
        "title": "6. Puentes: Bluesky AT Protocol, Bot de Telegram, MCP y OpenAI /v1",
        "summary": "Conectá tu estación local con Bluesky, Telegram, VS Code, Gemini CLI y tus dispositivos por Wi-Fi.",
        "svg": SVG_BRIDGES,
        "body": (
            "PUENTE BLUESKY (AT PROTOCOL):\n"
            "- Configurá tu Handle y App Password en Ajustes -> Puentes para publicar (máx. 300 caracteres vía POST /api/bluesky/post) y opcionalmente responder menciones nuevas de cuentas permitidas.\n"
            "BOT DE TELEGRAM Y MINI APP:\n"
            "- Pegá tu token de @BotFather para chatear, sacar capturas, controlar Spotify y ejecutar comandos desde cualquier lugar sin abrir puertos.\n"
            "SERVIDOR MCP (/mcp) Y OPENAI /v1:\n"
            "- Endpoint JSON-RPC 2.0 /mcp (con token Bearer opcional) para Gemini CLI y clientes MCP, más /v1/models y /v1/chat/completions compatibles con OpenAI."
        ),
        "tip": "En el Wi-Fi de tu casa abrí http://<IP_LAN>:8000 desde el celular; las IPs externas quedan bloqueadas automáticamente por lan_guard."
    },
    {
        "id": "specpulse_telemetry",
        "badge": "TELEMETRÍA",
        "title": "7. SpecPulse :: Monitor Visual de Hardware a 60 FPS y Benchmark",
        "summary": "Esquemático PCB interactivo, lectura real de VRAM de 64 bits, ondas en vivo y pruebas de rendimiento con 0% de carga al cerrarse.",
        "svg": "",
        "body": (
            "SpecPulse está integrado dentro del estudio y consume 0% de CPU/GPU cuando está cerrado.\n"
            "- Esquemático vivo a 60 FPS: Flujo de datos en tiempo real entre CPU, RAM, GPU, Almacenamiento y Motherboard.\n"
            "- Lector real de VRAM de 64 bits: Lee HardwareInformation.qwMemorySize del Registro de Windows para superar el límite de 4 GB de WMI.\n"
            "- Suite de Mini-Benchmark: Evalúa rendimiento Single-Core, Multi-Core, ancho de banda de RAM y lectura/escritura secuencial de 128 MB en .temp_cache.\n"
            "- Cómo abrirlo: Tocá 📊 SpecPulse en la barra lateral, abrí /specpulse o ejecutá /specs en la consola."
        ),
        "tip": "Instalá los paquetes opcionales `py-cpuinfo` y `wmi` (Windows) desde el Gestor de Librerías para lectura completa de caché de CPU y módulos de RAM."
    },
    {
        "id": "console_commands",
        "badge": "CONSOLA",
        "title": "8. Comandos de Consola (Bootstrapper, Terminal Web y Telegram)",
        "summary": "Referencia rápida compartida entre manager.py, la pestaña Terminal Web y tu Bot de Telegram.",
        "svg": "",
        "body": (
            "Comandos disponibles en la barra del Bootstrapper, la pestaña 💻 Terminal o tu Bot de Telegram:\n"
            "- /help : Lista todos los comandos.\n"
            "- /status : Modelo activo, GPU/CPU, RAM, modo, nivel de confianza y URL LAN.\n"
            "- /specs : Inventario profundo SpecPulse (VRAM 64-bit, carga de CPU/GPU, RAM).\n"
            "- /stop : Detiene al instante cualquier generación activa.\n"
            "- /unload | /wake | /sleep [mins] : Libera RAM/VRAM, despierta el GGUF o ajusta el auto-reposo.\n"
            "- /inject <categoría> | <dato> : Guarda un dato directo en la Bóveda de Memoria SQLite.\n"
            "- /toggle <ajuste> <valor> : Cambia ajustes en vivo (workspace_mode, workbench_trust, brain_mode, theme_preset, etc.).\n"
            "- /py <código> | /pip <paquete> | /log [filtro] [líneas] : Subproceso Python, instalación PyPI o lectura de error_audit.log.\n"
            "- /telegram | /tunnel | /update | /restart : Estado de Telegram, acceso remoto, actualización OTA verificada con SHA-256 o reinicio limpio."
        ),
        "tip": "En manager.py podés usar las flechas Arriba/Abajo para recorrer tu historial de comandos."
    },
    {
        "id": "errors_selfheal",
        "badge": "SOLUCIONES",
        "title": "9. Diccionario de Errores (ERR-01–ERR-14), Auto-Reparación y Hardware Antiguo",
        "summary": "Recuperación automática, parches supervisados Anti-Ouroboros y afinación para laptops 2015 / iGPUs antiguas.",
        "svg": SVG_SELFHEAL,
        "body": (
            "CÓDIGOS DE DIAGNÓSTICO:\n"
            "- ERR-01 / ERR-02: Sin GGUF cargado o aún cargando -> elegí/descargá un .gguf o esperá a la barra superior.\n"
            "- ERR-03 / ERR-04: Desborde de contexto o bucle de repetición -> auto-corregido por el compactador y el Watchdog.\n"
            "- ERR-05: Detenido por el usuario -> respuesta parcial guardada.\n"
            "- ERR-06 / ERR-07 / ERR-08: Fallo en Web / Spotify / Imágenes -> respaldos automáticos multi-nivel activados.\n"
            "- ERR-09 / ERR-10: Failsafe de OSWorld o fallo de inferencia -> atrapado sin cerrar el servidor (revisá /log).\n"
            "- ERR-11 / ERR-12: Índice corrupto o PDF ilegible -> aislado automáticamente.\n"
            "- ERR-13 / ERR-14 (PCs Antiguas): Error de Vulkan en iGPU/APU o poca RAM -> cambia a Modo CPU Seguro. En manager.py elegí Opción 6 -> Safe CPU Build, usá un GGUF 1.5B–3B Q4_K_M y el gobernador 'Laptop 2015 (Fast)'.\n"
            "AUTO-REPARACIÓN ANTI-OUROBOROS: La IA jamás sobreescribe archivos críticos directo; propone parches en /self_heal_staging verificados con py_compile para tu aprobación, guardando respaldo .good en stock_vault/."
        ),
        "tip": "Si un cambio experimental falla, usá 'Restore Golden Backup' en manager.py o el botón Rollback (.good) en Diagnóstico."
    },
    {
        "id": "portable_privacy_license",
        "badge": "PORTABILIDAD Y LEGAL",
        "title": "10. Migración Portable .ZIP, Privacidad Cero-Telemetría y Licencias",
        "summary": "Llevate tu estudio completo en un solo archivo .ZIP con cero telemetría y licenciamiento transparente.",
        "svg": "",
        "body": (
            "EXPORTACIÓN E IMPORTACIÓN .ZIP:\n"
            "- Empaqueta memory_core.db, workspace_config.json, user_profile_card.json, índices de memoria, /priority_pdfs, /memory_vault, /chat_logs, /custom_assets y multimedia en un solo archivo portable.\n"
            "- Tus claves API (api_keys_vault.json) se excluyen por defecto salvo que marques la casilla para incluirlas.\n"
            "GARANTÍA DE PRIVACIDAD CERO TELEMETRÍA:\n"
            "- Sin analíticas, rastreadores ni conexiones ocultas. Activá Modo Offline para cortar el 100% del tráfico saliente.\n"
            "LICENCIAS Y ATRIBUCIÓN:\n"
            "- Código fuente: Licencia MIT.\n"
            "- Marca, Logo (aethervault_logo.svg), Manual PDF y Documentación: CC BY-NC 4.0 — crédito a Enzeru (EnZeeeRu).\n"
            "- Hecho con ❤️ en Argentina por Enzeru, en colaboración con Google Gemini."
        ),
        "tip": "La Opción 5 de manager.py (Stock Offline Vault) guarda instaladores .whl, copias doradas y modelos GGUF para reconstruir tu .venv sin internet."
    },
]


def get_manual_sections(lang: str = "en") -> list[dict]:
    code = (lang or "en").strip().lower()[:2]
    return MANUAL_SECTIONS_ES if code == "es" else MANUAL_SECTIONS_EN
