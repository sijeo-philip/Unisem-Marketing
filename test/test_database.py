import json
from pathlib import Path


BASE_DIR = (Path(__file__).resolve().parent.parent)


MODULE_FILE = (BASE_DIR/ "data"/ "modules.json")


with open( MODULE_FILE,"r",encoding="utf-8") as file:
    database = json.load(file)


modules = database["modules"]


print()
print("UNISEM MODULE DATABASE")
print("======================")
print()

print("Portfolio version:", database["portfolio_version"])
print("Number of modules:", len(modules))

print()


# ---------------------------------------------------------
# Verify expected product count
# ---------------------------------------------------------

assert len(modules) == 11


# ---------------------------------------------------------
# Verify IDs are unique
# ---------------------------------------------------------

module_ids = [module["id"] for module in modules]


assert len(module_ids) == len(set(module_ids))


# ---------------------------------------------------------
# Verify mandatory fields
# ---------------------------------------------------------

for module in modules:

    assert "id" in module
    assert "name" in module
    assert "family" in module

    assert "connectivity" in module
    assert "wifi" in module
    assert "bluetooth" in module
    assert "architecture" in module

    print(module["id"],"->",module["family"])


print()
print("DATABASE VALIDATION PASSED")