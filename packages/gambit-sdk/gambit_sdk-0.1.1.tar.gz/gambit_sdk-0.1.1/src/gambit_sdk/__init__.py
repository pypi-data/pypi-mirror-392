"""
Gambit Platform Integration SDK

This package provides all the necessary components for developing a platform adapter
for the Gambit system.

The main entry points are:
- BaseAdapter: The abstract base class that every adapter must implement.
- AssignmentType: An enumeration of all supported assignment types.
- Unified*: A collection of Pydantic models representing the standardized data
  structures used for communication with the Gambit CORE system.
"""

from .base_adapter import BaseAdapter
from .enums import ExerciseType
from .schemas import (
    ChoiceAnswer,
    ChoiceStructure,
    MatchingAnswer,
    MatchingStructure,
    OrderingAnswer,
    OrderingStructure,
    StringAnswer,
    TextAnswer,
    TextFileAnswer,
    UnifiedAssignmentDetails,
    UnifiedAssignmentPreview,
    UnifiedExercise,
    UnifiedGrade,
    UnifiedSolution,
    UnifiedSolutionExercise,
)

__all__ = [
    "BaseAdapter",
    "ChoiceAnswer",
    "ChoiceStructure",
    "ExerciseType",
    "MatchingAnswer",
    "MatchingStructure",
    "OrderingAnswer",
    "OrderingStructure",
    "StringAnswer",
    "TextAnswer",
    "TextFileAnswer",
    "UnifiedAssignmentDetails",
    "UnifiedAssignmentPreview",
    "UnifiedExercise",
    "UnifiedGrade",
    "UnifiedSolution",
    "UnifiedSolutionExercise",
]
