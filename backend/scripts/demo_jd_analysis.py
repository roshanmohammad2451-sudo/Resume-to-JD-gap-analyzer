import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
import json
from unittest.mock import AsyncMock

from app.schemas.jd import JobDescription, JobSkill
from app.services.jd_parser import JDParserService

sample_jd_text = """
CloudScale Innovations — Lead Cloud Platform Engineer
Location: Remote / San Francisco, CA

ABOUT THE ROLE:
We are seeking a Lead Cloud Platform Engineer to architect next-generation multi-cloud infrastructure and developer tooling.

MINIMUM REQUIREMENTS:
- 7+ years of experience in software engineering or DevOps.
- Expert knowledge of Kubernetes (EKS, GKE) and infrastructure automation with Terraform.
- Deep hands-on experience with AWS cloud services (IAM, VPC, EC2, S3, RDS).
- Strong programming skills in Go or Python.

NICE TO HAVE:
- Experience with Service Mesh (Istio) and GitOps tooling (ArgoCD).
- Knowledge of vector databases (pgvector, Qdrant) and RAG architecture.
- AWS Certified Solutions Architect Professional.

RESPONSIBILITIES:
- Design, deploy, and operate production Kubernetes clusters across regions.
- Build internal developer platform APIs to streamline microservice deployments.
- Mentor junior engineers and champion cloud security best practices.
"""

async def run_demo():
    print("=== Testing Structured Job Description Analysis Engine ===")

    mock_parsed_jd = JobDescription(
        role="Lead Cloud Platform Engineer",
        company="CloudScale Innovations",
        summary="Architect next-generation multi-cloud infrastructure and developer tooling.",
        required_skills=[
            JobSkill(
                name="Kubernetes",
                evidence="Expert knowledge of Kubernetes (EKS, GKE) and infrastructure automation with Terraform.",
                importance="required",
                source_text="Expert knowledge of Kubernetes (EKS, GKE) and infrastructure automation with Terraform."
            ),
            JobSkill(
                name="Terraform",
                evidence="Expert knowledge of Kubernetes (EKS, GKE) and infrastructure automation with Terraform.",
                importance="required",
                source_text="Expert knowledge of Kubernetes (EKS, GKE) and infrastructure automation with Terraform."
            ),
            JobSkill(
                name="AWS",
                evidence="Deep hands-on experience with AWS cloud services (IAM, VPC, EC2, S3, RDS).",
                importance="required",
                source_text="Deep hands-on experience with AWS cloud services (IAM, VPC, EC2, S3, RDS)."
            ),
            JobSkill(
                name="Go",
                evidence="Strong programming skills in Go or Python.",
                importance="required",
                source_text="Strong programming skills in Go or Python."
            ),
            JobSkill(
                name="Python",
                evidence="Strong programming skills in Go or Python.",
                importance="required",
                source_text="Strong programming skills in Go or Python."
            )
        ],
        preferred_skills=[
            JobSkill(
                name="Istio",
                evidence="Experience with Service Mesh (Istio) and GitOps tooling (ArgoCD).",
                importance="preferred",
                source_text="Experience with Service Mesh (Istio) and GitOps tooling (ArgoCD)."
            ),
            JobSkill(
                name="ArgoCD",
                evidence="Experience with Service Mesh (Istio) and GitOps tooling (ArgoCD).",
                importance="preferred",
                source_text="Experience with Service Mesh (Istio) and GitOps tooling (ArgoCD)."
            ),
            JobSkill(
                name="pgvector",
                evidence="Knowledge of vector databases (pgvector, Qdrant) and RAG architecture.",
                importance="preferred",
                source_text="Knowledge of vector databases (pgvector, Qdrant) and RAG architecture."
            )
        ],
        responsibilities=[
            "Design, deploy, and operate production Kubernetes clusters across regions.",
            "Build internal developer platform APIs to streamline microservice deployments.",
            "Mentor junior engineers and champion cloud security best practices."
        ],
        qualifications=[
            "7+ years of experience in software engineering or DevOps.",
            "AWS Certified Solutions Architect Professional."
        ]
    )

    mock_llm = AsyncMock()
    mock_llm.generate_structured_output.return_value = mock_parsed_jd

    parser = JDParserService(llm_service=mock_llm)
    result = await parser.analyze_jd_text(sample_jd_text)

    json_output = result.model_dump_json(indent=2)
    print("\n--- RESULTING JOB DESCRIPTION JSON OUTPUT ---")
    print(json_output)

    # Validations
    assert result.role == "Lead Cloud Platform Engineer"
    assert result.company == "CloudScale Innovations"
    assert len(result.required_skills) == 5
    assert len(result.preferred_skills) == 3
    assert all(s.importance == "required" for s in result.required_skills)
    assert all(s.importance == "preferred" for s in result.preferred_skills)

    print("\n[OK] Phase 4 Job Description Analysis JSON validated successfully!")

if __name__ == "__main__":
    asyncio.run(run_demo())
