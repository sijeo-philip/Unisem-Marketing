
import sys
from pathlib import Path

BASE_DIR = (Path(__file__).resolve().parent.parent)
sys.path.insert(0, str(BASE_DIR))


from core.recommendation_bridge import (
    ModuleCandidate,
)

from core.module_comparison import (
    build_module_comparison,
    render_comparison_text,
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

customer = {
    "wifi_required": True,

    "ble_required": True,

    "bluetooth_classic_required": True,

    "wifi6_required": True,
    "wifi6_mandatory": True,

    "high_throughput_required": True,

    "host_interface": "pcie_usb",
}

comparison = (
    build_module_comparison(
        customer,
        modules,
        max_candidates=3,
    )
)

assert comparison.has_candidates

assert len(
    comparison.candidates
) == 2

assert (
    comparison.candidates[0].module_id
    == "USE_8852"
)

assert (
    comparison.candidates[0]
    .recommendation_label
    == "RECOMMENDED"
)

assert (
    comparison.candidates[1].module_id
    == "USE_8851"
)

assert (
    comparison.candidates[1]
    .recommendation_label
    == "ALTERNATIVE"
)

print(
    "Candidate selection test: PASS"
)

wifi6_row = comparison.get_row(
    "wifi6"
)
assert wifi6_row is not None

assert (
    wifi6_row.requirement_level
    == "MANDATORY"
)

cell = comparison.get_cell(
    "wifi6",
    "USE_8852",
)

assert cell is not None

assert cell.value == "Yes"

assert cell.status == "MATCH"

cell = comparison.get_cell(
    "wifi6",
    "USE_8851",
)

assert cell is not None

assert cell.value == "Yes"

assert cell.status == "MATCH"

print(
    "Mandatory capability comparison: PASS"
)

cell_8852 = comparison.get_cell(
    "high_throughput",
    "USE_8852",
)

cell_8851 = comparison.get_cell(
    "high_throughput",
    "USE_8851",
)

assert cell_8852 is not None
assert cell_8851 is not None

assert cell_8852.status == "MATCH"

assert (
    cell_8851.status
    == "TRADEOFF"
)

assert cell_8852.value == "Yes"
assert cell_8851.value == "No"

print(
    "Preference trade-off test: PASS"
)

host_row = comparison.get_row(
    "host_interface"
)

assert host_row is not None

assert (
    host_row.requirement_level
    == "PREFERRED"
)

host_8852 = comparison.get_cell(
    "host_interface",
    "USE_8852",
)

host_8851 = comparison.get_cell(
    "host_interface",
    "USE_8851",
)

assert host_8852.status == "MATCH"
assert host_8851.status == "MATCH"

assert host_8852.value == "pcie_usb"
assert host_8851.value == "pcie_usb"

print(
    "Host-interface comparison: PASS"
)
include_rejected=True
comparison_with_rejected = (
    build_module_comparison(
        customer,
        modules,

        max_candidates=3,

        include_rejected=True,
    )
)
assert len(
    comparison_with_rejected.candidates
) == 3

rejected_candidate = (
    comparison_with_rejected
    .candidates[2]
)

assert (
    rejected_candidate.module_id
    == "USE_8733"
)

assert (
    rejected_candidate.eligible
    is False
)

assert (
    rejected_candidate
    .recommendation_label
    == "NOT ELIGIBLE"
)

rejected_wifi6 = (
    comparison_with_rejected.get_cell(
        "wifi6",
        "USE_8733",
    )
)

assert rejected_wifi6 is not None

assert (
    rejected_wifi6.status
    == "BLOCKER"
)

assert rejected_wifi6.value == "No"

print(
    "Rejected-module comparison: PASS"
)
simple_customer = {
    "wifi_required": True,
}
simple_comparison = (
    build_module_comparison(
        simple_customer,
        modules,
        max_candidates=3,
    )
)

ble_cell = (
    simple_comparison.get_cell(
        "ble",
        "USE_8852",
    )
)

assert ble_cell is not None

assert ble_cell.status == "AVAILABLE"

print(
    "Available-extra capability test: PASS"
)

minimal_module = ModuleCandidate(
    module_id="TEST_WIFI_ONLY",

    wifi=True,

    ble=False,

    bluetooth_classic=False,

    wifi6=False,

    high_throughput=False,

    host_interfaces=(),
)
minimal_comparison = (
    build_module_comparison(
        simple_customer,

        [
            minimal_module,
        ],

        max_candidates=1,
    )
)

classic_cell = (
    minimal_comparison.get_cell(
        "bluetooth_classic",
        "TEST_WIFI_ONLY",
    )
)

assert classic_cell is not None

assert (
    classic_cell.status
    == "NOT_REQUIRED"
)

print(
    "Not-required capability test: PASS"
)

comparison_text = (
    render_comparison_text(
        comparison
    )
)

print()
print(comparison_text)

assert (
    "MODULE COMPARISON"
    in comparison_text
)

assert (
    "USE_8852"
    in comparison_text
)

assert (
    "USE_8851"
    in comparison_text
)

assert (
    "High Throughput"
    in comparison_text
)

assert (
    "TRADEOFF"
    in comparison_text
)

print(
    "Comparison renderer test: PASS"
)

impossible_customer = {
    "host_interface": "sdio",

    "host_interface_mandatory": True,
}
empty_comparison = (
    build_module_comparison(
        impossible_customer,
        modules,
    )
)

assert (
    empty_comparison.has_candidates
    is False
)

assert (
    empty_comparison.candidates
    == []
)

print(
    "No-match comparison test: PASS"
)

empty_text = (
    render_comparison_text(
        empty_comparison
    )
)

assert (
    empty_text
    == "No eligible modules available "
       "for comparison."
)

print()
print(
    "LESSON 3E: ALL TESTS PASS"
)
