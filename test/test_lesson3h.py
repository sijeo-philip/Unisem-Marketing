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
    str(PROJECT_ROOT),
)


from app import (
    app,
    build_recommendation_result,
)

from core.customer_requirement import (
    create_empty_requirement,
)


# ============================================================
# Helpers
# ============================================================

def choose_test_answer(
    question
):
    """
    Choose one valid answer from a live wizard question.

    This allows the acceptance test to follow the actual
    question tree without hard-coding question IDs.
    """

    options = question.get(
        "options",
        []
    )

    assert options, (
        "Question contains no options: "
        + str(question)
    )

    value = (
        options[0][
            "value"
        ]
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
            value
        ]

    return value


def complete_wizard(
    client
):
    """
    Follow one real valid browser path until the
    questionnaire completes.
    """

    answers = []

    first_question_id = None

    for step in range(
        50
    ):

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

            return (
                answers,
                data,
                first_question_id,
            )

        assert (
            data["state"]
            == "question"
        )

        question = (
            data["question"]
        )

        if (
            first_question_id
            is None
        ):

            first_question_id = (
                question.get(
                    "id"
                )
            )

        answers.append(
            choose_test_answer(
                question
            )
        )

    raise AssertionError(
        "Wizard did not complete "
        "within 50 questions"
    )


# ============================================================
# Tests
# ============================================================

