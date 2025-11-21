from __future__ import annotations

from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Query, HTTPException, status
from fastapi.responses import JSONResponse

from backend.src.services.candidate_storage import GoogleDriveCandidateStore, CandidateRecord

router = APIRouter(prefix="/candidates", tags=["Candidates"])


@router.get("/")
async def list_candidates(
    job_id: Optional[str] = Query(None, description="Filtruj po ID oferty pracy"),
    only_matched: bool = Query(
        False, description="Jeśli true – tylko kandydaci z co najmniej jednym MATCHED"
    ),
    only_rejected: bool = Query(
        False,
        description=(
            "Jeśli true – tylko kandydaci globalnie odrzuceni lub bez dopasowań"
        ),
    ),
):
    try:
        store = GoogleDriveCandidateStore()
        records: List[CandidateRecord] = store.load_all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Nie udało się odczytać candidates.json z Google Drive: {e}",
        )

    result: List[Dict[str, Any]] = []

    for rec in records:
        data = rec.model_dump()
        matches = data.get("job_matches") or []
        global_reason = data.get("global_rejection_reason")

        has_matched = any(m.get("status") == "MATCHED" for m in matches)

        if job_id:
            matches_filtered = [m for m in matches if m.get("job_id") == job_id]
            if not matches_filtered and not global_reason:
                continue
            data["job_matches"] = matches_filtered
        else:
            data["job_matches"] = matches

        is_globally_rejected = global_reason is not None
        has_any_match = len(data["job_matches"]) > 0

        if only_matched and not has_matched:
            continue

        if only_rejected and not (is_globally_rejected or not has_any_match):
            continue

        data["has_matched"] = has_matched
        data["is_globally_rejected"] = is_globally_rejected

        result.append(data)

    response_body = {
        "total_candidates": len(records),
        "returned_candidates": len(result),
        "candidates": result,
    }

    return JSONResponse(status_code=status.HTTP_200_OK, content=response_body)


@router.delete("/{candidate_id}")
async def delete_candidate(candidate_id: str):
    try:
        store = GoogleDriveCandidateStore()
        deleted = store.delete_candidate(candidate_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Nie udało się usunąć kandydata: {e}",
        )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kandydat o id={candidate_id} nie istnieje",
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "ok", "deleted_id": candidate_id},
    )
