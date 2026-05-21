"use client";

import { useState } from "react";
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
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { inboxService } from "@/services/inbox.service";
import type { Conversation, Message } from "@/types";
import { cn } from "@/lib/utils";

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
};

function ConversationItem({
  conversation,
  selected,
  onClick,
}: {
  conversation: Conversation;
  selected: boolean;
  onClick: () => void;
}) {
  const channel = CHANNEL_CONFIG[conversation.channel] ?? CHANNEL_CONFIG.email;
  const ChannelIcon = channel.icon;

  return (
    <button
      onClick={onClick}
      className={cn(
        "w-full text-left p-3 rounded-lg transition-colors",
        selected ? "bg-primary/10 border border-primary/20" : "hover:bg-muted/50"
      )}
    >
      <div className="flex items-start gap-3">
        <div className="h-9 w-9 rounded-full bg-muted flex items-center justify-center shrink-0">
          <User className="h-4 w-4 text-muted-foreground" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <p className="text-sm font-medium truncate">
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

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.sender_type === "user";
  return (
    <div className={cn("flex", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[70%] rounded-2xl px-4 py-2.5 text-sm",
          isUser
            ? "bg-primary text-primary-foreground rounded-br-sm"
            : message.sender_type === "system"
            ? "bg-muted text-muted-foreground text-xs italic rounded-xl px-3 py-1.5"
            : "bg-muted text-foreground rounded-bl-sm"
        )}
      >
        <p className="leading-relaxed">{message.content}</p>
        <p
          className={cn(
            "text-[10px] mt-1",
            isUser ? "text-primary-foreground/70 text-right" : "text-muted-foreground"
          )}
        >
          {new Date(message.created_at).toLocaleTimeString("pt-BR", {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </p>
      </div>
    </div>
  );
}

function MessagePanel({ conversation }: { conversation: Conversation }) {
  const queryClient = useQueryClient();
  const [message, setMessage] = useState("");

  const { data: messages = [] } = useQuery<Message[]>({
    queryKey: ["messages", conversation.id],
    queryFn: () => inboxService.getMessages(conversation.id),
    refetchInterval: 15_000,
  });

  const sendMutation = useMutation({
    mutationFn: (content: string) => inboxService.sendMessage(conversation.id, content),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["messages", conversation.id] });
      setMessage("");
    },
  });

  const closeMutation = useMutation({
    mutationFn: () => inboxService.closeConversation(conversation.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
    },
  });

  const channel = CHANNEL_CONFIG[conversation.channel] ?? CHANNEL_CONFIG.email;
  const ChannelIcon = channel.icon;

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
      </div>

      {/* Input */}
      {conversation.status === "open" && (
        <>
          <Separator />
          <div className="p-4">
            <form
              className="flex gap-2"
              onSubmit={(e) => {
                e.preventDefault();
                if (message.trim()) sendMutation.mutate(message.trim());
              }}
            >
              <Input
                placeholder="Digite uma mensagem..."
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                className="flex-1"
                disabled={sendMutation.isPending}
              />
              <Button
                type="submit"
                size="icon"
                disabled={!message.trim() || sendMutation.isPending}
              >
                <Send className="h-4 w-4" />
              </Button>
            </form>
          </div>
        </>
      )}

      {conversation.status === "closed" && (
        <div className="p-4 text-center">
          <p className="text-sm text-muted-foreground">Conversa encerrada</p>
        </div>
      )}
    </div>
  );
}

export default function InboxPage() {
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<"open" | "closed" | "">("open");

  const { data: conversations = [], isLoading } = useQuery<Conversation[]>({
    queryKey: ["conversations"],
    queryFn: inboxService.getConversations,
    refetchInterval: 30_000,
  });

  const filtered = conversations.filter((c) => {
    const matchSearch =
      !search ||
      c.lead_name?.toLowerCase().includes(search.toLowerCase()) ||
      c.subject?.toLowerCase().includes(search.toLowerCase());
    const matchStatus = !statusFilter || c.status === statusFilter;
    return matchSearch && matchStatus;
  });

  const selected = filtered.find((c) => c.id === selectedId) ?? null;
  const openCount = conversations.filter((c) => c.status === "open").length;

  return (
    <div className="flex gap-0 h-[calc(100vh-8rem)] -m-6 animate-fade-in">
      {/* Left panel: conversation list */}
      <div className="w-80 shrink-0 border-r border-border flex flex-col bg-card">
        {/* Header */}
        <div className="p-4 border-b border-border">
          <div className="flex items-center justify-between mb-3">
            <h1 className="font-semibold">Inbox</h1>
            {openCount > 0 && (
              <Badge className="text-xs">{openCount} abertas</Badge>
            )}
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
            <Input
              placeholder="Buscar..."
              className="pl-8 h-8 text-sm"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          {/* Status filter */}
          <div className="flex gap-1 mt-2 p-0.5 bg-muted rounded-md">
            {(["open", "closed", ""] as const).map((s) => (
              <button
                key={s}
                onClick={() => setStatusFilter(s)}
                className={cn(
                  "flex-1 text-xs py-1 rounded font-medium transition-colors",
                  statusFilter === s
                    ? "bg-background text-foreground shadow-sm"
                    : "text-muted-foreground"
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
                onClick={() => setSelectedId(conv.id)}
              />
            ))
          )}
        </div>
      </div>

      {/* Right panel: message thread */}
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
