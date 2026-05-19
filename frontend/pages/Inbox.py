"""
Inbox Omnichannel — página Streamlit.

Layout preparado para migração React/Next.js:
  - Conversas = componente ConversationList
  - Chat = componente ChatWindow
  - Cada seção é isolada e sem estado global além do token
  - Dados via REST; ao migrar substitua as chamadas por fetch()/SWR
"""

import sys
import os
import time

import streamlit as st

# Permite importar api.py que está um nível acima
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api import (
    get_leads,
    get_conversations,
    get_conversation,
    create_conversation,
    update_conversation,
    get_inbox_messages,
    send_inbox_message,
    get_lead_timeline,
)

# ── Configuração da página ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Inbox",
    page_icon="📬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Estilos ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Card de conversa na lista */
  .conv-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 10px 12px;
    margin-bottom: 6px;
    cursor: pointer;
    transition: box-shadow .15s;
  }
  .conv-card:hover { box-shadow: 0 2px 8px rgba(0,0,0,.10); }
  .conv-card.active { border-left: 4px solid #6366f1; background: #f5f3ff; }
  .conv-lead  { font-weight: 700; font-size: 14px; color: #1e293b; }
  .conv-sub   { font-size: 12px; color: #64748b; margin-top: 2px; }
  .conv-ts    { font-size: 11px; color: #94a3b8; }

  /* Status badges */
  .badge-open   { background:#dcfce7; color:#15803d; font-size:11px; font-weight:700;
                  padding:2px 8px; border-radius:99px; display:inline-block; }
  .badge-closed { background:#f1f5f9; color:#64748b; font-size:11px; font-weight:700;
                  padding:2px 8px; border-radius:99px; display:inline-block; }

  /* Bolhas de chat */
  .bubble-wrap  { display:flex; margin: 6px 0; }
  .bubble-user  { margin-left:auto; max-width:65%; }
  .bubble-lead  { margin-right:auto; max-width:65%; }
  .bubble-sys   { margin:4px auto; max-width:70%; text-align:center; }

  .bubble-user .bubble-body {
    background: #6366f1; color: #fff;
    border-radius: 18px 18px 4px 18px;
    padding: 10px 14px; font-size: 14px;
  }
  .bubble-lead .bubble-body {
    background: #f1f5f9; color: #1e293b;
    border-radius: 18px 18px 18px 4px;
    padding: 10px 14px; font-size: 14px;
  }
  .bubble-sys .bubble-body {
    background: #fef9c3; color: #92400e;
    border-radius: 8px; padding: 6px 12px; font-size: 12px;
  }
  .bubble-ts {
    font-size: 10px; color: #94a3b8;
    margin-top: 3px; padding: 0 4px;
  }
  .bubble-user .bubble-ts { text-align: right; }

  /* Área de mensagens */
  .chat-area {
    height: 420px;
    overflow-y: auto;
    padding: 8px 4px;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    background: #fafafa;
  }

  /* Header da conversa */
  .chat-header {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 8px;
  }
  .chat-lead-name { font-size: 17px; font-weight: 700; color: #1e293b; }
  .chat-meta      { font-size: 12px; color: #64748b; margin-top: 2px; }

  /* Canal icons */
  .ch-whatsapp { color: #25d366; font-weight: 700; }
  .ch-email    { color: #6366f1; font-weight: 700; }
  .ch-sms      { color: #f59e0b; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ── Constantes ─────────────────────────────────────────────────────────────────
_CH_ICON  = {"whatsapp": "📱", "email": "📧", "sms": "💬"}
_CH_LABEL = {"whatsapp": "WhatsApp", "email": "E-mail", "sms": "SMS"}
_ST_LABEL = {"open": "Aberta", "closed": "Encerrada"}


def _ts(iso: str) -> str:
    return (iso or "")[:16].replace("T", " ")


def _conv_header(conv: dict) -> str:
    ch    = conv["channel"]
    icon  = _CH_ICON.get(ch, "💬")
    label = _CH_LABEL.get(ch, ch)
    lead  = conv.get("lead_name") or "Sem lead"
    ts    = _ts(conv.get("last_message_at") or conv.get("created_at", ""))
    st_   = "badge-open" if conv["status"] == "open" else "badge-closed"
    st_l  = _ST_LABEL.get(conv["status"], conv["status"])
    return (
        '<div class="conv-card">'
        + '<div class="conv-lead">' + icon + " " + lead + '</div>'
        + '<div class="conv-sub">' + label + ((" · " + conv["subject"]) if conv.get("subject") else "") + '</div>'
        + '<div class="conv-ts">' + ts + '&nbsp;&nbsp;<span class="' + st_ + '">' + st_l + '</span></div>'
        + '</div>'
    )


def _bubble(msg: dict) -> str:
    st_type = msg.get("sender_type", "system")
    cls     = {"user": "bubble-user", "lead": "bubble-lead"}.get(st_type, "bubble-sys")
    ts      = _ts(msg.get("created_at", ""))
    content = msg.get("content", "").replace("<", "&lt;").replace(">", "&gt;")
    return (
        '<div class="bubble-wrap">'
        '<div class="' + cls + '">'
        '<div class="bubble-body">' + content + '</div>'
        '<div class="bubble-ts">' + ts + '</div>'
        '</div></div>'
    )


# ── Guard de autenticação ──────────────────────────────────────────────────────
if "token" not in st.session_state:
    st.warning("Faça login na página principal do CRM antes de acessar o inbox.")
    st.page_link("app.py", label="Ir para o login", icon="🔐")
    st.stop()

token     = st.session_state.token
user      = st.session_state.user
workspace = st.session_state.workspace
role      = user.get("role", "sales")

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📬 Inbox")
    st.caption(f"**{user['name']}** · {role.upper()}")
    st.divider()

    # Filtros
    filt_status  = st.selectbox("Status",  ["Abertas", "Encerradas", "Todas"], key="ib_status")
    filt_channel = st.selectbox("Canal",   ["Todos", "WhatsApp", "Email", "SMS"], key="ib_channel")
    st.divider()

    # Auto-refresh
    st.markdown("**⚡ Atualização**")
    auto_refresh = st.checkbox("Auto-atualizar (30s)", key="ib_auto")
    if st.button("🔄 Atualizar agora", use_container_width=True):
        st.session_state.pop("ib_messages_cache", None)
        st.rerun()

    # Nova conversa
    st.divider()
    st.markdown("**➕ Nova conversa**")
    leads_list = get_leads(token)
    lead_opts  = {"— sem lead —": None}
    lead_opts.update({f'{l["name"]} ({l["email"]})': l["id"] for l in leads_list})

    with st.form("form_nova_conv", clear_on_submit=True):
        nc_lead    = st.selectbox("Lead", list(lead_opts.keys()), key="nc_lead")
        nc_channel = st.selectbox("Canal", ["whatsapp", "email", "sms"], key="nc_channel")
        nc_subject = st.text_input("Assunto (e-mail)", key="nc_subject")
        nc_submit  = st.form_submit_button("Abrir conversa", use_container_width=True, type="primary")

    if nc_submit:
        payload = {"channel": nc_channel}
        if lead_opts[nc_lead]:
            payload["lead_id"] = lead_opts[nc_lead]
        if nc_subject:
            payload["subject"] = nc_subject
        try:
            new_conv = create_conversation(payload, token)
            st.session_state.selected_conv_id = new_conv["id"]
            st.success("Conversa criada!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")

# ── Mapeamento de filtros para params de API ───────────────────────────────────
_status_map  = {"Abertas": "open", "Encerradas": "closed", "Todas": None}
_channel_map = {"Todos": None, "WhatsApp": "whatsapp", "Email": "email", "SMS": "sms"}

api_status  = _status_map.get(st.session_state.get("ib_status",  "Abertas"))
api_channel = _channel_map.get(st.session_state.get("ib_channel", "Todos"))

# ── Auto-refresh: reexecuta se >30s desde a última atualização ─────────────────
if "ib_last_refresh" not in st.session_state:
    st.session_state.ib_last_refresh = time.time()

if auto_refresh and (time.time() - st.session_state.ib_last_refresh) >= 30:
    st.session_state.ib_last_refresh = time.time()
    st.session_state.pop("ib_messages_cache", None)
    st.rerun()

# ── Carrega conversas ──────────────────────────────────────────────────────────
conv_data  = get_conversations(token, status=api_status, channel=api_channel, limit=100)
conv_items = conv_data.get("items", [])

# ── Layout principal: lista | chat ─────────────────────────────────────────────
col_list, col_chat = st.columns([1, 2], gap="medium")

# ═══════════════════════════════════════════════════════════════════
# COLUNA ESQUERDA — lista de conversas
# ═══════════════════════════════════════════════════════════════════
with col_list:
    st.markdown(f"#### Conversas ({conv_data.get('total', 0)})")

    if not conv_items:
        st.info("Nenhuma conversa encontrada.")
    else:
        selected_id = st.session_state.get("selected_conv_id")
        for conv in conv_items:
            is_active = (conv["id"] == selected_id)
            # Card visual (não clicável via HTML puro no Streamlit)
            st.markdown(_conv_header(conv), unsafe_allow_html=True)
            if st.button(
                "Abrir" if not is_active else "✔ Selecionada",
                key=f"sel_{conv['id']}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.selected_conv_id = conv["id"]
                st.session_state.pop("ib_messages_cache", None)
                st.rerun()

# ═══════════════════════════════════════════════════════════════════
# COLUNA DIREITA — chat
# ═══════════════════════════════════════════════════════════════════
with col_chat:
    selected_id = st.session_state.get("selected_conv_id")

    if not selected_id:
        st.markdown("""
        <div style="display:flex;align-items:center;justify-content:center;
                    height:500px;color:#94a3b8;font-size:16px;flex-direction:column;gap:12px;">
          <span style="font-size:48px;">📬</span>
          <span>Selecione uma conversa para começar</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        # ── Carrega conversa e mensagens ───────────────────────────────────
        try:
            conv = get_conversation(token, selected_id)
        except Exception:
            st.error("Conversa não encontrada.")
            st.stop()

        # Cache local de mensagens para não recarregar a cada rerun trivial
        cache_key = f"ib_messages_cache_{selected_id}"
        if cache_key not in st.session_state:
            msg_data = get_inbox_messages(token, selected_id, limit=100)
            st.session_state[cache_key] = msg_data.get("items", [])
        messages = st.session_state[cache_key]

        ch      = conv["channel"]
        icon    = _CH_ICON.get(ch, "💬")
        label   = _CH_LABEL.get(ch, ch)
        lead_n  = conv.get("lead_name") or "Sem lead"
        st_cls  = "badge-open" if conv["status"] == "open" else "badge-closed"
        st_lbl  = _ST_LABEL.get(conv["status"], conv["status"])

        # ── Header ────────────────────────────────────────────────────────
        st.markdown(
            '<div class="chat-header">'
            '<div class="chat-lead-name">' + icon + " " + lead_n + "</div>"
            '<div class="chat-meta">'
            + label
            + ((" · " + conv["subject"]) if conv.get("subject") else "")
            + ' · <span class="' + st_cls + '">' + st_lbl + "</span>"
            + ((" · " + conv["lead_email"]) if conv.get("lead_email") else "")
            + ((" · 📞 " + conv["lead_phone"]) if conv.get("lead_phone") else "")
            + "</div></div>",
            unsafe_allow_html=True,
        )

        # ── Ações (manager+) ───────────────────────────────────────────────
        if role in ("admin", "manager"):
            act_col1, act_col2, act_col3 = st.columns([1, 1, 2])
            with act_col1:
                if conv["status"] == "open":
                    if st.button("🔒 Encerrar", use_container_width=True):
                        try:
                            update_conversation(selected_id, {"status": "closed"}, token)
                            st.session_state.pop(cache_key, None)
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
                else:
                    if st.button("🔓 Reabrir", use_container_width=True):
                        try:
                            update_conversation(selected_id, {"status": "open"}, token)
                            st.session_state.pop(cache_key, None)
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
            with act_col2:
                if st.button("🔄 Atualizar msgs", use_container_width=True):
                    st.session_state.pop(cache_key, None)
                    st.rerun()

        # ── Área de mensagens ──────────────────────────────────────────────
        if not messages:
            st.info("Nenhuma mensagem ainda. Envie a primeira mensagem abaixo.")
        else:
            bubbles_html = "".join(_bubble(m) for m in messages)
            st.markdown(
                '<div class="chat-area">' + bubbles_html + '</div>',
                unsafe_allow_html=True,
            )

        # ── Input de envio ─────────────────────────────────────────────────
        if conv["status"] == "open":
            prompt = st.chat_input(
                f"Mensagem via {label}...",
                key=f"chat_input_{selected_id}",
            )
            if prompt:
                try:
                    send_inbox_message(
                        {"conversation_id": selected_id, "content": prompt},
                        token,
                    )
                    st.session_state.pop(cache_key, None)  # invalida cache
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao enviar: {e}")
        else:
            st.caption("⚠️ Conversa encerrada — reabra para enviar mensagens.")

        # ── Timeline do lead ───────────────────────────────────────────────
        if conv.get("lead_id"):
            with st.expander("🕐 Timeline do lead", expanded=False):
                tl = get_lead_timeline(conv["lead_id"], token, limit=15)
                _ICON = {
                    "lead_created": "🟢", "lead_updated": "✏️", "lead_moved": "↗️",
                    "lead_captured": "📡", "lead_updated_from_webhook": "🔄",
                    "conversation_created": "📬", "message_sent": "📤",
                    "message_received": "📥", "conversation_closed": "🔒",
                    "task_created": "📋", "task_completed": "✅",
                    "followup_created": "🔔",
                }
                for act in tl.get("items", []):
                    icon_a = _ICON.get(act["type"], "•")
                    ts_a   = _ts(act.get("created_at", ""))
                    who    = act.get("user_name") or "Sistema"
                    st.markdown(
                        icon_a + " **" + act["description"] + "**  \n"
                        + "<small style='color:#94a3b8'>" + who + " · " + ts_a + "</small>",
                        unsafe_allow_html=True,
                    )
                if not tl.get("items"):
                    st.caption("Sem atividades registradas.")
