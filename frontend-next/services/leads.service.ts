import { api } from "./api";
import type { Lead, LeadCreate, KanbanColumn, Paginated } from "@/types";

export const leadsService = {
  async getLeads(): Promise<Lead[]> {
    const { data } = await api.get<Lead[]>("/leads/");
    return data;
  },

  async createLead(payload: LeadCreate): Promise<Lead> {
    const { data } = await api.post<Lead>("/leads/", payload);
    return data;
  },

  async getBoard(): Promise<KanbanColumn[]> {
    const { data } = await api.get<KanbanColumn[]>("/pipeline/board");
    return data;
  },

  async moveLead(leadId: number, stageId: number): Promise<Lead> {
    const { data } = await api.patch<Lead>(`/leads/${leadId}/move`, { stage_id: stageId });
    return data;
  },

  async getTimeline(leadId: number, page = 1, limit = 50): Promise<Paginated<unknown>> {
    const { data } = await api.get(`/leads/${leadId}/timeline`, { params: { page, limit } });
    return data;
  },
};
