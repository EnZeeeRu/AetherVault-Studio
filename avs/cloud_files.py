"""
avs/cloud_files.py — Nextcloud-Style Local Vault Cloud File Server (v7.1 Lamppost).
Provides:
  - Unified Shared Roots (workspace folders + custom mounted PC folders/drives)
  - Directory listing (Grid/List metadata, mime types, media categories, breadcrumbs)
  - Safe path traversal protection + multi-file upload/download/mkdir/rename/delete
  - True HTTP 206 Byte-Range streaming support for iPhone Safari, Android Chrome, VLC & Roku
  - Dynamic .m3u playlist generation for VLC / IPTV / media players
"""
from __future__ import annotations

import mimetypes
import re
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".svg", ".avif"}
VIDEO_EXTS = {".mp4", ".mkv", ".webm", ".mov", ".m4v", ".avi", ".ts"}
AUDIO_EXTS = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac", ".opus"}
DOC_EXTS = {".pdf", ".txt", ".md", ".json", ".csv", ".py", ".js", ".ts", ".html", ".css", ".yml", ".yaml", ".xml", ".log", ".ini"}
LORE_EXTS = {".pdf", ".txt", ".md"}


def classify_ext(ext: str) -> str:
    e = (ext or "").lower()
    if e in IMAGE_EXTS:
        return "image"
    if e in VIDEO_EXTS:
        return "video"
    if e in AUDIO_EXTS:
        return "audio"
    if e in DOC_EXTS:
        return "doc"
    return "other"


def guess_mime(path: Path) -> str:
    ext = path.suffix.lower()
    explicit = {
        ".mkv": "video/x-matroska",
        ".mp4": "video/mp4",
        ".m4v": "video/mp4",
        ".mov": "video/quicktime",
        ".webm": "video/webm",
        ".avi": "video/x-msvideo",
        ".mp3": "audio/mpeg",
        ".flac": "audio/flac",
        ".wav": "audio/wav",
        ".ogg": "audio/ogg",
        ".m4a": "audio/mp4",
        ".webp": "image/webp",
        ".svg": "image/svg+xml",
        ".md": "text/markdown; charset=utf-8",
        ".srt": "text/plain; charset=utf-8",
        ".vtt": "text/vtt; charset=utf-8",
    }
    if ext in explicit:
        return explicit[ext]
    mt, _ = mimetypes.guess_type(str(path))
    return mt or "application/octet-stream"


def sanitize_rel(rel_path: str) -> str:
    clean = str(rel_path or "").replace("\\", "/").strip().strip("/")
    parts = [p for p in clean.split("/") if p and p not in (".", "..")]
    return "/".join(parts)


def get_cloud_roots(base_dir: Path, cfg: dict) -> List[Dict[str, Any]]:
    vault_files = base_dir / "vault_files"
    vault_files.mkdir(parents=True, exist_ok=True)
    roots: List[Dict[str, Any]] = [
        {"id": "vault_files", "label": "Vault Files", "icon": "☁️", "path": str(vault_files.resolve()), "builtin": True, "cloud": True, "dlna": True},
        {"id": "priority_pdfs", "label": "Knowledge & Lore", "icon": "📚", "path": str((base_dir / "priority_pdfs").resolve()), "builtin": True, "cloud": True, "dlna": False},
        {"id": "generated_images", "label": "Generated Images", "icon": "🖼️", "path": str((base_dir / "generated_images").resolve()), "builtin": True, "cloud": True, "dlna": True},
        {"id": "generated_audio", "label": "Generated Audio", "icon": "🎵", "path": str((base_dir / "generated_audio").resolve()), "builtin": True, "cloud": True, "dlna": True},
        {"id": "chat_media", "label": "Chat Media", "icon": "📎", "path": str((base_dir / "custom_assets" / "chat_media").resolve()), "builtin": True, "cloud": True, "dlna": True},
        {"id": "chat_logs", "label": "Chat Exports", "icon": "📄", "path": str((base_dir / "chat_logs").resolve()), "builtin": True, "cloud": True, "dlna": False},
    ]
    custom_roots = ((cfg or {}).get("vault_cloud") or {}).get("custom_roots") or []
    seen_ids = {r["id"] for r in roots}
    for idx, cr in enumerate(custom_roots):
        if not isinstance(cr, dict):
            continue
        raw_p = str(cr.get("path") or "").strip()
        if not raw_p:
            continue
        p = Path(raw_p).expanduser()
        rid = re.sub(r"[^a-zA-Z0-9_-]", "_", str(cr.get("id") or f"custom_{idx}")).strip("_") or f"custom_{idx}"
        if rid in seen_ids:
            rid = f"{rid}_{idx}"
        seen_ids.add(rid)
        roots.append({
            "id": rid,
            "label": str(cr.get("label") or p.name or raw_p)[:48],
            "icon": str(cr.get("icon") or "💾"),
            "path": str(p.resolve()) if p.exists() else raw_p,
            "exists": p.exists() and p.is_dir(),
            "builtin": False,
            "cloud": bool(cr.get("cloud", True)),
            "dlna": bool(cr.get("dlna", True)),
        })
    for r in roots:
        if "exists" not in r:
            p_obj = Path(r["path"])
            p_obj.mkdir(parents=True, exist_ok=True)
            r["exists"] = True
    return roots


