from cfg.CfgParser import CfgParser
from cfg.CfgInterpreter import  CfgInterpreter
from interpreter.DatatestSet import DatatestSet
import sys

# usage : python main-tb.py input/text_source_while_in_a_while.txt datatests/dt3.txt 7

def main():
    if len(sys.argv) != 4:
        print('EXPECTING AS ARGV: SOURCE_CODE DATATESTSET I')
        exit()
    text_source = open(sys.argv[1], 'r').read()
    text_datatestset = open(sys.argv[2], 'r').read()
    I = int(sys.argv[3])

    dts = DatatestSet(text_datatestset)
    dts.parse()
    i = 1
    while_dict_list = []
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
        while_dict = cfginterpreter.interpretCfgForIWhile()
        print('/------- While with their labels and max iterations recorded -------/ ')
        for key in while_dict.keys():
            print("While {} iter {} ".format(key, while_dict[key][1]))
        while_dict_list.append(while_dict)
        print('/------- Variables final evaluation -------/ ')
        for k, v in cfginterpreter.interpreter.GLOBAL_SCOPE.items():
            print('%s = %s' % (k, v))
        i += 1
    print('====================================')
    print('------- Result of datatest set (jeu de donnee) --------')
    print('====================================')
    print('/------- All while with their max i iterations over all dataset----/')
    while_dict_max = {}
    for while_dict in while_dict_list:
        for key in while_dict.keys():
            if key not in while_dict_max.keys():
                while_dict_max[key] = while_dict[key][1]
            else:
                if while_dict_max[key]  < while_dict[key][1]:
                    while_dict_max[key] = while_dict[key][1]

    critere = True
    for key in while_dict_max.keys():
        if while_dict_max[key] > I:
            critere = False
        print("While {} has had a maximum of {} iterations".format(key, while_dict_max[key]))
    if critere:
        print()
        print('>> Critere TC for i = {} TRUE'.format(I))
    else:
        print()
        print('>> Critere TC for i = {} FALSE'.format(I))

if __name__ == '__main__':
    main()