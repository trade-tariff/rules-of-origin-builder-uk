import logging


def range_matches_heading(my_range, my_heading):
    potential_matches = []
    if "-" in my_range:
        parts = my_range.split("-")
        if len(parts[0]) == len(parts[1]):
            difference = to_integer(parts[1]) - to_integer(parts[0])
            potential_matches.append(parts[0])
            for i in range(1, difference + 1):
                potential_matches.append(str(to_integer(parts[0]) + i))
            if str(my_heading) in potential_matches:
                matched = True
            else:
                matched = False
        else:
            matched = False
    else:
        if my_heading == my_range:
            matched = True
        else:
            matched = False

    return matched


def to_integer(s):
    try:
        i = int(s)
    except Exception as e:
        logging.debug('to_integer', e.args)
        i = 0
    return i
