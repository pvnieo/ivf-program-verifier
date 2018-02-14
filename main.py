from interpreter.Interpreter import Interpreter
from interpreter.Lexer import Lexer
from interpreter.Parser import Parser

# usage : python main.py

def main():
    import sys
    # change here to try a different file
    sys.argv.append('input/text_source_complique.txt')
    text = open(sys.argv[1], 'r').read()

    lexer = Lexer(text)
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    result = interpreter.interpret()
    print('/------- All labels -------/')
    print(interpreter.parser.labels)
    print('/------- Labels visited -------/ ')
    print(interpreter.visited)
    print('/------- Labels not visited -------/ ')
    not_visited = [ u for u in interpreter.parser.labels if u not in interpreter.visited]
    print(not_visited)
    print('/------- Variables final evaluation -------/ ')
    for k, v in sorted(interpreter.GLOBAL_SCOPE.items()):
        print('%s = %s' % (k, v))

if __name__ == '__main__':
    main()

