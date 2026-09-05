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


def choose_test_answer(
    question
):
    """
    Pick one valid answer from the question returned
    by the browser API.

    This lets the test exercise a complete path without
    hard-coding product-specific question IDs.
    """

    options = question.get(
        "options",
        []
    )


    assert options, (
        "Question has no options: "
        + str(question)
    )


    first_value = (
        options[0]["value"]
    )


    question_type = str(
        question.get(
            "type",
            ""
        )
    ).lower()


    if (
        "multiple"
        in question_type
        or
        "multi_select"
        in question_type
    ):

        return [
            first_value
        ]


    return first_value


def run_tests():

    print()
    print(
        "Testing Lesson 2C Wizard Integration"
    )
    print(
        "------------------------------------"
    )


    client = app.test_client()


    # ====================================================
    # TEST 1
    # Empty answer list must return the first question.
    # ====================================================

    response = client.post(
        "/api/wizard",
        json={
            "answers": []
        },
    )


    assert (
        response.status_code
        == 200
    ), response.get_data(
        as_text=True
    )


    data = response.get_json()


    assert (
        data["status"]
        == "ok"
    )


    assert (
        data["state"]
        == "question"
    )


    assert (
        data["question"]
        is not None
    )


    print(
        "PASS - Wizard starts through QuestionSession"
    )


    # ====================================================
    # TEST 2
    # Follow one complete valid path.
    # ====================================================

    answers = []


    for step in range(50):

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

            break


        assert (
            data["state"]
            == "question"
        )


        answer = (
            choose_test_answer(
                data["question"]
            )
        )


        answers.append(
            answer
        )


    else:

        raise AssertionError(
            "Wizard did not complete within "
            "50 steps. Possible question-tree loop."
        )


    print(
        "PASS - Complete question path executed"
    )


    # ====================================================
    # TEST 3
    # Requirement must have been generated.
    # ====================================================

    assert (
        "requirement"
        in data
    )


    assert (
        isinstance(
            data["requirement"],
            dict,
        )
    )


    print(
        "PASS - Customer requirement generated"
    )


    # ====================================================
    # TEST 4
    # Selection engine must have executed.
    # ====================================================

    ranked_results = (
        data.get(
            "ranked_results"
        )
    )


    assert isinstance(
        ranked_results,
        list,
    )


    assert (
        len(ranked_results)
        > 0
    )


    print(
        "PASS - Portfolio evaluation executed"
    )


    # ====================================================
    # TEST 5
    # Decision must be valid.
    # ====================================================

    valid_decisions = {
        "recommended",
        "clarification_required",
        "no_suitable_module",
    }


    assert (
        data.get("decision")
        in valid_decisions
    )


    print(
        "PASS - Recommendation decision generated:",
        data["decision"]
    )


    # ====================================================
    # TEST 6
    # Every result must contain basic engine information.
    # ====================================================

    for result in ranked_results:

        assert (
            result.get(
                "module_id"
            )
        )

        assert (
            result.get(
                "status"
            )
        )


    print(
        "PASS - Ranked module results valid"
    )


    # ====================================================
    # TEST 7
    # Invalid answers must be rejected by Lesson 1.
    # ====================================================

    response = client.post(
        "/api/wizard",
        json={
            "answers": [
                "__definitely_not_a_valid_option__"
            ]
        },
    )


    assert (
        response.status_code
        == 400
    )


    print(
        "PASS - Invalid browser answer rejected"
    )


    print()
    print(
        "ALL LESSON 2C TESTS PASSED"
    )
    print()


if __name__ == "__main__":

    run_tests()