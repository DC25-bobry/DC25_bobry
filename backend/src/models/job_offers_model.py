from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional


class RequirementCreate(BaseModel):
    type: str = Field(..., description="SKILL, EDUCATION, EXPERIENCE, CERT, LANGUAGE, OTHER")
    name: str
    priority: str = Field(..., description="REQUIRED, IMPORTANT, OPTIONAL")
    weight: int = Field(..., ge=1, le=10)
    keywords: List[str] = Field(default_factory=list)


class Requirement(RequirementCreate):
    id: str


class JobOfferCreate(BaseModel):
    title: str
    contractType: Optional[str] = Field(default="UOP")
    seniority: Optional[str] = Field(default="Junior")
    description: Optional[str] = ""
    status: Optional[str] = Field(default="active")
    publishDate: Optional[str] = None
    expiryDate: Optional[str] = None

    requirements: List[RequirementCreate] = Field(..., min_length=1)


class JobOffer(JobOfferCreate):
    id: str
    requirements: List[Requirement]


class JobOfferList(BaseModel):
    items: List[JobOffer]
