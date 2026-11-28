"""
avs/cloud_sync.py — Portable Cloud Lore Vault & File Sync Bridge (v7.1 Lamppost).
Supports swapping & syncing lore/knowledge files (.pdf, .md, .txt) into `priority_pdfs/` from anywhere
to complement the Telegram bot, with ZERO extra pip dependencies (stdlib + `requests`):
  1. Nextcloud / OwnCloud / Generic WebDAV (PROPFIND / GET / PUT / MKCOL)
  2. Google Drive API v3 REST (API Key for shared folders or OAuth Bearer token for private pull/push)
  3. 1-Click Direct URL / Google Drive File / Google Doc Pull (auto-exports Docs to .md/.txt!)
  4. Local Cloud-Synced Folder Mirror (Google Drive Desktop, Nextcloud Desktop, Syncthing, Dropbox)
"""
from __future__ import annotations

import os
import re
import shutil
import time
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

ALLOWED_SYNC_EXTS = {".pdf", ".txt", ".md"}
MAX_REMOTE_FILE_BYTES = 35 * 1024 * 1024  # 35 MB per file safety cap


def _sanitize_rel_path(rel_path: str) -> str:
    clean = str(rel_path or "").replace("\\", "/").strip().lstrip("/")
    parts = [p for p in clean.split("/") if p and p not in (".", "..")]
    return "/".join(parts)


def _safe_target_in_root(root_dir: Path, rel_path: str) -> Optional[Path]:
    norm = _sanitize_rel_path(rel_path)
    if not norm:
        return None
    root_res = root_dir.resolve()
    target = (root_res / norm).resolve()
    if root_res not in target.parents:
        return None
    return target


def _safe_filename(name: str, default_ext: str = ".md") -> str:
    base = Path(str(name or "").strip()).name
    base = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", base).strip(" .")
    if not base:
        base = f"cloud_doc_{int(time.time())}{default_ext}"
    if Path(base).suffix.lower() not in ALLOWED_SYNC_EXTS:
        base = base + default_ext
    return base[:120]


# =====================================================================
# 1. DIRECT URL / GOOGLE DRIVE FILE / GOOGLE DOCS 1-CLICK PULL
# =====================================================================
def parse_gdrive_or_doc_url(url: str) -> Tuple[str, str]:
    """
    Detects Google Docs / Google Drive file URLs and returns (kind, file_id):
      - ('gdoc', id)   for docs.google.com/document/d/<id>
      - ('gdrive', id) for drive.google.com/file/d/<id> or ?id=<id>
      - ('raw', url)   for any direct HTTP/HTTPS file URL
    """
    u = (url or "").strip()
    m_doc = re.search(r"docs\.google\.com/document/d/([a-zA-Z0-9_-]{12,})", u)
    if m_doc:
        return "gdoc", m_doc.group(1)
    m_drv = re.search(r"drive\.google\.com/(?:file/d/|open\?id=|uc\?(?:[^#]*&)?id=)([a-zA-Z0-9_-]{12,})", u)
    if m_drv:
        return "gdrive", m_drv.group(1)
    return "raw", u


