import jmespath


class CommCodeValidator(object):
    def __init__(self, comm_code, json_obj):
        self.comm_code = comm_code
        self.json_obj = json_obj

    def validate(self):
        if self.comm_code >= "9800000000":
            return None
        query = "rule_sets[?min <= '{code}' && max >= '{code}']".format(code=self.comm_code)
        expression = jmespath.compile(query)
        ret = expression.search(self.json_obj)
        if ret:
            return None
        else:
            return self.comm_code
