"use client";

import { useEffect, useRef, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  MessageSquare,
  Send,
  Phone,
  Mail,
  MessageCircle,
  User,
  Search,
  CheckCheck,
  RefreshCw,
  WifiOff,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { inboxService } from "@/services/inbox.service";
import { useInbox, MSGS_KEY } from "@/hooks/use-inbox";
import { useRealtimeStatus } from "@/hooks/use-realtime";
import type { Conversation, Message } from "@/types";
import { cn } from "@/lib/utils";

// ── Channel config ────────────────────────────────────────────────────────────

const CHANNEL_CONFIG = {
  whatsapp: {
    label: "WhatsApp",
    icon: Phone,
    color: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  },
  email: {
    label: "Email",
    icon: Mail,
    color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  },
  sms: {
    label: "SMS",
    icon: MessageCircle,
    color: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
  },
} as const;

// ── Live indicator ────────────────────────────────────────────────────────────

function LiveDot() {
  const status = useRealtimeStatus();
  return (
    <span
      title={status === "connected" ? "Ao vivo" : status === "connecting" ? "Conectando…" : "Offline"}
      className={cn(
        "flex items-center justify-center h-5 w-5 rounded-full transition-colors",
        status === "connected" ? "text-emerald-500" : "text-muted-foreground/40",
      )}
    >
      {status === "connected" ? (
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-60" />
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
        </span>
      ) : status === "connecting" ? (
        <RefreshCw className="h-3.5 w-3.5 animate-spin" />
      ) : (
        <WifiOff className="h-3.5 w-3.5" />
      )}
    </span>
  );
}

// ── Conversation item ─────────────────────────────────────────────────────────

function ConversationItem({
  conversation,
  selected,
  unread,
  onClick,
}: {
  conversation: Conversation;
  selected: boolean;
  unread: boolean;
  onClick: () => void;
}) {
  const channel = CHANNEL_CONFIG[conversation.channel as keyof typeof CHANNEL_CONFIG] ?? CHANNEL_CONFIG.email;
  const ChannelIcon = channel.icon;

  return (
    <button
      onClick={onClick}
      className={cn(
        "w-full text-left p-3 rounded-lg transition-colors relative",
        selected ? "bg-primary/10 border border-primary/20" : "hover:bg-muted/50",
      )}
    >
      {unread && (
        <span className="absolute top-3 right-3 h-2 w-2 rounded-full bg-primary" />
      )}
      <div className="flex items-start gap-3">
        <div className="h-9 w-9 rounded-full bg-muted flex items-center justify-center shrink-0">
          <User className="h-4 w-4 text-muted-foreground" />
        </div>
        <div className="flex-1 min-w-0 pr-4">
          <div className="flex items-center justify-between gap-2">
            <p className={cn("text-sm truncate", unread ? "font-semibold" : "font-medium")}>
              {conversation.lead_name ?? "Contato desconhecido"}
            </p>
            <span className={cn("text-[10px] px-1.5 py-0.5 rounded-full font-medium shrink-0", channel.color)}>
              <ChannelIcon className="h-3 w-3 inline mr-0.5" />
              {channel.label}
            </span>
          </div>
          {conversation.subject && (
            <p className="text-xs text-muted-foreground truncate mt-0.5">{conversation.subject}</p>
          )}
          {conversation.last_message_at && (
            <p className="text-xs text-muted-foreground mt-0.5">
              {new Date(conversation.last_message_at).toLocaleString("pt-BR", {
                day: "2-digit",
                month: "2-digit",
                hour: "2-digit",
                minute: "2-digit",
              })}
            </p>
          )}
        </div>
      </div>
      {conversation.status === "closed" && (
        <div className="flex justify-end mt-1">
          <CheckCheck className="h-3 w-3 text-muted-foreground" />
        </div>
      )}
    </button>
  );
}

// ── Message bubble ────────────────────────────────────────────────────────────

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.sender_type === "user";
  const isSystem = message.sender_type === "system";

  return (
    <div className={cn("flex", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[70%] rounded-2xl px-4 py-2.5 text-sm transition-opacity",
          isUser
            ? "bg-primary text-primary-foreground rounded-br-sm"
            : isSystem
            ? "bg-muted text-muted-foreground text-xs italic rounded-xl px-3 py-1.5"
            : "bg-muted text-foreground rounded-bl-sm",
          message._optimistic && "opacity-60",
        )}
      >
        <p className="leading-relaxed">{message.content}</p>
        <p className={cn(
          "text-[10px] mt-1",
          isUser ? "text-primary-foreground/70 text-right" : "text-muted-foreground",
        )}>
          {new Date(message.created_at).toLocaleTimeString("pt-BR", {
            hour: "2-digit",
            minute: "2-digit",
          })}
          {message._optimistic && " · enviando…"}
        </p>
      </div>
    </div>
  );
}

