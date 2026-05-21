import { api } from "./api";
import type { Conversation, Message } from "@/types";

export const inboxService = {
  async getConversations(): Promise<Conversation[]> {
    const { data } = await api.get<Conversation[]>("/inbox/conversations");
    return data;
  },

  async getMessages(conversationId: number): Promise<Message[]> {
    const { data } = await api.get<Message[]>(
      `/inbox/conversations/${conversationId}/messages`
    );
    return data;
  },

  async sendMessage(conversationId: number, content: string): Promise<Message> {
    const { data } = await api.post<Message>(
      `/inbox/conversations/${conversationId}/messages`,
      { content, message_type: "text" }
    );
    return data;
  },

  async closeConversation(conversationId: number): Promise<Conversation> {
    const { data } = await api.patch<Conversation>(
      `/inbox/conversations/${conversationId}`,
      { status: "closed" }
    );
    return data;
  },
};
