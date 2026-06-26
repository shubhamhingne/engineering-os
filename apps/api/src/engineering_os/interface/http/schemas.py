"""Request/response models — the HTTP boundary contract."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    idea: str = Field(min_length=1)


class VisionUpdate(BaseModel):
    content: str = Field(min_length=1)


class VisionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    content: str
    source: str
    version: int
    model: Optional[str] = None
    updated_at: datetime


class ProjectOut(BaseModel):
    id: str
    title: str
    idea: str
    has_vision: bool = False
    created_at: datetime
    updated_at: datetime
