from typing import Any

from pydantic import BaseModel


class UnifiedGrade(BaseModel):
    platform_assignment_id: str
    score: float
    max_score: float
    is_passed: bool
    feedback: str | None = None
    correct_answers: dict[str, Any] | None = None
