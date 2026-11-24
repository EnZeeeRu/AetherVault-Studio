"""
avs/language_tools.py — Offline Multi-Language Detection, Lore-Safe Spellcheck & Argos Translate Bridge.
Zero required external dependencies: gracefully upgrades when optional `pyspellchecker`, `argostranslate`,
or `langid` packages are installed via the Studio API & Library Manager.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
from pathlib import Path
from typing import Any, Iterable

SUPPORTED_UI_LOCALES = {
    "en": {"name": "English", "native": "English", "speech": "en-US", "news_hl": "en-US", "news_gl": "US", "news_ceid": "US:en"},
    "es": {"name": "Spanish", "native": "Español", "speech": "es-AR", "news_hl": "es-419", "news_gl": "AR", "news_ceid": "AR:es-419"},
}

SPEECH_LOCALE_OPTIONS = [
    ("en-US", "English (US)"),
    ("en-GB", "English (UK)"),
    ("es-AR", "Español (Argentina)"),
    ("es-ES", "Español (España)"),
    ("es-MX", "Español (México)"),
    ("pt-BR", "Português (Brasil)"),
    ("fr-FR", "Français (France)"),
    ("de-DE", "Deutsch (Deutschland)"),
    ("it-IT", "Italiano (Italia)"),
    ("ja-JP", "日本語 (Japan)"),
]

SPELLCHECK_LANGS = {"en", "es", "fr", "de", "pt", "it", "ru", "ar", "nl"}

_FALLBACK_COMMON_TYPOS = {
    "en": {
        "teh": "the", "recieve": "receive", "seperate": "separate", "definately": "definitely",
        "occured": "occurred", "untill": "until", "wich": "which", "becuase": "because",
        "thier": "their", "beleive": "believe", "langauge": "language", "pelase": "please",
        "qeue": "queue", "ndentify": "identify", "repalce": "replace", "stilyze": "stylize",
        "everthing": "everything", "everythign": "everything", "autoupdate": "auto-update",
    },
    "es": {
        "qeu": "que", "porqeu": "porque", "tambien": "también", "tambíen": "también",
        "mas": "más", "aqui": "aquí", "asi": "así", "despues": "después", "quiza": "quizá",
        "facil": "fácil", "dificil": "difícil", "rapido": "rápido", "musica": "música",
        "cancion": "canción", "pronostico": "pronóstico", "traduccion": "traducción",
        "ortografia": "ortografía", "configuracion": "configuración", "informacion": "información",
    },
}

_LANG_STOP_HINTS = {
    "es": {"que", "para", "como", "pero", "este", "esta", "esto", "hola", "clima", "tiempo", "gracias", "por", "favor", "puedes", "podes", "poné", "pone", "quiero", "tengo", "donde", "dónde", "cómo", "qué", "estás", "estas", "canción", "cancion", "música", "musica", "buscar", "traducir", "idioma", "español"},
    "pt": {"você", "voce", "não", "nao", "para", "como", "obrigado", "olá", "ola", "tudo", "bem", "agora", "aqui", "música", "português"},
    "fr": {"bonjour", "merci", "avec", "pour", "dans", "vous", "nous", "mais", "très", "tres", "français", "salut", "comment"},
    "de": {"hallo", "danke", "nicht", "aber", "auch", "noch", "bitte", "wetter", "deutsch", "wie", "geht", "kannst"},
    "it": {"ciao", "grazie", "come", "stai", "molto", "bene", "italiano", "tempo", "musica", "questo"},
    "en": {"the", "and", "that", "this", "with", "what", "when", "where", "how", "please", "weather", "search", "play", "song", "thank", "thanks", "hello", "would", "could", "should"},
}


def configure_portable_argos_dir(model_dir: Path | None) -> Path | None:
    """Points Argos Translate package storage inside AetherVault's portable models/translate folder."""
    if not model_dir:
        return None
    t_dir = Path(model_dir) / "translate"
    t_dir.mkdir(parents=True, exist_ok=True)
    os.environ["ARGOS_PACKAGES_DIR"] = str(t_dir)
    return t_dir


