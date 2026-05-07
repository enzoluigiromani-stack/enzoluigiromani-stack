# CRM API

API REST para gerenciamento de leads com pipeline de vendas estilo Kanban, construída com FastAPI e SQLite.

## Tecnologias

- Python 3.10+
- FastAPI
- SQLAlchemy
- Pydantic v2
- SQLite
- Uvicorn

## Instalação

```bash
pip install -r requirements.txt
```

## Executando

```bash
uvicorn main:app --reload
```

A API sobe em `http://localhost:8000`. Documentação interativa em `http://localhost:8000/docs`.

Na primeira execução, o banco é criado automaticamente e as 6 etapas padrão do pipeline são inseridas via seed.

---

## Endpoints

### Leads

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/leads/` | Cria ou atualiza lead (dedup por e-mail) |
| `GET` | `/leads/` | Lista todos os leads |
| `GET` | `/leads/{id}` | Busca lead por ID |
| `PATCH` | `/leads/{id}` | Atualiza campos do lead |
| `PATCH` | `/leads/{id}/move` | Move lead para outra etapa do pipeline |
| `DELETE` | `/leads/{id}` | Remove lead |

### Pipeline

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/pipeline/stages` | Lista etapas ordenadas |
| `POST` | `/pipeline/stages` | Cria nova etapa |
| `GET` | `/pipeline/board` | Board Kanban com leads agrupados por etapa |

### Webhook

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/webhook/leads` | Recebe leads de fontes externas (formulários, Facebook Ads, etc.) |

---

## Lógica de deduplicação

O campo `email` é a chave de deduplicação. Ao criar um lead com e-mail já existente (via `POST /leads/` ou webhook), os dados são **atualizados** em vez de criar um registro duplicado. A resposta indica se o lead foi `criado` ou `atualizado`.

## Pipeline de vendas

Etapas padrão criadas automaticamente:

| # | Nome | Cor |
|---|------|-----|
| 1 | novo | `#6366f1` |
| 2 | contato | `#f59e0b` |
| 3 | qualificado | `#3b82f6` |
| 4 | proposta | `#8b5cf6` |
| 5 | fechado | `#22c55e` |
| 6 | perdido | `#ef4444` |

Todo lead criado é automaticamente associado à etapa **novo**.

## Webhook com segurança

Para proteger o endpoint de webhook, defina a variável de ambiente `WEBHOOK_SECRET`:

```bash
WEBHOOK_SECRET=minha-chave uvicorn main:app --reload
```

Envie o header `X-Webhook-Secret: minha-chave` nas requisições. Se a variável não estiver definida, o endpoint aceita qualquer requisição.

## Exemplos

**Criar lead:**
```bash
curl -X POST http://localhost:8000/leads/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Ana Souza","email":"ana@exemplo.com","source":"instagram"}'
```

**Mover lead para outra etapa:**
```bash
curl -X PATCH http://localhost:8000/leads/1/move \
  -H "Content-Type: application/json" \
  -d '{"stage_id": 3}'
```

**Board Kanban:**
```bash
curl http://localhost:8000/pipeline/board
```
