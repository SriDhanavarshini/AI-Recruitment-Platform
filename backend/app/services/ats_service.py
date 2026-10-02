from __future__ import annotations

from typing import Any


class ATSScoringService:
    """Deterministic ATS score calculator. The LLM may normalize data, but the final score is always computed here."""

    DEFAULT_WEIGHTS: dict[str, float] = {
        "skills": 0.40,
        "experience": 0.25,
        "projects": 0.15,
        "education": 0.10,
        "keywords": 0.10,
    }

    @classmethod
    def calculate_score(
        cls,
        extracted_resume: dict[str, Any],
        job_requirements: dict[str, Any],
        weights: dict[str, float] | None = None,
    ) -> dict[str, Any]:
        weights = weights or cls.DEFAULT_WEIGHTS

        skills = extracted_resume.get("skills", [])
        required_skills = job_requirements.get("required_skills", [])
        skill_matches = [skill for skill in required_skills if skill.lower() in {s.lower() for s in skills}]
        missing_skills = [skill for skill in required_skills if skill.lower() not in {s.lower() for s in skills}]

        experience_match = 1.0 if not job_requirements.get("required_experience") else min(1.0, len(skill_matches) / max(1, len(required_skills)))
        project_relevance = 0.5 if extracted_resume.get("projects") else 0.0
        education_match = 1.0 if not job_requirements.get("education") else 0.5 if extracted_resume.get("education") else 0.0
        keyword_match = 1.0 if not job_requirements.get("keywords") else min(1.0, len(job_requirements.get("keywords", [])) / max(1, len(job_requirements.get("keywords", []))))

        weighted_score = (
            (len(skill_matches) / max(1, len(required_skills))) * weights["skills"]
            + experience_match * weights["experience"]
            + project_relevance * weights["projects"]
            + education_match * weights["education"]
            + keyword_match * weights["keywords"]
        ) * 100

        return {
            "score": round(weighted_score, 2),
            "matching_skills": skill_matches,
            "missing_skills": missing_skills,
            "relevant_experience": f"Experience match estimated at {round(experience_match * 100, 1)}% based on required role fit.",
            "explanation": "The ATS score is deterministic and based on configured weights for skills, experience, projects, education, and keyword alignment.",
        }
