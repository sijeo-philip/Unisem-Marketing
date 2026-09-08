
from dataclasses import dataclass, field
from typing import List, Optional

from core.recommendation_result import (
    RecommendationResult,
    RecommendationShortlist,
)


@dataclass
class CandidateExplanation:
    module_id: str

    status: str
    rank: int

    match_percent: int
    match_strength: str

    headline: str
    summary: str

    strengths: List[str] = field(default_factory=list)
    tradeoffs: List[str] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)


@dataclass
class ShortlistExplanation:
    summary: str

    recommended: Optional[CandidateExplanation] = None
    alternatives: List[CandidateExplanation] = field(default_factory=list)
    rejected: List[CandidateExplanation] = field(default_factory=list)


def explain_candidate(result: RecommendationResult, recommended: bool = False) -> CandidateExplanation:

    if not result.eligible:
        headline = (f"{result.module_id} is not eligible")
        summary = (
            "This module does not satisfy all "
            "mandatory customer requirements."
        )
    elif recommended:
        headline = (f"{result.module_id} is the recommended module")
        summary = (
            f"This is the highest-ranked eligible "
            f"match at {result.match_percent}% "
            f"with a "
            f"{result.match_strength.lower()} fit."
        )
    else:
        headline = (f"{result.module_id} is an eligible alternative")
        summary = (
            f"This module remains technically "
            f"eligible and is ranked "
            f"#{result.rank} with a "
            f"{result.match_percent}% match."
        )
    return CandidateExplanation(module_id=result.module_id,
        status=result.status,
        rank=result.rank,
        match_percent=result.match_percent,
        match_strength=result.match_strength,
        headline=headline,
        summary=summary,
        strengths=list(result.reasons),
        tradeoffs=list(result.considerations),
        blockers=list(result.rejection_reasons),
    )


def explain_shortlist(shortlist: RecommendationShortlist, max_alternatives: int = 2) -> ShortlistExplanation:
    best = shortlist.best_eligible
    if best is None:
        rejected = [explain_candidate(item) for item in shortlist.ineligible_results]
        return ShortlistExplanation(
            summary=(
                "No module currently satisfies "
                "all mandatory customer "
                "requirements."
            ),
            recommended=None,
            alternatives=[],
            rejected=rejected,
        )

    recommended = explain_candidate(best, recommended=True)
    alternative_results = [item for item in shortlist.eligible_results if item is not best]
    alternatives = [explain_candidate(item) for item in alternative_results[:max_alternatives]]
    rejected = [explain_candidate(item) for item in shortlist.ineligible_results]
    summary = (
        f"{best.module_id} is the best eligible "
        f"match at {best.match_percent}%. "
        f"{len(alternatives)} eligible "
        f"alternative(s) are available."
    )
    return ShortlistExplanation(
        summary=summary,
        recommended=recommended,
        alternatives=alternatives,
        rejected=rejected,
    )


def render_shortlist_text(explanation: ShortlistExplanation) -> str:
    lines = []
    lines.append(explanation.summary)
    if explanation.recommended:
        item = explanation.recommended
        lines.append("")
        lines.append(f"RECOMMENDED: {item.module_id}")
        lines.append(f"Match: {item.match_percent}%({item.match_strength})")
        if item.strengths:
            lines.append("")
            lines.append("Why it fits:")
            for reason in item.strengths:
                lines.append(f"  + {reason}")
        if item.tradeoffs:
            lines.append("")
            lines.append("Considerations:")
            for tradeoff in item.tradeoffs:
                lines.append(f"  - {tradeoff}")
    if explanation.alternatives:
        lines.append("")
        lines.append("ALTERNATIVES:")
        for item in explanation.alternatives:
            lines.append(f"  #{item.rank} "
                f"{item.module_id} "
                f"- {item.match_percent}%"
            )

            for tradeoff in item.tradeoffs:
                lines.append(f"     - {tradeoff}")
    if explanation.rejected:
        lines.append("")
        lines.append("NOT ELIGIBLE:")
        for item in explanation.rejected:
            lines.append(f"  {item.module_id}")
            for blocker in item.blockers:
                lines.append(f"     ! {blocker}" )
    return "\n".join(lines)