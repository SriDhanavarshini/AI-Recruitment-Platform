import os
from abc import ABC, abstractmethod


class AIProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def analyze_resume(self, resume_text: str, job_description: str):
        raise NotImplementedError

    @abstractmethod
    def generate_questions(self, job_title: str, job_description: str, required_skills: list[str], experience_level: str):
        raise NotImplementedError

    @abstractmethod
    def generate_interview_question(self, category: str, job_context: dict):
        raise NotImplementedError

    @abstractmethod
    def evaluate_interview_answer(self, interview_question: str, candidate_answer: str, category: str):
        raise NotImplementedError


class ExternalAIProvider(AIProvider):
    def __init__(self):
        self.api_key = os.getenv("AI_API_KEY", "")
        self.provider = os.getenv("AI_PROVIDER", "gemini").lower()
        self.model = os.getenv("AI_MODEL", "gemini-1.5-flash")

    def generate(self, prompt: str, **kwargs):
        if not self.api_key:
            raise RuntimeError("AI API key is not configured. Set AI_API_KEY in the environment.")
        return {"prompt": prompt, "provider": self.provider, "model": self.model, **kwargs}

    def analyze_resume(self, resume_text: str, job_description: str):
        return {
            "resume_text": resume_text,
            "job_description": job_description,
            "provider": self.provider,
            "status": "ready_for_api_call",
        }

    def generate_questions(self, job_title: str, job_description: str, required_skills: list[str], experience_level: str):
        return {
            "job_title": job_title,
            "job_description": job_description,
            "required_skills": required_skills,
            "experience_level": experience_level,
            "provider": self.provider,
            "status": "ready_for_api_call",
        }

    def generate_interview_question(self, category: str, job_context: dict):
        return {"category": category, "job_context": job_context, "provider": self.provider}

    def evaluate_interview_answer(self, interview_question: str, candidate_answer: str, category: str):
        return {
            "question": interview_question,
            "answer": candidate_answer,
            "category": category,
            "provider": self.provider,
            "status": "ready_for_api_call",
        }


ai_provider = ExternalAIProvider()
