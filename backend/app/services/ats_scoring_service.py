from __future__ import annotations

import re
from functools import lru_cache
from typing import Any

MODEL_NAME = "all-MiniLM-L6-v2"
SEMANTIC_WEIGHT = 0.6
KEYWORD_WEIGHT = 0.4
CHUNK_WORDS = 120


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _chunks(text: str, max_words: int = CHUNK_WORDS) -> list[str]:
    words = _norm(text).split()
    if max_words < 1:
        raise ValueError("max_words must be greater than zero")
    return [" ".join(words[index : index + max_words]) for index in range(0, len(words), max_words)]


@lru_cache(maxsize=1)
def _get_model() -> Any:
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)


def keyword_score(resume_text: str, job_description: str) -> tuple[float, list[str], list[str]]:
    from sklearn.feature_extraction.text import CountVectorizer

    resume = _norm(resume_text)
    job = _norm(job_description)
    if not resume or not job:
        return 0.0, [], []

    vectorizer = CountVectorizer(ngram_range=(1, 2), stop_words="english", binary=True)
    try:
        vectors = vectorizer.fit_transform([resume, job])
    except ValueError:
        return 0.0, [], []

    features = vectorizer.get_feature_names_out()
    resume_indices = set(vectors[0].indices)
    job_indices = set(vectors[1].indices)
    job_keywords = [feature for index, feature in enumerate(features) if index in job_indices]
    matched_keywords = [feature for index, feature in enumerate(features) if index in job_indices and index in resume_indices]
    matched_indices = {index for index in job_indices if index in resume_indices}
    missing_keywords = [feature for index, feature in enumerate(features) if index in job_indices and index not in matched_indices]
    score = len(matched_keywords) / len(job_keywords) * 100 if job_keywords else 0.0
    return round(score, 2), matched_keywords, missing_keywords


def semantic_score(resume_text: str, job_description: str) -> float:
    resume_chunks = _chunks(resume_text)
    job_chunks = _chunks(job_description)
    if not resume_chunks or not job_chunks:
        return 0.0

    model = _get_model()
    resume_embeddings = model.encode(resume_chunks, show_progress_bar=False)
    job_embeddings = model.encode(job_chunks, show_progress_bar=False)
    best_matches = [
        max(_cosine_similarity(resume_embedding, job_embedding) for resume_embedding in resume_embeddings)
        for job_embedding in job_embeddings
    ]
    score = sum(max(0.0, similarity) for similarity in best_matches) / len(best_matches) * 100
    return round(min(100.0, max(0.0, score)), 2)


def ats_score(resume_text: str, job_description: str) -> dict[str, Any]:
    keyword, matched_keywords, missing_keywords = keyword_score(resume_text, job_description)
    semantic = semantic_score(resume_text, job_description)
    score = semantic * SEMANTIC_WEIGHT + keyword * KEYWORD_WEIGHT
    return {
        "score": round(score, 2),
        "semantic": semantic,
        "keyword": keyword,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
    }


def _cosine_similarity(left: Any, right: Any) -> float:
    left_values = [float(value) for value in left]
    right_values = [float(value) for value in right]
    if len(left_values) != len(right_values) or not left_values:
        return 0.0
    dot_product = sum(left_value * right_value for left_value, right_value in zip(left_values, right_values))
    left_norm = sum(value * value for value in left_values) ** 0.5
    right_norm = sum(value * value for value in right_values) ** 0.5
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot_product / (left_norm * right_norm)