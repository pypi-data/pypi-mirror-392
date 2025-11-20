from rynput.validators import RegEx

class SemVer(RegEx):
    def __init__(self):
        self.regex = r"(\d+.){2}(\d+)"

    def query_string(self):
        return f"Semantic Version"