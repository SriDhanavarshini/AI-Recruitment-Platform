from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, Boolean, Column, Date, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db import Base


class UserRole(str, Enum):
    HR = "HR"
    CANDIDATE = "CANDIDATE"


class EmploymentType(str, Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    INTERNSHIP = "INTERNSHIP"
    CONTRACT = "CONTRACT"


class JobStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class ApplicationStatus(str, Enum):
    APPLIED = "APPLIED"
    ATS_SHORTLISTED = "ATS_SHORTLISTED"
    ASSESSMENT_PENDING = "ASSESSMENT_PENDING"
    ASSESSMENT_PASSED = "ASSESSMENT_PASSED"
    AI_INTERVIEW_PENDING = "AI_INTERVIEW_PENDING"
    AI_INTERVIEW_COMPLETED = "AI_INTERVIEW_COMPLETED"
    SELECTED = "SELECTED"
    NOT_SELECTED = "NOT_SELECTED"


class QuestionType(str, Enum):
    APTITUDE = "APTITUDE"
    TECHNICAL_MCQ = "TECHNICAL_MCQ"
    CODING = "CODING"


class Difficulty(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class ProctoringEventType(str, Enum):
    FACE_NOT_DETECTED = "FACE_NOT_DETECTED"
    MULTIPLE_FACES = "MULTIPLE_FACES"
    TAB_SWITCH = "TAB_SWITCH"
    FULLSCREEN_EXIT = "FULLSCREEN_EXIT"
    CAMERA_DISCONNECTED = "CAMERA_DISCONNECTED"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    company = relationship("Company", back_populates="owner")
    resumes = relationship("Resume", back_populates="candidate")
    applications = relationship("Application", back_populates="candidate")


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="company")
    jobs = relationship("Job", back_populates="company")


class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    required_skills = Column(JSON, default=list)
    required_experience = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    employment_type = Column(SAEnum(EmploymentType), nullable=False)
    status = Column(SAEnum(JobStatus), default=JobStatus.OPEN)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    company = relationship("Company", back_populates="jobs")
    applications = relationship("Application", back_populates="job")


class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_url = Column(String(500), nullable=False)
    storage_path = Column(String(500), nullable=False)
    extracted_skills = Column(JSON, default=list)
    extracted_keywords = Column(JSON, default=list)
    extracted_experience = Column(Text, nullable=True)
    education = Column(Text, nullable=True)
    projects = Column(Text, nullable=True)
    certifications = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("User", back_populates="resumes")
    applications = relationship("Application", back_populates="resume")


class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    status = Column(SAEnum(ApplicationStatus), default=ApplicationStatus.APPLIED)
    ats_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    candidate = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    resume = relationship("Resume", back_populates="applications")
    ats_result = relationship("ATSResult", back_populates="application", uselist=False)


class ATSResult(Base):
    __tablename__ = "ats_results"
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False, unique=True)
    score = Column(Float, nullable=False)
    matching_skills = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    relevant_experience = Column(Text, nullable=True)
    extracted_resume_data = Column(JSON, default=dict)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("Application", back_populates="ats_result")


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    type = Column(SAEnum(QuestionType), nullable=False)
    topic = Column(String(255), nullable=False)
    difficulty = Column(SAEnum(Difficulty), nullable=False)
    options = Column(JSON, default=list)
    correct_answer = Column(String(255), nullable=True)
    explanation = Column(Text, nullable=True)
    marks = Column(Integer, default=1)
    approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Assessment(Base):
    __tablename__ = "assessments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    duration_minutes = Column(Integer, default=60)
    passing_score = Column(Float, default=60.0)
    marks = Column(Integer, default=100)
    difficulty = Column(SAEnum(Difficulty), default=Difficulty.MEDIUM)
    number_of_questions = Column(Integer, default=40)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AssessmentAttempt(Base):
    __tablename__ = "assessment_attempts"
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(50), default="IN_PROGRESS")
    score = Column(Float, default=0.0)
    percentage = Column(Float, default=0.0)
    pass_status = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)


class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("assessment_attempts.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected_answer = Column(String(255), nullable=True)
    is_correct = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class CodingProblem(Base):
    __tablename__ = "coding_problems"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    statement = Column(Text, nullable=False)
    input_description = Column(Text, nullable=True)
    output_description = Column(Text, nullable=True)
    constraints = Column(Text, nullable=True)
    examples = Column(JSON, default=list)
    visible_test_cases = Column(JSON, default=list)
    hidden_test_cases = Column(JSON, default=list)
    supported_languages = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)


class CodingSubmission(Base):
    __tablename__ = "coding_submissions"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    problem_id = Column(Integer, ForeignKey("coding_problems.id"), nullable=False)
    language = Column(String(50), nullable=False)
    code = Column(Text, nullable=False)
    passed_tests = Column(Integer, default=0)
    failed_tests = Column(Integer, default=0)
    execution_time_ms = Column(Integer, default=0)
    memory_kb = Column(Integer, default=0)
    score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class ProctoringEvent(Base):
    __tablename__ = "proctoring_events"
    id = Column(Integer, primary_key=True, index=True)
    assessment_attempt_id = Column(Integer, ForeignKey("assessment_attempts.id"), nullable=False)
    event_type = Column(SAEnum(ProctoringEventType), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, default=dict)


class AIInterview(Base):
    __tablename__ = "ai_interviews"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String(50), default="TECHNICAL")
    status = Column(String(50), default="PENDING")
    max_questions = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("ai_interviews.id"), nullable=False)
    question = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class InterviewAnswer(Base):
    __tablename__ = "interview_answers"
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("ai_interviews.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("interview_questions.id"), nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class InterviewReport(Base):
    __tablename__ = "interview_reports"
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("ai_interviews.id"), nullable=False, unique=True)
    technical_score = Column(Float, default=0.0)
    domain_score = Column(Float, default=0.0)
    communication_score = Column(Float, default=0.0)
    relevance_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
    strengths = Column(JSON, default=list)
    areas_for_improvement = Column(JSON, default=list)
    question_evaluations = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)


class CandidateStatusHistory(Base):
    __tablename__ = "candidate_status_history"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    status = Column(String(50), nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ReapplicationRestriction(Base):
    __tablename__ = "reapplication_restrictions"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    rejection_date = Column(Date, nullable=False)
    eligible_reapply_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = {"sqlite_autoincrement": True}
