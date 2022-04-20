all_headings = {}
all_subheadings = {}

def format_parts(s, index):
    s = s.strip()
    l = len(s)
    if index == 0:
        s = s + (10 - l) * "0"
    else:
        s = s + (10 - l) * "9"

    return s