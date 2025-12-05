/**
 * TypeScript types for API responses
 */

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_staff: boolean;
  roles: UserRole[];
  created_at: string;
}

export interface UserRole {
  role: string;
  role_display: string;
  department_id: string | null;
  department_name: string | null;
}

export interface Role {
  id: string;
  name: string;
  description: string;
}

export interface Department {
  id: string;
  name: string;
  code: string;
  parent: string | null;
  parent_name?: string;
  parent_code?: string;
  created_at: string;
  updated_at: string;
}

export interface ProformaTemplate {
  id: string;
  title: string;
  authority_name: string;
  description: string;
  version: string;
  is_active: boolean;
  sections?: ProformaSection[];
  sections_count?: number;
  created_at: string;
  updated_at: string;
}

export interface ProformaSection {
  id: string;
  code: string;
  title: string;
  weight: number;
  items?: ProformaItem[];
  items_count?: number;
  created_at: string;
  updated_at: string;
}

export interface ProformaItem {
  id: string;
  code: string;
  requirement_text: string;
  required_evidence_type: string;
  importance_level: number | null;
  created_at: string;
  updated_at: string;
}

export interface Assignment {
  id: string;
  proforma_template: ProformaTemplate;
  proforma_template_id: string;
  department: Department;
  department_id: string;
  start_date: string;
  due_date: string;
  status: 'NotStarted' | 'InProgress' | 'Completed';
  completion_percent: number;
  items_count: number;
  verified_count: number;
  created_at: string;
  updated_at: string;
}

export interface ItemStatus {
  id: string;
  assignment: string;
  proforma_item: string;
  proforma_item_code: string;
  proforma_item_text: string;
  status: 'NotStarted' | 'InProgress' | 'Submitted' | 'Verified' | 'Rejected';
  completion_percent: number;
  last_updated_by: string | null;
  last_updated_by_email: string | null;
  last_updated_at: string;
  created_at: string;
  updated_at: string;
}

export interface Evidence {
  id: string;
  item_status: string;
  file: string;
  file_url: string;
  file_name: string;
  file_size: number | null;
  description: string;
  uploaded_by: string;
  uploaded_by_email: string;
  uploaded_at: string;
  created_at: string;
}

export interface Comment {
  id: string;
  item_status: string;
  text: string;
  type: 'General' | 'Query' | 'Clarification' | 'NonComplianceNote';
  author: string;
  author_email: string;
  author_name: string;
  created_at: string;
}

export interface DashboardSummary {
  overall_completion_percent: number;
  assignments: AssignmentSummary[];
  sections: SectionSummary[];
}

export interface AssignmentSummary {
  id: string;
  department_name: string;
  completion_percent: number;
  due_date: string;
  status: string;
}

export interface SectionSummary {
  code: string;
  title: string;
  completion_percent: number;
}

export interface PendingItem {
  id: string;
  assignment_id: string;
  assignment_title: string;
  department_name: string;
  item_code: string;
  item_text: string;
  section_code: string;
  status: string;
  due_date: string;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: User;
}
