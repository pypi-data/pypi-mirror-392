from enum import StrEnum

from pydantic import BaseModel, Field


class DistributionType(StrEnum):
    SELF_HOSTED = "self_hosted"


class FilesConfig(BaseModel):
    max_size_bytes: int = Field(default=20000000)
    types: list[str]
    mime_types: dict[str, list[str]]


class AIModelConfig(BaseModel):
    model: str
    max_tokens: int


class MinMax(BaseModel):
    min: float
    max: float


class OpenAIConfig(BaseModel):
    presence_penalty: MinMax = Field(default=MinMax(min=-2.0, max=2.0))
    frequency_penalty: MinMax = Field(default=MinMax(min=-2.0, max=2.0))
    temperature: MinMax = Field(default=MinMax(min=0.0, max=2.0))
    models: list[AIModelConfig] = Field(default=[])


class AIConfig(BaseModel):
    litellm: OpenAIConfig = Field(default=OpenAIConfig())


class Settings(BaseModel):
    files: FilesConfig
    ai: AIConfig
    distribution_type: DistributionType
