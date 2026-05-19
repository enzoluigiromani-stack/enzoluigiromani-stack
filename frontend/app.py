import streamlit as st
from api import (
    register, login, get_me, get_workspace, get_workspace_settings,
    update_workspace_settings, get_leads, get_board, create_lead,
    move_lead, get_activities, get_lead_timeline,
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
        border-radius: 10px 10px 0 0;
        border-bottom: none;
        padding: 12px 14px 8px 14px;
        margin-bottom: 0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        transition: box-shadow 0.15s ease;
    }
    .lead-card:hover { box-shadow: 0 3px 10px rgba(0,0,0,0.1); }
    .lead-card-simple {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 8px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        transition: box-shadow 0.15s ease;
    }
    .lead-card-simple:hover { box-shadow: 0 3px 10px rgba(0,0,0,0.1); }
    .card-move-area {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-top: 1px dashed #e2e8f0;
        border-radius: 0 0 10px 10px;
        padding: 4px 6px 6px 6px;
        margin-bottom: 10px;
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
        margin-right: 4px;
    }
    .badge-budget {
        display: inline-block;
        background: #d1fae5;
        color: #065f46;
        font-size: 11px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 99px;
        margin-top: 6px;
        margin-right: 4px;
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
    .activity-row {
        display: flex; align-items: flex-start; gap: 10px;
        padding: 8px 0; border-bottom: 1px solid #f1f5f9;
    }
    .activity-icon { font-size: 18px; min-width: 24px; }
    .activity-body { flex: 1; }
    .activity-desc { font-size: 13px; color: #1e293b; }
    .activity-meta { font-size: 11px; color: #94a3b8; margin-top: 2px; }
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

_ACTIVITY_ICON = {
    "lead_created":  "🟢",
    "lead_updated":  "✏️",
    "lead_moved":    "↗️",
    "email_sent":    "📧",
    "whatsapp_sent": "📱",
    "user_login":    "🔐",
    "stage_created": "🏷️",
}


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

# ── Feedback de movimentação ──────────────────────────────────────────────────
if "_move_ok" in st.session_state:
    st.success(st.session_state.pop("_move_ok"))
if "_move_err" in st.session_state:
    st.error(st.session_state.pop("_move_err"))

st.divider()


# ── Kanban ────────────────────────────────────────────────────────────────────

# Mapa de etapas: id → nome e nome → id (usado nos selectboxes de movimentação)
_stage_by_id   = {item["stage"]["id"]: item["stage"] for item in board}
_stage_options = [(item["stage"]["id"], item["stage"]["name"].capitalize()) for item in board]
can_move = role in ("admin", "manager")

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
                f'<span class="badge-budget">💰 {_currency_fmt(lead["budget"], currency)}</span>'
                if lead.get("budget") else ""
            )

            # Classe do card: com ou sem área de movimentação abaixo
            card_class = "lead-card" if can_move else "lead-card-simple"
            st.markdown(
                f'<div class="{card_class}" style="border-left: 4px solid {color};">'
                f'  <div class="lead-name">{lead["name"]}</div>'
                f'  <div class="lead-info">✉️ {lead["email"]}</div>'
                f'  {phone_line}'
                f'  <div style="margin-top:4px">{source_line}{budget_line}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            # ── Controles de movimentação (admin/manager) ─────────────────────
            if can_move:
                dest_opts = [
                    (sid, sname)
                    for sid, sname in _stage_options
                    if sid != stage["id"]
                ]
                dest_labels = [s[1] for s in dest_opts]
                dest_id_map = {s[1]: s[0] for s in dest_opts}

                st.markdown('<div class="card-move-area">', unsafe_allow_html=True)
                c1, c2 = st.columns([3, 1])
                with c1:
                    dest = st.selectbox(
                        "etapa",
                        dest_labels,
                        key=f"dest_{lead['id']}",
                        label_visibility="collapsed",
                    )
                with c2:
                    move_clicked = st.button(
                        "→",
                        key=f"mv_{lead['id']}",
                        use_container_width=True,
                        help=f"Mover para {dest}",
                    )
                st.markdown('</div>', unsafe_allow_html=True)

                if move_clicked:
                    try:
                        move_lead(lead["id"], dest_id_map[dest], token)
                        st.session_state["_move_ok"] = (
                            f"**{lead['name']}** movido para **{dest}** com sucesso."
                        )
                    except Exception as e:
                        err = getattr(e, "response", None)
                        detail = err.json().get("detail", str(e)) if err else str(e)
                        st.session_state["_move_err"] = f"Erro ao mover: {detail}"
                    st.rerun()

# ── Atividades Recentes ───────────────────────────────────────────────────────
st.divider()
col_act, col_tl = st.columns([1, 1])

with col_act:
    st.markdown("### 📋 Atividades Recentes")
    act_data = get_activities(token, page=1, limit=10)
    activity_items = act_data.get("items", [])

    if not activity_items:
        st.caption("Nenhuma atividade registrada ainda.")
    else:
        rows_html = ""
        for a in activity_items:
            icon = _ACTIVITY_ICON.get(a["type"], "•")
            ts   = a["created_at"][:16].replace("T", " ")
            who  = a.get("user_name") or "Sistema"
            rows_html += (
                f'<div class="activity-row">'
                f'  <div class="activity-icon">{icon}</div>'
                f'  <div class="activity-body">'
                f'    <div class="activity-desc">{a["description"]}</div>'
                f'    <div class="activity-meta">{who} · {ts}</div>'
                f'  </div>'
                f'</div>'
            )
        st.markdown(rows_html, unsafe_allow_html=True)

# ── Timeline do Lead ─────────────────────────────────────────────────────────
with col_tl:
    st.markdown("### 🔍 Timeline do Lead")

    all_leads = get_leads(token)
    if not all_leads:
        st.caption("Nenhum lead cadastrado.")
    else:
        lead_options = {f'{l["name"]} ({l["email"]})': l["id"] for l in all_leads}
        selected = st.selectbox("Selecione um lead", list(lead_options.keys()),
                                label_visibility="collapsed")
        lead_id = lead_options[selected]

        tl_data = get_lead_timeline(lead_id, token, limit=20)
        tl_items = tl_data.get("items", [])

        if not tl_items:
            st.caption("Nenhuma atividade para este lead.")
        else:
            rows_html = ""
            for a in tl_items:
                icon = _ACTIVITY_ICON.get(a["type"], "•")
                ts   = a["created_at"][:16].replace("T", " ")
                who  = a.get("user_name") or "Sistema"
                rows_html += (
                    f'<div class="activity-row">'
                    f'  <div class="activity-icon">{icon}</div>'
                    f'  <div class="activity-body">'
                    f'    <div class="activity-desc">{a["description"]}</div>'
                    f'    <div class="activity-meta">{who} · {ts}</div>'
                    f'  </div>'
                    f'</div>'
                )
            st.markdown(rows_html, unsafe_allow_html=True)
            st.caption(f"Total: {tl_data['total']} evento(s)")
