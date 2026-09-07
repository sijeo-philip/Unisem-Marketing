

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


def choose_answer(
    question,
):
    """
    Choose one valid answer so we can complete one
    deterministic questionnaire path.
    """

    options = question.get(
        "options",
        []
    )


    assert options


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


def complete_wizard(
    client,
):
    """
    Complete one valid wizard path and return both
    browser answers and final engine response.
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


        if (
            data["state"]
            == "complete"
        ):

            return (
                answers,
                data,
            )


        answers.append(
            choose_answer(
                data["question"]
            )
        )


    raise AssertionError(
        "Wizard did not complete"
    )


def result_module_id(
    result,
):

    return (
        result.get(
            "module_id"
        )
        or
        result.get(
            "id"
        )
        or
        result.get(
            "part_number"
        )
        or
        result.get(
            "part_no"
        )
    )


def run_tests():

    print()

    print(
        "Testing Lesson 2E Module Comparison"
    )

    print(
        "-----------------------------------"
    )


    client = app.test_client()


    answers, wizard_data = (
        complete_wizard(
            client
        )
    )


    ranked_results = (
        wizard_data[
            "ranked_results"
        ]
    )


    assert ranked_results


    print(
        "PASS - Completed customer evaluation"
    )


    # ====================================================
    # Select up to first three evaluated modules.
    # ====================================================

    module_ids = []


    for result in ranked_results[:3]:

        module_id = (
            result_module_id(
                result
            )
        )


        assert module_id


        module_ids.append(
            str(
                module_id
            )
        )


    # ====================================================
    # TEST 1
    # Comparison API responds.
    # ====================================================

    response = client.post(
        "/api/compare",

        json={
            "answers":
                answers,

            "module_ids":
                module_ids,
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


    print(
        "PASS - Comparison API responded"
    )


    # ====================================================
    # TEST 2
    # Correct number of modules returned.
    # ====================================================

    comparison = (
        data["comparison"]
    )


    compared_modules = (
        comparison[
            "modules"
        ]
    )


    assert (
        len(
            compared_modules
        )
        ==
        len(
            module_ids
        )
    )


    print(
        "PASS - Requested modules returned"
    )


    # ====================================================
    # TEST 3
    # Module IDs are preserved.
    # ====================================================

    returned_ids = [
        module[
            "module_id"
        ]
        for module
        in compared_modules
    ]


    assert (
        returned_ids
        ==
        module_ids
    )


    print(
        "PASS - Module identities preserved"
    )


    # ====================================================
    # TEST 4
    # Comparison rows exist.
    # ====================================================

    rows = (
        comparison[
            "rows"
        ]
    )


    assert isinstance(
        rows,
        list,
    )


    assert rows


    print(
        "PASS - Comparison rows generated"
    )


    # ====================================================
    # TEST 5
    # Customer-fit row must exist.
    # ====================================================

    fit_rows = [
        row
        for row in rows
        if row.get(
            "key"
        )
        == "fit_status"
    ]


    assert (
        len(
            fit_rows
        )
        == 1
    )


    print(
        "PASS - Engine fit row generated"
    )


    # ====================================================
    # TEST 6
    # Comparison fit status must match engine status.
    # ====================================================

    fit_values = (
        fit_rows[0][
            "values"
        ]
    )


    result_by_id = {
        str(
            result_module_id(
                result
            )
        ):
        result

        for result
        in ranked_results
    }


    for module_id in module_ids:

        assert (
            fit_values[
                module_id
            ]
            ==
            result_by_id[
                module_id
            ]["status"]
        )


    print(
        "PASS - Comparison status matches engine"
    )


    # ====================================================
    # TEST 7
    # Unknown module must be rejected.
    # ====================================================

    response = client.post(
        "/api/compare",

        json={
            "answers":
                answers,

            "module_ids": [
                "__UNKNOWN_MODULE__"
            ],
        },
    )


    assert (
        response.status_code
        == 400
    )


    print(
        "PASS - Unknown module rejected"
    )


    # ====================================================
    # TEST 8
    # Incomplete requirement must be rejected.
    # ====================================================

    response = client.post(
        "/api/compare",

        json={
            "answers":
                [],

            "module_ids":
                module_ids,
        },
    )


    assert (
        response.status_code
        == 400
    )


    print(
        "PASS - Incomplete questionnaire rejected"
    )


    # ====================================================
    # TEST 9
    # Empty module selection must be rejected.
    # ====================================================

    response = client.post(
        "/api/compare",

        json={
            "answers":
                answers,

            "module_ids":
                [],
        },
    )


    assert (
        response.status_code
        == 400
    )


    print(
        "PASS - Empty comparison rejected"
    )


    print()

    print(
        "ALL LESSON 2E TESTS PASSED"
    )

    print()


if __name__ == "__main__":

    run_tests()