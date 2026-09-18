"""Configuracao dos canais de Telegram e dos modelos monitorados."""

# Canais publicos de ofertas monitorados via https://t.me/s/{canal}
CHANNELS = [
    "escolhasegura",
    "ctofertascelulares",
    "Fraguas84Oficial",
]

# Cada produto e definido por termos que precisam aparecer no texto do post
# (include_terms, todos obrigatorios) e termos que, se aparecerem, descartam
# o post (exclude_terms) - usado para nao confundir "S24" com "S24 FE", por
# exemplo. A comparacao e case-insensitive.
PRODUCTS = [
    {
        "name": "Samsung Galaxy S24 FE",
        "include_terms": ["s24", "fe"],
        "exclude_terms": ["ultra", "s24+", "plus"],
    },
    {
        "name": "Samsung Galaxy S25 FE",
        "include_terms": ["s25", "fe"],
        "exclude_terms": ["ultra", "s25+", "plus"],
    },
    {
        "name": "Samsung Galaxy A57",
        "include_terms": ["a57"],
        "exclude_terms": [],
    },
    {
        "name": "Samsung Galaxy S24",
        "include_terms": ["s24"],
        "exclude_terms": ["fe", "ultra", "s24+", "plus"],
    },
    {
        "name": "Samsung Galaxy S25",
        "include_terms": ["s25"],
        "exclude_terms": ["fe", "ultra", "s25+", "plus"],
    },
]

# Caminho do arquivo que guarda os IDs de post ja notificados entre execucoes.
HISTORY_PATH = "data/historico.json"


def matches_product(text: str, product: dict) -> bool:
    """Retorna True se o texto contem todos os include_terms e nenhum exclude_terms."""
    text_lower = text.lower()
    has_all_includes = all(term.lower() in text_lower for term in product["include_terms"])
    has_any_exclude = any(term.lower() in text_lower for term in product["exclude_terms"])
    return has_all_includes and not has_any_exclude
