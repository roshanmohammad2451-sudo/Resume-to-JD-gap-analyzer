export interface PageExtraction {
  page_number: number;
  text: string;
}

export interface PDFExtractionResponse {
  pages: PageExtraction[];
  total_pages: number;
  file_name: string;
}

export interface ResumeSkill {
  name: string;
  evidence: string;
  source_section: string;
  confidence: number;
}

export interface ResumeEducation {
  degree?: string;
  institution?: string;
  dates?: string;
  details?: string;
}

export interface ResumeExperience {
  title?: string;
  company?: string;
  dates?: string;
  responsibilities: string[];
}

export interface ResumeProject {
  name?: string;
  description?: string;
  technologies: string[];
}

export interface ResumeCertification {
  name?: string;
  issuer?: string;
  date?: string;
}

export interface ResumeProfile {
  name?: string;
  headline?: string;
  education: ResumeEducation[];
  experience: ResumeExperience[];
  projects: ResumeProject[];
  certifications: ResumeCertification[];
  skills: ResumeSkill[];
}

export interface JobSkill {
  name: string;
  evidence: string;
  importance: 'required' | 'preferred';
  source_text: string;
}

export interface JobDescriptionResponse {
  role?: string;
  company?: string;
  summary?: string;
  required_skills: JobSkill[];
  preferred_skills: JobSkill[];
  responsibilities: string[];
  qualifications: string[];
}

export interface SkillGapItem {
  normalized_skill_name: string;
  original_jd_wording?: string;
  original_resume_wording?: string;
  category?: string;
  requirement_importance: 'required' | 'preferred';
  match_status: 'matched' | 'partial' | 'missing';
  evidence?: string;
  jd_evidence?: string;
  resume_evidence?: string;
}

export interface ExperienceGapItem {
  requirement: string;
  resume_evidence?: string;
  status: 'matched' | 'partial' | 'missing';
  details?: string;
}

export interface QualificationGapItem {
  requirement: string;
  resume_evidence?: string;
  status: 'matched' | 'partial' | 'missing';
  details?: string;
}

export interface MatchedEvidenceItem {
  skill: string;
  jd_wording?: string;
  resume_wording?: string;
  jd_evidence?: string;
  resume_evidence?: string;
}

export interface PartialEvidenceItem {
  skill: string;
  jd_wording?: string;
  resume_wording?: string;
  jd_evidence?: string;
  resume_evidence?: string;
}

export interface MissingEvidenceItem {
  skill: string;
  importance: 'required' | 'preferred';
  jd_wording?: string;
  jd_evidence?: string;
}

export interface GapEvidenceData {
  matched_evidence?: MatchedEvidenceItem[];
  partial_evidence?: PartialEvidenceItem[];
  missing_evidence?: MissingEvidenceItem[];
  [key: string]: unknown;
}

export interface GapSummaryData {
  total_required_skills?: number;
  matched_required_count?: number;
  partial_required_count?: number;
  missing_required_count?: number;
  total_preferred_skills?: number;
  matched_preferred_count?: number;
  partial_preferred_count?: number;
  missing_preferred_count?: number;
  required_score_avg?: number;
  preferred_score_avg?: number | null;
  overall_match_score?: number;
  formula?: string;
  [key: string]: unknown;
}

export interface GapAnalysisResponse {
  overall_match_score: number;
  matched_skills: SkillGapItem[];
  partial_matches: SkillGapItem[];
  missing_required_skills: SkillGapItem[];
  missing_preferred_skills: SkillGapItem[];
  experience_gaps: ExperienceGapItem[];
  qualification_gaps: QualificationGapItem[];
  evidence: GapEvidenceData;
  summary: GapSummaryData;
}

export type SkillFilterType = 'all' | 'matched' | 'partial' | 'missing_required' | 'missing_preferred';

export interface GroundedRecommendation {
  skill: string;
  priority: 'high' | 'medium' | 'low';
  recommendation: string;
  rationale: string;
  evidence: string[];
  source_ids: string[];
  grounding_status: 'grounded' | 'insufficient_evidence' | 'rejected';
  confidence: number;
  validation_details?: {
    is_grounded?: boolean;
    status?: string;
    reasons?: string[];
    checks?: Record<string, boolean>;
    confidence?: number;
    [key: string]: unknown;
  };
}

export interface RecommendationResponse {
  recommendations: GroundedRecommendation[];
  insufficient_evidence_gaps: string[];
  rejected_recommendations: GroundedRecommendation[];
  summary: {
    total_gaps_evaluated?: number;
    grounded_recommendations_count?: number;
    insufficient_evidence_gaps_count?: number;
    rejected_count?: number;
    knowledge_base_chunks_active?: number;
    anti_hallucination_guarantee?: string;
    [key: string]: unknown;
  };
}
