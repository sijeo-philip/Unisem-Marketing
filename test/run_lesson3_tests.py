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
    / "test"
)


LESSON_3_TESTS = [

    "test_lesson3a.py",

    "test_lesson3b.py",

    "test_lesson3c.py",

    "test_lesson3d.py",

    "test_lesson3e.py",

    "test_lesson3f.py",

    "test_lesson3g.py",

    "test_lesson3h.py",
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
        " LESSON 3 MASTER REGRESSION"
    )

    print(
        "===================================================="
    )

    print()


    passed = []


    for filename in LESSON_3_TESTS:

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
                "LESSON 3 REGRESSION FAILED"
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
        "ALL LESSON 3 TESTS PASSED"
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