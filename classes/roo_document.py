import sys
import os
import json
import shutil

from dotenv import load_dotenv
from docx import Document
from docx.api import Document
from classes.rule_set import RuleSet


class RooDocument(object):
    def __init__(self):
        self.get_environment()
        self.get_arguments()
        self.open_document()
        self.read_table()
        self.process_table()
        self.process_subdivisions()
        self.write_table()
        self.kill_document()

    def get_environment(self):
        load_dotenv('.env')
        self.source_folder = os.getenv('source_folder')
        
    def get_arguments(self):
        if len(sys.argv) > 1:
            self.docx_filename = sys.argv[1]
            self.docx_filepath = os.path.join(self.source_folder, self.docx_filename)
        else:
            print("Please supply an input document")
            sys.exit()

        self.export_folder = os.path.join(os.getcwd(), "export")
        self.export_filename = self.docx_filename.replace(".docx", "").replace(" ", "_").lower()
        self.export_filepath = os.path.join(self.export_folder, self.export_filename) + ".json"

    def open_document(self):
        self.document = Document(self.docx_filepath)

    def read_table(self):
        table = self.document.tables[0]
        rename_keys = {
            "Classification": "original_heading",
            "PSR": "original_rule"
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
                    a = 1
                self.rows.append(item)

        a = 1
        
    def process_table(self):
        self.rule_sets = []
        for row in self.rows:
            if "Section" in row["original_heading"]:
                pass
            elif "SECTION" in row["original_heading"]:
                pass
            elif "Chapter" in row["original_heading"]:
                pass
            else:
                rule_set = RuleSet(row)
                self.rule_sets.append(rule_set.as_dict())
                a = 1
                pass
        a = 1
        
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
        json.dump({ "rule_sets": self.rule_sets}, out_file, indent = 6)
        out_file.close()

        dest = "/Users/mattlavis/sites and projects/1. Online Tariff/ott prototype/app/data/roo/uk/psr_new/" + self.export_filename + ".json"
        shutil.copy(self.export_filepath, dest)

    def kill_document(self):
        self.document = None

