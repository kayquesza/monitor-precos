# Monitor de Precos - Mercado Livre

Monitora o preco de celulares no Mercado Livre e envia uma notificacao no
Telegram sempre que o menor preco encontrado cair em relacao a ultima
execucao.

## Produtos monitorados

- Samsung Galaxy S24 FE
- Samsung Galaxy S25 FE
- Samsung Galaxy A57
- Samsung Galaxy S24
- Samsung Galaxy S25

A lista fica em `src/config.py` (lista `PRODUCTS`) e pode ser editada
livremente.

## Como funciona

1. `src/mercado_livre.py` consulta a API publica de busca do Mercado Livre
   (`https://api.mercadolibre.com/sites/MLB/search`) para cada produto e pega
   o anuncio de menor preco entre os resultados.
2. `src/monitor.py` compara o preco atual com o preco salvo em
   `data/price_history.json` na execucao anterior.
3. Se o preco caiu, `src/telegram.py` envia uma mensagem para o chat
   configurado via Telegram Bot API.
4. O historico e atualizado em `data/price_history.json`.

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

O workflow `.github/workflows/monitor.yml` roda nos minutos `:07` e `:44` de
cada hora (`cron: "7,44 * * * *"`), evitando os horarios de pico (`:00`/`:30`)
da fila do GitHub Actions, e tambem pode ser disparado manualmente pela aba
Actions (`workflow_dispatch`). Apos cada execucao, o arquivo
`data/price_history.json` e commitado de volta no repositorio para manter o
historico entre execucoes.
