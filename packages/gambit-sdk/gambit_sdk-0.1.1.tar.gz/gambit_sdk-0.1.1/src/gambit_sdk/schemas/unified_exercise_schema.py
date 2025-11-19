from pydantic import BaseModel

from gambit_sdk.enums import ExerciseType
from gambit_sdk.schemas.exercise_structure_schemas import (
    ChoiceStructure,
    MatchingStructure,
    OrderingStructure,
)


class UnifiedExercise(BaseModel):
    platform_exercise_id: str
    type: ExerciseType
    question: str
    max_score: float | None = None

    structure: ChoiceStructure | MatchingStructure | OrderingStructure | None = None
