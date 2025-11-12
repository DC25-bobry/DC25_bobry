from backend.src.api.models.candidate_model import CandidateModel
from backend.src.api.models.job_offer_model import Requirement

def check_requirement_from_cv(candidate: CandidateModel, requirement: Requirement) -> bool:
    for skill in candidate.skills:
        if requirement.name.lower() == skill.name.lower():
            return True
        else:
            for synonym in requirement.synonyms:
                if synonym.lower() == skill.name.lower():
                    return True
    return False