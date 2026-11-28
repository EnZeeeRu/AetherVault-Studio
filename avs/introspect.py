"""
avs/introspect.py — Live Python/API Self-Discovery & Diagnostic Error Hinting (v7.1 Lamppost).
"""
from __future__ import annotations

import difflib
import importlib
import importlib.metadata
import inspect
import json
import re
from typing import Any, Dict, List, Optional

import requests


def inspect_target(target: Any, max_members: int = 24) -> str:
    obj = target
    label = ""
    if isinstance(target, str):
        name = target.strip()
        label = name
        if not name:
            return "Pass a package/module name (e.g. 'json', 'PIL.Image', 'requests') or an object (e.g. vault.fs)."
        try:
            parts = name.split(".")
            mod = importlib.import_module(parts[0])
            obj = mod
            for attr in parts[1:]:
                if hasattr(obj, attr):
                    obj = getattr(obj, attr)
                else:
                    obj = importlib.import_module(".".join(parts[: parts.index(attr) + 1]))
        except Exception as e:
            return f"Could not import/locate '{name}': {type(e).__name__}: {e}"
    else:
        label = getattr(target, "__qualname__", None) or getattr(target, "__name__", None) or type(target).__name__

    lines: List[str] = [f"=== INSPECT: {label} ==="]
    top_pkg = label.split(".")[0] if isinstance(target, str) else (getattr(obj, "__module__", "") or "").split(".")[0]
    if top_pkg:
        try:
            ver = importlib.metadata.version(top_pkg)
            lines.append(f"Version: {ver}")
        except Exception:
            pass

    if callable(obj):
        try:
            sig = str(inspect.signature(obj))
            lines.append(f"Signature: {label}{sig}")
        except Exception:
            pass
        doc = inspect.getdoc(obj) or ""
        if doc:
            lines.append("Doc: " + doc[:500])
        return "\n".join(lines)

    doc = inspect.getdoc(obj) or ""
    if doc:
        lines.append("Summary: " + doc.splitlines()[0][:200])

    members: List[str] = []
    for m_name in sorted(dir(obj)):
        if m_name.startswith("_"):
            continue
        try:
            val = getattr(obj, m_name)
        except Exception:
            continue
        if callable(val):
            try:
                sig = str(inspect.signature(val))
            except Exception:
                sig = "(...)"
            short_d = (inspect.getdoc(val) or "").splitlines()[0][:70] if inspect.getdoc(val) else ""
            members.append(f"  - {m_name}{sig}" + (f"  # {short_d}" if short_d else ""))
        if len(members) >= max_members:
            break

    if members:
        lines.append(f"Callables (showing up to {max_members}):")
        lines.extend(members)
    else:
        attrs = [a for a in sorted(dir(obj)) if not a.startswith("_")][:max_members]
        lines.append("Attributes: " + ", ".join(attrs))
    return "\n".join(lines)


def api_probe(base_url: str, headers: Optional[Dict[str, str]] = None, offline_mode: bool = False) -> str:
    if offline_mode:
        return "Offline Mode is ON — cannot probe remote URLs."
    u = (base_url or "").strip().rstrip("/")
    if not u:
        return "Provide a URL (e.g. 'http://127.0.0.1:8000' or 'https://api.example.com')."
    if not re.match(r"^https?://", u, flags=re.IGNORECASE):
        u = "https://" + u

    hdrs = {"User-Agent": "AetherVaultStudio/7.1 (API Probe)"}
    if isinstance(headers, dict):
        hdrs.update({str(k): str(v) for k, v in headers.items()})

    for spec_path in ("/openapi.json", "/swagger.json", "/v1/openapi.json", ""):
        try:
            target = u if (spec_path == "" or u.endswith(".json")) else (u + spec_path)
            r = requests.get(target, headers=hdrs, timeout=8)
            if r.status_code == 200 and "json" in (r.headers.get("Content-Type") or "").lower():
                data = r.json()
                if isinstance(data, dict) and isinstance(data.get("paths"), dict):
                    info = data.get("info") or {}
                    paths = data["paths"]
                    lines = [f"=== OPENAPI SPEC: {info.get('title', target)} v{info.get('version', '?')} ({len(paths)} paths) ==="]
                    for p_key in sorted(paths.keys())[:30]:
                        methods = [m.upper() for m in paths[p_key].keys() if m.lower() in ("get", "post", "put", "patch", "delete")]
                        lines.append(f"  {','.join(methods):10s} {p_key}")
                    return "\n".join(lines)
                if spec_path == "":
                    keys = list(data.keys())[:15] if isinstance(data, dict) else f"list[{len(data)}]"
                    return f"=== JSON ENDPOINT ({target} | HTTP 200) ===\nTop keys/shape: {keys}\nSample: {json.dumps(data, ensure_ascii=False)[:600]}"
        except Exception:
            continue

    try:
        r = requests.get(u, headers=hdrs, timeout=8)
        return f"HTTP {r.status_code} ({r.headers.get('Content-Type', 'unknown')}) from {u} | Preview: {(r.text or '')[:350]}"
    except Exception as e:
        return f"API probe failed for '{u}': {type(e).__name__}: {e}"


def build_error_hint(exc: Exception, namespace: Optional[Dict[str, Any]] = None) -> str:
    etype = type(exc).__name__
    emsg = str(exc)
    ns = namespace or {}

    if etype == "AttributeError":
        m = re.search(r"'([^']+)' object has no attribute '([^']+)'", emsg)
        if m:
            obj_type, bad_attr = m.group(1), m.group(2)
            candidates = list(ns.items())
            for k, v in list(ns.items()):
                if k == "vault":
                    for sub_k in ("fs", "shortcuts", "plugins"):
                        try:
                            candidates.append((f"{k}.{sub_k}", getattr(v, sub_k)))
                        except Exception:
                            pass
            for k, v in candidates:
                if type(v).__name__ == obj_type:
                    pub = [a for a in dir(v) if not a.startswith("_")]
                    close = difflib.get_close_matches(bad_attr, pub, n=5, cutoff=0.4)
                    if close:
                        return f"[HINT] '{k}' ({obj_type}) has no '{bad_attr}'. Closest valid attributes: {', '.join(close)}."
                    return f"[HINT] Call vault.inspect({k}) to see valid attributes on {obj_type}."

    if etype == "TypeError":
        m = re.search(r"([a-zA-Z0-9_\.]+)\(\) (?:got an unexpected keyword|takes|missing)", emsg)
        if m:
            fn_name = m.group(1).split(".")[-1]
            for obj in list(ns.values()):
                if hasattr(obj, fn_name) and callable(getattr(obj, fn_name)):
                    try:
                        sig = inspect.signature(getattr(obj, fn_name))
                        return f"[HINT] Exact signature: {fn_name}{sig}"
                    except Exception:
                        pass

    if etype == "ModuleNotFoundError":
        m = re.search(r"No module named '([^']+)'", emsg)
        if m:
            pkg = m.group(1).split(".")[0]
            return f"[HINT] Module '{pkg}' is not installed in .venv. You can install it via vault.pip_install('{pkg}') or use Python stdlib."

    return ""
