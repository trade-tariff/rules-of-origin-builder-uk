import os
import json

from classes.roo_document import RooDocument
import classes.globals as g

g.clear()
file_list = []
source_folder = os.path.join(os.getcwd(), "resources", "source")
for file in os.listdir(source_folder):
    if file.endswith("docx"):
        if "$" not in file:
            if "~" not in file:
                file_list.append(file)

# omissions = ["Albania PSR.docx", "Cameroon PSR.docx"]
omissions = [
    "Australia PSR.docx",
    "New-Zealand PSR.docx",
    "Andean PSR.docx"
]

modern = [
    "EU PSR.docx",
    "Canada PSR.docx",
    "Turkey PSR.docx",
    "Japan PSR.docx"
]

included = [
    "Mexico PSR.docx"
]

omissions += modern
start_at = ""
file_list.sort()
index = 0
max_files = 100
for file in file_list:
    # if file in included:
    if file not in omissions:
        if file >= start_at:
            document = RooDocument(file)
            index += 1
            if index > max_files:
                break

filename = os.path.join(os.getcwd(), "resources", "temp", "multiple_chapter_rule_list.json")
with open(filename, 'w') as f:
    json.dump(g.multiple_chapter_rule_list, f, indent=4)
