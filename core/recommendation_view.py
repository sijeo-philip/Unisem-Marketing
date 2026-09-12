

from core.recommendation_bridge import (recommend_from_answers)
from core.recommendation_explanation import (explain_shortlist)
from core.module_comparison import (build_module_comparison)

def build_recommendation_view(answers, modules, max_alternatives=2):
    """
    Build all information required by the
    browser recommendation page.

    The browser/template must not perform
    scoring or eligibility calculations.
    """
    shortlist = recommend_from_answers(answers, modules)
    explanation = explain_shortlist(shortlist, max_alternatives=max_alternatives)
    comparison = build_module_comparison(answers, modules, max_candidates=(max_alternatives + 1))
    return {
        "shortlist": shortlist,
        "explanation": explanation,
        "comparison": comparison,
        "has_recommendation": (explanation.recommended is not None),
    }
    
    
def build_browser_recommendation_view(recommendation_result):
    """
    Convert the authoritative Lesson 1/2 selection result
    into a stable browser-facing Lesson 3 view.

    IMPORTANT:
    This function performs NO module selection,
    NO scoring and NO engineering eligibility decisions.
    """

    if not isinstance(recommendation_result, dict):
        raise ValueError("Recommendation result must be a dictionary")

    sales_view = (recommendation_result.get("sales_view") or {})

    top_candidate = (recommendation_result.get("top_candidate") or {})

    decision = (recommendation_result.get("decision"))

    return {
        "decision": decision,
        "has_recommendation": decision == "recommended",
        "outcome": sales_view.get("outcome") or {},
        "module": sales_view.get("module"),
        "strengths": list(sales_view.get("why_this_module") or []),
        "clarifications": list(sales_view.get("clarifications") or []),
        "conflicts": list(sales_view.get("conflicts") or []),
        "preference_matches": list(top_candidate.get("preference_matches") or []),
        "tradeoffs": list(top_candidate.get("preference_tradeoffs") or []),
        "next_action": sales_view.get("next_action") or "",
        "alternatives": list(sales_view.get("alternatives") or []),
    }