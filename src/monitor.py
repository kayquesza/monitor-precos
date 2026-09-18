"""Monitora canais publicos do Telegram em busca de ofertas dos modelos
configurados e notifica (no Telegram) cada post novo que der match."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict
from zoneinfo import ZoneInfo

from config import CHANNELS, HISTORY_PATH, PRODUCTS, matches_product
from telegram import send_message
from telegram_canais import fetch_channel_posts

REPO_ROOT = Path(__file__).resolve().parent.parent
HISTORY_MAX_AGE_DAYS = 30


def load_history(path: Path) -> Dict[str, dict]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_history(path: Path, history: Dict[str, dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def prune_old_history(history: Dict[str, dict], max_age_days: int = HISTORY_MAX_AGE_DAYS) -> Dict[str, dict]:
    """Remove entradas com mais de max_age_days, com base em 'notified_at'.

    Mantemos so o suficiente para nao notificar o mesmo post duas vezes -
    nao precisamos do historico completo para sempre.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    kept = {}
    for key, entry in history.items():
        notified_at = entry.get("notified_at")
        if not notified_at:
            kept[key] = entry
            continue
        if datetime.fromisoformat(notified_at) >= cutoff:
            kept[key] = entry
    return kept


def format_published_at(published_at: str | None) -> str:
    if not published_at:
        return "data de publicacao desconhecida"
    dt = datetime.fromisoformat(published_at)
    dt_br = dt.astimezone(ZoneInfo("America/Sao_Paulo"))
    return dt_br.strftime("%d/%m/%Y %H:%M")


def build_match_message(
    product_name: str, channel: str, post_text: str, post_url: str, published_at: str | None
) -> str:
    excerpt = post_text if len(post_text) <= 500 else post_text[:500] + "..."
    published_str = format_published_at(published_at)
    return (
        f"\U0001F4F1 <b>{product_name}</b> - possivel oferta em @{channel}\n"
        f"\U0001F553 Publicado em: {published_str}\n\n"
        f"{excerpt}\n\n"
        f"{post_url}"
    )


def build_alert_message(issues: list[str]) -> str:
    bullet_list = "\n".join(f"- {issue}" for issue in issues)
    return f"⚠️ <b>Alerta do monitor de precos</b>\n\n{bullet_list}"


def main() -> int:
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        print("TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID precisam estar definidos.", file=sys.stderr)
        return 1

    history_path = REPO_ROOT / HISTORY_PATH
    history = load_history(history_path)
    channel_issues: list[str] = []

    for channel in CHANNELS:
        try:
            posts = fetch_channel_posts(channel)
        except Exception as exc:  # noqa: BLE001 - loga e segue para o proximo canal
            print(f"[{channel}] erro ao buscar posts: {exc}", file=sys.stderr)
            channel_issues.append(f"@{channel}: erro ao buscar posts ({exc})")
            continue

        print(f"[{channel}] {len(posts)} posts encontrados na pagina de preview.")

        if not posts:
            print(f"[{channel}] nenhum post retornado.", file=sys.stderr)
            channel_issues.append(f"@{channel}: retornou 0 posts")

        for post in posts:
            for product in PRODUCTS:
                if not matches_product(post.text, product):
                    continue

                history_key = f"{post.post_id}::{product['name']}"
                if history_key in history:
                    continue

                message = build_match_message(
                    product["name"], channel, post.text, post.url, post.published_at
                )
                send_message(bot_token, chat_id, message)
                print(f"[{channel}] notificado: {product['name']} ({post.post_id})")

                history[history_key] = {
                    "channel": channel,
                    "post_id": post.post_id,
                    "product": product["name"],
                    "url": post.url,
                    "published_at": post.published_at,
                    "notified_at": datetime.now(timezone.utc).isoformat(),
                }

    if channel_issues:
        send_message(bot_token, chat_id, build_alert_message(channel_issues))
        print(f"Alerta enviado para {len(channel_issues)} canal(is) com problema.", file=sys.stderr)

    history = prune_old_history(history)
    save_history(history_path, history)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
