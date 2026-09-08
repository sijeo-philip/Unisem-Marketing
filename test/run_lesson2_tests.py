import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)


TEST_DIR = (
    PROJECT_ROOT
    / "tests"
)


LESSON_2_TESTS = [

    "test_web_shell.py",

    "test_question_tree_api.py",

    "test_wizard_api.py",

    "test_recommendation_view.py",

    "test_comparison_api.py",

    "test_navigation_session.py",

    "test_hardening.py",

]


def run():

    print()

    print(
        "===================================================="
    )

    print(
        " UNISEM OFFLINE MARKETING TOOL"
    )

    print(
        " LESSON 2 MASTER REGRESSION"
    )

    print(
        "===================================================="
    )

    print()


    passed = []


    for filename in LESSON_2_TESTS:

        print()

        print(
            "----------------------------------------------------"
        )

        print(
            "Running:",
            filename
        )

        print(
            "----------------------------------------------------"
        )

        print()


        path = (
            TEST_DIR
            / filename
        )


        if not path.exists():

            print(
                "FAIL - Test file not found:",
                path
            )


            return 1


        result = subprocess.run(
            [
                sys.executable,
                str(path),
            ],

            cwd=str(
                PROJECT_ROOT
            ),
        )


        if (
            result.returncode
            != 0
        ):

            print()

            print(
                "===================================================="
            )

            print(
                "LESSON 2 REGRESSION FAILED"
            )

            print(
                "Failed test:",
                filename
            )

            print(
                "===================================================="
            )


            return (
                result.returncode
                or 1
            )


        passed.append(
            filename
        )


    print()

    print(
        "===================================================="
    )

    print(
        "ALL LESSON 2 TESTS PASSED"
    )

    print(
        "===================================================="
    )

    print()


    print(
        "Tests passed:"
    )


    for filename in passed:

        print(
            "  PASS -",
            filename
        )


    print()


    return 0


if __name__ == "__main__":

    raise SystemExit(
        run()
    )