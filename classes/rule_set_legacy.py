import re
import json
import os

from classes.normalizer import Normalizer
from classes.rule import Rule
from classes.error import Error
import classes.globals as g


class RuleSetLegacy(object):
    def __init__(self, row, row_index, footnotes_lookup):
        self.row_index = row_index
        self.hierarchy_divider = " ➔ "
        self.hierarchy_divider = " ▸ "
        self.heading = ""
        self.footnotes_lookup = footnotes_lookup
        self.subdivision = ""
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
        self.subheadings = []
        self.mixes_ex_and_non_ex = False
        self.contains_non_contiguous_and = False
        self.multiple_ands = False
        self.possible_missing_hyphens = False
        self.added_to_heading = False
        self.index = 0
        self.subdivision_adoption_requirement = 0

        self.headings = []
        self.subheadings = []
        self.is_heading = False
        self.is_subheading = False
        self.is_range = False
        self.original_heading = ""
        self.original_rule = ""
        self.original_rule2 = ""
        self.mark_for_deletion = False

        if row is not None:
            # A rule set essentially equates to a row on the table
            self.original_heading = row["original_heading"].strip()
            self.description = ""
            self.subdivision = row["description"].strip()
            self.subdivision = self.subdivision.replace("; except for:", "")
            self.subdivision = self.subdivision.replace(", except for:", "")
            self.subdivision = self.subdivision.replace("\n<b>", "<br><b>")

            # Run the corrections
            corrections_file = os.path.join(os.getcwd(), "resources", "data", "corrections.json")
            f = open(corrections_file)
            corrections = json.load(f)
            for correction in corrections:
                self.subdivision = self.subdivision.replace(correction["from"], correction["to"])

            self.original_rule = row["original_rule"].strip()
            self.original_rule = self.original_rule.replace("Manufacture;", "Manufacture:")
            self.original_rule2 = row["original_rule2"].strip()

            # Before
            self.original_rule = re.sub(r'\n-([^ ])', "\n- \\1", self.original_rule)
            self.original_rule = self.standarise_hyphens(self.original_rule)
            self.original_rule = self.deal_with_semicolons_in_manufacture_rules(self.original_rule)

            # Concatenate the two columns of rules into one
            if self.original_rule2 != "":
                self.original_rule2 = self.standarise_hyphens(self.original_rule2)
                self.original_rule2 = self.deal_with_semicolons_in_manufacture_rules(self.original_rule2)
                self.original_rule += ";\n\n"
                self.original_rule += "or\n\n" + self.original_rule2
                self.original_rule2 = re.sub(r'\n-([^ ])', "\n- \\1", self.original_rule2)

            self.process_heading()
            self.process_subdivision()

            self.process_rule()
            self.capture_parent_description()
            self.set_valid_status()

    def standarise_hyphens(self, s):
        s = s.replace("–", "-")  # en-dash
        s = s.replace("—", "-")  # em-dash
        return s

    def deal_with_semicolons_in_manufacture_rules(self, s):
        ret = s.strip()
        ret = ret.replace("Manufacture in which;", "Manufacture in which:")
        if ret.startswith("Manufacture:") or ret.startswith("Manufacture in which:"):
            if ret.count("Manufacture") == 1:
                ret = ret.replace(";", "")
            # ret = ret.replace("\n", "\n- ")
            # ret = ret.replace("\n- \n", "\n\n")
            # ret = ret.replace("\n- - ", "\n- ")

        return ret

    def capture_parent_description(self):
        self.original_rule = self.original_rule.strip()
        if self.original_rule == "As specified for split headings":
            self.original_rule = ""
        if self.original_rule == "" or self.original_rule == "-":
            g.parent_heading = self.subdivision

    def set_valid_status(self):
        for rule in self.rules:
            if rule["rule"] != "-" and rule["rule"] != "":
                self.valid = True
                break

    def process_heading(self):
        self.original_heading = self.original_heading.replace("chapter", "Chapter")
        self.original_heading = re.sub("\s+", " ", self.original_heading)
        self.original_heading = re.sub("Chapter 0([1-9])", "Chapter \\1", self.original_heading)
        self.original_heading = re.sub("([0-9]{2}.[0-9]{2}),\s?([0-9]{2}.[0-9]{2})", "\\1-\\2", self.original_heading)
        self.original_heading = re.sub("\s\([a-z]\)", "", self.original_heading)
        self.original_heading = re.sub("ex\s+([0-9]{1,2}) ([0-9]{1,2})", "ex \\1\\2", self.original_heading)
        self.original_heading = re.sub("([0-9]{4}) and ([0-9]{4})", "\\1 to \\2", self.original_heading)
        self.original_heading = self.original_heading.replace(u'\xa0', u' ')
        self.original_heading = self.original_heading.replace("–", "-")
        self.original_heading = self.original_heading.replace("ex ex", "ex ")
        self.original_heading = self.original_heading.replace("\n", " ")
        self.original_heading = self.original_heading.replace(";", ",")
        self.original_heading = re.sub("\s+", " ", self.original_heading)
        self.original_heading = re.sub("([0-9]{4}) ([0-9]{2})", "\\1\\2", self.original_heading)
        self.original_heading = re.sub(" {2,10}", " ", self.original_heading)

        # Check if the use of a comma could actually be replaced by a "to"
        # which would be the case if the items are consecutive
        if "," in self.original_heading:
            if "ex" not in self.original_heading:
                if "-" not in self.original_heading:
                    parts = self.original_heading.split(",")
                    if len(parts) == 2:
                        if int(parts[0].strip()) == int(parts[1].strip()) - 1:
                            self.original_heading = self.original_heading.replace(", ", " to ")

        # Check if the use of an "and" could actually be replaced by a "to"
        # which would be the case if the items are consecutive
        if "and" in self.original_heading:
            if "ex" not in self.original_heading:
                if "-" not in self.original_heading:
                    parts = self.original_heading.split("and")
                    parts = [part.replace(".", "").strip() for part in parts]
                    if len(parts) == 2:
                        p1 = int(parts[0].strip())
                        p2 = int(parts[1].strip())
                        if int(parts[0].strip()) == int(parts[1].strip()) - 1:
                            self.original_heading = self.original_heading.replace("and", "to")

        # Check for mixing of ex and non ex codes in the same rule cell
        temp_heading = self.original_heading.replace(".", "").replace(" - ", "-").replace(" to ", "-").replace(" and ", "-")
        if "-" in temp_heading:
            parts = temp_heading.split("-")
            parts = [part.replace(".", "").strip() for part in parts]
            ex_count = 0
            for part in parts:
                if "ex" in part:
                    ex_count += 1
            if ex_count != len(parts) and ex_count != 0:
                self.mixes_ex_and_non_ex = True

        # Check for non-contiguous "ands", and multiple "ands"
        temp_heading = self.original_heading.strip()
        if "and" in temp_heading:
            parts = temp_heading.split("and")
            parts = [part.strip().replace(".", "") for part in parts]
            if len(parts) > 2:
                self.multiple_ands = True
            else:
                p1 = int(parts[0].strip())
                p2 = int(parts[1].strip())
                if int(parts[0].strip()) != int(parts[1].strip()) - 1:
                    self.contains_non_contiguous_and = True

        # Check for rules where "Manufacture is mentioned, but there are no bulleted items"
        temp_rule = self.original_rule.strip()
        if temp_rule.startswith("Manufacture"):
            newline_count = temp_rule.count("\n")
            hyphen_count = temp_rule.count("-")
            however_count = temp_rule.count("However")
            or_count = temp_rule.count("or")
            if self.original_rule2 == "":
                if or_count == 0 and however_count == 0:
                    if (hyphen_count + 1) < newline_count:
                        self.possible_missing_hyphens = True
                        g.possible_missing_hyphens.append(self.original_heading)

        n = Normalizer()
        self.heading = n.normalize(self.original_heading)

        self.heading = self.heading.replace(".", "")
        self.heading = self.heading.replace(" - ", "-")
        self.heading = self.heading.replace(" to ", "-")

        self.get_heading_class()

        if self.mixes_ex_and_non_ex:
            g.mix_ex_non_ex_errors.append(self.original_heading)

        elif self.contains_non_contiguous_and:
            g.non_contiguous_and_errors.append(self.original_heading)

        elif self.multiple_ands:
            g.multiple_and_errors.append(self.original_heading)

        else:
            if "-" in self.original_heading or " to " in self.original_heading:
                self.determine_minmax_from_range()
            else:
                self.determine_minmax_from_single_term()

        self.heading = self.heading.replace("chapter ", "Chapter ")

    def get_heading_class(self):
        tmp = self.heading.lower()
        self.is_ex_code = False
        self.is_range = False
        self.is_chapter = False
        self.is_heading = False
        self.is_subheading = False

        # Check if this is the chapter and get the chapter number
        try:
            if "chapter" in tmp:
                self.is_chapter = True
                tmp2 = tmp.replace("ex", "").strip()
                tmp2 = tmp2.replace("chapter", "").strip()
                tmp2 = int(tmp2)
                self.chapter = tmp2
            else:
                tmp2 = tmp.replace("ex", "").strip()
                tmp2 = tmp2.strip()[0:2]
                tmp2 = int(tmp2)
                self.chapter = tmp2
        except Exception as e:
            if self.heading is None or self.heading == "":
                self.heading = "Not supplied"
            msg = "Get heading class error on heading {heading} on row {row_index} of the table. This is typically caused by the presence of " + \
                "an empty cell in the left-hand column. You may need to merge the cell with the cell above in order to process fhe file correctly."
            msg = msg.format(
                heading=self.heading,
                row_index=str(self.row_index)
            )
            Error(msg, show_additional_information=True, exception=e)

        # Check if this is an excode
        if "ex" in tmp:
            self.is_ex_code = True

        # Check if this is a range
        tmp = tmp.replace("-", " to ")
        # tmp = tmp.replace("and", " to ")
        tmp = tmp.replace("  ", " ")
        if "to" in tmp:
            self.is_range = True

        # Check if this is a heading / subheading
        tmp = tmp.replace("ex ex", "").strip()
        tmp = tmp.replace("ex", "").strip()
        if self.is_range:
            parts = tmp.split("to")
            part = parts[0].strip()
            if len(part) == 4:
                self.is_heading = True
            elif len(part) == 6:
                self.is_subheading = True
        else:
            if len(tmp) == 4:
                self.is_heading = True
            elif len(tmp) == 6:
                self.is_subheading = True

        if not self.is_ex_code:
            self.heading = tmp

    def determine_minmax_from_single_term(self):
        tmp = self.heading.lower()
        tmp = tmp.replace("ex ", "")
        if self.is_chapter:
            tmp = tmp.replace("chapter", "").strip().rjust(2, "0")
            self.min = tmp + "00000000"
            self.max = tmp + "99999999"
        elif self.is_heading:
            tmp = tmp.replace(" ", "").strip()
            self.headings.append(tmp)
            self.min = g.format_parts(tmp, 0)
            self.max = g.format_parts(tmp, 1)
        elif self.is_subheading:
            tmp = tmp.replace(" ", "").strip()
            self.headings.append(tmp[0:4])
            self.subheadings.append(tmp)
            self.min = g.format_parts(tmp, 0)
            self.max = g.format_parts(tmp, 1)

    def determine_minmax_from_range(self):
        if "-" in self.heading:
            parts = self.heading.split("-")
        elif "to" in self.heading:
            parts = self.heading.split("to")

        for i in range(0, len(self.parts)):
            parts[i] = parts[i].replace(" ", "")

        # Work out the min and max of a range
        index = 0
        for part in parts:
            if index == 0:
                self.min = g.format_parts(part, index)
            else:
                self.max = g.format_parts(part, index)
            index += 1

        if self.is_heading:
            # Work out the headings that this rule_set covers
            self.headings.append(parts[0].strip())
            tmp_min = int(parts[0])
            tmp_max = int(parts[1])
            proceed = True
            while proceed:
                tmp_min += 1
                str_min = str(tmp_min).rjust(4, "0").strip()
                if str_min in g.all_headings:
                    self.headings.append(str_min)
                if tmp_min == tmp_max:
                    proceed = False
        elif self.is_subheading:
            # Work out the subheadings that this rule_set covers
            self.subheadings.append(parts[0])
            tmp_min = int(parts[0])
            tmp_max = int(parts[1])
            proceed = True
            while proceed:
                tmp_min += 1
                str_min = str(tmp_min).rjust(6, "0")
                if str_min in g.all_subheadings:
                    self.subheadings.append(str_min)
                if tmp_min == tmp_max:
                    proceed = False

    def process_subdivision(self):
        # Standardise different hyphen characters
        self.subdivision = self.subdivision.replace("—", "–")
        self.subdivision = self.subdivision.replace("–", "-")
        self.subdivision = self.subdivision.replace("  ", " ")

        # Normalise additional characters
        n = Normalizer()
        self.subdivision = n.normalize(self.subdivision).strip()
        self.subdivision = self.subdivision.replace(" %", "%")
        self.subdivision = self.subdivision.replace("ex ex", "ex ")

        # Work out if this is a first, second or third tier subdivision
        # If it starts with "- - ", then it is third tier, and the two tiers above need to be pre-pended
        # If it starts with "- ", then it is second tier, and the one tier above needs to be pre-pended
        # Otherwise leave well alone
        self.subdivision = self.subdivision.strip("\n")
        if self.subdivision.startswith("- - "):
            self.subdivision_adoption_requirement = 2
        elif self.subdivision.startswith("- "):
            self.subdivision_adoption_requirement = 1

        for i in range(0, 2):
            self.subdivision = self.subdivision.strip("- ")

        self.subdivision = self.subdivision.replace("\nsee also", "\nSee also")
        self.subdivision_original = self.subdivision

    def process_footnotes(self):
        if len(self.footnotes_lookup) > 0:
            matches = re.findall(r"\([0-9]{1,2}\)", self.original_rule)
            for match in matches:
                index = re.sub(r"[\(\)]", "", match)
                if index in self.footnotes_lookup["footnotes"]:
                    self.original_rule = self.original_rule.replace(match, "(" + self.footnotes_lookup["footnotes"][index] + ")")
                else:
                    self.original_rule = self.original_rule.replace(match, "")
        else:
            self.original_rule = re.sub("\([0-9]{1,2}\)", "", self.original_rule)

        self.original_rule = self.original_rule.replace("from :", "from:")

    def process_rule(self):
        n = Normalizer()
        self.original_rule = n.normalize(self.original_rule)
        self.original_rule = re.sub("\t", " ", self.original_rule)
        self.original_rule = re.sub(" +", " ", self.original_rule)
        self.original_rule = self.original_rule.replace("ex ex", "ex ")
        self.original_rule = self.original_rule.replace("\nOr\n", "\nor\n", )
        self.original_rule = self.original_rule.replace(",\nor\n\n-", ", or\n-")
        self.original_rule = self.original_rule.replace(",\nor\n-", ", or\n-")
        self.original_rule = self.original_rule.replace(";\nor\n-", ", or\n-")
        self.original_rule = self.original_rule.replace(";\n- ", ",\n- ")

        # Do not delete footnotes
        self.process_footnotes()
        self.rules = []

        self.original_rule = self.original_rule.replace("; and", ", and")
        self.original_rule = re.sub("([^;]) or Manufacture", "\\1; or\nManufacture", self.original_rule)

        self.original_rule = self.original_rule.replace("\nor\nManufacture", "; or\nManufacture")
        self.original_rule = self.original_rule.replace(";;", ";")
        self.original_rule = self.original_rule.replace(";\nor", ";\n\nTEMPOR")
        self.original_rule = self.original_rule.replace(";\n\nor", ";\n\nTEMPOR")
        self.original_rule = self.original_rule.replace("\nor\n", ";\n\nor\n\n")
        self.original_rule = self.original_rule.replace("TEMPOR", "or")
        self.original_rule = self.original_rule.strip(";")
        rule_strings = self.original_rule.split(";")
        
        # Check on "Manufacture" appearing more than once:
        if self.original_rule.count("Manufacture") > 1 and len(rule_strings) == 1:
            g.multiple_manufacture.append(self.heading)

        for rule_string in rule_strings:
            rule = Rule(rule_string, self.heading)
            self.rules.append(rule.as_dict())

    def as_dict(self):
        my_dictionary = {
            "heading": self.heading,
            "chapter": self.chapter,
            "subdivision": self.subdivision,
            "min": self.min,
            "max": self.max,
            "rules": self.rules,
            "valid": self.valid
        }
        return my_dictionary

    def __eq__(self, other):
        """
        You can consider two rules as being the same, and therefore mergeable if:
        a) they have the same rules and the same heading
        b) and they are chapter level
        """
        return (self.rules == other.rules) and (self.heading == other.heading) and self.is_chapter and ("Any other product" not in self.subdivision) and ("Any other product" not in other.subdivision)
