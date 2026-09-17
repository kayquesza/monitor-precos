"""Envio de notificacoes via Telegram Bot API."""

from __future__ import annotations

import requests

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"
TIMEOUT_SECONDS = 15


def send_message(bot_token: str, chat_id: str, text: str) -> None:
    url = TELEGRAM_API_URL.format(token=bot_token)
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    response = requests.post(url, json=payload, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
