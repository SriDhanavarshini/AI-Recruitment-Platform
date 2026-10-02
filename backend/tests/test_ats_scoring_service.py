from types import SimpleNamespace

import pytest

from app.services import ats_scoring_service as scoring

RESUME_TEXT = """
Senior Python engineer with experience building distributed backend services.
Designed REST APIs with FastAPI, PostgreSQL, Docker, and cloud infrastructure.
Led code reviews, improved performance, and collaborated with product teams.
"""

JOB_DESCRIPTION = """
We need a backend engineer skilled in Python, FastAPI, and PostgreSQL.
The role involves building distributed systems, REST APIs, Docker deployments,
cloud infrastructure, performance optimization, and cross-functional teamwork.
"""


class FakeSentenceModel:
    def encode(self, texts, show_progress_bar=False):
        return [[float(len(text.split())), 1.0, 2.0] for text in texts]


def test_service_imports_and_returns_expected_result(monkeypatch):
    monkeypatch.setattr(scoring, "_get_model", lambda: FakeSentenceModel())

    result = scoring.ats_score(RESUME_TEXT, JOB_DESCRIPTION)

    assert set(result) == {"score", "semantic", "keyword", "matched_keywords", "missing_keywords"}
    assert 0 <= result["score"] <= 100
    assert 0 <= result["semantic"] <= 100
    assert 0 <= result["keyword"] <= 100
    assert "python" in result["matched_keywords"]
    assert result["missing_keywords"]


@pytest.mark.parametrize(
    ("resume_text", "job_description"),
    [("", ""), ("Python", "Python"), (" ", "Backend developer")],
)
def test_empty_and_short_text_is_safe(monkeypatch, resume_text, job_description):
    monkeypatch.setattr(scoring, "_get_model", lambda: FakeSentenceModel())

    result = scoring.ats_score(resume_text, job_description)

    assert 0 <= result["score"] <= 100
    assert 0 <= result["semantic"] <= 100
    assert 0 <= result["keyword"] <= 100
    if not resume_text.strip() or not job_description.strip():
        assert result["semantic"] == 0
        assert result["keyword"] == 0


def test_sentence_transformer_model_is_cached(monkeypatch):
    calls = []

    class FakeSentenceTransformer:
        def __init__(self, model_name):
            calls.append(model_name)

    monkeypatch.setitem(
        __import__("sys").modules,
        "sentence_transformers",
        SimpleNamespace(SentenceTransformer=FakeSentenceTransformer),
    )
    scoring._get_model.cache_clear()
    try:
        first = scoring._get_model()
        second = scoring._get_model()
    finally:
        scoring._get_model.cache_clear()

    assert first is second
    assert calls == ["all-MiniLM-L6-v2"]


def test_keyword_scoring_returns_bigrams_and_missing_terms():
    score, matched, missing = scoring.keyword_score(
        "Python developer with REST APIs",
        "Python developer building REST APIs using PostgreSQL",
    )

    assert 0 < score < 100
    assert "python" in matched
    assert "postgresql" in missing
    assert "rest apis" in matched