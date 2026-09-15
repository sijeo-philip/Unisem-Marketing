import sys
from pathlib import Path

BASE_DIR = (Path(__file__).resolve().parent.parent)
sys.path.insert(0, str(BASE_DIR))

from app import (app, validate_module_records)

from core.recommendation_view import (build_browser_recommendation_view)

def choose_test_answer(question):
    options = (question.get("options", []))
    assert options
    value = (options[0]["value"])
    question_type = str(question.get("type", "")).lower()
    if ("multiple" in question_type or "multi_select" in question_type):
        return [value]
    return value

def run_tests():

    print()
    print("Testing Lesson 3G Recommendation Hardening")
    print("------------------------------------------")

    # ====================================================
    # TEST 1
    # Strings must remain complete list entries.
    # ====================================================
    synthetic_result = {
        "decision": "recommended",
        "sales_view": {
            "outcome": {
                "code": "recommended",
                "label":"Recommended",
                "headline": "Test recommendation",
                "summary": "Test summary",
            },
            "module": {
                "role": "Recommended Module",
                "module_id": "USE_TEST",
                "module_name": "Test Module",
                "capabilities": "Wi-Fi",
            },
            "why_this_module": "Wi-Fi capability is supported.",
            "clarifications": None,
            "conflicts": [],
            "next_action": None,
            "alternatives": [ None,
                {
                    "module_id": ""
                },
                {
                    "module_id": "USE_ALT",
                    "module_name": "Alternative",
                    "status": "COMPATIBLE",
                },
                {
                    "module_id": "USE_ALT",
                    "module_name": "Duplicate",
                },
            ],
        },

        "top_candidate": {
            "preference_matches": "High-performance preference matches.",
            "preference_tradeoffs": "Larger module footprint.",
        },
    }

    view = (build_browser_recommendation_view(synthetic_result))


    assert view["strengths"] == ["Wi-Fi capability is supported."]
    assert (view["module"]["capabilities"] == ["Wi-Fi"])
    assert (view["preference_matches"] == ["High-performance preference matches."])
    assert view["tradeoffs"] == ["Larger module footprint."]
    assert (len(view["alternatives"]) == 1)
    assert (view["alternatives"][0]["module_id"] == "USE_ALT")
    print("PASS - Browser view sanitizes malformed fields")


    # ====================================================
    # TEST 2
    # No-candidate result must still be browser-safe.
    # ====================================================

    no_match = (build_browser_recommendation_view({
                "decision": "no_suitable_module",
                "sales_view": {},
                "top_candidate": None,
            }
        )
    )

    assert (no_match["has_recommendation"] is False)
    assert (no_match["module"] is None)
    assert (no_match["strengths"] == [])
    assert (no_match["outcome"]["code"] == "no_suitable_module")
    print("PASS - No-match result remains displayable")
    


    # ====================================================
    # TEST 3
    # Portfolio must contain engine-required fields.
    # ====================================================

    try:
        validate_module_records(
            [
                {
                    "id": "BROKEN_MODULE",
                    "family": "wifi"
                }
            ]
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Missing module name was not rejected")
    print("PASS - Malformed portfolio record rejected")

    # ====================================================
    # TEST 4
    # Incomplete wizard must not contain Lesson 3 result.
    # ====================================================

    client = (app.test_client())
    response = client.post("/api/wizard",
        json={
            "answers": []
        },
    )

    assert (response.status_code == 200)
    data = (response.get_json())
    assert (data["state"] == "question")
    assert ("lesson3_view" not in data)
    print("PASS - Lesson 3 view only appears after completion")
    # ====================================================
    # TEST 5
    # Complete a real wizard path.
    # ====================================================

    answers = []
    for step in range(50):
        response = client.post("/api/wizard",
            json={
                "answers": answers
            },
        )

        assert (response.status_code == 200), response.get_data(as_text=True)
        data = (response.get_json())
        if (data["state"] == "complete"):
            break
        answer = (choose_test_answer(data["question"]))
        answers.append(answer)
    else:
        raise AssertionError("Wizard did not complete within 50 steps")
    assert ("lesson3_view" in data)
    lesson3_view = (data["lesson3_view"])
    assert isinstance(lesson3_view, dict)
    assert (lesson3_view["decision"] in {"recommended", "clarification_required", "no_suitable_module"})
    assert isinstance(lesson3_view["strengths"], list)
    assert isinstance(lesson3_view["clarifications" ], list)
    assert isinstance(lesson3_view["conflicts"], list)
    assert isinstance(lesson3_view["tradeoffs"], list)
    assert isinstance(lesson3_view["alternatives"], list)

    print("PASS - Completed wizard returns hardened Lesson 3 view")


    # ====================================================
    # TEST 6
    # Health API should report Lesson 3G.
    # ====================================================

    response = client.get("/api/health")
    data = (response.get_json())
    assert (data["lesson"] == "3G")
    print("PASS - Application milestone reports Lesson 3G")
    print()
    print("LESSON 3G: ALL TESTS PASS")
    print()

if __name__ == "__main__":

    run_tests()