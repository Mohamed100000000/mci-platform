// Types mirror the REAL backend Pydantic schemas 1:1 (see ./app/schemas/*.py
// and ./app/models/enums.py in the backend). Do not add fields that don't
// exist on the backend response models — check the schema before extending.

export type UserRole =
  | "admin"
  | "training_manager"
  | "instructor"
  | "assessor"
  | "trainee"
  | "viewer";

export interface User {
  id: string; // uuid
  full_name: string;
  email: string;
  role: UserRole;
  phone: string | null;
  is_active: boolean;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string; // "bearer"
}

export interface OrganizationUnit {
  id: string; // uuid
  name: string;
  unit_type: string;
  imo_number: string | null;
  contact_email: string | null;
  contact_phone: string | null;
}

export interface OrganizationUnitCreateInput {
  name: string;
  unit_type?: string;
  imo_number?: string;
  contact_email?: string;
  contact_phone?: string;
}

// "Trainee" is the backend concept. The frontend UI still labels this
// "Candidate" in places for continuity with the existing design — but the
// data shape and API calls are 100% Trainee.
export interface Trainee {
  id: string; // uuid
  trainee_code: string;
  full_name: string;
  national_id: string | null;
  passport_number: string | null;
  seaman_book_number: string | null;
  nationality: string | null;
  date_of_birth: string | null; // ISO date
  rank: string | null;
  email: string | null;
  phone: string | null;
  organization_unit_id: string | null;
}

export interface TraineeCreateInput {
  trainee_code: string;
  full_name: string;
  national_id?: string;
  passport_number?: string;
  seaman_book_number?: string;
  nationality?: string;
  date_of_birth?: string;
  rank?: string;
  email?: string;
  phone?: string;
  organization_unit_id?: string;
}

export type TraineeUpdateInput = Partial<{
  full_name: string;
  rank: string;
  email: string;
  phone: string;
  organization_unit_id: string;
}>;

export type CourseStatus = "draft" | "scheduled" | "in_progress" | "completed" | "cancelled";

export interface Course {
  id: string; // uuid
  code: string;
  title: string;
  description: string | null;
  stcw_reference: string | null;
  duration_hours: number;
  validity_months: number | null;
  max_capacity: number;
}

export interface CourseCreateInput {
  code: string;
  title: string;
  description?: string;
  stcw_reference?: string;
  duration_hours?: number;
  validity_months?: number;
  max_capacity?: number;
}

export interface CourseSession {
  id: string; // uuid
  course_id: string;
  start_date: string; // ISO date
  end_date: string;
  location: string | null;
  instructor_id: string | null;
  status: CourseStatus;
}

export interface CourseSessionCreateInput {
  course_id: string;
  start_date: string;
  end_date: string;
  location?: string;
  instructor_id?: string;
  status?: CourseStatus;
}

export type EnrollmentStatus =
  | "registered"
  | "confirmed"
  | "attending"
  | "completed"
  | "withdrawn"
  | "failed";

export interface Enrollment {
  id: string;
  trainee_id: string;
  session_id: string;
  status: EnrollmentStatus;
}

export type AttendanceStatus = "present" | "absent" | "late" | "excused";

export interface AttendanceRecord {
  id: string;
  enrollment_id: string;
  session_date: string;
  status: AttendanceStatus;
}

export interface CompetencyCriteria {
  id: string;
  course_id: string;
  code: string;
  title: string;
  description: string | null;
  weight: number;
  max_score: number;
}

export type AssessmentResult = "competent" | "not_yet_competent" | "pending";

export interface CompetencyAssessment {
  id: string;
  trainee_id: string;
  session_id: string;
  criteria_id: string;
  score: number;
  result: AssessmentResult;
  assessed_on: string;
  remarks: string | null;
  assessor_id: string | null;
}

export interface CompetencyAssessmentCreateInput {
  trainee_id: string;
  session_id: string;
  criteria_id: string;
  score: number;
  result?: AssessmentResult;
  assessed_on: string;
  remarks?: string;
}

export type CertificateStatus = "issued" | "expired" | "revoked" | "pending";

export interface Certificate {
  id: string;
  trainee_id: string;
  course_id: string;
  certificate_number: string;
  status: CertificateStatus;
  issued_on: string | null;
  expires_on: string | null;
}

// MCI = Marine Competency Index (0-1000 scale), matches MCIScoreOut exactly.
export interface MciScore {
  id: string;
  trainee_id: string;
  calculated_on: string; // ISO date
  total_score: number;
  attendance_component: number;
  competency_component: number;
  certification_component: number;
  recency_component: number;
  breakdown: Record<string, unknown> | null;
  created_at: string;
}
