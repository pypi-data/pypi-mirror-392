# MCP Facebook Ads (Python)

Servidor MCP em Python para consultar dados da Facebook Marketing API (somente leitura).
Baseado no projeto [`mcp-facebook-ads`](../mcp-facebook-ads), porém construído com
Python e pronto para publicação no PyPI.

## 🚀 Recursos

- Consultar campanhas da conta de anúncios (`get_campaigns`)
- Consultar métricas de campanhas (`get_campaign_insights`)
- Consultar insights da conta (`get_account_insights`)
- Consultar criativos de anúncios (`get_ad_creatives`)
- Listar anúncios de uma campanha (`get_campaign_ads`)

## 📋 Pré-requisitos

- Python 3.10+
- Conta e App configurados no [Facebook Developers](https://developers.facebook.com)
- Access Token com permissão `ads_read`
- ID da conta de anúncios

## 🔧 Instalação (local)

```bash
pip install -e .
```

Opcionalmente, copie `.env.example` para `.env` e configure as credenciais:

```env
FB_ACCESS_TOKEN=seu_token_aqui
FB_ACCOUNT_ID=seu_account_id_aqui
FB_API_VERSION=v21.0
```

## 🎯 Como usar

### Via PyPI + npx-like (`uvx`/`pipx`/`python -m`)

Após a publicação no PyPI será possível executar:

```bash
pip install mcp_facebook_ads
mcp_facebook_ads --transport stdio
```

Para integrar ao MCP config (por exemplo `.cursor/mcp.json`):

```json
"facebook-ads": {
  "command": "mcp_facebook_ads",
  "args": ["--transport", "stdio"],
  "env": {
    "FB_ACCESS_TOKEN": "seu_token_aqui",
    "FB_ACCOUNT_ID": "seu_account_id_aqui",
    "FB_API_VERSION": "v21.0"
  }
}
```

### Execução local direta

```bash
python -m mcp_facebook_ads --transport stdio
```

### Variáveis de ambiente

| Variável           | Descrição                                   |
| ------------------ | ------------------------------------------- |
| `FB_ACCESS_TOKEN`  | Access token da Marketing API (obrigatório) |
| `FB_ACCOUNT_ID`    | ID da conta (sem o prefixo `act_`)          |
| `FB_API_VERSION`   | Versão da API (padrão: `v21.0`)             |

## 🧰 Tools

As mesmas tools do projeto em Node, com os mesmos parâmetros e comportamento.
Use os nomes: `get_campaigns`, `get_campaign_insights`, `get_account_insights`,
`get_ad_creatives`, `get_campaign_ads`.

## 📦 Publicação no PyPI

O projeto já possui `pyproject.toml` configurado com `hatchling`.
Para publicar:

```bash
python -m build
python -m twine upload dist/*
```

## 📝 License

MIT
