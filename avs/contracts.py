"""Shared contracts, error codes, and input/output validators for AetherVault Studio (Power of 10 style)."""
from dataclasses import dataclass, field
from typing import Any, Optional

MAX_ROUNDS = 4
MAX_RETRIES = 1
MAX_OBS_CHARS = 3200
MAX_OBS_LINES = 50


@dataclass
class ToolSpec:
    name: str
    trust_tier: str = "safe_auto"  # "safe_auto" | "full_pc"
    description: str = ""
    aliases: tuple[str, ...] = ()


@dataclass
class ToolResult:
    ok: bool
    summary: str = ""
    data: Any = None
    error: Optional[str] = None
    media: dict[str, Optional[str]] = field(default_factory=lambda: {"image_url": None, "audio_url": None})


def clamp_text(text: str, max_chars: int = MAX_OBS_CHARS) -> str:
    if not text:
        return ""
    limit = max(64, int(max_chars))
    if len(text) <= limit:
        return text
    return text[:limit].rsplit("\n", 1)[0].strip() + f"\n... [Truncated at {limit} chars]"
