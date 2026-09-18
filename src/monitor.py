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
from telegram import escape_html, send_message
from telegram_canais import fetch_channel_posts

REPO_ROOT = Path(__file__).resolve().parent.parent
HISTORY_MAX_AGE_DAYS = 30


def load_history(path: Path, bot_token: str, chat_id: str) -> Dict[str, dict]:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        print(f"Historico corrompido em {path}: {exc}", file=sys.stderr)
        try:
            send_message(
                bot_token,
                chat_id,
                build_alert_message(
                    [f"{escape_html(str(path))} esta corrompido ({escape_html(str(exc))}) - reiniciando historico vazio"]
                ),
            )
        except Exception as send_exc:  # noqa: BLE001 - nao deixa a notificacao de alerta derrubar o run
            print(f"Falha ao enviar alerta de historico corrompido: {send_exc}", file=sys.stderr)
        return {}


def save_history(path: Path, history: Dict[str, dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(path.name + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)


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
        f"\U0001F4F1 <b>{escape_html(product_name)}</b> - possivel oferta em @{escape_html(channel)}\n"
        f"\U0001F553 Publicado em: {published_str}\n\n"
        f"{escape_html(excerpt)}\n\n"
        f"{escape_html(post_url)}"
    )


def build_alert_message(issues: list[str]) -> str:
    # `issues` ja vem com as partes dinamicas (canal, mensagem de excecao)
    # escapadas na origem - aqui so montamos o texto fixo ao redor.
    bullet_list = "\n".join(f"- {issue}" for issue in issues)
    return f"⚠️ <b>Alerta do monitor de precos</b>\n\n{bullet_list}"


def main() -> int:
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        print("TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID precisam estar definidos.", file=sys.stderr)
        return 1

    history_path = REPO_ROOT / HISTORY_PATH
    history = load_history(history_path, bot_token, chat_id)
    channel_issues: list[str] = []

    for channel in CHANNELS:
        try:
            posts = fetch_channel_posts(channel)
        except Exception as exc:  # noqa: BLE001 - loga e segue para o proximo canal
            print(f"[{channel}] erro ao buscar posts: {exc}", file=sys.stderr)
            channel_issues.append(f"@{escape_html(channel)}: erro ao buscar posts ({escape_html(str(exc))})")
            continue

        print(f"[{channel}] {len(posts)} posts encontrados na pagina de preview.")

        if not posts:
            print(f"[{channel}] nenhum post retornado.", file=sys.stderr)
            channel_issues.append(f"@{escape_html(channel)}: retornou 0 posts")

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
                try:
                    send_message(bot_token, chat_id, message)
                except Exception as exc:  # noqa: BLE001 - loga e segue para o proximo post
                    print(
                        f"[{channel}] erro ao notificar {product['name']} ({post.post_id}): {exc}",
                        file=sys.stderr,
                    )
                    # nao marca como notificado - tenta de novo na proxima execucao
                    continue

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
        try:
            send_message(bot_token, chat_id, build_alert_message(channel_issues))
            print(f"Alerta enviado para {len(channel_issues)} canal(is) com problema.", file=sys.stderr)
        except Exception as exc:  # noqa: BLE001 - nao deixa isso impedir o save_history abaixo
            print(f"Erro ao enviar alerta de canais com problema: {exc}", file=sys.stderr)

    history = prune_old_history(history)
    save_history(history_path, history)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
