
import sys
from pathlib import Path

BASE_DIR = (Path(__file__).resolve().parent.parent)
sys.path.insert(0, str(BASE_DIR))


from core.customer_requirements import (
    CustomerRequirements,
    requirements_from_answers,
)

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


answers = {
    "wifi_required": True,
    "ble_required": True,
    "bluetooth_classic_required": True,
    "wifi6_required": True,
    "high_throughput_required": True,
    "host_interface": "pcie_usb",
}


requirements = requirements_from_answers(
    answers
)


assert requirements.wifi_required is True
assert requirements.ble_required is True
assert requirements.bluetooth_classic_required is True
assert requirements.wifi6_required is True
assert requirements.high_throughput_required is True

assert requirements.host_interface == "pcie_usb"


print("Requirements conversion: PASS")

empty_requirements = requirements_from_answers({})

assert empty_requirements.wifi_required is False
assert empty_requirements.ble_required is False
assert (empty_requirements.bluetooth_classic_required is False)
assert empty_requirements.wifi6_required is False
assert (empty_requirements.high_throughput_required is False)
assert empty_requirements.host_interface is None

print("Missing-answer defaults: PASS")


shortlist = recommend_from_answers( answers, modules)

print()
print("Recommendation results")
print("----------------------")

for result in shortlist.results:
    print(
        f"{result.rank}. "
        f"{result.module_id} "
        f"{result.match_percent}%"
    )
    
    
assert shortlist.best is not None

assert (
    shortlist.best.module_id
    == "USE_8852"
)

assert shortlist.best.rank == 1
assert shortlist.best.match_percent == 100

assert (
    shortlist.results[1].module_id
    == "USE_8851"
)

assert (
    shortlist.results[2].module_id
    == "USE_8733"
)

print("Ranking test: PASS")

best = shortlist.best

assert (
    "Supports Wi-Fi 6"
    in best.reasons
)

assert (
    "Suitable for high-throughput applications"
    in best.reasons
)

assert (
    "Matches the required host interface"
    in best.reasons
)

print("Explanation generation: PASS")


usb_customer = {
    "wifi_required": True,
    "ble_required": True,
    "bluetooth_classic_required": True,

    "wifi6_required": False,
    "high_throughput_required": False,

    "host_interface": "usb",
}

usb_shortlist = recommend_from_answers( usb_customer, modules)
assert (usb_shortlist.best.module_id== "USE_8733")

print("USB customer test: PASS")

print()
print("LESSON 3B: ALL TESTS PASS")