from backend.src.api.models.candidate_model import CandidateModel
from backend.src.api.models.job_offer_model import JobOfferModel, Requirement, RequirementType
from backend.src.api.services.requirements_validation.separate_required_requirements import \
    separate_required_requirements
from backend.src.email.email_service import EmailService
from requirement_checks import *
from backend.src.email.email_generator import EmailGenerator

class RequirementsValidationService:
    def __init__(self, candidate: CandidateModel, job_offer: JobOfferModel) -> None:
        self.candidate = candidate
        self.job_offer = job_offer

    def check_requirements(self) -> bool:
        email_service = EmailService()
        generator = EmailGenerator()
        requirements_met = True
        if (not self.candidate.health_certificate
                or not self.candidate.dental_parameters.valid_dental_checkup
                or self.candidate.dental_parameters.teeth_spacing > 5.0):
            requirements_met = False

        requirements = separate_required_requirements(self.job_offer)
        for requirement in requirements:
            valid = check_requirement_from_cv(candidate=self.candidate, requirement=requirement)
            if not valid:
                requirements_met = False

        if not requirements_met:
            rejection_message = ((generator.set_name(self.candidate.name)
                                 .set_position(self.job_offer.position)
                                 .set_template(EmailGenerator.REJECTED))
                                 .generate())
            email_service.send_email_from_file(self.candidate.email, self.job_offer.position, rejection_message)

        return requirements_met
