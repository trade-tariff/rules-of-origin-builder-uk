from re import sub
import sys
import os
import json
import shutil
import csv
from dotenv import load_dotenv
from docx import Document
from docx.api import Document

from classes.rule_set_modern import RuleSetModern
from classes.rule_set_legacy import RuleSetLegacy
from classes.comm_code_validator import CommCodeValidator
import classes.globals as g

class RooDocument(object):
    def __init__(self, file=None):
        self.file = file
        self.get_environment()
        self.get_all_rules_with_classes()
        self.get_chapter_codes()
        self.get_arguments()
        if self.create_json:
            self.open_document()
            self.get_document_type()
            self.validate_table()
            self.read_table()
            self.process_table()
            if self.modern:
                self.process_subdivisions()
                self.remove_invalid_entries()
            else:
                self.remove_working_nodes()
            self.write_table()
            self.kill_document()

        if self.validate_commodities:
            self.check_coverage()
        if self.validate_min_max:
            self.validate_min_max_values()

        print("\nFinished processing {file}\n".format(file=self.docx_filename))

    def get_environment(self):
        load_dotenv('.env')
        self.source_folder = os.path.join(os.getcwd(), "source")

        # Get paths
        self.code_list = os.getenv('code_list')
        self.ott_path = os.getenv('ott_path')
        self.all_rules_path = os.getenv('all_rules_path')

        # Get features
        modern_documents = os.getenv('modern_documents')
        self.validate_tables = int(os.getenv('validate_tables'))
        self.modern_documents = modern_documents.split(",")
        self.create_json = os.getenv('create_json')
        self.validate_commodities = int(os.getenv('validate_commodities'))
        self.validate_min_max = int(os.getenv('validate_min_max'))

    def remove_invalid_entries(self):
        for i in range(len(self.rule_sets) - 1, -1, -1):
            rule_set = self.rule_sets[i]
            if rule_set["valid"] is False:
                a = 1
                self.rule_sets.pop(i)

    def get_all_rules_with_classes(self):
        f = open(self.all_rules_path)
        g.all_rules_with_classes = json.load(f)
        f.close()
        a = 1

    def get_chapter_codes(self):
        g.all_headings = {}
        g.all_subheadings = {}
        g.all_codes = []
        found_headings = []
        with open(self.code_list) as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row["Class"] == "commodity":
                    if row["Commodity code"][0:4] not in found_headings:
                        found_headings.append(row["Commodity code"][0:4])
                        g.all_codes.append(row["Commodity code"])

                if row["Commodity code"][-6:] == "000000" and row["Commodity code"][-8:] != "00000000":
                    heading = row["Commodity code"][0:4]
                    g.all_headings[heading] = row["Description"]

                if row["Commodity code"][-4:] == "0000" and row["Commodity code"][-6:] != "000000":
                    subheading = row["Commodity code"][0:6]
                    g.all_subheadings[subheading] = row["Description"]

        csv_file.close()
        a = 1

    def get_arguments(self):
        if self.file is not None:
            self.docx_filename = self.file
            self.docx_filepath = os.path.join(self.source_folder, self.docx_filename)
        else:
            if len(sys.argv) > 1:
                self.docx_filename = sys.argv[1]
                self.docx_filepath = os.path.join(self.source_folder, self.docx_filename)
            else:
                print("Please supply an input document")
                sys.exit()

        self.export_folder = os.path.join(os.getcwd(), "export")
        self.export_filename = self.docx_filename.replace(".docx", "").replace(" ", "_").lower()
        self.export_filename = self.export_filename.replace("_psr", "")
        self.export_filepath = os.path.join(self.export_folder, self.export_filename) + ".json"

    def open_document(self):
        print("\nBeginning processing {file}\n".format(file=self.docx_filename))
        self.document = Document(self.docx_filepath)

    def get_document_type(self):
        filename_compare = self.docx_filename.replace(" PSR.docx", "")
        if filename_compare in self.modern_documents:
            self.modern = True
        else:
            self.modern = False

    def read_table(self):
        print("- Reading table for file {file}".format(file=self.docx_filename))
        table = self.document.tables[0]

        if self.modern:
            rename_keys = {
                "Classification": "original_heading",
                "PSR": "original_rule"
            }
        else:
            rename_keys = {
                "Classification": "original_heading",
                "Description": "description",
                "PSR": "original_rule",
                "PSR2": "original_rule2"
            }

        data = []

        keys = None
        for i, row in enumerate(table.rows):
            text = (cell.text for cell in row.cells)

            # Establish the mapping based on the first row
            # headers; these will become the keys of our dictionary
            if i == 0:
                keys = tuple(text)
                continue

            # Construct a dictionary for this row, mapping
            # keys to values for this row
            row_data = dict(zip(keys, text))
            data.append(row_data)

        self.rows = []
        for item in data:
            if item != {}:
                for old_key in rename_keys:
                    new_key = rename_keys[old_key]
                    item[new_key] = item.pop(old_key)

                self.rows.append(item)

    def process_table(self):
        print("- Processing table for {file}".format(file=self.docx_filename))
        if self.modern:
            self.process_table_modern()
        else:
            self.process_table_legacy()

    def process_table_modern(self):
        self.rule_sets = []
        for row in self.rows:
            if "Section" in row["original_heading"]:
                pass
            elif "SECTION" in row["original_heading"]:
                pass
            elif "Chapter" in row["original_heading"]:
                pass
            else:
                if "61.01-61.17" in row["original_heading"]:
                    a = 1
                rule_set = RuleSetModern(row)
                self.rule_sets.append(rule_set.as_dict())

    def process_table_legacy(self):
        self.rule_sets = []
        for row in self.rows:
            # print(row["original_heading"])
            if "ex Chapter 28" in row["original_heading"]:
                a = 1
            rule_set = RuleSetLegacy(row)
            if rule_set.valid:
                self.rule_sets.append(rule_set.as_dict())

        self.normalise_chapters()

    def normalise_chapters(self):
        for chapter in range(1, 98):
            all_ex_codes = True
            if chapter == 30:
                a = 1
            is_chapter_mentioned = False
            rule_set_count = 0
            if chapter != 77:
                for rule_set in self.rule_sets:
                    if rule_set["chapter"] == chapter:
                        rule_set_count += 1
                        if not rule_set["is_ex_code"]:
                            all_ex_codes = False
                        if rule_set["is_chapter"]:
                            is_chapter_mentioned = True

            if not all_ex_codes:  # If it is all ex-codes, then we can just leave it as-is
                if rule_set_count > 1 and is_chapter_mentioned:
                    # Check if there are any ex codes anywhere except for on the chapter itself
                    # If there are not, then we can just replicate rules, ignoring the headings that are exceptions
                    has_ex_code_headings = False
                    for rule_set in self.rule_sets:
                        if rule_set["chapter"] == chapter:
                            if "chapter" not in rule_set["heading"].lower():
                                if "ex" in rule_set["heading"]:
                                    has_ex_code_headings = True
                                    break

                    if not has_ex_code_headings:
                        self.normalise_standard_chapter(chapter)
                    else:
                        self.normalise_complex_chapter(chapter)

    def normalise_complex_chapter(self, chapter):
        # print(chapter)
        # Get all the other rules in that chapter that are not the chapter heading
        if chapter == 30:
            a = 1
        matches = {}
        contains_subheading = False
        index = 0
        chapter_index = None
        for rule_set in self.rule_sets:
            if rule_set["chapter"] == chapter:
                if rule_set["is_chapter"]:
                    chapter_index = index

                if rule_set["is_subheading"]:
                    contains_subheading = True

                matches[index] = rule_set
            index += 1

        # Loop through all of the headings in chapter (according to the DB)
        # If the heading is missing:
        #   add in the heading as a copy of the chapter rule_set

        chapter_string = str(chapter).rjust(2, "0")
        if contains_subheading is False:
            for heading in g.all_headings:
                if heading[0:2] == chapter_string:
                    heading_exists_in_rule_set = False
                    for match in matches:
                        if heading in matches[match]["headings"]:
                            heading_exists_in_rule_set = True
                            if matches[match]["is_ex_code"]:
                                process_ex_code = True
                            else:
                                process_ex_code = False
                            break

                    if not heading_exists_in_rule_set:
                        # In expanding out the definition of a chapter to its subheadings, we will need
                        # to copy the rules from the chapter down to the headings that did not previously
                        # exist. In such cases, we need to create those headings and add them to the rule set.
                        obj = {
                            "heading": heading,
                            "headings": [heading],
                            "subheadings": [],
                            "chapter": chapter,
                            "subdivision": matches[chapter_index]["subdivision"],
                            "prefix": "",
                            "min": g.format_parts(heading, 0),
                            "max": g.format_parts(heading, 1),
                            "rules": matches[chapter_index]["rules"],
                            "is_ex_code": False,
                            "is_chapter": False,
                            "is_heading": True,
                            "is_subheading": False,
                            "is_range": False,
                            "valid": True
                        }
                        self.rule_sets.append(obj)
                    else:
                        if process_ex_code:
                            # This takes the definition of the chapter, reduced to 'Any other product'
                            # and assigns it to the matched heading as a counterpoint to the existing
                            # ex code, to cover all commodities that are not catered for within the
                            # specific ex code.
                            obj = {
                                "heading": matches[match]["heading"],
                                "headings": [],
                                "subheadings": [],
                                "chapter": chapter,
                                "subdivision": "Any other product",
                                "prefix": "",
                                "min": matches[match]["min"],
                                "max": matches[match]["max"],
                                "rules": matches[chapter_index]["rules"],
                                "is_ex_code": True,
                                "is_chapter": False,
                                "is_heading": True,
                                "is_subheading": False,
                                "is_range": False,
                                "valid": True
                            }
                            self.rule_sets.append(obj)

                if heading[0:2] > chapter_string:
                    break

            # Finally, remove the old chapter code, as its value has been copied elsewhere now
            self.rule_sets.pop(chapter_index)
        else:
            # Firstly check for any headings under the chapter that have rules that are based on subheadings and not headings
            this_chapter_headings = []
            headings_with_subheading_rules = []
            headings_without_subheading_rules = []

            for heading in g.all_headings:
                heading_contains_matches = False
                if heading[0:2] == chapter_string:
                    subheadings = []
                    contains_subheadings = False
                    matched = False
                    for match in matches:
                        if heading in matches[match]["headings"]:
                            if matches[match]["is_subheading"]:
                                contains_subheadings = True
                                subheadings.append(matches[match])
                            matched = True

                    if matched:
                        status = "matched"
                    else:
                        status = "unmatched"
                        contains_subheadings = False

                    obj = {heading: {
                        "status": status,
                        "contains_subheadings": contains_subheadings,
                        "subheadings": subheadings
                    }}
                    this_chapter_headings.append(obj)
                    if contains_subheadings:
                        headings_with_subheading_rules.append(heading)
                    else:
                        headings_without_subheading_rules.append(heading + "00")

            affected_subheadings = []
            for subheading in g.all_subheadings:
                if subheading[0:4] in headings_with_subheading_rules:
                    affected_subheadings.append(subheading)

            full_list = headings_without_subheading_rules + affected_subheadings
            full_list.sort()
            additional_rulesets = []
            for subheading in full_list:
                for match in matches:
                    if matches[match]["min"] <= str(subheading) + "0000" and matches[match]["max"] >= str(subheading) + "0000":
                        new_min = subheading + "0000"
                        if g.right(subheading, 2) == "00":
                            new_max = subheading[0:4] + "999999"
                        elif g.right(subheading, 1) == "0":
                            new_max = subheading[0:5] + "99999"
                        else:
                            new_max = subheading + "9999"
                        new_ruleset = self.copy_ruleset(matches[match], new_min, new_max)
                        additional_rulesets.append(new_ruleset)
                        a = 1

            # Remove any rulesets for the selected chapter, as these will all be replaced by the newly formed equivalents
            ruleset_count = len(self.rule_sets)
            for i in range(ruleset_count - 1, -1, -1):
                rule_set = self.rule_sets[i]
                if rule_set["chapter"] == chapter:
                    self.rule_sets.pop(i)

            # Then add the new rule sets onto the list
            self.rule_sets += additional_rulesets

    def copy_ruleset(self, match, new_min, new_max):
        obj = {
            "heading": match["heading"],
            "headings": match["headings"],
            "subheadings": match["subheadings"],
            "chapter": match["chapter"],
            "subdivision": match["subdivision"],
            "prefix": match["prefix"],
            "min": new_min,
            "max": new_max,
            "rules": match["rules"],
            "is_ex_code": match["is_ex_code"],
            "is_chapter": match["is_chapter"],
            "is_heading": match["is_heading"],
            "is_subheading": match["is_subheading"],
            "is_range": match["is_range"],
            "valid": match["valid"]
        }
        return obj

    def normalise_standard_chapter(self, chapter):
        # First, get the chapter's own rule-set
        chapter_found = False
        string_to_find = "chapter " + str(chapter)
        index = -1
        for rule_set in self.rule_sets:
            index += 1
            heading_string = rule_set["heading"].lower()
            heading_string = heading_string.replace("ex", "")
            heading_string = heading_string.replace("  ", " ")
            heading_string = heading_string.strip()
            if string_to_find == heading_string:
                chapter_found = True
                rule_set_rubric = RuleSetLegacy()
                rule_set_rubric.rules = rule_set["rules"]
                break

        # Then, get all headings that do not have rulesets
        # and assign the rulesets to them
        chapter_string = str(chapter).rjust(2, "0")
        for heading in g.all_headings:
            if heading[0:2] == chapter_string:
                matched = False
                for rule_set in self.rule_sets:
                    if rule_set["heading"] == heading:
                        matched = True
                        break
                if not matched:
                    obj = {
                        "heading": heading,
                        "description": g.all_headings[heading],
                        "subdivision": "",
                        "is_ex_code": False,
                        "prefix": "",
                        "min": heading + "000000",
                        "max": heading + "999999",
                        "rules": rule_set["rules"],
                        "valid": True,
                        "chapter": chapter
                    }
                    self.rule_sets.append(obj)

            if heading[0:2] > chapter_string:
                break

        if chapter_found:
            self.rule_sets.pop(index)

    def process_subdivisions(self):
        previous_ruleset = None
        for rule_set in self.rule_sets:
            if rule_set["subdivision"] != "":
                if previous_ruleset is not None:
                    rule_set["heading"] = previous_ruleset["heading"]
                    rule_set["min"] = previous_ruleset["min"]
                    rule_set["max"] = previous_ruleset["max"]
            previous_ruleset = rule_set

    def write_table(self):
        out_file = open(self.export_filepath, "w")
        json.dump({"rule_sets": self.rule_sets}, out_file, indent=6)
        out_file.close()
        dest = self.ott_path + self.export_filename + ".json"
        shutil.copy(self.export_filepath, dest)

    def kill_document(self):
        self.document = None

    def remove_working_nodes(self):
        for rule_set in self.rule_sets:
            try:
                del rule_set["description"]
            except Exception as e:
                pass

            try:
                del rule_set["headings"]
            except Exception as e:
                pass

            try:
                del rule_set["subheadings"]
            except Exception as e:
                pass

            try:
                del rule_set["is_ex_code"]
            except Exception as e:
                pass

            try:
                del rule_set["is_chapter"]
            except Exception as e:
                pass

            try:
                del rule_set["is_heading"]
            except Exception as e:
                pass

            try:
                del rule_set["is_subheading"]
            except Exception as e:
                pass

            try:
                del rule_set["is_range"]
            except Exception as e:
                pass

    def validate_table(self):
        if self.validate_tables:
            self.count_document_tables()
            self.count_document_table_row_cells()

    def count_document_table_row_cells(self):
        print("- Counting cells in each row for {file}".format(file=self.docx_filename))
        table = self.document.tables[0]
        cells = []
        cell_previous = "UNSPECIFIED"
        for i, row in enumerate(table.rows):
            cell1 = row.cells[0].text.strip()
            if cell1 == "":
                print("\nERROR: Empty cell in first column not permitted - row after {cell_previous}.\n".format(cell_previous=cell_previous))
                sys.exit()
            cell_previous = cell1

            cell_count = len(row.cells)
            if cell_count > 4:
                print("\nERROR: There must not be more than 4 columns in the table")
                sys.exit()

            cells.append(cell_count)
        cell_set = list(set(cells))

        if len(cell_set) > 1:
            print("\nERROR: Please ensure that all rows have the same number of columns and that they are of equal width.\n")
            sys.exit()

    def count_document_tables(self):
        print("- Counting tables for {file}".format(file=self.docx_filename))
        table_count = len(self.document.tables)
        if table_count > 1:
            print("\nERROR: Please ensure that there is only one table in the document.\n")
            sys.exit()
        elif table_count == 0:
            print("\nERROR: Please ensure that there a table in the document.\n")
            sys.exit()

    def check_coverage(self):
        print("- Checking that all commodity codes are covered for {file}".format(file=self.docx_filename))
        self.comm_code_omissions = []
        f = open(self.export_filepath)
        json_obj = json.load(f)
        previous_heading = ""
        for comm_code in g.all_codes:
            heading = comm_code[0:4]
            if heading == "8443":
                a = 1
            v = CommCodeValidator(comm_code, json_obj)
            ret = v.validate()
            if ret:
                self.comm_code_omissions.append(comm_code)
                print("No coverage for commodity code {comm_code}".format(comm_code=comm_code))

        print("Finished validating {file}".format(file=self.docx_filename))

    def validate_min_max_values(self):
        print("- Checking min max for {file}".format(file=self.docx_filename))
        issues = []
        for rule_set in self.rule_sets:
            if rule_set["min"] is None or \
                len(rule_set["min"]) != 10 or \
                "," in rule_set["min"] or \
                "and" in rule_set["min"] or \
                rule_set["max"] is None or \
                len(rule_set["max"]) != 10 or \
                "," in rule_set["max"] or \
                    "and" in rule_set["max"]:
                issues.append(rule_set["heading"])
                obj = {
                    "document": self.docx_filename,
                    "heading": rule_set["heading"],
                }
                g.min_max_issues.append(obj)

        if len(issues) > 0:
            s = "  - There are issues with null min and max values - please correct:\n\n  - "
            s += "\n  - ".join(issues)
            print(s)
            # sys.exit()
        else:
            print("  - All min max fine")
