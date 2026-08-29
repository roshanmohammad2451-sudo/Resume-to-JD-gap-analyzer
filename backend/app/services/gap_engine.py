import re
from typing import List, Dict, Any, Tuple, Optional, Set
from app.schemas.resume import ResumeProfile, ResumeSkill
from app.schemas.jd import JobDescription, JobSkill
from app.schemas.gap import (
    SkillGapItem,
    ExperienceGapItem,
    QualificationGapItem,
    GapAnalysisResponse,
)

# Rule-based equivalence dictionary for technology and skill aliases
EXPLICIT_SKILL_MAP: Dict[str, str] = {
    "ms excel": "excel",
    "microsoft excel": "excel",
    "excel": "excel",
    "power bi": "power bi",
    "ms power bi": "power bi",
    "microsoft power bi": "power bi",
    "python programming": "python",
    "python language": "python",
    "python": "python",
    "pandas library": "pandas",
    "pandas": "pandas",
    "react.js": "react",
    "reactjs": "react",
    "react js": "react",
    "react": "react",
    "node.js": "node.js",
    "nodejs": "node.js",
    "node js": "node.js",
    "node": "node.js",
    "vue.js": "vue.js",
    "vuejs": "vue.js",
    "vue js": "vue.js",
    "vue": "vue.js",
    "js": "javascript",
    "javascript": "javascript",
    "ts": "typescript",
    "typescript": "typescript",
    "py": "python",
    "postgres": "postgresql",
    "postgres db": "postgresql",
    "postgresql": "postgresql",
    "mongo": "mongodb",
    "mongodb": "mongodb",
    "aws": "aws",
    "amazon web services": "aws",
    "gcp": "gcp",
    "google cloud platform": "gcp",
    "azure": "azure",
    "microsoft azure": "azure",
    "k8s": "kubernetes",
    "kubernetes": "kubernetes",
    "c sharp": "c#",
    "c#": "c#",
    "cpp": "c++",
    "c++": "c++",
    "dotnet": ".net",
    "dot net": ".net",
    ".net": ".net",
    "rest api": "rest api",
    "restful api": "rest api",
    "restful apis": "rest api",
    "rest apis": "rest api",
    "sql database": "sql",
    "sql": "sql",
    "my sql": "mysql",
    "mysql": "mysql",
    "docker container": "docker",
    "docker": "docker",
}

# Regex to strip generic noise words from skill names
NOISE_WORDS_REGEX = re.compile(
    r"\b(programming|language|library|framework|tool|tools|software|sdk|api|apis|database|db)\b",
    re.IGNORECASE,
)


def normalize_skill_name(skill_name: str) -> str:
    """
    Normalizes skill names deterministically before comparison.
    
    Examples:
    - "MS Excel" -> "excel"
    - "Microsoft Excel" -> "excel"
    - "Power BI" -> "power bi"
    - "Python programming" -> "python"
    - "Pandas library" -> "pandas"
    """
    if not skill_name:
        return ""

    cleaned = skill_name.strip().lower()

    # Direct match in explicit mapping dictionary
    if cleaned in EXPLICIT_SKILL_MAP:
        return EXPLICIT_SKILL_MAP[cleaned]

    # Remove generic noise words
    without_noise = NOISE_WORDS_REGEX.sub("", cleaned)
    without_noise = re.sub(r"\s+", " ", without_noise).strip()

    if without_noise in EXPLICIT_SKILL_MAP:
        return EXPLICIT_SKILL_MAP[without_noise]

    return without_noise if without_noise else cleaned


