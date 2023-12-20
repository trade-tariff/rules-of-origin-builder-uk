import copy
import classes.globals as g
from classes.rule_set_heading import RuleSetHeading
from classes.rule_set_legacy import RuleSetLegacy


class RuleSetChapter(object):
    def __init__(self, chapter_index, rule_sets):
        self.chapter_index = chapter_index
        self.chapter_rule_set_has_ex_code = False
        self.has_ex_codes = False
        self.all_ex_codes = True
        self.has_subheadings = False
        self.whole_chapter_rule_count = 0

        self.get_rule_sets_for_this_chapter(rule_sets)
        if len(self.rule_sets) > 1 and (len(self.rule_sets) > len(self.chapter_rule_sets)):
            self.check_for_ex_codes()
            self.check_for_subheadings()
            self.get_catalogue_headings_subheadings_for_chapter()
            self.process_headings()
            self.merge_contiguous_identical_rules()
        else:
            self.chapter_rule_sets = self.rule_sets

    def get_rule_sets_for_this_chapter(self, rule_sets):
        """
        Filters the list of rules to just those that belong to this chapter
        """
        self.rule_sets = []
        self.chapter_rule_sets = []
        for rule_set in rule_sets:
            if rule_set.chapter == self.chapter_index:
                self.rule_sets.append(rule_set)
                if rule_set.is_chapter:
                    self.chapter_rule_sets.append(rule_set)
                    self.whole_chapter_rule_count += 1


    def check_for_ex_codes(self):
        """
        Checks if there are any ex codes in the chapter, and also
        if the chapter is made up entirely of ex codes, also if the 
        chapter ruleset is an ex-code rule set
        """
        for rule_set in self.rule_sets:
            if rule_set.is_ex_code:
                self.has_ex_codes = True
                if rule_set.is_chapter:
                    self.chapter_rule_set_has_ex_code = True
            else:
                self.all_ex_codes = False

    def check_for_subheadings(self):
        """
        Checks if there are any subheadings in the chapter
        """
        for rule_set in self.rule_sets:
            if len(rule_set.subheadings) > 0:
                self.has_subheadings = True
                break

    def get_catalogue_headings_subheadings_for_chapter(self):
        """
        Get the headings and subheadings from the catalogue for this chapter
        """
        self.chapter_headings = {}
        self.chapter_subheadings = {}

        chapter_string = str(self.chapter_index).rjust(2, "0")
        for heading in g.all_headings:
            if heading[0:2] == chapter_string:
                self.chapter_headings[heading] = g.all_headings[heading]

        for subheading in g.all_subheadings:
            if subheading[0:2] == chapter_string:
                self.chapter_subheadings[subheading] = g.all_subheadings[subheading]

    def process_headings(self):
        """
        Process all headings in this chapter
        """
        self.chapter_rule_sets = []
        for chapter_heading in self.chapter_headings:
            rule_set_heading = RuleSetHeading(chapter_heading, self.rule_sets)
            self.chapter_rule_sets += rule_set_heading.heading_rule_sets
        
    def merge_contiguous_identical_rules(self):
        """
        Where multiple chapter residual rules have been applied that are contiguous and identical
        these need to be merged to reduce the size of the JSON file.
        """
        # Apply an index to the rules, so that they can be sorted correctly.
        rule_set_count = len(self.chapter_rule_sets)
        for index in range(rule_set_count - 1, -1, -1):
            current_rule_set = self.chapter_rule_sets[index]
            if current_rule_set.is_chapter:
                current_rule_set.index = 9999
            else:
                current_rule_set.index = index

        pre_sorted = False
        if self.whole_chapter_rule_count > 1 and len(self.rule_sets) > self.whole_chapter_rule_count:
            self.chapter_rule_sets.sort(key=lambda x: x.rules[0]["rule"], reverse=False)
            self.chapter_rule_sets.sort(key=lambda x: x.heading, reverse=False)
            pre_sorted = True

        next_rule_set = RuleSetLegacy(None, None, None)
        for index in range(rule_set_count - 1, -1, -1):
            current_rule_set = self.chapter_rule_sets[index]
            if current_rule_set.is_heading:
                if next_rule_set.is_heading:
                    if current_rule_set == next_rule_set:
                        self.chapter_rule_sets[index + 1].mark_for_deletion = True
                        self.chapter_rule_sets[index].max = next_rule_set.max
            
            next_rule_set = copy.copy(current_rule_set)
        
        # Delete all that are marked for deletion
        for index in range(rule_set_count - 1, -1, -1):
            rule_set = self.chapter_rule_sets[index]
            if rule_set.mark_for_deletion:
                self.chapter_rule_sets.pop(index)

        if pre_sorted:
            self.chapter_rule_sets.sort(key=lambda x: x.index, reverse=False)
        else:
            self.chapter_rule_sets.sort(key=lambda x: x.index, reverse=False)
            self.chapter_rule_sets.sort(key=lambda x: x.heading, reverse=False)
