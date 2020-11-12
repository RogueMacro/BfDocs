class Parser:
    def __init__(self, tokens):
        self.pos = 0
        self.tokens = tokens

    @property
    def current(self):
        assert(self.pos > 0 && self.pos < len(tokens), "Invalid position")
        return tokens[pos]