from pydantic import BaseModel


class ChoiceAnswer(BaseModel):
    selected_ids: list[str]


class StringAnswer(BaseModel):
    value: str


class TextAnswer(BaseModel):
    text: str


class TextFileAnswer(BaseModel):
    filename: str
    content_base64: str


class MatchingAnswer(BaseModel):
    pairs: dict[str, str]


class OrderingAnswer(BaseModel):
    ordered_ids: list[str]
