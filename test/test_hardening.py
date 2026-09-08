

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


from app import (
    app,
    MAX_WIZARD_ANSWERS,
    MAX_COMPARE_MODULES,
)


def run_tests():

    print()

    print(
        "Testing Lesson 2G Application Hardening"
    )

    print(
        "---------------------------------------"
    )


    client = app.test_client()


    # ====================================================
    # TEST 1
    # Main browser page.
    # ====================================================

    response = client.get(
        "/"
    )


    assert (
        response.status_code
        == 200
    )


    print(
        "PASS - Browser shell available"
    )


    # ====================================================
    # TEST 2
    # CSS asset.
    # ====================================================

    response = client.get(
        "/static/css/style.css"
    )


    assert (
        response.status_code
        == 200
    )


    assert (
        len(response.data)
        > 0
    )


    print(
        "PASS - CSS asset available"
    )


    # ====================================================
    # TEST 3
    # JavaScript asset.
    # ====================================================

    response = client.get(
        "/static/js/app.js"
    )


    assert (
        response.status_code
        == 200
    )


    assert (
        len(response.data)
        > 0
    )


    print(
        "PASS - JavaScript asset available"
    )


    # ====================================================
    # TEST 4
    # No external CDN dependency in browser HTML.
    # ====================================================

    response = client.get(
        "/"
    )


    html = response.get_data(
        as_text=True
    ).lower()


    assert (
        "https://" not in html
    )


    assert (
        "http://" not in html
    )


    print(
        "PASS - Browser page has no external URL dependency"
    )


    # ====================================================
    # TEST 5
    # Health API.
    # ====================================================

    response = client.get(
        "/api/health"
    )


    assert (
        response.status_code
        == 200
    )


    data = response.get_json()


    assert (
        data["status"]
        == "ok"
    )


    assert (
        data["offline"]
        is True
    )


    print(
        "PASS - Health API valid"
    )


    # ====================================================
    # TEST 6
    # Security headers.
    # ====================================================

    assert (
        response.headers.get(
            "X-Content-Type-Options"
        )
        == "nosniff"
    )


    assert (
        response.headers.get(
            "X-Frame-Options"
        )
        == "DENY"
    )


    assert (
        response.headers.get(
            "Referrer-Policy"
        )
        == "no-referrer"
    )


    assert (
        response.headers.get(
            "Content-Security-Policy"
        )
    )


    print(
        "PASS - Browser security headers applied"
    )


    # ====================================================
    # TEST 7
    # API response must not be cached.
    # ====================================================

    cache_control = (
        response.headers.get(
            "Cache-Control",
            ""
        )
    )


    assert (
        "no-store"
        in cache_control
    )


    print(
        "PASS - API caching disabled"
    )


    # ====================================================
    # TEST 8
    # Wizard requires JSON Content-Type.
    # ====================================================

    response = client.post(
        "/api/wizard",

        data="{}",
    )


    assert (
        response.status_code
        == 400
    )


    print(
        "PASS - Non-JSON wizard request rejected"
    )


    # ====================================================
    # TEST 9
    # Malformed JSON rejected.
    # ====================================================

    response = client.post(
        "/api/wizard",

        data="{broken-json",

        content_type=
            "application/json",
    )


    assert (
        response.status_code
        == 400
    )


    print(
        "PASS - Malformed JSON rejected"
    )


    # ====================================================
    # TEST 10
    # JSON array is not valid API request body.
    # ====================================================

    response = client.post(
        "/api/wizard",

        json=[
            "not",
            "an",
            "object",
        ],
    )


    assert (
        response.status_code
        == 400
    )


    print(
        "PASS - Non-object JSON rejected"
    )


    # ====================================================
    # TEST 11
    # Answers must be list.
    # ====================================================

    response = client.post(
        "/api/wizard",

        json={
            "answers":
                "not-a-list"
        },
    )


    assert (
        response.status_code
        == 400
    )


    print(
        "PASS - Invalid answer container rejected"
    )


    # ====================================================
    # TEST 12
    # Excessive answer history rejected.
    # ====================================================

    excessive_answers = [
        "x"
        for _ in range(
            MAX_WIZARD_ANSWERS
            + 1
        )
    ]


    response = client.post(
        "/api/wizard",

        json={
            "answers":
                excessive_answers
        },
    )


    assert (
        response.status_code
        == 400
    )


    print(
        "PASS - Excessive answer history rejected"
    )


    # ====================================================
    # TEST 13
    # Comparison requires JSON.
    # ====================================================

    response = client.post(
        "/api/compare",

        data="{}",
    )


    assert (
        response.status_code
        == 400
    )


    print(
        "PASS - Non-JSON comparison request rejected"
    )


    # ====================================================
    # TEST 14
    # Too many comparison modules rejected.
    #
    # This happens before requirement reconstruction.
    # ====================================================

    too_many_modules = [
        "MODULE_"
        + str(index)

        for index in range(
            MAX_COMPARE_MODULES
            + 1
        )
    ]


    response = client.post(
        "/api/compare",

        json={
            "answers": [],

            "module_ids":
                too_many_modules,
        },
    )


    assert (
        response.status_code
        == 400
    )


    print(
        "PASS - Comparison module limit enforced"
    )


    # ====================================================
    # TEST 15
    # Question-tree API remains healthy.
    # ====================================================

    response = client.get(
        "/api/question-tree"
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
        len(
            data["questions"]
        )
        > 0
    )


    print(
        "PASS - Valid question tree survives hardening"
    )


    print()

    print(
        "ALL LESSON 2G TESTS PASSED"
    )

    print()


if __name__ == "__main__":

    run_tests()