// ── Message panel ─────────────────────────────────────────────────────────────

function MessagePanel({ conversation }: { conversation: Conversation }) {
  const queryClient = useQueryClient();
  const [draft, setDraft] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  const { data: messages = [] } = useQuery<Message[]>({
    queryKey: MSGS_KEY(conversation.id),
    queryFn: () => inboxService.getMessages(conversation.id),
    staleTime: 60_000,
    // No polling — WS pushes new messages
  });

  // Scroll to bottom whenever messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length]);

  const sendMutation = useMutation({
    mutationFn: (content: string) => inboxService.sendMessage(conversation.id, content),

    onMutate: async (content) => {
      await queryClient.cancelQueries({ queryKey: MSGS_KEY(conversation.id) });
      const previous = queryClient.getQueryData<Message[]>(MSGS_KEY(conversation.id));
      const tempId = -Date.now();
      const optimistic: Message = {
        id: tempId,
        conversation_id: conversation.id,
        sender_type: "user",
        content,
        message_type: "text",
        created_at: new Date().toISOString(),
        _optimistic: true,
      };
      queryClient.setQueryData<Message[]>(MSGS_KEY(conversation.id), (old = []) => [
        ...old,
        optimistic,
      ]);
      return { previous, tempId };
    },

    onSuccess: (saved, _, ctx) => {
      // Replace optimistic with real message
      queryClient.setQueryData<Message[]>(MSGS_KEY(conversation.id), (old = []) =>
        old.map((m) => (m.id === ctx?.tempId ? saved : m)),
      );
    },

    onError: (_, __, ctx) => {
      if (ctx?.previous) {
        queryClient.setQueryData(MSGS_KEY(conversation.id), ctx.previous);
      }
    },
  });

  const closeMutation = useMutation({
    mutationFn: () => inboxService.closeConversation(conversation.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
    },
  });

  const channel = CHANNEL_CONFIG[conversation.channel as keyof typeof CHANNEL_CONFIG] ?? CHANNEL_CONFIG.email;
  const ChannelIcon = channel.icon;

  function handleSend(e: React.FormEvent) {
    e.preventDefault();
    const content = draft.trim();
    if (!content) return;
    setDraft("");
    sendMutation.mutate(content);
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-full bg-muted flex items-center justify-center">
            <User className="h-4 w-4 text-muted-foreground" />
          </div>
          <div>
            <p className="font-medium text-sm">
              {conversation.lead_name ?? "Contato desconhecido"}
            </p>
            <div className="flex items-center gap-1 text-xs text-muted-foreground">
              <ChannelIcon className="h-3 w-3" />
              {channel.label}
              {conversation.lead_email && ` · ${conversation.lead_email}`}
              {conversation.lead_phone && ` · ${conversation.lead_phone}`}
            </div>
          </div>
        </div>
        {conversation.status === "open" && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => closeMutation.mutate()}
            disabled={closeMutation.isPending}
          >
            Fechar conversa
          </Button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-2">
            <MessageSquare className="h-8 w-8 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">Nenhuma mensagem ainda</p>
          </div>
        ) : (
          messages.map((msg) => <MessageBubble key={msg.id} message={msg} />)
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      {conversation.status === "open" ? (
        <>
          <Separator />
          <div className="p-4">
            <form className="flex gap-2" onSubmit={handleSend}>
              <Input
                placeholder="Digite uma mensagem..."
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                className="flex-1"
                autoComplete="off"
              />
              <Button type="submit" size="icon" disabled={!draft.trim()}>
                <Send className="h-4 w-4" />
              </Button>
            </form>
          </div>
        </>
      ) : (
        <div className="p-4 text-center">
          <p className="text-sm text-muted-foreground">Conversa encerrada</p>
        </div>
      )}
    </div>
  );
}