def pull_url_to_knowledge_tree(
    url: str,
    pdf_dir: Path,
    subfolder: str = "cloud",
    filename_hint: str = "",
    offline_mode: bool = False,
) -> Dict[str, Any]:
    """Downloads a Google Doc (as Markdown/Text), Google Drive file, or direct URL into priority_pdfs/."""
    if offline_mode:
        return {"ok": False, "error": "Offline Mode is ON."}
    raw_u = (url or "").strip()
    if not raw_u or not re.match(r"^https?://", raw_u, flags=re.IGNORECASE):
        return {"ok": False, "error": "Provide a valid http:// or https:// Google Drive, Google Docs, or raw file URL."}

    kind, ident = parse_gdrive_or_doc_url(raw_u)
    headers = {"User-Agent": "AetherVaultStudio/7.1 (Cloud Lore Sync)"}
    dl_url = raw_u
    default_ext = ".md"

    if kind == "gdoc":
        dl_url = f"https://docs.google.com/document/d/{ident}/export?format=txt"
        default_ext = ".txt"
    elif kind == "gdrive":
        dl_url = f"https://drive.google.com/uc?export=download&id={ident}"
        default_ext = ".pdf"

    try:
        r = requests.get(dl_url, headers=headers, timeout=25, allow_redirects=True)
        r.raise_for_status()
        content = r.content
        if len(content) > MAX_REMOTE_FILE_BYTES:
            return {"ok": False, "error": f"Remote file exceeds 35 MB safety limit ({len(content):,} bytes)."}
        if not content:
            return {"ok": False, "error": "Downloaded 0 bytes from URL."}

        # Detect filename from Content-Disposition or URL path
        cd = r.headers.get("Content-Disposition") or ""
        m_cd = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";\r\n]+)"?', cd, flags=re.IGNORECASE)
        ctype = (r.headers.get("Content-Type") or "").lower()
        if filename_hint:
            fname = _safe_filename(filename_hint, default_ext=default_ext)
        elif m_cd:
            fname = _safe_filename(urllib.parse.unquote(m_cd.group(1)), default_ext=default_ext)
        else:
            url_tail = Path(urllib.parse.urlparse(raw_u).path).name
            if url_tail and Path(url_tail).suffix.lower() in ALLOWED_SYNC_EXTS:
                fname = _safe_filename(url_tail, default_ext=default_ext)
            else:
                ext_pick = ".pdf" if "pdf" in ctype else (".txt" if "text/plain" in ctype else default_ext)
                fname = _safe_filename(f"{kind}_{ident[:10]}{ext_pick}", default_ext=ext_pick)

        # Guard against Google login HTML wall when a Drive link isn't shared publicly
        if ("text/html" in ctype) and fname.endswith(".pdf") and not content.startswith(b"%PDF-"):
            return {
                "ok": False,
                "error": "Google Drive returned an HTML sign-in/preview page instead of the file. Make sure the file is shared ('Anyone with the link') or use Google Drive API v3 with a Bearer token."
            }

        sub_clean = _sanitize_rel_path(subfolder)
        rel_dest = f"{sub_clean}/{fname}" if sub_clean else fname
        dest = _safe_target_in_root(pdf_dir, rel_dest)
        if not dest:
            return {"ok": False, "error": "Invalid destination subfolder/filename."}
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(content)
        return {
            "ok": True,
            "kind": kind,
            "rel_path": dest.relative_to(pdf_dir.resolve()).as_posix(),
            "bytes": len(content),
            "message": f"Pulled '{dest.name}' ({len(content):,} bytes) into /priority_pdfs/{dest.relative_to(pdf_dir.resolve()).as_posix()}!"
        }
    except Exception as e:
        return {"ok": False, "error": f"URL pull failed: {e}"}


# =====================================================================
# 2. NEXTCLOUD / OWNCLOUD / GENERIC WEBDAV SYNC (ZERO EXTRA DEPS)
# =====================================================================
def _webdav_propfind_files(base_url: str, auth: Optional[Tuple[str, str]], timeout: int = 18) -> Tuple[bool, Any]:
    url = base_url.rstrip("/") + "/"
    prop_body = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<d:propfind xmlns:d="DAV:"><d:prop>'
        '<d:resourcetype/><d:getcontentlength/><d:getlastmodified/>'
        '</d:prop></d:propfind>'
    )
    try:
        r = requests.request(
            "PROPFIND",
            url,
            data=prop_body.encode("utf-8"),
            headers={"Depth": "1", "Content-Type": "application/xml", "User-Agent": "AetherVaultStudio/7.1"},
            auth=auth,
            timeout=timeout,
        )
        if r.status_code not in (200, 207):
            return False, f"WebDAV PROPFIND failed (HTTP {r.status_code}): {(r.text or '')[:180]}"
        root = ET.fromstring(r.content)
        parsed_base = urllib.parse.urlparse(url)
        base_path = urllib.parse.unquote(parsed_base.path).rstrip("/")
        files: List[Dict[str, Any]] = []
        for resp in root.findall(".//{DAV:}response"):
            href_el = resp.find("{DAV:}href")
            if href_el is None or not href_el.text:
                continue
            href_raw = href_el.text.strip()
            href_path = urllib.parse.unquote(urllib.parse.urlparse(href_raw).path).rstrip("/")
            if href_path == base_path:
                continue
            is_col = resp.find(".//{DAV:}collection") is not None
            if is_col:
                continue
            name = Path(href_path).name
            if Path(name).suffix.lower() not in ALLOWED_SYNC_EXTS:
                continue
            size_el = resp.find(".//{DAV:}getcontentlength")
            size_b = int(size_el.text) if (size_el is not None and (size_el.text or "").isdigit()) else 0
            full_dl = urllib.parse.urljoin(f"{parsed_base.scheme}://{parsed_base.netloc}", href_raw)
            files.append({"name": name, "url": full_dl, "size": size_b})
        return True, files
    except Exception as e:
        return False, f"WebDAV error: {e}"


