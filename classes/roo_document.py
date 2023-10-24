import sys
import os
import json
import shutil
import csv
from dotenv import load_dotenv
# from docx import Document
from docx.api import Document

from classes.rule_set_modern import RuleSetModern
from classes.rule_set_legacy import RuleSetLegacy
from classes.comm_code_validator import CommCodeValidator
from classes.environment_variable import EnvironmentVariable
import classes.globals as g
import classes.functions as func


class RooDocument(object):
    def __init__(self, psr_source_file=None):
        self.psr_source_file = psr_source_file
        self.get_config()
        self.get_footnotes()
        self.get_all_rules_with_classes()
        self.get_commodities()
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
        self.sort_by_minmax()
        self.write_table()
        self.kill_document()

        if self.validate_commodities:
            self.check_coverage()
        if self.validate_min_max:
            self.validate_min_max_values()

        print("\nFinished processing {file}\n".format(file=self.docx_filename))

    def get_config(self):
        """ Works out paths and other configuration settings """

        load_dotenv('.env')
        self.resources_folder = os.path.join(os.getcwd(), "resources")
        self.source_folder = os.path.join(self.resources_folder, "source")
        self.export_folder = os.path.join(self.resources_folder, "export")
        self.config_folder = os.path.join(self.resources_folder, "config")
        self.defaults_folder = os.path.join(self.resources_folder, "defaults")

        # Get paths from environment variables
        self.preferred_code_list_file = EnvironmentVariable('preferred_code_list_file', 'string', permit_omission=True).value
        self.ott_prototype_path = EnvironmentVariable('ott_prototype_path', 'string', permit_omission=True).value
        self.all_rules_path = EnvironmentVariable('all_rules_path', 'string', permit_omission=True).value

        # Get features
        modern_documents = os.getenv('modern_documents')
        self.validate_tables = int(os.getenv('validate_tables'))
        self.modern_documents = modern_documents.split(",")
        self.validate_commodities = int(os.getenv('validate_commodities'))
        self.validate_min_max = int(os.getenv('validate_min_max'))

        if self.psr_source_file is not None:
            self.docx_filename = self.psr_source_file
            self.docx_filepath = os.path.join(self.source_folder, self.docx_filename)
        else:
            if len(sys.argv) > 1:
                self.docx_filename = sys.argv[1]
                self.docx_filepath = os.path.join(self.source_folder, self.docx_filename)
            else:
                print("Please supply an input document")
                sys.exit()

        # Export paths
        self.export_filename = self.docx_filename.replace(".docx", "").replace(" ", "-").lower()
        self.export_filename = self.export_filename.replace("_psr", "")
        self.export_filename = self.export_filename.replace("-psr", "")
        self.export_filepath = os.path.join(self.export_folder, self.export_filename) + ".json"

        self.config_filepath = os.path.join(self.config_folder, "config")
        self.config_filename = os.path.join(self.config_filepath, "config-" + self.export_filename + ".json")

    def get_footnotes(self):
        # Load footnotes
        self.footnotes = {}
        if os.path.exists(self.config_filename):
            f = open(self.config_filename)
            self.footnotes = json.load(f)

    def get_all_rules_with_classes(self):
        """ Function to pull in a list of all of the rules from the XI tariff and the
        classes of rule that are associated with each of these. These are used (for example) 
        in determining if a rule is wholly-obtained, and to populate the 'class' node
        in the resultant JSON file"""
        if not os.path.exists(self.all_rules_path):
            self.all_rules_path = os.path.join(self.defaults_folder, "all_rules.json")
        f = open(self.all_rules_path)
        g.all_rules_with_classes = json.load(f)
        f.close()

    def get_commodities(self):
        """ Function to retrieve all of the commodity codes (latest version) from an external CSV file
        """
        g.all_headings = {}
        g.all_subheadings = {}
        g.all_codes = []
        found_headings = []
        self.check_preferred_code_list_file_exists()
        with open(self.preferred_code_list_file) as csv_file:
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

    def check_preferred_code_list_file_exists(self):
        # Get default commodity code list file
        self.default_code_list_file = os.path.join(self.defaults_folder, "uk_commodities_2023-10-23.csv")
        if not os.path.exists(self.preferred_code_list_file):
            self.preferred_code_list_file = self.default_code_list_file

    def export_min_max(self):
        filename = os.path.join(self.resources_folder, "temp", "temp.csv")
        f = open(filename, "w")
        for rs in self.rule_sets:
            f.write("'" + rs["heading"] + "',")
            f.write(rs["min"] + ",")
            f.write(rs["max"] + "\n")
        f.close()

    def sort_by_minmax(self):
        error_count = 0
        self.export_min_max()
        for rs in self.rule_sets:
            if rs["min"] is None or rs["max"] is None:
                error_count += 1
                print("Max or min of 'None' found", rs["min"], rs["max"], rs["heading"])

        if error_count > 0:
            print("Aborting until issues are resolved in the source data file")

        self.rule_sets = sorted(self.rule_sets, key=self.sort_by_max)
        self.rule_sets = sorted(self.rule_sets, key=self.sort_by_min)

    def sort_by_max(self, list):
        return list["max"]

    def sort_by_min(self, list):
        return list["min"]

    def remove_invalid_entries(self):
        for i in range(len(self.rule_sets) - 1, -1, -1):
            rule_set = self.rule_sets[i]
            if rule_set["valid"] is False:
                self.rule_sets.pop(i)

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
                rule_set = RuleSetModern(row)
                self.rule_sets.append(rule_set.as_dict())

    def process_table_legacy(self):
        self.rule_sets = []
        for row in self.rows:
            rule_set = RuleSetLegacy(row, self.footnotes)
            if rule_set.valid:
                self.rule_sets.append(rule_set.as_dict())

        self.normalise_chapters()

    def normalise_chapters(self):
        for chapter in range(1, 98):
            all_ex_codes = True
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
        chapter_string = str(chapter).rjust(2, "0")
        print("Normalising complex chapter {chapter}".format(
            chapter=chapter_string
        ))
        # Get all the other rules in that chapter that are not the chapter heading
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

        # The matches variable captures all of the rules for the current chapter

        my_headings = {}
        for heading in g.all_headings:
            if heading[0:2] == chapter_string:
                my_headings[heading] = g.all_headings[heading]

        if contains_subheading is False:
            for heading in my_headings:
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

            # Finally, remove the old chapter code, as its value has been copied elsewhere now
            self.rule_sets.pop(chapter_index)
        else:
            # Firstly check for any headings under the chapter that have rules that are based on subheadings and not headings
            this_chapter_headings = []
            headings_with_subheading_rules = []
            headings_without_subheading_rules = []

            for heading in g.all_headings:
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

            # Remove any rulesets for the selected chapter, as these will all be replaced by the newly formed equivalents
            ruleset_count = len(self.rule_sets)
            for i in range(ruleset_count - 1, -1, -1):
                rule_set = self.rule_sets[i]
                if rule_set["chapter"] == chapter:
                    self.rule_sets.pop(i)

            # Then add the new rule sets onto the list
            self.rule_sets += additional_rulesets

    def normalise_standard_chapter(self, chapter):
        # The chapter has an ex code in its chapter definition
        # But there are no other ex codes withi the chapter
        rules_for_ex_chapter = []
        rulesets_to_pop = []
        rules_for_current_chapter = []
        # First, get the chapter's own rule-set
        string_to_find = "chapter " + str(chapter)
        string_to_find2 = "chapter 0" + str(chapter)
        index = -1
        for rule_set in self.rule_sets:
            if rule_set["chapter"] == chapter:
                rules_for_current_chapter.append(rule_set)
            index += 1
            heading_string = rule_set["heading"].lower()
            heading_string = heading_string.replace("ex", "")
            heading_string = heading_string.replace("  ", " ")
            heading_string = heading_string.strip()
            if (heading_string == string_to_find) or (heading_string == string_to_find2):
                rules_for_ex_chapter.append(rule_set)
                rulesets_to_pop.append(index)

        # Then, get all headings that do not have rulesets
        # and assign the rulesets to them
        chapter_string = str(chapter).rjust(2, "0")
        if (len(rules_for_ex_chapter)) > 0:
            for chapter_definition in rules_for_ex_chapter:
                for heading in g.all_headings:
                    if heading[0:2] == chapter_string:
                        matched = False
                        for rule_set in rules_for_current_chapter:  # self.rule_sets:
                            # if "5203" in rule_set["heading"] or "5204" in rule_set["heading"] :
                            #     a = 1
                            rule_matches_heading = func.range_matches_heading(rule_set["heading"], heading)
                            if rule_matches_heading:
                                matched = True
                                break
                        if not matched:
                            obj = {
                                "heading": heading,
                                "description": g.all_headings[heading],
                                "subdivision": chapter_definition["subdivision"],
                                "is_ex_code": False,
                                "min": heading + "000000",
                                "max": heading + "999999",
                                "rules": chapter_definition["rules"],
                                "valid": True,
                                "chapter": chapter
                            }
                            self.rule_sets.append(obj)

                    # When looping through the heading,
                    # break out of the loop when the heading
                    # exceeds the chapter
                    if heading[0:2] > chapter_string:
                        break

        if len(rulesets_to_pop) > 0:
            for i in range(len(rulesets_to_pop) - 1, -1, -1):
                ruleset_to_pop = rulesets_to_pop[i]
                self.rule_sets.pop(ruleset_to_pop)

    def copy_ruleset(self, match, new_min, new_max):
        obj = {
            "heading": match["heading"],
            "headings": match["headings"],
            "subheadings": match["subheadings"],
            "chapter": match["chapter"],
            "subdivision": match["subdivision"],
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
        dest = os.path.join(self.ott_prototype_path, self.export_filename + ".json")
        shutil.copy(self.export_filepath, dest)

    def kill_document(self):
        self.document = None

    def remove_working_nodes(self):
        for rule_set in self.rule_sets:
            try:
                del rule_set["description"]
            except Exception as e:
                print(e.args)

            try:
                del rule_set["headings"]
            except Exception as e:
                print(e.args)

            try:
                del rule_set["subheadings"]
            except Exception as e:
                print(e.args)

            try:
                del rule_set["is_ex_code"]
            except Exception as e:
                print(e.args)

            try:
                del rule_set["is_chapter"]
            except Exception as e:
                print(e.args)

            try:
                del rule_set["is_heading"]
            except Exception as e:
                print(e.args)

            try:
                del rule_set["is_subheading"]
            except Exception as e:
                print(e.args)

            try:
                del rule_set["is_range"]
            except Exception as e:
                print(e.args)

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
        for comm_code in g.all_codes:
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