class GapEngine:
    """
    Deterministic Resume-to-JD Gap Analysis Engine.
    
    Does NOT use LLM for decision making or match scoring.
    All evaluations are explainable, rule-based, and fully deterministic.
    """

    def analyze_gap(
        self, 
        resume_profile: ResumeProfile, 
        job_description: JobDescription
    ) -> GapAnalysisResponse:
        """
        Performs deterministic gap analysis between ResumeProfile and JobDescription.
        """
        # 1. Normalize and deduplicate candidate resume skills
        resume_skills_map: Dict[str, ResumeSkill] = {}
        for r_skill in resume_profile.skills:
            norm_name = normalize_skill_name(r_skill.name)
            if not norm_name:
                continue
            if norm_name not in resume_skills_map:
                resume_skills_map[norm_name] = r_skill
            else:
                # Keep entry with higher confidence or combine evidence
                if r_skill.confidence > resume_skills_map[norm_name].confidence:
                    resume_skills_map[norm_name] = r_skill

        # 2. Extract and deduplicate JD required skills
        required_jd_skills: List[JobSkill] = []
        seen_required_norm: Set[str] = set()
        for jd_skill in job_description.required_skills:
            norm_name = normalize_skill_name(jd_skill.name)
            if not norm_name or norm_name in seen_required_norm:
                continue
            seen_required_norm.add(norm_name)
            required_jd_skills.append(jd_skill)

        # 3. Extract and deduplicate JD preferred skills (excluding required duplicates)
        preferred_jd_skills: List[JobSkill] = []
        seen_preferred_norm: Set[str] = set()
        for jd_skill in job_description.preferred_skills:
            norm_name = normalize_skill_name(jd_skill.name)
            if not norm_name or norm_name in seen_required_norm or norm_name in seen_preferred_norm:
                continue
            seen_preferred_norm.add(norm_name)
            preferred_jd_skills.append(jd_skill)

        # 4. Process Required Skills Gap
        matched_items: List[SkillGapItem] = []
        partial_items: List[SkillGapItem] = []
        missing_req_items: List[SkillGapItem] = []

        req_scores: List[float] = []

        for jd_skill in required_jd_skills:
            item, score = self._evaluate_skill(
                jd_skill=jd_skill,
                importance="required",
                resume_skills_map=resume_skills_map
            )
            req_scores.append(score)

            if item.match_status == "matched":
                matched_items.append(item)
            elif item.match_status == "partial":
                partial_items.append(item)
            else:
                missing_req_items.append(item)

        # 5. Process Preferred Skills Gap
        missing_pref_items: List[SkillGapItem] = []
        pref_scores: List[float] = []

        for jd_skill in preferred_jd_skills:
            item, score = self._evaluate_skill(
                jd_skill=jd_skill,
                importance="preferred",
                resume_skills_map=resume_skills_map
            )
            pref_scores.append(score)

            if item.match_status == "matched":
                matched_items.append(item)
            elif item.match_status == "partial":
                partial_items.append(item)
            else:
                missing_pref_items.append(item)

        # 6. Calculate Deterministic Match Score
        #
        # FORMULA DOCUMENTATION:
        # Transparent Weighted Score Formula:
        # - Required skills account for 70% (0.70) of overall score weight.
        # - Preferred skills account for 30% (0.30) of overall score weight.
        # - Each requirement match status yields:
        #     matched = 1.0
        #     partial = 0.5
        #     missing = 0.0
        # - If preferred skills list is empty, required skills account for 100% (1.00) of overall score.
        # - Overall score is scaled from 0.0 to 100.0 and rounded to 2 decimal places.

        req_avg = sum(req_scores) / len(req_scores) if req_scores else 1.0
        
        if pref_scores:
            pref_avg = sum(pref_scores) / len(pref_scores)
            if req_scores:
                weighted_ratio = 0.70 * req_avg + 0.30 * pref_avg
            else:
                weighted_ratio = pref_avg
        else:
            pref_avg = 0.0
            weighted_ratio = req_avg if req_scores else 1.0

        overall_match_score = round(weighted_ratio * 100.0, 2)

        # 7. Evaluate Experience and Qualification Gaps
        experience_gaps = self._evaluate_experience_gaps(job_description, resume_profile)
        qualification_gaps = self._evaluate_qualification_gaps(job_description, resume_profile)

        # 8. Build Evidence Summary & Structure
        evidence_dict = {
            "matched_evidence": [
                {
                    "skill": item.normalized_skill_name,
                    "jd_wording": item.original_jd_wording,
                    "resume_wording": item.original_resume_wording,
                    "jd_evidence": item.jd_evidence,
                    "resume_evidence": item.resume_evidence,
                }
                for item in matched_items
            ],
            "partial_evidence": [
                {
                    "skill": item.normalized_skill_name,
                    "jd_wording": item.original_jd_wording,
                    "resume_wording": item.original_resume_wording,
                    "jd_evidence": item.jd_evidence,
                    "resume_evidence": item.resume_evidence,
                }
                for item in partial_items
            ],
            "missing_evidence": [
                {
                    "skill": item.normalized_skill_name,
                    "importance": item.requirement_importance,
                    "jd_wording": item.original_jd_wording,
                    "jd_evidence": item.jd_evidence,
                }
                for item in (missing_req_items + missing_pref_items)
            ],
        }

        summary_dict = {
            "total_required_skills": len(required_jd_skills),
            "matched_required_count": sum(1 for item in req_scores if item == 1.0),
            "partial_required_count": sum(1 for item in req_scores if item == 0.5),
            "missing_required_count": len(missing_req_items),
            "total_preferred_skills": len(preferred_jd_skills),
            "matched_preferred_count": sum(1 for item in pref_scores if item == 1.0),
            "partial_preferred_count": sum(1 for item in pref_scores if item == 0.5),
            "missing_preferred_count": len(missing_pref_items),
            "required_score_avg": round(req_avg, 4),
            "preferred_score_avg": round(pref_avg, 4) if pref_scores else None,
            "overall_match_score": overall_match_score,
            "formula": (
                "70% Required Skills Weight + 30% Preferred Skills Weight "
                "(100% Required if no Preferred skills present)."
            ),
        }

        return GapAnalysisResponse(
            overall_match_score=overall_match_score,
            matched_skills=matched_items,
            partial_matches=partial_items,
            missing_required_skills=missing_req_items,
            missing_preferred_skills=missing_pref_items,
            experience_gaps=experience_gaps,
            qualification_gaps=qualification_gaps,
            evidence=evidence_dict,
            summary=summary_dict,
        )

    def _evaluate_skill(
        self,
        jd_skill: JobSkill,
        importance: str,
        resume_skills_map: Dict[str, ResumeSkill]
    ) -> Tuple[SkillGapItem, float]:
        norm_jd = normalize_skill_name(jd_skill.name)

        # A. Check Exact / Alias Match
        if norm_jd in resume_skills_map:
            matched_res_skill = resume_skills_map[norm_jd]
            item = SkillGapItem(
                normalized_skill_name=norm_jd,
                original_jd_wording=jd_skill.name,
                original_resume_wording=matched_res_skill.name,
                category=matched_res_skill.source_section or "Skills",
                requirement_importance=importance,
                match_status="matched",
                evidence=f"Exact skill match for '{norm_jd}'. JD: {jd_skill.evidence} | Resume: {matched_res_skill.evidence}",
                jd_evidence=jd_skill.evidence or jd_skill.source_text,
                resume_evidence=matched_res_skill.evidence,
            )
            return item, 1.0

        # B. Check Partial Match (Substring or Token Overlap)
        best_partial_res: Optional[ResumeSkill] = None
        for res_norm, res_skill in resume_skills_map.items():
            if norm_jd in res_norm or res_norm in norm_jd:
                best_partial_res = res_skill
                break

            # Token overlap check (ignoring short words)
            jd_tokens = set(t for t in norm_jd.split() if len(t) > 1)
            res_tokens = set(t for t in res_norm.split() if len(t) > 1)
            if jd_tokens and res_tokens and (jd_tokens & res_tokens):
                best_partial_res = res_skill
                break

        if best_partial_res:
            item = SkillGapItem(
                normalized_skill_name=norm_jd,
                original_jd_wording=jd_skill.name,
                original_resume_wording=best_partial_res.name,
                category=best_partial_res.source_section or "Skills",
                requirement_importance=importance,
                match_status="partial",
                evidence=f"Partial match for '{norm_jd}' against candidate skill '{best_partial_res.name}'.",
                jd_evidence=jd_skill.evidence or jd_skill.source_text,
                resume_evidence=best_partial_res.evidence,
            )
            return item, 0.5

        # C. Missing Skill
        item = SkillGapItem(
            normalized_skill_name=norm_jd,
            original_jd_wording=jd_skill.name,
            original_resume_wording=None,
            category=None,
            requirement_importance=importance,
            match_status="missing",
            evidence=f"Skill '{jd_skill.name}' ({norm_jd}) was required in JD but not found in candidate resume.",
            jd_evidence=jd_skill.evidence or jd_skill.source_text,
            resume_evidence=None,
        )
        return item, 0.0

    def _evaluate_experience_gaps(
        self, 
        job_description: JobDescription, 
        resume_profile: ResumeProfile
    ) -> List[ExperienceGapItem]:
        gaps: List[ExperienceGapItem] = []
        if not job_description.responsibilities:
            return gaps

        # Combine experience text from resume
        resume_text_corpus: List[Tuple[str, str]] = []
        for exp in resume_profile.experience:
            text = f"{exp.title or ''} {exp.company or ''} {' '.join(exp.responsibilities)}"
            resume_text_corpus.append((text.lower(), exp.company or exp.title or "Work Experience"))

        for proj in resume_profile.projects:
            text = f"{proj.name or ''} {proj.description or ''} {' '.join(proj.technologies)}"
            resume_text_corpus.append((text.lower(), proj.name or "Project"))

        for resp in job_description.responsibilities:
            resp_lower = resp.lower()
            keywords = [k for k in re.findall(r"\b\w{4,}\b", resp_lower) if k not in {"with", "that", "this", "from", "have", "will", "your", "their"}]
            
            matched_evidence: Optional[str] = None
            matched_count = 0

            for corpus_text, source_name in resume_text_corpus:
                found_kw = [kw for kw in keywords if kw in corpus_text]
                if len(found_kw) > matched_count:
                    matched_count = len(found_kw)
                    matched_evidence = f"Found relevant experience in {source_name} matching terms ({', '.join(found_kw)})"

            if matched_count >= max(2, len(keywords) // 2):
                status = "matched"
                details = f"Strong alignment with responsibility: '{resp[:60]}...'"
            elif matched_count > 0:
                status = "partial"
                details = f"Partial overlap with keywords in responsibility: '{resp[:60]}...'"
            else:
                status = "missing"
                details = f"No direct candidate experience found matching responsibility: '{resp[:60]}...'"

            gaps.append(
                ExperienceGapItem(
                    requirement=resp,
                    resume_evidence=matched_evidence,
                    status=status,
                    details=details,
                )
            )

        return gaps

    def _evaluate_qualification_gaps(
        self, 
        job_description: JobDescription, 
        resume_profile: ResumeProfile
    ) -> List[QualificationGapItem]:
        gaps: List[QualificationGapItem] = []
        if not job_description.qualifications:
            return gaps

        # Combine education & certification text from resume
        edu_cert_corpus: List[Tuple[str, str]] = []
        for edu in resume_profile.education:
            text = f"{edu.degree or ''} {edu.institution or ''} {edu.details or ''}"
            edu_cert_corpus.append((text.lower(), f"{edu.degree or 'Degree'} at {edu.institution or 'Institution'}"))

        for cert in resume_profile.certifications:
            text = f"{cert.name or ''} {cert.issuer or ''}"
            edu_cert_corpus.append((text.lower(), f"Certification: {cert.name or 'Cert'}"))

        for qual in job_description.qualifications:
            qual_lower = qual.lower()
            keywords = [k for k in re.findall(r"\b\w{3,}\b", qual_lower) if k not in {"with", "that", "this", "from", "have", "will", "your", "their", "must", "plus"}]

            matched_evidence: Optional[str] = None
            matched_count = 0

            for corpus_text, source_name in edu_cert_corpus:
                found_kw = [kw for kw in keywords if kw in corpus_text]
                if len(found_kw) > matched_count:
                    matched_count = len(found_kw)
                    matched_evidence = f"Candidate credential '{source_name}' contains matching terms ({', '.join(found_kw)})"

            if matched_count >= max(1, len(keywords) // 2):
                status = "matched"
                details = f"Candidate possesses matching qualification/degree for '{qual[:60]}...'"
            elif matched_count > 0:
                status = "partial"
                details = f"Partial qualification match for '{qual[:60]}...'"
            else:
                status = "missing"
                details = f"No explicit candidate degree or certification found for requirement '{qual[:60]}...'"

            gaps.append(
                QualificationGapItem(
                    requirement=qual,
                    resume_evidence=matched_evidence,
                    status=status,
                    details=details,
                )
            )

        return gaps


# Default instance
default_gap_engine = GapEngine()
