import os

from classes.roo_document import RooDocument
import classes.globals as g


g.clear()
file_list = []
source_folder = os.path.join(os.getcwd(), "source")
for file in os.listdir(source_folder):
    if file.endswith("docx"):
        if "$" not in file:
            if "~" not in file:
                file_list.append(file)

# omissions = ["Albania PSR.docx", "Cameroon PSR.docx"]
omissions = ["CotedIvoire PSR.docx"]
start_at = "Andean PSR.docx"
# start_at = ""
file_list.sort()
index = 0
max_files = 100
for file in file_list:
    if file not in omissions:
        if file >= start_at:
            document = RooDocument(file)
            index += 1
            if index > max_files:
                break
