
import sys
from pathlib import Path

BASE_DIR = (Path(__file__).resolve().parent.parent)
sys.path.insert(0, str(BASE_DIR))

from core.recommendation_bridge import (ModuleCandidate)
from core.recommendation_view import (build_recommendation_view)

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

answers = {
    "wifi_required": True,
    "ble_required": True,
    "bluetooth_classic_required": True,
    "wifi6_required": True,
    "wifi6_mandatory": True,
    "high_throughput_required": True,
    "host_interface": "pcie_usb",
}

view =build_recommendation_view(answers, modules)

assert view["has_recommendation"] is True

assert (view["explanation"].recommended.module_id == "USE_8852")
assert (view["explanation"].recommended.match_percent == 100)
assert len(view["explanation"].alternatives) == 1
assert (view["explanation"].alternatives[0].module_id == "USE_8851")
assert (view["comparison"].candidates[0].module_id == "USE_8852")
print("Recommendation view model: PASS")

impossible_answers = {"host_interface": "sdio", "host_interface_mandatory": True}
no_match_view = (build_recommendation_view(impossible_answers, modules))
assert (no_match_view["has_recommendation"] is False)
assert (no_match_view["explanation"].recommended is None)
assert (no_match_view["comparison"].has_candidates is False)
print("No-match view model: PASS")

