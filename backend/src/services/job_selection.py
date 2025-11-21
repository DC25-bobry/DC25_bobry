import re
from dataclasses import dataclass
from typing import List, Optional, Iterable

from backend.src.models.job_offers_model import JobOffer


@dataclass
class JobSelectionResult:
    jobs_to_consider: List[JobOffer]
    explicit_title: Optional[str]
    explicit_title_matched: bool
    global_rejection_reason: Optional[str]


class JobSelectionService:
    def select_jobs(
        self,
        cv_text: str,
        all_jobs: Iterable[JobOffer],
    ) -> JobSelectionResult:
        text_norm = cv_text.lower()

        text_without_contacts = re.sub(r"\S+@\S+", " ", text_norm)
        text_without_contacts = re.sub(r"https?://\S+", " ", text_without_contacts)

        text_without_contacts = re.sub(r"\s+", " ", text_without_contacts)

        active_jobs = [j for j in all_jobs if j.status in ("active", "ACTIVE")]

        for job in active_jobs:
            if not job.title:
                continue

            title_norm = job.title.strip().lower()
            if not title_norm:
                continue

            pattern = r"\b" + re.escape(title_norm) + r"\b"
            if re.search(pattern, text_without_contacts):
                return JobSelectionResult(
                    jobs_to_consider=[job],
                    explicit_title=job.title,
                    explicit_title_matched=True,
                    global_rejection_reason=None,
                )

        return JobSelectionResult(
            jobs_to_consider=active_jobs,
            explicit_title=None,
            explicit_title_matched=False,
            global_rejection_reason=None,
        )
