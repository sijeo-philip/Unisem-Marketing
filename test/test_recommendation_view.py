import sys
from pathlib import Path


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)


sys.path.insert(
    0,
    str(PROJECT_ROOT)
)


from app import app


def select_valid_answer(
    question,
):
    """
    Select one valid option so the test can traverse one
    complete deterministic questionnaire path.
    """

    options = question.get(
        "options",
        []
    )


    assert options, (
        "Question has no options: "
        + str(question)
    )


    value = (
        options[0]["value"]
    )


    question_type = (
        str(
            question.get(
                "type",
                ""
            )
        )
        .lower()
    )


    if (
        "multiple"
        in question_type
        or
        "multi_select"
        in question_type
    ):

        return [
            value
        ]


    return value


def complete_one_path(
    client,
):
    """
    Follow one valid questionnaire path until the engine
    returns a completed evaluation.
    """

    answers = []


    for _ in range(50):

        response = client.post(
            "/api/wizard",

            json={
                "answers":
                    answers
            },
        )


        assert (
            response.status_code
            == 200
        ), response.get_data(
            as_text=True
        )


        data = (
            response.get_json()
        )


        assert (
            data["status"]
            == "ok"
        )


        if (
            data["state"]
            == "complete"
        ):

            return data


        assert (
            data["state"]
            == "question"
        )


        answers.append(
            select_valid_answer(
                data["question"]
            )
        )


    raise AssertionError(
        "Wizard did not complete within 50 steps"
    )


def run_tests():

    print()

    print(
        "Testing Lesson 2D Recommendation Experience"
    )

    print(
        "-------------------------------------------"
    )


    client = app.test_client()


    data = complete_one_path(
        client
    )


    # ====================================================
    # TEST 1
    # Existing selection result still exists.
    # ====================================================

    assert (
        "ranked_results"
        in data
    )


    assert isinstance(
        data["ranked_results"],
        list,
    )


    print(
        "PASS - Selection engine result preserved"
    )


    # ====================================================
    # TEST 2
    # Sales view generated.
    # ====================================================

    sales_view = (
        data.get(
            "sales_view"
        )
    )


    assert isinstance(
        sales_view,
        dict,
    )


    print(
        "PASS - Sales presentation generated"
    )


    # ====================================================
    # TEST 3
    # Presentation decision must match engine decision.
    # ====================================================

    outcome = (
        sales_view.get(
            "outcome"
        )
    )


    assert isinstance(
        outcome,
        dict,
    )


    assert (
        outcome.get("code")
        == data.get("decision")
    )


    print(
        "PASS - Presentation decision matches engine"
    )


    # ====================================================
    # TEST 4
    # Outcome contains salesperson-facing language.
    # ====================================================

    assert (
        outcome.get("label")
    )


    assert (
        outcome.get("headline")
    )


    assert (
        outcome.get("summary")
    )


    print(
        "PASS - Sales outcome wording available"
    )


    # ====================================================
    # TEST 5
    # If an engine candidate exists, the sales card must
    # represent the same module.
    # ====================================================

    top_candidate = (
        data.get(
            "top_candidate"
        )
    )


    sales_module = (
        sales_view.get(
            "module"
        )
    )


    if top_candidate:

        assert isinstance(
            sales_module,
            dict,
        )


        engine_module_id = (
            top_candidate.get(
                "module_id"
            )
            or
            top_candidate.get(
                "id"
            )
            or
            top_candidate.get(
                "part_number"
            )
        )


        assert (
            str(
                sales_module.get(
                    "module_id"
                )
            )
            ==
            str(
                engine_module_id
            )
        )


    print(
        "PASS - Sales card uses engine-selected module"
    )


    # ====================================================
    # TEST 6
    # Presentation lists must be safe lists.
    # ====================================================

    for field in (
        "why_this_module",
        "clarifications",
        "conflicts",
        "preference_notes",
        "alternatives",
    ):

        assert isinstance(
            sales_view.get(
                field
            ),
            list,
        )


    print(
        "PASS - Recommendation sections normalized"
    )


    # ====================================================
    # TEST 7
    # Next action is always available.
    # ====================================================

    assert (
        sales_view.get(
            "next_action"
        )
    )


    print(
        "PASS - Sales next action generated"
    )


    print()

    print(
        "ALL LESSON 2D TESTS PASSED"
    )

    print()


if __name__ == "__main__":

    run_tests()