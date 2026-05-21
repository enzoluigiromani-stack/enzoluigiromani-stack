import { api } from "./api";

export interface Notification {
  id: number;
  workspace_id: number;
  user_id: number | null;
  type: string;
  title: string;
  message: string | null;
  read: boolean;
  created_at: string;
}

export const notificationsService = {
  async list(unreadOnly = false): Promise<Notification[]> {
    const { data } = await api.get<Notification[]>("/notifications/", {
      params: { unread_only: unreadOnly },
    });
    return data;
  },

  async markRead(id: number): Promise<Notification> {
    const { data } = await api.patch<Notification>(`/notifications/${id}/read`);
    return data;
  },

  async markAllRead(): Promise<void> {
    await api.patch("/notifications/read-all");
  },
};
