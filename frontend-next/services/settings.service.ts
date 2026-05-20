import { api } from "./api";
import type {
  User,
  Workspace,
  WorkspaceSettings,
  WorkspaceSettingsUpdate,
  WorkspaceIntegrations,
  WorkspaceIntegrationsUpdate,
  WorkspaceMember,
  InviteUser,
  UpdateMember,
  ProfileUpdate,
  Stage,
  StageCreate,
  StageUpdate,
} from "@/types";

export const settingsService = {
  // ── Workspace ────────────────────────────────────────────────────────────
  async getWorkspace(): Promise<Workspace> {
    const { data } = await api.get<Workspace>("/workspace/me");
    return data;
  },

  // ── General Settings ─────────────────────────────────────────────────────
  async getSettings(): Promise<WorkspaceSettings> {
    const { data } = await api.get<WorkspaceSettings>("/workspace/settings");
    return data;
  },

  async updateSettings(payload: WorkspaceSettingsUpdate): Promise<WorkspaceSettings> {
    const { data } = await api.put<WorkspaceSettings>("/workspace/settings", payload);
    return data;
  },

  // ── Pipeline Stages ──────────────────────────────────────────────────────
  async getStages(): Promise<Stage[]> {
    const { data } = await api.get<Stage[]>("/pipeline/stages");
    return data;
  },

  async createStage(payload: StageCreate): Promise<Stage> {
    const { data } = await api.post<Stage>("/pipeline/stages", payload);
    return data;
  },

  async updateStage(id: number, payload: StageUpdate): Promise<Stage> {
    const { data } = await api.put<Stage>(`/pipeline/stages/${id}`, payload);
    return data;
  },

  async deleteStage(id: number): Promise<void> {
    await api.delete(`/pipeline/stages/${id}`);
  },

  // ── Team ─────────────────────────────────────────────────────────────────
  async getMembers(): Promise<WorkspaceMember[]> {
    const { data } = await api.get<WorkspaceMember[]>("/workspace/users");
    return data;
  },

  async inviteMember(payload: InviteUser): Promise<WorkspaceMember> {
    const { data } = await api.post<WorkspaceMember>("/workspace/invite", payload);
    return data;
  },

  async updateMember(id: number, payload: UpdateMember): Promise<WorkspaceMember> {
    const { data } = await api.patch<WorkspaceMember>(`/workspace/users/${id}`, payload);
    return data;
  },

  async removeMember(id: number): Promise<void> {
    await api.delete(`/workspace/users/${id}`);
  },

  // ── Profile / Security ────────────────────────────────────────────────────
  async updateProfile(payload: ProfileUpdate): Promise<User> {
    const { data } = await api.patch<User>("/auth/profile", payload);
    return data;
  },

  // ── Integrations ─────────────────────────────────────────────────────────
  async getIntegrations(): Promise<WorkspaceIntegrations> {
    const { data } = await api.get<WorkspaceIntegrations>("/workspace/integrations");
    return data;
  },

  async updateIntegrations(payload: WorkspaceIntegrationsUpdate): Promise<WorkspaceIntegrations> {
    const { data } = await api.put<WorkspaceIntegrations>("/workspace/integrations", payload);
    return data;
  },
};
