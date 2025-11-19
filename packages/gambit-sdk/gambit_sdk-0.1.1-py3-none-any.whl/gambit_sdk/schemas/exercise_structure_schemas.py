from pydantic import BaseModel


class ChoiceStructure(BaseModel):
    options: dict[str, str]


class MatchingStructure(BaseModel):
    group_a: dict[str, str]
    group_b: dict[str, str]


class OrderingStructure(BaseModel):
    items: dict[str, str]