def sync_webdav_vault(
    webdav_url: str,
    username: str,
    password: str,
    pdf_dir: Path,
    subfolder: str = "cloud",
    direction: str = "pull",
) -> Dict[str, Any]:
    """Pulls, pushes, or two-way syncs .pdf/.md/.txt files with Nextcloud / OwnCloud / WebDAV."""
    u = (webdav_url or "").strip().rstrip("/")
    if not u or not re.match(r"^https?://", u, flags=re.IGNORECASE):
        return {"ok": False, "error": "Enter a valid WebDAV folder URL (e.g. https://cloud.example.com/remote.php/dav/files/user/AVS_Lore)."}
    auth = (username.strip(), password.strip()) if username.strip() else None
    ok_list, remote_or_err = _webdav_propfind_files(u, auth)
    if not ok_list:
        return {"ok": False, "error": str(remote_or_err)}

    remote_files: List[Dict[str, Any]] = remote_or_err
    sub_clean = _sanitize_rel_path(subfolder)
    local_root = (pdf_dir / sub_clean).resolve() if sub_clean else pdf_dir.resolve()
    local_root.mkdir(parents=True, exist_ok=True)

    pulled: List[str] = []
    pushed: List[str] = []
    errors: List[str] = []

    if direction in ("pull", "both"):
        for rf in remote_files:
            if rf.get("size", 0) > MAX_REMOTE_FILE_BYTES:
                errors.append(f"Skipped {rf['name']} (>35 MB)")
                continue
            fname = _safe_filename(rf["name"])
            dest = _safe_target_in_root(local_root, fname)
            if not dest:
                continue
            try:
                r_get = requests.get(rf["url"], auth=auth, headers={"User-Agent": "AetherVaultStudio/7.1"}, timeout=25)
                r_get.raise_for_status()
                dest.write_bytes(r_get.content)
                pulled.append(dest.relative_to(pdf_dir.resolve()).as_posix())
            except Exception as e:
                errors.append(f"Pull {fname}: {e}")

    if direction in ("push", "both"):
        for lf in sorted(local_root.iterdir()):
            if not lf.is_file() or lf.suffix.lower() not in ALLOWED_SYNC_EXTS:
                continue
            if lf.stat().st_size > MAX_REMOTE_FILE_BYTES:
                continue
            put_url = f"{u}/{urllib.parse.quote(lf.name)}"
            try:
                r_put = requests.put(
                    put_url,
                    data=lf.read_bytes(),
                    auth=auth,
                    headers={"User-Agent": "AetherVaultStudio/7.1"},
                    timeout=25,
                )
                if r_put.status_code in (200, 201, 204):
                    pushed.append(lf.relative_to(pdf_dir.resolve()).as_posix())
                else:
                    errors.append(f"Push {lf.name}: HTTP {r_put.status_code}")
            except Exception as e:
                errors.append(f"Push {lf.name}: {e}")

    return {
        "ok": len(errors) == 0 or bool(pulled or pushed),
        "provider": "webdav",
        "direction": direction,
        "remote_count": len(remote_files),
        "pulled": pulled,
        "pushed": pushed,
        "errors": errors,
        "message": f"WebDAV {direction}: pulled {len(pulled)}, pushed {len(pushed)} file(s)" + (f" ({len(errors)} warning(s))" if errors else "."),
    }


