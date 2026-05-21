import { api } from "./api";
import type { Task, TaskSummary } from "@/types";

interface PaginatedTasks {
  items: Task[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface TaskCreate {
  title: string;
  description?: string;
  lead_id?: number;
  assigned_user_id?: number;
  priority?: "low" | "medium" | "high";
  due_date?: string;
}

export const tasksService = {
  async getTasks(status?: string): Promise<Task[]> {
    const { data } = await api.get<PaginatedTasks>("/tasks/", {
      params: { ...(status ? { status } : {}), limit: 200 },
    });
    return data.items;
  },

  async createTask(payload: TaskCreate): Promise<Task> {
    const { data } = await api.post<Task>("/tasks/", payload);
    return data;
  },

  async completeTask(id: number): Promise<Task> {
    const { data } = await api.patch<Task>(`/tasks/${id}/complete`);
    return data;
  },

  async updateStatus(id: number, status: Task["status"]): Promise<Task> {
    const { data } = await api.patch<Task>(`/tasks/${id}/status`, { status });
    return data;
  },

  async getSummary(): Promise<TaskSummary> {
    const { data } = await api.get<TaskSummary>("/tasks/summary");
    return data;
  },
};