// ── Inbox page ────────────────────────────────────────────────────────────────

export default function InboxPage() {
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<"open" | "closed" | "">("open");

  const { conversations, isLoading, unreadIds, markRead } = useInbox(selectedId);

  const filtered = conversations.filter((c) => {
    const matchSearch =
      !search ||
      c.lead_name?.toLowerCase().includes(search.toLowerCase()) ||
      c.subject?.toLowerCase().includes(search.toLowerCase());
    const matchStatus = !statusFilter || c.status === statusFilter;
    return matchSearch && matchStatus;
  });

  const selected = conversations.find((c) => c.id === selectedId) ?? null;
  const openCount = conversations.filter((c) => c.status === "open").length;
  const totalUnread = unreadIds.size;

  function selectConversation(id: number) {
    setSelectedId(id);
    markRead(id);
  }

  return (
    <div className="flex gap-0 h-[calc(100vh-8rem)] -m-6 animate-fade-in">
      {/* Left panel */}
      <div className="w-80 shrink-0 border-r border-border flex flex-col bg-card">
        {/* Header */}
        <div className="p-4 border-b border-border">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <h1 className="font-semibold">Inbox</h1>
              <LiveDot />
            </div>
            <div className="flex items-center gap-1.5">
              {totalUnread > 0 && (
                <Badge variant="destructive" className="text-[10px] h-4 px-1.5">
                  {totalUnread}
                </Badge>
              )}
              {openCount > 0 && (
                <Badge className="text-xs">{openCount} abertas</Badge>
              )}
            </div>
          </div>

          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
            <Input
              placeholder="Buscar..."
              className="pl-8 h-8 text-sm"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <div className="flex gap-1 mt-2 p-0.5 bg-muted rounded-md">
            {(["open", "closed", ""] as const).map((s) => (
              <button
                key={s}
                onClick={() => setStatusFilter(s)}
                className={cn(
                  "flex-1 text-xs py-1 rounded font-medium transition-colors",
                  statusFilter === s
                    ? "bg-background text-foreground shadow-sm"
                    : "text-muted-foreground",
                )}
              >
                {s === "" ? "Todas" : s === "open" ? "Abertas" : "Fechadas"}
              </button>
            ))}
          </div>
        </div>

        {/* List */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {isLoading ? (
            <div className="space-y-2 p-2">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-16 bg-muted/50 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : filtered.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full py-12 gap-2">
              <MessageSquare className="h-8 w-8 text-muted-foreground" />
              <p className="text-xs text-muted-foreground text-center">
                {search ? "Nenhuma conversa encontrada" : "Nenhuma conversa"}
              </p>
            </div>
          ) : (
            filtered.map((conv) => (
              <ConversationItem
                key={conv.id}
                conversation={conv}
                selected={conv.id === selectedId}
                unread={unreadIds.has(conv.id)}
                onClick={() => selectConversation(conv.id)}
              />
            ))
          )}
        </div>
      </div>

      {/* Right panel */}
      <div className="flex-1 bg-background overflow-hidden">
        {selected ? (
          <MessagePanel key={selected.id} conversation={selected} />
        ) : (
          <div className="flex flex-col items-center justify-center h-full gap-3">
            <MessageSquare className="h-12 w-12 text-muted-foreground" />
            <div className="text-center">
              <p className="font-medium text-muted-foreground">Selecione uma conversa</p>
              <p className="text-sm text-muted-foreground mt-1">
                Escolha uma conversa à esquerda para começar
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
