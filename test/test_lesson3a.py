
import sys
from pathlib import Path

BASE_DIR = (Path(__file__).resolve().parent.parent)
sys.path.insert(0, str(BASE_DIR))

from core.recommendation_result import (
    RecommendationResult,
    RecommendationShortlist,
)


r1 = RecommendationResult(
    module_id="USE_8851",
    score=82.4,
    reasons=[
        "Supports Wi-Fi 6",
        "Supports Bluetooth",
    ],
)

r2 = RecommendationResult(
    module_id="USE_8852",
    score=94.2,
    reasons=[
        "Supports Wi-Fi 6",
        "Supports Bluetooth Classic",
        "Supports BLE",
        "Supports high-performance 2x2 Wi-Fi",
    ],
    considerations=[
        "Larger module than USE_8851",
    ],
)

r3 = RecommendationResult(
    module_id="USE_8733",
    score=68.5,
    reasons=[
        "Supports dual-band Wi-Fi",
        "Supports Bluetooth",
    ],
)


shortlist = RecommendationShortlist(
    results=[
        r1,
        r2,
        r3,
    ]
)

shortlist.sort_by_score()


print("Recommendation shortlist")
print("------------------------")

for item in shortlist.results:
    print(
        f"{item.rank}. "
        f"{item.module_id} "
        f"{item.match_percent}%"
    )


print()
print("Best recommendation:")
print(shortlist.best.module_id)

print()
print("Why:")
for reason in shortlist.best.reasons:
    print(" +", reason)

print()
print("Considerations:")
for consideration in shortlist.best.considerations:
    print(" -", consideration)
    
    
empty = RecommendationShortlist()

assert empty.best is None
assert empty.top() == []

print()
print("Empty shortlist test: PASS")

too_high = RecommendationResult(
    module_id="TEST_HIGH",
    score=115
)

too_low = RecommendationResult(
    module_id="TEST_LOW",
    score=-10
)

assert too_high.match_percent == 100
assert too_low.match_percent == 0

print("Score boundary test: PASS")

assert shortlist.best.module_id == "USE_8852"

assert shortlist.results[0].rank == 1
assert shortlist.results[1].rank == 2
assert shortlist.results[2].rank == 3

assert shortlist.results[0].module_id == "USE_8852"
assert shortlist.results[1].module_id == "USE_8851"
assert shortlist.results[2].module_id == "USE_8733"

assert shortlist.results[0].match_percent == 94
assert shortlist.results[1].match_percent == 82
assert shortlist.results[2].match_percent == 68

print()
print("LESSON 3A: ALL TESTS PASS")