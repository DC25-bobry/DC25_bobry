from typing import Optional, List
from pydantic import BaseModel, HttpUrl


class EducationModel(BaseModel):
    school_name: str
    start_year: int
    end_year: int
    field_of_study: str

    model_config = {"extra": "forbid"}

class ExperienceModel(BaseModel):
    company_name: str
    start_year: str
    end_year: str
    position: str

    model_config = {"extra": "forbid"}

class DentalParametersModel(BaseModel):
    valid_dental_checkup: bool
    teeth_spacing: float

    model_config = {"extra": "forbid"}

class SkillModel(BaseModel):
    name: str
    category: str
    proficiency_level: int

    model_config = {"extra": "forbid"}

class CandidateModel(BaseModel):
    name: str
    surname: str
    email: str
    phone: str
    linkedin: Optional[HttpUrl] = None

    education: Optional[List[EducationModel]] = None
    experience: Optional[List[ExperienceModel]] = None
    dental_parameters: DentalParametersModel

    health_certificate: bool
    skills: Optional[List[SkillModel]] = None

    model_config = {"extra": "forbid"}
