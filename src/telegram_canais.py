"""Leitura de posts publicos de canais do Telegram via t.me/s/{canal}.

Essa pagina de preview nao exige login nem token: e a mesma usada para
embutir posts de canais publicos em sites externos.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import requests
from bs4 import BeautifulSoup

PREVIEW_URL = "https://t.me/s/{channel}"
TIMEOUT_SECONDS = 20
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
}


@dataclass
class Post:
    channel: str
    post_id: str  # ex: "escolhasegura/22842" (data-post do Telegram, unico por canal)
    text: str
    url: str
    published_at: str | None  # ISO 8601 (ex: "2026-09-18T14:12:02+00:00"), do atributo datetime da <time>


def fetch_channel_posts(channel: str) -> List[Post]:
    """Busca os posts atualmente visiveis na pagina de preview do canal."""
    url = PREVIEW_URL.format(channel=channel)
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    posts: List[Post] = []

    for message_div in soup.select("div.tgme_widget_message[data-post]"):
        post_id = message_div["data-post"]

        text_div = message_div.select_one("div.tgme_widget_message_text")
        if text_div is None:
            continue  # post sem texto (ex: apenas foto/video) - nada para filtrar

        text = text_div.get_text(separator="\n", strip=True)

        time_tag = message_div.select_one("time[datetime]")
        published_at = time_tag["datetime"] if time_tag else None

        posts.append(
            Post(
                channel=channel,
                post_id=post_id,
                text=text,
                url=f"https://t.me/{post_id}",
                published_at=published_at,
            )
        )

    return posts
