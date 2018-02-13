from interpreter.Interpreter import Interpreter
from interpreter.Lexer import Lexer
from interpreter.Parser import Parser

def main():
    import sys
    sys.argv.append('input/text_source_simple.txt')
    text = open(sys.argv[1], 'r').read()

    lexer = Lexer(text)
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    result = interpreter.interpret()
    for k, v in sorted(interpreter.GLOBAL_SCOPE.items()):
        print('%s = %s' % (k, v))

if __name__ == '__main__':
    main()

