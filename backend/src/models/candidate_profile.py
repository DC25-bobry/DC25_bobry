from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, EmailStr, AnyUrl


class EducationEntry(BaseModel):
    school_name: str
    start_year: int
    end_year: int
    field_of_study: str

    class Config:
        extra = "forbid"


class ExperienceEntry(BaseModel):
    company_name: str
    start_year: int
    end_year: int
    position: str

    class Config:
        extra = "forbid"


class SkillEntry(BaseModel):
    name: str
    category: str
    proficiency: Optional[float] = None

    class Config:
        extra = "forbid"


class CandidateProfile(BaseModel):
    name: str
    surname: str
    email: EmailStr
    phone_number: str
    linkedin_profile: Optional[AnyUrl] = None

    education: List[EducationEntry] = []
    experience: List[ExperienceEntry] = []
    skills: List[SkillEntry] = []

    class Config:
        extra = "forbid"
