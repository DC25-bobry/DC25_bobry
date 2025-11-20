from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from backend.src.services.job_offers.job_offers_model import JobOffer, JobOfferCreate
from backend.src.services.job_offers.job_offers_repository import JobOfferRepository
from backend.src.services.job_offers.job_offers_store import GoogleDriveJobOfferStore

router = APIRouter(prefix="/jobs", tags=["Job Offers"])

store = GoogleDriveJobOfferStore()
repo = JobOfferRepository(store)


def get_repo() -> JobOfferRepository:
    return repo


@router.get("", response_model=List[JobOffer])
async def list_jobs(repository: JobOfferRepository = Depends(get_repo)):
    return await repository.list()


@router.get("/{job_id}", response_model=JobOffer)
async def get_job(job_id: str, repository: JobOfferRepository = Depends(get_repo)):
    job = await repository.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job offer not found")
    return job


@router.post("", response_model=JobOffer, status_code=201)
async def create_job(
    payload: JobOfferCreate,
    repository: JobOfferRepository = Depends(get_repo),
):
    return await repository.create(payload)


@router.put("/{job_id}", response_model=JobOffer)
async def update_job(
    job_id: str, payload: JobOfferCreate, repository: JobOfferRepository = Depends(get_repo)
):
    try:
        return await repository.update(job_id, payload)
    except KeyError:
        raise HTTPException(status_code=404, detail="Job offer not found")


@router.delete("/{job_id}", status_code=204)
async def delete_job(job_id: str, repository: JobOfferRepository = Depends(get_repo)):
    try:
        await repository.delete(job_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Job offer not found")
