import json
import sys
from pathlib import Path

from flask import Flask, jsonify, render_template


# ============================================================
# Application paths
# ============================================================

def get_base_dir() -> Path:
    """
    Return the directory containing application resources.

    During normal Python execution this is the project folder.

    Later, when we package the application as a Windows EXE,
    PyInstaller may provide the temporary resource directory
    through sys._MEIPASS.
    """

    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)

    return Path(__file__).resolve().parent


BASE_DIR = get_base_dir()


# ============================================================
# Flask application
# ============================================================

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "web" / "templates"),
    static_folder=str(BASE_DIR / "web" / "static"),
)


# ============================================================
# Utility functions
# ============================================================

def find_project_file(filename: str):
    """
    Find a project data file.

    Lesson 1 projects may currently have the JSON files either
    directly in the project directory or inside a data folder.

    Supporting both layouts avoids changing our validated
    Lesson 1 structure.
    """

    candidates = [BASE_DIR / filename, BASE_DIR / "data" / filename,]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return None


def load_json_file(filename: str):
    """
    Load and return JSON data.

    Raises FileNotFoundError if the requested project file
    cannot be located.
    """

    path = find_project_file(filename)

    if path is None:
        raise FileNotFoundError(filename)

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


# ============================================================
# Question-tree normalization
# ============================================================

def first_present(mapping, *keys):
    """
    Return the first non-empty value found using the
    supplied keys.
    """

    if not isinstance(mapping, dict):
        return None

    for key in keys:
        if key in mapping:
            value = mapping[key]
            if value is not None and value != "":
                return value
    return None


def normalize_option(raw_option, fallback_value, dictionary_key=None,):
    """
    Convert one question option into a consistent structure
    for the browser.

    Browser format:

        {
            "label": "...",
            "value": "...",
            "next_question_id": "..."
        }
    """

    # --------------------------------------------------------
    # Dictionary-style option
    # --------------------------------------------------------

    if isinstance(raw_option, dict):

        label = first_present(raw_option, "label", "text", "name", "title", "display")
        value = first_present(raw_option, "value", "id", "key", "code")
        next_question = first_present(raw_option, "next", "next_question", "next_question_id", "next_id", "goto", "target" )

        if label is None:
            label = dictionary_key

        if label is None:
            label = value

        if label is None:
            label = str(fallback_value)

        if value is None:
            value = dictionary_key

        if value is None:
            value = label

        return {"label": str(label), "value": value, "next_question_id": (str(next_question) if next_question is not None else None)}


    # --------------------------------------------------------
    # Simple string / number option
    # --------------------------------------------------------

    if dictionary_key is not None:

        return {"label": str(dictionary_key), "value": dictionary_key, "next_question_id": (str(raw_option) if raw_option is not None else None)}


    return {"label": str(raw_option), "value": raw_option, "next_question_id": None}


