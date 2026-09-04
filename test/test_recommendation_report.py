

import json
import sys

from pathlib import Path
BASE_DIR = (Path(__file__).resolve().parent.parent)
sys.path.insert(0, str(BASE_DIR))

from core.customer_requirement import (create_empty_requirement)
from core.selection_engine import (evaluate_portfolio)
from core.recommendation_report import (
    build_recommendation_report,
    print_recommendation_report
)

# =========================================================
# LOAD PORTFOLIO
# =========================================================

with open(BASE_DIR/ "data"/ "modules.json", "r", encoding="utf-8") as file:
    database = json.load(file)

modules = database["modules"]

# =========================================================
# CUSTOMER SCENARIO
# =========================================================

requirement = (create_empty_requirement())
requirement["application"]["name"] = "Smart HMI Controller"
requirement["connectivity"]["wifi_required"] = True
requirement["connectivity"]["ble_required"] = True
requirement["wifi"]["band_5ghz_required"] = True
requirement["embedded_features"]["integrated_mcu_required"] = True
requirement["embedded_features"]["adc_required"] = True
requirement["embedded_features"]["capacitive_touch_required"] = True
requirement["environment"]["minimum_temperature_c"] = -40
requirement["environment"]["maximum_temperature_c"] = 85


# =========================================================
# RUN ENGINE
# =========================================================

results = evaluate_portfolio(requirement, modules)

# =========================================================
# BUILD SALES REPORT
# =========================================================

report = build_recommendation_report(requirement,results, modules)

# =========================================================
# VALIDATE
# =========================================================

assert (report["decision"] == "RECOMMEND")
assert (report["primary"]["module_id"] == "USE_8721")

# =========================================================
# DISPLAY
# =========================================================

print_recommendation_report(report)
print()
print("RECOMMENDATION REPORT TEST PASSED")

print()
print()
print("TEST 2 - CUSTOMER INFORMATION INCOMPLETE")
print("=" * 72)

requirement = (create_empty_requirement())
requirement["application"]["name"] = "Wi-Fi 6 Gateway"
requirement["connectivity"]["wifi_required"] = True
requirement["connectivity"]["ble_required"] = True
requirement["connectivity"]["bluetooth_classic_required"] = True
requirement["wifi"]["wifi6_required"] = True

# PCIe and USB deliberately remain None.
results = evaluate_portfolio(requirement, modules)
report = build_recommendation_report(requirement,results, modules)
print_recommendation_report(report)

