all_headings = {}
all_subheadings = {}

parent_heading = ""

def format_parts(s, index):
    s = s.strip()
    l = len(s)
    if index == 0:
        s = s + (10 - l) * "0"
    else:
        s = s + (10 - l) * "9"

    return s

def is_numeric(s):
    s = s.strip()
    s = s.replace(" to ", "")
    s = s.replace("-", "")
    s = s.replace("\n", "")
    s = s.replace(".", "")
    s = s.replace(" ", "")
    ret = s.isnumeric()
    return ret
