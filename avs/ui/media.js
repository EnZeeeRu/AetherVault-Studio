/* avs/ui/media.js — Full-Res Media Lightbox, Multi-File Staging Tray, Drag-Drop & Lossless Cropper */
(function () {
  window.pendingAttachments = [];

  function syncLegacyPendingAttachment() {
    const list = window.pendingAttachments || [];
    if (!list.length) {
      window.pendingAttachment = { name: "", text: "", previewDataUrl: null, mediaUrls: [] };
    } else {
      window.pendingAttachment = {
        name: list.map(a => a.name).join(", "),
        text: list.map(a => a.text || `[Attached: ${a.name}]`).join("\n\n---\n\n"),
        previewDataUrl: (list.find(a => a.mediaUrl || a.previewDataUrl) || {}).mediaUrl
          || (list.find(a => a.previewDataUrl) || {}).previewDataUrl || null,
        mediaUrls: list.filter(a => a.mediaUrl).map(a => a.mediaUrl),
      };
    }
    renderComposerMediaTray();
  }

  function formatBytesShort(b) {
    const n = Number(b || 0);
    if (!n) return "";
    if (n < 1024) return n + " B";
    if (n < 1024 * 1024) return (n / 1024).toFixed(1) + " KB";
    return (n / (1024 * 1024)).toFixed(2) + " MB";
  }

  window.renderComposerMediaTray = function () {
    const tray = document.getElementById("composer-media-tray");
    const legacyBar = document.getElementById("attach-bar");
    if (legacyBar) legacyBar.style.display = "none";
    if (!tray) return;
    const list = window.pendingAttachments || [];
    if (!list.length) {
      tray.style.display = "none";
      tray.innerHTML = "";
      return;
    }
    tray.style.display = "flex";
    tray.innerHTML = list.map((item, idx) => {
      const thumb = item.isImage
        ? `<img src="${escapeHtml(item.mediaUrl || item.previewDataUrl || '')}" alt="${escapeHtml(item.name)}" onclick="openMediaLightbox('${escapeHtml(item.mediaUrl || item.previewDataUrl || '')}', '${escapeHtml(item.name)}')">`
        : `<div class="staging-chip-icon">${item.name.endsWith('.pdf') ? '📕' : (item.name.endsWith('.py') ? '🐍' : '📄')}</div>`;
      const sub = item.parsing
        ? "⏳ Parsing..."
        : (item.isImage
            ? `${item.width && item.height ? item.width + '×' + item.height + 'px' : 'Full-Res Image'}${item.size ? ' · ' + formatBytesShort(item.size) : ''}`
            : `${(item.text || '').length} chars${item.size ? ' · ' + formatBytesShort(item.size) : ''}`);
      return `
        <div class="staging-chip">
          ${thumb}
          <div class="staging-chip-meta">
            <span class="staging-chip-name" title="${escapeHtml(item.name)}">${escapeHtml(item.name)}</span>
            <span class="staging-chip-sub">${escapeHtml(sub)}</span>
          </div>
          <button class="staging-chip-rm" onclick="removePendingAttachment(${idx})" title="Remove">✖</button>
        </div>`;
    }).join("");
  };

  window.removePendingAttachment = function (idx) {
    window.pendingAttachments.splice(idx, 1);
    syncLegacyPendingAttachment();
  };

  window.clearAttachment = function () {
    window.pendingAttachments = [];
    syncLegacyPendingAttachment();
  };

  window.attachFileObject = function (file) {
    if (!file) return;
    const item = {
      name: file.name || ("pasted_" + Date.now() + ".png"),
      size: file.size || 0,
      isImage: (file.type || "").startsWith("image/") || /\.(png|jpe?g|webp|gif|bmp|avif)$/i.test(file.name || ""),
      previewDataUrl: null,
      mediaUrl: null,
      width: 0,
      height: 0,
      text: "",
      parsing: true,
    };
    window.pendingAttachments.push(item);
    syncLegacyPendingAttachment();

    const reader = new FileReader();
    reader.onload = async () => {
      if (item.isImage) item.previewDataUrl = reader.result;
      renderComposerMediaTray();
      try {
        const res = await fetch("/parse_attachment", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ filename: item.name, data_base64: reader.result }),
        });
        const data = await res.json();
        item.text = data.text || `[Attached: ${item.name}]`;
        if (data.media_url) item.mediaUrl = data.media_url;
        if (data.width) item.width = data.width;
        if (data.height) item.height = data.height;
      } catch (e) {
        item.text = `[Attached: ${item.name}]`;
      } finally {
        item.parsing = false;
        syncLegacyPendingAttachment();
      }
    };
    reader.readAsDataURL(file);
  };

  window.attachCloudFileToChat = async function (rootId, relPath, fileName, kind, streamUrl) {
    if (typeof window.switchMainView === "function") window.switchMainView("chat");
    const item = {
      name: fileName,
      size: 0,
      isImage: kind === "image",
      previewDataUrl: kind === "image" ? streamUrl : null,
      mediaUrl: kind === "image" ? streamUrl : null,
      width: 0,
      height: 0,
      text: `[Vault Cloud File: ${rootId}/${relPath}]`,
      parsing: true,
    };
    window.pendingAttachments.push(item);
    syncLegacyPendingAttachment();
    try {
      const resp = await fetch(streamUrl);
      const blob = await resp.blob();
      item.size = blob.size;
      const b64 = await new Promise((resolve) => {
        const r = new FileReader();
        r.onload = () => resolve(r.result);
        r.readAsDataURL(blob);
      });
      const pr = await fetch("/parse_attachment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename: fileName, data_base64: b64 }),
      });
      const pd = await pr.json();
      item.text = pd.text || item.text;
      if (pd.media_url) item.mediaUrl = pd.media_url;
      if (pd.width) item.width = pd.width;
      if (pd.height) item.height = pd.height;
    } catch (e) {}
    item.parsing = false;
    syncLegacyPendingAttachment();
  };

  window.handleAttachment = function (inputEl) {
    const files = Array.from((inputEl && inputEl.files) || []);
    files.forEach(f => window.attachFileObject(f));
    if (inputEl) inputEl.value = "";
  };

  window.openMediaLightbox = function (src, title) {
    const lb = document.getElementById("avs-lightbox");
    const img = document.getElementById("lb-img");
    const meta = document.getElementById("lb-meta");
    const dl = document.getElementById("lb-dl-link");
    if (!lb || !img || !src) return;
    img.classList.remove("zoomed");
    img.src = src;
    if (dl) { dl.href = src; dl.download = title || "aethervault_image.png"; }
    if (meta) meta.innerText = title || "Full-Resolution Preview";
    img.onload = () => {
      if (meta) meta.innerText = `${title || "Image"} — ${img.naturalWidth} × ${img.naturalHeight} px (Original Resolution)`;
    };
    lb.classList.add("open");
  };

  window.closeMediaLightbox = function () {
    const lb = document.getElementById("avs-lightbox");
    if (lb) lb.classList.remove("open");
  };

  window.toggleLightboxZoom = function () {
    const img = document.getElementById("lb-img");
    if (img) img.classList.toggle("zoomed");
  };

  document.addEventListener("click", (e) => {
    const img = e.target && e.target.closest ? e.target.closest(".chat-img") : null;
    if (img && img.src) window.openMediaLightbox(img.src, img.alt || "Chat Image");
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      const lb = document.getElementById("avs-lightbox");
      if (lb && lb.classList.contains("open")) { window.closeMediaLightbox(); return; }
      document.querySelectorAll(".leo-popover.open").forEach(p => p.classList.remove("open"));
    }
  });

  let dragDepth = 0;
  window.addEventListener("dragenter", (e) => {
    if (!(e.dataTransfer && Array.from(e.dataTransfer.types || []).includes("Files"))) return;
    e.preventDefault();
    dragDepth++;
    const ov = document.getElementById("global-drop-overlay");
    if (ov) ov.classList.add("visible");
  });
  window.addEventListener("dragover", (e) => {
    if (e.dataTransfer && Array.from(e.dataTransfer.types || []).includes("Files")) e.preventDefault();
  });
  window.addEventListener("dragleave", () => {
    dragDepth = Math.max(0, dragDepth - 1);
    if (dragDepth === 0) {
      const ov = document.getElementById("global-drop-overlay");
      if (ov) ov.classList.remove("visible");
    }
  });
  window.addEventListener("drop", (e) => {
    dragDepth = 0;
    const ov = document.getElementById("global-drop-overlay");
    if (ov) ov.classList.remove("visible");
    const files = Array.from((e.dataTransfer && e.dataTransfer.files) || []);
    if (!files.length) return;
    e.preventDefault();
    const cloudView = document.getElementById("view-cloud");
    if (cloudView && cloudView.classList.contains("active") && typeof window.uploadCloudFilesList === "function") {
      window.uploadCloudFilesList(files);
    } else {
      files.forEach(f => window.attachFileObject(f));
    }
  });

  window.uploadOriginalAsset = async function (type) {
    const st = (window.cropState || {})[type];
    if (!st || !st.dataUrl) return alert("Choose an image first!");
    const indEl = document.getElementById(type === "avatar" ? "av-file-indicator" : "wall-file-indicator");
    if (indEl) indEl.innerText = `⏳ Saving untouched original ${st.filename}...`;
    const data = await runWithActivityFeedback("orig_" + type, `Saving Lossless Original ${type.toUpperCase()}`, async () => {
      const res = await fetch("/upload_asset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ asset_type: type, filename: st.filename, data_base64: st.dataUrl, use_original: true }),
      });
      return await res.json();
    });
    if (data && data.ok) {
      if (indEl) indEl.innerHTML = `✨ <b style="color:#a7f3d0;">Applied Original (Lossless): ${escapeHtml(st.filename)}!</b>`;
      window.workspaceConfig = data.config;
      applyThemeObject(data.config.theme_colors, data.config.wallpaper_url, data.config.wallpaper_opacity, data.config.avatar_url, data.config.ai_name);
      refreshStatus();
    }
  };

  const _origRenderCrop = window.renderCropPreview;
  if (typeof _origRenderCrop === "function") {
    window.renderCropPreview = function (type) {
      const canvas = document.getElementById(type === "avatar" ? "av-crop-canvas" : "wall-crop-canvas");
      if (canvas) {
        const ctx = canvas.getContext("2d");
        if (ctx) { ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = "high"; }
      }
      const origBtn = document.getElementById(type === "avatar" ? "av-orig-btn" : "wall-orig-btn");
      if (origBtn && window.cropState && window.cropState[type] && window.cropState[type].dataUrl) {
        origBtn.disabled = false;
      }
      return _origRenderCrop(type);
    };
  }
})();
