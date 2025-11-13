from typing import Dict, Any, List
from backend.src.api.models.job_offer_model import JobOfferModel, RequirementPriority
from backend.src.api.models.candidate_model import CandidateModel
from backend.src.api.services.requirements_validation.requirement_checks import check_requirement_met

# Base points assigned by requirement priority
BASE_POINTS_BY_PRIORITY = {
    RequirementPriority.REQUIRED: 1.0,
    RequirementPriority.IMPORTANT: 0.7,
    RequirementPriority.OPTIONAL: 0.4,
}

def score_requirements(candidate: CandidateModel, job_offer: JobOfferModel) -> Dict[str, Any]:
    """
    Evaluate every requirement, award base points for met requirements, then multiply by weight.
    Returns a dictionary with:
      - total_score: sum of awarded weighted points
      - max_score: sum of maximum (base * weight) over all requirements
      - percentage: total_score / max_score * 100 (0 if max_score == 0)
      - details: list of per-requirement breakdowns
    """
    total_score = 0.0
    max_score = 0.0
    details: List[Dict[str, Any]] = []

    for req in job_offer.requirements:
        base_points = BASE_POINTS_BY_PRIORITY.get(req.priority, 0.0)
        weighted_max = base_points * (req.weight or 1.0)

        met = check_requirement_met(candidate, req)
        awarded = weighted_max if met else 0.0

        details.append({
            "id": req.id,
            "name": req.name,
            "type": req.type.value if hasattr(req.type, "value") else str(req.type),
            "priority": req.priority.value if hasattr(req.priority, "value") else str(req.priority),
            "base_points": base_points,
            "weight": req.weight,
            "weighted_max_points": weighted_max,
            "met": met,
            "awarded_points": awarded,
        })

        total_score += awarded
        max_score += weighted_max

    percentage = (total_score / max_score * 100) if max_score > 0 else 0.0

    return {
        "total_score": total_score,
        "max_score": max_score,
        "percentage": percentage,
        "details": details,
    }