# =====================================================================
# 3. GOOGLE DRIVE API v3 REST SYNC (API KEY OR OAUTH BEARER TOKEN)
# =====================================================================
def sync_gdrive_api_folder(
    folder_id: str,
    api_key: str,
    bearer_token: str,
    pdf_dir: Path,
    subfolder: str = "cloud",
    direction: str = "pull",
) -> Dict[str, Any]:
    """Syncs a Google Drive folder using pure REST v3 (API key for public/shared folders, Bearer token for private pull/push)."""
    fid = (folder_id or "").strip()
    m_f = re.search(r"folders/([a-zA-Z0-9_-]{10,})", fid)
    if m_f:
        fid = m_f.group(1)
    if not fid:
        return {"ok": False, "error": "Provide a Google Drive Folder ID (or paste the folder URL)."}
    ak = (api_key or "").strip()
    bt = (bearer_token or "").strip()
    if not ak and not bt:
        return {"ok": False, "error": "Provide either a Google API Key (for shared folders) or an OAuth Bearer Token (for private pull/push)."}

    headers = {"User-Agent": "AetherVaultStudio/7.1"}
    if bt:
        headers["Authorization"] = f"Bearer {bt}"
    params = {
        "q": f"'{fid}' in parents and trashed = false",
        "fields": "files(id,name,mimeType,size)",
        "pageSize": 100,
    }
    if ak and not bt:
        params["key"] = ak

    try:
        r = requests.get("https://www.googleapis.com/drive/v3/files", params=params, headers=headers, timeout=18)
        if r.status_code != 200:
            return {"ok": False, "error": f"Google Drive API HTTP {r.status_code}: {(r.text or '')[:220]}"}
        items = (r.json() or {}).get("files") or []
    except Exception as e:
        return {"ok": False, "error": f"Google Drive list failed: {e}"}

    sub_clean = _sanitize_rel_path(subfolder)
    local_root = (pdf_dir / sub_clean).resolve() if sub_clean else pdf_dir.resolve()
    local_root.mkdir(parents=True, exist_ok=True)

    pulled: List[str] = []
    pushed: List[str] = []
    errors: List[str] = []

    if direction in ("pull", "both"):
        for it in items:
            mtype = str(it.get("mimeType") or "")
            raw_name = str(it.get("name") or "")
            item_id = str(it.get("id") or "")
            if not item_id:
                continue
            if mtype == "application/vnd.google-apps.document":
                dl_url = f"https://www.googleapis.com/drive/v3/files/{item_id}/export"
                dl_params = {"mimeType": "text/plain"}
                fname = _safe_filename(raw_name, default_ext=".txt")
            elif Path(raw_name).suffix.lower() in ALLOWED_SYNC_EXTS:
                dl_url = f"https://www.googleapis.com/drive/v3/files/{item_id}"
                dl_params = {"alt": "media"}
                fname = _safe_filename(raw_name)
            else:
                continue
            if ak and not bt:
                dl_params["key"] = ak
            dest = _safe_target_in_root(local_root, fname)
            if not dest:
                continue
            try:
                rd = requests.get(dl_url, params=dl_params, headers=headers, timeout=25)
                rd.raise_for_status()
                if len(rd.content) <= MAX_REMOTE_FILE_BYTES:
                    dest.write_bytes(rd.content)
                    pulled.append(dest.relative_to(pdf_dir.resolve()).as_posix())
            except Exception as e:
                errors.append(f"Pull {fname}: {e}")

    if direction in ("push", "both"):
        if not bt:
            errors.append("Push to Google Drive requires an OAuth Bearer Token (API keys are read-only).")
        else:
            existing_by_name = {str(it.get("name") or "").lower(): str(it.get("id") or "") for it in items}
            for lf in sorted(local_root.iterdir()):
                if not lf.is_file() or lf.suffix.lower() not in ALLOWED_SYNC_EXTS:
                    continue
                if lf.stat().st_size > MAX_REMOTE_FILE_BYTES:
                    continue
                try:
                    ex_id = existing_by_name.get(lf.name.lower())
                    if ex_id:
                        up_url = f"https://www.googleapis.com/upload/drive/v3/files/{ex_id}?uploadType=media"
                        rp = requests.patch(up_url, data=lf.read_bytes(), headers=headers, timeout=25)
                    else:
                        meta = {"name": lf.name, "parents": [fid]}
                        boundary = "===AVS_GDRIVE_BOUNDARY==="
                        mime_f = "application/pdf" if lf.suffix.lower() == ".pdf" else "text/plain"
                        body = (
                            f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n"
                            + requests.compat.json.dumps(meta)
                            + f"\r\n--{boundary}\r\nContent-Type: {mime_f}\r\n\r\n"
                        ).encode("utf-8") + lf.read_bytes() + f"\r\n--{boundary}--\r\n".encode("utf-8")
                        up_hdrs = {**headers, "Content-Type": f"multipart/related; boundary={boundary}"}
                        rp = requests.post("https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart", data=body, headers=up_hdrs, timeout=25)
                    rp.raise_for_status()
                    pushed.append(lf.relative_to(pdf_dir.resolve()).as_posix())
                except Exception as e:
                    errors.append(f"Push {lf.name}: {e}")

    return {
        "ok": len(errors) == 0 or bool(pulled or pushed),
        "provider": "gdrive",
        "direction": direction,
        "remote_count": len(items),
        "pulled": pulled,
        "pushed": pushed,
        "errors": errors,
        "message": f"Google Drive {direction}: pulled {len(pulled)}, pushed {len(pushed)} file(s)" + (f" ({len(errors)} warning(s))" if errors else "."),
    }


