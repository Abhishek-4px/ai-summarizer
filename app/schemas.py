from pydantic import BaseModel


class SummarizeRequest(BaseModel):
    text: str


class SummaryResponse(BaseModel):
    summary: str
    key_points: list[str]
    word_count: int
