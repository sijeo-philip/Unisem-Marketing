

from dataclasses import dataclass
from typing import List

from core.customer_requirements import (
    CustomerRequirements,
    requirements_from_answers,
)

from core.recommendation_result import (
    RecommendationResult,
    RecommendationShortlist,
)


@dataclass
class ModuleCandidate:
    module_id: str

    wifi: bool = False
    ble: bool = False
    bluetooth_classic: bool = False

    wifi6: bool = False
    high_throughput: bool = False

    host_interfaces: tuple = ()


def _evaluate_requirement(
    *,
    required: bool,
    mandatory: bool,
    supported: bool,
    weight: float,
    success_message: str,
    preference_failure_message: str,
    mandatory_failure_message: str,
    reasons: list,
    considerations: list,
    rejection_reasons: list,
):
    """
    Evaluate one customer requirement.

    Returns:
        earned_weight,
        total_weight
    """

    if not required:
        return 0.0, 0.0

    total_weight = weight

    if supported:
        reasons.append(success_message)
        return weight, total_weight
    if mandatory:
        rejection_reasons.append(mandatory_failure_message)
    else:
        considerations.append(preference_failure_message)
    return 0.0, total_weight


def evaluate_candidate(module: ModuleCandidate,requirements: CustomerRequirements) -> RecommendationResult:

    reasons = []
    considerations = []
    rejection_reasons = []

    total_weight = 0.0
    earned_weight = 0.0

    earned, total = _evaluate_requirement(
        required=requirements.wifi_required,
        mandatory=requirements.wifi_mandatory,
        supported=module.wifi,
        weight=20,

        success_message=("Supports required Wi-Fi connectivity"),
        preference_failure_message=("Does not provide preferred Wi-Fi connectivity"),
        mandatory_failure_message=("Mandatory Wi-Fi capability is not available"),
        reasons=reasons,
        considerations=considerations,
        rejection_reasons=rejection_reasons,
    )

    earned_weight += earned
    total_weight += total

    earned, total = _evaluate_requirement(
        required=requirements.ble_required,
        mandatory=requirements.ble_mandatory,
        supported=module.ble,
        weight=20,
        success_message=("Supports required Bluetooth LE"),
        preference_failure_message=("Does not provide preferred Bluetooth LE"),
        mandatory_failure_message=("Mandatory Bluetooth LE capability is not available"),
        reasons=reasons,
        considerations=considerations,
        rejection_reasons=rejection_reasons,
    )

    earned_weight += earned
    total_weight += total

    earned, total = _evaluate_requirement(required=(requirements.bluetooth_classic_required),
        mandatory=(requirements.bluetooth_classic_mandatory),
        supported=module.bluetooth_classic,
        weight=20,
        success_message=("Supports Bluetooth Classic"),
        preference_failure_message=("Does not provide preferred Bluetooth Classic"),
        mandatory_failure_message=("Mandatory Bluetooth Classic capability is not available"),
        reasons=reasons,
        considerations=considerations,
        rejection_reasons=rejection_reasons,
    )

    earned_weight += earned
    total_weight += total
    earned, total = _evaluate_requirement(required=requirements.wifi6_required, mandatory=requirements.wifi6_mandatory,
        supported=module.wifi6, weight=20, success_message=("Supports Wi-Fi 6"),
        preference_failure_message=("Does not support preferred Wi-Fi 6" ),
        mandatory_failure_message=("Mandatory Wi-Fi 6 capability is not available" ),
        reasons=reasons, considerations=considerations,
        rejection_reasons=rejection_reasons,
    )
    earned_weight += earned
    total_weight += total
    earned, total = _evaluate_requirement(required=(requirements.high_throughput_required),
        mandatory=(requirements.high_throughput_mandatory),
        supported=module.high_throughput,
        weight=10,
        success_message=("Suitable for high-throughput applications"),
        preference_failure_message=("Not optimized for the preferred throughput level"),
        mandatory_failure_message=("Mandatory high-throughput capability is not available"),
        reasons=reasons,
        considerations=considerations,
        rejection_reasons=rejection_reasons,
    )
    earned_weight += earned
    total_weight += total
    if requirements.host_interface:
        host_supported = (
            requirements.host_interface
            in module.host_interfaces
        )
        earned, total = _evaluate_requirement(required=True, mandatory=(requirements.host_interface_mandatory),
            supported=host_supported, weight=10, success_message=("Matches the required host interface"),
            preference_failure_message=("Preferred host interface is not available"),
            mandatory_failure_message=("Mandatory host interface is not available"),
            reasons=reasons, considerations=considerations, rejection_reasons=rejection_reasons,
        )

        earned_weight += earned
        total_weight += total
    if total_weight > 0:
        score = (earned_weight / total_weight) * 100.0
    else:
        score = 0.0
    eligible = (len(rejection_reasons) == 0)
    return RecommendationResult(
        module_id=module.module_id,
        score=score,
        reasons=reasons,
        considerations=considerations,
        eligible=eligible,
        rejection_reasons=rejection_reasons,
    )


def recommend_from_answers(answers: dict, modules: List[ModuleCandidate]) -> RecommendationShortlist:
    requirements = requirements_from_answers(answers)
    results = []
    for module in modules:
        result = evaluate_candidate(module, requirements)
        results.append(result)
    shortlist = RecommendationShortlist(results=results)
    shortlist.sort_by_score()
    return shortlist