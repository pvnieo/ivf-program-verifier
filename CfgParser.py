from interpreter.Lexer import Lexer
from interpreter.Parser import Parser
import sys
import networkx as nx
import matplotlib.pyplot as plt

class Node:
    def __init__(self, _num, type, value):
        self._num = _num
        self.type = type
        self.value = value

class Edge:
    def __init__(self, node1, node2, value):
        self.node1 = node1
        self.node2 = node2
        self.value = value

class CfgParser:

    def __init__(self, text_source):
        self.test_source = text_source
        lexer = Lexer(text_source)
        parser = Parser(lexer)
        self.parser = parser
        self.ast = self.parser.parse()
        self.cfg = nx.DiGraph()
        self.previous_label = ''
        self.previous_source = ''
        self.last_true_label = ''
        self.inIfFalse = False

    def visit(self, node):
        # to debug and follow which node is visited
        #print(type(node).__name__)
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))

    def visit_Program(self, node):
        for compound in node.compounds:
            self.visit(compound)

    def visit_Compound(self, node):
        return self.visit(node.cblock)

    def visit_IfBlock(self, node):
        self.visit(node.cond_block)
        self.inIfTrue = True
        self.visit(node.block_true)
        self.last_true_label = self.previous_label
        self.inIfTrue = False
        self.inIfFalse = True
        self.visit(node.block_false)
        self.inIfFalse = False

    def visit_WhileBlock(self, node):
        self.visit(node.cond_block)
        self.visit(node.block)

    def visit_CondBlock(self, node):
        label = node.label.value
        self.addlabel(label)
        #self.visit(node.condition)
        #s = '  node{} -> node{}\n'.format(node._num, node.condition._num)
        #self.dot_body.append(s)

    def visit_Block(self, node):
        label = node.label.value
        self.addlabel(label)

        #for statement in node.statement_list:
        #    self.visit(statement)
        #    s = '  node{} -> node{}\n'.format(node._num, statement._num)
        #    self.dot_body.append(s)

    def addlabel(self, label):
        self.cfg.add_node(label, label=label)
        if self.previous_label != '' \
            and not self.inIfFalse :
            self.cfg.add_edge(self.previous_label, label)
        elif self.previous_label != '' \
            and self.inIfFalse \
            and self.previous_source != '' :
            self.cfg.add_edge(self.previous_source, label)
            self.previous_source = ''
        elif self.previous_label != '' \
            and self.inIfFalse \
            and self.previous_source == '':
            self.cfg.add_edge(self.previous_label, label)
        if self.last_true_label != ''\
            and not self.inIfFalse :
            self.cfg.add_edge(self.last_true_label, label)
            self.last_true_label = ''
        self.previous_label = label

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
        pass

    def visit_NoneType(self, node):
        return None

    def gendot(self):
        self.visit(self.ast)
        pos = nx.circular_layout(self.cfg)
        nx.draw(self.cfg, pos, with_labels=True, font_weight='bold')
        node_labels = nx.get_node_attributes(self.cfg, 'label')
        nx.draw_networkx_labels(self.cfg, pos, labels=node_labels)
        edge_labels = nx.get_edge_attributes(self.cfg, 'label')
        nx.draw_networkx_edge_labels(self.cfg, pos, labels=edge_labels)
        plt.show()

sys.argv.append('input/text_source_complique.txt')
text_source_original = open(sys.argv[1], 'r').read()
cfgparser = CfgParser(text_source_original)
content = cfgparser.gendot()
print(content)