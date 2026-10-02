from __future__ import annotations


class AssessmentScoringService:
    @staticmethod
    def score_attempt(answers: list[dict], total_marks: float = 100.0) -> dict:
        total_score = 0.0
        for answer in answers:
            if answer.get("is_correct"):
                total_score += float(answer.get("marks", 1))

        percentage = round((total_score / total_marks) * 100, 2) if total_marks else 0.0
        return {
            "total_score": round(total_score, 2),
            "percentage": percentage,
            "pass_status": percentage >= 60.0,
        }
