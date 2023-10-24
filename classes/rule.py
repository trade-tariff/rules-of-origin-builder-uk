import re
import json
import os
import classes.globals as g


class Rule(object):
    def __init__(self, rule_string, heading):
        self.heading = heading
        self.boolean_operator = None
        self.quota = False
        self.is_import = True
        self.is_export = True
        self.rule_class = []
        self.rule_string = rule_string.strip()
        self.rule_string_original = rule_string.strip()
        self.specific_processes = None
        self.double_dash = False
        self.process_rule()

    def process_rule(self):
        self.cleanse()
        self.get_rule_class()
        self.get_rule_class_lookup()
        self.get_specific_processes()
        self.fix_punctuation()
        self.embolden_percentages()
        self.hyperlink_headings()
        self.italicise_conjunctions()
        self.double_up_newlines()
        self.get_double_dash()
        self.reinsert_colons()
        self.final_formatting()
        self.check_for_quota()
        self.check_trade_direction()

    def check_for_quota(self):
        if "quota" in self.rule_string:
            self.quota = True

    def check_trade_direction(self):
        if "to the UK" in self.rule_string or "to the United Kingdom" in self.rule_string:
            self.is_import = True
            self.is_export = False
        if "from the UK" in self.rule_string or "from the United Kingdom" in self.rule_string:
            self.is_import = False
            self.is_export = True

    def final_formatting(self):
        self.rule_string = self.rule_string.replace(" and\n\n", " *and*\n\n")
        self.rule_string = self.rule_string.replace("()", "")
        self.rule_string = self.rule_string.replace(" .", ".")
        self.rule_string = self.rule_string.replace("%**%", "%**")

    def reinsert_colons(self):
        self.rule_string = self.rule_string.replace("Manufacture\n", "Manufacture:\n")
        self.rule_string = self.rule_string.replace("Manufacture in which\n", "Manufacture in which:\n")

    def double_up_newlines(self):
        self.rule_string = self.rule_string.replace("\n", "\n\n")
        self.rule_string = self.rule_string.replace("\n\n\n", "\n\n")

    def get_rule_class_lookup(self):
        self.rules_alphanumeric_only = self.alphanumeric_only(self.rule_string)
        try:
            my_classes = g.all_rules_with_classes[self.rules_alphanumeric_only]
            if len(my_classes) > 0:
                # Remove unspecified if this has previously been added
                if "Unspecified" in self.rule_class:
                    self.rule_class.remove("Unspecified")

                # Add in the classes that have been newly found by looking up in the XI data
                for item in my_classes:
                    items = item.upper().split("AND")
                    for item2 in items:
                        item2 = item2.strip()
                        item2 = item2.replace("(", "")
                        item2 = item2.replace(")", "")
                        if item2 not in self.rule_class:
                            self.rule_class.append(item2)
        except Exception as e:
            print(e.args)
            pass

    def get_specific_processes(self):
        if "specific process" in self.rule_string.lower():
            self.specific_processes = True
        else:
            self.specific_processes = False

    def alphanumeric_only(self, s):
        s2 = ''.join(ch for ch in s if ch.isalnum()).lower()
        return s2

    def get_double_dash(self):
        if "- -" in self.rule_string:
            self.double_dash = True

    def cleanse(self):
        self.rule_string = self.rule_string.replace("; and", ", and")
        self.rule_string = self.rule_string.replace("Manufacture in which;", "Manufacture in which:")
        self.rule_string = self.rule_string.replace("Manufacture;", "Manufacture:")
        self.rule_string = self.rule_string.replace("MaxNOM", "MAXNOM")
        self.rule_string = self.rule_string.strip()
        self.rule_string = re.sub(r'[ \t]+', " ", self.rule_string)
        self.rule_string = self.rule_string.replace(" %", "%")
        self.rule_string = self.rule_string.replace(" cm", "&nbsp;cm")
        self.rule_string = re.sub(r'MAXNOM ([0-9]{1,3}%) \(EXW\)', "A maximum of \\1 of the EXW is made up of non-originating parts (MaxNOM)", self.rule_string)
        self.rule_string = re.sub(r'RVC ([0-9]{1,3})% \(FOB\)', "Your goods contain a Regional Value Content (RVC) of at least \\1% of the Free on Board (FOB) cost of the goods", self.rule_string)
        self.rule_string = re.sub(r'([^\(])FOB', "\\1Free on Board (FOB) cost", self.rule_string)
        self.rule_string = re.sub("\t", " ", self.rule_string)

        self.rule_string = self.rule_string.replace("and/or", "and&nbsp;/&nbsp;or")

        if self.rule_string[0:4] == "and\n":
            self.boolean_operator = "and"

        if self.rule_string[0:5] == "and -":
            self.boolean_operator = "and"

        elif self.rule_string[0:3] == "or\n":
            self.boolean_operator = "or"

        elif self.rule_string[0:3] == "or ":
            self.boolean_operator = "or"

        self.rule_string = self.rule_string.removeprefix("and\n")
        self.rule_string = self.rule_string.removeprefix("and -")
        self.rule_string = self.rule_string.removeprefix("or\n")
        self.rule_string = self.rule_string.removeprefix("or ")
        self.rule_string = self.rule_string.removeprefix("- ")
        self.rule_string = self.rule_string.removesuffix(".")
        self.rule_string = self.rule_string.removeprefix("or ")

        self.rule_string = re.sub("\(([a-z])\) ", "\n- (\\1) ", self.rule_string)
        self.rule_string = re.sub("\(([a-z])\) ", "\\1) ", self.rule_string)
        # self.rule_string = re.sub(r'\(([i]{1,3})\)', "\n- (\\1)", self.rule_string)
        # self.rule_string = self.rule_string.replace("Production from", "Your goods are produced from")
        self.rule_string = self.rule_string.replace("ex- works", "ex-works")
        self.rule_string = self.rule_string.replace("semi heated", "semi-heated")
        self.rule_string = self.rule_string.replace("whether or note", "whether or not")
        self.rule_string = self.rule_string.replace("Manufacture form", "Manufacture from")
        self.rule_string = self.rule_string.replace("nonassembled", "non-assembled")

        self.rule_string = self.rule_string.replace("\n- \n- ", "\n- ")
        self.rule_string = self.rule_string.replace(": - ", ":\n- ")
        self.rule_string = self.rule_string.replace("; - ", ";\n- ")
        self.rule_string = self.rule_string.replace("; and - ", "; and \n- ")

        self.rule_string = self.rule_string.replace("\u2014", "-")
        if len(self.rule_string) > 0:
            self.rule_string = self.rule_string[0].upper() + self.rule_string[1:]

        self.rule_string = self.rule_string.replace("Weaving combined with making-up including cutting", "Weaving, combined with making-up, including cutting")
        self.rule_string = self.rule_string.replace("in column (3)", "in the rule above")
        self.rule_string = self.rule_string.replace("non originating", "non-originating")
        self.rule_string = self.rule_string.replace("shall not exceed", "must not exceed")

        # self.rule_string = self.rule_string.replace("EXW", "ex-works price (EXW)")
        # self.rule_string = self.rule_string.replace("FOB", "Free on Board (FOB)")
        # self.rule_string = self.rule_string.replace("RVC", "Regional Value Content (RVC)")
        if self.rule_string == ".":
            self.rule_string == ""

        corrections_file = os.path.join(os.getcwd(), "data", "corrections.json")
        f = open(corrections_file)
        corrections = json.load(f)
        for correction in corrections:
            self.rule_string = self.rule_string.replace(correction["from"], correction["to"])
        self.rule_string = self.rule_string.replace("- - ", "- ")
        self.rule_string = self.rule_string.replace(",\n- and\n\n", ", and\n")
        self.rule_string = self.rule_string.replace(",\n- and\n", ", and\n")

        # Remove deliberately inserted <b> tags and replace with markdown
        self.rule_string = self.rule_string.replace("<b>", "**")
        self.rule_string = self.rule_string.replace("</b>", "**")

        self.remove_footnote_references()

    def remove_footnote_references(self):
        self.rule_string = re.sub("\( ([0-9]{1,3}) \)", "", self.rule_string)

    def embolden_percentages(self):
        # self.rule_string = re.sub("([0-9]{1,3}),([0-9]{1,2})%", "\\1.\\2%", self.rule_string)
        # self.rule_string = re.sub("([0-9]{1,3}\.[0-9]{1,2}%)", "<b>\\1</b>", self.rule_string)
        # self.rule_string = re.sub("([0-9]{1,3}\%)", "<b>\\1</b>", self.rule_string)

        # Use this if we need to use markdown for bold
        self.rule_string = re.sub("([0-9]{1,3}),([0-9]{1,3}([ %]))", "\\1.\\2\\3", self.rule_string)
        self.rule_string = self.rule_string.replace(" per cent", "%")
        self.rule_string = self.rule_string.replace("  ", " ")
        self.rule_string = self.rule_string.replace(" %", "%")
        self.rule_string = re.sub("([0-9]{1,3}\.[0-9]{1,2}%)", "**\\1**", self.rule_string)
        self.rule_string = re.sub("([0-9]{1,3}),([0-9]{1,2})\%", "\\1.\\2%", self.rule_string)
        self.rule_string = re.sub(" ([0-9]{1,3}\%)", " **\\1**", self.rule_string)

    def italicise_conjunctions(self):
        return
        self.rule_string = re.sub("and/or", "and&nbsp;/&nbsp;or", self.rule_string)
        self.rule_string = re.sub("and&nbsp;/&nbsp;or", "*and&nbsp;/&nbsp;or*", self.rule_string)
        self.rule_string = re.sub(" and\n", " *and*\n", self.rule_string)
        self.rule_string = re.sub(" or\n", " *or*\n", self.rule_string)

    def hyperlink_headings(self):
        self.rule_string = self.rule_string.replace("headings No ", "heading ")
        self.rule_string = self.rule_string.replace("heading No ", "heading ")
        self.rule_string = self.rule_string.replace("heading Nos ", "heading ")
        self.rule_string = self.rule_string.replace("sub-heading", "subheading")
        self.rule_string = self.rule_string.replace("Sub-heading", "Subheading")
        self.rule_string = self.rule_string.replace("Chapter", "chapter")

        self.rule_string = re.sub(" ([0-9]{2}).([0-9]{2})([., ])", " \\1\\2\\3", self.rule_string)
        self.rule_string = re.sub(" ([0-9]{1,4}) through ([0-9]{1,4})([., ])", " \\1 to \\2\\3", self.rule_string)

        # Deal with subheadings
        self.rule_string = re.sub(" ([0-9]{4}).([0-9]{2})([., ])", " \\1\\2\\3", self.rule_string)
        self.rule_string = re.sub("subheadings", "subheading", self.rule_string)
        self.rule_string = re.sub(" subheading ([0-9]{4}) to ([0-9]{4})([., ])", " subheading \\1 to subheading \\2\\3", self.rule_string)

        for i in range(0, 4):
            self.rule_string = re.sub(" subheading ([0-9]{6}), ([0-9]{6})([., ])", " subheading \\1, subheading \\2\\3", self.rule_string)

        self.rule_string = re.sub(" subheading ([0-9]{6}) and ([0-9]{6})([., ])", " subheading \\1 and subheading \\2\\3", self.rule_string)
        self.rule_string = re.sub(" subheading ([0-9]{6}) and ([0-9]{6})$", " subheading \\1 and subheading \\2", self.rule_string)

        self.rule_string = re.sub(" subheading ([0-9]{6}) or ([0-9]{6})([., ])", " subheading \\1 or subheading \\2\\3", self.rule_string)
        self.rule_string = re.sub(" subheading ([0-9]{6}) or ([0-9]{6})$", " subheading \\1 or subheading \\2", self.rule_string)

        self.rule_string = re.sub(" subheading ([0-9]{6}) to ([0-9]{6})([., ])", " subheading \\1 to subheading \\2\\3", self.rule_string)
        self.rule_string = re.sub(" subheading ([0-9]{6}) to ([0-9]{6})$", " subheading \\1 to subheading \\2", self.rule_string)

        # self.rule_string = re.sub("([Ss]ubheading) ([0-9]{6})([ ,;.])", "<a href='/subheadings/\\2x0000-80' target='_blank'>\\1 \\2</a>\\3", self.rule_string)
        self.rule_string = re.sub("([Ss]ubheading) ([0-9]{6})([ ,;.])", "[\\1 \\2](/subheadings/\\2x0000-80)\\3", self.rule_string)  # Links in markdown
        self.rule_string = re.sub("x0000-80", "0000-80", self.rule_string)

        # Deal with headings
        self.rule_string = re.sub("headings", "heading", self.rule_string)
        self.rule_string = re.sub(" heading ([0-9]{4}) to ([0-9]{4})([., ])", " heading \\1 to heading \\2\\3", self.rule_string)

        for i in range(0, 4):
            self.rule_string = re.sub(" heading ([0-9]{4}), ([0-9]{4})([., ])", " heading \\1, heading \\2\\3", self.rule_string)

        self.rule_string = re.sub(" heading ([0-9]{4}) and ([0-9]{4})([., ])", " heading \\1 and heading \\2\\3", self.rule_string)
        self.rule_string = re.sub(" heading ([0-9]{4}) and ([0-9]{4})$", " heading \\1 and heading \\2", self.rule_string)

        self.rule_string = re.sub(" heading ([0-9]{4}) or ([0-9]{4})([., ])", " heading \\1 or heading \\2\\3", self.rule_string)
        self.rule_string = re.sub(" heading ([0-9]{4}) or ([0-9]{4})$", " heading \\1 or heading \\2", self.rule_string)

        self.rule_string = re.sub(" heading ([0-9]{4}) to ([0-9]{4})([., ])", " heading \\1 to heading \\2\\3", self.rule_string)
        self.rule_string = re.sub(" heading ([0-9]{4}) to ([0-9]{4})$", " heading \\1 to heading \\2", self.rule_string)

        self.rule_string = re.sub(" heading ([0-9]{4})$", " heading \\1", self.rule_string)

        self.rule_string = re.sub("([Hh]eading)(s*) ([0-9]{1,4})([ ,;.])", "[\\1\\2 \\3](/headings/\\3)\\4", self.rule_string)  # Links in markdown

        # Deal with chapters
        for i in range(0, 4):
            self.rule_string = re.sub(" chapter ([0-9]{1,2}), ([0-9]{1,2})([ ,;.])", " chapter \\1, chapter \\2\\3", self.rule_string)

        self.rule_string = re.sub("chapter ([0-9]{1,2}) to ([0-9]{1,2})([., ])", "chapter \\1 to chapter \\2\\3", self.rule_string)

        self.rule_string = re.sub("([Cc]hapter)(s*) ([0-9])([ ,;.])", "\\1\\2 0\\3\\4", self.rule_string)
        self.rule_string = re.sub("([Cc]hapter)(s*) ([0-9][0-9]) and ([1-9]) ", "\\1\\2 \\3 and 0\\4 ", self.rule_string)
        self.rule_string = re.sub("([Cc]hapter)(s*) ([0-9]{1,2}) and ([0-9]{1,2})", "[\\1 \\3](/chapters/\\3) and chapter \\4", self.rule_string)  # Links in markdown
        self.rule_string = re.sub("([Cc]hapter)(s*) ([0-9]{1,2}) or ([0-9]{1,2})", "[\\1 \\3](/chapters/\\3) or chapter \\4", self.rule_string)  # Links in markdown
        self.rule_string = re.sub("([Cc]hapter)(s*) ([0-9])([ ,;.])", "[\\1\\2  \\3](/chapters/0\\3)\\4", self.rule_string)  # Links in markdown
        self.rule_string = re.sub("([Cc]hapter)(s*) ([0-9]{1,2})([ ,;.])", "[\\1\\2 \\3](/chapters/\\3)\\4", self.rule_string)  # Links in markdown
        self.rule_string = re.sub("chapter 0([1-9])", "chapter \\1", self.rule_string)

        self.rule_string = re.sub(" +", " ", self.rule_string)

        # Add in non-breaking spaces
        self.rule_string = re.sub("chapter ([0-9]{1,2})", "chapter&nbsp;\\1", self.rule_string)
        self.rule_string = re.sub("subheading ([0-9]{6})", "subheading&nbsp;\\1", self.rule_string)
        self.rule_string = re.sub("heading ([0-9]{4})", "heading&nbsp;\\1", self.rule_string)

    def fix_punctuation(self):
        self.rule_string = self.rule_string.replace(" ,", ",").strip()
        if len(self.rule_string) > 0:
            if self.rule_string[-1:] != ".":
                self.rule_string += "."
        self.rule_string = self.rule_string.replace(",.", ",")

    def get_rule_class(self):
        self.rule_class = []
        self.rule_string_original = self.rule_string_original.replace("A change from any other heading", "CTH")  # For Canada

        cc_string = "<abbr title='Change of tariff chapter'>CC</abbr>: All non-originating materials used in the production of the good have undergone a change in tariff classification at the 2-digit level (chapter)"
        cth_string = "<abbr title='Change of tariff heading'>CTH</abbr>: All non-originating materials used in the production of the good have undergone a change in tariff classification at the 4-digit level (tariff heading)"

        tmp = self.rule_string.lower()
        if self.rule_string_original == "CTH":
            self.rule_string = cth_string
            self.rule_class = ["CTH"]

        elif "CTH" in self.rule_string_original:
            self.rule_string = self.rule_string.replace("CTH", cth_string)
            self.rule_class = ["CTH"]
            if "in which" in tmp or "provided that" in tmp:
                self.rule_class.append("MAXNOM")

        if self.rule_string_original == "WO":
            self.rule_string = "All goods must be wholly obtained."
            self.rule_class = ["WO"]

        if self.rule_string_original == "CTSH":
            self.rule_string = "<abbr title='Change of tariff subheading'>CTSH</abbr>: All non-originating materials used in the production of the good have undergone a change in tariff classification at the 6-digit level (subheading)."
            self.rule_class = ["CTSH"]

        if self.rule_string_original == "CC":
            self.rule_string = "<abbr title='Change of tariff chapter'>CC</abbr>: All non-originating materials used in the production of the good have undergone a change in tariff classification at the 2-digit level (chapter)."
            self.rule_class = ["CC"]

        elif "CC" in self.rule_string_original:
            self.rule_string = self.rule_string.replace("CC", cc_string)
            self.rule_class = ["CC"]

        # Deal with MaxNOMs
        self.rule_string = self.rule_string.replace("Max Nom", "MAXNOM")
        self.rule_string = self.rule_string.replace("MaxNom", "MAXNOM")
        self.rule_string = self.rule_string.replace("MaxNOM", "MAXNOM")
        self.rule_string = self.rule_string.replace("MAXNOM (EXW)", "MAXNOM of the EXW of the good")

        if "MAXNOM" in self.rule_string:
            self.rule_string = re.sub("([0-9]{1,3})% MAXNOM", "The maximum value of non-originating materials (MaxNOM) cannot exceed \\1%", self.rule_string)
            self.rule_class.append("MAXNOM")

        if "your goods are produced from non-originating materials of any heading" in tmp \
                or ("production from non-originating materials of any heading" in tmp and "except" not in tmp):
            self.rule_class.append("Insufficient processing")
            if "in which" in tmp:
                self.rule_class.append("MAXNOM")

        if "wholly obtained" in self.rule_string:
            self.rule_class = ["WO"]

        if "RVC" in self.rule_string:
            self.rule_class = ["RVC"]

        if "value of non-originating" in self.rule_string_original:
            self.rule_class = ["MAXNOM"]

        if re.search("exceed[s]? [0-9]{1,3}% of", self.rule_string) and "value" in self.rule_string:
            self.rule_class = ["MAXNOM"]

        self.rule_string = self.rule_string.replace("EXW", "ex-works price (EXW)")

    def as_dict(self):
        s = {
            "rule": self.rule_string,
            "class": self.rule_class,
            "footnotes": [],
            "operator": self.boolean_operator,
            "quota": self.quota,
            "import": self.is_import,
            "export": self.is_export,
        }

        # s = {
        #     "rule": self.rule_string,
        #     "class": self.rule_class,
        #     "operator": self.boolean_operator
        # }
        return s
