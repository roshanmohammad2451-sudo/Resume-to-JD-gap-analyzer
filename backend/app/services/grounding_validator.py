import logging
import re
from typing import List, Dict, Any, Tuple
from app.services.retrieval_service import RetrievedEvidence
from app.services.gap_engine import normalize_skill_name

logger = logging.getLogger(__name__)

# Known external platforms that hallucinating models often invent
EXTERNAL_PLATFORM_TERMS = {
    "coursera", "udemy", "edx", "pluralsight", "linkedin learning", "datacamp",
    "codecademy", "freecodecamp", "udacity", "skillshare", "youtube.com",
}

# Known distinct programming technologies to prevent foreign tech hallucination
KNOWN_DISTINCT_TECHS = {
    "python", "javascript", "typescript", "java", "c#", "c++", "go", "golang",
    "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "perl", "julia",
    "react", "angular", "vue", "django", "flask", "fastapi", "spring", "rails",
    "docker", "kubernetes", "terraform", "ansible", "jenkins", "aws", "azure", "gcp",
    "sql", "postgresql", "mysql", "mongodb", "redis", "cassandra", "elasticsearch",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "power bi", "tableau",
    "excel", "git", "github", "kafka", "spark", "hadoop", "graphql", "solidity"
}


class GroundingValidationResult:
    def __init__(
        self,
        is_grounded: bool,
        status: str,  # "grounded", "insufficient_evidence", "rejected"
        reasons: List[str],
        checks: Dict[str, bool],
        confidence: float = 1.0,
    ):
        self.is_grounded = is_grounded
        self.status = status
        self.reasons = reasons
        self.checks = checks
        self.confidence = confidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_grounded": self.is_grounded,
            "status": self.status,
            "reasons": self.reasons,
            "checks": self.checks,
            "confidence": round(self.confidence, 4),
        }


class DeterministicGroundingValidator:
    """
    Deterministic rule-based grounding validator.
    
    Verifies that generated recommendations adhere strictly to retrieved knowledge chunks.
    Rejects any recommendation that introduces invented technologies, external platforms,
    unsupported URLs, or ungrounded claims.
    """

    def validate_recommendation(
        self,
        skill: str,
        recommendation_text: str,
        rationale_text: str,
        retrieved_evidence: List[RetrievedEvidence],
        cited_source_ids: List[str],
    ) -> GroundingValidationResult:
        reasons: List[str] = []
        checks: Dict[str, bool] = {}

        norm_skill = normalize_skill_name(skill)

        # 0. Check for minimum retrieved evidence
        if not retrieved_evidence:
            return GroundingValidationResult(
                is_grounded=False,
                status="insufficient_evidence",
                reasons=["No retrieved evidence chunks available to ground recommendation."],
                checks={"has_evidence": False},
                confidence=0.0,
            )
        checks["has_evidence"] = True

        combined_rec = f"{recommendation_text} {rationale_text}".lower()
        all_chunk_text = " ".join(c.text.lower() for c in retrieved_evidence)
        valid_source_ids = {c.source_id for c in retrieved_evidence}

        # 1. Target Skill Consistency Check
        # The recommendation must mention the target skill or its normalized variant
        skill_tokens = set(re.findall(r"\w+", norm_skill.lower()))
        rec_tokens = set(re.findall(r"\w+", combined_rec))

        skill_mentioned = bool(skill_tokens & rec_tokens) or (norm_skill in combined_rec)
        checks["target_skill_referenced"] = skill_mentioned
        if not skill_mentioned:
            reasons.append(f"Recommendation does not reference target skill '{norm_skill}'.")

        # 2. No Invented URLs or Web Links
        has_urls = bool(re.search(r"https?://|www\.|\.com/|\.org/|\.edu/", combined_rec))
        # Allow URL only if it was present in the retrieved chunk text
        if has_urls and not re.search(r"https?://|www\.", all_chunk_text):
            checks["no_invented_urls"] = False
            reasons.append("Recommendation introduced ungrounded external URLs/links.")
        else:
            checks["no_invented_urls"] = True

        # 3. No Invented External Learning Platforms
        invented_platforms = []
        for platform in EXTERNAL_PLATFORM_TERMS:
            if platform in combined_rec and platform not in all_chunk_text:
                invented_platforms.append(platform)
        
        if invented_platforms:
            checks["no_invented_platforms"] = False
            reasons.append(f"Recommendation introduced ungrounded external platforms: {', '.join(invented_platforms)}.")
        else:
            checks["no_invented_platforms"] = True

        # 4. No Foreign / Unsupported Technologies
        # Any distinct technology mentioned in the recommendation must either be the target skill
        # or be explicitly discussed in the retrieved knowledge chunks
        foreign_techs = []
        for tech in KNOWN_DISTINCT_TECHS:
            if tech in combined_rec and tech != norm_skill and tech not in norm_skill:
                # Check if it was in the retrieved evidence text
                if tech not in all_chunk_text:
                    foreign_techs.append(tech)

        if foreign_techs:
            checks["no_foreign_technologies"] = False
            reasons.append(f"Recommendation introduced unsupported technologies absent from knowledge base: {', '.join(foreign_techs)}.")
        else:
            checks["no_foreign_technologies"] = True

        # 5. Source ID Integrity Check
        # Cited source IDs must all belong to the retrieved chunks
        if cited_source_ids:
            invalid_ids = [sid for sid in cited_source_ids if sid not in valid_source_ids]
            if invalid_ids:
                checks["valid_source_ids"] = False
                reasons.append(f"Recommendation cited invalid or non-retrieved source IDs: {', '.join(invalid_ids)}.")
            else:
                checks["valid_source_ids"] = True
        else:
            # If no source IDs explicitly cited, but we have valid retrieved chunks, warn or link them
            checks["valid_source_ids"] = True

        # 6. Substantive Concept Grounding Overlap
        # Extract substantive words (>3 chars, non-stopwords) and verify overlap with chunks
        stopwords = {
            "this", "that", "with", "from", "have", "will", "your", "their", "about",
            "learn", "build", "using", "create", "practice", "focus", "understanding",
            "skills", "knowledge", "recommendation", "recommended", "candidate", "project"
        }
        rec_words = [w for w in re.findall(r"\b[a-z]{4,}\b", combined_rec) if w not in stopwords]
        chunk_words = set(re.findall(r"\b[a-z]{4,}\b", all_chunk_text))

        if rec_words:
            grounded_word_count = sum(1 for w in rec_words if w in chunk_words)
            grounding_ratio = grounded_word_count / len(rec_words)
        else:
            grounding_ratio = 1.0

        checks["substantive_overlap"] = grounding_ratio >= 0.40
        if grounding_ratio < 0.40:
            reasons.append(
                f"Low concept grounding ratio ({grounding_ratio:.1%}). Too many unsupported claims."
            )

        # Final evaluation
        is_grounded = all(checks.values())
        status = "grounded" if is_grounded else "rejected"
        confidence = round(grounding_ratio, 3) if is_grounded else 0.0

        return GroundingValidationResult(
            is_grounded=is_grounded,
            status=status,
            reasons=reasons,
            checks=checks,
            confidence=confidence,
        )


default_grounding_validator = DeterministicGroundingValidator()
