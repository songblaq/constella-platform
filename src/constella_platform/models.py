from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field


@dataclass(frozen=True)
class Capability:
    capability_id: str
    domain: str
    description: str
    surfaces: tuple[str, ...]
    effects: tuple[str, ...] = field(default_factory=tuple)
    dangerous: bool = False
    audit_required: bool = True


class PlanCreate(BaseModel):
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)


class LessonCreate(BaseModel):
    title: str = Field(min_length=1)
    why_failed: str = Field(min_length=1)
    what_was_missed: str = Field(min_length=1)
    next_guardrail: str = Field(min_length=1)


class FindingCreate(BaseModel):
    title: str = Field(min_length=1)
    severity: str = Field(pattern="^(critical|high|medium|low)$")
    detail: str = Field(min_length=1)


class DecisionCreate(BaseModel):
    title: str = Field(min_length=1)
    rationale: str = Field(min_length=1)
    disposition: str = Field(min_length=1)


class InvokeResult(BaseModel):
    capability_id: str
    data: Any
