from backend.src.api.models.candidate_model import CandidateModel
from backend.src.api.models.job_offer_model import JobOfferModel, Requirement, RequirementType
from backend.src.api.services.requirements_validation.requirement_checks import *
from backend.src.email.email_generator import EmailGenerator
from backend.src.email.email_service import EmailService

class RequirementsValidationService:
    def __init__(self, candidate: CandidateModel, job_offer: JobOfferModel) -> None:
        self.candidate = candidate
        self.job_offer = job_offer

    def validate_requirements(self) -> None:
        requirements_met = check_requirements(self.candidate, self.job_offer)
        if requirements_met:
            pass
            # to further validation
        else:
            email_service = EmailService()
            generator = EmailGenerator()
            rejection_message = ((generator.set_name(self.candidate.name)
                                  .set_position(self.job_offer.position)
                                  .set_template(EmailGenerator.REJECTED))
                                 .generate())
            email_service.send_email_from_file(self.candidate.email, self.job_offer.position, rejection_message)

