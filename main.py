from dotenv import load_dotenv
load_dotenv(override=True)

import logging
logging.basicConfig(level=logging.INFO)

from fastapi import FastAPI
from sqlalchemy import text
from app.database.database import Base, engine, SessionLocal
from app.models import pipeline_stage  # registra PipelineStage no Base antes do create_all
from app.models import lead             # registra Lead no Base antes do create_all
from app.api import leads, webhook, pipeline


def _migrate():
    """Adiciona colunas novas em tabelas existentes (SQLite não suporta Alembic aqui)."""
    with engine.connect() as conn:
        cols = [r[1] for r in conn.execute(text("PRAGMA table_info(leads)"))]
        if "stage_id" not in cols:
            conn.execute(text("ALTER TABLE leads ADD COLUMN stage_id INTEGER"))
            conn.commit()
        if "budget" not in cols:
            conn.execute(text("ALTER TABLE leads ADD COLUMN budget REAL"))
            conn.commit()


def _seed():
    """Cria as etapas padrão do pipeline se a tabela estiver vazia."""
    db = SessionLocal()
    try:
        if db.query(pipeline_stage.PipelineStage).count() > 0:
            return
        defaults = [
            {"name": "novo",        "order": 1, "color": "#6366f1"},
            {"name": "contato",     "order": 2, "color": "#f59e0b"},
            {"name": "qualificado", "order": 3, "color": "#3b82f6"},
            {"name": "proposta",    "order": 4, "color": "#8b5cf6"},
            {"name": "fechado",     "order": 5, "color": "#22c55e"},
            {"name": "perdido",     "order": 6, "color": "#ef4444"},
        ]
        for s in defaults:
            db.add(pipeline_stage.PipelineStage(**s))
        db.commit()
    finally:
        db.close()


Base.metadata.create_all(bind=engine)
_migrate()
_seed()

app = FastAPI(
    title="CRM API",
    description="API de gerenciamento de leads",
    version="1.0.0",
)

app.include_router(leads.router)
app.include_router(webhook.router)
app.include_router(pipeline.router)


@app.get("/")
def root():
    return {"message": "CRM API funcionando", "docs": "/docs"}
