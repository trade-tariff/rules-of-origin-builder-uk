import sys


class Error(object):
    def __init__(self, message):
        self.message = message
        print("\nERROR: {message}.\n".format(
            message=message
        ))
        sys.exit()
