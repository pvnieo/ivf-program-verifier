from interpreter.Interpreter import Interpreter
from interpreter.Lexer import Lexer
from interpreter.Parser import Parser
from interpreter.DatatestSet import DatatestSet, Datatest
import sys

# usage : python main.py input/text_source.txt datatests/dt1.txt

def main():

    text_source_original = open(sys.argv[1], 'r').read()
    text_datatestset = open(sys.argv[2], 'r').read()

    dts = DatatestSet(text_datatestset)
    dts.parse()
    i = 1
    visited = []
    for dt in dts.datatests :
        """ Evaluate program for each datatest """
        print('====================================')
        print('-------Datatest '+str(i)+'--------')
        print('====================================')
        """ Add assigments to program """
        dt.parse()
        text_source = dt.ini_source + text_source_original
        print('/------- Evaluating with initial assigments:  -------/ ')
        print(dt.ini_source)
        """ Now Interpret program """
        lexer = Lexer(text_source)
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        result = interpreter.interpret()
        print('/------- Labels ASSIGN visited -------/ ')
        i_visited = [l.value for l in interpreter.visited if l.type == 'ASSIGN']
        print(i_visited)
        visited = set(list(visited)+i_visited)
        print('/------- Variables final evaluation -------/ ')
        for k, v in sorted(interpreter.GLOBAL_SCOPE.items()):
            print('%s = %s' % (k, v))
        i += 1
    print('====================================')
    print('------- Result of datatest set (jeu de donnee) --------')
    print('====================================')
    print('/------- All labels ASSIGN-------/')
    print([ l.value for l in interpreter.parser.labels if l.type == 'ASSIGN' ] )
    print('/------- Labels ASSIGN not visited -------/ ')
    not_visited = [ u.value for u in interpreter.parser.labels if u.value not in visited and u.type == 'ASSIGN']
    print(not_visited)
    if not_visited == []:
        print()
        print('>> Critere TA TRUE')
    else:
        print()
        print('>> Critere TA FALSE')

if __name__ == '__main__':
    main()

