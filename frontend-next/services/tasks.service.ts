import { api } from "./api";
import type { Task, TaskSummary } from "@/types";

export interface TaskCreate {
  title: string;
  description?: string;
  lead_id?: number;
  assigned_to?: number;
  priority?: "low" | "medium" | "high";
  due_date?: string;
}

export const tasksService = {
  async getTasks(status?: string): Promise<Task[]> {
    const { data } = await api.get<Task[]>("/tasks/", {
      params: status ? { status } : {},
    });
    return data;
  },

  async createTask(payload: TaskCreate): Promise<Task> {
    const { data } = await api.post<Task>("/tasks/", payload);
    return data;
  },

  async updateTask(id: number, payload: Partial<Task>): Promise<Task> {
    const { data } = await api.patch<Task>(`/tasks/${id}`, payload);
    return data;
  },

  async getSummary(): Promise<TaskSummary> {
    const { data } = await api.get<TaskSummary>("/tasks/summary");
    return data;
  },
};
