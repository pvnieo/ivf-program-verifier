from cfg.CfgParser import CfgParser
import sys

# to visualize : python mainvisualize_cfg.py input/text_source_complique.txt && dot -Tpng -o input/text_source_complique_cfg.png cfg.dot
text_source = open(sys.argv[1], 'r').read()
cfgparser = CfgParser(text_source)
cfgparser.parse()
print('To visualize : ')
print('dot -Tpng -o {} cfg.dot'.format(sys.argv[1].replace('.txt','_cfg.png')))

