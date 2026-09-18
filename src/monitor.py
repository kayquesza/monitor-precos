"""Monitora canais publicos do Telegram em busca de ofertas dos modelos
configurados e notifica (no Telegram) cada post novo que der match."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from config import CHANNELS, HISTORY_PATH, PRODUCTS, matches_product
from telegram import send_message
from telegram_canais import fetch_channel_posts

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_history(path: Path) -> Dict[str, dict]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_history(path: Path, history: Dict[str, dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def build_match_message(product_name: str, channel: str, post_text: str, post_url: str) -> str:
    excerpt = post_text if len(post_text) <= 500 else post_text[:500] + "..."
    return (
        f"\U0001F4F1 <b>{product_name}</b> - possivel oferta em @{channel}\n\n"
        f"{excerpt}\n\n"
        f"{post_url}"
    )


def main() -> int:
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        print("TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID precisam estar definidos.", file=sys.stderr)
        return 1

    history_path = REPO_ROOT / HISTORY_PATH
    history = load_history(history_path)

    for channel in CHANNELS:
        try:
            posts = fetch_channel_posts(channel)
        except Exception as exc:  # noqa: BLE001 - loga e segue para o proximo canal
            print(f"[{channel}] erro ao buscar posts: {exc}", file=sys.stderr)
            continue

        print(f"[{channel}] {len(posts)} posts encontrados na pagina de preview.")

        for post in posts:
            for product in PRODUCTS:
                if not matches_product(post.text, product):
                    continue

                history_key = f"{post.post_id}::{product['name']}"
                if history_key in history:
                    continue

                message = build_match_message(product["name"], channel, post.text, post.url)
                send_message(bot_token, chat_id, message)
                print(f"[{channel}] notificado: {product['name']} ({post.post_id})")

                history[history_key] = {
                    "channel": channel,
                    "post_id": post.post_id,
                    "product": product["name"],
                    "url": post.url,
                    "notified_at": datetime.now(timezone.utc).isoformat(),
                }

    save_history(history_path, history)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
