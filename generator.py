from lexer import Lexer
from parser import Parser

def run(filepath):
    with open(filepath, "r") as f:
        text = f.read()
    
    lexer = Lexer(text)
    tokens = lexer.lex()
    print(tokens)
    parser = Parser(tokens)

run("TestClass.bf")