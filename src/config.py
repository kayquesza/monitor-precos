"""Configuracao dos produtos monitorados no Mercado Livre."""

# Cada produto tem um termo de busca usado na API do Mercado Livre.
# site_id "MLB" = Mercado Livre Brasil.
SITE_ID = "MLB"

PRODUCTS = [
    {"name": "Samsung Galaxy S24 FE", "query": "samsung galaxy s24 fe"},
    {"name": "Samsung Galaxy S25 FE", "query": "samsung galaxy s25 fe"},
    {"name": "Samsung Galaxy A57", "query": "samsung galaxy a57"},
    {"name": "Samsung Galaxy S24", "query": "samsung galaxy s24"},
    {"name": "Samsung Galaxy S25", "query": "samsung galaxy s25"},
]

# Quantidade de resultados considerados por busca ao escolher o menor preco.
SEARCH_LIMIT = 20

# Caminho do arquivo que guarda o historico de precos entre execucoes.
PRICE_HISTORY_PATH = "data/price_history.json"
