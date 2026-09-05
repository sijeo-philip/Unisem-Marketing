import sys
from pathlib import Path


PROJECT_ROOT = (Path(__file__).resolve().parent.parent)
sys.path.insert(0, str(PROJECT_ROOT))

from app import app

def run_tests():

    print()
    print("Testing Lesson 2B Question Tree API")
    print("-----------------------------------")
    client = app.test_client()

    # ====================================================
    # TEST 1
    # API must respond
    # ====================================================

    response = client.get("/api/question-tree")
    assert (response.status_code == 200), ("Question-tree API returned HTTP {response.status_code}: {response.get_data(as_text=True)}")
    print("PASS - Question-tree API responded")


    # ====================================================
    # TEST 2
    # JSON response
    # ====================================================

    data = response.get_json()
    assert data is not None
    assert (data.get("status") == "ok"), data
    print("PASS - Question-tree API status OK")


    # ====================================================
    # TEST 3
    # Questions exist
    # ====================================================

    questions = data.get("questions")
    assert isinstance(questions,list)
    assert (len(questions) > 0)
    print("PASS - Questions loaded:",len(questions))
    # ====================================================
    # TEST 4
    # Every question has an ID
    # ====================================================

    question_ids = []
    for question in questions:
        question_id = question.get("id" )
        assert question_id
        question_ids.append(str(question_id))

    assert (len(question_ids) == len(set(question_ids))), ("Duplicate question IDs detected")
    print("PASS - Question IDs are valid and unique")

    # ====================================================
    # TEST 5
    # Starting question exists
    # ====================================================

    start_question_id = str(data.get("start_question_id"))
    assert (start_question_id in question_ids), ("Start question does not exist:" + start_question_id)
    print("PASS - Start question exists:", start_question_id)

    # ====================================================
    # TEST 6
    # Question text exists
    # ====================================================

    for question in questions:
        assert (question.get("text"))
    print("PASS - All questions have display text")

    # ====================================================
    # TEST 7
    # At least one selectable option exists
    # ====================================================

    total_options = sum(len(question.get("options", [])) for question in questions)
    assert (total_options > 0)
    print("PASS - Selectable options found:", total_options)
    print()
    print("ALL LESSON 2B TESTS PASSED")
    print()


if __name__ == "__main__":

    run_tests()