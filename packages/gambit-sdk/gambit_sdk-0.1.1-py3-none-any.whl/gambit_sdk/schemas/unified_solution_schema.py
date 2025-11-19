from pydantic import BaseModel

from gambit_sdk.schemas.solution_type_schemas import (
    ChoiceAnswer,
    MatchingAnswer,
    OrderingAnswer,
    StringAnswer,
    TextAnswer,
    TextFileAnswer,
)


class UnifiedSolutionExercise(BaseModel):
    platform_exercise_id: str
    answer: ChoiceAnswer | StringAnswer | TextAnswer | TextFileAnswer | MatchingAnswer | OrderingAnswer


class UnifiedSolution(BaseModel):
    platform_assignment_id: str
    answers: list[UnifiedSolutionExercise]