def detect_language(text: str, default: str = "en") -> str:
    """Offline language detector (uses optional `langid` if installed, else deterministic stdlib heuristics)."""
    sample = (text or "").strip()
    if not sample:
        return default

    # Fast script checks for non-Latin scripts
    if re.search(r"[\u3040-\u30ff]", sample):
        return "ja"
    if re.search(r"[\uac00-\ud7af]", sample):
        return "ko"
    if re.search(r"[\u4e00-\u9fff]", sample):
        return "zh"
    if re.search(r"[\u0400-\u04ff]", sample):
        return "ru"
    if re.search(r"[\u0600-\u06ff]", sample):
        return "ar"

    if importlib.util.find_spec("langid") is not None and len(sample) >= 18:
        try:
            import langid  # type: ignore
            code, _conf = langid.classify(sample)
            if code and len(code) == 2:
                return code.lower()
        except Exception:
            pass

    low = sample.lower()
    if "¿" in sample or "¡" in sample or "ñ" in low:
        return "es"

    words = re.findall(r"[a-zA-Záéíóúüñçàèìòùâêîôûäöüß]+", low)
    if not words:
        return default

    scores: dict[str, float] = {}
    for code, hints in _LANG_STOP_HINTS.items():
        scores[code] = sum(1.0 for w in words if w in hints)
    if any(ch in low for ch in ("á", "é", "í", "ó", "ú")):
        scores["es"] = scores.get("es", 0.0) + 1.2
    if any(ch in low for ch in ("ã", "õ", "ç")):
        scores["pt"] = scores.get("pt", 0.0) + 1.5
    if any(ch in low for ch in ("ä", "ö", "ü", "ß")):
        scores["de"] = scores.get("de", 0.0) + 1.5

    best_code = max(scores, key=lambda k: scores[k])
    if scores.get(best_code, 0.0) >= 1.0:
        return best_code
    return default


def _preserve_case(orig: str, repl: str) -> str:
    if not orig or not repl:
        return repl
    if orig.isupper():
        return repl.upper()
    if orig[0].isupper():
        return repl[0].upper() + repl[1:]
    return repl


def spellcheck_text(
    text: str,
    lang: str = "auto",
    custom_words: Iterable[str] | None = None,
    max_issues: int = 25,
) -> dict[str, Any]:
    """
    Universal offline multi-language spell checker with Lore/Glossary custom-word whitelisting.
    - Uses `pyspellchecker` when installed (supports en, es, fr, de, pt, it, ru, ar, nl).
    - Falls back cleanly to a lightweight built-in typo & repeated-word checker when offline/uninstalled.
    - Never alters code blocks, URLs, slash commands, or whitelisted lore/character names.
    """
    raw = str(text or "")
    if not raw.strip():
        return {"ok": True, "lang": "en", "engine": "noop", "issues": [], "corrected": raw, "whitelisted_count": 0}

    use_lang = detect_language(raw) if (not lang or lang == "auto") else str(lang).strip().lower()[:2]
    if use_lang not in SPELLCHECK_LANGS:
        use_lang = "en"

    whitelist = {
        "aethervault", "specpulse", "osworld", "gguf", "vulkan", "bluesky", "atproto",
        "spotipy", "fastapi", "uvicorn", "pymupdf", "sqlite", "workbench", "bootstrapper",
        "gemma", "deepseek", "qwen", "llama", "mistral", "hermes", "dolphin", "enzeru", "enzy",
        "posadas", "misiones", "argostranslate", "pyspellchecker", "json", "mcp", "ota", "vram",
    }
    for w in (custom_words or []):
        tok = str(w or "").strip().lower()
        if len(tok) >= 2:
            whitelist.add(tok)

    # Mask fenced code blocks & URLs so we never corrupt code or links
    protected_spans: list[tuple[int, int]] = []
    for pat in (r"```[\s\S]*?```", r"`[^`\n]+`", r"https?://\S+", r"\bvault\.[a-zA-Z0-9_]+", r"/[a-zA-Z0-9_/-]+"):
        for m in re.finditer(pat, raw):
            protected_spans.append((m.start(), m.end()))

    def _in_protected(pos: int) -> bool:
        return any(s <= pos < e for s, e in protected_spans)

    issues: list[dict[str, Any]] = []
    replacements: list[tuple[int, int, str]] = []
    engine_name = "builtin-fallback"

    has_pyspell = importlib.util.find_spec("spellchecker") is not None
    if has_pyspell:
        try:
            from spellchecker import SpellChecker  # type: ignore
            sc = SpellChecker(language=use_lang)
            sc.word_frequency.load_words(whitelist)
            engine_name = f"pyspellchecker ({use_lang})"
            for m in re.finditer(r"\b([A-Za-zÁÉÍÓÚÜÑáéíóúüñÇçÀÈÌÒÙàèìòùÂÊÎÔÛâêîôûÄÖÜäöüß]{2,32})\b", raw):
                if _in_protected(m.start()):
                    continue
                word = m.group(1)
                low_w = word.lower()
                if low_w in whitelist or word.isupper():
                    continue
                if low_w in sc.unknown([low_w]):
                    best = sc.correction(low_w) or ""
                    cands = [c for c in (sc.candidates(low_w) or []) if c and c != low_w][:4]
                    if best and best != low_w and best not in cands:
                        cands.insert(0, best)
                    if cands:
                        sug = _preserve_case(word, cands[0])
                        issues.append({
                            "word": word,
                            "suggestions": [_preserve_case(word, c) for c in cands[:4]],
                            "start": m.start(),
                            "end": m.end(),
                        })
                        replacements.append((m.start(), m.end(), sug))
                        if len(issues) >= max_issues:
                            break
        except Exception:
            has_pyspell = False

    if not has_pyspell:
        typo_map = _FALLBACK_COMMON_TYPOS.get(use_lang, _FALLBACK_COMMON_TYPOS["en"])
        for m in re.finditer(r"\b([A-Za-zÁÉÍÓÚÜÑáéíóúüñ]{2,32})\b", raw):
            if _in_protected(m.start()):
                continue
            word = m.group(1)
            low_w = word.lower()
            if low_w in whitelist:
                continue
            if low_w in typo_map:
                sug = _preserve_case(word, typo_map[low_w])
                if sug != word:
                    issues.append({"word": word, "suggestions": [sug], "start": m.start(), "end": m.end()})
                    replacements.append((m.start(), m.end(), sug))
                    if len(issues) >= max_issues:
                        break
        # Also catch immediate repeated words ("the the", "de de")
        for m in re.finditer(r"\b([A-Za-zÁÉÍÓÚÜÑáéíóúüñ]{2,})\s+\1\b", raw, flags=re.IGNORECASE):
            if _in_protected(m.start()):
                continue
            issues.append({"word": m.group(0), "suggestions": [m.group(1)], "start": m.start(), "end": m.end()})
            replacements.append((m.start(), m.end(), m.group(1)))

    corrected = raw
    for s_idx, e_idx, sug in sorted(replacements, key=lambda x: x[0], reverse=True):
        corrected = corrected[:s_idx] + sug + corrected[e_idx:]

    return {
        "ok": True,
        "lang": use_lang,
        "engine": engine_name,
        "pyspellchecker_installed": has_pyspell,
        "issue_count": len(issues),
        "issues": issues,
        "corrected": corrected,
        "whitelisted_count": len(whitelist),
        "hint": "" if has_pyspell else "Install 'pyspellchecker' in API & Library Manager for full multi-language dictionary coverage.",
    }


