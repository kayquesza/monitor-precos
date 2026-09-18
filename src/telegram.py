"""Envio de notificacoes via Telegram Bot API."""

from __future__ import annotations

import html

import requests

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"
TIMEOUT_SECONDS = 15


def escape_html(text: str) -> str:
    """Escapa &, < e > para uso seguro em mensagens com parse_mode="HTML".

    Chame isso em qualquer trecho de texto dinamico/externo (post de canal,
    mensagem de excecao, etc.) antes de monta-lo dentro da string final -
    nao chame na string final inteira, pois isso escaparia tambem as tags
    <b> etc. que a propria mensagem usa de proposito.
    """
    return html.escape(text, quote=False)


def send_message(bot_token: str, chat_id: str, text: str) -> None:
    url = TELEGRAM_API_URL.format(token=bot_token)
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    response = requests.post(url, json=payload, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
