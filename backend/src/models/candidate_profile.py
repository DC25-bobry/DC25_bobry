from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, EmailStr, AnyUrl


class EducationEntry(BaseModel):
    school_name: str
    start_year: int
    end_year: int
    field_of_study: str


class ExperienceEntry(BaseModel):
    company_name: str
    start_year: int
    end_year: int
    position: str


class SkillEntry(BaseModel):
    name: str
    category: str
    proficiency: Optional[float] = None


class CandidateProfile(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    linkedin_profile: Optional[AnyUrl] = None

    education: List[EducationEntry] = []
    experience: List[ExperienceEntry] = []
    skills: List[SkillEntry] = []
