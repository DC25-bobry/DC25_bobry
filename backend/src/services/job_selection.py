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
    GENERIC_POSITION_PATTERN = re.compile(
        r"(stanowisk[oa]|aplikuj[ęe]\s+na|aplikacja\s+na|position)\s*:?\s*(.+)",
        re.IGNORECASE,
    )

    def select_jobs(
        self,
        cv_text: str,
        all_jobs: Iterable[JobOffer],
    ) -> JobSelectionResult:
        text_norm = cv_text.lower()
        active_jobs = [j for j in all_jobs if j.status in ("active", "ACTIVE")]

        for job in active_jobs:
            if job.title and job.title.lower() in text_norm:
                return JobSelectionResult(
                    jobs_to_consider=[job],
                    explicit_title=job.title,
                    explicit_title_matched=True,
                    global_rejection_reason=None,
                )

        m = self.GENERIC_POSITION_PATTERN.search(cv_text)
        if m:
            raw_title = m.group(2).strip()
            reason = (
                f"CV zawiera aplikację na stanowisko '{raw_title}', "
                f"którego nie ma w aktualnie otwartych ofertach."
            )
            return JobSelectionResult(
                jobs_to_consider=[],
                explicit_title=raw_title,
                explicit_title_matched=False,
                global_rejection_reason=reason,
            )

        return JobSelectionResult(
            jobs_to_consider=active_jobs,
            explicit_title=None,
            explicit_title_matched=False,
            global_rejection_reason=None,
        )
