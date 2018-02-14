###############################################################################
#  AST visualizer - generates a DOT file for Graphviz.                        #
#                                                                             #
#  To generate an image from the DOT file run $ dot -Tpng -o ast.png ast.dot  #
#                                                                             #
###############################################################################

## To visualize
# C:\Program Files (x86)\Graphviz2.38\bin
# python mainvisualize.py input/text_source_complique.txt > text_source_complique.dot && dot -Tpng -o text_source_complique.png text_source_complique.dot

import argparse
import textwrap

from interpreter.Interpreter import Interpreter, NodeVisitor
from interpreter.Lexer import Lexer
from interpreter.Parser import Parser

class ASTVisualizer(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser
        self.ncount = 1
        self.dot_header = [textwrap.dedent("""\
        digraph astgraph {
          node [shape=circle, fontsize=12, fontname="Courier", height=.1];
          ranksep=.3;
          edge [arrowsize=.5]
        """)]
        self.dot_body = []
        self.dot_footer = ['}']

    def visit_Program(self, node):
        s = '  node{} [label="Program"]\n'.format(self.ncount)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        for compound in node.compounds:
            self.visit(compound)

        for compound in node.compounds:
            s = '  node{} -> node{}\n'.format(node._num, compound._num)
            self.dot_body.append(s)

    def visit_Compound(self, node):
        s = '  node{} [label="Compound {}"]\n'.format(self.ncount, node.type)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.block)
        s = '  node{} -> node{}\n'.format(node._num,  node.block._num)
        self.dot_body.append(s)

    def visit_IfBlock(self, node):
        s = '  node{} [label="IF"]\n'.format(self.ncount)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.cond_block)
        s = '  node{} -> node{} [label="COND"]\n'.format(node._num,  node.cond_block._num)
        self.dot_body.append(s)

        self.visit(node.block_true)
        s = '  node{} -> node{} [label="IF TRUE"] \n'.format(node._num,  node.block_true._num)
        self.dot_body.append(s)

        self.visit(node.block_false)
        s = '  node{} -> node{} [label="ELSE"] \n'.format(node._num,  node.block_false._num)
        self.dot_body.append(s)

    def visit_WhileBlock(self, node):
        s = '  node{} [label="WHILE"]\n'.format(self.ncount)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.cond_block)
        s = '  node{} -> node{} [label="COND"]\n'.format(node._num,  node.cond_block._num)
        self.dot_body.append(s)

        self.visit(node.block)
        s = '  node{} -> node{} [label="IF TRUE"] \n'.format(node._num,  node.block._num)
        self.dot_body.append(s)

    def visit_CondBlock(self, node):
        s = '  node{} [label="Label {}"]\n'.format(self.ncount, node.label.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.condition)
        s = '  node{} -> node{}\n'.format(node._num, node.condition._num)
        self.dot_body.append(s)

    def visit_Block(self, node):
        s = '  node{} [label="Label {}"]\n'.format(self.ncount, node.label.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        for statement in node.statement_list:
            self.visit(statement)
            s = '  node{} -> node{}\n'.format(node._num, statement._num)
            self.dot_body.append(s)

    def visit_VarDecl(self, node):
        s = '  node{} [label="VarDecl"]\n'.format(self.ncount)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.var_node)
        s = '  node{} -> node{}\n'.format(node._num, node.var_node._num)
        self.dot_body.append(s)

        self.visit(node.type_node)
        s = '  node{} -> node{}\n'.format(node._num, node.type_node._num)
        self.dot_body.append(s)

    def visit_Type(self, node):
        s = '  node{} [label="{}"]\n'.format(self.ncount, node.token.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

    def visit_Num(self, node):
        s = '  node{} [label="{}"]\n'.format(self.ncount, node.token.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

    def visit_BinOp(self, node):
        s = '  node{} [label="{}"]\n'.format(self.ncount, node.op.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.left)
        self.visit(node.right)

        for child_node in (node.left, node.right):
            s = '  node{} -> node{}\n'.format(node._num, child_node._num)
            self.dot_body.append(s)

    def visit_UnaryOp(self, node):
        s = '  node{} [label="unary {}"]\n'.format(self.ncount, node.op.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.expr)
        s = '  node{} -> node{}\n'.format(node._num, node.expr._num)
        self.dot_body.append(s)

    def visit_Assign(self, node):
        s = '  node{} [label="{}"]\n'.format(self.ncount, node.op.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.left)
        self.visit(node.right)

        for child_node in (node.left, node.right):
            s = '  node{} -> node{}\n'.format(node._num, child_node._num)
            self.dot_body.append(s)

    def visit_Var(self, node):
        s = '  node{} [label="{}"]\n'.format(self.ncount, node.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

    def visit_NoOp(self, node):
        s = '  node{} [label="NoOp"]\n'.format(self.ncount)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

    def visit_NoneType(self, node):
        return None

    def gendot(self):
        tree = self.parser.parse()
        self.visit(tree)
        return ''.join(self.dot_header + self.dot_body + self.dot_footer)


def main():
    argparser = argparse.ArgumentParser(
        description='Generate an AST DOT file.'
    )
    argparser.add_argument(
        'fname',
        help='Pascal source file'
    )
    args = argparser.parse_args()
    fname = args.fname
    text = open(fname, 'r').read()

    lexer = Lexer(text)
    parser = Parser(lexer)
    viz = ASTVisualizer(parser)
    content = viz.gendot()
    print(content)

if __name__ == '__main__':
    main()