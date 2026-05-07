import streamlit as st
from api import get_leads, get_board, create_lead

st.set_page_config(
    page_title="CRM Agência",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .lead-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 10px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .lead-name  { font-weight: 700; font-size: 14px; color: #1e293b; margin-bottom: 4px; }
    .lead-info  { color: #64748b; font-size: 13px; margin-top: 3px; }
    .badge {
        display: inline-block;
        background: #f1f5f9;
        color: #475569;
        font-size: 11px;
        padding: 2px 8px;
        border-radius: 99px;
        margin-top: 6px;
    }
    .stage-header {
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        padding-bottom: 8px;
        margin-bottom: 10px;
    }
    .empty-stage { color: #94a3b8; font-size: 12px; text-align: center; padding: 16px 0; }
    div[data-testid="metric-container"] {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px 20px;
    }
</style>
""", unsafe_allow_html=True)


# ── Sidebar: formulário de novo lead ──────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📋 Novo Lead")
    st.divider()

    with st.form("form_lead", clear_on_submit=True):
        nome     = st.text_input("Nome *")
        email    = st.text_input("Email *")
        telefone = st.text_input("Telefone")
        origem   = st.selectbox(
            "Origem",
            ["", "site", "facebook", "instagram", "google", "indicacao", "outro"],
        )
        budget   = st.number_input("Investimento Estimado (R$)", min_value=0.0, step=100.0, format="%.2f")
        enviado = st.form_submit_button(
            "Adicionar Lead", use_container_width=True, type="primary"
        )

    if enviado:
        if not nome or not email:
            st.error("Nome e email são obrigatórios.")
        else:
            try:
                payload = {"name": nome, "email": email}
                if telefone:
                    payload["phone"] = telefone
                if origem:
                    payload["source"] = origem
                if budget:
                    payload["budget"] = budget
                result = create_lead(payload)
                st.success(result.get("message", "Lead adicionado!"))
                st.rerun()
            except Exception as err:
                st.error(f"Erro ao salvar: {err}")


# ── Cabeçalho ─────────────────────────────────────────────────────────────────
st.title("📊 CRM Agência")

leads = get_leads()
board = get_board()

if not board:
    st.error(
        "Não foi possível conectar à API. "
        "Verifique se o servidor está rodando em http://localhost:8001"
    )
    st.stop()


# ── Métricas ──────────────────────────────────────────────────────────────────
total    = len(leads)
stage_map = {item["stage"]["name"]: item["total"] for item in board}
fechados = stage_map.get("fechado", 0)
novos    = stage_map.get("novo", 0)
taxa     = f"{round(fechados / total * 100)}%" if total else "—"

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total de Leads",     total)
m2.metric("Novos",              novos)
m3.metric("Fechados",           fechados)
m4.metric("Taxa de Conversão",  taxa)

st.divider()


# ── Kanban ────────────────────────────────────────────────────────────────────
kanban_cols = st.columns(len(board))

for i, item in enumerate(board):
    stage       = item["stage"]
    stage_leads = item["leads"]
    color       = stage.get("color", "#94a3b8")

    with kanban_cols[i]:
        st.markdown(
            f'<div class="stage-header" '
            f'style="color:{color}; border-bottom:2px solid {color};">'
            f'{stage["name"].capitalize()} '
            f'<span style="color:#94a3b8; font-weight:400;">({item["total"]})</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if not stage_leads:
            st.markdown(
                '<div class="empty-stage">Nenhum lead</div>',
                unsafe_allow_html=True,
            )
            continue

        for lead in stage_leads:
            phone_line  = f'<div class="lead-info">📞 {lead["phone"]}</div>' if lead.get("phone") else ""
            source_line = f'<span class="badge">📍 {lead["source"]}</span>'  if lead.get("source") else ""
            budget_line = f'<span class="badge">💰 R$ {lead["budget"]:,.2f}</span>' if lead.get("budget") else ""

            st.markdown(
                f'<div class="lead-card">'
                f'  <div class="lead-name">{lead["name"]}</div>'
                f'  <div class="lead-info">✉️ {lead["email"]}</div>'
                f'  {phone_line}'
                f'  {source_line}'
                f'  {budget_line}'
                f'</div>',
                unsafe_allow_html=True,
            )
