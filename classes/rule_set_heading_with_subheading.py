import copy
import classes.globals as g


class RuleSetHeadingWithSubHeadings(object):
    def __init__(self, heading, rule_sets, chapter_rule):
        self.heading = heading
        self.chapter_rule = chapter_rule
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
        for subheading in self.heading_subheadings:
            for rule_set in self.rule_sets:
                if subheading in rule_set.subheadings:
                    self.heading_rule_sets.append(rule_set)
                    rule_set.added_to_heading = True
                    if rule_set.is_ex_code:
                        if self.heading_ex_code_rule_set is not None:
                            residual_rule = self.copy_rule(self.heading_ex_code_rule_set, subheading, True)
                            # self.heading_rule_sets.append(residual_rule)
                        elif self.chapter_rule is not None:
                            residual_rule = self.copy_rule(self.chapter_rule, subheading[0:4], True)
                            self.heading_rule_sets.append(residual_rule)
                    else:
                        if self.heading_ex_code_rule_set is not None:
                            residual_rule = self.copy_rule(self.heading_ex_code_rule_set, subheading, True)
                            # self.heading_rule_sets.append(residual_rule)
                        else:
                            if self.chapter_rule is not None:
                                residual_rule = self.copy_rule(self.chapter_rule, subheading[0:4], True)
                                self.heading_rule_sets.append(residual_rule)                        
        for rule_set in self.rule_sets:
            if not rule_set.added_to_heading:
                self.heading_rule_sets.append(rule_set)

    def copy_rule(self, rule_set, subheading, is_ex_code):
        obj = copy.copy(rule_set)
        obj.min = subheading + "0" * (10 - len(subheading))
        obj.max = subheading + "9" * (10 - len(subheading))
        return obj


    def get_catalogue_headings_subheadings_for_heading(self):
        """
        Get the headings and subheadings from the catalogue for this chapter
        """
        self.heading_subheadings = {}

        for subheading in g.all_subheadings:
            if subheading[0:4] == self.heading:
                self.heading_subheadings[subheading] = g.all_subheadings[subheading]
