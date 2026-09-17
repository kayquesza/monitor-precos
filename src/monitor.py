"""Monitora precos de celulares no Mercado Livre e notifica quedas via Telegram."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Dict

from config import PRICE_HISTORY_PATH, PRODUCTS, SEARCH_LIMIT, SITE_ID
from mercado_livre import find_cheapest_listing
from telegram import send_message

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


def build_drop_message(product_name: str, old_price: float, new_price: float, permalink: str) -> str:
    discount = 100 * (old_price - new_price) / old_price
    return (
        f"\U0001F4C9 <b>Queda de preco: {product_name}</b>\n"
        f"De R$ {old_price:.2f} para R$ {new_price:.2f} (-{discount:.1f}%)\n"
        f"{permalink}"
    )


def main() -> int:
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        print("TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID precisam estar definidos.", file=sys.stderr)
        return 1

    history_path = REPO_ROOT / PRICE_HISTORY_PATH
    history = load_history(history_path)

    for product in PRODUCTS:
        name = product["name"]
        query = product["query"]

        try:
            listing = find_cheapest_listing(query, site_id=SITE_ID, limit=SEARCH_LIMIT)
        except Exception as exc:  # noqa: BLE001 - loga e segue para o proximo produto
            print(f"[{name}] erro ao consultar Mercado Livre: {exc}", file=sys.stderr)
            continue

        if listing is None:
            print(f"[{name}] nenhum anuncio encontrado para a busca '{query}'.")
            continue

        previous = history.get(name)
        print(f"[{name}] menor preco atual: R$ {listing.price:.2f} ({listing.permalink})")

        if previous is not None and listing.price < previous["price"]:
            message = build_drop_message(name, previous["price"], listing.price, listing.permalink)
            send_message(bot_token, chat_id, message)
            print(f"[{name}] notificacao enviada: queda de preco detectada.")

        history[name] = {
            "price": listing.price,
            "title": listing.title,
            "permalink": listing.permalink,
        }

    save_history(history_path, history)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
