"""
avs/fs_ops.py — Robust Filesystem, Cross-Drive App Relocation & Shortcut Engine (v7.1 Lamppost).
- Multi-threaded native OS transfers (`robocopy /E /MT:8` on Windows, `rsync -a` on Unix, safe shutil fallback)
- Pre-flight free disk space & running-process lock checks via psutil
- Safe Trash/Recycle Bin move (never hard-deletes by default)
- Smart Program Relocation with NTFS Directory Junctions (`mklink /J`) or Unix symlinks
- Native Windows `.lnk` Desktop/Start-Menu shortcut inspection, creation & batch path rewriting via WScript.Shell COM
- Background job tracker for multi-GB folder transfers
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import psutil
except ImportError:
    psutil = None

IS_WINDOWS = (os.name == "nt")
PROTECTED_ROOT_NAMES = {"windows", "system32", "syswow64", "programdata", "boot", "recovery"}
FS_JOBS: Dict[str, Dict[str, Any]] = {}


def _resolve_path(raw_path: str) -> Path:
    s = str(raw_path or "").strip().strip("'\"")
    norm = s.replace("\\", "/")
    low = norm.lower()
    if low == "desktop":
        return (Path.home() / "Desktop").resolve()
    if low.startswith("desktop/"):
        return (Path.home() / "Desktop" / norm[8:]).resolve()
    if low.startswith("documents/"):
        return (Path.home() / "Documents" / norm[10:]).resolve()
    if low.startswith("downloads/"):
        return (Path.home() / "Downloads" / norm[10:]).resolve()
    return Path(s).expanduser().resolve()


def _is_protected_target(p: Path, base_dir: Path, protected_core: set) -> Optional[str]:
    if p == p.anchor or str(p) == p.anchor:
        return f"Refusing destructive operation on drive root '{p}'."
    if p == Path.home().resolve() or p == base_dir.resolve():
        return f"Refusing destructive operation on protected root '{p}'."
    if p.parent == base_dir.resolve() and p.name in protected_core:
        return f"Protected AetherVault core file '{p.name}' cannot be modified directly."
    parts_low = [part.lower() for part in p.parts]
    if len(parts_low) <= 2 and any(x in PROTECTED_ROOT_NAMES for x in parts_low):
        return f"Refusing operation on critical OS directory '{p}'."
    return None


def _dir_size_and_count(p: Path) -> tuple[int, int]:
    if p.is_file():
        return p.stat().st_size, 1
    total_b = 0
    cnt = 0
    for f in p.rglob("*"):
        if f.is_file():
            try:
                total_b += f.stat().st_size
                cnt += 1
            except Exception:
                pass
    return total_b, cnt


def _find_running_exes_in_folder(folder: Path) -> List[str]:
    if psutil is None:
        return []
    hits: List[str] = []
    f_str = str(folder.resolve()).lower()
    for proc in psutil.process_iter(["pid", "name", "exe"]):
        try:
            exe = str(proc.info.get("exe") or "").lower()
            if exe and exe.startswith(f_str):
                hits.append(f"{proc.info.get('name')} (PID {proc.info.get('pid')})")
        except Exception:
            continue
    return hits


def _run_ps(script: str, timeout: float = 20.0) -> Dict[str, Any]:
    if not IS_WINDOWS:
        return {"ok": False, "output": "PowerShell WScript.Shell shortcuts are Windows-only."}
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    proc = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", script],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        startupinfo=si,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000),
        timeout=timeout,
    )
    return {"ok": proc.returncode == 0, "exit_code": proc.returncode, "output": (proc.stdout or "").strip()}


def tree(path: str, depth: int = 2, max_entries: int = 80) -> str:
    root = _resolve_path(path)
    if not root.exists():
        return f"Path not found: '{root}'"
    if root.is_file():
        return f"[FILE] {root} ({root.stat().st_size:,} bytes)"
    lines = [f"📁 {root}"]
    count = 0

    def _walk(cur: Path, level: int, prefix: str):
        nonlocal count
        if level > depth or count >= max_entries:
            return
        try:
            children = sorted(cur.iterdir(), key=lambda x: (0 if x.is_dir() else 1, x.name.lower()))
        except Exception:
            return
        for ch in children:
            if count >= max_entries:
                lines.append(f"{prefix}... (truncated at {max_entries} entries)")
                return
            count += 1
            tag = "📂" if ch.is_dir() else "📄"
            sz = "" if ch.is_dir() else f" ({ch.stat().st_size:,} B)"
            lines.append(f"{prefix}{tag} {ch.name}{sz}")
            if ch.is_dir() and level < depth:
                _walk(ch, level + 1, prefix + "  ")

    _walk(root, 1, "  ")
    return "\n".join(lines)


def _native_copy_tree(src: Path, dst: Path) -> Dict[str, Any]:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_file():
        if dst.is_dir():
            dst = dst / src.name
        shutil.copy2(src, dst)
        return {"ok": True, "engine": "shutil.copy2", "dest": str(dst)}

    if IS_WINDOWS and shutil.which("robocopy"):
        dst.mkdir(parents=True, exist_ok=True)
        proc = subprocess.run(
            ["robocopy", str(src), str(dst), "/E", "/MT:8", "/R:2", "/W:2", "/NFL", "/NDL", "/NJH", "/NJS"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
        )
        if proc.returncode <= 7:
            return {"ok": True, "engine": "robocopy /MT:8", "exit_code": proc.returncode, "dest": str(dst)}
        return {"ok": False, "engine": "robocopy", "exit_code": proc.returncode, "error": (proc.stdout or "")[-400:]}

    if not IS_WINDOWS and shutil.which("rsync"):
        dst.mkdir(parents=True, exist_ok=True)
        proc = subprocess.run(["rsync", "-a", str(src).rstrip("/") + "/", str(dst).rstrip("/") + "/"], capture_output=True, text=True)
        if proc.returncode == 0:
            return {"ok": True, "engine": "rsync -a", "dest": str(dst)}

    shutil.copytree(src, dst, dirs_exist_ok=True)
    return {"ok": True, "engine": "shutil.copytree", "dest": str(dst)}


def copy_path(src: str, dst: str, base_dir: Path, protected_core: set, trust: str = "safe_auto") -> Dict[str, Any]:
    s = _resolve_path(src)
    d = _resolve_path(dst)
    if not s.exists():
        return {"ok": False, "error": f"Source not found: '{s}'"}
    prot = _is_protected_target(d, base_dir, protected_core)
    if prot:
        return {"ok": False, "error": prot}
    size_b, cnt = _dir_size_and_count(s)
    check_drive = d if d.exists() else d.parent
    try:
        free_b = shutil.disk_usage(check_drive if check_drive.exists() else check_drive.anchor).free
        if free_b < int(size_b * 1.05):
            return {"ok": False, "error": f"Not enough free space on destination ({free_b / (1024**3):.2f} GB free, need {size_b / (1024**3):.2f} GB)."}
    except Exception:
        pass
    res = _native_copy_tree(s, d)
    res.update({"files": cnt, "bytes": size_b})
    return res


def move_path(src: str, dst: str, base_dir: Path, protected_core: set, trust: str = "safe_auto") -> Dict[str, Any]:
    s = _resolve_path(src)
    d = _resolve_path(dst)
    if not s.exists():
        return {"ok": False, "error": f"Source not found: '{s}'"}
    for chk in (s, d):
        prot = _is_protected_target(chk, base_dir, protected_core)
        if prot:
            return {"ok": False, "error": prot}
    if s.is_dir():
        running = _find_running_exes_in_folder(s)
        if running:
            return {"ok": False, "error": f"Cannot move '{s}': running process(es) locked inside folder: {', '.join(running[:5])}. Close them first!"}

    if s.anchor.lower() == d.anchor.lower():
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(s), str(d))
        return {"ok": True, "engine": "atomic_move", "src": str(s), "dest": str(d)}

    cp = copy_path(str(s), str(d), base_dir, protected_core, trust)
    if not cp.get("ok"):
        return cp
    dst_bytes, dst_cnt = _dir_size_and_count(d)
    if dst_cnt < cp.get("files", 0):
        return {"ok": False, "error": f"Verification failed after copy ({dst_cnt} < {cp.get('files')} files); original kept intact at '{s}'."}
    if s.is_dir():
        shutil.rmtree(s)
    else:
        s.unlink()
    return {"ok": True, "engine": cp.get("engine") + "+verify", "src": str(s), "dest": str(d), "files": dst_cnt, "bytes": dst_bytes}


def rename_path(src: str, new_name: str, base_dir: Path, protected_core: set) -> Dict[str, Any]:
    s = _resolve_path(src)
    if not s.exists():
        return {"ok": False, "error": f"Path not found: '{s}'"}
    clean_n = Path(str(new_name or "").strip()).name
    if not clean_n:
        return {"ok": False, "error": "Invalid new name."}
    dst = s.with_name(clean_n)
    prot = _is_protected_target(s, base_dir, protected_core) or _is_protected_target(dst, base_dir, protected_core)
    if prot:
        return {"ok": False, "error": prot}
    s.rename(dst)
    return {"ok": True, "old": str(s), "new": str(dst)}


def trash_path(path: str, base_dir: Path, protected_core: set) -> Dict[str, Any]:
    p = _resolve_path(path)
    if not p.exists():
        return {"ok": False, "error": f"Path not found: '{p}'"}
    prot = _is_protected_target(p, base_dir, protected_core)
    if prot:
        return {"ok": False, "error": prot}
    if IS_WINDOWS:
        esc = str(p).replace("'", "''")
        ps = (
            "Add-Type -AssemblyName Microsoft.VisualBasic; "
            f"if (Test-Path -LiteralPath '{esc}' -PathType Container) "
            f"{{ [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteDirectory('{esc}', 'OnlyErrorDialogs', 'SendToRecycleBin') }} "
            f"else {{ [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile('{esc}', 'OnlyErrorDialogs', 'SendToRecycleBin') }}"
        )
        res = _run_ps(ps, timeout=20.0)
        if res.get("ok"):
            return {"ok": True, "method": "Windows Recycle Bin", "path": str(p)}
    trash_dir = base_dir / ".temp_cache" / "trash"
    trash_dir.mkdir(parents=True, exist_ok=True)
    dst = trash_dir / f"{int(time.time())}_{p.name}"
    shutil.move(str(p), str(dst))
    return {"ok": True, "method": "Portable Trash (.temp_cache/trash)", "path": str(p), "trashed_to": str(dst)}


def relocate_app(src: str, dst: str, base_dir: Path, protected_core: set, mode: str = "junction", temp_dir: Optional[Path] = None, background: bool = False) -> Dict[str, Any]:
    s = _resolve_path(src)
    d = _resolve_path(dst)
    if not s.exists() or not s.is_dir():
        return {"ok": False, "error": f"Source folder not found: '{s}'"}
    for chk in (s, d):
        prot = _is_protected_target(chk, base_dir, protected_core)
        if prot:
            return {"ok": False, "error": prot}
    running = _find_running_exes_in_folder(s)
    if running:
        return {"ok": False, "error": f"App is currently running ({', '.join(running[:4])}). Close it before relocating!"}

    job_id = f"reloc_{int(time.time() * 1000)}"
    job = {"id": job_id, "status": "running", "src": str(s), "dst": str(d), "mode": mode, "started_at": time.strftime("%H:%M:%S"), "detail": "Starting transfer..."}
    FS_JOBS[job_id] = job

    def _exec() -> Dict[str, Any]:
        try:
            src_bytes, src_cnt = _dir_size_and_count(s)
            job["detail"] = f"Copying {src_cnt} file(s) ({src_bytes / (1024**2):.1f} MB)..."
            cp = copy_path(str(s), str(d), base_dir, protected_core, "full_pc")
            if not cp.get("ok"):
                job.update({"status": "failed", "detail": cp.get("error", "Copy failed")})
                return {"ok": False, "job_id": job_id, "error": cp.get("error")}
            dst_bytes, dst_cnt = _dir_size_and_count(d)
            if dst_cnt < src_cnt:
                err = f"Verification mismatch: copied {dst_cnt}/{src_cnt} files. Original kept safe."
                job.update({"status": "failed", "detail": err})
                return {"ok": False, "job_id": job_id, "error": err}

            if temp_dir:
                temp_dir.mkdir(parents=True, exist_ok=True)
                (temp_dir / f"{job_id}_manifest.json").write_text(
                    json.dumps({"src": str(s), "dst": str(d), "mode": mode, "files": dst_cnt, "bytes": dst_bytes, "ts": time.strftime("%Y-%m-%d %H:%M:%S")}, indent=2),
                    encoding="utf-8",
                )

            backup_old = s.with_name(s.name + f".avs_reloc_old_{int(time.time())}")
            s.rename(backup_old)
            link_note = ""
            if mode == "junction":
                try:
                    if IS_WINDOWS:
                        mk = subprocess.run(["cmd", "/c", "mklink", "/J", str(s), str(d)], capture_output=True, text=True)
                        if mk.returncode != 0:
                            raise RuntimeError(mk.stderr or mk.stdout or "mklink /J failed")
                        link_note = f"Created NTFS Directory Junction: {s} -> {d}"
                    else:
                        os.symlink(str(d), str(s), target_is_directory=True)
                        link_note = f"Created symlink: {s} -> {d}"
                    shutil.rmtree(backup_old, ignore_errors=True)
                except Exception as le:
                    if backup_old.exists() and not s.exists():
                        backup_old.rename(s)
                    job.update({"status": "failed", "detail": f"Junction failed (rolled back safely): {le}"})
                    return {"ok": False, "job_id": job_id, "error": f"Junction failed (original restored): {le}"}
            else:
                shutil.rmtree(backup_old, ignore_errors=True)
                rw = rewrite_shortcuts(str(s), str(d))
                link_note = f"Clean move complete. Shortcuts updated: {rw.get('updated', 0)}"

            summary = f"Relocated '{s}' -> '{d}' ({dst_cnt} files, {dst_bytes / (1024**2):.1f} MB). {link_note}"
            job.update({"status": "done", "detail": summary})
            return {"ok": True, "job_id": job_id, "summary": summary, "files": dst_cnt, "bytes": dst_bytes}
        except Exception as e:
            job.update({"status": "failed", "detail": str(e)})
            return {"ok": False, "job_id": job_id, "error": str(e)}

    if background:
        threading.Thread(target=_exec, daemon=True).start()
        return {"ok": True, "job_id": job_id, "status": "running", "summary": f"Started background relocation job '{job_id}' ({s} -> {d}). Check with vault.job_status('{job_id}')."}
    return _exec()


def get_job_status(job_id: str = "") -> Dict[str, Any]:
    if not job_id:
        return {"ok": True, "jobs": list(FS_JOBS.values())[-15:]}
    j = FS_JOBS.get(job_id)
    return {"ok": bool(j), "job": j} if j else {"ok": False, "error": f"Unknown job '{job_id}'."}


def create_shortcut(target_path: str, shortcut_path: str, arguments: str = "", working_dir: str = "", icon_path: str = "", description: str = "") -> Dict[str, Any]:
    tgt = _resolve_path(target_path)
    lnk = _resolve_path(shortcut_path)
    if IS_WINDOWS and lnk.suffix.lower() != ".lnk":
        lnk = lnk.with_suffix(".lnk")
    if not IS_WINDOWS:
        lnk.parent.mkdir(parents=True, exist_ok=True)
        if lnk.exists() or lnk.is_symlink():
            lnk.unlink()
        os.symlink(str(tgt), str(lnk))
        return {"ok": True, "shortcut": str(lnk), "target": str(tgt), "method": "symlink"}

    lnk.parent.mkdir(parents=True, exist_ok=True)
    wd = str(_resolve_path(working_dir)) if working_dir else str(tgt.parent)
    esc = lambda v: str(v or "").replace("'", "''")
    ps = (
        "$wsh = New-Object -ComObject WScript.Shell; "
        f"$sc = $wsh.CreateShortcut('{esc(lnk)}'); "
        f"$sc.TargetPath = '{esc(tgt)}'; "
        f"$sc.WorkingDirectory = '{esc(wd)}'; "
        + (f"$sc.Arguments = '{esc(arguments)}'; " if arguments else "")
        + (f"$sc.IconLocation = '{esc(icon_path)}'; " if icon_path else "")
        + (f"$sc.Description = '{esc(description)}'; " if description else "")
        + "$sc.Save(); Write-Output 'OK'"
    )
    res = _run_ps(ps)
    return {"ok": bool(res.get("ok")), "shortcut": str(lnk), "target": str(tgt), "detail": res.get("output")}


def list_shortcuts(folder: str = "Desktop") -> Dict[str, Any]:
    root = _resolve_path(folder)
    if not root.exists():
        return {"ok": False, "error": f"Folder not found: '{root}'"}
    if not IS_WINDOWS:
        items = [{"name": p.name, "path": str(p), "target": str(p.resolve())} for p in sorted(root.glob("*")) if p.is_symlink()]
        return {"ok": True, "folder": str(root), "shortcuts": items}
    esc = str(root).replace("'", "''")
    ps = (
        "$wsh = New-Object -ComObject WScript.Shell; "
        f"$out = @(); Get-ChildItem -LiteralPath '{esc}' -Filter '*.lnk' -ErrorAction SilentlyContinue | ForEach-Object {{ "
        "$sc = $wsh.CreateShortcut($_.FullName); "
        "$out += [PSCustomObject]@{ name=$_.Name; path=$_.FullName; target=$sc.TargetPath; workdir=$sc.WorkingDirectory; args=$sc.Arguments } "
        "}; $out | ConvertTo-Json -Compress"
    )
    res = _run_ps(ps)
    if not res.get("ok"):
        return {"ok": False, "error": res.get("output")}
    raw = res.get("output") or "[]"
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            parsed = [parsed]
        return {"ok": True, "folder": str(root), "shortcuts": parsed}
    except Exception:
        return {"ok": True, "folder": str(root), "shortcuts": []}


def rewrite_shortcuts(old_prefix: str, new_prefix: str, search_dirs: Optional[List[str]] = None) -> Dict[str, Any]:
    old_p = str(_resolve_path(old_prefix))
    new_p = str(_resolve_path(new_prefix))
    if not IS_WINDOWS:
        return {"ok": True, "updated": 0, "note": "Shortcut .lnk rewriting is Windows-specific."}
    dirs = search_dirs or [
        str(Path.home() / "Desktop"),
        str(Path(os.environ.get("APPDATA", "")) / "Microsoft/Windows/Start Menu/Programs"),
    ]
    updated = []
    esc = lambda v: str(v).replace("'", "''")
    for d in dirs:
        if not d or not Path(d).exists():
            continue
        ps = (
            "$wsh = New-Object -ComObject WScript.Shell; "
            f"$oldP = '{esc(old_p)}'; $newP = '{esc(new_p)}'; "
            f"Get-ChildItem -LiteralPath '{esc(d)}' -Filter '*.lnk' -Recurse -ErrorAction SilentlyContinue | ForEach-Object {{ "
            "$sc = $wsh.CreateShortcut($_.FullName); $chg = $false; "
            "if ($sc.TargetPath -and $sc.TargetPath.StartsWith($oldP, [System.StringComparison]::OrdinalIgnoreCase)) { "
            "$sc.TargetPath = $newP + $sc.TargetPath.Substring($oldP.Length); $chg = $true }; "
            "if ($sc.WorkingDirectory -and $sc.WorkingDirectory.StartsWith($oldP, [System.StringComparison]::OrdinalIgnoreCase)) { "
            "$sc.WorkingDirectory = $newP + $sc.WorkingDirectory.Substring($oldP.Length); $chg = $true }; "
            "if ($chg) { $sc.Save(); Write-Output $_.FullName } }"
        )
        res = _run_ps(ps, timeout=25.0)
        if res.get("ok") and res.get("output"):
            updated.extend([ln.strip() for ln in res["output"].splitlines() if ln.strip()])
    return {"ok": True, "updated": len(updated), "files": updated[:50]}
