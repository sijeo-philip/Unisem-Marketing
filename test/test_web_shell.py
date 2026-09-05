
import sys
from pathlib import Path

PROJECT_ROOT = (Path(__file__).resolve().parent.parent)

sys.path.insert(0, str(PROJECT_ROOT))


from app import app 


def run_tests():

    print()
    print("Testing Lesson 2A Web Application")
    print("---------------------------------")
    client = app.test_client()

    # ----------------------------------------------------
    # Test 1
    # Main browser page
    # ----------------------------------------------------
    response = client.get("/")
    assert response.status_code == 200
    print("PASS - Browser home page")

    # ----------------------------------------------------
    # Test 2
    # Health API
    # ----------------------------------------------------

    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["offline"] is True
    print("PASS - Backend health API")

    # ----------------------------------------------------
    # Test 3
    # Lesson 1 module database found
    # ----------------------------------------------------

    assert (data["modules_database"] is True)
    print("PASS - modules.json detected")

    # ----------------------------------------------------
    # Test 4
    # Lesson 1 question tree found
    # ----------------------------------------------------

    assert (data["question_tree"] is True)
    print("PASS - question_tree.json detected")
    # ----------------------------------------------------
    # Test 5
    # System API
    # ----------------------------------------------------
    response = client.get("/api/system")
    assert response.status_code == 200
    print("PASS - System information API")
    print()
    print("ALL LESSON 2A TESTS PASSED")
    print()

if __name__ == "__main__":
    run_tests()