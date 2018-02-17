from cfg.CfgParser import CfgParser
import sys

sys.argv.append('input/text_source_complique.txt')
text_source_original = open(sys.argv[1], 'r').read()
cfgparser = CfgParser(text_source_original)
cfgparser.parse()