import { api } from "./api";
import type { Conversation, Message } from "@/types";

interface PaginatedMessages {
  items: Message[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export const inboxService = {
  async getConversations(): Promise<Conversation[]> {
    const { data } = await api.get<{ items: Conversation[]; total: number }>(
      "/inbox/conversations",
      { params: { limit: 200 } },
    );
    return data.items ?? data;
  },

  async getMessages(conversationId: number): Promise<Message[]> {
    const { data } = await api.get<PaginatedMessages>(
      `/inbox/messages/${conversationId}`,
      { params: { limit: 200 } },
    );
    return data.items;
  },

  async sendMessage(conversationId: number, content: string): Promise<Message> {
    const { data } = await api.post<Message>("/inbox/messages", {
      conversation_id: conversationId,
      content,
      message_type: "text",
    });
    return data;
  },

  async closeConversation(conversationId: number): Promise<Conversation> {
    const { data } = await api.patch<Conversation>(
      `/inbox/conversations/${conversationId}`,
      { status: "closed" },
    );
    return data;
  },
};
