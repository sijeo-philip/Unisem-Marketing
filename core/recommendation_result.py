
from dataclasses import dataclass, field
from typing import List


@dataclass
class RecommendationResult:
    module_id: str
    score: float

    reasons: List[str] = field(default_factory=list)

    considerations: List[str] = field(
        default_factory=list
    )

    rank: int = 0

    eligible: bool = True

    rejection_reasons: List[str] = field(
        default_factory=list
    )

    @property
    def match_percent(self) -> int:
        value = round(self.score)

        if value < 0:
            return 0

        if value > 100:
            return 100

        return value

    @property
    def status(self) -> str:
        if self.eligible:
            return "ELIGIBLE"

        return "INELIGIBLE"

    @property
    def match_strength(self) -> str:
        if not self.eligible:
            return "Rejected"

        if self.score >= 90:
            return "Excellent"

        if self.score >= 75:
            return "Strong"

        if self.score >= 60:
            return "Moderate"

        return "Weak"


@dataclass
class RecommendationShortlist:
    results: List[RecommendationResult] = field(
        default_factory=list
    )

    @property
    def best(self):
        """
        Kept for backward compatibility with Lesson 3A/3B.
        """
        if not self.results:
            return None

        return self.results[0]

    @property
    def eligible_results(self):
        return [
            item
            for item in self.results
            if item.eligible
        ]

    @property
    def ineligible_results(self):
        return [
            item
            for item in self.results
            if not item.eligible
        ]

    @property
    def best_eligible(self):
        eligible = self.eligible_results

        if not eligible:
            return None

        return eligible[0]

    def top(self, count: int = 3):
        """
        Kept for compatibility with Lesson 3A.
        """
        return self.results[:count]

    def top_eligible(self, count: int = 3):
        return self.eligible_results[:count]

    def sort_by_score(self):
        """
        Eligible modules always appear before
        ineligible modules.

        Within each group, highest score wins.
        """

        self.results.sort(
            key=lambda item: (
                item.eligible,
                item.score,
            ),
            reverse=True,
        )

        eligible_rank = 1

        for item in self.results:

            if item.eligible:
                item.rank = eligible_rank
                eligible_rank += 1

            else:
                item.rank = 0