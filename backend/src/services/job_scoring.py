from __future__ import annotations

from typing import List

from backend.src.models.candidate_matching import JobMatch, RequirementMatch
from backend.src.models.job_offers_model import JobOffer
from backend.src.services.synonym_recognition import SynonymRecognizer


class JobMatchScorer:
    def __init__(self, synonym_recognizer: SynonymRecognizer | None):
        self.synonym_recognizer = synonym_recognizer

    @staticmethod
    def _normalize(text: str) -> str:
        return text.lower()

    def _match_requirement(self, text_norm: str, keywords: List[str]) -> bool:
        if not keywords:
            return False

        for kw in keywords:
            kw_norm = kw.lower().strip()
            if not kw_norm:
                continue

            if kw_norm in text_norm:
                return True

            if self.synonym_recognizer:
                synonyms = self.synonym_recognizer.find_synonyms(kw_norm)
                if synonyms:
                    return True

        return False

    def score_for_job(self, cv_text: str, job: JobOffer) -> JobMatch:
        text_norm = self._normalize(cv_text)

        matched_reqs: List[RequirementMatch] = []
        missing_required: List[RequirementMatch] = []
        missing_optional: List[RequirementMatch] = []

        total_score = 0
        max_score = 0

        for req in job.requirements or []:
            max_score += req.weight

            keywords = req.keywords or []

            matched = self._match_requirement(text_norm, keywords)

            rm = RequirementMatch(
                requirement_id=getattr(req, "id", None),
                name=req.name,
                priority=req.priority,
                weight=req.weight,
                matched=matched,
            )

            if matched:
                matched_reqs.append(rm)
                total_score += req.weight
            else:
                if req.priority == "REQUIRED":
                    missing_required.append(rm)
                else:
                    missing_optional.append(rm)

        rejection_reasons: List[str] = []
        if missing_required:
            reason = "Brak wymaganych kompetencji: " + ", ".join(
                r.name for r in missing_required
            )
            rejection_reasons.append(reason)
            status = "REJECTED"
            total_score = 0
            score_percent = 0
        else:
            status = "MATCHED"
            score_percent = int(round((total_score / max_score) * 100)) if max_score > 0 else 0

        return JobMatch(
            job_id=job.id,
            job_title=job.title,
            status=status,
            score_percent=score_percent,
            total_score=total_score,
            max_score=max_score,
            matched_requirements=matched_reqs,
            missing_required=missing_required,
            missing_optional=missing_optional,
            rejection_reasons=rejection_reasons,
        )
