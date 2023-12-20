import copy
import classes.globals as g
from classes.rule_set_heading_with_subheading import RuleSetHeadingWithSubHeadings


class RuleSetHeading(object):
    def __init__(self, heading, rule_sets):
        self.append_to_rule_sets = False
        self.heading = heading
        self.rule_sets = rule_sets
        self.heading_rule_sets = []
        self.processed = False

        self.check_for_subheadings()
        self.get_min_max()
        self.get_whole_chapter_rule()
        self.find_matching_rule_sets()

    def check_for_subheadings(self):
        self.has_subheadings = False
        for rule_set in self.rule_sets:
            if self.heading in rule_set.headings:
                if len(rule_set.subheadings) > 0:
                    self.has_subheadings = True

    def get_min_max(self):
        """
        Get the min and max values for this heading
        """
        self.min = self.heading + "000000"
        self.max = self.heading + "999999"

    def find_matching_rule_sets(self):
        """
        Find the rule sets that match the heading, and then process them
        """
        if len(self.rule_sets) > 0:
            for rule_set in self.rule_sets:
                if self.heading in rule_set.headings:
                    # If there is an ex-code in the heading, check to see if there are also subheadings
                    if self.has_subheadings:
                        # If there are subheadings, then we need to process all of the rules for the heading together
                        heading_obj = RuleSetHeadingWithSubHeadings(self.heading, self.rule_sets, self.whole_chapter_rules)
                        self.heading_rule_sets += heading_obj.heading_rule_sets
                        self.processed = True
                        break
                    else:
                        if rule_set.is_ex_code:
                            # Add in both the rule set itself as well as the chapter rule
                            self.heading_rule_sets.append(rule_set)
                            if len(self.whole_chapter_rules) > 0:
                                if self.heading not in g.residual_added:
                                    # print("Adding")
                                    whole_chapter_rule_sets = self.apply_heading_to_chapter_rule_sets(self.whole_chapter_rules, self.heading, None, True)
                                    self.heading_rule_sets += whole_chapter_rule_sets
                                    g.residual_added.append(self.heading)
                                # self.heading_rule_sets.append(whole_chapter_rule_set)
                        else:
                            if not rule_set.added_to_heading:
                                self.heading_rule_sets.append(rule_set)
                                rule_set.added_to_heading = True
                    self.processed = True

            if not self.processed:
                # The heading has not been specifcally found with a rule, therefore this must be a chapter rule
                # Add in all the chapter rules
                if len(self.whole_chapter_rules) > 0:
                    rule_sets = self.apply_heading_to_chapter_rule_sets(self.whole_chapter_rules, self.heading, None, False)
                    # self.heading_rule_sets.append(rule_set)
                    self.heading_rule_sets += rule_sets

    def get_whole_chapter_rule(self):
        """
        If it exists, get the rule applied to the chapter for this chapter
        This may not exist, and there may be more than one chapter rule
        """
        self.whole_chapter_rules = []
        self.whole_chapter_rule = None
        for rule_set in self.rule_sets:
            if rule_set.is_chapter:
                self.whole_chapter_rule = rule_set
                self.whole_chapter_rules.append(rule_set)
                # break

    def apply_heading_to_chapter_rule_set(self, rule_set, heading=None, subheading=None):
        """
        Make a copy of the chapter rule set, but replace the heading, min and max
        This is the residual rule, which is needed when the code is an ex ode, but
        you still inherit down the chapter-level rule
        """
        obj = copy.copy(rule_set)

        obj.min = self.min
        obj.max = self.max
        obj.is_chapter = True
        obj.is_heading = True

        if heading == None:
            obj.headings = []
        else:
            obj.headings = [heading]

        if subheading == None:
            obj.subheadings = []
        else:
            obj.subheadings = [subheading]
        return obj

    def apply_heading_to_chapter_rule_sets(self, rule_sets, heading=None, subheading=None, apply_other_label=False):
        """
        Make a copy of the chapter rule set, but replace the heading, min and max
        This is the residual rule, which is needed when the code is an ex ode, but
        you still inherit down the chapter-level rule
        """
        ret = []
        for rule_set in rule_sets:
            obj = copy.copy(rule_set)

            obj.min = self.min
            obj.max = self.max
            # obj.is_chapter = False
            obj.is_chapter = True
            obj.is_heading = True
            
            if apply_other_label:
                if heading is not None:
                    obj.subdivision = "Any other product from heading {heading}".format(
                        heading=heading
                    )

            if heading == None:
                obj.headings = []
            else:
                obj.headings = [heading]

            if subheading == None:
                obj.subheadings = []
            else:
                obj.subheadings = [subheading]

            ret.append(obj)
        return ret
