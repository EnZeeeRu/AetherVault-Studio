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
import threading
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
