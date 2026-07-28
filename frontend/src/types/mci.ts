export interface Candidate {
  id: number;
  full_name: string;
  nationality: string | null;
  current_position: string | null;
  years_of_experience: number;
  created_at: string;
}

export interface CandidateCreateInput {
  full_name: string;
  nationality?: string;
  current_position?: string;
  years_of_experience?: number;
  email?: string;
}

export interface FactorDefinition {
  key: string;
  label: string;
  optional: boolean;
}

export interface FactorGroup {
  key: string;
  label: string;
  weight: number;
  factors: FactorDefinition[];
}

export interface CategoryBreakdown {
  key: string;
  label: string;
  weight: number;
  sub_score_0_100: number;
  missing_required_factors: string[];
}

export interface MciResult {
  user_id: number;
  mci_score: number;
  level: string;
  overall_completeness: number;
  categories: CategoryBreakdown[];
  computed_at: string;
}

export interface Position {
  id: number;
  position_title: string;
  description: string | null;
  min_overall_mci: number;
  factor_requirements: Record<string, number>;
}

export interface GapDetail {
  factor_key: string;
  required: number;
  actual: number;
  gap: number;
}

export interface ReadinessResult {
  user_id: number;
  position_id: number;
  position_title: string;
  verdict: "Ready" | "Almost Ready" | "Needs Improvement" | "Not Qualified Yet";
  mci_score: number;
  min_overall_mci: number;
  gap_detail: GapDetail[];
}

export interface SkillGapItem {
  factor_key: string;
  factor_label: string;
  category: string;
  required: number;
  actual: number;
  gap: number;
  priority: "High" | "Medium" | "Low";
}

export interface SkillGapResult {
  user_id: number;
  position_id: number;
  position_title: string;
  items: SkillGapItem[];
}
