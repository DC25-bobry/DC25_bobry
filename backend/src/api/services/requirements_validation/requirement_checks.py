from backend.src.api.models.candidate_model import CandidateModel
from backend.src.api.models.job_offer_model import Requirement, JobOfferModel, RequirementType
from backend.src.api.services.requirements_validation.separate_required_requirements import \
    separate_required_requirements
from datetime import datetime

def check_skills_from_cv(candidate: CandidateModel, requirement: Requirement) -> bool:
    for skill in candidate.skills or []:
        if requirement.name.lower() == skill.name.lower():
            return True
        else:
            for synonym in requirement.synonyms or []:
                if synonym.lower() == skill.name.lower():
                    return True
    return False

def check_education_from_cv(candidate: CandidateModel, requirement: Requirement) -> bool:
    current_year = datetime.today().year
    for education in candidate.educations or []:
        if requirement.name.lower() == "student":
            if current_year < education.end_year:
                return True
        else:
            if current_year > education.end_year:
                return True
    return False

def check_requirements(candidate: CandidateModel, job_offer: JobOfferModel) -> bool:
        requirements_met = True

        requirements = separate_required_requirements(job_offer)
        for requirement in requirements:
            match requirement.type:
                case RequirementType.SKILL | RequirementType.LANGUAGE | RequirementType.OTHER:
                    if not check_skills_from_cv(candidate, requirement):
                        requirements_met = False
                case RequirementType.EDUCATION:
                    if not check_education_from_cv(candidate, requirement):
                        requirements_met = False



        return requirements_met