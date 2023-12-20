import sys
import os


class Error(object):
    """
    Used to print errors that stop execution
    """
    def __init__(self, message, show_additional_information=True, exception=None):
        self.message = message
        print("\nERROR: {message}\n".format(
            message=message
        ))
        if show_additional_information:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error", exc_type, "in file", fname, "at line", exc_tb.tb_lineno, "\n")
        sys.exit()
