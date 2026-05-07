# CRM Agência

API REST para gerenciamento de leads com pipeline de vendas estilo Kanban e dashboard visual, construída com FastAPI, SQLite e Streamlit.

## Tecnologias

**Backend**
- Python 3.10+
- FastAPI
- SQLAlchemy
- Pydantic v2
- SQLite
- Uvicorn

**Frontend**
- Streamlit
- Requests
- Pandas

## Instalação

```bash
pip install -r requirements.txt
pip install streamlit requests pandas
```

## Executando

### 1. Backend (API)

```bash
uvicorn main:app --reload
```

A API sobe em `http://localhost:8000`. Documentação interativa em `http://localhost:8000/docs`.

Na primeira execução, o banco é criado automaticamente e as 6 etapas padrão do pipeline são inseridas via seed.

### 2. Frontend (Dashboard)

Em um segundo terminal, na pasta raiz do projeto:

```bash
streamlit run frontend/app.py
```

O dashboard abre automaticamente em `http://localhost:8501`.

> **Atenção:** por padrão o frontend aponta para `http://localhost:8000`. Se o backend estiver em outra porta, edite `API_URL` em `frontend/api.py`.

### Estrutura de pastas

```
crm/
├── main.py                  # Entrypoint da API
├── requirements.txt
├── app/
│   ├── api/
│   │   ├── leads.py         # Endpoints de leads
│   │   ├── pipeline.py      # Endpoints do pipeline
│   │   └── webhook.py       # Endpoint de webhook
│   ├── models/
│   │   ├── lead.py
│   │   └── pipeline_stage.py
│   ├── schemas/
│   │   ├── lead.py
│   │   └── pipeline_stage.py
│   └── database/
│       └── database.py
└── frontend/
    ├── app.py               # Interface Streamlit
    └── api.py               # Cliente da API
```

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
