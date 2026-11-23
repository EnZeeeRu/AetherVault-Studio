"""Model-agnostic behavioral polisher & audit helpers for AetherVault Studio (v6.7)."""
import re


def normalize_model_output(
    text: str,
    ai_name: str = "Aether",
    user_name: str = "Creator",
    is_assistant_mode: bool = True,
) -> str:
    """
    Cleans output from ANY local GGUF or cloud model (Gemma, Qwen, Llama, Mistral,
    DeepSeek, Hermes, Gemini, Groq, etc.) without stripping roleplay/creative voice
    when in roleplay mode, while keeping assistant/tool mode crisp and grounded.
    """
    s = (text or "").strip()
    if not s:
        return ""

    # Strip internal reasoning tags, control tokens, and leaked turn headers across model families
    s = re.sub(r"<\|think\|>[\s\S]*?<\|/think\|>", "", s, flags=re.IGNORECASE)
    s = re.sub(r"<think>[\s\S]*?</think>", "", s, flags=re.IGNORECASE)
    if "<think>" in s and "</think>" not in s:
        s = s.split("<think>", 1)[0]
    s = re.sub(r"<end_of_turn>|<start_of_turn>.*|<\|im_end\|>|<\|im_start\|>.*", "", s, flags=re.IGNORECASE | re.DOTALL)
    s = re.sub(rf"(?im)^\s*(?:{re.escape(ai_name)}|assistant|model)\s*:\s*", "", s)
    s = re.sub(rf"(?im)\n+(?:{re.escape(user_name)}|user|human|model|assistant)\s*:\s*$", "", s)

    # Remove generic canned assistant filler
    filler_patterns = [
        r"(?im)^(?:certainly!?|sure thing!?|of course!?|here is what i found:?)\s*",
        r"(?im)\b(?:let me know if you need anything else|how can i assist you today|as an ai(?: language model)?)[.!?]*\b",
    ]
    for fp in filler_patterns:
        s = re.sub(fp, "", s)

    # In assistant/operator mode, strip stage-action narration (*action*) so tool/PC replies stay direct
    if is_assistant_mode:
        s = re.sub(r"\*[^*\n]{1,100}\*", "", s)

    s = re.sub(r"\n{3,}", "\n\n", s).strip()
    if len(s) >= 2 and s.startswith("\"") and s.endswith("\"") and s.count("\"") == 2:
        s = s[1:-1].strip()
    return s


def classify_model_family(model_or_provider: str) -> str:
    """Identifies the general model/provider family for adaptive tuning without hardcoding a single model."""
    low = (model_or_provider or "").lower()
    if any(k in low for k in ("deepseek", "qwq", "r1")):
        return "reasoning_model"
    if any(k in low for k in ("coder", "codestral")):
        return "code_model"
    if any(k in low for k in ("dolphin", "hermes", "mistral", "rp", "roleplay")):
        return "expressive_chat"
    if any(k in low for k in ("gemma", "qwen", "llama")):
        return "compact_general"
    if any(k in low for k in ("gemini", "groq", "openrouter", "openai")):
        return "cloud_endpoint"
    return "general"


def provider_profile_hints(model_or_provider: str, workspace_mode: str = "assistant") -> dict:
    """Returns adaptive sampling & style hints across any model family and workspace mode."""
    family = classify_model_family(model_or_provider)
    is_rp = (workspace_mode or "").strip().lower() in ("roleplay", "rp")
    if family == "reasoning_model":
        return {"temperature": 0.65, "top_p": 0.92, "family": family, "style": "careful_reasoning"}
    if family == "code_model":
        return {"temperature": 0.45, "top_p": 0.90, "family": family, "style": "precise_technical"}
    if is_rp or family == "expressive_chat":
        return {"temperature": 0.80, "top_p": 0.95, "family": family, "style": "expressive_narrative"}
    if family == "cloud_endpoint":
        return {"temperature": 0.68, "top_p": 0.93, "family": family, "style": "fast_grounded"}
    return {"temperature": 0.72, "top_p": 0.94, "family": family, "style": "balanced_general"}
