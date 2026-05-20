// Auth
export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  name: string;
  email: string;
  role: "admin" | "manager" | "sales";
  is_admin: boolean;
  is_active: boolean;
  workspace_id: number;
  created_at: string;
}

// Team
export interface WorkspaceMember {
  id: number;
  name: string;
  email: string;
  role: "admin" | "manager" | "sales";
  is_admin: boolean;
  is_active: boolean;
  workspace_id: number;
  created_at: string;
}

export interface InviteUser {
  name: string;
  email: string;
  password: string;
  role: "admin" | "manager" | "sales";
}

export interface UpdateMember {
  role?: string;
  is_active?: boolean;
}

// Profile
export interface ProfileUpdate {
  name?: string;
  current_password?: string;
  new_password?: string;
}

// Workspace
export interface Workspace {
  id: number;
  name: string;
  slug: string;
  plan: string;
  settings?: Record<string, unknown>;
}

// Leads
export interface Lead {
  id: number;
  workspace_id: number;
  name: string;
  email?: string;
  phone?: string;
  company?: string;
  stage_id?: number;
  stage?: Stage;
  assigned_to?: number;
  value?: number;
  status: string;
  tags?: string[];
  utm_source?: string;
  utm_campaign?: string;
  utm_medium?: string;
  utm_content?: string;
  utm_term?: string;
  campaign_name?: string;
  adset_name?: string;
  ad_name?: string;
  external_source_id?: string;
  created_at: string;
  updated_at?: string;
}

export interface LeadCreate {
  name: string;
  email?: string;
  phone?: string;
  company?: string;
  stage_id?: number;
  value?: number;
}

// Pipeline
export interface Stage {
  id: number;
  name: string;
  order: number;
  color?: string;
}

export interface KanbanColumn {
  stage: Stage;
  leads: Lead[];
}

// Activities
export interface Activity {
  id: number;
  workspace_id: number;
  lead_id?: number;
  user_id?: number;
  type: string;
  description: string;
  meta?: Record<string, unknown>;
  created_at: string;
}

// Tasks
export interface Task {
  id: number;
  workspace_id: number;
  lead_id?: number;
  assigned_to?: number;
  title: string;
  description?: string;
  status: "pending" | "in_progress" | "completed" | "cancelled";
  priority: "low" | "medium" | "high";
  due_date?: string;
  completed_at?: string;
  created_at: string;
}

export interface TaskSummary {
  pending: number;
  overdue: number;
  completed: number;
  due_today: number;
}

// Inbox
export interface Conversation {
  id: number;
  workspace_id: number;
  lead_id?: number;
  lead_name?: string;
  lead_email?: string;
  lead_phone?: string;
  assigned_user_id?: number;
  channel: "whatsapp" | "email" | "sms";
  status: "open" | "closed";
  subject?: string;
  last_message_at?: string;
  created_at: string;
  updated_at?: string;
}

export interface Message {
  id: number;
  conversation_id: number;
  sender_type: "user" | "lead" | "system";
  sender_id?: number;
  content: string;
  message_type: "text" | "image" | "file";
  created_at: string;
}

// Workspace Integrations
export interface WorkspaceIntegrations {
  id: number;
  workspace_id: number;
  whatsapp_token?: string;
  whatsapp_phone_id?: string;
  meta_access_token?: string;
  meta_pixel_id?: string;
  sendgrid_api_key?: string;
  sendgrid_from_email?: string;
  twilio_account_sid?: string;
  twilio_auth_token?: string;
  twilio_from_number?: string;
}

export interface WorkspaceIntegrationsUpdate {
  whatsapp_token?: string;
  whatsapp_phone_id?: string;
  meta_access_token?: string;
  meta_pixel_id?: string;
  sendgrid_api_key?: string;
  sendgrid_from_email?: string;
  twilio_account_sid?: string;
  twilio_auth_token?: string;
  twilio_from_number?: string;
}

// Workspace Settings
export interface WorkspaceSettings {
  id: number;
  workspace_id: number;
  company_name?: string;
  currency: string;
  timezone: string;
  primary_color: string;
  logo_url?: string;
}

export interface WorkspaceSettingsUpdate {
  company_name?: string;
  currency?: string;
  timezone?: string;
  primary_color?: string;
  logo_url?: string;
}

// Stage CRUD
export interface StageCreate {
  name: string;
  order: number;
  color?: string;
}

export interface StageUpdate {
  name?: string;
  order?: number;
  color?: string;
}

// Pagination
export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

// Dashboard metrics
export interface DashboardMetrics {
  total_leads: number;
  leads_this_month: number;
  open_conversations: number;
  tasks_due_today: number;
  tasks_overdue: number;
}
