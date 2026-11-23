"""Post-generation grounding referee, reasoning-echo stripper, and truncation detector."""
import re


def strip_echoes(text: str, ai_name: str = "Aether", user_name: str = "Creator") -> str:
    if not text:
        return ""
    s = re.sub(r"<\|think\|>[\s\S]*?<\|/think\|>", "", text, flags=re.IGNORECASE)
    s = re.sub(r"<think>[\s\S]*?</think>", "", s, flags=re.IGNORECASE)
    if "<think>" in s and "</think>" not in s:
        s = s.split("<think>", 1)[0]
    s = re.sub(rf"(?im)\n+(?:{re.escape(user_name)}|user|human|model|assistant)\s*:\s*$", "", s)
    s = re.sub(r"<end_of_turn>|<start_of_turn>.*", "", s, flags=re.IGNORECASE | re.DOTALL)
    return s.strip()


def check_exclusive_titles(reply_text: str, evidence_pool: str) -> list[str]:
    warnings: list[str] = []
    ev_low = (evidence_pool or "").lower()
    matches = re.findall(r"\b(?:the\s+(?:primary|sole|only|true|original)\s+[a-zA-Z0-9_-]{3,24})\b", reply_text or "", flags=re.IGNORECASE)
    for phrase in matches[:8]:
        tokens = [t.lower() for t in re.findall(r"[a-zA-Z]{4,}", phrase) if t.lower() not in ("primary", "sole", "only", "true", "original")]
        if tokens and not any(t in ev_low for t in tokens):
            warnings.append(f"Unverified exclusive title \x27{phrase}\x27 not found in CORE/LORE context.")
    return warnings


def is_abrupt_reply(reply_text: str) -> bool:
    t = (reply_text or "").strip()
    if len(t) < 40:
        return False
    if t.count("```") % 2 != 0:
        return True
    if t.endswith((",", ":", ";", "-", "(", "[", "/", "and", "or", "with", "to", "for", "in")):
        return True
    if len(t) >= 180 and t[-1] not in ".!?)\x27\"\x60”’" and not t.endswith("..."):
        return True
    return False
