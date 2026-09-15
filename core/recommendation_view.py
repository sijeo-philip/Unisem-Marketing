

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
    
VALID_BROWSER_DECISIONS = {
    "recommended",
    "clarification_required",
    "no_suitable_module",
}


DEFAULT_OUTCOMES = {

    "recommended": {
        "code": "recommended",
        "label": "Recommended",
        "headline": "Best fit for the captured customer requirement",
        "summary": (
            "A compatible module was identified "
            "for the captured requirement."
        ),
    },

    "clarification_required": {
        "code": "clarification_required",
        "label": "Needs Clarification",
        "headline": (
            "A potential module exists, but "
            "additional information is required"
        ),
        "summary": (
            "Resolve the highlighted clarification "
            "items before confirming the module."
        ),
    },

    "no_suitable_module": {
        "code": "no_suitable_module",
        "label": "No Suitable Module",
        "headline": (
            "No current module fully satisfies "
            "the captured requirement"
        ),
        "summary": (
            "Review the requirement or escalate "
            "the opportunity for technical review."
        ),
    },
}

def _safe_text_list(value):
    """
    Convert optional browser-facing text into
    a clean list of strings.

    Important:
    A string must become one list item, not a
    list of individual characters.
    """

    if value is None:
        return []

    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        return [text]
    if isinstance(value, (list, tuple, set)):
        result = []
        for item in value:
            if item is None:
                continue
            text = str(item).strip()
            if not text:
                continue
            result.append(text)
        return result
    text = str(value).strip()
    if not text:
        return []
    return [text]

def _safe_outcome(value, decision):
    fallback = (DEFAULT_OUTCOMES[decision])
    if not isinstance(value, dict):
        return dict(fallback)
    return {
        "code": str(value.get("code") or fallback["code"]),
        "label": str(value.get("label") or fallback["label"]),
        "headline": str(value.get("headline") or fallback["headline"]),
        "summary": str(value.get("summary") or fallback["summary"]),
    }


def _safe_module(value):
    if not isinstance(value, dict):
        return None
    module_id = str(value.get("module_id") or "").strip()
    if not module_id:
        return None
    return {
        "role": str(value.get("role") or ""),
        "module_id": module_id,
        "module_name": str(value.get("module_name") or ""),
        "description": str(value.get("description") or ""),
        "choose_when": str(value.get("choose_when") or ""),
        "capabilities": _safe_text_list(value.get("capabilities")),
    }
    
    
def _safe_alternatives(value):
    if not isinstance(value, (list, tuple)):
        return []
    result = []
    seen = set()
    for item in value:
        if not isinstance(item, dict):
            continue
        module_id = str(item.get("module_id") or "").strip()
        if not module_id:
            continue
        normalized_id = (module_id.lower())
        if normalized_id in seen:
            continue
        seen.add(normalized_id)
        result.append({
                "module_id": module_id,
                "module_name": str(item.get("module_name") or "" ),
                "status": str(item.get("status") or ""),
                "choose_when": str(item.get("choose_when") or ""),
            }
        )
        if len(result) >= 3:
            break
    return result    
    
    
    
def build_browser_recommendation_view(
    recommendation_result
):
    """
    Convert the authoritative selection result into
    the stable Lesson 3 browser representation.

    This function performs no engineering selection.
    """

    if not isinstance(recommendation_result, dict):
        raise ValueError("Recommendation result must be a dictionary")

    decision = (recommendation_result.get("decision"))
    if (decision not in VALID_BROWSER_DECISIONS):
        raise ValueError("Unknown recommendation decision: " + str(decision))
    sales_view = (recommendation_result.get("sales_view"))
    if not isinstance(sales_view, dict):
        sales_view = {}
    top_candidate = (recommendation_result.get("top_candidate"))
    if not isinstance(top_candidate, dict):
        top_candidate = {}
    next_action = (sales_view.get("next_action"))
    if next_action is None:
        next_action = ""
    else:
        next_action = str(next_action).strip()
    return {
        "decision": decision,
        "has_recommendation": decision == "recommended",
        "outcome": _safe_outcome(sales_view.get("outcome"), decision),
        "module": _safe_module(sales_view.get("module")),
        "strengths": _safe_text_list(sales_view.get("why_this_module")),
        "clarifications": _safe_text_list(sales_view.get("clarifications")),
        "conflicts": _safe_text_list(sales_view.get("conflicts")),
        "preference_matches": _safe_text_list(top_candidate.get("preference_matches")),
        "tradeoffs": _safe_text_list(top_candidate.get("preference_tradeoffs")),
        "next_action": next_action,
        "alternatives": _safe_alternatives(sales_view.get("alternatives")),
    }
    
    
    
    
    
    
    