def resolve_root_path(base_dir: Path, cfg: dict, root_id: str, rel_path: str = "") -> Tuple[Optional[Dict[str, Any]], Optional[Path], str]:
    roots = get_cloud_roots(base_dir, cfg)
    root = next((r for r in roots if r["id"] == root_id), None)
    if not root:
        return None, None, f"Unknown root '{root_id}'."
    root_dir = Path(root["path"]).resolve()
    if not root_dir.exists() or not root_dir.is_dir():
        return root, None, f"Root folder does not exist on disk: '{root_dir}'."
    norm = sanitize_rel(rel_path)
    if not norm:
        return root, root_dir, ""
    target = (root_dir / norm).resolve()
    if target != root_dir and root_dir not in target.parents:
        return root, None, "Path escapes root boundary."
    return root, target, ""


def list_directory(base_dir: Path, cfg: dict, root_id: str, rel_path: str = "", search: str = "") -> Dict[str, Any]:
    root, target, err = resolve_root_path(base_dir, cfg, root_id, rel_path)
    if err or not target:
        return {"ok": False, "error": err or "Invalid path"}
    if not target.exists() or not target.is_dir():
        return {"ok": False, "error": f"Folder not found: '{rel_path}'"}

    root_dir = Path(root["path"]).resolve()
    q_low = (search or "").strip().lower()
    entries: List[Dict[str, Any]] = []
    try:
        items = list(target.rglob("*") if q_low else target.iterdir())
    except Exception as e:
        return {"ok": False, "error": str(e)}

    for p in items[:600]:
        try:
            name = p.name
            if name.startswith(".") and name not in (".gitattributes",):
                continue
            if q_low and q_low not in name.lower():
                continue
            st = p.stat()
            is_dir = p.is_dir()
            rel = p.relative_to(root_dir).as_posix()
            ext = "" if is_dir else p.suffix.lower()
            kind = "folder" if is_dir else classify_ext(ext)
            stream_url = "" if is_dir else f"/cloud/stream/{urllib.parse.quote(root_id)}/{urllib.parse.quote(rel)}"
            entries.append({
                "name": name,
                "rel_path": rel,
                "is_dir": is_dir,
                "size": 0 if is_dir else int(st.st_size),
                "mtime": int(st.st_mtime),
                "ext": ext,
                "kind": kind,
                "mime": "inode/directory" if is_dir else guess_mime(p),
                "stream_url": stream_url,
                "can_lore": (not is_dir) and (ext in LORE_EXTS),
            })
        except Exception:
            continue

    entries.sort(key=lambda x: (0 if x["is_dir"] else 1, x["name"].lower()))
    norm_rel = sanitize_rel(rel_path)
    crumbs = [{"label": root["label"], "rel_path": ""}]
    if norm_rel:
        acc = []
        for part in norm_rel.split("/"):
            acc.append(part)
            crumbs.append({"label": part, "rel_path": "/".join(acc)})

    return {
        "ok": True,
        "root": root,
        "rel_path": norm_rel,
        "breadcrumbs": crumbs,
        "entries": entries[:400],
        "total": len(entries),
    }


def parse_byte_range(range_header: str, file_size: int) -> Optional[Tuple[int, int]]:
    if not range_header or file_size <= 0:
        return None
    m = re.match(r"bytes=(\d*)-(\d*)", range_header.strip(), flags=re.IGNORECASE)
    if not m:
        return None
    s_raw, e_raw = m.group(1), m.group(2)
    if not s_raw and not e_raw:
        return None
    if s_raw:
        start = int(s_raw)
        end = int(e_raw) if e_raw else (file_size - 1)
    else:
        suffix = int(e_raw)
        start = max(0, file_size - suffix)
        end = file_size - 1
    if start >= file_size or start > end:
        return None
    return start, min(end, file_size - 1)


def iter_file_range(path: Path, start: int, end: int, chunk_size: int = 256 * 1024):
    remaining = (end - start) + 1
    with open(path, "rb") as f:
        f.seek(start)
        while remaining > 0:
            data = f.read(min(chunk_size, remaining))
            if not data:
                break
            remaining -= len(data)
            yield data


def build_m3u_playlist(base_dir: Path, cfg: dict, server_base_url: str, root_id: str = "") -> str:
    roots = get_cloud_roots(base_dir, cfg)
    base_u = server_base_url.rstrip("/")
    lines = ["#EXTM3U"]
    for r in roots:
        if root_id and r["id"] != root_id:
            continue
        if not root_id and not r.get("dlna", True):
            continue
        rdir = Path(r["path"])
        if not rdir.exists():
            continue
        count = 0
        for p in sorted(rdir.rglob("*")):
            if count >= 500:
                break
            if not p.is_file():
                continue
            kind = classify_ext(p.suffix.lower())
            if kind not in ("video", "audio"):
                continue
            rel = p.relative_to(rdir).as_posix()
            url = f"{base_u}/cloud/stream/{urllib.parse.quote(r['id'])}/{urllib.parse.quote(rel)}"
            lines.append(f"#EXTINF:-1,{r['label']} - {p.stem}")
            lines.append(url)
            count += 1
    return "\n".join(lines) + "\n"
