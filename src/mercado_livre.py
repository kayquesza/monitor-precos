"""Cliente simples para a API publica de busca do Mercado Livre."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import requests

SEARCH_URL = "https://api.mercadolibre.com/sites/{site_id}/search"
TIMEOUT_SECONDS = 15


@dataclass
class Listing:
    item_id: str
    title: str
    price: float
    permalink: str


def find_cheapest_listing(query: str, site_id: str, limit: int = 20) -> Optional[Listing]:
    """Busca um produto no Mercado Livre e retorna o anuncio de menor preco."""
    params = {"q": query, "limit": limit}
    response = requests.get(
        SEARCH_URL.format(site_id=site_id), params=params, timeout=TIMEOUT_SECONDS
    )
    response.raise_for_status()
    results = response.json().get("results", [])

    if not results:
        return None

    cheapest = min(results, key=lambda item: item["price"])
    return Listing(
        item_id=cheapest["id"],
        title=cheapest["title"],
        price=float(cheapest["price"]),
        permalink=cheapest["permalink"],
    )
