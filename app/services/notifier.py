"""
Envío de alertas por Telegram.
"""

import httpx
from app.config import settings


async def send_telegram_message(text: str) -> bool:
    token = settings.telegram_bot_token
    chat_id = settings.telegram_chat_id

    if not token or not chat_id:
        print("[notifier] Telegram no configurado")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return True
    except Exception as e:
        print(f"[notifier] Error enviando Telegram: {e}")
        return False


async def notify_change(summary: str, url: str) -> bool:
    message = (
        f"🔔 <b>Cambio detectado</b>\n\n"
        f"{summary}\n\n"
        f"🔗 <a href=\"{url}\">Ver página</a>"
    )
    return await send_telegram_message(message)