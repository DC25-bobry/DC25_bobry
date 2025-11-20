import uuid
from typing import Dict, List, Optional

from pydantic import ValidationError

from backend.src.services.job_offers.job_offers_model import JobOffer, JobOfferCreate, Requirement
from backend.src.services.job_offers.job_offers_store import GoogleDriveJobOfferStore


class JobOfferRepository:
    def __init__(self, store: GoogleDriveJobOfferStore):
        self.store = store
        self._cache: Dict[str, JobOffer] = {}
        self._loaded = False

    async def _load(self):
        if self._loaded:
            return

        raw = await self.store.load_all()
        for item in raw:
            try:
                job = JobOffer(**item)
                self._cache[job.id] = job
            except ValidationError:
                continue

        self._loaded = True

    async def _flush(self):
        data = [j.dict() for j in self._cache.values()]
        await self.store.save_all(data)

    async def list(self) -> List[JobOffer]:
        await self._load()
        return list(self._cache.values())

    async def get(self, job_id: str) -> Optional[JobOffer]:
        await self._load()
        return self._cache.get(job_id)

    async def create(self, payload: JobOfferCreate) -> JobOffer:
        await self._load()

        job_id = str(uuid.uuid4())
        reqs = [
            Requirement(id=str(uuid.uuid4()), **r.dict())
            for r in payload.requirements
        ]

        job = JobOffer(
            id=job_id,
            **payload.dict(exclude={"requirements"}),
            requirements=reqs,
        )

        self._cache[job_id] = job
        await self._flush()
        return job

    async def update(self, job_id: str, payload: JobOfferCreate) -> JobOffer:
        await self._load()

        if job_id not in self._cache:
            raise KeyError(job_id)

        updated = JobOffer(
            id=job_id,
            **payload.dict(exclude={"requirements"}),
            requirements=[
                Requirement(id=str(uuid.uuid4()), **r.dict())
                for r in payload.requirements
            ],
        )

        self._cache[job_id] = updated
        await self._flush()
        return updated

    async def delete(self, job_id: str):
        await self._load()

        if job_id not in self._cache:
            raise KeyError(job_id)

        del self._cache[job_id]
        await self._flush()
