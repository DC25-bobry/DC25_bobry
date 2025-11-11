from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from datetime import date

class ContractType(str, Enum):
    UOP = "UOP"
    B2B = "B2B"
    UZ = "UZ"
    UOD = "UOD"

class Seniority(str, Enum):
    JUNIOR = "Junior"
    MID = "Mid"
    SENIOR = "Senior"
    LEAD = "Lead"
    EXPERT = "Expert"

class Status(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"

class RequirementType(str, Enum):
    SKILL = "SKILL"
    EDUCATION = "EDUCATION"
    EXPERIENCE = "EXPERIENCE"
    CERT = "CERT"
    LANGUAGE = "LANGUAGE"
    OTHER = "OTHER"

class RequirementPriority(str, Enum):
    REQUIRED = "REQUIRED"
    IMPORTANT = "IMPORTANT"
    OPTIONAL = "OPTIONAL"

class Requirement(BaseModel):
    id: str
    type: RequirementType
    name: str
    priority: RequirementPriority
    weight: float
    keywords: Optional[List[str]] = None
    synonyms: Optional[List[str]] = None

    model_config = {"extra": "forbid"}

class JobOfferModel(BaseModel):
    id: str
    name: str
    type: Optional[ContractType] = None
    seniority: Optional[Seniority] = None
    description: Optional[str] = None
    status: Optional[Status] = None
    publish_date: Optional[date] = None
    expiry_date: Optional[date] = None

    requirements: List[Requirement]

    model_config = {"extra": "forbid"}

