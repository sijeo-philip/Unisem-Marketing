import sys
from pathlib import Path

BASE_DIR = (Path(__file__).resolve().parent.parent)
sys.path.insert(0, str(BASE_DIR))


from core.recommendation_bridge import (
    ModuleCandidate,
    recommend_from_answers,
)

from core.recommendation_explanation import (
    explain_shortlist,
    render_shortlist_text,
)

modules = [
    ModuleCandidate(
        module_id="USE_8733",
        wifi=True,
        ble=True,
        bluetooth_classic=True,
        wifi6=False,
        high_throughput=False,
        host_interfaces=("usb",),
    ),

    ModuleCandidate(
        module_id="USE_8851",
        wifi=True,
        ble=True,
        bluetooth_classic=True,
        wifi6=True,
        high_throughput=False,
        host_interfaces=("pcie_usb",),
    ),

    ModuleCandidate(
        module_id="USE_8852",
        wifi=True,
        ble=True,
        bluetooth_classic=True,
        wifi6=True,
        high_throughput=True,
        host_interfaces=("pcie_usb",),
    ),
]

customer = {
    "wifi_required": True,

    "ble_required": True,

    "bluetooth_classic_required": True,

    "wifi6_required": True,
    "wifi6_mandatory": True,

    "high_throughput_required": True,

    "host_interface": "pcie_usb",
}

shortlist = recommend_from_answers(
    customer,
    modules,
)

explanation = explain_shortlist(
    shortlist
)

text = render_shortlist_text(
    explanation
)

print(text)

assert explanation.recommended is not None

assert (
    explanation.recommended.module_id
    == "USE_8852"
)

assert (
    explanation.recommended.status
    == "ELIGIBLE"
)

assert (
    explanation.recommended.rank
    == 1
)

assert (
    explanation.recommended.match_percent
    == 100
)

assert (
    "Supports Wi-Fi 6"
    in explanation.recommended.strengths
)

print(
    "Recommended explanation test: PASS"
)

assert len(
    explanation.alternatives
) == 1

alternative = (
    explanation.alternatives[0]
)

assert alternative.module_id == "USE_8851"

assert alternative.rank == 2

assert alternative.status == "ELIGIBLE"

assert (
    "Not optimized for the preferred "
    "throughput level"
    in alternative.tradeoffs
)

print(
    "Alternative explanation test: PASS"
)

assert len(
    explanation.rejected
) == 1

rejected = explanation.rejected[0]

assert rejected.module_id == "USE_8733"

assert rejected.status == "INELIGIBLE"

assert (
    "Mandatory Wi-Fi 6 capability "
    "is not available"
    in rejected.blockers
)

print(
    "Rejected explanation test: PASS"
)

assert (
    "RECOMMENDED: USE_8852"
    in text
)

assert (
    "ALTERNATIVES:"
    in text
)

assert (
    "USE_8851"
    in text
)

assert (
    "NOT ELIGIBLE:"
    in text
)

assert (
    "USE_8733"
    in text
)

print(
    "Rendered explanation test: PASS"
)

impossible_customer = {
    "wifi_required": True,

    "host_interface": "sdio",
    "host_interface_mandatory": True,
}

no_match_shortlist = (
    recommend_from_answers(
        impossible_customer,
        modules,
    )
)

no_match_explanation = (
    explain_shortlist(
        no_match_shortlist
    )
)

assert (
    no_match_explanation.recommended
    is None
)

assert (
    no_match_explanation.alternatives
    == []
)

assert len(
    no_match_explanation.rejected
) == 3

assert (
    "No module currently satisfies"
    in no_match_explanation.summary
)

print(
    "No-match explanation test: PASS"
)

simple_customer = {
    "wifi_required": True,
    "ble_required": True,
}

simple_shortlist = (
    recommend_from_answers(
        simple_customer,
        modules,
    )
)

simple_explanation = (
    explain_shortlist(
        simple_shortlist,
        max_alternatives=1,
    )
)

assert (
    simple_explanation.recommended
    is not None
)

assert len(
    simple_explanation.alternatives
) == 1

print(
    "Alternative-limit test: PASS"
)

print()
print(
    "LESSON 3D: ALL TESTS PASS"
)