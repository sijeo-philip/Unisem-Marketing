import json
from pathlib import Path
import sys


BASE_DIR = (Path(__file__).resolve().parent.parent)


sys.path.insert(0, str(BASE_DIR))


from core.customer_requirement import (create_empty_requirement)
from core.selection_engine import (evaluate_portfolio)


# =========================================================
# LOAD MODULE DATABASE
# =========================================================

with open(BASE_DIR/ "data"/ "modules.json", "r", encoding="utf-8") as file:
    database = json.load(file)


modules = database["modules"]


# =========================================================
# CUSTOMER SCENARIO
#
# High-performance automotive infotainment
# =========================================================

requirement = (create_empty_requirement())


requirement["application"]["name"] = "Automotive Infotainment"
requirement["connectivity"]["wifi_required"] = True
requirement["connectivity"]["ble_required"] = True
requirement["connectivity"]["bluetooth_classic_required"] = True
requirement["wifi"]["band_5ghz_required"] = True
requirement["wifi"]["wifi6_required"] = True
requirement["wifi"]["mimo_2x2_required"] = True
requirement["interfaces"]["pcie_available"] = True
requirement["interfaces"]["usb_available"] = True
requirement["environment"]["minimum_temperature_c"] = 0
requirement["environment"]["maximum_temperature_c"] = 70
requirement["preferences"]["high_performance"] = True


# =========================================================
# EVALUATE COMPLETE PORTFOLIO
# =========================================================

results = evaluate_portfolio(requirement, modules)


# =========================================================
# DISPLAY RESULTS
# =========================================================

print()
print("UNISEM PORTFOLIO SELECTION")

print("==========================")
print()

print("Application:",requirement["application"]["name"])

print()


for index, result in enumerate(results, start=1):

    print(index,result["module_name"])
    print("   Status:",result["status"])
    print("   Preference score:", result["preference_score"])

    if result["hard_failures"]:
        print("   Why rejected:")
        for failure in result["hard_failures"]:
            print("      -", failure)

    if result["clarifications"]:
        print("   Needs confirmation:")
        for clarification in result["clarifications"]:
            print("      -", clarification)

    print()


# =========================================================
# AUTOMATED EXPECTATION
# =========================================================

assert (results[0]["module_id"] == "USE_8852")
assert (results[0]["status"] == "COMPATIBLE")

print("PRIMARY RECOMMENDATION TEST PASSED")

print()
print()
print("TEST 2 - SECURE BLE + CAN")
print("=========================")

requirement = (create_empty_requirement())
requirement["application"]["name"] = "Wireless Battery Management System"
requirement["connectivity"]["ble_required"] = True
requirement["interfaces"]["can_required"] = True
requirement["embedded_features"]["integrated_mcu_required"] = True

results = evaluate_portfolio(requirement, modules)


for result in results:
    print(result["module_name"],"->", result["status"])

assert (results[0]["module_id"] == "USE_45")
assert (results[0]["status"] == "COMPATIBLE")

print()
print("BLE + CAN RECOMMENDATION TEST PASSED")