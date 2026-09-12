

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
    
    
    