def normalize_question_tree(raw_tree):
    """
    Convert question_tree.json into a predictable structure
    for the web browser.

    This function intentionally supports several common JSON
    naming conventions so that the browser UI is isolated from
    the storage format used by Lesson 1.
    """

    if not isinstance(raw_tree, dict):

        raise ValueError("question_tree.json must contain a JSON object")


    # --------------------------------------------------------
    # Locate the question collection
    # --------------------------------------------------------

    raw_questions = first_present(raw_tree, "questions", "question_tree", "nodes", "steps")


    # --------------------------------------------------------
    # Fallback:
    # The root itself may contain q1, q2, q3...
    # --------------------------------------------------------

    if raw_questions is None:
        possible_questions = {}
        for key, value in raw_tree.items():
            if not isinstance(value, dict):
                continue

            if any(field in value for field in ("text", "question", "prompt", "options", "choices", "answers")):
                possible_questions[key] = value

        if possible_questions:
            raw_questions = possible_questions

    if raw_questions is None:
        raise ValueError("Unable to locate questions in question_tree.json")

    normalized_questions = []


    # --------------------------------------------------------
    # Dictionary:
    #
    # "questions": {
    #     "q1": {...},
    #     "q2": {...}
    # }
    # --------------------------------------------------------

    if isinstance(raw_questions, dict):

        question_items = list(raw_questions.items())


    # --------------------------------------------------------
    # List:
    #
    # "questions": [
    #     {"id": "q1", ...},
    #     {"id": "q2", ...}
    # ]
    # --------------------------------------------------------

    elif isinstance(raw_questions, list):

        question_items = []
        for index, question in enumerate(raw_questions):
            question_items.append((str(index + 1), question,))
    else:
        raise ValueError("Questions must be stored as a dictionary or list")


    # --------------------------------------------------------
    # Normalize each question
    # --------------------------------------------------------

    for index, (dictionary_question_id, raw_question,) in enumerate(question_items):
        if not isinstance(raw_question, dict):
            continue

        question_id = first_present(raw_question, "id", "question_id", "key", "code")
        if question_id is None:
            question_id = dictionary_question_id

        question_text = first_present(raw_question, "text", "question", "prompt", "label", "title")

        if question_text is None:
            question_text = (f"Question {index + 1}")

        question_type = first_present(raw_question, "type", "question_type", "input_type")

        if question_type is None:
            question_type = "single_choice"
        raw_options = first_present(raw_question, "options", "choices", "answers", "responses")

        question_default_next = first_present(raw_question, "next", "next_question", "next_question_id", "next_id")
        normalized_options = []


        # ----------------------------------------------------
        # Options stored as dictionary
        # ----------------------------------------------------

        if isinstance(raw_options, dict):

            for option_key, option_value in (raw_options.items()):
                option = normalize_option(option_value, option_key, dictionary_key=option_key,)
                if (option["next_question_id"] is None and question_default_next is not None):
                    option["next_question_id"] = str(question_default_next)
                normalized_options.append(option)


        # ----------------------------------------------------
        # Options stored as list
        # ----------------------------------------------------
        elif isinstance(raw_options, list):
            for option_index, raw_option in (enumerate(raw_options)):
                option = normalize_option(raw_option, option_index,)
                if (option["next_question_id"] is None and question_default_next is not None):
                    option["next_question_id"] = str(question_default_next)
                normalized_options.append(option)


        normalized_questions.append(
            {
                "id": str(question_id),
                "text": str(question_text),
                "type": str(question_type),
                "options": normalized_options,
            }
        )


    if not normalized_questions:

        raise ValueError(
            "No usable questions were found"
        )


    # --------------------------------------------------------
    # Add sequential fallback navigation.
    #
    # This is used only when the JSON does not explicitly
    # provide branching information.
    # --------------------------------------------------------

    for index, question in enumerate(normalized_questions):
        if index + 1 < len(normalized_questions):
            fallback_next = (normalized_questions[index + 1]["id"])
        else:
            fallback_next = None
        for option in question["options"]:
            if option["next_question_id"] is None:
                option["next_question_id"] = fallback_next


    # --------------------------------------------------------
    # Determine starting question
    # --------------------------------------------------------

    start_question = first_present(raw_tree, "start_question", "start_question_id", "start", "root", "first_question", "entry")
    if start_question is None:
        start_question = (normalized_questions[0]["id"])

    version = first_present(raw_tree, "version", "question_tree_version", "revision" )
    return {"version": version, "start_question_id": str(start_question), "questions": normalized_questions}

# ============================================================
# Browser routes
# ============================================================

@app.get("/")
def home():
    """
    Main browser interface.
    """

    return render_template("index.html")


# ============================================================
# API routes
# ============================================================

@app.get("/api/health")
def api_health():
    """
    Basic health-check endpoint used by the browser.

    The browser calls this endpoint during startup to make
    sure that the local Python application is running.
    """

    modules_file = find_project_file("modules.json")
    question_tree_file = find_project_file("question_tree.json")

    return jsonify(
        {
            "status": "ok",
            "application": "Unisem Offline Marketing Tool",
            "offline": True,
            "lesson": "2A",
            "modules_database": modules_file is not None,
            "question_tree": question_tree_file is not None,
        }
    )


@app.get("/api/system")
def api_system():
    """
    Return basic application/database information.
    """

    result = {
        "modules_available": False,
        "question_tree_available": False,
    }

    modules_file = find_project_file("modules.json")

    if modules_file is not None:
        result["modules_available"] = True

        try:
            data = load_json_file("modules.json")

            if isinstance(data, dict):

                result["portfolio_version"] = (
                    data.get("portfolio_version")
                    or data.get("version")
                    or "unknown"
                )

                modules = data.get("modules")

                if isinstance(modules, list):
                    result["module_count"] = len(modules)

                elif isinstance(modules, dict):
                    result["module_count"] = len(modules)

            elif isinstance(data, list):
                result["module_count"] = len(data)

        except Exception as exc:
            result["modules_error"] = str(exc)

    question_tree_file = find_project_file("question_tree.json")

    if question_tree_file is not None:
        result["question_tree_available"] = True

    return jsonify(result)
    
    
@app.get("/api/question-tree")
def api_question_tree():
    """
    Return a browser-friendly representation of the
    Sales Wizard question tree.

    Important:
    This does NOT execute the recommendation engine.
    It only exposes the questionnaire structure.
    """

    try:

        raw_tree = load_json_file("question_tree.json")
        normalized_tree = (normalize_question_tree(raw_tree))
        return jsonify({"status": "ok", **normalized_tree})

    except FileNotFoundError:
        return jsonify(
            {
                "status": "error",
                "error": (
                    "question_tree.json "
                    "was not found"
                ),
            }
        ), 404


    except Exception as exc:
        return jsonify(
            {
                "status": "error",
                "error": str(exc),
            }
        ), 500


# ============================================================
# Application entry point
# ============================================================

if __name__ == "__main__":

    print()
    print("=====================================================")
    print(" UNISEM OFFLINE MARKETING TOOL")
    print("=====================================================")
    print()
    print("Local application starting...")
    print()
    print("Open your browser at:")
    print()
    print("    http://127.0.0.1:5000")
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
    )