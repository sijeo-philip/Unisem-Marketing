

import subprocess
import sys

from pathlib import Path

BASE_DIR = (Path(__file__).resolve().parent.parent)

TESTS = [
    "test_database.py",
    "test_requirement.py",
    "test_question_tree.py",
    "test_selection_engine.py",
    "test_portfolio_selection.py",
    "test_full_portfolio_matrix.py",
    "test_recommendation_report.py",
    "test_question_engine.py"
]

print()
print("=" * 72)
print("UNISEM MARKETING TOOL - FULL REGRESSION TEST")
print("=" * 72)

for test in TESTS:
    print()
    print("Running:", test)
    print("-" * 72)
    test_path = (BASE_DIR/ "test"/ test)

    result = subprocess.run([sys.executable, str(test_path)], cwd=BASE_DIR)

    if result.returncode != 0:
        print()
        print("TEST SUITE FAILED:")
        print(test)
        sys.exit(result.returncode)
print()
print("=" * 72)
print("ALL UNISEM REGRESSION TESTS PASSED")
print("=" * 72)