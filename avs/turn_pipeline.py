"""Shared turn post-processing & orchestration helpers for AetherVault Studio (v6.5)."""
import re
from avs.contracts import MAX_ROUNDS, MAX_OBS_CHARS, MAX_OBS_LINES, clamp_text
from avs.referee import strip_echoes, check_exclusive_titles, is_abrupt_reply


def bounded_rounds(requested_rounds: int, max_allowed: int = MAX_ROUNDS) -> int:
    """Enforces a strict static upper bound on multi-step Workbench/tool rounds."""
    cap = max(1, int(max_allowed))
    try:
        val = int(requested_rounds)
    except Exception:
        val = 2
    return max(1, min(cap, val))


def compact_observations(observations: list[str], max_chars: int = MAX_OBS_CHARS, max_lines: int = MAX_OBS_LINES) -> str:
    """Combines and compacts tool/workbench observations with deduplicated adjacent lines."""
    if not observations:
        return ""
    raw = "\n\n".join(str(x).strip() for x in observations if str(x).strip())
    if not raw:
        return ""
    lines = [ln.rstrip() for ln in raw.splitlines() if ln.strip()]
    deduped: list[str] = []
    for ln in lines:
        if not deduped or ln != deduped[-1]:
            deduped.append(ln)
    line_cap = max(6, int(max_lines))
    if len(deduped) > line_cap:
        head_n = line_cap // 2
        tail_n = line_cap - head_n
        deduped = deduped[:head_n] + [f"... ({len(lines) - line_cap} middle lines compacted) ..."] + deduped[-tail_n:]
    return clamp_text("\n".join(deduped).strip(), max_chars=max_chars)


def finalize_turn_reply(
    raw_reply: str,
    ai_name: str = "Aether",
    user_name: str = "Creator",
    evidence_pool: str = "",
) -> dict:
    """
    Shared post-generation referee pass across chat, Telegram, and Bluesky:
    - Strips reasoning echoes, turn leaks, and excessive blank lines.
    - Checks exclusive/unique titles against available CORE/LORE context.
    - Flags abrupt/truncated replies for optional continuation stitching.
    """
    cleaned = strip_echoes(raw_reply or "", ai_name=ai_name, user_name=user_name)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    if not cleaned:
        cleaned = "✅ Done."
    warnings = check_exclusive_titles(cleaned, evidence_pool)
    abrupt = is_abrupt_reply(cleaned)
    return {
        "reply": cleaned,
        "warnings": warnings,
        "abrupt": abrupt,
    }
