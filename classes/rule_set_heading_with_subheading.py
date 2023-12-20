import copy
import classes.globals as g


class RuleSetHeadingWithSubHeadings(object):
    def __init__(self, heading, rule_sets, whole_chapter_rules):
        self.heading = heading
        self.whole_chapter_rules = whole_chapter_rules
        self.heading_ex_code_rule_set = None
        self.heading_rule_sets = []
        self.get_catalogue_headings_subheadings_for_heading()

        # Get the rule sets that apply to this heading
        self.rule_sets = []
        for my_set in rule_sets:
            if self.heading in my_set.headings:
                self.rule_sets.append(my_set)

        self.check_ex_code_at_heading_level()
        self.find_matching_rule_sets()

    def check_ex_code_at_heading_level(self):
        for rule_set in self.rule_sets:
            if rule_set.is_subheading is False and rule_set.is_ex_code:
                self.heading_ex_code_rule_set = copy.copy(rule_set)
                break

    def find_matching_rule_sets(self):
        """
        Words go here
        """
        whole_chapter_rules_inserted = False
        for subheading in self.heading_subheadings:
            for rule_set in self.rule_sets:
                if subheading in rule_set.subheadings:
                    self.heading_rule_sets.append(rule_set)
                    rule_set.added_to_heading = True
                    if rule_set.is_ex_code:
                        if len(self.whole_chapter_rules) > 0:
                            if not whole_chapter_rules_inserted:
                                residual_rules = self.copy_rule(self.whole_chapter_rules, subheading[0:4])
                                self.heading_rule_sets += residual_rules
                                whole_chapter_rules_inserted = True
                    else:
                        if self.heading_ex_code_rule_set is None:
                            if len(self.whole_chapter_rules) > 0:
                                if not whole_chapter_rules_inserted:
                                    residual_rules = self.copy_rule(self.whole_chapter_rules, subheading[0:4])
                                    self.heading_rule_sets += residual_rules
                                    whole_chapter_rules_inserted = True

        for rule_set in self.rule_sets:
            if not rule_set.added_to_heading:
                self.heading_rule_sets.append(rule_set)

    def copy_rule(self, rule_sets, subheading):
        ret = []
        for rule_set in rule_sets:
            obj = copy.copy(rule_set)
            obj.min = subheading + "0" * (10 - len(subheading))
            obj.max = subheading + "9" * (10 - len(subheading))
            obj.headings = [subheading]
            # print(subheading)
            ret.append(obj)

        return ret


    def get_catalogue_headings_subheadings_for_heading(self):
        """
        Get the headings and subheadings from the catalogue for this chapter
        """
        self.heading_subheadings = {}

        for subheading in g.all_subheadings:
            if subheading[0:4] == self.heading:
                self.heading_subheadings[subheading] = g.all_subheadings[subheading]
