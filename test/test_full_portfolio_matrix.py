import json
import sys

from pathlib import Path


BASE_DIR = (Path(__file__).resolve().parent.parent)


sys.path.insert(0,str(BASE_DIR))

from core.customer_requirement import (create_empty_requirement)
from core.selection_engine import (evaluate_portfolio)

MODULE_FILE = (BASE_DIR/ "data"/ "modules.json")

with open(MODULE_FILE, "r", encoding="utf-8") as file:
    database = json.load(file)

modules = database["modules"]

def run_scenario(scenario_name,requirement,expected_module):
    """
    Evaluate one simulated customer requirement
    against the entire Unisem portfolio.
    """

    results = evaluate_portfolio(requirement, modules)
    primary = results[0]

    passed = (primary["module_id"] == expected_module and primary["status"] == "COMPATIBLE")
    print()
    print("=" * 70)
    print(scenario_name)
    print("=" * 70)
    print("Expected:", expected_module)
    print("Selected:", primary["module_id"])
    print("Status:", primary["status"])
    print("Preference score:",primary["preference_score"])
    print()
    print("Top 3:")
    for index, result in enumerate(results[:3], start=1):
        print(f"  {index}.",result["module_id"],"-",result["status"],"- score:",result["preference_score"])

    if passed:
        print()
        print("RESULT: PASS")

    else:
        print()
        print("RESULT: FAIL")
        print()
        print("Primary module failures:")
        for failure in primary["hard_failures"]:
            print("   ", failure)

    assert passed
    return results
    
    
requirement = (create_empty_requirement())
requirement["application"]["name"] = "Low-Power Sensor"
requirement["connectivity"]["ble_required"] = True
requirement["embedded_features"]["integrated_mcu_required"] = True
requirement["preferences"]["low_power"] = True

run_scenario("SCENARIO 1 - LOW POWER BLE SENSOR", requirement, "USE_8762_MINI")

requirement = (create_empty_requirement())
requirement["application"]["name"] = "Wireless Battery Management System"
requirement["connectivity"]["ble_required"] = True
requirement["embedded_features"]["integrated_mcu_required"] = True
requirement["interfaces"]["can_required"] = True
run_scenario("SCENARIO 2 - BLE + CAN / WIRELESS BMS", requirement, "USE_45")

requirement = (create_empty_requirement())
requirement["application"]["name"] = "Bluetooth Audio Receiver"
requirement["connectivity"]["ble_required"] = True
requirement["connectivity"]["bluetooth_classic_required"] = True
requirement["bluetooth"]["audio_required"] = True


run_scenario("SCENARIO 3 - BLUETOOTH AUDIO", requirement,"USE_8763_M")

requirement = (create_empty_requirement())
requirement["application"]["name"] = "USB Wi-Fi Camera"
requirement["connectivity"]["wifi_required"] = True
requirement["interfaces"]["usb_available"] = True
requirement["interfaces"]["sdio_available"] = False
requirement["interfaces"]["pcie_available"] = False
requirement["preferences"]["compact_size"] = True

run_scenario("SCENARIO 4 - COMPACT USB WI-FI", requirement, "USE_8188_FN")

requirement = (create_empty_requirement())

requirement["application"]["name"] = "SDIO Wi-Fi Display"
requirement["connectivity"]["wifi_required"] = True
requirement["interfaces"]["usb_available"] = False
requirement["interfaces"]["sdio_available"] = True
requirement["interfaces"]["pcie_available"] = False
requirement["preferences"]["compact_size"] = True

run_scenario("SCENARIO 5 - COMPACT SDIO WI-FI", requirement, "USE_8189")

requirement = (create_empty_requirement())
requirement["application"]["name"] = "Smart Energy Meter"
requirement["connectivity"]["wifi_required"] = True
requirement["connectivity"]["ble_required"] = True
requirement["embedded_features"]["integrated_mcu_required"] = True
requirement["preferences"]["cost_optimized"] = True
requirement["environment"]["minimum_temperature_c"] = -40
requirement["environment"]["maximum_temperature_c"] = 85

