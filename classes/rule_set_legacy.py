import re

from classes.normalizer import Normalizer
from classes.rule import Rule
import classes.globals as g


class RuleSetLegacy(object):
    def __init__(self, row = None):
        self.heading = ""
        self.subdivision = ""
        self.prefix = ""
        self.rule = ""
        self.is_ex_code = False
        self.parts = []
        self.rules = []
        self.is_subdivision = False
        self.min = None
        self.max = None
        self.valid = False
        self.chapter = -1
        self.headings = []

        if row is not None:
            # A rule set essentially equates to a row on the table
            self.original_heading = row["original_heading"].strip()
            self.description = row["description"].strip()
            self.original_rule = row["original_rule"].strip()
            self.original_rule2 = row["original_rule2"].strip()
            
            if self.original_heading == "2934":
                a = 1
                
            if self.original_rule2 != "":
                self.original_rule += ";\n"
                self.original_rule += "or " + self.original_rule2
                a = 1

            self.process_heading()
            self.process_rule()
            self.set_valid_status()
        
    def set_valid_status(self):
        for rule in self.rules:
            if rule["rule"] != "-" and rule["rule"] != "":
                self.valid = True
                break


    def process_heading(self):
        self.original_heading = self.original_heading.replace(u'\xa0', u' ')
        self.original_heading = self.original_heading.replace("ex ex", "ex ")
        self.original_heading = self.original_heading.replace("  ", " ")
        if "ex" in self.original_heading:
            self.is_ex_code = True
        else:
            self.is_ex_code = False

        n = Normalizer()
        self.heading = n.normalize(self.original_heading)
        self.heading = self.heading.replace(".", "")
        self.heading = self.heading.replace(" - ", "-")
        self.heading = self.heading.replace(" to ", "-")
        if ":" in self.original_heading or self.original_heading.startswith("-"):
            self.heading = self.heading.removeprefix("- ")
            self.heading = self.heading.removesuffix(":")
            self.subdivision = self.heading
            self.subdivision = self.subdivision.replace("-", "\n-")
            if self.subdivision.startswith("\n"):
                self.subdivision.lstrip()
            if self.subdivision == "Other":
                self.subdivision = "Others"
            self.heading = ""
            self.is_subdivision = True
        else:
            if "-" in self.original_heading or " to " in self.original_heading :
                self.get_range()
            else:
                self.extend_range_from_single()
        pass
        self.get_chapter()
        
    def get_chapter(self):
        tmp = self.heading.lower()
        tmp = tmp.replace("ex", "").strip()
        if "chapter" in tmp:
            tmp = tmp.replace("chapter", "").strip()
            tmp = int(tmp)
            self.chapter = tmp
        elif self.is_numeric(tmp):
            tmp = tmp[0:2]
            tmp = int(tmp)
            self.chapter = tmp
            a = 1
        else:
            a = 1

    def extend_range_from_single(self):
        self.headings = []
        if "ex" in self.heading:
            a = 1
        tmp = self.heading.lower()
        tmp = tmp.replace("ex ", "")
        if "chapter" in tmp:
            tmp = tmp.replace("chapter", "")
            tmp = tmp.strip()
            tmp = tmp.rjust(2, "0")
            self.min = tmp + "00000000"
            self.max = tmp + "99999999"
        else:
            tmp = tmp.replace(" ", "").strip()
            self.headings.append(tmp)
            self.min = self.format_parts(tmp, 0)
            self.max = self.format_parts(tmp, 1)

    def get_range(self):
        if '5603 11' in self.heading:
            a = 1
        if "-" in self.heading:
            self.parts = self.heading.split("-")
        elif "to" in self.heading:
            self.parts = self.heading.split("to")
            
        for i in range(0, len(self.parts)):
            self.parts[i] = self.parts[i].replace(" ", "")

        index = 0
        for part in self.parts:
            if index == 0:
                self.min = self.format_parts(part, index)
            else:
                self.max = self.format_parts(part, index)
            index += 1
            
        self.headings = []
        self.headings.append(self.parts[0])
        tmp_min = int(self.parts[0])
        tmp_max = int(self.parts[1])
        proceed = True
        while proceed:
            tmp_min += 1
            str_min = str(tmp_min).rjust(4, "0")
            if str_min in g.all_headings:
                self.headings.append(str_min)
            if tmp_min == tmp_max:
                proceed = False
        a = 1

    def process_rule(self):
        n = Normalizer()
        self.original_rule = n.normalize(self.original_rule)
        self.original_rule = self.original_rule.replace("ex ex", "ex ")
        self.original_rule = re.sub("\([0-9]{1,2}\)", "", self.original_rule)
        self.rules = []
        tmp = self.original_rule.lower()
        # if self.original_heading == "04.01-04.10":
        if "62.17" in self.original_heading:
            a = 1

        if "production in which:" in tmp:
            self.original_rule = self.original_rule.replace("Production in which:\n", "")
            self.original_rule = self.original_rule.replace("Production in which: ", "")
            self.rule_strings = self.original_rule.split(";")
            self.prefix = "Production in which:"
            a = 1
        # elif "provided that" in tmp:
        #     self.rule_strings = [self.original_rule]
        else:
            self.rule_strings = self.original_rule.split(";")

        for rule_string in self.rule_strings:
            rule = Rule(rule_string)
            self.rules.append(rule.as_dict())

    def as_dict(self):
        s = {
            "heading": self.heading,
            "headings": self.headings,
            "description": self.description,
            "subdivision": self.subdivision,
            "is_ex_code": self.is_ex_code,
            "prefix": self.prefix,
            "min": self.min,
            "max": self.max,
            "rules": self.rules,
            "valid": self.valid,
            "chapter": self.chapter
        }
        return s

    @staticmethod
    def format_parts(s, index):
        s = s.strip()
        s = s.replace(" ", "")
        l = len(s)
        if index == 0:
            s = s + (10 - l) * "0"
        else:
            s = s + (10 - l) * "9"

        return s

    @staticmethod
    def is_numeric(s):
        s = s.strip()
        s = s.replace(" to ", "")
        s = s.replace("-", "")
        s = s.replace("\n", "")
        s = s.replace(".", "")
        s = s.replace(" ", "")
        ret = s.isnumeric()
        return ret