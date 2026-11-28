"""
avs/dlna_server.py — Pure-Python Toggleable DLNA / UPnP Media Server (v7.1 Lamppost).
Broadcasts AetherVault Media over local LAN via SSDP multicast (239.255.255.250:1900)
and serves UPnP Device Description + ContentDirectory:1 SOAP Browse XML over the active
FastAPI HTTP port so Roku Media Player and VLC auto-discover shared folders with 0% CPU when OFF.
"""
from __future__ import annotations

import hashlib
import html
import socket
import struct
import threading
import time
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from avs import cloud_files

SSDP_ADDR = "239.255.255.250"
SSDP_PORT = 1900
UPNP_MEDIA_EXTS = cloud_files.VIDEO_EXTS | cloud_files.AUDIO_EXTS | cloud_files.IMAGE_EXTS


def _stable_uuid(seed: str) -> str:
    h = hashlib.md5(seed.encode("utf-8")).hexdigest()
    return f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


class DLNAMediaServer:
    """Lightweight, toggleable SSDP responder + UPnP ContentDirectory:1 XML generator."""

    def __init__(self, get_lan_ip_fn: Callable[[], str], get_port_fn: Callable[[], int], get_roots_fn: Callable[[], List[Dict[str, Any]]]):
        self._get_lan_ip = get_lan_ip_fn
        self._get_port = get_port_fn
        self._get_roots = get_roots_fn
        self.friendly_name = "AetherVault Media"
        self.udn = f"uuid:{_stable_uuid('AetherVaultStudio-DLNA-v71')}"
        self._running = False
        self._stop_evt = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._sock: Optional[socket.socket] = None
        self.last_error = ""
        self.started_at = 0.0
        self.discoveries_served = 0

    @property
    def running(self) -> bool:
        return bool(self._running)

    def _location_url(self) -> str:
        return f"http://{self._get_lan_ip()}:{self._get_port()}/dlna/device.xml"

    def _build_notify(self, nt: str, nts: str) -> bytes:
        usn = f"{self.udn}::{nt}" if nt != self.udn else self.udn
        lines = [
            "NOTIFY * HTTP/1.1",
            f"HOST: {SSDP_ADDR}:{SSDP_PORT}",
            "CACHE-CONTROL: max-age=1800",
            f"LOCATION: {self._location_url()}",
            f"NT: {nt}",
            f"NTS: {nts}",
            "SERVER: AetherVault/7.1 UPnP/1.0 DLNADOC/1.50",
            f"USN: {usn}",
            "",
            "",
        ]
        return "\r\n".join(lines).encode("utf-8")

    def _build_msearch_reply(self, st: str) -> bytes:
        usn = f"{self.udn}::{st}" if st != self.udn else self.udn
        lines = [
            "HTTP/1.1 200 OK",
            "CACHE-CONTROL: max-age=1800",
            "EXT:",
            f"LOCATION: {self._location_url()}",
            "SERVER: AetherVault/7.1 UPnP/1.0 DLNADOC/1.50",
            f"ST: {st}",
            f"USN: {usn}",
            "",
            "",
        ]
        return "\r\n".join(lines).encode("utf-8")

    def _broadcast_nts(self, sock: socket.socket, nts: str):
        targets = [
            "upnp:rootdevice",
            self.udn,
            "urn:schemas-upnp-org:device:MediaServer:1",
            "urn:schemas-upnp-org:service:ContentDirectory:1",
        ]
        for nt in targets:
            try:
                sock.sendto(self._build_notify(nt, nts), (SSDP_ADDR, SSDP_PORT))
            except Exception:
                pass

    def start(self, friendly_name: str = "") -> Dict[str, Any]:
        if friendly_name:
            self.friendly_name = friendly_name[:48]
        if self._running:
            return self.status()
        self._stop_evt.clear()
        self.last_error = ""
        self._running = True
        self.started_at = time.time()
        self._thread = threading.Thread(target=self._ssdp_loop, daemon=True)
        self._thread.start()
        return self.status()

    def stop(self) -> Dict[str, Any]:
        if not self._running:
            return self.status()
        self._running = False
        self._stop_evt.set()
        if self._sock is not None:
            try:
                self._broadcast_nts(self._sock, "ssdp:byebye")
            except Exception:
                pass
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.5)
        self._thread = None
        return self.status()

    def status(self) -> Dict[str, Any]:
        roots = [r for r in (self._get_roots() or []) if r.get("dlna", True) and r.get("exists", True)]
        return {
            "enabled": self._running,
            "friendly_name": self.friendly_name,
            "udn": self.udn,
            "device_xml_url": self._location_url(),
            "m3u_url": f"http://{self._get_lan_ip()}:{self._get_port()}/cloud/playlist.m3u",
            "shared_root_count": len(roots),
            "discoveries_served": self.discoveries_served,
            "last_error": self.last_error,
        }

    def _ssdp_loop(self):
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if hasattr(socket, "SO_REUSEPORT"):
                try:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                except Exception:
                    pass
            try:
                sock.bind(("", SSDP_PORT))
            except OSError:
                sock.bind(("", 0))
            mreq = struct.pack("4sl", socket.inet_aton(SSDP_ADDR), socket.INADDR_ANY)
            try:
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            except Exception:
                pass
            try:
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            except Exception:
                pass
            sock.settimeout(1.0)
            self._sock = sock
            self._broadcast_nts(sock, "ssdp:alive")
            last_announce = time.time()

            while not self._stop_evt.is_set() and self._running:
                now = time.time()
                if (now - last_announce) >= 120.0:
                    self._broadcast_nts(sock, "ssdp:alive")
                    last_announce = now
                try:
                    data, addr = sock.recvfrom(4096)
                except socket.timeout:
                    continue
                except OSError:
                    break
                msg = data.decode("utf-8", errors="ignore")
                if "M-SEARCH" in msg and "ssdp:discover" in msg.lower():
                    st_line = ""
                    for ln in msg.splitlines():
                        if ln.lower().startswith("st:"):
                            st_line = ln.split(":", 1)[1].strip()
                            break
                    if st_line in (
                        "ssdp:all",
                        "upnp:rootdevice",
                        self.udn,
                        "urn:schemas-upnp-org:device:MediaServer:1",
                        "urn:schemas-upnp-org:service:ContentDirectory:1",
                    ):
                        reply_st = "urn:schemas-upnp-org:device:MediaServer:1" if st_line == "ssdp:all" else st_line
                        try:
                            sock.sendto(self._build_msearch_reply(reply_st), addr)
                            self.discoveries_served += 1
                        except Exception:
                            pass
        except Exception as e:
            self.last_error = f"{type(e).__name__}: {e}"
        finally:
            if sock is not None:
                try:
                    self._broadcast_nts(sock, "ssdp:byebye")
                except Exception:
                    pass
                try:
                    sock.close()
                except Exception:
                    pass
            self._sock = None

    def build_device_xml(self) -> str:
        base_u = f"http://{self._get_lan_ip()}:{self._get_port()}"
        return f"""<?xml version="1.0" encoding="utf-8"?>
<root xmlns="urn:schemas-upnp-org:device-1-0" xmlns:dlna="urn:schemas-dlna-org:device-1-0">
  <specVersion><major>1</major><minor>0</minor></specVersion>
  <URLBase>{base_u}/</URLBase>
  <device>
    <deviceType>urn:schemas-upnp-org:device:MediaServer:1</deviceType>
    <friendlyName>{html.escape(self.friendly_name)}</friendlyName>
    <manufacturer>AetherVault Studio</manufacturer>
    <modelName>AetherVault Media Server</modelName>
    <modelNumber>7.1</modelNumber>
    <UDN>{self.udn}</UDN>
    <dlna:X_DLNADOC>DMS-1.50</dlna:X_DLNADOC>
    <serviceList>
      <service>
        <serviceType>urn:schemas-upnp-org:service:ContentDirectory:1</serviceType>
        <serviceId>urn:upnp-org:serviceId:ContentDirectory</serviceId>
        <SCPDURL>/dlna/cds.xml</SCPDURL>
        <controlURL>/dlna/control</controlURL>
        <eventSubURL>/dlna/event</eventSubURL>
      </service>
    </serviceList>
  </device>
</root>"""

    def build_cds_scpd_xml(self) -> str:
        return """<?xml version="1.0" encoding="utf-8"?>
<scpd xmlns="urn:schemas-upnp-org:service-1-0">
  <specVersion><major>1</major><minor>0</minor></specVersion>
  <actionList>
    <action>
      <name>Browse</name>
      <argumentList>
        <argument><name>ObjectID</name><direction>in</direction><relatedStateVariable>A_ARG_TYPE_ObjectID</relatedStateVariable></argument>
        <argument><name>BrowseFlag</name><direction>in</direction><relatedStateVariable>A_ARG_TYPE_BrowseFlag</relatedStateVariable></argument>
        <argument><name>Filter</name><direction>in</direction><relatedStateVariable>A_ARG_TYPE_Filter</relatedStateVariable></argument>
        <argument><name>StartingIndex</name><direction>in</direction><relatedStateVariable>A_ARG_TYPE_Index</relatedStateVariable></argument>
        <argument><name>RequestedCount</name><direction>in</direction><relatedStateVariable>A_ARG_TYPE_Count</relatedStateVariable></argument>
        <argument><name>SortCriteria</name><direction>in</direction><relatedStateVariable>A_ARG_TYPE_SortCriteria</relatedStateVariable></argument>
        <argument><name>Result</name><direction>out</direction><relatedStateVariable>A_ARG_TYPE_Result</relatedStateVariable></argument>
        <argument><name>NumberReturned</name><direction>out</direction><relatedStateVariable>A_ARG_TYPE_Count</relatedStateVariable></argument>
        <argument><name>TotalMatches</name><direction>out</direction><relatedStateVariable>A_ARG_TYPE_Count</relatedStateVariable></argument>
        <argument><name>UpdateID</name><direction>out</direction><relatedStateVariable>A_ARG_TYPE_UpdateID</relatedStateVariable></argument>
      </argumentList>
    </action>
    <action>
      <name>GetSystemUpdateID</name>
      <argumentList>
        <argument><name>Id</name><direction>out</direction><relatedStateVariable>SystemUpdateID</relatedStateVariable></argument>
      </argumentList>
    </action>
  </actionList>
  <serviceStateTable>
    <stateVariable sendEvents="no"><name>A_ARG_TYPE_ObjectID</name><dataType>string</dataType></stateVariable>
    <stateVariable sendEvents="no"><name>A_ARG_TYPE_Result</name><dataType>string</dataType></stateVariable>
    <stateVariable sendEvents="no"><name>A_ARG_TYPE_BrowseFlag</name><dataType>string</dataType></stateVariable>
    <stateVariable sendEvents="no"><name>A_ARG_TYPE_Filter</name><dataType>string</dataType></stateVariable>
    <stateVariable sendEvents="no"><name>A_ARG_TYPE_SortCriteria</name><dataType>string</dataType></stateVariable>
    <stateVariable sendEvents="no"><name>A_ARG_TYPE_Index</name><dataType>ui4</dataType></stateVariable>
    <stateVariable sendEvents="no"><name>A_ARG_TYPE_Count</name><dataType>ui4</dataType></stateVariable>
    <stateVariable sendEvents="no"><name>A_ARG_TYPE_UpdateID</name><dataType>ui4</dataType></stateVariable>
    <stateVariable sendEvents="yes"><name>SystemUpdateID</name><dataType>ui4</dataType></stateVariable>
  </serviceStateTable>
</scpd>"""

    def handle_soap_action(self, soap_action: str, body_xml: str, base_url: str) -> str:
        act = (soap_action or "").strip().strip('"')
        if "GetSystemUpdateID" in act or "GetSystemUpdateID" in body_xml:
            return (
                '<?xml version="1.0" encoding="utf-8"?>'
                '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
                '<s:Body><u:GetSystemUpdateIDResponse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1">'
                '<Id>1</Id></u:GetSystemUpdateIDResponse></s:Body></s:Envelope>'
            )

        obj_id = "0"
        start_idx = 0
        req_count = 200
        try:
            root_el = ET.fromstring(body_xml.encode("utf-8"))
            for el in root_el.iter():
                tag = el.tag.split("}")[-1]
                if tag == "ObjectID" and el.text:
                    obj_id = el.text.strip()
                elif tag == "StartingIndex" and el.text and el.text.strip().isdigit():
                    start_idx = int(el.text.strip())
                elif tag == "RequestedCount" and el.text and el.text.strip().isdigit():
                    req_count = int(el.text.strip()) or 200
        except Exception:
            pass

        didl_items = self._browse_didl(obj_id, base_url.rstrip("/"))
        total = len(didl_items)
        sliced = didl_items[start_idx : start_idx + (req_count if req_count > 0 else total)]
        didl = (
            '<DIDL-Lite xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" '
            'xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/">'
            + "".join(sliced)
            + "</DIDL-Lite>"
        )
        return (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
            '<s:Body><u:BrowseResponse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1">'
            f"<Result>{html.escape(didl)}</Result>"
            f"<NumberReturned>{len(sliced)}</NumberReturned>"
            f"<TotalMatches>{total}</TotalMatches>"
            "<UpdateID>1</UpdateID>"
            "</u:BrowseResponse></s:Body></s:Envelope>"
        )

    def _browse_didl(self, obj_id: str, base_url: str) -> List[str]:
        roots = [r for r in (self._get_roots() or []) if r.get("dlna", True) and r.get("exists", True)]
        out: List[str] = []
        if obj_id in ("0", "", "root"):
            for r in roots:
                cid = f"root:{r['id']}"
                out.append(
                    f'<container id="{html.escape(cid)}" parentID="0" restricted="1">'
                    f"<dc:title>{html.escape(r['label'])}</dc:title>"
                    "<upnp:class>object.container.storageFolder</upnp:class></container>"
                )
            return out

        if obj_id.startswith("root:"):
            raw = obj_id[5:]
            root_id, _, rel = raw.partition("/")
            root = next((r for r in roots if r["id"] == root_id), None)
            if not root:
                return []
            rdir = Path(root["path"]).resolve()
            cur = (rdir / cloud_files.sanitize_rel(rel)).resolve() if rel else rdir
            if cur != rdir and rdir not in cur.parents:
                return []
            if not cur.exists() or not cur.is_dir():
                return []
            for p in sorted(cur.iterdir(), key=lambda x: (0 if x.is_dir() else 1, x.name.lower())):
                if p.name.startswith("."):
                    continue
                p_rel = p.relative_to(rdir).as_posix()
                if p.is_dir():
                    cid = f"root:{root_id}/{p_rel}"
                    out.append(
                        f'<container id="{html.escape(cid)}" parentID="{html.escape(obj_id)}" restricted="1">'
                        f"<dc:title>{html.escape(p.name)}</dc:title>"
                        "<upnp:class>object.container.storageFolder</upnp:class></container>"
                    )
                elif p.suffix.lower() in UPNP_MEDIA_EXTS:
                    kind = cloud_files.classify_ext(p.suffix.lower())
                    upnp_cls = {
                        "video": "object.item.videoItem",
                        "audio": "object.item.audioItem.musicTrack",
                        "image": "object.item.imageItem.photo",
                    }.get(kind, "object.item")
                    mime = cloud_files.guess_mime(p)
                    size = p.stat().st_size
                    url = f"{base_url}/cloud/stream/{urllib.parse.quote(root_id)}/{urllib.parse.quote(p_rel)}"
                    iid = f"item:{root_id}/{p_rel}"
                    out.append(
                        f'<item id="{html.escape(iid)}" parentID="{html.escape(obj_id)}" restricted="1">'
                        f"<dc:title>{html.escape(p.stem)}</dc:title>"
                        f"<upnp:class>{upnp_cls}</upnp:class>"
                        f'<res size="{size}" protocolInfo="http-get:*:{mime}:DLNA.ORG_OP=01;DLNA.ORG_CI=0">{html.escape(url)}</res>'
                        "</item>"
                    )
        return out
