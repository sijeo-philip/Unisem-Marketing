import json
from pathlib import Path
import sys

BASE_DIR = ( Path(__file__).resolve().parent.parent )

sys.path.insert(0, str(BASE_DIR))

from core.customer_requirement import create_empty_requirement
from core.selection_engine import evaluate_module

# ===================================
# LOAD MODULE DATABASE
# ===================================

MODULE_FILE = ( BASE_DIR/"data"/"modules.json" )

with open( MODULE_FILE, "r", encoding="utf-8") as file:
    database = json.load(file)
    
module = database["modules"][0]

# =========================================================
# CREATE CUSTOMER REQUIREMENT
# =========================================================

requirement = (
    create_empty_requirement()
)


requirement["application"]["name"] = "Automotive Infotainment"
requirement["connectivity"]["wifi_required"] = True
requirement["connectivity"]["ble_required"] = True
requirement["connectivity"]["bluetooth_classic_required"] = True
requirement["wifi"]["band_5ghz_required"] = True
requirement["wifi"]["wifi6_required"] = True
requirement["wifi"]["mimo_2x2_required"] = True
requirement["interfaces"]["pcie_available"] = True
requirement["interfaces"]["usb_available"] = True
requirement["preferences"]["high_performance"] = True
requirement["environment"]["minimum_temperature_c"] = 0
requirement["environment"]["maximum_temperature_c"] = 70


# =========================================================
# EVALUATE MODULE
# =========================================================

result = evaluate_module(requirement, module)


# =========================================================
# PRINT RESULT
# =========================================================

print()
print("MODULE EVALUATION")
print("=================")
print()

print("Module:", result["module_name"])
print("Status:", result["status"])

print("Preference score:", result["preference_score"])
print()
print("PASSED REQUIREMENTS")

print("-------------------")

for item in result["passed_requirements"]:

    print("PASS:",item)

print()
print("HARD FAILURES")

print("-------------")

if not result["hard_failures"]:

    print("None")

else:

    for item in result["hard_failures"]:

        print("FAIL:", item)


print()
print("CLARIFICATIONS")

print("--------------")
if not result["clarifications"]:
    print("None")
else:
    for item in result["clarifications"]:
        print("CHECK:",item)
print()
print("PREFERENCE NOTES")
print("----------------")

for item in result["preference_notes"]:
    print(item)
    
    
print()
print()
print("TEST 2 - TEMPERATURE FAILURE")
print("=============================")

requirement["environment"]["maximum_temperature_c"] = 85

result = evaluate_module(requirement, module)
print("Module:", result["module_name"])
print("Status:", result["status"])
for failure in result["hard_failures"]:
    print("FAIL:",failure)
    
    
    
print()
print()
print("TEST 3 - MISSING HOST INFORMATION")
print("=================================")

requirement = (create_empty_requirement())

requirement["connectivity"]["wifi_required"] = True
requirement["connectivity"]["ble_required"] = True
requirement["connectivity"]["bluetooth_classic_required"] = True

requirement["wifi"]["wifi6_required"] = True
requirement["wifi"]["mimo_2x2_required"] = True

# IMPORTANT:
#
# We deliberately DO NOT set:
#
# pcie_available
# usb_available
#
# They therefore remain None.
requirement["interfaces"]["pcie_available"] = False
requirement["interfaces"]["usb_available"] = True

result = evaluate_module( requirement, module)

print("Module:",result["module_name"])
print("Status:",result["status"])


for item in result["clarifications"]:

    print("CHECK:",item)
    
    
