
from copy import deepcopy

from core.customer_requirement import (create_empty_requirement)

class QuestionTreeError(Exception):
    """
    Raised when the question tree or an answer
    is invalid.
    """

    pass
    
    
def _set_requirement_value(requirement, path, value):
    """
    Set a value inside the customer requirement
    using dot notation.

    Example:

        connectivity.wifi_required

    becomes:

        requirement["connectivity"]["wifi_required"]
    """

    parts = path.split(".")
    current = requirement

    for part in parts[:-1]:
        if part not in current:
            raise QuestionTreeError(f"Invalid requirement path: {path}")

        if not isinstance(current[part],dict):
            raise QuestionTreeError(f"Requirement path is not a dictionary:{path}")

        current = current[part]

    final_key = parts[-1]

    if final_key not in current:
        raise QuestionTreeError(f"Invalid requirement field: {path}")

    current[final_key] = value
    
    
def _apply_updates(requirement,updates):
    """
    Apply all field updates contained in a
    question-tree 'set' object.
    """
    if not updates:
        return
    for path, value in updates.items():
        _set_requirement_value(requirement,path, value)
        
        
class QuestionSession:
    """
    Represents one customer requirement interview.

    The session:

        1. Starts at the configured first question
        2. Accepts an answer
        3. Updates customer_requirement
        4. Moves to the correct next question
        5. Records question history
    """

    def __init__(self, question_tree, requirement=None):
        self.question_tree = deepcopy(question_tree)
        if requirement is None:
            self.requirement = (create_empty_requirement())
        else:
            self.requirement = deepcopy(requirement)

        self.current_question_id = (self.question_tree["start_question"])
        self.history = []
        
    def get_current_question(self):
        """
        Return the question currently being asked.
        """

        if self.current_question_id is None:
            return None
        questions = self.question_tree["questions"]

        if self.current_question_id not in questions:
            raise QuestionTreeError(f"Question does not exist: {self.current_question_id}")

        question = deepcopy(questions[self.current_question_id])
        question["id"] = self.current_question_id

        return question
        
        
    def is_complete(self):
        """
        True when no further question remains.
        """

        return (self.current_question_id is None)
        
    def _answer_single_choice(self, question, answer):
        options = question.get("options", [])
        selected_option = None
        for option in options:
            if option["id"] == answer:
                selected_option = option
                break

        if selected_option is None:
            raise QuestionTreeError(f"Invalid answer '{answer}' for question {self.current_question_id}")
            
        _apply_updates(self.requirement, selected_option.get("set"))
        return selected_option.get("next", question.get("next"))
        
        
    def _answer_yes_no(self, question, answer):
        if isinstance(answer, bool):
            normalized = ("yes" if answer else "no")
        elif isinstance(answer, str ):
            normalized = (answer.strip().lower())
            if normalized in ("y", "true", "1"):
                normalized = "yes"
            elif normalized in ("n", "false", "0"):
                normalized = "no"
        else:
            raise QuestionTreeError("Yes/no answer must be True, False, yes or no.")
        if normalized not in ("yes", "no"):
            raise QuestionTreeError(f"Invalid yes/no answer: {answer}")

        branch = question.get(normalized)

        if branch is None:
            raise QuestionTreeError(f"Question {self.current_question_id} does not define a '{normalized}' branch." )

        _apply_updates(self.requirement, branch.get("set"))

        return branch.get("next")
    

    def _answer_multiple_choice(self, question, answer):

        if not isinstance(answer,(list, tuple, set)):
            raise QuestionTreeError("Multiple-choice answer must be a list of option IDs.")

        selected_ids = list(answer)
        if not selected_ids:
            raise QuestionTreeError("At least one option must be selected.")

        # -------------------------------------------------
        # 'unknown' cannot logically be selected together
        # with a confirmed interface.
        # -------------------------------------------------

        if ("unknown" in selected_ids and len(selected_ids) > 1):
            raise QuestionTreeError("'unknown' cannot be combined with another host interface.")

        available_options = {option["id"]:option for option in question.get("options", [])}
        for selected_id in selected_ids:
            if selected_id not in available_options:
                raise QuestionTreeError(f"Invalid option: {selected_id}")

        # -------------------------------------------------
        # Initialize all host-interface values.
        # -------------------------------------------------

        _apply_updates(self.requirement,question.get("before_answer"))

        # -------------------------------------------------
        # Apply every selected option.
        # -------------------------------------------------

        for selected_id in selected_ids:
            option = available_options[selected_id]
            _apply_updates(self.requirement, option.get("set"))

        return question.get("next")   
        
    def answer(self,answer):
        """
        Answer the current question and move
        the session to the next question.
        """

        question = (self.get_current_question())

        if question is None:
            raise QuestionTreeError("The question session is already complete.")

        question_id = (self.current_question_id)
        question_type = question["type"]

        if question_type == "single_choice":
            next_question = (self._answer_single_choice(question, answer))

        elif question_type == "yes_no":
            next_question = (self._answer_yes_no(question, answer))

        elif question_type == "multiple_choice":
            next_question = (self._answer_multiple_choice(question, answer))

        else:
            raise QuestionTreeError(f"Unsupported question type: {question_type}")

        self.history.append({"question_id": question_id,
                "question": question["text"],
                "answer": deepcopy(answer),
                "next_question": next_question
            }
        )

        self.current_question_id = (next_question)
        return self.get_current_question() 

            
    def get_requirement(self):
        """
        Return the current structured customer requirement.
        """

        return deepcopy(self.requirement)
        
    def get_history(self):
        """
        Return the sales-question history.
        """

        return deepcopy(self.history)