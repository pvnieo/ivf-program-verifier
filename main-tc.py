from cfg.CfgParser import CfgParser
from cfg.CfgInterpreter import  CfgInterpreter
from interpreter.DatatestSet import DatatestSet
import sys

# usage : python main-tc.py input/text_source.txt datatests/dt1.txt 10

def main():
    if len(sys.argv) != 3:
        print('EXPECTING AS ARGV: SOURCE_CODE DATATESTSET K')
        exit()
    text_source = open(sys.argv[1], 'r').read()
    text_datatestset = open(sys.argv[2], 'r').read()
    K = int(sys.argv[3])

    dts = DatatestSet(text_datatestset)
    dts.parse()
    i = 1
    visited = []
    for dt in dts.datatests:
        """ Evaluate program for each datatest """
        print('====================================')
        print('-------Datatest ' + str(i) + '--------')
        print('====================================')
        """ Add assigments to program """
        dt.parse()
        print('/------- Evaluating with initial assigments:  -------/ ')
        print(dt.ini_assigns)
        """ Now Interpret program """
        cfgparser = CfgParser(text_source)
        cfgparser.parse()
        cfginterpreter = CfgInterpreter(cfgparser)
        cfginterpreter.interpretAssigments(dt.ini_assigns)
        cfginterpreter.interpretCfg()
        print('/------- Path visited -------/ ')
        i_visited = sorted(cfginterpreter.visited)
        print(i_visited)
        visited.append(i_visited)
        print('/------- Variables final evaluation -------/ ')
        for k, v in sorted(cfginterpreter.interpreter.GLOBAL_SCOPE.items()):
            print('%s = %s' % (k, v))
        i += 1
    print('====================================')
    print('------- Result of datatest set (jeu de donnee) --------')
    print('====================================')
    print('/------- All paths visited-------/')
    print(visited)
    print('/------- All paths -------/')
    k_paths = []
    for path in cfginterpreter.getPaths(K):
        k_paths.append(sorted(path))
    print(k_paths)
    print('/------- Paths not visited -------/')
    not_visited = [ path for path in k_paths if path  not in visited]
    print(not_visited)

    if not_visited == []:
        print()
        print('>> Critere TC TRUE')
    else:
        print()
        print('>> Critere TC FALSE')
    if len(k_paths) > 0 :
        coverage_rate = round(1 - len(not_visited)/len(k_paths),2)*100
        print()
        print('>> Taux de couverture : {}%'.format(coverage_rate))
    else :
        coverage_rate = 100
        print()
        print('>> Taux de couverture : {}% : no {}-paths found'.format(coverage_rate, K))

if __name__ == '__main__':
    main()
