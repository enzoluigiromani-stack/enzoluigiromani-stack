import streamlit as st
from api import (
    register, login, get_me, get_workspace, get_workspace_settings,
    update_workspace_settings, get_leads, get_board, create_lead,
    move_lead, get_activities, get_lead_timeline,
    get_tasks, create_task, complete_task, refresh_tasks, get_task_summary,
    get_capture_events, get_capture_stats, post_meta_test,
    get_conversations, create_conversation, update_conversation,
    get_inbox_messages, send_inbox_message,
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
    .task-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .task-title   { font-weight: 700; font-size: 14px; color: #1e293b; margin-bottom: 4px; }
    .task-meta    { font-size: 12px; color: #64748b; margin-top: 4px; }
    .task-desc    { font-size: 12px; color: #94a3b8; margin-top: 3px; }
    .badge-priority-high   { background:#fee2e2; color:#b91c1c; font-size:11px; font-weight:700; padding:2px 8px; border-radius:99px; display:inline-block; margin-right:4px; }
    .badge-priority-medium { background:#fef9c3; color:#92400e; font-size:11px; font-weight:700; padding:2px 8px; border-radius:99px; display:inline-block; margin-right:4px; }
    .badge-priority-low    { background:#dcfce7; color:#15803d; font-size:11px; font-weight:700; padding:2px 8px; border-radius:99px; display:inline-block; margin-right:4px; }
    .badge-status-pending   { background:#dbeafe; color:#1d4ed8; font-size:11px; padding:2px 8px; border-radius:99px; display:inline-block; margin-right:4px; }
    .badge-status-overdue   { background:#fee2e2; color:#b91c1c; font-size:11px; font-weight:700; padding:2px 8px; border-radius:99px; display:inline-block; margin-right:4px; }
    .badge-status-completed { background:#dcfce7; color:#15803d; font-size:11px; padding:2px 8px; border-radius:99px; display:inline-block; margin-right:4px; }
    /* ── Inbox ── */
    .ib-conv-card { background:#fff; border:1px solid #e2e8f0; border-radius:10px; padding:10px 12px; margin-bottom:6px; }
    .ib-conv-card.ib-active { border-left:4px solid #6366f1; background:#f5f3ff; }
    .ib-conv-lead { font-weight:700; font-size:14px; color:#1e293b; }
    .ib-conv-sub  { font-size:12px; color:#64748b; margin-top:2px; }
    .ib-conv-ts   { font-size:11px; color:#94a3b8; margin-top:2px; }
    .ib-badge-open   { background:#dcfce7; color:#15803d; font-size:10px; font-weight:700; padding:1px 7px; border-radius:99px; display:inline-block; }
    .ib-badge-closed { background:#f1f5f9; color:#64748b; font-size:10px; font-weight:700; padding:1px 7px; border-radius:99px; display:inline-block; }
    .ib-chat-area { height:380px; overflow-y:auto; padding:10px 6px; border:1px solid #e2e8f0; border-radius:10px; background:#fafafa; margin-bottom:8px; }
    .ib-bubble-wrap { display:flex; margin:5px 0; }
    .ib-bubble-user { margin-left:auto; max-width:65%; }
    .ib-bubble-lead { margin-right:auto; max-width:65%; }
    .ib-bubble-sys  { margin:3px auto; max-width:75%; text-align:center; }
    .ib-bubble-user .ib-body { background:#6366f1; color:#fff; border-radius:18px 18px 4px 18px; padding:9px 13px; font-size:14px; }
    .ib-bubble-lead .ib-body { background:#f1f5f9; color:#1e293b; border-radius:18px 18px 18px 4px; padding:9px 13px; font-size:14px; }
    .ib-bubble-sys  .ib-body { background:#fef9c3; color:#92400e; border-radius:8px; padding:5px 12px; font-size:12px; }
    .ib-bubble-user .ib-ts   { font-size:10px; color:#94a3b8; text-align:right; margin-top:2px; padding:0 3px; }
    .ib-bubble-lead .ib-ts   { font-size:10px; color:#94a3b8; margin-top:2px; padding:0 3px; }
    .ib-chat-header { background:#fff; border:1px solid #e2e8f0; border-radius:10px; padding:10px 14px; margin-bottom:8px; }
    .ib-chat-title  { font-size:16px; font-weight:700; color:#1e293b; }
    .ib-chat-meta   { font-size:12px; color:#64748b; margin-top:2px; }
</style>
""", unsafe_allow_html=True)

_CURRENCY_SYMBOL = {"BRL": "R$", "USD": "$", "EUR": "€", "GBP": "£"}

_ACTIVITY_ICON = {
    "lead_created":              "🟢",
    "lead_updated":              "✏️",
    "lead_moved":                "↗️",
    "lead_captured":             "📡",
    "lead_updated_from_webhook": "🔄",
    "lead_capture_error":        "⚠️",
    "lead_tagged":               "🏷️",
    "email_sent":                "📧",
    "whatsapp_sent":             "📱",
    "user_login":                "🔐",
    "stage_created":             "🏷️",
    "task_created":              "📋",
    "task_completed":            "✅",
    "followup_created":          "🔔",
}

_TAG_STYLE = {
    "facebook":   ("background:#1877f2;color:#fff",  "fb"),
    "google":     ("background:#ea4335;color:#fff",  "G"),
    "tiktok":     ("background:#010101;color:#fff",  "tt"),
    "organic":    ("background:#22c55e;color:#fff",  "org"),
    "paid":       ("background:#8b5cf6;color:#fff",  "paid"),
    "referral":   ("background:#f59e0b;color:#fff",  "ref"),
    "high_ticket":("background:#fbbf24;color:#1e293b","💰"),
}

_SOURCE_LABEL = {
    "meta_lead_ads":    "Meta Lead Ads",
    "custom":           "Formulário",
    "landing_page":     "Landing Page",
    "google_lead_forms":"Google Leads",
    "tiktok_ads":       "TikTok Ads",
    "zapier":           "Zapier",
    "n8n":              "n8n",
    "unknown":          "Desconhecido",
}

_PRIORITY_COLOR = {"high": "#ef4444", "medium": "#f59e0b", "low": "#22c55e"}
_PRIORITY_LABEL = {"high": "Alta", "medium": "Média", "low": "Baixa"}
_STATUS_COLOR   = {"pending": "#3b82f6", "overdue": "#ef4444", "completed": "#22c55e"}
_STATUS_LABEL   = {"pending": "Pendente", "overdue": "Atrasada", "completed": "Concluída"}


def _currency_fmt(value: float, currency: str) -> str:
    symbol = _CURRENCY_SYMBOL.get(currency, currency)
    return f"{symbol} {value:,.2f}"


def _tag_badges_html(tags: list | None) -> str:
    if not tags:
        return ""
    parts = []
    for tag in tags:
        style, label = _TAG_STYLE.get(tag, ("background:#e2e8f0;color:#475569", tag))
        parts.append(
            f'<span style="display:inline-block;{style};font-size:10px;font-weight:700;'
            f'padding:1px 6px;border-radius:99px;margin-right:3px;">{label}</span>'
        )
    return "".join(parts)


def _utm_info_html(lead: dict) -> str:
    parts = []
    if lead.get("utm_source"):
        parts.append(lead["utm_source"])
    if lead.get("campaign_name"):
        parts.append(f'<em>{lead["campaign_name"]}</em>')
    elif lead.get("utm_campaign"):
        parts.append(f'<em>{lead["utm_campaign"]}</em>')
    if not parts:
        return ""
    return (
        f'<div style="font-size:11px;color:#94a3b8;margin-top:2px;">'
        f'📡 {"&nbsp;·&nbsp;".join(parts)}</div>'
    )


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


# ── Filtros de campanha ───────────────────────────────────────────────────────
with st.expander("🔍 Filtrar por Campanha / Origem", expanded=False):
    _all_sources   = sorted({l.get("utm_source") or l.get("source") or "" for l in leads if l.get("utm_source") or l.get("source")})
    _all_campaigns = sorted({l.get("campaign_name") or l.get("utm_campaign") or "" for l in leads if l.get("campaign_name") or l.get("utm_campaign")})
    _all_tags      = sorted({t for l in leads for t in (l.get("tags") or [])})

    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        filt_source = st.selectbox("Origem", ["Todas"] + _all_sources, key="filt_source")
    with fc2:
        filt_campaign = st.selectbox("Campanha", ["Todas"] + _all_campaigns, key="filt_campaign")
    with fc3:
        filt_tag = st.selectbox("Tag", ["Todas"] + _all_tags, key="filt_tag")

    if st.button("Limpar Filtros", key="clear_filters"):
        st.session_state.pop("filt_source", None)
        st.session_state.pop("filt_campaign", None)
        st.session_state.pop("filt_tag", None)
        st.rerun()


def _lead_passes_filter(lead: dict) -> bool:
    src      = st.session_state.get("filt_source", "Todas")
    camp     = st.session_state.get("filt_campaign", "Todas")
    tag_filt = st.session_state.get("filt_tag", "Todas")
    if src != "Todas":
        lead_src = lead.get("utm_source") or lead.get("source") or ""
        if lead_src != src:
            return False
    if camp != "Todas":
        lead_camp = lead.get("campaign_name") or lead.get("utm_campaign") or ""
        if lead_camp != camp:
            return False
    if tag_filt != "Todas":
        if tag_filt not in (lead.get("tags") or []):
            return False
    return True


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

        visible_leads = [l for l in stage_leads if _lead_passes_filter(l)]
        if not visible_leads:
            st.markdown('<div class="empty-stage">Nenhum lead</div>', unsafe_allow_html=True)
            continue

        for lead in visible_leads:
            phone_line  = f'<div class="lead-info">📞 {lead["phone"]}</div>' if lead.get("phone") else ""
            source_line = f'<span class="badge">📍 {lead["source"]}</span>' if lead.get("source") else ""
            budget_line = (
                f'<span class="badge-budget">💰 {_currency_fmt(lead["budget"], currency)}</span>'
                if lead.get("budget") else ""
            )
            tag_html = _tag_badges_html(lead.get("tags"))
            utm_html = _utm_info_html(lead)

            # Classe do card: com ou sem área de movimentação abaixo
            card_class = "lead-card" if can_move else "lead-card-simple"
            tag_row = '<div style="margin-top:4px">' + tag_html + '</div>' if tag_html else ""
            card_html = (
                '<div class="' + card_class + '" style="border-left: 4px solid ' + color + ';">'
                + '<div class="lead-name">' + lead["name"] + '</div>'
                + '<div class="lead-info">✉️ ' + lead["email"] + '</div>'
                + phone_line
                + '<div style="margin-top:4px">' + source_line + budget_line + '</div>'
                + tag_row
                + utm_html
                + '</div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)

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


# ── Painel de Tarefas ─────────────────────────────────────────────────────────
st.divider()
st.markdown("## 📋 Tarefas & Follow-ups")

# Feedback de tarefa
if "_task_ok" in st.session_state:
    st.success(st.session_state.pop("_task_ok"))
if "_task_err" in st.session_state:
    st.error(st.session_state.pop("_task_err"))


def _task_card_html(t: dict) -> str:
    priority   = t.get("priority", "medium")
    status     = t.get("status", "pending")
    due        = t["due_date"][:16].replace("T", " ") if t.get("due_date") else "—"
    lead_badge = f'<span class="badge">👤 {t["lead_name"]}</span>' if t.get("lead_name") else ""
    user_badge = f'<span class="badge">🧑 {t["assigned_user_name"]}</span>' if t.get("assigned_user_name") else ""
    desc_line  = f'<div class="task-desc">{t["description"]}</div>' if t.get("description") else ""
    return (
        f'<div class="task-card" style="border-left: 4px solid {_PRIORITY_COLOR.get(priority, "#94a3b8")};">'
        f'  <div class="task-title">{t["title"]}</div>'
        f'  {desc_line}'
        f'  <div style="margin-top:6px">'
        f'    <span class="badge-priority-{priority}">⚡ {_PRIORITY_LABEL.get(priority, priority)}</span>'
        f'    <span class="badge-status-{status}">{_STATUS_LABEL.get(status, status)}</span>'
        f'    {lead_badge}{user_badge}'
        f'  </div>'
        f'  <div class="task-meta">📅 Vence: {due}</div>'
        f'</div>'
    )


# ── Dashboard de métricas de tarefas ─────────────────────────────────────────
_summary = get_task_summary(token)
tm1, tm2, tm3, tm4 = st.columns(4)
tm1.metric("⏳ Pendentes",  _summary.get("pending", 0))
tm2.metric("🚨 Atrasadas",  _summary.get("overdue", 0))
tm3.metric("📅 Vencem Hoje", _summary.get("due_today", 0))
tm4.metric("✅ Concluídas", _summary.get("completed", 0))

tab_hoje, tab_atrasadas, tab_agenda, tab_nova = st.tabs(
    ["📅 Hoje", "🚨 Atrasadas", "🗓️ Agenda", "➕ Nova Tarefa"]
)

# ── Aba: Hoje ────────────────────────────────────────────────────────────────
with tab_hoje:
    today_data  = get_tasks(token, due_today=True, limit=50)
    today_items = today_data.get("items", [])
    st.caption(f"{len(today_items)} tarefa(s) para hoje")

    if not today_items:
        st.info("Nenhuma tarefa para hoje. 🎉")
    else:
        for t in today_items:
            st.markdown(_task_card_html(t), unsafe_allow_html=True)
            if t["status"] != "completed":
                if st.button("✅ Concluir", key=f"done_today_{t['id']}"):
                    try:
                        complete_task(t["id"], token)
                        st.session_state["_task_ok"] = f"Tarefa **{t['title']}** concluída!"
                    except Exception as e:
                        st.session_state["_task_err"] = str(e)
                    st.rerun()

# ── Aba: Atrasadas ───────────────────────────────────────────────────────────
with tab_atrasadas:
    overdue_data  = get_tasks(token, overdue_only=True, limit=50)
    overdue_items = overdue_data.get("items", [])
    st.caption(f"{overdue_items and len(overdue_items) or 0} tarefa(s) atrasada(s)")

    if not overdue_items:
        st.success("Nenhuma tarefa atrasada!")
    else:
        for t in overdue_items:
            st.markdown(_task_card_html(t), unsafe_allow_html=True)
            if st.button("✅ Concluir", key=f"done_over_{t['id']}"):
                try:
                    complete_task(t["id"], token)
                    st.session_state["_task_ok"] = f"Tarefa **{t['title']}** concluída!"
                except Exception as e:
                    st.session_state["_task_err"] = str(e)
                st.rerun()

# ── Aba: Agenda ──────────────────────────────────────────────────────────────
with tab_agenda:
    col_filt1, col_filt2, col_sync = st.columns([2, 2, 1])
    with col_filt1:
        filt_status = st.selectbox(
            "Status", ["Todos", "Pendente", "Atrasada", "Concluída"],
            key="agenda_status", label_visibility="collapsed",
        )
    with col_filt2:
        filt_priority = st.selectbox(
            "Prioridade", ["Todas", "Alta", "Média", "Baixa"],
            key="agenda_priority", label_visibility="collapsed",
        )
    with col_sync:
        if role in ("admin", "manager") and st.button("🔄", help="Criar lembretes para leads parados", use_container_width=True):
            try:
                r = refresh_tasks(token)
                st.session_state["_task_ok"] = (
                    f"Sincronizado: {r.get('overdue_updated',0)} overdue, "
                    f"{r.get('reminders_created',0)} lembretes criados."
                )
            except Exception as e:
                st.session_state["_task_err"] = str(e)
            st.rerun()

    _status_map   = {"Todos": None, "Pendente": "pending", "Atrasada": "overdue", "Concluída": "completed"}
    _priority_map = {"Todas": None, "Alta": "high", "Média": "medium", "Baixa": "low"}
    agenda_data  = get_tasks(
        token,
        status=_status_map[filt_status],
        priority=_priority_map[filt_priority],
        limit=100,
    )
    agenda_items = agenda_data.get("items", [])
    st.caption(f"{agenda_data.get('total', 0)} tarefa(s)")

    if not agenda_items:
        st.info("Nenhuma tarefa encontrada com esses filtros.")
    else:
        for t in agenda_items:
            st.markdown(_task_card_html(t), unsafe_allow_html=True)
            if t["status"] != "completed":
                if st.button("✅ Concluir", key=f"done_ag_{t['id']}"):
                    try:
                        complete_task(t["id"], token)
                        st.session_state["_task_ok"] = f"Tarefa **{t['title']}** concluída!"
                    except Exception as e:
                        st.session_state["_task_err"] = str(e)
                    st.rerun()

# ── Aba: Nova Tarefa ─────────────────────────────────────────────────────────
with tab_nova:
    with st.form("form_task", clear_on_submit=True):
        t_title    = st.text_input("Título *")
        t_desc     = st.text_area("Descrição", height=80)
        tc1, tc2   = st.columns(2)
        with tc1:
            t_priority = st.selectbox("Prioridade", ["Média", "Alta", "Baixa"])
        with tc2:
            t_due = st.date_input("Vencimento")
        t_lead_sel = st.selectbox(
            "Lead (opcional)",
            ["— nenhum —"] + [f'{l["name"]} ({l["email"]})' for l in leads],
            key="task_lead_sel",
        )
        t_submit = st.form_submit_button("Criar Tarefa", use_container_width=True, type="primary")

    if t_submit:
        if not t_title:
            st.error("Título é obrigatório.")
        else:
            _prio_map = {"Alta": "high", "Média": "medium", "Baixa": "low"}
            payload: dict = {
                "title":    t_title,
                "priority": _prio_map[t_priority],
                "due_date": t_due.isoformat() + "T09:00:00",
            }
            if t_desc:
                payload["description"] = t_desc
            if t_lead_sel != "— nenhum —":
                lead_label_map = {f'{l["name"]} ({l["email"]})': l["id"] for l in leads}
                payload["lead_id"] = lead_label_map.get(t_lead_sel)
            try:
                create_task(payload, token)
                st.session_state["_task_ok"] = f"Tarefa **{t_title}** criada!"
                st.rerun()
            except Exception as e:
                st.error(f"Erro: {e}")


# ── Painel de Captura Automática ──────────────────────────────────────────────
st.divider()
st.markdown("## 📡 Captura Automática de Leads")

if role not in ("admin", "manager"):
    st.info("Painel disponível apenas para manager e admin.")
else:
    tab_eventos, tab_stats, tab_teste = st.tabs(
        ["📋 Eventos", "📊 Estatísticas", "🧪 Teste Meta"]
    )

    # ── Aba: Eventos ─────────────────────────────────────────────────────────
    with tab_eventos:
        ev_col1, ev_col2 = st.columns([2, 1])
        with ev_col1:
            ev_source = st.selectbox(
                "Plataforma",
                ["Todas", "meta_lead_ads", "custom", "landing_page",
                 "google_lead_forms", "tiktok_ads", "zapier", "n8n"],
                key="ev_source",
            )
        with ev_col2:
            ev_proc = st.selectbox("Status", ["Todos", "Processado", "Com erro"], key="ev_proc")

        src_param  = None if ev_source == "Todas" else ev_source
        proc_param = None
        if ev_proc == "Processado": proc_param = True
        if ev_proc == "Com erro":   proc_param = False

        ev_data  = get_capture_events(token, page=1, limit=50, source=src_param, processed=proc_param)
        ev_items = ev_data.get("items", [])
        st.caption(f"{ev_data.get('total', 0)} evento(s)")

        if not ev_items:
            st.info("Nenhum evento de captura encontrado.")
        else:
            for ev in ev_items:
                src_label = _SOURCE_LABEL.get(ev["source"], ev["source"])
                ts        = (ev.get("created_at") or "")[:16].replace("T", " ")
                status_icon = "✅" if ev["processed"] else "❌"
                lead_link   = f'Lead #{ev["lead_id"]}' if ev.get("lead_id") else "—"
                err_text    = f' · `{ev["error"]}`' if ev.get("error") else ""
                st.markdown(
                    f'{status_icon} **{src_label}** · {ts} · {lead_link}{err_text}'
                )

    # ── Aba: Estatísticas ─────────────────────────────────────────────────────
    with tab_stats:
        stats = get_capture_stats(token)
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("Total de Eventos", stats.get("total", 0))
        sc2.metric("✅ Processados",   stats.get("processed", 0))
        sc3.metric("❌ Com Erro",      stats.get("failed", 0))

        by_source = stats.get("by_source", {})
        if by_source:
            st.markdown("#### Por plataforma")
            for src, counts in by_source.items():
                label = _SOURCE_LABEL.get(src, src)
                st.markdown(
                    f"- **{label}**: {counts['total']} total "
                    f"({counts['processed']} ok / {counts['failed']} erro)"
                )
        else:
            st.info("Nenhum dado ainda.")

    # ── Aba: Teste Meta ───────────────────────────────────────────────────────
    with tab_teste:
        st.markdown(
            "Simula um webhook **Meta Lead Ads** para testar a integração "
            "sem precisar de uma campanha real."
        )
        with st.form("form_meta_test", clear_on_submit=True):
            mt1, mt2 = st.columns(2)
            with mt1:
                mt_name      = st.text_input("Nome *")
                mt_email     = st.text_input("Email *")
                mt_phone     = st.text_input("Telefone")
            with mt2:
                mt_campaign  = st.text_input("Campanha", value="Teste Campanha")
                mt_adset     = st.text_input("Adset",    value="Teste Adset")
                mt_ad        = st.text_input("Anúncio",  value="Teste Ad")
            mt_budget    = st.number_input("Budget (opcional)", min_value=0.0, step=500.0, format="%.2f")
            mt_submit    = st.form_submit_button("▶ Disparar Teste", use_container_width=True, type="primary")

        if mt_submit:
            if not mt_name or not mt_email:
                st.error("Nome e email são obrigatórios.")
            else:
                ws_slug = workspace.get("slug", "")
                body = {
                    "workspace_slug": ws_slug,
                    "name":           mt_name,
                    "email":          mt_email,
                    "phone":          mt_phone or None,
                    "campaign_name":  mt_campaign or None,
                    "adset_name":     mt_adset   or None,
                    "ad_name":        mt_ad      or None,
                    "budget":         mt_budget  or None,
                    "utm_medium":     "paid",
                }
                try:
                    result = post_meta_test(body, token)
                    acao   = result.get("acao", "?")
                    tags   = result.get("tags", [])
                    lead_r = result.get("lead", {})
                    st.success(
                        f"Lead **{lead_r.get('name')}** {acao}! "
                        f"Tags: {', '.join(tags) if tags else '—'} · "
                        f"Event #{result.get('event_id')}"
                    )
                    with st.expander("Ver envelope Meta enviado"):
                        st.json(result.get("envelope", {}))
                except Exception as e:
                    st.error(f"Erro: {e}")


# ── Inbox Omnichannel ─────────────────────────────────────────────────────────
st.divider()
st.markdown("## 📬 Inbox Omnichannel")

_IB_CH_ICON  = {"whatsapp": "📱", "email": "📧", "sms": "💬"}
_IB_CH_LABEL = {"whatsapp": "WhatsApp", "email": "E-mail", "sms": "SMS"}
_IB_ST_LABEL = {"open": "Aberta", "closed": "Encerrada"}
_IB_STATUS_MAP  = {"Abertas": "open", "Encerradas": "closed", "Todas": None}
_IB_CHANNEL_MAP = {"Todos": None, "WhatsApp": "whatsapp", "Email": "email", "SMS": "sms"}


def _ib_ts(iso: str) -> str:
    return (iso or "")[:16].replace("T", " ")


def _ib_conv_html(conv: dict, active: bool) -> str:
    ch    = conv.get("channel", "")
    icon  = _IB_CH_ICON.get(ch, "💬")
    label = _IB_CH_LABEL.get(ch, ch)
    lead  = conv.get("lead_name") or "Sem lead"
    ts    = _ib_ts(conv.get("last_message_at") or conv.get("created_at", ""))
    st_b  = "ib-badge-open" if conv["status"] == "open" else "ib-badge-closed"
    st_l  = _IB_ST_LABEL.get(conv["status"], conv["status"])
    cls   = "ib-conv-card ib-active" if active else "ib-conv-card"
    subj  = (" · " + conv["subject"]) if conv.get("subject") else ""
    return (
        '<div class="' + cls + '">'
        + '<div class="ib-conv-lead">' + icon + " " + lead + '</div>'
        + '<div class="ib-conv-sub">' + label + subj + '</div>'
        + '<div class="ib-conv-ts">' + ts + '&nbsp;<span class="' + st_b + '">' + st_l + '</span></div>'
        + '</div>'
    )


def _ib_bubble_html(msg: dict) -> str:
    st_type = msg.get("sender_type", "system")
    cls     = {"user": "ib-bubble-user", "lead": "ib-bubble-lead"}.get(st_type, "ib-bubble-sys")
    ts      = _ib_ts(msg.get("created_at", ""))
    body    = msg.get("content", "").replace("<", "&lt;").replace(">", "&gt;")
    return (
        '<div class="ib-bubble-wrap">'
        '<div class="' + cls + '">'
        '<div class="ib-body">' + body + '</div>'
        '<div class="ib-ts">' + ts + '</div>'
        '</div></div>'
    )


# Filtros
ib_f1, ib_f2, ib_f3, ib_f4 = st.columns([2, 2, 1, 1])
with ib_f1:
    ib_status_sel  = st.selectbox("Status", ["Abertas", "Encerradas", "Todas"], key="ib_main_status")
with ib_f2:
    ib_channel_sel = st.selectbox("Canal",  ["Todos", "WhatsApp", "Email", "SMS"], key="ib_main_channel")
with ib_f3:
    if st.button("🔄 Atualizar", key="ib_main_refresh", use_container_width=True):
        for k in [k for k in st.session_state if k.startswith("ib_msgs_")]:
            st.session_state.pop(k)
        st.rerun()
with ib_f4:
    if st.button("✖ Fechar", key="ib_close_chat", use_container_width=True):
        st.session_state.pop("ib_selected_conv", None)
        st.rerun()

api_ib_status  = _IB_STATUS_MAP.get(ib_status_sel)
api_ib_channel = _IB_CHANNEL_MAP.get(ib_channel_sel)

conv_resp = get_conversations(token, status=api_ib_status, channel=api_ib_channel, limit=100)
ib_convs  = conv_resp.get("items", [])

ib_col_list, ib_col_chat = st.columns([1, 2], gap="medium")

# ── Lista de conversas ────────────────────────────────────────────────────────
with ib_col_list:
    st.markdown(f"**{conv_resp.get('total', 0)} conversa(s)**")

    with st.expander("➕ Nova conversa"):
        with st.form("form_ib_nova", clear_on_submit=True):
            nc_lead_opts = {"— sem lead —": None}
            nc_lead_opts.update({f'{l["name"]} ({l["email"]})': l["id"] for l in leads})
            nc_lead    = st.selectbox("Lead", list(nc_lead_opts.keys()), key="nc_lead_main")
            nc_channel = st.selectbox("Canal", ["whatsapp", "email", "sms"],  key="nc_ch_main")
            nc_subject = st.text_input("Assunto (e-mail)", key="nc_sub_main")
            nc_ok      = st.form_submit_button("Abrir", use_container_width=True, type="primary")
        if nc_ok:
            nc_payload = {"channel": nc_channel}
            if nc_lead_opts[nc_lead]:
                nc_payload["lead_id"] = nc_lead_opts[nc_lead]
            if nc_subject:
                nc_payload["subject"] = nc_subject
            try:
                new_conv = create_conversation(nc_payload, token)
                st.session_state.ib_selected_conv = new_conv["id"]
                st.rerun()
            except Exception as e:
                st.error(f"Erro: {e}")

    if not ib_convs:
        st.caption("Nenhuma conversa encontrada.")
    else:
        ib_sel = st.session_state.get("ib_selected_conv")
        for conv in ib_convs:
            is_active = (conv["id"] == ib_sel)
            st.markdown(_ib_conv_html(conv, is_active), unsafe_allow_html=True)
            btn_lbl = "✔ Selecionada" if is_active else "Abrir"
            if st.button(btn_lbl, key=f"ib_sel_{conv['id']}", use_container_width=True,
                         type="primary" if is_active else "secondary"):
                st.session_state.ib_selected_conv = conv["id"]
                st.session_state.pop(f"ib_msgs_{conv['id']}", None)
                st.rerun()

# ── Área de chat ──────────────────────────────────────────────────────────────
with ib_col_chat:
    ib_sel = st.session_state.get("ib_selected_conv")

    if not ib_sel:
        st.markdown(
            '<div style="display:flex;align-items:center;justify-content:center;'
            'height:380px;color:#94a3b8;font-size:15px;flex-direction:column;gap:10px;">'
            '<span style="font-size:42px">📬</span>'
            '<span>Selecione uma conversa</span>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        ib_conv = next((c for c in ib_convs if c["id"] == ib_sel), None)
        if not ib_conv:
            st.warning("Conversa não encontrada na lista atual. Ajuste os filtros ou atualize.")
        else:
            msgs_key = f"ib_msgs_{ib_sel}"
            if msgs_key not in st.session_state:
                msgs_data = get_inbox_messages(token, ib_sel, limit=100)
                st.session_state[msgs_key] = msgs_data.get("items", [])
            ib_msgs = st.session_state[msgs_key]

            ch     = ib_conv.get("channel", "")
            icon   = _IB_CH_ICON.get(ch, "💬")
            label  = _IB_CH_LABEL.get(ch, ch)
            lead_n = ib_conv.get("lead_name") or "Sem lead"
            st_b   = "ib-badge-open" if ib_conv["status"] == "open" else "ib-badge-closed"
            st_l   = _IB_ST_LABEL.get(ib_conv["status"], ib_conv["status"])
            subj   = (" · " + ib_conv["subject"]) if ib_conv.get("subject") else ""
            email_ = (" · " + ib_conv["lead_email"]) if ib_conv.get("lead_email") else ""
            phone_ = (" · 📞 " + ib_conv["lead_phone"]) if ib_conv.get("lead_phone") else ""

            st.markdown(
                '<div class="ib-chat-header">'
                '<div class="ib-chat-title">' + icon + " " + lead_n + '</div>'
                '<div class="ib-chat-meta">'
                + label + subj
                + ' · <span class="' + st_b + '">' + st_l + '</span>'
                + email_ + phone_
                + '</div></div>',
                unsafe_allow_html=True,
            )

            # Ações manager+
            if role in ("admin", "manager"):
                ha1, ha2 = st.columns([1, 3])
                with ha1:
                    if ib_conv["status"] == "open":
                        if st.button("🔒 Encerrar", key=f"ib_close_{ib_sel}", use_container_width=True):
                            try:
                                update_conversation(ib_sel, {"status": "closed"}, token)
                                st.session_state.pop(msgs_key, None)
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))
                    else:
                        if st.button("🔓 Reabrir", key=f"ib_open_{ib_sel}", use_container_width=True):
                            try:
                                update_conversation(ib_sel, {"status": "open"}, token)
                                st.session_state.pop(msgs_key, None)
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))

            # Bolhas
            if not ib_msgs:
                st.info("Nenhuma mensagem ainda.")
            else:
                bubbles = "".join(_ib_bubble_html(m) for m in ib_msgs)
                st.markdown('<div class="ib-chat-area">' + bubbles + '</div>', unsafe_allow_html=True)

            # Envio
            if ib_conv["status"] == "open":
                prompt = st.chat_input(f"Mensagem via {label}…", key=f"ib_input_{ib_sel}")
                if prompt:
                    try:
                        send_inbox_message({"conversation_id": ib_sel, "content": prompt}, token)
                        st.session_state.pop(msgs_key, None)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
            else:
                st.caption("Conversa encerrada — reabra para enviar mensagens.")

            # Timeline do lead
            if ib_conv.get("lead_id"):
                with st.expander("🕐 Timeline do lead"):
                    tl_ib = get_lead_timeline(ib_conv["lead_id"], token, limit=15)
                    for act in tl_ib.get("items", []):
                        icon_a = _ACTIVITY_ICON.get(act["type"], "•")
                        ts_a   = act.get("created_at", "")[:16].replace("T", " ")
                        who_a  = act.get("user_name") or "Sistema"
                        st.markdown(
                            icon_a + " " + act["description"] + "  \n"
                            + "<small style='color:#94a3b8'>" + who_a + " · " + ts_a + "</small>",
                            unsafe_allow_html=True,
                        )
                    if not tl_ib.get("items"):
                        st.caption("Sem atividades.")
