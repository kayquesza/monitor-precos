# Monitor de Precos - Canais de Ofertas no Telegram

Monitora canais publicos de ofertas no Telegram e notifica (tambem via
Telegram) sempre que aparecer um post novo mencionando um dos celulares
configurados.

## Produtos monitorados

- Samsung Galaxy S24 FE
- Samsung Galaxy S25 FE
- Samsung Galaxy A57
- Samsung Galaxy S23
- Samsung Galaxy S24
- Samsung Galaxy S25
- Samsung Galaxy S24+
- Samsung Galaxy S25+
- MacBook

A lista, com os termos obrigatorios/exclusao usados para casar cada modelo no
texto dos posts (incluindo exclusao de acessorios como capa/capinha/pelicula
e de aparelhos reembalados/seminovos), fica em `src/config.py` (lista
`PRODUCTS`) e pode ser editada livremente.

## Canais monitorados

- [@escolhasegura](https://t.me/escolhasegura)
- [@ctofertascelulares](https://t.me/ctofertascelulares)
- [@Fraguas84Oficial](https://t.me/Fraguas84Oficial)
- [@pelandobr](https://t.me/pelandobr)
- [@cupons_desconto](https://t.me/cupons_desconto)
- [@BenchPromos](https://t.me/BenchPromos)

A lista fica em `src/config.py` (lista `CHANNELS`).

## Como funciona

1. `src/telegram_canais.py` busca a pagina de preview publica de cada canal
   (`https://t.me/s/{canal}`) - a mesma usada para embutir posts em sites
   externos, que nao exige login nem token - e extrai o texto e o ID unico de
   cada post.
2. `src/config.py` define, para cada modelo, quais termos precisam aparecer
   no texto (`include_terms`) e quais termos descartam o post
   (`exclude_terms`, para nao confundir por exemplo "S24" com "S24 FE").
3. `src/monitor.py` filtra os posts de cada canal pelos modelos configurados
   e compara com `data/historico.json`, que guarda os posts ja notificados
   (chave `"{canal}/{id_do_post}"::"{nome_do_modelo}"`).
4. Para cada post novo que der match, `src/telegram.py` envia uma mensagem
   com o texto do post, a data/hora de publicacao (extraida da pagina) e o
   link direto para ele no chat configurado.
5. Se algum canal falhar ao buscar ou retornar 0 posts, um alerta separado
   e enviado avisando qual canal deu problema.

## Configuracao

### 1. Criar um bot no Telegram

1. Fale com [@BotFather](https://t.me/BotFather) e crie um bot com `/newbot`.
2. Guarde o token gerado (`TELEGRAM_BOT_TOKEN`).
3. Descubra o `chat_id` (do seu usuario ou de um grupo) enviando uma mensagem
   para o bot e consultando `https://api.telegram.org/bot<TOKEN>/getUpdates`.

### 2. Configurar secrets no GitHub

No repositorio, va em **Settings > Secrets and variables > Actions** e crie:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

### 3. Rodar localmente (opcional)

```bash
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN=xxxx
export TELEGRAM_CHAT_ID=xxxx
python src/monitor.py
```

No Windows (PowerShell):

```powershell
pip install -r requirements.txt
$env:TELEGRAM_BOT_TOKEN = "xxxx"
$env:TELEGRAM_CHAT_ID = "xxxx"
python src/monitor.py
```

## Automacao (GitHub Actions)

O workflow `.github/workflows/monitor.yml` roda a cada 15 minutos
(`cron: "*/15 * * * *"`) e tambem pode ser disparado manualmente pela aba
Actions (`workflow_dispatch`). Apos cada execucao, o arquivo
`data/historico.json` e commitado de volta no repositorio para manter o
historico de posts ja notificados entre execucoes.