def run_tests():

    print()
    print(
        "===================================================="
    )
    print(
        " UNISEM OFFLINE MARKETING TOOL"
    )
    print(
        " LESSON 3H - FINAL ACCEPTANCE"
    )
    print(
        "===================================================="
    )
    print()


    client = (
        app.test_client()
    )


    # ========================================================
    # TEST 1
    # Browser DOM contract.
    #
    # This specifically protects against the duplicate /
    # missing IDs we encountered during Lesson 3G.
    # ========================================================

    response = client.get(
        "/"
    )

    assert (
        response.status_code
        == 200
    )

    html = response.get_data(
        as_text=True
    )


    critical_ids = [

        "wizardComplete",

        "recommendationPanel",

        "decisionBadge",

        "recommendedModule",

        "recommendedModuleName",

        "chooseWhen",

        "comparisonLauncher",

        "comparisonChoices",

        "compareModulesButton",

        "comparisonPanel",

        "comparisonTable",

        "completionActions",

        "changeAnswersButton",

        "newCustomerButton",
    ]


    for element_id in critical_ids:

        marker = (
            'id="'
            + element_id
            + '"'
        )

        count = html.count(
            marker
        )

        assert (
            count
            == 1
        ), (
            "Expected exactly one "
            + marker
            + ", found "
            + str(count)
        )


    print(
        "PASS - Browser DOM contract valid"
    )


    # ========================================================
    # TEST 2
    # Complete a real browser wizard.
    # ========================================================

    (
        answers,
        completed,
        first_question_id,
    ) = complete_wizard(
        client
    )


    assert (
        len(answers)
        > 0
    )

    assert (
        completed["state"]
        == "complete"
    )


    print(
        "PASS - Real Sales Wizard completes"
    )


    # ========================================================
    # TEST 3
    # Lesson 3 browser model present.
    # ========================================================

    assert (
        "lesson3_view"
        in completed
    )

    lesson3_view = (
        completed[
            "lesson3_view"
        ]
    )

    assert isinstance(
        lesson3_view,
        dict,
    )

    assert (
        lesson3_view[
            "decision"
        ]
        ==
        completed[
            "decision"
        ]
    )


    print(
        "PASS - Lesson 3 presentation attached"
    )


    # ========================================================
    # TEST 4
    # Portfolio evaluation must contain module results.
    # ========================================================

    ranked_results = (
        completed.get(
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
        "PASS - Ranked portfolio results returned:",
        len(ranked_results),
        "modules",
    )


    # ========================================================
    # TEST 5
    # Every module result must have a unique ID.
    # ========================================================

    module_ids = []

    for result in ranked_results:

        assert isinstance(
            result,
            dict,
        )

        module_id = (
            result.get(
                "module_id"
            )
        )

        assert module_id

        module_ids.append(
            str(module_id)
        )


    assert (
        len(module_ids)
        ==
        len(set(module_ids))
    )


    print(
        "PASS - Ranked module IDs are unique"
    )


    # ========================================================
    # TEST 6
    # Every ranked result must have a valid engine status.
    # ========================================================

    valid_statuses = {

        "COMPATIBLE",

        "NEEDS_CLARIFICATION",

        "NOT_SUITABLE",
    }


    for result in ranked_results:

        assert (
            result.get(
                "status"
            )
            in valid_statuses
        )


    print(
        "PASS - All module evaluation states valid"
    )


    # ========================================================
    # TEST 7
    # Comparison selector has enough backend data.
    #
    # This protects against the empty selector problem
    # discovered immediately before Lesson 3G completion.
    # ========================================================

    comparable_ids = [

        result[
            "module_id"
        ]

        for result
        in ranked_results

        if result.get(
            "module_id"
        )
    ]


    assert (
        len(comparable_ids)
        > 0
    )


    print(
        "PASS - Comparison selector source data available"
    )


    # ========================================================
    # TEST 8
    # Compare first two evaluated modules.
    # ========================================================

    selected_ids = (
        comparable_ids[:2]
    )


    response = client.post(
        "/api/compare",

        json={
            "answers":
                answers,

            "module_ids":
                selected_ids,
        },
    )


    assert (
        response.status_code
        == 200
    ), response.get_data(
        as_text=True
    )


    comparison_data = (
        response.get_json()
    )


    assert (
        comparison_data[
            "status"
        ]
        == "ok"
    )


    comparison = (
        comparison_data[
            "comparison"
        ]
    )


    assert isinstance(
        comparison[
            "modules"
        ],
        list,
    )

    assert (
        len(
            comparison[
                "modules"
            ]
        )
        ==
        len(
            selected_ids
        )
    )


    assert isinstance(
        comparison[
            "rows"
        ],
        list,
    )

    assert (
        len(
            comparison[
                "rows"
            ]
        )
        > 0
    )


    print(
        "PASS - Side-by-side comparison API works"
    )


    # ========================================================
    # TEST 9
    # Comparison returns requested module IDs.
    # ========================================================

    returned_ids = [

        item[
            "module_id"
        ]

        for item
        in comparison[
            "modules"
        ]
    ]


    assert (
        returned_ids
        ==
        selected_ids
    )


    print(
        "PASS - Comparison preserves selected modules"
    )


    # ========================================================
    # TEST 10
    # Change Last Answer architecture.
    #
    # app.js implements this by popping the final answer
    # and replaying the remaining answer history.
    # Test exactly that backend behavior here.
    # ========================================================

    shortened_answers = (
        answers[:-1]
    )


    response = client.post(
        "/api/wizard",

        json={
            "answers":
                shortened_answers
        },
    )


    assert (
        response.status_code
        == 200
    )


    back_data = (
        response.get_json()
    )


    assert (
        back_data[
            "state"
        ]
        == "question"
    )


    print(
        "PASS - Change Last Answer replay works"
    )


    # ========================================================
    # TEST 11
    # Start New Customer architecture.
    # ========================================================

    response = client.post(
        "/api/wizard",

        json={
            "answers":
                []
        },
    )


    assert (
        response.status_code
        == 200
    )


    restart_data = (
        response.get_json()
    )


    assert (
        restart_data[
            "state"
        ]
        == "question"
    )


    assert (
        restart_data[
            "step"
        ]
        == 1
    )


    if (
        first_question_id
        is not None
    ):

        assert (
            restart_data[
                "question"
            ].get(
                "id"
            )
            ==
            first_question_id
        )


    print(
        "PASS - Start New Customer returns to first question"
    )


    # ========================================================
    # TEST 12
    # REAL DECISION STATE:
    # BLE + integrated MCU.
    #
    # Current portfolio contains BLE embedded-MCU modules,
    # so this should produce a compatible recommendation.
    # ========================================================

    requirement = (
        create_empty_requirement()
    )


    requirement[
        "connectivity"
    ][
        "ble_required"
    ] = True


    requirement[
        "bluetooth"
    ][
        "ble_required"
    ] = True


    requirement[
        "embedded_features"
    ][
        "integrated_mcu_required"
    ] = True


    result = (
        build_recommendation_result(
            requirement
        )
    )


    assert (
        result[
            "decision"
        ]
        == "recommended"
    )


    assert (
        result[
            "top_candidate"
        ][
            "status"
        ]
        == "COMPATIBLE"
    )


    print(
        "PASS - Recommended-state acceptance scenario"
    )


    # ========================================================
    # TEST 13
    # REAL DECISION STATE:
    # Wi-Fi 6 but host interface unknown.
    #
    # The current Wi-Fi 6 modules are host-based.
    # Leaving customer host availability unknown should
    # therefore require clarification.
    # ========================================================

    requirement = (
        create_empty_requirement()
    )


    requirement[
        "connectivity"
    ][
        "wifi_required"
    ] = True


    requirement[
        "wifi"
    ][
        "required"
    ] = True


    requirement[
        "wifi"
    ][
        "wifi6_required"
    ] = True


    result = (
        build_recommendation_result(
            requirement
        )
    )


    assert (
        result[
            "decision"
        ]
        == "clarification_required"
    ), result


    assert (
        result[
            "top_candidate"
        ][
            "status"
        ]
        == "NEEDS_CLARIFICATION"
    )


    assert (
        len(
            result[
                "top_candidate"
            ][
                "clarifications"
            ]
        )
        > 0
    )


    print(
        "PASS - Clarification-state acceptance scenario"
    )


    # ========================================================
    # TEST 14
    # REAL DECISION STATE:
    #
    # Wi-Fi 6 + integrated MCU.
    #
    # In the current portfolio the Wi-Fi 6 host modules do
    # not provide an integrated MCU, while embedded-MCU
    # modules are earlier Wi-Fi generations.
    # ========================================================

    requirement = (
        create_empty_requirement()
    )


    requirement[
        "connectivity"
    ][
        "wifi_required"
    ] = True


    requirement[
        "wifi"
    ][
        "required"
    ] = True


    requirement[
        "wifi"
    ][
        "wifi6_required"
    ] = True


    requirement[
        "embedded_features"
    ][
        "integrated_mcu_required"
    ] = True


    result = (
        build_recommendation_result(
            requirement
        )
    )


    assert (
        result[
            "decision"
        ]
        == "no_suitable_module"
    ), result


    assert (
        result[
            "top_candidate"
        ]
        is not None
    )


    assert (
        result[
            "top_candidate"
        ][
            "status"
        ]
        == "NOT_SUITABLE"
    )


    print(
        "PASS - No-suitable-module acceptance scenario"
    )


    print()
    print(
        "===================================================="
    )
    print(
        " LESSON 3H: ALL ACCEPTANCE TESTS PASS"
    )
    print(
        "===================================================="
    )
    print()


if __name__ == "__main__":

    run_tests()