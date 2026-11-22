"""
avs/hardware_monitor.py — SpecPulse-Inspired Deep Hardware & Live Telemetry Engine.
Features:
  - True 64-bit GPU VRAM reader via Windows Registry (bypasses 4GB WMI AdapterRAM cap).
  - Deep static specs (CPU, Motherboard/BIOS, RAM sticks, GPUs, Physical Disks).
  - Live telemetry snapshot (per-core CPU, RAM, GPU 3D/Compute %, Dedicated VRAM MB, Disk & Net I/O).
  - 100% graceful fallback on macOS/Linux or when optional wmi/py-cpuinfo are not installed.
"""
import os
import time
import socket
import platform
import hashlib
import math
import threading
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any, Dict, List

IS_WINDOWS = (platform.system() == "Windows")

try:
    import psutil
except ImportError:
    psutil = None

try:
    import cpuinfo
except ImportError:
    cpuinfo = None

HAS_WMI = False
if IS_WINDOWS:
    try:
        import winreg
    except ImportError:
        winreg = None
    try:
        import pythoncom
        import wmi
        HAS_WMI = True
    except ImportError:
        HAS_WMI = False
else:
    winreg = None


def read_registry_gpu_vram() -> Dict[str, int]:
    """Reads true 64-bit VRAM (bytes) from Windows registry to bypass the 4GB 32-bit WMI cap."""
    vram_map: Dict[str, int] = {}
    if not IS_WINDOWS or winreg is None:
        return vram_map
    base_path = r"SYSTEM\ControlSet001\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base_path) as base_key:
            for i in range(32):
                try:
                    sub_name = winreg.EnumKey(base_key, i)
                    if not sub_name.isdigit():
                        continue
                    with winreg.OpenKey(base_key, sub_name) as sub_key:
                        try:
                            desc, _ = winreg.QueryValueEx(sub_key, "DriverDesc")
                        except FileNotFoundError:
                            continue
                        try:
                            qw_mem, _ = winreg.QueryValueEx(sub_key, "HardwareInformation.qwMemorySize")
                            if isinstance(qw_mem, bytes):
                                qw_mem = int.from_bytes(qw_mem, byteorder="little")
                            vram_map[str(desc).strip().lower()] = int(qw_mem)
                        except FileNotFoundError:
                            pass
                except OSError:
                    break
    except OSError:
        pass
    return vram_map


def get_static_hardware_specs() -> Dict[str, Any]:
    """Collects Speccy/SpecPulse-style deep hardware specs once (cached by caller)."""
    cinfo = {}
    if cpuinfo is not None:
        try:
            cinfo = cpuinfo.get_cpu_info() or {}
        except Exception:
            cinfo = {}

    freq = psutil.cpu_freq() if psutil else None
    vm = psutil.virtual_memory() if psutil else None

    specs: Dict[str, Any] = {
        "hostname": socket.gethostname(),
        "os": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "arch": platform.machine(),
            "boot_time": psutil.boot_time() if psutil else 0,
        },
        "cpu": {
            "name": cinfo.get("brand_raw") or platform.processor() or "Unknown CPU",
            "arch": cinfo.get("arch_string_raw") or platform.machine(),
            "physical_cores": (psutil.cpu_count(logical=False) or 1) if psutil else (os.cpu_count() or 1),
            "logical_cores": (psutil.cpu_count(logical=True) or 1) if psutil else (os.cpu_count() or 1),
            "max_mhz": round(freq.max, 0) if freq else 0,
            "l2_cache": cinfo.get("l2_cache_size", "N/A"),
            "l3_cache": cinfo.get("l3_cache_size", "N/A"),
        },
        "motherboard": {
            "manufacturer": "Unknown",
            "product": "Unknown",
            "bios_version": "Unknown",
            "bios_date": "Unknown",
        },
        "ram": {
            "total_gb": round(vm.total / (1024 ** 3), 2) if vm else 0.0,
            "sticks": [],
        },
        "gpus": [],
        "disks": [],
    }

    reg_vram = read_registry_gpu_vram()
    if HAS_WMI:
        pythoncom.CoInitialize()
        try:
            c = wmi.WMI()
            for board in c.Win32_BaseBoard():
                specs["motherboard"]["manufacturer"] = (board.Manufacturer or "").strip() or "Unknown"
                specs["motherboard"]["product"] = (board.Product or "").strip() or "Unknown"
                break
            for bios in c.Win32_BIOS():
                specs["motherboard"]["bios_version"] = (bios.SMBIOSBIOSVersion or bios.Name or "Unknown").strip()
                raw_date = str(bios.ReleaseDate or "")
                if len(raw_date) >= 8:
                    specs["motherboard"]["bios_date"] = f"{raw_date[0:4]}-{raw_date[4:6]}-{raw_date[6:8]}"
                break
            for mem in c.Win32_PhysicalMemory():
                cap_gb = round(int(mem.Capacity or 0) / (1024 ** 3), 1)
                specs["ram"]["sticks"].append({
                    "slot": (mem.DeviceLocator or "DIMM").strip(),
                    "manufacturer": (mem.Manufacturer or "Unknown").strip(),
                    "capacity_gb": cap_gb,
                    "speed_mhz": int(mem.ConfiguredClockSpeed or mem.Speed or 0),
                    "part": (mem.PartNumber or "").strip(),
                })
            for gpu in c.Win32_VideoController():
                name = (gpu.Name or "Unknown GPU").strip()
                vram_bytes = reg_vram.get(name.lower()) or int(gpu.AdapterRAM or 0)
                vram_gb = round(vram_bytes / (1024 ** 3), 2) if vram_bytes > 0 else 0
                res = f"{gpu.CurrentHorizontalResolution}x{gpu.CurrentVerticalResolution}" if gpu.CurrentHorizontalResolution else "N/A"
                refresh = f"{gpu.CurrentRefreshRate} Hz" if gpu.CurrentRefreshRate else ""
                specs["gpus"].append({
                    "name": name,
                    "vram_gb": vram_gb,
                    "driver": (gpu.DriverVersion or "Unknown").strip(),
                    "resolution": f"{res} {refresh}".strip(),
                })
            for disk in c.Win32_DiskDrive():
                size_gb = round(int(disk.Size or 0) / (1024 ** 3), 1)
                specs["disks"].append({
                    "model": (disk.Model or "Unknown Drive").strip(),
                    "interface": (disk.InterfaceType or "Unknown").strip(),
                    "size_gb": size_gb,
                    "status": (disk.Status or "OK").strip(),
                })
        except Exception:
            pass
        finally:
            pythoncom.CoUninitialize()
    elif reg_vram:
        for desc, vbytes in reg_vram.items():
            specs["gpus"].append({
                "name": desc.title(),
                "vram_gb": round(vbytes / (1024 ** 3), 2) if vbytes > 0 else 0,
                "driver": "Registry",
                "resolution": "N/A",
            })

    if not specs["gpus"]:
        specs["gpus"].append({"name": "Standard Display Adapter", "vram_gb": 0, "driver": "N/A", "resolution": "N/A"})

    return specs


