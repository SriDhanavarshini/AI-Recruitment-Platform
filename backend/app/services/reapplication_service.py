from __future__ import annotations

from datetime import date, timedelta


class ReapplicationRestrictionService:
    @staticmethod
    def calculate_eligible_reapply_date(rejection_date: date) -> date:
        return rejection_date + timedelta(days=183)

    @staticmethod
    def can_apply(candidate_applied_on: date, current_date: date) -> bool:
        return current_date >= candidate_applied_on
