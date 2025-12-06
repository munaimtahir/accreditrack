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
  code?: string;
  title: string;
  authority_name: string;
  description: string;
  version: string;
  is_active: boolean;
  sections?: ProformaSection[];
  sections_count?: number;
  module_code?: string;
  module_display_name?: string;
  created_at: string;
  updated_at: string;
}

export interface ProformaSection {
  id: string;
  code: string;
  title: string;
  weight: number;
  section_type?: 'CATEGORY' | 'STANDARD';
  parent_id?: string;
  parent_code?: string;
  items?: ProformaItem[];
  items_count?: number;
  children?: ProformaSection[];
  created_at: string;
  updated_at: string;
}

export interface ProformaItem {
  id: string;
  code: string;
  requirement_text: string;
  required_evidence_type: string;
  importance_level: number | null;
  implementation_criteria?: string;
  max_score?: number;
  weightage_percent?: number;
  is_licensing_critical?: boolean;
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
  status: 'NOT_STARTED' | 'IN_PROGRESS' | 'PENDING_REVIEW' | 'COMPLETED' | 'VERIFIED';
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
  status: 'NOT_STARTED' | 'IN_PROGRESS' | 'PENDING_REVIEW' | 'COMPLETED' | 'VERIFIED' | 'REJECTED';
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
  note: string;
  reference_code: string;
  evidence_type: 'file' | 'image' | 'note' | 'reference';
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

export interface Module {
  id: string;
  code: string;
  display_name: string;
  description: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserModuleRole {
  id: string;
  user: string;
  user_email: string;
  user_full_name: string;
  module: string;
  module_code: string;
  module_display_name: string;
  role: 'SUPERADMIN' | 'DASHBOARD_ADMIN' | 'CATEGORY_ADMIN' | 'USER';
  categories: string[];
  created_at: string;
  updated_at: string;
}

export interface ModuleStats {
  module_id: string;
  module_code: string;
  module_display_name: string;
  total_assignments: number;
  total_items: number;
  overall_completion_percent: number;
  verified_count: number;
  pending_review_count?: number;
  in_progress_count: number;
  not_started_count: number;
  completed_count?: number;
  templates_count: number;
  category_breakdown?: CategoryBreakdown[];
  category_completion?: CategoryCompletion[];
  standard_completion?: StandardCompletion[];
  overdue_assignments?: OverdueAssignment[];
  overall_completion?: number;
}

export interface CategoryBreakdown {
  section_code: string;
  section_title: string;
  total_items: number;
  verified_count: number;
  pending_review_count?: number;
  in_progress_count: number;
  not_started_count: number;
  completed_count?: number;
  completion_percent: number;
}

export interface CategoryCompletion {
  code: string;
  title: string;
  total_indicators: number;
  verified_indicators: number;
  assigned_indicators: number;
  completion_percent: number;
}

export interface StandardCompletion {
  code: string;
  title: string;
  category_code: string | null;
  category_title: string | null;
  total_indicators: number;
  verified_indicators: number;
  completion_percent: number;
}

export interface OverdueAssignment {
  assignment_id: string;
  indicator_code: string;
  indicator_text: string;
  section_code: string;
  due_date: string;
  status: string;
  assigned_to: string[];
  department_name: string | null;
}

export interface ModuleAssignment {
  id: string;
  proforma_template_id: string;
  proforma_template_title: string;
  module_id: string | null;
  module_code: string | null;
  scope_type: 'DEPARTMENT' | 'SECTION' | 'INDICATOR';
  section_code: string | null;
  proforma_item_code: string | null;
  instructions: string;
  start_date: string;
  due_date: string;
  status: 'NOT_STARTED' | 'IN_PROGRESS' | 'PENDING_REVIEW' | 'COMPLETED' | 'VERIFIED';
  total_items: number;
  verified_items: number;
  completion_percent: number;
}

export interface TemplateStats {
  template_id: string;
  template_code: string;
  template_title: string;
  total_indicators: number;
  assigned_indicators: number;
  indicators_with_evidence: number;
}
