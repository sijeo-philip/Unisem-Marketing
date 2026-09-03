

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

QUESTION_FILE = (
    BASE_DIR
    / "data"
    / "question_tree.json"
    )
    
    
with open(
    QUESTION_FILE,
    "r",
    encoding = "utf-8"
    ) as file:
        tree = json.load(file)
        

print()
print("QUESTION TREE")
print("=============")
print()

print("version:",tree["version"])
print("Start Question:", tree["start_question"])
print()

print("Number of Questions:", len(tree["questions"]))
print()

for question_id, question in tree["questions"].items():
    print(question_id, "=>", question["text"])
    
    