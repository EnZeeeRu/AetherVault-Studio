/* avs/ui/telegram.js — Separated Telegram Mirror (+ Fork to Web Chat), Guided 3-Step Setup & Stickers Config */
(function () {
  window.activeTgMirrorSession = "";
  window.tgStickersConfig = { enabled: true, cooldown_turns: 3, stickers: [] };

  window.filterWebSessionsOnly = function (sessions) {
    return (sessions || []).filter(s => !String(s.id || "").startsWith("telegram_") && !String(s.id || "").startsWith("bsky_"));
  };
  window.filterTelegramSessionsOnly = function (sessions) {
    return (sessions || []).filter(s => String(s.id || "").startsWith("telegram_"));
  };

  window.renderTelegramMirror = async function (selectSid) {
    const listEl = document.getElementById("tg-mirror-list");
    const feedEl = document.getElementById("tg-mirror-feed");
    const hdrEl = document.getElementById("tg-mirror-title");
    if (!listEl || !feedEl) return;

    const allSessions = window.latestAllSessions || [];
    const tgSessions = window.filterTelegramSessionsOnly(allSessions);
    if (!tgSessions.length) {
      listEl.innerHTML = '<div style="font-size:0.78rem;color:#9ca3af;padding:8px;">No Telegram chats yet.<br>Connect your bot in <b>Settings → Bridges</b> and send <code>/start</code> on your phone!</div>';
      feedEl.innerHTML = `<div class="avs-welcome-stage">
        <h3 style="margin-bottom:6px;">✈️ Telegram Mirror (Read-Only)</h3>
        <p style="font-size:0.82rem;color:#cbd5e1;margin:0 0 10px 0;">Telegram conversations live here instead of cluttering your interactive desktop chats. Pair your bot in 3 clicks — no manual required!</p>
        <button class="small-btn" onclick="openStudioModal('tab-integrations')">🔌 Open Guided Telegram Setup</button>
      </div>`;
      return;
    }

    const active = selectSid || window.activeTgMirrorSession || tgSessions[0].id;
    window.activeTgMirrorSession = active;
    listEl.innerHTML = tgSessions.map(s => `
      <button class="cloud-root-btn ${s.id === active ? 'active' : ''}" onclick="renderTelegramMirror('${escapeHtml(s.id)}')">
        <span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">✈️ ${escapeHtml((s.title || s.id).replace(/^📱\s*/, ''))}</span>
      </button>`).join("");

    const activeObj = tgSessions.find(s => s.id === active) || tgSessions[0];
    if (hdrEl) hdrEl.innerText = `✈️ ${activeObj.title || activeObj.id} (Read-Only Mirror)`;

    feedEl.innerHTML = '<div style="color:#9ca3af;padding:12px;">⏳ Loading Telegram conversation...</div>';
    try {
      const res = await fetch(`/session/${encodeURIComponent(active)}`);
      const data = await res.json();
      const msgs = data.messages || [];
      feedEl.innerHTML = msgs.map(m => {
        const isU = m.role === "user";
        const tr = m.thought_trace || null;
        const imgHtml = (tr && tr.image_url) ? `<br><img src="${escapeHtml(tr.image_url)}" class="chat-img">` : "";
        return `
          <div class="msg-row ${isU ? 'user-row' : 'assistant-row'}" style="margin-bottom:10px;">
            <div class="msg ${isU ? 'user' : 'assistant'}">
              <div class="msg-reply-text">${renderMarkdownAndArtifacts(m.content || '')}</div>${imgHtml}
            </div>
          </div>`;
      }).join("") || '<div style="color:#9ca3af;">No messages in this thread yet.</div>';
    } catch (e) {
      feedEl.innerHTML = `<div class="issue-alert">Could not load Telegram thread: ${escapeHtml(String(e))}</div>`;
    }
  };

  window.forkActiveTelegramChat = async function () {
    const sid = window.activeTgMirrorSession;
    if (!sid) return alert("Select a Telegram thread first.");
    const res = await fetch("/api/telegram/fork_session", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sid }),
    });
    const d = await res.json();
    if (d.ok && d.session_id) {
      if (typeof window.switchMainView === "function") window.switchMainView("chat");
      await loadSession(d.session_id);
      await refreshStatus();
    }
  };

  window.testTelegramBotToken = async function () {
    const tok = ((document.getElementById("cfg-tg-token") || {}).value || "").trim();
    const box = document.getElementById("tg-wizard-status");
    if (box) { box.style.display = "block"; box.innerText = "⏳ Testing connection with Telegram getMe..."; }
    try {
      const res = await fetch("/api/telegram/test", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bot_token: tok }),
      });
      const d = await res.json();
      if (box) {
        box.innerHTML = d.ok
          ? `✅ <b style="color:#a7f3d0;">${escapeHtml(d.message)}</b> — Now click <b>🎯 Detect My Chat ID</b> or save settings!`
          : `⚠️ <span style="color:#fca5a5;">${escapeHtml(d.error || 'Token check failed')}</span>`;
      }
    } catch (e) { if (box) box.innerText = "❌ " + e; }
  };

  window.detectTelegramChatId = async function () {
    const tok = ((document.getElementById("cfg-tg-token") || {}).value || "").trim();
    const box = document.getElementById("tg-wizard-status");
    if (box) { box.style.display = "block"; box.innerText = "🎯 Listening! Open Telegram and send /start to your bot now..."; }
    const res = await fetch("/api/telegram/detect_id", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ bot_token: tok }),
    });
    const d = await res.json();
    if (d.chat_id) {
      const inp = document.getElementById("cfg-tg-chatid");
      if (inp) inp.value = d.chat_id;
      if (box) box.innerHTML = `✅ <b style="color:#a7f3d0;">Detected Chat ID: ${escapeHtml(d.chat_id)}!</b> Filled automatically — hit Save Integration Settings to lock your bot to you.`;
      return;
    }
    let tries = 0;
    const poller = setInterval(async () => {
      tries++;
      if (tries > 25) { clearInterval(poller); return; }
      try {
        const sr = await fetch("/status");
        const sd = await sr.json();
        if (sd.telegram_detected_chat_id) {
          clearInterval(poller);
          const inp = document.getElementById("cfg-tg-chatid");
          if (inp) inp.value = sd.telegram_detected_chat_id;
          if (box) box.innerHTML = `✅ <b style="color:#a7f3d0;">Paired Chat ID: ${escapeHtml(sd.telegram_detected_chat_id)}!</b> Click Save to lock bot to only you.`;
        }
      } catch (e) {}
    }, 2000);
  };

  window.loadTelegramStickersUI = async function () {
    try {
      const res = await fetch("/api/telegram/stickers");
      const d = await res.json();
      if (d.ok && d.config) {
        window.tgStickersConfig = d.config;
        const en = document.getElementById("cfg-tg-stickers-enabled");
        const cd = document.getElementById("cfg-tg-sticker-cooldown");
        if (en) en.checked = d.config.enabled !== false;
        if (cd) cd.value = String(d.config.cooldown_turns ?? 3);
        renderStickerRows();
      }
    } catch (e) {}
  };

  function renderStickerRows() {
    const list = document.getElementById("tg-stickers-list");
    if (!list) return;
    const items = (window.tgStickersConfig.stickers || []);
    if (!items.length) {
      list.innerHTML = '<div style="font-size:0.74rem;color:#9ca3af;">No stickers configured yet. Paste a <code>t.me/addstickers/PackName</code> link above or send <code>/addsticker smug</code> to your bot!</div>';
      return;
    }
    list.innerHTML = items.map((s, idx) => `
      <div class="item-row" style="gap:6px;">
        <input type="checkbox" ${s.enabled !== false ? 'checked' : ''} onchange="tgStickersConfig.stickers[${idx}].enabled=this.checked; saveTelegramStickersUI()">
        <span style="font-size:1rem;">${escapeHtml(s.emoji || '✨')}</span>
        <input value="${escapeHtml(s.mood || '')}" placeholder="mood (e.g. smug)" style="width:115px;padding:3px 6px;font-size:0.74rem;" onchange="tgStickersConfig.stickers[${idx}].mood=this.value; saveTelegramStickersUI()">
        <span style="flex:1;font-family:monospace;font-size:0.68rem;color:#9ca3af;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escapeHtml(s.pack || 'custom')} · ${escapeHtml((s.file_id || '').slice(0, 14))}…</span>
        <span class="del-btn" onclick="tgStickersConfig.stickers.splice(${idx},1); saveTelegramStickersUI()">✖</span>
      </div>`).join("");
  }

  window.saveTelegramStickersUI = async function () {
    const en = document.getElementById("cfg-tg-stickers-enabled");
    const cd = document.getElementById("cfg-tg-sticker-cooldown");
    window.tgStickersConfig.enabled = en ? en.checked : true;
    window.tgStickersConfig.cooldown_turns = cd ? parseInt(cd.value, 10) : 3;
    const res = await fetch("/api/telegram/stickers/save", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(window.tgStickersConfig),
    });
    const d = await res.json();
    if (d.ok && d.config) { window.tgStickersConfig = d.config; renderStickerRows(); }
  };

  window.importTelegramStickerPack = async function () {
    const pack = ((document.getElementById("tg-sticker-pack-input") || {}).value || "").trim();
    const tok = ((document.getElementById("cfg-tg-token") || {}).value || "").trim();
    const box = document.getElementById("tg-wizard-status");
    if (!pack) return alert("Paste a Telegram sticker pack link (t.me/addstickers/...) or pack name first!");
    if (box) { box.style.display = "block"; box.innerText = `⏳ Importing sticker pack '${pack}' from Telegram...`; }
    const res = await fetch("/api/telegram/stickers/import_pack", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pack, bot_token: tok }),
    });
    const d = await res.json();
    if (d.ok) {
      window.tgStickersConfig = d.config;
      renderStickerRows();
      if (box) box.innerHTML = `✅ <b style="color:#a7f3d0;">${escapeHtml(d.message)}</b>`;
    } else if (box) {
      box.innerHTML = `⚠️ <span style="color:#fca5a5;">${escapeHtml(d.error || 'Import failed')}</span>`;
    }
  };

  window.armTelegramStickerCapture = async function () {
    const mood = prompt("Enter the mood/emotion tag for the next sticker you send to your bot (e.g. smug, laugh, facepalm, hype):", "smug");
    if (!mood || !mood.trim()) return;
    await fetch("/api/telegram/stickers/capture_mode", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mood: mood.trim() }),
    });
    alert(`🎯 Armed! Open Telegram and send any sticker to your bot — it will automatically save under '${mood.trim()}'.`);
  };

  window.showQuickTip = function (title, text) {
    upsertPersistentToast("quick_tip", "toast-working", `💡 ${escapeHtml(title)}`, `${escapeHtml(text)} <i>(Click ✖ to dismiss)</i>`, false);
  };
})();
