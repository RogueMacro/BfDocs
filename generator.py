def run(filepath):
    with open(filepath, "r") as f:
        text = f.read()

    lexer = Lexer(text)
    tokens = lexer.lex()
    print("Tokens:", tokens)

    md_generator = MarkdownGenerator(tokens)
    md_generator.generate()


class MarkdownGenerator:
    def __init__(self, tokens):
        self.tokens = tokens

    def generate(self):
        pass


class Lexer:
    def __init__(self, text: str):
        self.pos = 0
        self.text = text
        self.tokens = []

    def is_valid_pos(self, pos) -> bool:
        return pos >= 0 and pos < len(self.text)

    def is_current_pos_valid(self) -> bool:
        return self.is_valid_pos(self.pos)

    def assert_pos(self) -> None:
        assert self.is_current_pos_valid(), "Invalid position"

    def lex(self) -> list:
        self.skip_usings()
        while self.is_current_pos_valid():
            self.search("namespace ")
            namespace = self.get_word()
            if len(namespace) > 0:
                self.tokens.append(f"NAMESPACE:{namespace}")

            self.search("class", "//")
            commentPos = self.pos - 2
            self.skip_whitespace()
            if self.match("<summary>"):
                self.pos = commentPos
                xml = self.read_documentation_comments()
                self.tokens.append(f"DOCS:{xml}")
            else:
                className = self.get_word()
                if len(className) > 0:
                    self.tokens.append(f"CLASS:{className}")
            self.next()

        return self.tokens

    def read_documentation_comments(self) -> str:
        xml = ""
        while self.match("//"):
            self.skip_if_match("//")
            xml += self.read_until_match("\n")
            self.skip_whitespace()
        return xml

    def read_until_match(self, match: str) -> str:
        string = ""
        while self.is_current_pos_valid() and not self.match(match):
            string += self.current
            self.next()
        return string

    def skip_usings(self) -> None:
        while self.match("using "):
            self.search(";")

    def skip_whitespace(self) -> None:
        while self.is_current_pos_valid() and self.current.isspace():
            self.next()

    def next(self) -> str:
        self.pos += 1
        return self.peek(0)

    def get_token(self, *end_of_token: str) -> str:
        token = ""
        while self.is_current_pos_valid() and not self.current in end_of_token:
            token += self.next()
        return token

    def get_word(self) -> str:
        word = ""
        while self.is_current_pos_valid() and not self.current.isspace():
            word += self.current
            self.next()
        return word

    @property
    def current(self):
        self.assert_pos()
        return self.peek(0)

    def peek(self, offset: int = 1):
        if not self.is_valid_pos(self.pos + offset):
            return None
        return self.text[self.pos + offset]

    def match(self, match: str) -> bool:
        if not self.is_valid_pos(self.pos + len(match)):
            return False

        for i in range(len(match)):
            if self.peek(i) != match[i]:
                return False
        return True

    def skip_if_match(self, *matches: str) -> bool:
        for match in matches:
            if self.match(match):
                self.pos += len(match)
                return True
        return False

    def search(self, *matches: str) -> bool:
        while self.is_current_pos_valid() and not self.skip_if_match(*matches):
            self.next()


run("Test.bf")