run_scenario("SCENARIO 6 - COST OPTIMIZED EMBEDDED WI-FI + BLE", requirement, "USE_8720_CF")

requirement = (create_empty_requirement())
requirement["application"]["name"] = "Industrial Energy Gateway"
requirement["connectivity"]["wifi_required"] = True
requirement["connectivity"]["ble_required"] = True
requirement["wifi"]["band_5ghz_required"] = True
requirement["embedded_features"]["integrated_mcu_required"] = True
requirement["environment"]["minimum_temperature_c"] = -40
requirement["environment"]["maximum_temperature_c"] = 85

run_scenario("SCENARIO 7 - DUAL BAND EMBEDDED WI-FI + BLE", requirement, "USE_8720_DF")

requirement = (create_empty_requirement())
requirement["application"]["name"] = "Smart HMI Controller"
requirement["connectivity"]["wifi_required"] = True
requirement["connectivity"]["ble_required"] = True
requirement["wifi"]["band_5ghz_required"] = True
requirement["embedded_features"]["integrated_mcu_required"] = True
requirement["embedded_features"]["adc_required"] = True
requirement["embedded_features"]["capacitive_touch_required"] = True

run_scenario("SCENARIO 8 - FEATURE RICH EMBEDDED HMI", requirement, "USE_8721")

requirement = (create_empty_requirement())
requirement["application"]["name"] = "Embedded Linux Media Device"
requirement["connectivity"]["wifi_required"] = True
requirement["connectivity"]["ble_required"] = True
requirement["connectivity"]["bluetooth_classic_required"] = True
requirement["wifi"]["band_5ghz_required"] = True
requirement["interfaces"]["usb_available"] = True
requirement["interfaces"]["pcie_available"] = False

run_scenario("SCENARIO 9 - USB WI-FI + BLUETOOTH COMBO", requirement, "USE_8733")

requirement = (create_empty_requirement())
requirement["application"]["name"] = "Compact Wi-Fi 6 Smart Display"
requirement["connectivity"]["wifi_required"] = True
requirement["connectivity"]["ble_required"] = True
requirement["connectivity"]["bluetooth_classic_required"] = True
requirement["wifi"]["band_5ghz_required"] = True
requirement["wifi"]["wifi6_required"] = True
requirement["interfaces"]["pcie_available"] = True
requirement["interfaces"]["usb_available"] = True
requirement["preferences"]["compact_size"] = True
requirement["preferences"]["high_performance"] = True

run_scenario("SCENARIO 10 - COMPACT 1x1 WI-FI 6", requirement, "USE_8851")


requirement = (create_empty_requirement())
requirement["application"]["name"] = "High Performance Infotainment"
requirement["connectivity"]["wifi_required"] = True
requirement["connectivity"]["ble_required"] = True
requirement["connectivity"]["bluetooth_classic_required"] = True
requirement["wifi"]["band_5ghz_required"] = True
requirement["wifi"]["wifi6_required"] = True
requirement["wifi"]["mimo_2x2_required"] = True
requirement["interfaces"]["pcie_available"] = True
requirement["interfaces"]["usb_available"] = True
requirement["preferences"]["high_performance"] = True

run_scenario("SCENARIO 11 - HIGH PERFORMANCE 2x2 WI-FI 6", requirement, "USE_8852")

expected_modules = {
        "USE_8762_MINI",
        "USE_45",
        "USE_8763_M",
        
        "USE_8188_FN",
        "USE_8189",
        
        "USE_8720_CF",
        "USE_8720_DF",
        "USE_8721",
        
        "USE_8733",
        "USE_8851",
        "USE_8852"
    }
    
database_modules = {
    module["id"]
    for module in modules
    }
    
assert(expected_modules == database_modules)

print()
print()
print("=" * 70)
print("ALL 11 UNISEM MODULE SCENARIOS PASSED")
print("=" * 70)


        