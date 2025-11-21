from __future__ import annotations

import logging
from typing import List, Optional, Dict, Set, Tuple

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.src.services.candidate_storage import GoogleDriveCandidateStore
from backend.src.services.email.email_notifications import (
    send_accept_email,
    send_reject_all_email,
    send_reject_matched_email,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["notifications"])


class JobCandidateView(BaseModel):
    candidate_id: Optional[str] = None
    file_name: str
    is_top: bool = False


class JobView(BaseModel):
    job_id: str
    job_title: str
    candidates: List[JobCandidateView] = []


class RejectedCandidateView(BaseModel):
    candidate_id: Optional[str] = None
    file_name: str
    reason: Optional[str] = None


class NotificationRequest(BaseModel):
    top_n: int
    jobs: List[JobView] = []
    rejected: List[RejectedCandidateView] = []


class NotificationResponse(BaseModel):
    sent_accept: int
    sent_reject: int
    skipped_no_email: int


@router.post("/send-emails", response_model=NotificationResponse)
async def send_notifications(request: NotificationRequest):
    if request.top_n < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="top_n must be >= 1",
        )

    store = GoogleDriveCandidateStore()
    records = store.load_all()

    profiles_by_id: Dict[str, any] = {
        r.id: r.profile for r in records if getattr(r, "profile", None)
    }

    accepted_positions: Dict[str, str] = {}
    rejected_ids: Set[str] = set()
    candidate_jobs: Dict[str, List[Tuple[str, str, bool]]] = {}

    for job in request.jobs:
        for c in job.candidates:
            if not c.candidate_id:
                continue

            candidate_jobs.setdefault(c.candidate_id, []).append(
                (job.job_id, job.job_title, c.is_top)
            )

            if c.is_top and c.candidate_id not in accepted_positions:
                accepted_positions[c.candidate_id] = job.job_title

    for rc in request.rejected:
        if not rc.candidate_id:
            continue
        if rc.candidate_id not in accepted_positions:
            rejected_ids.add(rc.candidate_id)

    matched_rejected: Dict[str, str] = {}

    for cand_id, jobs_list in candidate_jobs.items():
        if cand_id in accepted_positions:
            continue

        is_top_any = any(is_top for _, _, is_top in jobs_list)
        if is_top_any:
            continue

        if len(jobs_list) == 1:
            _, job_title, _ = jobs_list[0]
            matched_rejected[cand_id] = job_title

    for cand_id in matched_rejected.keys():
        rejected_ids.discard(cand_id)

    sent_accept = 0
    sent_reject_matched = 0
    sent_reject_all = 0
    skipped_no_email = 0

    for cand_id, position in accepted_positions.items():
        profile = profiles_by_id.get(cand_id)
        if not profile or not profile.email:
            skipped_no_email += 1
            logger.info(
                "Skipping acceptance email due to missing email",
                extra={
                    "event": "skip_email_no_address",
                    "type": "accept",
                    "candidate_id": cand_id,
                    "position": position,
                    "reason": "missing_email",
                },
            )
            continue

        try:
            send_accept_email(
                name=getattr(profile, "name", None),
                email=profile.email,
                position=position,
            )
            sent_accept += 1
        except Exception:
            logger.exception(
                "Failed to send acceptance email",
                extra={
                    "event": "send_accept_email_error",
                    "candidate_id": cand_id,
                    "position": position,
                },
            )

    for cand_id, position in matched_rejected.items():
        profile = profiles_by_id.get(cand_id)
        if not profile or not profile.email:
            skipped_no_email += 1
            logger.info(
                "Skipping matched rejection email due to missing email",
                extra={
                    "event": "skip_email_no_address",
                    "type": "reject_matched",
                    "candidate_id": cand_id,
                    "position": position,
                    "reason": "missing_email",
                },
            )
            continue

        try:
            send_reject_matched_email(
                name=getattr(profile, "name", None),
                email=profile.email,
                position=position,
            )
            sent_reject_matched += 1
        except Exception:
            logger.exception(
                "Failed to send matched rejection email",
                extra={
                    "event": "send_reject_matched_email_error",
                    "candidate_id": cand_id,
                    "position": position,
                },
            )

    for cand_id in rejected_ids:
        profile = profiles_by_id.get(cand_id)
        if not profile or not profile.email:
            skipped_no_email += 1
            logger.info(
                "Skipping global rejection email due to missing email",
                extra={
                    "event": "skip_email_no_address",
                    "type": "reject_all",
                    "candidate_id": cand_id,
                    "reason": "missing_email",
                },
            )
            continue

        try:
            send_reject_all_email(
                name=getattr(profile, "name", None),
                email=profile.email,
            )
            sent_reject_all += 1
        except Exception:
            logger.exception(
                "Failed to send global rejection email",
                extra={
                    "event": "send_reject_all_email_error",
                    "candidate_id": cand_id,
                },
            )

    sent_reject_total = sent_reject_matched + sent_reject_all

    logger.info(
        "Finished sending recruitment emails",
        extra={
            "event": "notifications_summary",
            "sent_accept": sent_accept,
            "sent_reject_total": sent_reject_total,
            "sent_reject_matched": sent_reject_matched,
            "sent_reject_all": sent_reject_all,
            "skipped_no_email": skipped_no_email,
        },
    )

    return NotificationResponse(
        sent_accept=sent_accept,
        sent_reject=sent_reject_total,
        skipped_no_email=skipped_no_email,
    )