class GpuLivePoller:
    """Polls Windows language-independent GPU WMI counters in a background thread."""

    def __init__(self) -> None:
        self.util_percent: float = 0.0
        self.vram_used_mb: float = 0.0
        self._running = False
        self._thread = None

    def start(self) -> None:
        if not HAS_WMI or self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False

    def _loop(self) -> None:
        pythoncom.CoInitialize()
        try:
            c = wmi.WMI()
            while self._running:
                try:
                    engines = c.Win32_PerfFormattedData_GPUPerformanceCounters_GPUEngine()
                    util_3d = 0.0
                    for eng in engines:
                        name = str(eng.Name or "").lower()
                        if "engtype_3d" in name or "engtype_compute" in name:
                            util_3d += float(eng.UtilizationPercentage or 0)
                    self.util_percent = round(min(util_3d, 100.0), 1)

                    mem_rows = c.Win32_PerfFormattedData_GPUPerformanceCounters_GPUAdapterMemory()
                    max_ded = 0
                    for row in mem_rows:
                        ded = int(row.DedicatedUsage or 0)
                        if ded > max_ded:
                            max_ded = ded
                    self.vram_used_mb = round(max_ded / (1024 ** 2), 1)
                except Exception:
                    pass
                time.sleep(2.0)
        finally:
            pythoncom.CoUninitialize()


_CACHED_SPECS: Dict[str, Any] = {}
_GPU_POLLER = GpuLivePoller()


def get_full_hardware_report() -> Dict[str, Any]:
    """Returns cached static specs + live CPU/RAM/GPU/VRAM snapshot."""
    global _CACHED_SPECS
    if not _CACHED_SPECS:
        _CACHED_SPECS = get_static_hardware_specs()
        _GPU_POLLER.start()
    live: Dict[str, Any] = {
        "cpu_percent": psutil.cpu_percent(interval=0.05) if psutil else 0.0,
        "gpu_util_percent": _GPU_POLLER.util_percent,
        "gpu_vram_used_mb": _GPU_POLLER.vram_used_mb,
        "uptime_sec": int(time.time() - psutil.boot_time()) if psutil else 0,
    }
    if psutil:
        vm = psutil.virtual_memory()
        live["ram_percent"] = vm.percent
        live["ram_used_gb"] = round(vm.used / (1024 ** 3), 2)
        live["ram_free_gb"] = round(vm.available / (1024 ** 3), 2)
    return {"specs": _CACHED_SPECS, "live": live}


