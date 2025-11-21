# backend/src/routes/upload_route.py
from __future__ import annotations

import asyncio
import logging
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, UploadFile, File, HTTPException, status, Query
from fastapi.responses import JSONResponse

from backend.src.services.document_parsing import DocumentParsingService
from backend.src.services.job_offers.job_offers_store import GoogleDriveJobOfferStore
from backend.src.utils.file_validation import validate_file
from backend.src.services.cv_storage import save_cv_file_to_drive
from backend.src.services.cv_processing import (
    process_file,
    CandidateProcessingResult,
)
from backend.src.models.job_offers_model import JobOffer

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload")
async def upload_files(
    top_n: int = Query(3, ge=1, le=20),
    files: List[UploadFile] = File(...),
):
    if not files:
        raise HTTPException(status_code=400, detail="No files sent")

    parsing_service = DocumentParsingService()

    job_store = GoogleDriveJobOfferStore()
    offers_data = await job_store.load_all()
    jobs: List[JobOffer] = [JobOffer(**o) for o in offers_data]

    if not jobs:
        logger.warning("No job offers available for matching.")

    sem = asyncio.Semaphore(10)

    async def handle_single_file(file: UploadFile) -> Optional[CandidateProcessingResult]:
        async with sem:
            file_bytes = await file.read()

            is_valid, info = validate_file(
                file_bytes, file.filename, file.content_type
            )
            if not is_valid:
                logger.warning(
                    "File rejected during validation",
                    extra={
                        "event": "cv_validation_rejected",
                        "file_name": file.filename,
                        "reason": info,
                    },
                )
                return None

            try:
                cv_drive_file_id = save_cv_file_to_drive(
                    file_bytes=file_bytes,
                    filename=file.filename,
                    content_type=file.content_type,
                )
            except Exception as e:
                logger.exception(
                    "Failed to store CV in Google Drive",
                    extra={
                        "event": "cv_drive_store_error",
                        "file_name": file.filename,
                    },
                )
                return None

            result: CandidateProcessingResult = await asyncio.to_thread(
                process_file,
                file_bytes,
                file.filename,
                file.content_type,
                parsing_service,
                cv_drive_file_id,
                jobs,
            )
            return result

    tasks = [handle_single_file(f) for f in files]
    raw_results = await asyncio.gather(*tasks, return_exceptions=True)

    candidate_results: List[CandidateProcessingResult] = []
    for res in raw_results:
        if isinstance(res, Exception):
            logger.exception(
                "Internal error occurred when processing CV",
                extra={"event": "cv_processing_error"},
            )
            continue
        if res is None:
            continue
        candidate_results.append(res)

    total_cv = len(candidate_results)

    jobs_map: Dict[str, Dict[str, Any]] = {}
    rejected_list: List[Dict[str, Any]] = []

    for res in candidate_results:
        record = res.record
        matches = record.job_matches or []

        global_reason = record.global_rejection_reason

        valid_matches = [m for m in matches if getattr(m, "status", None) == "MATCHED"]

        if global_reason or not valid_matches:
            reason = global_reason

            if not reason:
                rejection_reasons: List[str] = []
                for m in matches:
                    rr = getattr(m, "rejection_reasons", None)
                    if rr:
                        rejection_reasons.extend(rr)
                if rejection_reasons:
                    seen = set()
                    unique = []
                    for r in rejection_reasons:
                        if r not in seen:
                            seen.add(r)
                            unique.append(r)
                    reason = "; ".join(unique)
                else:
                    reason = "Brak dopasowania do ofert"

            rejected_list.append(
                {
                    "candidate_id": record.id,
                    "file_name": res.file_name,
                    "reason": reason,
                }
            )
            continue

        sorted_matches = sorted(
            valid_matches, key=lambda jm: jm.score_percent, reverse=True
        )
        best = sorted_matches[0]

        job_id = best.job_id
        job_title = best.job_title

        if job_id not in jobs_map:
            jobs_map[job_id] = {
                "job_id": job_id,
                "job_title": job_title,
                "candidates": [],
            }

        def _req_list(reqs):
            result = []
            for r in reqs or []:
                name = getattr(r, "name", None) or getattr(
                    r, "requirement_name", None
                )
                weight = getattr(r, "weight", None)
                result.append(
                    {
                        "name": name,
                        "weight": weight,
                    }
                )
            return result

        matched_reqs = _req_list(best.matched_requirements)
        unmatched_reqs = _req_list(
            (best.missing_required or []) + (best.missing_optional or [])
        )

        other_matches = [
            {
                "job_title": m.job_title,
                "score": m.score_percent,
            }
            for m in sorted_matches[1:]
        ]

        candidate_view = {
            "candidate_id": record.id,
            "file_name": res.file_name,
            "score": best.score_percent,
            "total_score": best.total_score,
            "max_score": best.max_score,
            "matched_requirements": matched_reqs,
            "unmatched_requirements": unmatched_reqs,
            "other_matches": other_matches,
            "rank": None,
            "is_top": False,
        }

        jobs_map[job_id]["candidates"].append(candidate_view)

    matched_cv = 0
    for job in jobs_map.values():
        cands = job["candidates"]
        cands.sort(key=lambda c: c["score"], reverse=True)

        for idx, c in enumerate(cands, start=1):
            c["rank"] = idx
            c["is_top"] = idx <= top_n

        matched_cv += len(cands)

    rejected_cv = len(rejected_list)

    response_body = {
        "total_cv": total_cv,
        "matched_cv": matched_cv,
        "rejected_cv": rejected_cv,
        "jobs": list(jobs_map.values()),
        "rejected": rejected_list,
    }

    return JSONResponse(status_code=status.HTTP_200_OK, content=response_body)
