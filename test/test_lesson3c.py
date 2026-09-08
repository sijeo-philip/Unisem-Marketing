import sys
from pathlib import Path

BASE_DIR = (Path(__file__).resolve().parent.parent)
sys.path.insert(0, str(BASE_DIR))

from core.recommendation_bridge import (
    ModuleCandidate,
    recommend_from_answers,
)


modules = [
    ModuleCandidate(
        module_id="USE_8733",
        wifi=True,
        ble=True,
        bluetooth_classic=True,
        wifi6=False,
        high_throughput=False,
        host_interfaces=(
            "usb",
        ),
    ),

    ModuleCandidate(
        module_id="USE_8851",
        wifi=True,
        ble=True,
        bluetooth_classic=True,
        wifi6=True,
        high_throughput=False,
        host_interfaces=(
            "pcie_usb",
        ),
    ),

    ModuleCandidate(
        module_id="USE_8852",
        wifi=True,
        ble=True,
        bluetooth_classic=True,
        wifi6=True,
        high_throughput=True,
        host_interfaces=(
            "pcie_usb",
        ),
    ),
]

preference_customer = {
    "wifi_required": True,
    "ble_required": True,
    "bluetooth_classic_required": True,

    "wifi6_required": True,
    "high_throughput_required": True,

    "host_interface": "pcie_usb",
}


preference_shortlist = recommend_from_answers(
    preference_customer,
    modules,
)


assert len(
    preference_shortlist.eligible_results
) == 3

assert len(
    preference_shortlist.ineligible_results
) == 0

assert (
    preference_shortlist.best_eligible.module_id
    == "USE_8852"
)

print(
    "Preference-only eligibility test: PASS"
)

mandatory_wifi6_customer = {
    "wifi_required": True,

    "wifi6_required": True,
    "wifi6_mandatory": True,

    "ble_required": True,

    "bluetooth_classic_required": True,

    "high_throughput_required": True,

    "host_interface": "pcie_usb",
}

wifi6_shortlist = recommend_from_answers(
    mandatory_wifi6_customer,
    modules,
)

print()
print("Mandatory Wi-Fi 6 test")
print("----------------------")

for item in wifi6_shortlist.results:

    print(
        item.module_id,
        item.status,
        item.match_percent,
        item.match_strength,
    )
    
assert (
    wifi6_shortlist.best_eligible.module_id
    == "USE_8852"
)

assert len(
    wifi6_shortlist.eligible_results
) == 2

assert len(
    wifi6_shortlist.ineligible_results
) == 1

rejected = (
    wifi6_shortlist.ineligible_results[0]
)

assert rejected.module_id == "USE_8733"

assert rejected.eligible is False

assert (
    "Mandatory Wi-Fi 6 capability "
    "is not available"
    in rejected.rejection_reasons
)

print(
    "Mandatory Wi-Fi 6 gating test: PASS"
)

high_performance_customer = {
    "wifi_required": True,

    "wifi6_required": True,
    "wifi6_mandatory": True,

    "high_throughput_required": True,
    "high_throughput_mandatory": True,

    "ble_required": True,

    "bluetooth_classic_required": True,

    "host_interface": "pcie_usb",
    "host_interface_mandatory": True,
}

performance_shortlist = (
    recommend_from_answers(
        high_performance_customer,
        modules,
    )
)

assert len(
    performance_shortlist.eligible_results
) == 1

assert (
    performance_shortlist.best_eligible.module_id
    == "USE_8852"
)

assert (
    performance_shortlist.top_eligible(3)[0].module_id
    == "USE_8852"
)

print(
    "Mandatory high-throughput test: PASS"
)

impossible_customer = {
    "wifi_required": True,

    "host_interface": "sdio",

    "host_interface_mandatory": True,
}

no_match_shortlist = recommend_from_answers(
    impossible_customer,
    modules,
)

assert (
    no_match_shortlist.best_eligible
    is None
)

assert (
    no_match_shortlist.top_eligible()
    == []
)

assert len(
    no_match_shortlist.eligible_results
) == 0

assert len(
    no_match_shortlist.ineligible_results
) == 3

print(
    "No eligible module test: PASS"
)

top_customer = {
    "wifi_required": True,
    "ble_required": True,
}

top_shortlist = recommend_from_answers(
    top_customer,
    modules,
)

top_two = top_shortlist.top_eligible(2)

assert len(top_two) == 2

assert top_two[0].rank == 1
assert top_two[1].rank == 2

print("Top-N shortlist test: PASS")

for item in preference_shortlist.results:

    print(
        item.module_id,
        item.match_percent,
        item.match_strength,
    )


assert (
    preference_shortlist.results[0].match_strength
    == "Excellent"
)

print("Match-strength test: PASS")

print()
print("LESSON 3C: ALL TESTS PASS")