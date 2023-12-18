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
        self.get_chapter_rule()
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
                        heading_obj = RuleSetHeadingWithSubHeadings(self.heading, self.rule_sets, self.chapter_rule)
                        self.heading_rule_sets += heading_obj.heading_rule_sets
                        self.processed = True
                        break
                    else:
                        if rule_set.is_ex_code:
                            # Add in both the rule set itself as well as the chapter rule
                            self.heading_rule_sets.append(rule_set)
                            if self.chapter_rule is not None:
                                chapter_rule_set = self.apply_heading_to_chapter_rule_set(self.chapter_rule, True)
                                self.heading_rule_sets.append(chapter_rule_set)
                        else:
                            if not rule_set.added_to_heading:
                                self.heading_rule_sets.append(rule_set)
                                rule_set.added_to_heading = True
                    self.processed = True

            if not self.processed:
                # The heading has not been found, therefore this must be a chapter rule
                if self.chapter_rule is not None:
                    rule_set = self.apply_heading_to_chapter_rule_set(self.chapter_rule, False)
                    self.heading_rule_sets.append(rule_set)

    def get_chapter_rule(self):
        """
        If it exists, get the rule applied to the chapter for this chapter
        This may not exist
        """
        self.chapter_rule = None
        for rule_set in self.rule_sets:
            if rule_set.is_chapter:
                self.chapter_rule = rule_set
                break

    def apply_heading_to_chapter_rule_set(self, rule_set, is_ex_code):
        """
        Make a copy of the chapter rule set, but replace the heading, min and max
        This is the residual rule, which is needed when the code is an ex ode, but
        you still inherit down the chapter-level rule
        """
        obj = copy.copy(rule_set)

        obj.min = self.min
        obj.max = self.max
        obj.is_chapter = False
        obj.is_heading = True
        return obj
