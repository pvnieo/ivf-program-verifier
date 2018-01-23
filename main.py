from interpreter.Interpreter import Interpreter
from interpreter.Lexer import Lexer
from interpreter.Parser import Parser

def main():
    # Read source code
    file = 'input/text_source.txt'
    file = 'input/pascal_test.txt'
    lexer = Lexer(file)
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    result = interpreter.interpret()
    print(result)

if __name__ == '__main__':
    main()

main()