# =============================================================================
# SPECPULSE MINI-BENCHMARK ENGINE (Top-level for Windows multiprocessing)
# =============================================================================
def _cpu_math_workload(iterations: int) -> float:
    """Prime sieve + floating-point trig mix for deterministic CPU scoring."""
    limit = 65000
    sieve = bytearray(b"\x01") * limit
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(limit ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i:limit:i] = b"\x00" * ((limit - 1 - i * i) // i + 1)

    acc = float(sum(sieve))
    for i in range(1, iterations):
        acc += math.sin(i * 0.0013) * math.cos(i * 0.0027)
    return acc


class BenchmarkManager:
    def __init__(self) -> None:
        self.running = False
        self.phase = "Idle"
        self.progress = 0
        self.results = None
        self.error = None

    def start(self, temp_dir: Path = None) -> bool:
        if self.running:
            return False
        self.running = True
        self.phase = "Initializing..."
        self.progress = 2
        self.results = None
        self.error = None
        tdir = Path(temp_dir) if temp_dir else Path(__file__).resolve().parent.parent / ".temp_cache"
        threading.Thread(target=self._run_suite, args=(tdir,), daemon=True).start()
        return True

    def _run_suite(self, temp_dir: Path) -> None:
        try:
            cores = (psutil.cpu_count(logical=True) if psutil else os.cpu_count()) or 2

            # 1. Single-Core CPU
            self.phase = "Single-Core CPU Stress (Primes + Trig)"
            self.progress = 12
            t0 = time.perf_counter()
            _cpu_math_workload(450_000)
            sc_time = max(time.perf_counter() - t0, 0.001)
            sc_score = int(round(1200 / sc_time))
            self.progress = 32

            # 2. Multi-Core CPU
            self.phase = f"Multi-Core CPU Stress ({cores} Threads)"
            t0 = time.perf_counter()
            with ProcessPoolExecutor(max_workers=cores) as ex:
                list(ex.map(_cpu_math_workload, [350_000] * cores))
            mc_time = max(time.perf_counter() - t0, 0.001)
            mc_score = int(round((1000 * cores) / mc_time))
            self.progress = 62

            # 3. RAM Bandwidth
            self.phase = "Memory Bandwidth & Hashing"
            t0 = time.perf_counter()
            block = bytearray(os.urandom(16 * 1024 * 1024))  # 16 MB
            total_bytes = 0
            for _ in range(18):
                copy_buf = bytearray(block)
                hashlib.blake2b(copy_buf, digest_size=16).digest()
                total_bytes += len(copy_buf) * 2
            ram_time = max(time.perf_counter() - t0, 0.001)
            ram_mb_s = round((total_bytes / (1024 ** 2)) / ram_time, 1)
            ram_score = int(round(ram_mb_s * 1.4))
            self.progress = 82

            # 4. Storage Sequential R/W (isolated inside .temp_cache, auto-deleted)
            self.phase = "Storage Sequential Read/Write (128 MB)"
            temp_dir.mkdir(parents=True, exist_ok=True)
            tmp_path = temp_dir / ".specpulse_bench.tmp"
            chunk = os.urandom(4 * 1024 * 1024)  # 4 MB x 32 = 128 MB
            try:
                t0 = time.perf_counter()
                with open(tmp_path, "wb") as f:
                    for _ in range(32):
                        f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
                write_time = max(time.perf_counter() - t0, 0.001)
                write_mb_s = round(128.0 / write_time, 1)

                t0 = time.perf_counter()
                with open(tmp_path, "rb") as f:
                    while f.read(4 * 1024 * 1024):
                        pass
                read_time = max(time.perf_counter() - t0, 0.001)
                read_mb_s = round(128.0 / read_time, 1)
            finally:
                if tmp_path.exists():
                    tmp_path.unlink()

            disk_score = int(round((write_mb_s + read_mb_s) * 1.1))
            total_score = sc_score + mc_score + ram_score + disk_score

            if total_score >= 16000:
                tier = "S-TIER WORKSTATION"
            elif total_score >= 10000:
                tier = "A-TIER PERFORMANCE"
            elif total_score >= 6000:
                tier = "B-TIER BALANCED RIG"
            else:
                tier = "C-TIER EVERYDAY MACHINE"

            self.results = {
                "total_score": total_score,
                "tier": tier,
                "single_core": {"score": sc_score, "time_s": round(sc_time, 2)},
                "multi_core": {"score": mc_score, "time_s": round(mc_time, 2), "threads": cores},
                "memory": {"score": ram_score, "mb_s": ram_mb_s},
                "storage": {"score": disk_score, "write_mb_s": write_mb_s, "read_mb_s": read_mb_s},
            }
            self.progress = 100
            self.phase = "Complete"
        except Exception as exc:
            self.error = str(exc)
            self.phase = "Error"
        finally:
            self.running = False


_BENCHMARK = BenchmarkManager()
_TELEM_STATE: Dict[str, Any] = {"disk": None, "net": None, "ts": 0.0, "primed": False}


def start_benchmark(temp_dir: Path = None) -> Dict[str, Any]:
    return {"started": _BENCHMARK.start(temp_dir=temp_dir)}


def get_benchmark_status() -> Dict[str, Any]:
    return {
        "running": _BENCHMARK.running,
        "phase": _BENCHMARK.phase,
        "progress": _BENCHMARK.progress,
        "results": _BENCHMARK.results,
        "error": _BENCHMARK.error,
    }


def get_cached_static_specs() -> Dict[str, Any]:
    global _CACHED_SPECS
    if not _CACHED_SPECS:
        _CACHED_SPECS = get_static_hardware_specs()
        _GPU_POLLER.start()
    return _CACHED_SPECS


def get_live_telemetry_payload() -> Dict[str, Any]:
    """1-second polling telemetry snapshot for the embedded SpecPulse dashboard (zero WebSocket dep)."""
    if not _CACHED_SPECS:
        get_cached_static_specs()

    if not psutil:
        return {
            "cpu_total": 0.0, "per_core": [0.0], "cpu_mhz": 0,
            "ram_pct": 0.0, "ram_used_gb": 0.0, "ram_total_gb": 0.0,
            "gpu_util": _GPU_POLLER.util_percent, "gpu_vram_used_mb": _GPU_POLLER.vram_used_mb,
            "disk_read_mbs": 0.0, "disk_write_mbs": 0.0,
            "net_down_kbs": 0.0, "net_up_kbs": 0.0,
            "partitions": [], "top_procs": [], "uptime_sec": 0,
        }

    now_ts = time.perf_counter()
    if not _TELEM_STATE["primed"]:
        psutil.cpu_percent(interval=None, percpu=True)
        _TELEM_STATE["disk"] = psutil.disk_io_counters()
        _TELEM_STATE["net"] = psutil.net_io_counters()
        _TELEM_STATE["ts"] = now_ts
        _TELEM_STATE["primed"] = True

    dt = max(now_ts - _TELEM_STATE["ts"], 0.2)
    _TELEM_STATE["ts"] = now_ts

    per_core = psutil.cpu_percent(interval=None, percpu=True)
    cpu_total = round(sum(per_core) / max(len(per_core), 1), 1)
    freq = psutil.cpu_freq()
    vm = psutil.virtual_memory()

    cur_disk = psutil.disk_io_counters()
    prev_disk = _TELEM_STATE["disk"]
    disk_read_mbs = round(max(cur_disk.read_bytes - prev_disk.read_bytes, 0) / (1024 ** 2) / dt, 2) if (cur_disk and prev_disk) else 0.0
    disk_write_mbs = round(max(cur_disk.write_bytes - prev_disk.write_bytes, 0) / (1024 ** 2) / dt, 2) if (cur_disk and prev_disk) else 0.0
    _TELEM_STATE["disk"] = cur_disk

    cur_net = psutil.net_io_counters()
    prev_net = _TELEM_STATE["net"]
    net_down_kbs = round(max(cur_net.bytes_recv - prev_net.bytes_recv, 0) / 1024 / dt, 1) if (cur_net and prev_net) else 0.0
    net_up_kbs = round(max(cur_net.bytes_sent - prev_net.bytes_sent, 0) / 1024 / dt, 1) if (cur_net and prev_net) else 0.0
    _TELEM_STATE["net"] = cur_net

    partitions: List[Dict[str, Any]] = []
    for p in psutil.disk_partitions(all=False):
        try:
            u = psutil.disk_usage(p.mountpoint)
            partitions.append({
                "mount": p.mountpoint,
                "fstype": p.fstype,
                "used_gb": round(u.used / (1024 ** 3), 1),
                "total_gb": round(u.total / (1024 ** 3), 1),
                "percent": u.percent,
            })
        except (PermissionError, OSError):
            continue

    procs = []
    for proc in psutil.process_iter(["pid", "name", "memory_percent"]):
        try:
            info = proc.info
            if info["name"] and info["memory_percent"] is not None:
                procs.append({
                    "pid": info["pid"],
                    "name": info["name"][:24],
                    "mem_pct": round(info["memory_percent"], 1),
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    procs.sort(key=lambda x: x["mem_pct"], reverse=True)

    return {
        "cpu_total": cpu_total,
        "per_core": per_core,
        "cpu_mhz": round(freq.current, 0) if freq else 0,
        "ram_pct": vm.percent,
        "ram_used_gb": round(vm.used / (1024 ** 3), 2),
        "ram_total_gb": round(vm.total / (1024 ** 3), 2),
        "gpu_util": _GPU_POLLER.util_percent,
        "gpu_vram_used_mb": _GPU_POLLER.vram_used_mb,
        "disk_read_mbs": disk_read_mbs,
        "disk_write_mbs": disk_write_mbs,
        "net_down_kbs": net_down_kbs,
        "net_up_kbs": net_up_kbs,
        "partitions": partitions,
        "top_procs": procs[:7],
        "uptime_sec": int(time.time() - psutil.boot_time()),
    }


# =============================================================================
# EMBEDDED SPECPULSE 60-FPS DASHBOARD HTML (1-Second Polling, Zero WebSockets)
# =============================================================================
SPECPULSE_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>SpecPulse :: AetherVault Hardware Telemetry</title>
<style>
  :root {
    --bg: #070b14;
    --panel: rgba(15, 23, 42, 0.82);
    --border: rgba(56, 189, 248, 0.22);
    --cyan: #38bdf8;
    --purple: #a855f7;
    --emerald: #10b981;
    --amber: #f59e0b;
    --rose: #f43f5e;
    --text: #e2e8f0;
    --muted: #94a3b8;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: radial-gradient(circle at 20% 0%, #0f1c36 0%, var(--bg) 55%);
    color: var(--text);
    min-height: 100vh;
    padding: 16px 20px 28px;
    overflow-x: hidden;
  }
  header {
    display: flex; justify-content: space-between; align-items: center;
    padding-bottom: 12px; margin-bottom: 16px;
    border-bottom: 1px solid var(--border); flex-wrap: wrap; gap: 12px;
  }
  .brand { display: flex; align-items: center; gap: 10px; }
  .pulse-dot {
    width: 11px; height: 11px; border-radius: 50%;
    background: var(--emerald); box-shadow: 0 0 12px var(--emerald);
    animation: pulse 1.6s infinite;
  }
  @keyframes pulse { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.45); opacity: 0.55; } }
  h1 { font-size: 1.25rem; letter-spacing: 1px; font-weight: 700; }
  h1 span { color: var(--cyan); }
  .meta-bar { display: flex; gap: 16px; font-size: 0.83rem; color: var(--muted); align-items: center; flex-wrap: wrap; }
  .meta-bar strong { color: var(--text); }
  .btn {
    background: linear-gradient(135deg, var(--cyan), var(--purple));
    border: none; color: #fff; font-weight: 600;
    padding: 8px 16px; border-radius: 8px; cursor: pointer;
    letter-spacing: 0.4px; transition: transform 0.15s, box-shadow 0.2s;
    box-shadow: 0 0 16px rgba(56, 189, 248, 0.35);
  }
  .btn:hover { transform: translateY(-1px); box-shadow: 0 0 24px rgba(168, 85, 247, 0.55); }
  .btn:disabled { opacity: 0.5; cursor: not-allowed; }
  .grid-top { display: grid; grid-template-columns: 1.35fr 1fr; gap: 16px; margin-bottom: 16px; }
  .grid-bottom { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
  @media (max-width: 1050px) { .grid-top, .grid-bottom { grid-template-columns: 1fr; } }
  .card {
    background: var(--panel); border: 1px solid var(--border); border-radius: 14px;
    padding: 15px 17px; backdrop-filter: blur(10px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35); position: relative; overflow: hidden;
  }
  .card-title {
    font-size: 0.78rem; text-transform: uppercase; letter-spacing: 1.3px;
    color: var(--cyan); margin-bottom: 10px;
    display: flex; justify-content: space-between; align-items: center;
  }
  .card-title .badge {
    font-size: 0.7rem; background: rgba(56, 189, 248, 0.15);
    padding: 2px 8px; border-radius: 99px; color: var(--text);
  }
  #schematicCanvas {
    width: 100%; height: 295px; display: block; border-radius: 10px;
    background: radial-gradient(circle at center, #0d172a 0%, #050811 100%); cursor: pointer;
  }
  .schematic-hint { font-size: 0.76rem; color: var(--muted); margin-top: 8px; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 6px; }
  .spec-list { list-style: none; font-size: 0.85rem; }
  .spec-list li { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(148, 163, 184, 0.12); gap: 10px; }
  .spec-list li:last-child { border-bottom: none; }
  .spec-key { color: var(--muted); white-space: nowrap; }
  .spec-val { color: var(--text); font-weight: 500; text-align: right; word-break: break-word; }
  .cores-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(22px, 1fr)); gap: 6px; height: 105px; align-items: end; margin-top: 8px; }
  .core-col { display: flex; flex-direction: column; align-items: center; height: 100%; justify-content: flex-end; }
  .core-bar-bg { width: 100%; height: 86px; background: rgba(255,255,255,0.06); border-radius: 5px; overflow: hidden; display: flex; align-items: flex-end; }
  .core-bar-fill { width: 100%; height: 5%; background: linear-gradient(to top, var(--cyan), var(--purple)); transition: height 0.35s ease, background 0.35s ease; border-radius: 4px; }
  .core-lbl { font-size: 0.62rem; color: var(--muted); margin-top: 4px; }
  .wave-canvas { width: 100%; height: 88px; display: block; margin-top: 8px; }
  .bar-row { margin-bottom: 10px; }
  .bar-head { display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px; }
  .bar-track { height: 8px; background: rgba(255,255,255,0.08); border-radius: 99px; overflow: hidden; }
  .bar-fill { height: 100%; width: 0%; background: linear-gradient(90deg, var(--emerald), var(--cyan)); transition: width 0.45s ease; }
  .modal-backdrop {
    position: fixed; inset: 0; background: rgba(3, 7, 18, 0.84); backdrop-filter: blur(8px);
    display: none; align-items: center; justify-content: center; z-index: 99; padding: 20px;
  }
  .modal-backdrop.open { display: flex; }
  .modal { width: 100%; max-width: 600px; background: #0d1526; border: 1px solid rgba(56, 189, 248, 0.4); border-radius: 16px; padding: 20px 22px; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.7); }
  #benchCanvas { width: 100%; height: 140px; border-radius: 10px; background: #050914; margin: 12px 0; display: block; }
  .score-hero { text-align: center; padding: 12px 0 6px; }
  .score-num { font-size: 2.6rem; font-weight: 800; background: linear-gradient(90deg, var(--cyan), var(--purple)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .score-tier { font-size: 0.82rem; letter-spacing: 2px; color: var(--emerald); font-weight: 700; }
</style>
</head>
<body>
<header>
  <div class="brand">
    <div class="pulse-dot"></div>
    <h1>SPEC<span>PULSE</span> <small style="font-size:0.7rem;color:var(--muted);font-weight:500;">// AetherVault Studio</small></h1>
  </div>
  <div class="meta-bar">
    <div>HOST: <strong id="hdrHost">...</strong></div>
    <div>OS: <strong id="hdrOS">...</strong></div>
    <div>UPTIME: <strong id="hdrUptime">00:00:00</strong></div>
    <button class="btn" id="openBenchBtn">Run Benchmark</button>
  </div>
</header>

<section class="grid-top">
  <div class="card">
    <div class="card-title">
      <span>Live Hardware Schematic</span>
      <span class="badge" id="schematicStatus">60 FPS TELEMETRY</span>
    </div>
    <canvas id="schematicCanvas"></canvas>
    <div class="schematic-hint">
      <span>Click any component block (CPU, RAM, GPU, STORAGE, MOBO) to inspect detailed specs.</span>
      <span id="liveNetLbl">NET: ↓ 0 KB/s | ↑ 0 KB/s</span>
    </div>
  </div>
  <div class="card">
    <div class="card-title">
      <span id="inspectorTitle">Hardware Inspector :: CPU</span>
      <span class="badge" id="inspectorBadge">ACTIVE</span>
    </div>
    <ul class="spec-list" id="inspectorList">
      <li><span class="spec-key">Loading hardware inventory...</span></li>
    </ul>
  </div>
</section>

<section class="grid-bottom">
  <div class="card">
    <div class="card-title">
      <span>CPU Core Activity</span>
      <span class="badge" id="cpuStatBadge">0% @ 0 MHz</span>
    </div>
    <div class="cores-grid" id="coresGrid"></div>
    <canvas class="wave-canvas" id="cpuWave"></canvas>
  </div>

  <div class="card">
    <div class="card-title">
      <span>Memory &amp; Graphics Load</span>
      <span class="badge" id="gpuStatBadge">GPU 0%</span>
    </div>
    <div class="bar-row">
      <div class="bar-head"><span>System RAM</span><span id="ramTxt">0 / 0 GB</span></div>
      <div class="bar-track"><div class="bar-fill" id="ramBar"></div></div>
    </div>
    <div class="bar-row">
      <div class="bar-head"><span>GPU 3D / Compute Engine</span><span id="gpuTxt">0%</span></div>
      <div class="bar-track"><div class="bar-fill" id="gpuBar" style="background:linear-gradient(90deg, var(--purple), var(--rose))"></div></div>
    </div>
    <div class="bar-row">
      <div class="bar-head"><span>Dedicated VRAM In Use</span><span id="vramTxt">0 MB</span></div>
      <div class="bar-track"><div class="bar-fill" id="vramBar" style="background:linear-gradient(90deg, var(--amber), var(--purple))"></div></div>
    </div>
    <div class="card-title" style="margin-top:12px; margin-bottom:6px;"><span>Top Memory Processes</span></div>
    <ul class="spec-list" id="procList"></ul>
  </div>

  <div class="card">
    <div class="card-title">
      <span>Storage &amp; Disk I/O</span>
      <span class="badge" id="diskIoBadge">R: 0 | W: 0 MB/s</span>
    </div>
    <div id="partitionsBox"></div>
    <canvas class="wave-canvas" id="ioWave"></canvas>
  </div>
</section>

<div class="modal-backdrop" id="benchModal">
  <div class="modal">
    <div class="card-title">
      <span>SpecPulse Mini-Benchmark Suite</span>
      <button class="btn" id="closeBenchBtn" style="padding:4px 12px; font-size:0.75rem; background:#334155; box-shadow:none;">Close</button>
    </div>
    <p style="font-size:0.83rem; color:var(--muted);">
      Tests Single-Core math, Multi-Core scaling, Memory bandwidth, and 128 MB Sequential Storage R/W (isolated in .temp_cache).
    </p>
    <canvas id="benchCanvas"></canvas>
    <div class="bar-row">
      <div class="bar-head"><span id="benchPhase">Ready</span><span id="benchPct">0%</span></div>
      <div class="bar-track"><div class="bar-fill" id="benchBar"></div></div>
    </div>
    <div id="benchResultsBox" style="display:none;">
      <div class="score-hero">
        <div class="score-num" id="scoreTotal">0</div>
        <div class="score-tier" id="scoreTier">--</div>
      </div>
      <ul class="spec-list" id="benchBreakdown"></ul>
    </div>
    <div style="margin-top:14px; text-align:right;">
      <button class="btn" id="startBenchBtn">Start Benchmark</button>
    </div>
  </div>
</div>

<script>
let SPECS = null;
let SELECTED = 'CPU';
let TELEMETRY = {
  cpu_total: 0, per_core: [], cpu_mhz: 0,
  ram_pct: 0, ram_used_gb: 0, ram_total_gb: 1,
  gpu_util: 0, gpu_vram_used_mb: 0,
  disk_read_mbs: 0, disk_write_mbs: 0,
  net_down_kbs: 0, net_up_kbs: 0,
  partitions: [], top_procs: [], uptime_sec: 0
};
const cpuHistory = new Array(50).fill(0);
const ioHistory = new Array(50).fill(0);

async function loadSpecs() {
  const res = await fetch('/api/specpulse/specs');
  SPECS = await res.json();
  document.getElementById('hdrHost').textContent = SPECS.hostname;
  document.getElementById('hdrOS').textContent = `${SPECS.os.system} ${SPECS.os.release}`;
  renderInspector('CPU');
}

function renderInspector(node) {
  SELECTED = node;
  const title = document.getElementById('inspectorTitle');
  const badge = document.getElementById('inspectorBadge');
  const list = document.getElementById('inspectorList');
  if (!SPECS) return;
  title.textContent = `Hardware Inspector :: ${node}`;
  let rows = [];
  if (node === 'CPU') {
    badge.textContent = `${SPECS.cpu.physical_cores}C / ${SPECS.cpu.logical_cores}T`;
    rows = [
      ['Processor', SPECS.cpu.name],
      ['Architecture', SPECS.cpu.arch],
      ['Physical / Logical', `${SPECS.cpu.physical_cores} Cores / ${SPECS.cpu.logical_cores} Threads`],
      ['Max Clock', SPECS.cpu.max_mhz ? `${SPECS.cpu.max_mhz} MHz` : 'N/A'],
      ['L2 / L3 Cache', `${SPECS.cpu.l2_cache} / ${SPECS.cpu.l3_cache}`],
    ];
  } else if (node === 'RAM') {
    badge.textContent = `${SPECS.ram.total_gb} GB`;
    rows.push(['Total Installed', `${SPECS.ram.total_gb} GB`]);
    if (SPECS.ram.sticks && SPECS.ram.sticks.length) {
      SPECS.ram.sticks.forEach((s, idx) => {
        rows.push([`Slot ${idx + 1} (${s.slot})`, `${s.capacity_gb} GB @ ${s.speed_mhz} MHz (${s.manufacturer})`]);
      });
    } else {
      rows.push(['Modules', 'Install wmi in Library Manager for per-DIMM specs']);
    }
  } else if (node === 'GPU') {
    badge.textContent = `${SPECS.gpus.length} ADAPTER(S)`;
    SPECS.gpus.forEach((g, idx) => {
      rows.push([`GPU #${idx + 1}`, g.name]);
      rows.push([`VRAM / Display`, `${g.vram_gb} GB | ${g.resolution}`]);
      rows.push([`Driver Version`, g.driver]);
    });
  } else if (node === 'STORAGE') {
    badge.textContent = `${SPECS.disks.length} DRIVE(S)`;
    if (SPECS.disks && SPECS.disks.length) {
      SPECS.disks.forEach((d, idx) => {
        rows.push([`Drive #${idx + 1}`, `${d.model}`]);
        rows.push([`Size / Interface`, `${d.size_gb} GB (${d.interface}) — ${d.status}`]);
      });
    } else {
      rows.push(['Drives', 'See mounted partitions below']);
    }
  } else if (node === 'MOBO') {
    badge.textContent = 'SYSTEM BOARD';
    rows = [
      ['Manufacturer', SPECS.motherboard.manufacturer],
      ['Board Model', SPECS.motherboard.product],
      ['BIOS Version', SPECS.motherboard.bios_version],
      ['BIOS Date', SPECS.motherboard.bios_date],
      ['OS Build', SPECS.os.version],
    ];
  }
  list.innerHTML = rows.map(([k, v]) => `<li><span class="spec-key">${k}</span><span class="spec-val">${v}</span></li>`).join('');
}

function fmtUptime(sec) {
  const h = String(Math.floor(sec / 3600)).padStart(2, '0');
  const m = String(Math.floor((sec % 3600) / 60)).padStart(2, '0');
  const s = String(sec % 60).padStart(2, '0');
  return `${h}:${m}:${s}`;
}

async function pollTelemetry() {
  try {
    const res = await fetch('/api/specpulse/telemetry');
    if (res.ok) {
      TELEMETRY = await res.json();
      updateUI();
    }
  } catch (e) {}
  setTimeout(pollTelemetry, 1000);
}

function updateUI() {
  const t = TELEMETRY;
  document.getElementById('hdrUptime').textContent = fmtUptime(t.uptime_sec || 0);
  document.getElementById('liveNetLbl').textContent = `NET: ↓ ${t.net_down_kbs} KB/s | ↑ ${t.net_up_kbs} KB/s`;
  document.getElementById('cpuStatBadge').textContent = `${t.cpu_total}% @ ${t.cpu_mhz} MHz`;
  document.getElementById('gpuStatBadge').textContent = `GPU ${t.gpu_util}%`;
  document.getElementById('diskIoBadge').textContent = `R: ${t.disk_read_mbs} | W: ${t.disk_write_mbs} MB/s`;

  const grid = document.getElementById('coresGrid');
  if (grid.children.length !== t.per_core.length) {
    grid.innerHTML = t.per_core.map((_, i) =>
      `<div class="core-col"><div class="core-bar-bg"><div class="core-bar-fill" id="coreFill${i}"></div></div><div class="core-lbl">C${i}</div></div>`
    ).join('');
  }
  t.per_core.forEach((val, i) => {
    const el = document.getElementById(`coreFill${i}`);
    if (el) {
      el.style.height = `${Math.max(val, 4)}%`;
      el.style.background = val > 80 ? 'linear-gradient(to top, #f59e0b, #f43f5e)' : 'linear-gradient(to top, #38bdf8, #a855f7)';
    }
  });

  document.getElementById('ramTxt').textContent = `${t.ram_used_gb} / ${t.ram_total_gb} GB (${t.ram_pct}%)`;
  document.getElementById('ramBar').style.width = `${t.ram_pct}%`;
  document.getElementById('gpuTxt').textContent = `${t.gpu_util}%`;
  document.getElementById('gpuBar').style.width = `${t.gpu_util}%`;

  const maxVramMb = (SPECS && SPECS.gpus[0] && SPECS.gpus[0].vram_gb > 0) ? SPECS.gpus[0].vram_gb * 1024 : 4096;
  const vramPct = Math.min(100, (t.gpu_vram_used_mb / maxVramMb) * 100);
  document.getElementById('vramTxt').textContent = `${t.gpu_vram_used_mb} MB`;
  document.getElementById('vramBar').style.width = `${vramPct}%`;

  document.getElementById('procList').innerHTML = (t.top_procs || []).map(p =>
    `<li><span class="spec-key">${p.name}</span><span class="spec-val">${p.mem_pct}% RAM</span></li>`
  ).join('');

  document.getElementById('partitionsBox').innerHTML = (t.partitions || []).map(p => `
    <div class="bar-row">
      <div class="bar-head"><span>${p.mount} (${p.fstype})</span><span>${p.used_gb} / ${p.total_gb} GB</span></div>
      <div class="bar-track"><div class="bar-fill" style="width:${p.percent}%; background:${p.percent > 85 ? '#f43f5e' : 'linear-gradient(90deg, #10b981, #38bdf8)'}"></div></div>
    </div>
  `).join('');

  cpuHistory.push(t.cpu_total); cpuHistory.shift();
  ioHistory.push(Math.min(100, (t.disk_read_mbs + t.disk_write_mbs) * 1.5)); ioHistory.shift();
  drawWave('cpuWave', cpuHistory, '#38bdf8');
  drawWave('ioWave', ioHistory, '#10b981');
}

function drawWave(canvasId, data, color) {
  const c = document.getElementById(canvasId);
  const ctx = c.getContext('2d');
  const w = c.width = c.clientWidth * devicePixelRatio;
  const h = c.height = c.clientHeight * devicePixelRatio;
  ctx.clearRect(0, 0, w, h);
  ctx.beginPath();
  data.forEach((v, i) => {
    const x = (i / (data.length - 1)) * w;
    const y = h - (v / 100) * (h - 12) - 6;
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
  });
  ctx.strokeStyle = color;
  ctx.lineWidth = 2.2 * devicePixelRatio;
  ctx.stroke();
  ctx.lineTo(w, h); ctx.lineTo(0, h); ctx.closePath();
  const grad = ctx.createLinearGradient(0, 0, 0, h);
  grad.addColorStop(0, color + '44'); grad.addColorStop(1, color + '00');
  ctx.fillStyle = grad; ctx.fill();
}

const schCanvas = document.getElementById('schematicCanvas');
const schCtx = schCanvas.getContext('2d');
let nodes = [];
const particles = Array.from({ length: 28 }, (_, i) => ({ bus: i % 4, t: Math.random(), speed: 0.004 + Math.random() * 0.006 }));

function layoutNodes(w, h) {
  const isNarrow = (w / (window.devicePixelRatio || 1)) < 520;
  if (isNarrow) {
    nodes = [
      { id: 'MOBO',    x: w * 0.04, y: h * 0.07, w: w * 0.27, h: h * 0.25, color: '#64748b' },
      { id: 'CPU',     x: w * 0.365, y: h * 0.07, w: w * 0.27, h: h * 0.25, color: '#38bdf8' },
      { id: 'RAM',     x: w * 0.69, y: h * 0.07, w: w * 0.27, h: h * 0.25, color: '#10b981' },
      { id: 'GPU',     x: w * 0.06, y: h * 0.56, w: w * 0.41, h: h * 0.28, color: '#a855f7' },
      { id: 'STORAGE', x: w * 0.53, y: h * 0.56, w: w * 0.41, h: h * 0.28, color: '#f59e0b' },
    ];
    return;
  }
  nodes = [
    { id: 'CPU',     x: w * 0.34, y: h * 0.16, w: w * 0.22, h: h * 0.32, color: '#38bdf8' },
    { id: 'RAM',     x: w * 0.66, y: h * 0.14, w: w * 0.24, h: h * 0.28, color: '#10b981' },
    { id: 'GPU',     x: w * 0.14, y: h * 0.58, w: w * 0.36, h: h * 0.28, color: '#a855f7' },
    { id: 'STORAGE', x: w * 0.60, y: h * 0.56, w: w * 0.28, h: h * 0.28, color: '#f59e0b' },
    { id: 'MOBO',    x: w * 0.06, y: h * 0.16, w: w * 0.20, h: h * 0.28, color: '#64748b' },
  ];
}

schCanvas.addEventListener('click', (e) => {
  const rect = schCanvas.getBoundingClientRect();
  const mx = (e.clientX - rect.left) * devicePixelRatio;
  const my = (e.clientY - rect.top) * devicePixelRatio;
  for (const n of nodes) {
    if (mx >= n.x && mx <= n.x + n.w && my >= n.y && my <= n.y + n.h) {
      renderInspector(n.id);
      break;
    }
  }
});

function drawSchematic(ts) {
  const w = schCanvas.width = schCanvas.clientWidth * devicePixelRatio;
  const h = schCanvas.height = schCanvas.clientHeight * devicePixelRatio;
  layoutNodes(w, h);
  schCtx.clearRect(0, 0, w, h);
  schCtx.strokeStyle = 'rgba(56, 189, 248, 0.05)';
  schCtx.lineWidth = 1;
  const step = 24 * devicePixelRatio;
  for (let x = 0; x < w; x += step) { schCtx.beginPath(); schCtx.moveTo(x, 0); schCtx.lineTo(x, h); schCtx.stroke(); }
  for (let y = 0; y < h; y += step) { schCtx.beginPath(); schCtx.moveTo(0, y); schCtx.lineTo(w, y); schCtx.stroke(); }

  const center = (n) => ({ x: n.x + n.w / 2, y: n.y + n.h / 2 });
  const cCPU = center(nodes[0]), cRAM = center(nodes[1]), cGPU = center(nodes[2]), cSTO = center(nodes[3]), cMB = center(nodes[4]);
  const buses = [
    [cCPU, cRAM, '#10b981', 1 + TELEMETRY.ram_pct / 40],
    [cCPU, cGPU, '#a855f7', 1 + TELEMETRY.gpu_util / 30],
    [cCPU, cSTO, '#f59e0b', 1 + Math.min(4, (TELEMETRY.disk_read_mbs + TELEMETRY.disk_write_mbs) / 20)],
    [cMB,  cCPU, '#38bdf8', 1 + TELEMETRY.cpu_total / 35],
  ];
  buses.forEach(([a, b, col]) => {
    schCtx.beginPath(); schCtx.moveTo(a.x, a.y); schCtx.lineTo(b.x, b.y);
    schCtx.strokeStyle = col + '44'; schCtx.lineWidth = 2.5 * devicePixelRatio; schCtx.stroke();
  });
  particles.forEach((p) => {
    const [a, b, col, boost] = buses[p.bus];
    p.t = (p.t + p.speed * boost) % 1;
    const px = a.x + (b.x - a.x) * p.t, py = a.y + (b.y - a.y) * p.t;
    schCtx.beginPath(); schCtx.arc(px, py, 3.2 * devicePixelRatio, 0, Math.PI * 2);
    schCtx.fillStyle = col; schCtx.shadowColor = col; schCtx.shadowBlur = 10 * devicePixelRatio; schCtx.fill(); schCtx.shadowBlur = 0;
  });

  const loads = { CPU: TELEMETRY.cpu_total, RAM: TELEMETRY.ram_pct, GPU: TELEMETRY.gpu_util, STORAGE: Math.min(100, (TELEMETRY.disk_read_mbs + TELEMETRY.disk_write_mbs) * 1.5), MOBO: 25 };
  const labels = { CPU: `${TELEMETRY.cpu_total}%`, RAM: `${TELEMETRY.ram_pct}%`, GPU: `${TELEMETRY.gpu_util}%`, STORAGE: `${(TELEMETRY.disk_read_mbs + TELEMETRY.disk_write_mbs).toFixed(1)} MB/s`, MOBO: 'BIOS/CHIPSET' };
  nodes.forEach((n) => {
    const load = loads[n.id];
    const pulse = 0.5 + 0.5 * Math.sin(ts * (0.003 + load * 0.00012));
    const isSel = SELECTED === n.id;
    schCtx.fillStyle = 'rgba(15, 23, 42, 0.92)';
    schCtx.strokeStyle = isSel ? '#ffffff' : n.color;
    schCtx.lineWidth = (isSel ? 2.6 : 1.5) * devicePixelRatio;
    schCtx.shadowColor = n.color;
    schCtx.shadowBlur = (6 + (load / 100) * 18 * pulse) * devicePixelRatio;
    schCtx.beginPath(); schCtx.roundRect(n.x, n.y, n.w, n.h, 10 * devicePixelRatio); schCtx.fill(); schCtx.stroke(); schCtx.shadowBlur = 0;
    const barW = (n.w - 16 * devicePixelRatio) * (load / 100);
    schCtx.fillStyle = n.color + 'aa';
    schCtx.fillRect(n.x + 8 * devicePixelRatio, n.y + n.h - 10 * devicePixelRatio, barW, 4 * devicePixelRatio);
    const compact = (w / (window.devicePixelRatio || 1)) < 520;
    const fTitle = (compact ? 10.5 : 13) * devicePixelRatio;
    const fSub = (compact ? 9.5 : 12) * devicePixelRatio;
    const padX = (compact ? 8 : 12) * devicePixelRatio;
    schCtx.fillStyle = '#e2e8f0'; schCtx.font = `700 ${fTitle}px Segoe UI, sans-serif`;
    schCtx.fillText(n.id, n.x + padX, n.y + 22 * devicePixelRatio);
    schCtx.fillStyle = n.color; schCtx.font = `600 ${fSub}px Segoe UI, sans-serif`;
    schCtx.fillText(compact && n.id === 'MOBO' ? 'BIOS' : labels[n.id], n.x + padX, n.y + 40 * devicePixelRatio);
  });
  requestAnimationFrame(drawSchematic);
}

const benchModal = document.getElementById('benchModal');
const benchCanvas = document.getElementById('benchCanvas');
const benchCtx = benchCanvas.getContext('2d');
let benchActive = false;

document.getElementById('openBenchBtn').onclick = () => { benchModal.classList.add('open'); drawBenchReactor(0); };
document.getElementById('closeBenchBtn').onclick = () => benchModal.classList.remove('open');
document.getElementById('startBenchBtn').onclick = async () => {
  document.getElementById('benchResultsBox').style.display = 'none';
  document.getElementById('startBenchBtn').disabled = true;
  await fetch('/api/specpulse/benchmark/start', { method: 'POST' });
  benchActive = true;
  pollBench();
};

async function pollBench() {
  const res = await fetch('/api/specpulse/benchmark/status');
  const st = await res.json();
  document.getElementById('benchPhase').textContent = st.phase;
  document.getElementById('benchPct').textContent = `${st.progress}%`;
  document.getElementById('benchBar').style.width = `${st.progress}%`;
  if (st.running) {
    setTimeout(pollBench, 400);
  } else {
    benchActive = false;
    document.getElementById('startBenchBtn').disabled = false;
    if (st.results) {
      const r = st.results;
      document.getElementById('benchResultsBox').style.display = 'block';
      document.getElementById('scoreTotal').textContent = r.total_score.toLocaleString();
      document.getElementById('scoreTier').textContent = r.tier;
      document.getElementById('benchBreakdown').innerHTML = `
        <li><span class="spec-key">Single-Core CPU</span><span class="spec-val">${r.single_core.score} pts (${r.single_core.time_s}s)</span></li>
        <li><span class="spec-key">Multi-Core CPU (${r.multi_core.threads}T)</span><span class="spec-val">${r.multi_core.score} pts (${r.multi_core.time_s}s)</span></li>
        <li><span class="spec-key">Memory Bandwidth</span><span class="spec-val">${r.memory.score} pts (${r.memory.mb_s} MB/s)</span></li>
        <li><span class="spec-key">Storage Seq R/W</span><span class="spec-val">${r.storage.score} pts (R ${r.storage.read_mb_s} / W ${r.storage.write_mb_s} MB/s)</span></li>
      `;
    }
  }
}

function drawBenchReactor(ts) {
  if (!benchModal.classList.contains('open')) return;
  const w = benchCanvas.width = benchCanvas.clientWidth * devicePixelRatio;
  const h = benchCanvas.height = benchCanvas.clientHeight * devicePixelRatio;
  benchCtx.clearRect(0, 0, w, h);
  const cx = w / 2, cy = h / 2, speed = benchActive ? 0.0045 : 0.0008;
  for (let i = 0; i < 4; i++) {
    const r = (20 + i * 15) * devicePixelRatio;
    const start = ts * speed * (i % 2 === 0 ? 1 : -1.3) + i;
    benchCtx.beginPath(); benchCtx.arc(cx, cy, r, start, start + Math.PI * 1.25);
    benchCtx.strokeStyle = i % 2 === 0 ? '#38bdf8' : '#a855f7';
    benchCtx.lineWidth = 3 * devicePixelRatio;
    benchCtx.shadowColor = benchCtx.strokeStyle; benchCtx.shadowBlur = (benchActive ? 14 : 4) * devicePixelRatio;
    benchCtx.stroke();
  }
  benchCtx.shadowBlur = 0;
  requestAnimationFrame(drawBenchReactor);
}

loadSpecs();
pollTelemetry();
requestAnimationFrame(drawSchematic);
</script>
</body>
</html>
"""
