from dotenv import load_dotenv
load_dotenv(override=True)

import logging
logging.basicConfig(level=logging.INFO)

from fastapi import FastAPI
from sqlalchemy import text
from app.database.database import Base, engine
from app.models import workspace          # noqa: F401
from app.models import workspace_settings  # noqa: F401
from app.models import pipeline_stage     # noqa: F401
from app.models import lead               # noqa: F401
from app.models import user               # noqa: F401
from app.models import activity           # noqa: F401
from app.models import task               # noqa: F401
from app.models import lead_capture_event  # noqa: F401
from app.api import leads, webhook, pipeline, auth, workspace as workspace_router
from app.api import activities, tasks, lead_capture


def _drop_stale_tables():
    """Descarta tabelas sem workspace_id na primeira migração multi-tenant."""
    with engine.connect() as conn:
        tables = {r[0] for r in conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ))}
        if "workspaces" not in tables:
            conn.execute(text("DROP TABLE IF EXISTS leads"))
            conn.execute(text("DROP TABLE IF EXISTS pipeline_stages"))
            conn.commit()
            logging.info("Tabelas stale descartadas para migração multi-tenant.")


def _migrate_columns():
    """Adiciona colunas ausentes em instalações pré-existentes."""
    with engine.connect() as conn:
        user_cols = {r[1] for r in conn.execute(text("PRAGMA table_info(users)"))}
        for col, ddl in [
            ("workspace_id", "INTEGER REFERENCES workspaces(id)"),
            ("name",         "VARCHAR"),
            ("is_admin",     "BOOLEAN DEFAULT 0"),
            ("role",         "VARCHAR DEFAULT 'admin'"),
        ]:
            if col not in user_cols:
                conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} {ddl}"))
                conn.commit()

        lead_cols = {r[1] for r in conn.execute(text("PRAGMA table_info(leads)"))}
        for col, ddl in [
            ("stage_id",           "INTEGER"),
            ("budget",             "REAL"),
            ("user_id",            "INTEGER"),
            ("workspace_id",       "INTEGER REFERENCES workspaces(id)"),
            ("utm_source",         "VARCHAR"),
            ("utm_campaign",       "VARCHAR"),
            ("utm_medium",         "VARCHAR"),
            ("utm_content",        "VARCHAR"),
            ("utm_term",           "VARCHAR"),
            ("campaign_name",      "VARCHAR"),
            ("adset_name",         "VARCHAR"),
            ("ad_name",            "VARCHAR"),
            ("external_source_id", "VARCHAR"),
            ("tags",               "TEXT"),
        ]:
            if col not in lead_cols:
                conn.execute(text(f"ALTER TABLE leads ADD COLUMN {col} {ddl}"))
                conn.commit()

        ps_cols = {r[1] for r in conn.execute(text("PRAGMA table_info(pipeline_stages)"))}
        if "workspace_id" not in ps_cols:
            conn.execute(text("ALTER TABLE pipeline_stages ADD COLUMN workspace_id INTEGER REFERENCES workspaces(id)"))
            conn.commit()


_drop_stale_tables()
Base.metadata.create_all(bind=engine)
_migrate_columns()

app = FastAPI(
    title="CRM API",
    description="API de gerenciamento de leads multi-tenant com RBAC",
    version="4.0.0",
)

app.include_router(auth.router)
app.include_router(workspace_router.router)
app.include_router(leads.router)
app.include_router(activities.router)
app.include_router(tasks.router)
app.include_router(webhook.router)
app.include_router(lead_capture.router)
app.include_router(pipeline.router)


@app.get("/")
def root():
    return {"message": "CRM API funcionando", "docs": "/docs", "version": app.version}
