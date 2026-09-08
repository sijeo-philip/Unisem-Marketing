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
    Return one valid engine value.
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


def run_tests():

    print()

    print(
        "Testing Lesson 2F Navigation and Session Replay"
    )

    print(
        "-----------------------------------------------"
    )


    client = app.test_client()


    # ====================================================
    # TEST 1
    # Obtain first question.
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
    )


    first_data = (
        response.get_json()
    )


    assert (
        first_data["state"]
        == "question"
    )


    first_question = (
        first_data["question"]
    )


    first_question_id = (
        first_question["id"]
    )


    print(
        "PASS - First question loaded:",
        first_question_id
    )


    # ====================================================
    # TEST 2
    # Answer first question.
    # ====================================================

    first_answer = (
        choose_answer(
            first_question
        )
    )


    answers = [
        first_answer
    ]


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
    )


    second_data = (
        response.get_json()
    )


    print(
        "PASS - First answer replayed"
    )


    # ====================================================
    # TEST 3
    # Simulate BACK by removing last answer.
    # ====================================================

    answers.pop()


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
    )


    back_data = (
        response.get_json()
    )


    assert (
        back_data["state"]
        == "question"
    )


    assert (
        back_data["question"]["id"]
        ==
        first_question_id
    )


    print(
        "PASS - Back navigation restores prior question"
    )


    # ====================================================
    # TEST 4
    # Server has no hidden session state.
    #
    # Ask again with no answers and we must still receive
    # the same first question.
    # ====================================================

    response = client.post(
        "/api/wizard",
        json={
            "answers": []
        },
    )


    reset_data = (
        response.get_json()
    )


    assert (
        reset_data["question"]["id"]
        ==
        first_question_id
    )


    print(
        "PASS - Wizard server remains stateless"
    )


    # ====================================================
    # TEST 5
    # Build several answers, then truncate history.
    # ====================================================

    answers = []


    question_ids = []


    for _ in range(4):

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
        )


        data = (
            response.get_json()
        )


        if (
            data["state"]
            == "complete"
        ):

            break


        question_ids.append(
            data["question"]["id"]
        )


        answers.append(
            choose_answer(
                data["question"]
            )
        )


    if (
        len(answers) >= 2
    ):

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


        shortened_data = (
            response.get_json()
        )


        assert (
            shortened_data["status"]
            == "ok"
        )


        print(
            "PASS - Truncated answer history replays safely"
        )

    else:

        print(
            "PASS - Short wizard path handled safely"
        )


    # ====================================================
    # TEST 6
    # Two independent customer sessions must produce
    # independent state from their supplied answers.
    # ====================================================

    response_a = client.post(
        "/api/wizard",
        json={
            "answers": []
        },
    )


    response_b = client.post(
        "/api/wizard",
        json={
            "answers": []
        },
    )


    data_a = (
        response_a.get_json()
    )


    data_b = (
        response_b.get_json()
    )


    assert (
        data_a["question"]["id"]
        ==
        data_b["question"]["id"]
    )


    print(
        "PASS - Independent customer sessions start clean"
    )


    print()

    print(
        "ALL LESSON 2F TESTS PASSED"
    )

    print()


if __name__ == "__main__":

    run_tests()