

from dataclasses import dataclass
from typing import Optional


@dataclass
class CustomerRequirements:
    wifi_required: bool = False
    wifi_mandatory: bool = False

    ble_required: bool = False
    ble_mandatory: bool = False

    bluetooth_classic_required: bool = False
    bluetooth_classic_mandatory: bool = False

    wifi6_required: bool = False
    wifi6_mandatory: bool = False

    high_throughput_required: bool = False
    high_throughput_mandatory: bool = False

    host_interface: Optional[str] = None
    host_interface_mandatory: bool = False


def _as_bool(value) -> bool:
    """
    Convert common questionnaire values safely to bool.

    Supports:
        True / False
        1 / 0
        "yes" / "no"
        "true" / "false"
        "mandatory"
    """

    if isinstance(value, bool):
        return value

    if value is None:
        return False

    if isinstance(value, str):
        return value.strip().lower() in {
            "1",
            "true",
            "yes",
            "y",
            "required",
            "mandatory",
        }

    return bool(value)


def requirements_from_answers(answers: dict) -> CustomerRequirements:
    wifi_required = _as_bool(answers.get("wifi_required", False))
    ble_required = _as_bool(answers.get("ble_required", False))
    bluetooth_classic_required = _as_bool(answers.get("bluetooth_classic_required", False))

    wifi6_required = _as_bool(answers.get("wifi6_required", False))

    high_throughput_required = _as_bool(answers.get("high_throughput_required", False))
    host_interface = answers.get("host_interface")
    return CustomerRequirements(
        wifi_required=wifi_required,
        wifi_mandatory=(wifi_required and _as_bool(answers.get( "wifi_mandatory", False))),
        ble_required=ble_required,
        ble_mandatory=(ble_required and _as_bool(answers.get("ble_mandatory", False))),
        bluetooth_classic_required=(bluetooth_classic_required),
        bluetooth_classic_mandatory=(bluetooth_classic_required and _as_bool(answers.get("bluetooth_classic_mandatory", False))),
        wifi6_required=wifi6_required,
        wifi6_mandatory=(wifi6_required and _as_bool(answers.get("wifi6_mandatory", False))),
        high_throughput_required=(high_throughput_required),
        high_throughput_mandatory=(high_throughput_required and _as_bool(answers.get("high_throughput_mandatory", False))),
        host_interface=host_interface,
        host_interface_mandatory=(bool(host_interface) and _as_bool(answers.get("host_interface_mandatory", False))),
    )
    
    