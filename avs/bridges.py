"""External bridge & background worker helpers for AetherVault Studio (v6.4 Bluesky Edition)."""
import re
from urllib.parse import quote

MAX_BSKY_CHARS = 300
MAX_TG_CHUNK = 3950


def format_bluesky_post(text: str, max_chars: int = MAX_BSKY_CHARS) -> str:
    """Normalizes whitespace and enforces Bluesky's 300-character post limit cleanly."""
    clean = re.sub(r"\s+", " ", (text or "").strip())
    limit = max(60, int(max_chars))
    if len(clean) <= limit:
        return clean
    return clean[: max(1, limit - 3)].rstrip() + "..."


def build_bluesky_post_record(text: str, created_at_iso: str, reply_uri: str = "", reply_cid: str = "") -> dict:
    """Builds an AT Protocol app.bsky.feed.post record with optional reply threading."""
    record: dict = {
        "$type": "app.bsky.feed.post",
        "text": format_bluesky_post(text),
        "createdAt": created_at_iso,
        "langs": ["en"],
    }
    if reply_uri and reply_cid:
        ref = {"uri": reply_uri, "cid": reply_cid}
        record["reply"] = {"root": ref, "parent": ref}
    return record


def chunk_telegram_message(text: str, chunk_size: int = MAX_TG_CHUNK) -> list[str]:
    """Splits long Telegram replies into bounded chunks without exceeding API limits."""
    clean = text or "✅ Done."
    step = max(200, int(chunk_size))
    if len(clean) <= step:
        return [clean]
    chunks: list[str] = []
    for idx in range(0, len(clean), step):
        chunks.append(clean[idx : idx + step])
    return chunks


def normalize_telegram_command(raw_text: str) -> str:
    """Strips @BotUsername suffix from slash commands while preserving arguments."""
    txt = (raw_text or "").strip()
    if not txt.startswith("/"):
        return txt
    parts = txt.split(None, 1)
    parts[0] = parts[0].split("@", 1)[0]
    return " ".join(parts)


def build_telegram_control_rows(lan_url: str, miniapp_url: str = "") -> list[list[dict]]:
    """Builds the inline control panel button layout for Telegram."""
    rows: list[list[dict]] = [
        [
            {"text": "📊 Status", "callback_data": "avs_cmd:/status"},
            {"text": "🖥️ Specs", "callback_data": "avs_cmd:/specs"},
            {"text": "📥 Queue", "callback_data": "avs_cmd:/queue"},
        ],
        [
            {"text": "💤 Unload RAM", "callback_data": "avs_cmd:/unload"},
            {"text": "⚡ Wake Model", "callback_data": "avs_cmd:/wake"},
            {"text": "⏹️ Stop", "callback_data": "avs_cmd:/stop"},
        ],
        [
            {"text": "📸 Screenshot", "callback_data": "avs_tool:screenshot"},
            {"text": "🎵 Now Playing", "callback_data": "avs_tool:spotify_current"},
            {"text": "🔄 OTA Update", "callback_data": "avs_cmd:/update"},
        ],
    ]
    if (miniapp_url or "").strip().startswith("https://"):
        rows.append([{"text": "🚀 Open Studio Mini App", "web_app": {"url": miniapp_url.strip()}}])
    else:
        rows.append([{"text": f"📱 Wi-Fi LAN: {lan_url}", "callback_data": "avs_info:lan"}])
    return rows


def build_spotify_search_uri(query: str) -> str:
    """Returns a safe spotify:search URI for desktop fallback."""
    clean_q = (query or "").strip() or "lo-fi chill beats"
    return f"spotify:search:{quote(clean_q)}"
