import sys
import os


class Warning(object):
    """
    Used to print warnings that do not stop execution
    """
    def __init__(self, message):
        self.message = message
        print("\nERROR: {message}\n".format(
            message=message
        ))
