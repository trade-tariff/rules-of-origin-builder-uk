import re


class Rule(object):
    def __init__(self, rule_string):
        self.boolean_operator = None
        self.rule_class = []
        self.rule_string = rule_string.strip()
        self.rule_string_original = rule_string.strip()
        self.specific_processes = None
        self.double_dash = False
        self.process_rule()

    def process_rule(self):
        self.cleanse()
        self.get_rule_class()
        self.fix_punctuation()
        self.embolden_percentages()
        self.link_headings()
        self.get_specific_processes()
        self.get_double_dash()
        
    def get_specific_processes(self):
        if "specific process" in self.rule_string.lower():
            self.specific_processes = True
        else:
            self.specific_processes = False
            
    def get_double_dash(self):
        if "- -" in self.rule_string:
            self.double_dash = True

    def cleanse(self):
        self.rule_string = self.rule_string.strip()
        self.rule_string = re.sub(r'[ \t]+', " ", self.rule_string)
        self.rule_string = self.rule_string.replace(" %", "%")
        self.rule_string = re.sub(r'MaxNOM ([0-9]{1,3}%) \(EXW\)', "A maximum of \\1 of the ex-works price is made up of non-originating parts", self.rule_string)
        self.rule_string = re.sub(r'RVC ([0-9]{1,3})% \(FOB\)', "Your goods contain a Regional Value Content (RVC) of at least \\1% of the Free on Board (FOB) cost of the goods", self.rule_string)
        self.rule_string = re.sub(r'([^\(])FOB', "\\1Free on Board (FOB) cost", self.rule_string)

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
        
        self.rule_string = re.sub(r'\(([a-z])\)', "\n- (\\1)", self.rule_string)
        self.rule_string = re.sub(r'\(([i]{1,3})\)', "\n- (\\1)", self.rule_string)
        self.rule_string = self.rule_string.replace("Production from", "Your goods are produced from")
        self.rule_string = self.rule_string.replace("ex- works", "ex-works")
        self.rule_string = self.rule_string.replace("semi heated", "semi-heated")
        self.rule_string = self.rule_string.replace("whether or note", "whether or not")
        self.rule_string = self.rule_string.replace("Manufacture from materials of any heading", "Your goods are manufactured from materials of any tariff heading")
        
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

        self.rule_string = self.rule_string.replace("EXW", "ex-works price (EXW)")
        # self.rule_string = self.rule_string.replace("FOB", "Free on Board (FOB)")
        # self.rule_string = self.rule_string.replace("RVC", "Regional Value Content (RVC)")
        
    def embolden_percentages(self):
        self.rule_string = re.sub("([0-9]{1,3}\%)", "<b>\\1</b>", self.rule_string)
        
    def link_headings(self):
        self.rule_string = re.sub(" ([0-9]{1,5})([ ,;])", " <a href='/headings/\\1' target='_blank'>\\1</a>\\2", self.rule_string)
                
    def fix_punctuation(self):
        self.rule_string = self.rule_string.replace(" ,", ",")
        if self.rule_string[-1:] != ".":
            self.rule_string += "."
        

    def get_rule_class(self):
        self.rule_string_original = self.rule_string_original.replace("A change from any other heading", "CTH") # For Canada
        
        cth_string_full = "All non-originating materials used in the production of the good have undergone a change in tariff classification at the 4-digit level (tariff heading). "
        cth_string_partial = "All non-originating materials used in the production of the good have undergone a change in tariff classification at the 4-digit level (tariff heading)"
        tmp = self.rule_string.lower()
        if self.rule_string_original == "CTH":
            self.rule_string = cth_string_full
            self.rule_class = ["CTH"]

        elif "CTH" in self.rule_string_original:
            self.rule_string = self.rule_string.replace("CTH", cth_string_partial)
            self.rule_class = ["CTH"]
            if "in which" in tmp or "provided that" in tmp:
                self.rule_class.append("MaxNOM")

        elif self.rule_string_original == "CTSH":
            self.rule_string = "All non-originating materials used in the production of the good have undergone a change in tariff classification at the 6-digit level (subheading)."
            self.rule_class = ["CTSH"]

        elif self.rule_string_original == "CC":
            self.rule_string = "All non-originating materials used in the production of the good have undergone a change in tariff classification at the 2-digit level (chapter)."
            self.rule_class = ["CC"]
            
        elif "your goods are produced from non-originating materials of any heading" in tmp \
            or ("production from non-originating materials of any heading" in tmp and "except" not in tmp) :
            self.rule_class.append("Insufficient processing")
            if "in which" in tmp:
                self.rule_class.append("MaxNOM")

        elif "wholly obtained" in self.rule_string:
            self.rule_class = ["WO"]

        elif "RVC" in self.rule_string:
            self.rule_class = ["RVC"]

        elif "value of non-originating" in self.rule_string_original:
            self.rule_class = ["MaxNOM"]
            
        elif re.search("exceed[s]? [0-9]{1,3}% of", self.rule_string) and "value" in self.rule_string:
            self.rule_class = ["MaxNOM"]
        
        else:
            a = 1
            
        

    def as_dict(self):
        s = {
            "rule": self.rule_string,
            "original": self.rule_string_original,
            "class": self.rule_class,
            "operator": self.boolean_operator,
            "specific_processes": self.specific_processes,
            "double_dash": self.double_dash
        }
        return s
