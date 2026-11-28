/* avs/ui/composer.js — Brave Leo Floating Composer, Custom /Skills, Unified +/📎 Menu & View Switcher */
(function () {
  window.customSkillsList = [];
  window.activeMainView = "chat";

  window.switchMainView = function (viewName) {
    window.activeMainView = viewName || "chat";
    const chatBox = document.getElementById("chat-box");
    const leoWrap = document.getElementById("leo-composer-wrap");
    const spellBar = document.getElementById("spellcheck-bar");
    const cloudView = document.getElementById("view-cloud");
    const tgView = document.getElementById("view-telegram");

    const isChat = (viewName === "chat");
    if (chatBox) chatBox.style.display = isChat ? "flex" : "none";
    if (leoWrap) leoWrap.style.display = isChat ? "flex" : "none";
    if (spellBar && !isChat) spellBar.style.display = "none";
    if (cloudView) cloudView.classList.toggle("active", viewName === "cloud");
    if (tgView) tgView.classList.toggle("active", viewName === "telegram");

    document.querySelectorAll(".avs-view-btn").forEach(b => {
      b.classList.toggle("active", b.getAttribute("data-view") === viewName);
    });
    if (viewName === "cloud" && typeof window.refreshCloudView === "function") window.refreshCloudView();
    if (viewName === "telegram" && typeof window.renderTelegramMirror === "function") window.renderTelegramMirror();
    if (typeof closeAllMobileSidebars === "function") closeAllMobileSidebars();
  };

  window.toggleDesktopStudioDrawer = function () {
    document.body.classList.toggle("studio-drawer-collapsed");
    const collapsed = document.body.classList.contains("studio-drawer-collapsed");
    try { localStorage.setItem("avs_drawer_collapsed", collapsed ? "1" : "0"); } catch (e) {}
    const btn = document.getElementById("desktop-drawer-toggle-btn");
    if (btn) btn.innerText = collapsed ? "🎛️ Show Controls" : "🎛️ Hide Controls";
  };

  window.toggleLeoPopover = function (popId, evt) {
    if (evt) evt.stopPropagation();
    const target = document.getElementById(popId);
    if (!target) return;
    const willOpen = !target.classList.contains("open");
    document.querySelectorAll(".leo-popover.open").forEach(p => p.classList.remove("open"));
    if (willOpen) {
      target.classList.add("open");
      if (popId === "leo-skills-popover") loadAndRenderSkillsMenu();
    }
  };

  document.addEventListener("click", (e) => {
    if (!e.target.closest || !e.target.closest("#leo-composer")) {
      document.querySelectorAll(".leo-popover.open").forEach(p => p.classList.remove("open"));
    }
  });

  window.loadAndRenderSkillsMenu = async function () {
    try {
      const res = await fetch("/api/skills");
      const data = await res.json();
      if (data.ok && Array.isArray(data.skills)) window.customSkillsList = data.skills;
    } catch (e) {}
    const box = document.getElementById("leo-skills-scroll");
    if (!box) return;
    const byCat = {};
    (window.customSkillsList || []).forEach(s => {
      const cat = s.category || "Quick Actions";
      if (!byCat[cat]) byCat[cat] = [];
      byCat[cat].push(s);
    });
    let html = "";
    Object.keys(byCat).forEach(cat => {
      html += `<div class="leo-pop-cat">${escapeHtml(cat)}</div>`;
      byCat[cat].forEach(s => {
        const sid = escapeHtml(s.id).replace(/'/g, "&#39;");
        html += `
          <div class="leo-pop-item" onclick="applyCustomSkill('${sid}')">
            <span>${escapeHtml(s.label)}</span>
            <span class="del-btn" onclick="event.stopPropagation(); deleteCustomSkill('${sid}')" title="Remove shortcut">×</span>
          </div>`;
      });
    });
    box.innerHTML = html || '<div style="padding:10px;color:#9ca3af;font-size:0.78rem;">No quick actions yet. Click + New below!</div>';
  };

  window.applyCustomSkill = function (skillId) {
    const sk = (window.customSkillsList || []).find(s => s.id === skillId);
    document.querySelectorAll(".leo-popover.open").forEach(p => p.classList.remove("open"));
    if (!sk) return;
    const inp = document.getElementById("user-input");
    if (!inp) return;
    const cur = inp.value.trim();
    if (sk.prompt.endsWith("\n\n")) {
      inp.value = cur ? (sk.prompt + cur) : sk.prompt;
      inp.focus();
      if (typeof autoResizeChatInput === "function") autoResizeChatInput(inp);
    } else {
      inp.value = sk.prompt;
      if (typeof sendMessage === "function") sendMessage();
    }
  };

  window.createCustomSkillPrompt = async function () {
    const label = prompt("Quick Action name (e.g. 'Dialogue Polish', 'Check Lore'):");
    if (!label || !label.trim()) return;
    const category = prompt("Category (e.g. 'Lore & Writing', 'Rewrite', 'PC & Media'):", "Lore & Writing") || "Custom";
    const promptTxt = prompt("Prompt text (end with space/newline to wrap your input, or write a standalone command):", "Polish this dialogue in-character:\n\n");
    if (!promptTxt || !promptTxt.trim()) return;
    await fetch("/api/skills/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ label: label.trim(), category: category.trim(), prompt: promptTxt }),
    });
    await loadAndRenderSkillsMenu();
  };

  window.deleteCustomSkill = async function (skillId) {
    await fetch("/api/skills/delete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: skillId }),
    });
    await loadAndRenderSkillsMenu();
  };

  window.renderWelcomeStageIfEmpty = function () {
    const box = document.getElementById("chat-box");
    if (!box || box.children.length > 1) return;
    if (box.querySelector(".avs-welcome-stage")) return;
    const aiName = (window.workspaceConfig || {}).ai_name || "Aether";
    const stage = document.createElement("div");
    stage.className = "avs-welcome-stage";
    stage.innerHTML = `
      <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;">
        <div style="display:flex;align-items:center;gap:10px;">
          <img src="/logo.svg" style="width:34px;height:34px;" alt="AVS">
          <div>
            <div style="font-weight:700;font-size:1rem;color:#fff;">Welcome to ${escapeHtml(aiName)} • Lamppost Studio</div>
            <div style="font-size:0.76rem;color:#9ca3af;">No manual required — click any card below or drop images, PDFs, or code anywhere to begin.</div>
          </div>
        </div>
        <button class="secondary small-btn" onclick="this.closest('.avs-welcome-stage').remove()">Hide</button>
      </div>
      <div class="avs-starter-grid">
        <div class="avs-starter-card" onclick="openUserCardInSettings(false)">
          <div style="font-weight:700;font-size:0.82rem;color:var(--accent-soft);">🧬 Shape Companion &amp; Lore</div>
          <div style="font-size:0.73rem;color:#9ca3af;margin-top:3px;">Set persona, avatar portrait, wallpaper &amp; CORE/LORE files.</div>
        </div>
        <div class="avs-starter-card" onclick="switchMainView('cloud')">
          <div style="font-weight:700;font-size:0.82rem;color:#38bdf8;">☁️ Vault Cloud &amp; Roku DLNA</div>
          <div style="font-size:0.73rem;color:#9ca3af;margin-top:3px;">Browse PC files over Wi-Fi, share QR to phones &amp; stream to Roku/VLC.</div>
        </div>
        <div class="avs-starter-card" onclick="openStudioModal('tab-integrations')">
          <div style="font-weight:700;font-size:0.82rem;color:#34d399;">✈️ Pair Telegram &amp; Stickers</div>
          <div style="font-size:0.73rem;color:#9ca3af;margin-top:3px;">3-step guided setup with live token test, 1-click Chat ID &amp; sticker packs.</div>
        </div>
        <div class="avs-starter-card" onclick="openStudioModal('tab-smartapi')">
          <div style="font-weight:700;font-size:0.82rem;color:#fbbf24;">🧠 Local GGUF or Smart APIs</div>
          <div style="font-size:0.73rem;color:#9ca3af;margin-top:3px;">Run Gemma 4 offline or connect free Gemini/Groq keys with auto-failsafe.</div>
        </div>
      </div>`;
    box.appendChild(stage);
  };

  setInterval(() => {
    const mPill = document.getElementById("leo-model-pill");
    const modePill = document.getElementById("leo-mode-pill");
    const topModel = document.getElementById("active-model-label");
    if (mPill && topModel) {
      const clean = (topModel.innerText || "Automatic").replace(/^(🧠 Model:|☁️ API:)\s*/, "").trim();
      mPill.innerText = (clean || "Automatic").slice(0, 24) + " ▾";
    }
    if (modePill) {
      modePill.innerText = (window.currentWorkspaceMode === "roleplay") ? "🎭 Roleplay" : "🛠️ Assistant";
    }
  }, 1500);

  try {
    if (localStorage.getItem("avs_drawer_collapsed") === "1") {
      document.body.classList.add("studio-drawer-collapsed");
      const btn = document.getElementById("desktop-drawer-toggle-btn");
      if (btn) btn.innerText = "🎛️ Show Controls";
    }
  } catch (e) {}
})();
