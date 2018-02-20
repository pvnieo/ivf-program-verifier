from cfg.CfgParser import CfgParser
from cfg.CfgInterpreter import  CfgInterpreter
from interpreter.DatatestSet import DatatestSet
import sys

# usage : python main-tdef.py input/text_source.txt datatests/dt1.txt 2

def main():
    if len(sys.argv) != 2 :
        print('EXPECTING AS ARGV: SOURCE_CODE DATATESTSET')
        exit()
    text_source = open(sys.argv[1], 'r').read()
    text_datatestset = open(sys.argv[2], 'r').read()

    dts = DatatestSet(text_datatestset)
    dts.parse()
    i = 1
    while_dict_list = []
    critere = True
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
        # we don't really count the initial test assigment as definition
        cfginterpreter.interpreter.toUse = []
        # variable so that an exception is raised when a variable is not used after a declaration i.e. between two declarations
        cfginterpreter.interpreter.raiseExceptionIfNotUsed = True
        try:
            while_dict = cfginterpreter.interpretCfg()
        except RuntimeError:
            critere = False
        print('/------- Variables declarations not used at the end of the program: -------/ ')
        print(cfginterpreter.interpreter.toUse)
        if cfginterpreter.interpreter.toUse != []:
            critere = False
        print('/------- Variables final evaluation -------/ ')
        for k, v in cfginterpreter.interpreter.GLOBAL_SCOPE.items():
            print('%s = %s' % (k, v))
        i += 1
    print('====================================')
    print('------- Result of datatest set (jeu de donnee) --------')
    print('====================================')
    if critere:
        print()
        print('>> Critere TDef  TRUE')
    else:
        print()
        print('>> Critere TDef FALSE')

if __name__ == '__main__':
    main()

