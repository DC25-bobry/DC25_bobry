import logging
from typing import List, Optional

from backend.src.models.candidate_profile import CandidateProfile
from backend.src.models.candidate_matching import JobMatch
from backend.src.models.job_offers_model import JobOffer
from backend.src.services.candidate_extraction.candidate_extractor import CandidateExtractor
from backend.src.services.candidate_storage import GoogleDriveCandidateStore
from backend.src.services.job_selection import JobSelectionService
from backend.src.services.job_scoring import JobMatchScorer
from backend.src.services.synonym_recognition import SynonymRecognizer

logger = logging.getLogger(__name__)


def process_file(
    file_bytes: bytes,
    filename: str,
    content_type: Optional[str],
    parsing_service,
    cv_drive_file_id: Optional[str],
    jobs: List[JobOffer],
) -> None:

    parsed_document = parsing_service.extract_text(file_bytes, filename=filename, content_type=content_type)
    cv_text: str = parsed_document.text

    extractor = CandidateExtractor()
    profile: CandidateProfile = extractor.extract(cv_text)

    selection_service = JobSelectionService()
    selection_result = selection_service.select_jobs(cv_text, jobs)

    job_matches: List[JobMatch] = []
    global_reason: Optional[str] = selection_result.global_rejection_reason

    if not global_reason:
        synonym_recognizer = SynonymRecognizer(cv_text)
        scorer = JobMatchScorer(synonym_recognizer)

        job_matches = [
            scorer.score_for_job(cv_text, job)
            for job in selection_result.jobs_to_consider
        ]

    store = GoogleDriveCandidateStore()
    record = store.append_candidate(
        profile=profile,
        job_matches=job_matches,
        cv_drive_file_id=cv_drive_file_id,
        global_rejection_reason=global_reason,
    )

    logger.info(
        "Zapisano kandydata %s %s (id=%s), dopasowania: %d, global_reason=%s",
        profile.name,
        profile.surname,
        record.id,
        len(record.job_matches),
        global_reason,
    )
