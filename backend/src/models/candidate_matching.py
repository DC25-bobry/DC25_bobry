from __future__ import annotations

from typing import List, Optional, Literal

from pydantic import BaseModel

from backend.src.models.candidate_profile import CandidateProfile


class RequirementMatch(BaseModel):
    requirement_id: Optional[str] = None
    name: str
    priority: str
    weight: int
    matched: bool


class JobMatch(BaseModel):
    job_id: str
    job_title: str
    status: Literal["MATCHED", "REJECTED"]

    score_percent: int
    total_score: int
    max_score: int

    matched_requirements: List[RequirementMatch] = []
    missing_required: List[RequirementMatch] = []
    missing_optional: List[RequirementMatch] = []

    rejection_reasons: List[str] = []


class CandidateRecord(BaseModel):
    id: str
    profile: CandidateProfile
    cv_drive_file_id: Optional[str] = None

    job_matches: List[JobMatch] = []
    global_rejection_reason: Optional[str] = None
