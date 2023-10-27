import re

from classes.normalizer import Normalizer
from classes.rule import Rule


class RuleSetModern(object):
    def __init__(self, row):
        # A rule set essentially equates to a row on the table
        self.original_heading = row["original_heading"].strip()
        self.original_rule = row["original_rule"].strip()

        self.heading = ""
        self.subdivision = ""
        self.rule = ""
        self.parts = []
        self.is_subdivision = False
        self.min = None
        self.max = None
        self.valid = False

        self.process_heading()
        self.process_rule()
        self.set_valid_status()

    def set_valid_status(self):
        for rule in self.rules:
            if rule["rule"] != "-" and rule["rule"] != "":
                self.valid = True
                break

    def process_heading(self):
        n = Normalizer()
        self.heading = n.normalize(self.original_heading)
        self.heading = self.heading.replace(".", "")
        self.heading = self.heading.replace(" - ", "-")
        self.heading = re.sub("([0-9]) to ([0-9])", "\\1 - \\2", self.heading)
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
            if "-" in self.original_heading:
                self.determine_minmax_from_range()
            else:
                self.determine_minmax_from_single_term()
        pass

    def determine_minmax_from_single_term(self):
        self.min = self.format_parts(self.heading, 0)
        self.max = self.format_parts(self.heading, 1)

    def determine_minmax_from_range(self):
        self.parts = self.heading.split("-")
        index = 0
        for part in self.parts:
            if index == 0:
                self.min = self.format_parts(part, index)
            else:
                self.max = self.format_parts(part, index)
            index += 1

    def process_rule(self):
        n = Normalizer()
        self.original_rule = n.normalize(self.original_rule)
        self.rules = []
        self.original_rule = self.original_rule.strip(";")
        self.original_rule = self.original_rule.replace("; and", ", and")
        self.original_rule = self.original_rule.replace("ICCAT", "I.C.C.A.T.")
        self.rule_strings = self.original_rule.split(";")

        for rule_string in self.rule_strings:
            rule = Rule(rule_string, self.original_heading)
            self.rules.append(rule.as_dict())

    def as_dict(self):
        s = {
            "heading": self.heading,
            "subdivision": self.subdivision,
            "min": self.min,
            "max": self.max,
            "rules": self.rules,
            "valid": self.valid
        }
        return s

    @staticmethod
    def format_parts(s, index):
        if "ex" in s:
            s = s.replace("ex.", "")
            s = s.replace("ex", "")
        s = s.strip()
        length = len(s)
        if index == 1:
            if length == 6:
                if s[4:6] == "00":
                    s = s[0:4] + "99"
        if index == 0:
            s = s + (10 - length) * "0"
        else:
            if length > 4:
                if s[-1] == "0":
                    s = s[:-1] + "9"
            s = s + (10 - length) * "9"

        return s

    @staticmethod
    def is_numeric(p):
        s = p.strip()
        s = s.replace(" to ", "")
        s = s.replace("-", "")
        s = s.replace("\n", "")
        s = s.replace(".", "")
        s = s.replace(" ", "")
        ret = s.isnumeric()
        return ret
