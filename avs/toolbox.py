"""
avs/toolbox.py — Unified tool manifest & help/OpenAI schema helper for AetherVault Studio.
"""
from typing import Dict, List


class _UnifiedToolbox:
    """Provides structured tool help text and OpenAI-compatible function schemas."""

    def __init__(self) -> None:
        self._topics: Dict[str, str] = {
            "web": "vault.web('keywords') | vault.fetch_url('https://...') | vault.docs('topic')",
            "weather": "vault.weather() -> Live Open-Meteo weather & 2-day forecast",
            "spotify": "vault.spotify('current_track'|'playlists'|'play_liked'|'play'|'pause'|'next'|'prev', 'query')",
            "files": "vault.files('query') | vault.read_file('path') | vault.chunk_read('path', 0) | vault.write_desktop('name.txt', 'text')",
            "pc": "vault.pc_info() | vault.specs() | vault.disk_usage() | vault.ps_list() | vault.open_app('app') | vault.browser(...)",
            "studio": "vault.toggle(setting, value) | vault.settings() | vault.pip_list()",
            "memory": "vault.profile() | vault.update_profile(...) | vault.memory_save(cat, fact) | vault.forget(id_or_kw)",
            "knowledge": "vault.knowledge_list() | vault.knowledge_write('lore/note.md', text) | vault.lore('keywords')",
            "media": "vault.generate_image('prompt') | vault.generate_music('prompt', duration=8)",
            "gauntlet": "vault.test_all(include_active=False) | vault.test_step('tool_name')",
        }

    def help_text(self, topic: str = "") -> str:
        t = (topic or "").strip().lower()
        if t:
            rows = [f"- {k}: {v}" for k, v in self._topics.items() if t in k or t in v.lower()]
            if rows:
                return "=== AVS TOOLBOX HELP ===\n" + "\n".join(rows)
        return "=== AVS TOOLBOX CHEATSHEET ===\n" + "\n".join(f"- {k}: {v}" for k, v in self._topics.items())

    def openai_schemas(self) -> List[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "run_workbench",
                    "description": "Execute Python code inside AetherVault's Workbench with the pre-imported `vault` bridge.",
                    "parameters": {
                        "type": "object",
                        "properties": {"code": {"type": "string"}},
                        "required": ["code"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Search the live web using zero-key multi-engine search.",
                    "parameters": {
                        "type": "object",
                        "properties": {"query": {"type": "string"}},
                        "required": ["query"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Fetch live weather and 2-day forecast for the user's saved location or a specified city.",
                    "parameters": {
                        "type": "object",
                        "properties": {"location": {"type": "string"}},
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_pc_info",
                    "description": "Retrieve live host PC hostname, OS, RAM, active brain, and installed Python libraries.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            },
        ]


toolbox = _UnifiedToolbox()
