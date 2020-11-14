def run(filepath):
    with open(filepath, "r") as f:
        text = f.read()

    lexer = Lexer(text)
    tokens = lexer.lex()
    print("Tokens:", tokens)

    generate_markdown(tokens)

def generate_markdown(tokens):
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
            nspos = self.find("namespace ")
            nxtpos = self.find("class ", "//")
            if self.find("namespace ") < self.find("class ", "//"):
                self.skip_until_match("namespace ")
                namespace = self.get_word(".")
                if len(namespace) > 0:
                    self.tokens.append(f"NAMESPACE:{namespace}")
                    self.skip_until_match("{")
            else:
                self.lex_docifyable()

        possible_duplicates = True
        while possible_duplicates:
            possible_duplicates = False
            for i, token in enumerate(self.tokens):
                if token.startswith("DOCS") and i + 1 < len(self.tokens) and not self.tokens[i+1].startswith("CLASS") and not self.tokens[i+1].startswith("METHOD"):
                    del self.tokens[i]
                    possible_duplicates = True
                    break

        ends_needed = 0
        for token in self.tokens:
            if token.startswith("NAMESPACE") or token.startswith("CLASS"):
                ends_needed += 1
            elif token == "END":
                ends_needed -= 1

        assert ends_needed == 0, f"Umatched end for namespace or class. Missing ends: {ends_needed}"

        return self.tokens

    def lex_docifyable(self):
        self.skip_until_match("public ", "//", "{", "}")
        if self.peek(-1) == "{":
            self.skip_method()
            return
        elif self.peek(-1) == "}":
            self.tokens.append("END")
            return

        comment_pos = self.pos - 2
        self.skip_whitespace()

        if self.match("<summary>"):
            self.pos = comment_pos
            xml = self.read_documentation_comments()
            self.tokens.append(f"DOCS:{xml}")
            self.lex_docifyable()
        elif self.skip_if_match("class "):
            class_name = self.get_word()
            if class_name != "":
                self.tokens.append(f"CLASS:{class_name}")
                self.skip_until_match("{")
        else:
            method_type = self.get_word()
            self.skip_whitespace()
            method_name = self.get_word()
            if method_type != "" and method_name != "":
                self.tokens.append(f"METHOD:{method_type}:{method_name}")
            self.skip_until_match("{")
            self.skip_method()

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
            self.skip_until_match(";")
            self.skip_whitespace()

    def skip_whitespace(self) -> None:
        while self.is_current_pos_valid() and self.current.isspace():
            self.next()

    def next(self, offset = 1) -> str:
        self.pos += offset
        return self.peek(0)

    def get_token(self, *end_of_token: str) -> str:
        token = ""
        while self.is_current_pos_valid() and not self.current in end_of_token:
            token += self.next()
        return token

    def get_word(self, *allowed_chars: str) -> str:
        word = ""
        while self.is_current_pos_valid() and (self.current.isalpha() or self.current in allowed_chars):
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

    def match(self, *matches: str) -> bool:
        for match in matches:
            if not self.is_valid_pos(self.pos + len(match)):
                continue

            no_match = False
            for i, char in enumerate(match):
                if self.peek(i) != char:
                    no_match = True
                    break
            if no_match:
                continue

            return True
        return False

    def match_at_pos(self, pos, *matches: str) -> bool:
        original_pos = self.pos
        self.pos = pos
        is_match = self.match(*matches)
        self.pos = original_pos
        return is_match

    def skip_if_match(self, *matches: str) -> bool:
        for match in matches:
            if self.match(match):
                self.pos += len(match)
                return True
        return False

    def skip_until_match(self, *matches: str) -> bool:
        ignore_end_token = ""
        while self.is_current_pos_valid():
            if ignore_end_token != "":
                if self.skip_if_match(ignore_end_token):
                    ignore_end_token = ""
                else:
                    self.next()
                    continue

            if self.skip_if_match(*matches):
                break
            
            if self.skip_if_match("\""):
                ignore_end_token = "\""
            elif self.skip_if_match("//"):
                ignore_end_token = "\n"
            elif self.skip_if_match("/*"):
                ignore_end_token = "*/"
            else:
                self.next()

    def skip_method(self):
        ignore_end_token = ""
        begin_brace_count = 0
        while self.is_current_pos_valid():
            if ignore_end_token != "":
                if self.skip_if_match(ignore_end_token):
                    ignore_end_token = ""
                else:
                    self.next()
                    continue

            if self.current == "{":
                begin_brace_count += 1
            elif self.current == "}":
                if begin_brace_count == 0:
                    self.next()
                    return
                begin_brace_count -= 1

            if self.skip_if_match("\""):
                ignore_end_token = "\""
            elif self.skip_if_match("//"):
                ignore_end_token = "\n"
            elif self.skip_if_match("/*"):
                ignore_end_token = "*/"
            else:
                self.next()

    def find(self, *matches: str) -> int:
        pos = self.pos
        while self.is_valid_pos(pos) and not self.match_at_pos(pos, *matches):
            pos += 1
        
        return pos

run("Test.bf")
