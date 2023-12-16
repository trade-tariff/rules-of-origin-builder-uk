import sys
import os


class Warning(object):
    def __init__(self, message):
        self.message = message
        print("\nERROR: {message}\n".format(
            message=message
        ))
