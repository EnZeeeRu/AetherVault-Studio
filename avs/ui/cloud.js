/* avs/ui/cloud.js — Nextcloud-Style Vault Cloud Drive + Toggleable DLNA (Roku/VLC) + Phone Connect */
(function () {
  window.cloudState = {
    rootId: "vault_files", relPath: "", viewMode: "grid",
    roots: [], dlna: { enabled: false }, cloudEnabled: true, lanUrl: window.location.origin,
  };

  function fmtSize(b) {
    const n = Number(b || 0);
    if (n < 1024) return n + " B";
    if (n < 1024 * 1024) return (n / 1024).toFixed(1) + " KB";
    if (n < 1024 * 1024 * 1024) return (n / (1024 * 1024)).toFixed(1) + " MB";
    return (n / (1024 * 1024 * 1024)).toFixed(2) + " GB";
  }

  function iconForKind(kind, ext) {
    if (kind === "folder") return "📁";
    if (kind === "image") return "🖼️";
    if (kind === "video") return "🎬";
    if (kind === "audio") return "🎵";
    if (ext === ".pdf") return "📕";
    if (ext === ".py" || ext === ".js") return "💻";
    if (ext === ".md" || ext === ".txt") return "📝";
    return "📄";
  }

  window.refreshCloudView = async function () {
    try {
      const r = await fetch("/api/cloud_files/roots");
      const d = await r.json();
      if (d.ok) {
        window.cloudState.roots = d.roots || [];
        window.cloudState.dlna = d.dlna || { enabled: false };
        window.cloudState.cloudEnabled = Boolean(d.enabled);
        window.cloudState.lanUrl = d.lan_url || window.location.origin;
        renderCloudRootsAndSwitches();
      }
    } catch (e) {}
    await window.loadCloudDir(window.cloudState.rootId, window.cloudState.relPath);
  };

  function renderCloudRootsAndSwitches() {
    const rootsBox = document.getElementById("cloud-roots-list");
    const dlnaChk = document.getElementById("cloud-dlna-toggle");
    const cloudChk = document.getElementById("cloud-server-toggle");
    const dlnaBadge = document.getElementById("cloud-dlna-status-pill");
    if (dlnaChk) dlnaChk.checked = Boolean(window.cloudState.dlna.enabled);
    if (cloudChk) cloudChk.checked = Boolean(window.cloudState.cloudEnabled);
    if (dlnaBadge) {
      dlnaBadge.innerText = window.cloudState.dlna.enabled
        ? `📺 DLNA ON (${window.cloudState.dlna.friendly_name || 'AetherVault Media'})`
        : "📺 DLNA OFF (0% CPU)";
      dlnaBadge.style.borderColor = window.cloudState.dlna.enabled ? "#10b981" : "var(--border)";
      dlnaBadge.style.color = window.cloudState.dlna.enabled ? "#a7f3d0" : "#9ca3af";
    }
    if (!rootsBox) return;
    rootsBox.innerHTML = (window.cloudState.roots || []).map(r => {
      const active = r.id === window.cloudState.rootId ? "active" : "";
      const rmBtn = !r.builtin ? `<span class="del-btn" onclick="event.stopPropagation(); removeCloudRoot('${escapeHtml(r.id)}')" title="Unmount folder">✖</span>` : "";
      const dlnaTag = r.dlna ? '<span title="Shared over DLNA (Roku/VLC)" style="font-size:0.68rem;">📺</span>' : "";
      return `
        <button class="cloud-root-btn ${active}" onclick="loadCloudDir('${escapeHtml(r.id)}', '')">
          <span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escapeHtml(r.icon || '📁')} ${escapeHtml(r.label)}</span>
          <span style="display:flex;align-items:center;gap:4px;">${dlnaTag}${rmBtn}</span>
        </button>`;
    }).join("");
  }

  window.toggleCloudServices = async function () {
    const dlnaEn = Boolean((document.getElementById("cloud-dlna-toggle") || {}).checked);
    const cloudEn = Boolean((document.getElementById("cloud-server-toggle") || {}).checked);
    const res = await fetch("/api/dlna/toggle", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ dlna_enabled: dlnaEn, cloud_enabled: cloudEn }),
    });
    const d = await res.json();
    if (d.ok) {
      window.cloudState.dlna = d.dlna || { enabled: dlnaEn };
      window.cloudState.cloudEnabled = Boolean(d.cloud_enabled);
      renderCloudRootsAndSwitches();
      if (cloudEn) window.loadCloudDir(window.cloudState.rootId, window.cloudState.relPath);
    }
  };

  window.addCustomCloudRoot = async function () {
    let picked = "";
    try {
      const br = await fetch("/workspace/browse_folder");
      const bd = await br.json();
      if (bd.ok && bd.path) picked = bd.path;
    } catch (e) {}
    if (!picked) picked = prompt("Enter a PC folder path to mount into Vault Cloud & DLNA (e.g. D:/Movies or C:/Users/You/Videos):");
    if (!picked || !picked.trim()) return;
    const res = await fetch("/api/cloud_files/roots/add", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: picked.trim(), cloud: true, dlna: true }),
    });
    const d = await res.json();
    if (!d.ok) return alert(d.error || "Could not add folder");
    await window.refreshCloudView();
  };

  window.removeCloudRoot = async function (rid) {
    if (!confirm("Unmount this PC folder from Vault Cloud / DLNA? (Does NOT delete any files on disk.)")) return;
    await fetch("/api/cloud_files/roots/remove", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: rid }),
    });
    if (window.cloudState.rootId === rid) window.cloudState.rootId = "vault_files";
    await window.refreshCloudView();
  };

  window.setCloudViewMode = function (mode) {
    window.cloudState.viewMode = mode === "list" ? "list" : "grid";
    window.loadCloudDir(window.cloudState.rootId, window.cloudState.relPath);
  };

  window.loadCloudDir = async function (rootId, relPath) {
    window.cloudState.rootId = rootId || "vault_files";
    window.cloudState.relPath = relPath || "";
    renderCloudRootsAndSwitches();
    const q = ((document.getElementById("cloud-search-input") || {}).value || "").trim();
    const box = document.getElementById("cloud-entries-box");
    const crumbsEl = document.getElementById("cloud-breadcrumbs");
    if (!box) return;
    box.innerHTML = '<div style="color:#9ca3af;padding:12px;">⏳ Loading files...</div>';
    try {
      const res = await fetch(`/api/cloud_files/list?root_id=${encodeURIComponent(window.cloudState.rootId)}&path=${encodeURIComponent(window.cloudState.relPath)}&search=${encodeURIComponent(q)}`);
      const d = await res.json();
      if (!d.ok) {
        box.innerHTML = `<div class="issue-alert">${escapeHtml(d.error || 'Vault Cloud unavailable')}</div>`;
        return;
      }
      if (crumbsEl) {
        crumbsEl.innerHTML = (d.breadcrumbs || []).map((c, idx) =>
          `${idx > 0 ? '<span style="color:#6b7280;"> / </span>' : ''}<button class="secondary small-btn" onclick="loadCloudDir('${escapeHtml(window.cloudState.rootId)}', '${escapeHtml(c.rel_path)}')">${escapeHtml(c.label)}</button>`
        ).join("");
      }
      const items = d.entries || [];
      if (!items.length) {
        box.innerHTML = '<div style="color:#9ca3af;padding:24px;text-align:center;">📂 Folder is empty — drag &amp; drop files anywhere or click <b>⬆️ Upload</b>!</div>';
        return;
      }
      if (window.cloudState.viewMode === "list") {
        box.className = "";
        box.innerHTML = `<div style="display:flex;flex-direction:column;gap:6px;">` + items.map(it => {
          const clickAct = it.is_dir
            ? `loadCloudDir('${escapeHtml(window.cloudState.rootId)}', '${escapeHtml(it.rel_path)}')`
            : `previewCloudEntry('${escapeHtml(window.cloudState.rootId)}', '${escapeHtml(it.rel_path)}', '${escapeHtml(it.name)}', '${escapeHtml(it.kind)}', '${escapeHtml(it.stream_url)}')`;
          const loreBtns = it.can_lore
            ? `<button class="secondary small-btn" onclick="event.stopPropagation(); pinCloudFileToLore('${escapeHtml(window.cloudState.rootId)}', '${escapeHtml(it.rel_path)}', 'core')" title="Pin as 24/7 CORE">🟣</button>
               <button class="secondary small-btn" onclick="event.stopPropagation(); pinCloudFileToLore('${escapeHtml(window.cloudState.rootId)}', '${escapeHtml(it.rel_path)}', 'lore')" title="Add to LORE RAG">🟢</button>` : "";
          const chatBtn = !it.is_dir
            ? `<button class="small-btn" onclick="event.stopPropagation(); attachCloudFileToChat('${escapeHtml(window.cloudState.rootId)}', '${escapeHtml(it.rel_path)}', '${escapeHtml(it.name)}', '${escapeHtml(it.kind)}', '${escapeHtml(it.stream_url)}')" title="Attach to Chat">💬</button>
               <a href="${escapeHtml(it.stream_url)}?download=1" onclick="event.stopPropagation()"><button class="secondary small-btn" title="Download">⬇️</button></a>` : "";
          return `
            <div class="cloud-list-row" onclick="${clickAct}" style="cursor:pointer;">
              <div style="display:flex;align-items:center;gap:8px;min-width:0;flex:1;">
                <span>${iconForKind(it.kind, it.ext)}</span>
                <span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-weight:600;">${escapeHtml(it.name)}</span>
              </div>
              <span style="color:#9ca3af;font-size:0.74rem;white-space:nowrap;">${it.is_dir ? 'Folder' : fmtSize(it.size)}</span>
              <div style="display:flex;gap:4px;">${chatBtn}${loreBtns}<button class="secondary small-btn" onclick="event.stopPropagation(); deleteCloudEntry('${escapeHtml(window.cloudState.rootId)}', '${escapeHtml(it.rel_path)}')" title="Move to Trash">🗑️</button></div>
            </div>`;
        }).join("") + `</div>`;
      } else {
        box.className = "cloud-grid";
        box.innerHTML = items.map(it => {
          const thumb = (!it.is_dir && it.kind === "image")
            ? `<img src="${escapeHtml(it.stream_url)}" loading="lazy" alt="${escapeHtml(it.name)}">`
            : `<span>${iconForKind(it.kind, it.ext)}</span>`;
          const clickAct = it.is_dir
            ? `loadCloudDir('${escapeHtml(window.cloudState.rootId)}', '${escapeHtml(it.rel_path)}')`
            : `previewCloudEntry('${escapeHtml(window.cloudState.rootId)}', '${escapeHtml(it.rel_path)}', '${escapeHtml(it.name)}', '${escapeHtml(it.kind)}', '${escapeHtml(it.stream_url)}')`;
          const actions = it.is_dir ? "" : `
            <div style="display:flex;gap:4px;margin-top:2px;flex-wrap:wrap;" onclick="event.stopPropagation()">
              <button class="small-btn" style="flex:1;" onclick="attachCloudFileToChat('${escapeHtml(window.cloudState.rootId)}', '${escapeHtml(it.rel_path)}', '${escapeHtml(it.name)}', '${escapeHtml(it.kind)}', '${escapeHtml(it.stream_url)}')">💬 Chat</button>
              ${it.can_lore ? `<button class="secondary small-btn" onclick="pinCloudFileToLore('${escapeHtml(window.cloudState.rootId)}', '${escapeHtml(it.rel_path)}', 'lore')" title="Pin to LORE">🟢</button>` : ""}
              <a href="${escapeHtml(it.stream_url)}?download=1"><button class="secondary small-btn" title="Download">⬇️</button></a>
            </div>`;
          return `
            <div class="cloud-card" onclick="${clickAct}">
              <div class="cloud-thumb">${thumb}</div>
              <div style="font-size:0.78rem;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="${escapeHtml(it.name)}">${escapeHtml(it.name)}</div>
              <div style="font-size:0.69rem;color:#9ca3af;display:flex;justify-content:space-between;">
                <span>${it.is_dir ? 'Folder' : fmtSize(it.size)}</span>
                <span class="del-btn" onclick="event.stopPropagation(); deleteCloudEntry('${escapeHtml(window.cloudState.rootId)}', '${escapeHtml(it.rel_path)}')" title="Move to Trash">🗑️</span>
              </div>
              ${actions}
            </div>`;
        }).join("");
      }
    } catch (e) {
      box.innerHTML = `<div class="issue-alert">Error loading Vault Cloud: ${escapeHtml(String(e))}</div>`;
    }
  };

  window.previewCloudEntry = function (rootId, relPath, name, kind, streamUrl) {
    if (kind === "image") { window.openMediaLightbox(streamUrl, name); return; }
    const modal = document.getElementById("cloud-preview-modal");
    const titleEl = document.getElementById("cloud-prev-title");
    const bodyEl = document.getElementById("cloud-prev-body");
    const dlEl = document.getElementById("cloud-prev-dl");
    if (!modal || !bodyEl) { window.open(streamUrl, "_blank"); return; }
    if (titleEl) titleEl.innerText = name;
    if (dlEl) { dlEl.href = streamUrl + "?download=1"; dlEl.download = name; }
    if (kind === "video") {
      bodyEl.innerHTML = `<video src="${escapeHtml(streamUrl)}" controls playsinline autoplay style="width:100%;max-height:70vh;border-radius:10px;background:#000;"></video>
        <div style="font-size:0.74rem;color:#9ca3af;margin-top:8px;">Direct HTTP 206 Byte-Range stream — works on iOS Safari, Android Chrome &amp; VLC.</div>`;
    } else if (kind === "audio") {
      bodyEl.innerHTML = `<audio src="${escapeHtml(streamUrl)}" controls autoplay style="width:100%;margin:20px 0;"></audio>`;
    } else if (name.toLowerCase().endsWith(".pdf")) {
      bodyEl.innerHTML = `<iframe src="${escapeHtml(streamUrl)}" style="width:100%;height:70vh;border:none;border-radius:8px;background:#fff;"></iframe>`;
    } else {
      bodyEl.innerHTML = '<div style="color:#9ca3af;">Loading text preview...</div>';
      fetch(streamUrl).then(r => r.text()).then(t => {
        bodyEl.innerHTML = `<pre style="max-height:68vh;overflow:auto;background:#07080d;padding:12px;border-radius:8px;color:#e5e7eb;font-size:0.78rem;white-space:pre-wrap;">${escapeHtml(t.slice(0, 40000))}</pre>`;
      }).catch(() => { bodyEl.innerText = "Preview unavailable — click Download."; });
    }
    modal.style.display = "flex";
  };

  window.uploadCloudFilesList = async function (files) {
    const arr = Array.from(files || []);
    if (!arr.length) return;
    await runWithActivityFeedback("cloud_up", `Uploading ${arr.length} file(s) to Vault Cloud`, async () => {
      for (const f of arr) {
        const fd = new FormData();
        fd.append("file", f);
        await fetch(`/api/cloud_files/upload?root_id=${encodeURIComponent(window.cloudState.rootId)}&rel_path=${encodeURIComponent(window.cloudState.relPath)}`, {
          method: "POST", body: fd,
        });
      }
      await window.loadCloudDir(window.cloudState.rootId, window.cloudState.relPath);
    });
  };

  window.createCloudFolder = async function () {
    const name = prompt("New folder name:");
    if (!name || !name.trim()) return;
    await fetch("/api/cloud_files/mkdir", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ root_id: window.cloudState.rootId, rel_path: window.cloudState.relPath, name: name.trim() }),
    });
    await window.loadCloudDir(window.cloudState.rootId, window.cloudState.relPath);
  };

  window.deleteCloudEntry = async function (rootId, relPath) {
    if (!confirm(`Move '${relPath}' to Trash / Recycle Bin?`)) return;
    await fetch("/api/cloud_files/delete", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ root_id: rootId, rel_path: relPath }),
    });
    await window.loadCloudDir(window.cloudState.rootId, window.cloudState.relPath);
  };

  window.pinCloudFileToLore = async function (rootId, relPath, mode) {
    await runWithActivityFeedback("cloud_lore", `Pinning to ${mode.toUpperCase()}`, async () => {
      const res = await fetch("/api/cloud_files/to_lore", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ root_id: rootId, rel_path: relPath, mode }),
      });
      const d = await res.json();
      if (!d.ok) throw new Error(d.error || "Failed");
      window.lastPdfStateHash = "";
      await refreshStatus();
    });
  };

  window.showPhoneConnectModal = function () {
    const url = window.cloudState.lanUrl || window.currentLanUrl || window.location.origin;
    const m3u = url.replace(/\/$/, "") + "/cloud/playlist.m3u";
    const modal = document.getElementById("cloud-preview-modal");
    const titleEl = document.getElementById("cloud-prev-title");
    const bodyEl = document.getElementById("cloud-prev-body");
    const dlEl = document.getElementById("cloud-prev-dl");
    if (!modal || !bodyEl) return;
    if (titleEl) titleEl.innerText = "📱 Connect Any Phone, VLC or Roku TV on Wi-Fi";
    if (dlEl) { dlEl.href = m3u; dlEl.download = "AetherVault_Media.m3u"; }
    bodyEl.innerHTML = `
      <div style="display:flex;flex-direction:column;gap:12px;font-size:0.84rem;">
        <div class="card">
          <b>1. iPhone (Safari) &amp; Android (Chrome / Firefox)</b>
          <div style="margin-top:6px;">Connect to the same Wi-Fi and open:</div>
          <div style="display:flex;gap:6px;margin-top:6px;">
            <input readonly value="${escapeHtml(url)}" style="flex:1;font-family:monospace;color:#38bdf8;">
            <button class="small-btn" onclick="navigator.clipboard && navigator.clipboard.writeText('${escapeHtml(url)}')">📋 Copy</button>
          </div>
        </div>
        <div class="card">
          <b>2. Roku TV (Roku Media Player) &amp; VLC Local Network</b>
          <div style="margin-top:6px;color:#cbd5e1;">Flip <b>📺 DLNA ON</b> in Vault Cloud (or ask your companion <i>"turn on DLNA"</i>). Open <b>Roku Media Player</b> on your TV or <b>VLC → Local Network → UPnP</b> and pick <b>AetherVault Media</b>!</div>
          <div style="font-size:0.74rem;color:#fde68a;margin-top:6px;">Tip: On Windows, set your Wi-Fi network profile to <b>Private</b> so Windows Firewall allows local SSDP multicast (UDP 1900).</div>
        </div>
        <div class="card">
          <b>3. VLC Direct Playlist Fallback (.m3u — works even if a router blocks multicast)</b>
          <div style="display:flex;gap:6px;margin-top:6px;">
            <input readonly value="${escapeHtml(m3u)}" style="flex:1;font-family:monospace;color:#a7f3d0;">
            <button class="small-btn" onclick="navigator.clipboard && navigator.clipboard.writeText('${escapeHtml(m3u)}')">📋 Copy .M3U</button>
          </div>
        </div>
      </div>`;
    modal.style.display = "flex";
  };
})();
