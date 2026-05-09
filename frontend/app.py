import streamlit as st
from api import (
    register, login, get_me, get_workspace, get_workspace_settings,
    update_workspace_settings, get_leads, get_board, create_lead,
)

st.set_page_config(
    page_title="CRM",
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
    .ws-badge {
        background: #ede9fe; color: #6d28d9;
        font-size: 12px; font-weight: 600;
        padding: 3px 10px; border-radius: 99px;
        display: inline-block; margin-bottom: 4px;
    }
    .role-admin   { background:#fee2e2; color:#b91c1c; font-size:11px; font-weight:700; padding:2px 8px; border-radius:99px; display:inline-block; }
    .role-manager { background:#fef9c3; color:#92400e; font-size:11px; font-weight:700; padding:2px 8px; border-radius:99px; display:inline-block; }
    .role-sales   { background:#dcfce7; color:#15803d; font-size:11px; font-weight:700; padding:2px 8px; border-radius:99px; display:inline-block; }
</style>
""", unsafe_allow_html=True)

_CURRENCY_SYMBOL = {"BRL": "R$", "USD": "$", "EUR": "€", "GBP": "£"}


def _currency_fmt(value: float, currency: str) -> str:
    symbol = _CURRENCY_SYMBOL.get(currency, currency)
    return f"{symbol} {value:,.2f}"


# ── Tela de autenticação ───────────────────────────────────────────────────────

def show_auth():
    st.title("📊 CRM")
    tab_login, tab_register = st.tabs(["Entrar", "Criar Conta"])

    with tab_login:
        with st.form("form_login"):
            email    = st.text_input("E-mail")
            password = st.text_input("Senha", type="password")
            submitted = st.form_submit_button("Entrar", use_container_width=True, type="primary")
        if submitted:
            if not email or not password:
                st.error("Preencha e-mail e senha.")
            else:
                try:
                    data = login(email, password)
                    _load_session(data["access_token"])
                    st.rerun()
                except Exception as e:
                    st.error(f"E-mail ou senha incorretos. ({e})")

    with tab_register:
        with st.form("form_register"):
            name       = st.text_input("Nome")
            email_r    = st.text_input("E-mail")
            password_r = st.text_input("Senha", type="password")
            submitted_r = st.form_submit_button("Criar Conta", use_container_width=True, type="primary")
        if submitted_r:
            if not name or not email_r or not password_r:
                st.error("Preencha todos os campos.")
            elif len(password_r) < 6:
                st.error("Senha deve ter no mínimo 6 caracteres.")
            else:
                try:
                    register(name, email_r, password_r)
                    data = login(email_r, password_r)
                    _load_session(data["access_token"])
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao criar conta: {e}")


def _load_session(token: str):
    st.session_state.token     = token
    st.session_state.user      = get_me(token)
    st.session_state.workspace = get_workspace(token)
    try:
        st.session_state.settings = get_workspace_settings(token)
    except Exception:
        st.session_state.settings = {"currency": "BRL", "company_name": None, "primary_color": "#6366f1"}


# ── Guard de sessão ────────────────────────────────────────────────────────────

if "token" not in st.session_state:
    show_auth()
    st.stop()

token     = st.session_state.token
user      = st.session_state.user
workspace = st.session_state.workspace
settings  = st.session_state.get("settings", {"currency": "BRL", "company_name": None})
currency  = settings.get("currency", "BRL")
company   = settings.get("company_name") or workspace["name"]
role      = user.get("role", "sales")


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f'<div class="ws-badge">🏢 {company}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="role-{role}">{role.upper()}</div>', unsafe_allow_html=True)
    st.caption(f'Usuário: **{user["name"]}**')
    st.caption(f'slug: `{workspace["slug"]}`')
    st.divider()

    # ── Novo Lead ─────────────────────────────────────────────────────────────
    st.markdown("## 📋 Novo Lead")
    with st.form("form_lead", clear_on_submit=True):
        nome     = st.text_input("Nome *")
        email    = st.text_input("Email *")
        telefone = st.text_input("Telefone")
        origem   = st.selectbox("Origem",
                                ["", "site", "facebook", "instagram", "google", "indicacao", "outro"])
        budget   = st.number_input("Investimento Estimado", min_value=0.0, step=100.0, format="%.2f")
        enviado  = st.form_submit_button("Adicionar Lead", use_container_width=True, type="primary")

    if enviado:
        if not nome or not email:
            st.error("Nome e email são obrigatórios.")
        else:
            try:
                payload = {"name": nome, "email": email}
                if telefone: payload["phone"] = telefone
                if origem:   payload["source"] = origem
                if budget:   payload["budget"] = budget
                result = create_lead(payload, token)
                st.success(result.get("message", "Lead adicionado!"))
                st.rerun()
            except Exception as err:
                st.error(f"Erro ao salvar: {err}")

    # ── Configurações (somente admin) ─────────────────────────────────────────
    if role == "admin":
        st.divider()
        with st.expander("⚙️ Configurações"):
            with st.form("form_settings"):
                s = settings
                new_company = st.text_input("Nome da Empresa", value=s.get("company_name") or "")
                new_currency = st.selectbox("Moeda",
                                            ["BRL", "USD", "EUR", "GBP"],
                                            index=["BRL", "USD", "EUR", "GBP"].index(
                                                s.get("currency", "BRL")))
                new_tz = st.text_input("Fuso Horário", value=s.get("timezone", "America/Sao_Paulo"))
                new_color = st.text_input("Cor Principal (hex)", value=s.get("primary_color", "#6366f1"))
                salvo = st.form_submit_button("Salvar", use_container_width=True)
            if salvo:
                try:
                    updated = update_workspace_settings({
                        "company_name":  new_company or None,
                        "currency":      new_currency,
                        "timezone":      new_tz,
                        "primary_color": new_color,
                    }, token)
                    st.session_state.settings = updated
                    st.success("Configurações salvas!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

    st.divider()
    if st.button("Sair", use_container_width=True):
        for key in ["token", "user", "workspace", "settings"]:
            st.session_state.pop(key, None)
        st.rerun()


# ── Cabeçalho ─────────────────────────────────────────────────────────────────
st.title(f"📊 {company}")

leads = get_leads(token)
board = get_board(token)

if not board:
    st.error("Não foi possível conectar à API. Verifique se o servidor está rodando em http://localhost:8000")
    st.stop()


# ── Métricas ──────────────────────────────────────────────────────────────────
total     = len(leads)
stage_map = {item["stage"]["name"]: item["total"] for item in board}
fechados  = stage_map.get("fechado", 0)
novos     = stage_map.get("novo", 0)
taxa      = f"{round(fechados / total * 100)}%" if total else "—"

budget_total = sum(l.get("budget") or 0 for l in leads)

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total de Leads",    total)
m2.metric("Novos",             novos)
m3.metric("Fechados",          fechados)
m4.metric("Taxa de Conversão", taxa)
m5.metric("Receita Estimada",  _currency_fmt(budget_total, currency) if budget_total else "—")

st.divider()


# ── Kanban ────────────────────────────────────────────────────────────────────
kanban_cols = st.columns(len(board))

for i, item in enumerate(board):
    stage       = item["stage"]
    stage_leads = item["leads"]
    color       = stage.get("color", "#94a3b8")

    with kanban_cols[i]:
        st.markdown(
            f'<div class="stage-header" style="color:{color}; border-bottom:2px solid {color};">'
            f'{stage["name"].capitalize()} '
            f'<span style="color:#94a3b8; font-weight:400;">({item["total"]})</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if not stage_leads:
            st.markdown('<div class="empty-stage">Nenhum lead</div>', unsafe_allow_html=True)
            continue

        for lead in stage_leads:
            phone_line  = f'<div class="lead-info">📞 {lead["phone"]}</div>' if lead.get("phone") else ""
            source_line = f'<span class="badge">📍 {lead["source"]}</span>' if lead.get("source") else ""
            budget_line = (
                f'<span class="badge">💰 {_currency_fmt(lead["budget"], currency)}</span>'
                if lead.get("budget") else ""
            )
            st.markdown(
                f'<div class="lead-card">'
                f'  <div class="lead-name">{lead["name"]}</div>'
                f'  <div class="lead-info">✉️ {lead["email"]}</div>'
                f'  {phone_line}{source_line}{budget_line}'
                f'</div>',
                unsafe_allow_html=True,
            )