def list_installed_argos_pairs(model_dir: Path | None = None) -> list[dict[str, str]]:
    """Lists locally installed offline Argos Translate language pairs inside models/translate/."""
    configure_portable_argos_dir(model_dir)
    if importlib.util.find_spec("argostranslate") is None:
        return []
    try:
        import argostranslate.package as argos_pkg  # type: ignore
        pkgs = argos_pkg.get_installed_packages() or []
        return [
            {
                "from_code": getattr(p, "from_code", ""),
                "to_code": getattr(p, "to_code", ""),
                "from_name": getattr(p, "from_name", ""),
                "to_name": getattr(p, "to_name", ""),
                "pair": f"{getattr(p, 'from_code', '')}->{getattr(p, 'to_code', '')}",
            }
            for p in pkgs
        ]
    except Exception:
        return []


def install_argos_language_pair(from_code: str, to_code: str, model_dir: Path | None = None, offline_mode: bool = False) -> dict[str, Any]:
    """Downloads and installs an offline .argosmodel language pack into models/translate/."""
    if offline_mode:
        return {"ok": False, "error": "Offline Mode is ON — disable Offline Mode briefly to download the language pack."}
    if importlib.util.find_spec("argostranslate") is None:
        return {"ok": False, "error": "Package 'argostranslate' is not installed yet. Install it from the API & Library Manager sidebar first!"}
    fc = (from_code or "en").strip().lower()[:2]
    tc = (to_code or "es").strip().lower()[:2]
    if fc == tc:
        return {"ok": False, "error": "Source and target languages must be different."}
    configure_portable_argos_dir(model_dir)
    try:
        import argostranslate.package as argos_pkg  # type: ignore
        argos_pkg.update_package_index()
        available = argos_pkg.get_available_packages() or []
        match = next((p for p in available if p.from_code == fc and p.to_code == tc), None)
        if not match:
            return {"ok": False, "error": f"No Argos offline language pack found for '{fc} -> {tc}'."}
        dl_path = match.download()
        argos_pkg.install_from_path(dl_path)
        return {
            "ok": True,
            "pair": f"{fc}->{tc}",
            "message": f"Installed offline Argos Translate pack '{fc} -> {tc}' into portable models/translate/!",
            "installed_pairs": list_installed_argos_pairs(model_dir),
        }
    except Exception as e:
        return {"ok": False, "error": f"Failed to install Argos pack '{fc}->{tc}': {e}"}


