from pydantic import BaseModel, Field


class AIGenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=20_000)
    max_output_tokens: int = Field(default=500, ge=1, le=4096)


class AIGenerateResponse(BaseModel):
    text: str
    input_tokens: int
    output_tokens: int
