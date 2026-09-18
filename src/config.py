"""Configuracao dos canais de Telegram e dos modelos monitorados."""

import re

# Canais publicos de ofertas monitorados via https://t.me/s/{canal}
CHANNELS = [
    "escolhasegura",
    "ctofertascelulares",
    "Fraguas84Oficial",
    "pelandobr",
    "cupons_desconto",
    "BenchPromos",
]

# Termos que descartam um post por ser acessorio/reembalado, nao o aparelho
# em si. Compartilhado entre todos os modelos de celular e o MacBook.
ACCESSORY_EXCLUDE_TERMS = [
    "capa",
    "capinha",
    "case",
    "pelicula",
    "película",
    "suporte",
    "reembalado",
    "seminovo",
]

# Cada produto e definido por termos que precisam aparecer no texto do post
# (include_terms, todos obrigatorios) e termos que, se aparecerem, descartam
# o post (exclude_terms) - usado para nao confundir "S24" com "S24 FE" ou com
# "S24+", por exemplo. A comparacao e case-insensitive e por token (ver
# _contains_term), nao substring solta.
PRODUCTS = [
    {
        "name": "Samsung Galaxy S24 FE",
        "include_terms": ["s24", "fe"],
        "exclude_terms": ["ultra", "s24+", "plus"] + ACCESSORY_EXCLUDE_TERMS,
    },
    {
        "name": "Samsung Galaxy S25 FE",
        "include_terms": ["s25", "fe"],
        "exclude_terms": ["ultra", "s25+", "plus"] + ACCESSORY_EXCLUDE_TERMS,
    },
    {
        "name": "Samsung Galaxy A57",
        "include_terms": ["a57"],
        "exclude_terms": [] + ACCESSORY_EXCLUDE_TERMS,
    },
    {
        "name": "Samsung Galaxy S23",
        "include_terms": ["s23"],
        "exclude_terms": ["fe", "ultra", "s23+", "plus"] + ACCESSORY_EXCLUDE_TERMS,
    },
    {
        "name": "Samsung Galaxy S24",
        "include_terms": ["s24"],
        "exclude_terms": ["fe", "ultra", "s24+", "plus"] + ACCESSORY_EXCLUDE_TERMS,
    },
    {
        "name": "Samsung Galaxy S25",
        "include_terms": ["s25"],
        "exclude_terms": ["fe", "ultra", "s25+", "plus", "edge"] + ACCESSORY_EXCLUDE_TERMS,
    },
    {
        # Variante "Plus": usamos o token composto "s24+" (com o simbolo) em
        # vez de ["s24", "plus"] separados, porque posts reais escrevem
        # "S24+" com o simbolo, sem a palavra "Plus" por extenso - testado,
        # ["s24", "plus"] em AND NAO bateria com "Samsung Galaxy S24+ 256GB".
        "name": "Samsung Galaxy S24+",
        "include_terms": ["s24+"],
        "exclude_terms": ["fe", "ultra", "edge"] + ACCESSORY_EXCLUDE_TERMS,
    },
    {
        "name": "Samsung Galaxy S25+",
        "include_terms": ["s25+"],
        "exclude_terms": ["fe", "ultra", "edge"] + ACCESSORY_EXCLUDE_TERMS,
    },
    {
        "name": "MacBook",
        "include_terms": ["macbook"],
        "exclude_terms": [] + ACCESSORY_EXCLUDE_TERMS,
    },
]

# Caminho do arquivo que guarda os IDs de post ja notificados entre execucoes.
HISTORY_PATH = "data/historico.json"


def _contains_term(text: str, term: str) -> bool:
    """Verifica se `term` aparece em `text` como palavra/token isolado.

    Usa lookaround em vez de \\b puro para lidar bem com termos que tem
    caracteres nao-alfanumericos (ex: "s24+"), onde \\b se comporta de forma
    inconsistente. Sem isso, substring simples faz "fe" bater dentro de
    "oferta", confundindo S24/S25 com S24 FE/S25 FE.

    Atencao: um caractere nao-alfanumerico (como "+") conta como fronteira,
    entao o termo "s24" TAMBEM bate dentro de "S24+" - por isso os produtos
    base (S24, S25, S23) precisam excluir "s24+"/"s25+"/"s23+" explicitamente
    alem da palavra "plus".
    """
    pattern = r"(?<!\w)" + re.escape(term) + r"(?!\w)"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def matches_product(text: str, product: dict) -> bool:
    """Retorna True se o texto contem todos os include_terms e nenhum exclude_terms."""
    has_all_includes = all(_contains_term(text, term) for term in product["include_terms"])
    has_any_exclude = any(_contains_term(text, term) for term in product["exclude_terms"])
    return has_all_includes and not has_any_exclude
