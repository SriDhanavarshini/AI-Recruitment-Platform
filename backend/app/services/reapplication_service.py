from __future__ import annotations

import calendar
from datetime import date


class ReapplicationRestrictionService:
    @staticmethod
    def calculate_eligible_reapply_date(rejection_date: date) -> date:
        month_index = rejection_date.month - 1 + 6
        year = rejection_date.year + month_index // 12
        month = month_index % 12 + 1
        day = min(rejection_date.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)

    @staticmethod
    def can_apply(candidate_applied_on: date, current_date: date) -> bool:
        return current_date >= candidate_applied_on