# =====================================================================
# 4. LOCAL SYNCED FOLDER MIRROR (Google Drive Desktop / Nextcloud / Syncthing)
# =====================================================================
def sync_local_mirror_folder(
    mirror_path: str,
    pdf_dir: Path,
    subfolder: str = "cloud",
    direction: str = "both",
) -> Dict[str, Any]:
    """Two-way mtime-aware mirror between a local cloud-synced folder and priority_pdfs/<subfolder>."""
    mp = Path(str(mirror_path or "").strip()).expanduser()
    if not mp.exists() or not mp.is_dir():
        return {"ok": False, "error": f"Mirror folder does not exist: '{mirror_path}'"}
    mirror_root = mp.resolve()
    sub_clean = _sanitize_rel_path(subfolder)
    local_root = (pdf_dir / sub_clean).resolve() if sub_clean else pdf_dir.resolve()
    local_root.mkdir(parents=True, exist_ok=True)
    if mirror_root == local_root:
        return {"ok": False, "error": "Mirror folder cannot be the exact same directory as target priority_pdfs folder."}

    pulled: List[str] = []
    pushed: List[str] = []

    if direction in ("pull", "both"):
        for src in sorted(mirror_root.rglob("*")):
            if not src.is_file() or src.suffix.lower() not in ALLOWED_SYNC_EXTS:
                continue
            rel = src.relative_to(mirror_root).as_posix()
            dst = _safe_target_in_root(local_root, rel)
            if not dst:
                continue
            if (not dst.exists()) or (src.stat().st_mtime > dst.stat().st_mtime + 1.0):
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                pulled.append(dst.relative_to(pdf_dir.resolve()).as_posix())

    if direction in ("push", "both"):
        for src in sorted(local_root.rglob("*")):
            if not src.is_file() or src.suffix.lower() not in ALLOWED_SYNC_EXTS:
                continue
            rel = src.relative_to(local_root).as_posix()
            dst = _safe_target_in_root(mirror_root, rel)
            if not dst:
                continue
            if (not dst.exists()) or (src.stat().st_mtime > dst.stat().st_mtime + 1.0):
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                pushed.append(src.relative_to(pdf_dir.resolve()).as_posix())

    return {
        "ok": True,
        "provider": "local_mirror",
        "direction": direction,
        "pulled": pulled,
        "pushed": pushed,
        "errors": [],
        "message": f"Local Cloud Mirror ({direction}): pulled {len(pulled)}, pushed {len(pushed)} file(s).",
    }


def run_configured_cloud_sync(cfg: dict, pdf_dir: Path, direction: str = "pull", offline_mode: bool = False) -> Dict[str, Any]:
    """Unified dispatcher for Nextcloud/WebDAV, Google Drive API v3, or Local Cloud Mirror."""
    c = cfg if isinstance(cfg, dict) else {}
    prov = (c.get("provider") or "webdav").strip().lower()
    sub = _sanitize_rel_path(c.get("subfolder") or "cloud")
    d = (direction or "pull").strip().lower()
    if d not in ("pull", "push", "both"):
        d = "pull"

    if prov == "local_mirror":
        return sync_local_mirror_folder(c.get("local_mirror_path") or "", pdf_dir=pdf_dir, subfolder=sub, direction=d)
    if offline_mode:
        return {"ok": False, "error": "Offline Mode is ON (Local Synced Folder Mirror still works offline!)."}
    if prov == "gdrive":
        return sync_gdrive_api_folder(
            folder_id=c.get("gdrive_folder_id") or "",
            api_key=c.get("gdrive_api_key") or "",
            bearer_token=c.get("gdrive_bearer_token") or "",
            pdf_dir=pdf_dir,
            subfolder=sub,
            direction=d,
        )
    return sync_webdav_vault(
        webdav_url=c.get("webdav_url") or "",
        username=c.get("webdav_username") or "",
        password=c.get("webdav_password") or "",
        pdf_dir=pdf_dir,
        subfolder=sub,
        direction=d,
    )
