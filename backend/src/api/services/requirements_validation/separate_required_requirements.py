from backend.src.api.models.job_offer_model import JobOfferModel, Requirement
from typing import List

def separate_required_requirements(job_offer: JobOfferModel) -> List[Requirement]:
    separated_requirements: List[Requirement] = []

    for requirement in job_offer.requirements:
        if requirement.priority == Requirement.Priority.REQUIRED:
            separated_requirements.append(requirement)

    return separated_requirements