def translate_text(
    text: str,
    to_lang: str = "en",
    from_lang: str = "auto",
    model_dir: Path | None = None,
) -> dict[str, Any]:
    """
    Offline neural translation via Argos Translate (with automatic pivot chaining & code-block preservation).
    """
    raw = str(text or "").strip()
    if not raw:
        return {"ok": True, "translated": "", "from_lang": from_lang, "to_lang": to_lang, "engine": "noop"}

    src = detect_language(raw) if (not from_lang or from_lang == "auto") else str(from_lang).strip().lower()[:2]
    dst = (to_lang or "en").strip().lower()[:2]
    if src == dst:
        return {"ok": True, "translated": raw, "from_lang": src, "to_lang": dst, "engine": "identity"}

    configure_portable_argos_dir(model_dir)
    if importlib.util.find_spec("argostranslate") is None:
        return {
            "ok": False,
            "translated": raw,
            "from_lang": src,
            "to_lang": dst,
            "engine": "unavailable",
            "error": "Offline translator 'argostranslate' is not installed. Click Install on 'Argos Translate' in the API & Library Manager sidebar!",
        }

    try:
        import argostranslate.translate as argos_tr  # type: ignore
        installed_langs = argos_tr.get_installed_languages() or []
        from_obj = next((l for l in installed_langs if l.code == src), None)
        to_obj = next((l for l in installed_langs if l.code == dst), None)
        if not from_obj or not to_obj:
            return {
                "ok": False,
                "translated": raw,
                "from_lang": src,
                "to_lang": dst,
                "engine": "argostranslate",
                "installed_pairs": list_installed_argos_pairs(model_dir),
                "error": f"Offline pack '{src} -> {dst}' is not downloaded yet. Install it in Studio Settings -> Language & Translation!",
            }
        translator = from_obj.get_translation(to_obj)
        if not translator:
            return {
                "ok": False,
                "translated": raw,
                "from_lang": src,
                "to_lang": dst,
                "engine": "argostranslate",
                "installed_pairs": list_installed_argos_pairs(model_dir),
                "error": f"No offline translation route installed from '{src}' to '{dst}'.",
            }
        # Preserve fenced code blocks untranslated
        saved_blocks: list[str] = []
        def _stash(m: re.Match) -> str:
            saved_blocks.append(m.group(0))
            return f"__AVSCODEBLOCK{len(saved_blocks)-1}__"
        masked = re.sub(r"```[\s\S]*?```", _stash, raw)
        translated = translator.translate(masked)
        for idx, blk in enumerate(saved_blocks):
            translated = translated.replace(f"__AVSCODEBLOCK{idx}__", blk)
        return {
            "ok": True,
            "translated": translated,
            "from_lang": src,
            "to_lang": dst,
            "engine": "argostranslate",
        }
    except Exception as e:
        return {"ok": False, "translated": raw, "from_lang": src, "to_lang": dst, "engine": "argostranslate", "error": str(e)}


def load_locale_pack(locales_dir: Path, lang_code: str = "en") -> dict[str, Any]:
    """Loads locales/en.json as base and merges locales/<lang>.json so missing keys never break UI."""
    base: dict[str, Any] = {}
    en_p = locales_dir / "en.json"
    if en_p.exists():
        try:
            base = json.loads(en_p.read_text(encoding="utf-8"))
        except Exception:
            base = {}
    code = re.sub(r"[^a-zA-Z_-]", "", str(lang_code or "en")).lower()[:5] or "en"
    if code != "en":
        lang_p = locales_dir / f"{code}.json"
        if lang_p.exists():
            try:
                override = json.loads(lang_p.read_text(encoding="utf-8"))
                if isinstance(override, dict):
                    for k, v in override.items():
                        if isinstance(v, dict) and isinstance(base.get(k), dict):
                            base[k] = {**base[k], **v}
                        else:
                            base[k] = v
            except Exception:
                pass
    return base


def get_language_capabilities(model_dir: Path | None = None, locales_dir: Path | None = None) -> dict[str, Any]:
    avail_locales = ["en"]
    if locales_dir and locales_dir.exists():
        avail_locales = sorted({p.stem for p in locales_dir.glob("*.json")}) or ["en"]
    return {
        "pyspellchecker_installed": importlib.util.find_spec("spellchecker") is not None,
        "argostranslate_installed": importlib.util.find_spec("argostranslate") is not None,
        "langid_installed": importlib.util.find_spec("langid") is not None,
        "installed_argos_pairs": list_installed_argos_pairs(model_dir),
        "supported_ui_locales": SUPPORTED_UI_LOCALES,
        "available_locale_files": avail_locales,
        "speech_locales": [{"code": c, "label": lbl} for c, lbl in SPEECH_LOCALE_OPTIONS],
        "spellcheck_languages": sorted(SPELLCHECK_LANGS),
    }
