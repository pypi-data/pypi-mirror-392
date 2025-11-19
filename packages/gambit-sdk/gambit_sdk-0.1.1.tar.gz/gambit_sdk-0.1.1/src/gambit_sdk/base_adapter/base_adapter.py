from abc import ABC, abstractmethod

from httpx import AsyncClient

from gambit_sdk.schemas import (
    UnifiedAssignmentDetails,
    UnifiedAssignmentPreview,
    UnifiedGrade,
    UnifiedSolution,
)


class BaseAdapter(ABC):
    def __init__(
            self,
            session: AsyncClient,
    ) -> None:
        self.session = session

    @abstractmethod
    async def login(
            self,
            username: str,
            password: str,
    ) -> None:
        pass

    @abstractmethod
    async def get_assignment_previews(
            self,
    ) -> list[UnifiedAssignmentPreview]:
        pass

    @abstractmethod
    async def get_assignment_details(
            self,
            preview: UnifiedAssignmentPreview,
    ) -> UnifiedAssignmentDetails:
        pass

    @abstractmethod
    async def submit_solution(
            self,
            details: UnifiedAssignmentDetails,
            solution: UnifiedSolution,
    ) -> UnifiedGrade | None:
        pass

    @abstractmethod
    async def get_grade(
            self,
            details: UnifiedAssignmentPreview,
    ) -> UnifiedGrade | None:
        pass
