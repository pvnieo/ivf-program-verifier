import sys
import networkx as nx
import copy
from interpreter.Lexer import Lexer
from interpreter.Parser import Parser
from cfg.NodeExtractor import NodeExtractor
import pydot as pydot
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
        self.text_source = text_source
        lexer = Lexer(text_source)
        parser = Parser(lexer)
        self.parser = parser
        self.ast = self.parser.parse()
        self.ne = NodeExtractor(copy.deepcopy(self.ast))
        self.cfg = nx.DiGraph()
        self.previous_label = ''
        self.labelsIf = []
        self.labelsWhile = []

    def visit(self, node):
        # to debug and follow which node is visited
        #print(type(node).__name__)
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))

    def visit_Program(self, node):
        # labels_to_connect to contain lists of last labels of compounds
        # useful to connect if blocks together
        labels_to_connect = []
        previous_labels = []
        for compound in node.compounds:
            self.visit(compound)
            labels_to_connect.append(compound.label)
            if node.source is None:
                node.source = compound.source
            # connect last labels of previous compound to next compound
            if previous_labels:
                self.connectCompounds(previous_labels, compound.source)
            previous_labels = compound.label
        node.label = labels_to_connect
        return labels_to_connect

    def visit_Compound(self, node):
        self.visit(node.cblock)
        node.label = node.cblock.label
        node.source = node.cblock.source

    def visit_IfBlock(self, node):
        self.visit(node.cond_block)
        self.visit(node.block_true)
        cond_label = node.cond_block.label.value
        node.source = cond_label
        self.labelsIf.append(cond_label)
        if type(node.block_false).__name__ != 'NoOp':
            self.visit(node.block_false)
            node.label = [node.block_true.label, node.block_false.label]
            # connect cond to true_block and false_block
            self.connectIf(cond_label, node.block_true.label, node.block_false.label, node)
        else:
            # if no false block must connect to if source node for next compound
            node.label = [node.block_true.label, node.source]
            self.connectIf(cond_label, node.block_true.label, None, node)

    def visit_WhileBlock(self, node):
        self.visit(node.cond_block)
        self.visit(node.block)
        node.source = node.cond_block.label.value
        node.label = node.block.label
        self.labelsWhile.append(node.source)
        self.connectWhile(node.source, node.label, "", node)
        # for WHILE, we need to connect not only the last label of the true block
        # to the next compound
        # but ALSO the decision label
        node.label = [node.label, node.source]


    def visit_CondBlock(self, node):
        label = node.label.value
        self.addlabel(label)
        #self.visit(node.condition)
        #s = '  node{} -> node{}\n'.format(node._num, node.condition._num)
        #self.dot_body.append(s)

    def visit_Block(self, node):
        label = node.label.value
        self.addlabel(label)
        node.label = label
        node.source = label

        code = ""
        for statement in node.statement_list:
            if type(statement).__name__ != 'NoOp':
                code += self.visit(statement) + ' ; '
        return code

    def addlabel(self, label):
        self.cfg.add_node(label, label=label)
        #if self.previous_label != '':
            #self.cfg.add_edge(self.previous_label, label)
        self.previous_label = label

    def connectIf(self,cl,tl, fl, node):
        """ cl : unique label of decision (condition)
            tl : (true) labels returned from true branch
            fl : (false) labels returned from false branch
            The idea behind the algorithm is that when connecting the ifs
            We want to connect the first label of each branch (true_block|false_block)
            So we iterate until we get the first branch (most left side of list)
        """
        if fl is not None :
            if isinstance(tl, int):
                tl = [tl]
            if len(tl) == 1 :
                self.cfg.add_edge(cl, tl[0], label=self.visit_BinOp(node.cond_block.condition))
            else:
                # connect with fist label of true block
                self.connectIf(cl, tl[0], fl, node)
            if isinstance(fl, int):
                fl = [fl]
            if len(fl) == 1 :
                self.cfg.add_edge(cl, fl[0], label="! "+self.visit_BinOp(node.cond_block.condition))
            else:
                # connect with fist label of false block
                self.connectIf(cl, tl,fl[0], node)
        else:
            if isinstance(tl, int):
                tl = [tl]
            if len(tl) == 1 :
                self.cfg.add_edge(cl, tl[0], label=self.visit_BinOp(node.cond_block.condition))
            else:
                # connect with fist label of true block
                self.connectIf(cl, tl[0], fl, node)

    def connectWhile(self, cl, tl, direction, node):
        """
        Connect while labels like for connectIF :
        connect decision label to first assigment label
        and last assigment label to decision label
        """
        if isinstance(tl, int):
            tl = [tl]
        # connect decision label to first assigment label
        if len(tl) == 1 and direction != "LAST":
            self.cfg.add_edge(cl, tl[0], label=self.visit_BinOp(node.cond_block.condition))
        elif direction != "LAST":
            # connect with fist label
            self.connectWhile(cl, tl[0], "FIRST", node)
        # connect last assigment label to decision label
        if len(tl) == 1 and direction != "FIRST":
            # to extract the assigment label, we just extract the block whose label matches
            # and then we visit it ...
            assign_label = self.visit(copy.deepcopy(self.ne.extractBlockFromLabel(tl[0])))
            self.cfg.add_edge(tl[0], cl, label=assign_label)
        elif direction != "FIRST":
            # connect with fist label
            self.connectWhile(cl, tl[-1], "LAST", node)

    def connectCompounds(self,previous_labels, next_label):
        """ Connect compounds recursively
        The idea behind the algorithm is that when connecting the last labels
        of the previous compound to the source of the next compound, we need
        to iterate to most right side of the list until we fin one element.
        """
        if isinstance(previous_labels, int):
            previous_labels = [previous_labels]
        for labels in previous_labels :
            if isinstance(labels, int):
                labels = [labels]
            if len(labels) == 1:
                # if the node is a condition, we must add "!" in front since if it was a direct condition
                # from a while or if, the edge would have been handled in connectWhile or connect If
                subtree = copy.deepcopy(self.ne.extractBlockFromLabel(labels[0]))
                if type(subtree).__name__ == 'BinOp':
                    assign_label = '! '+self.visit(subtree)
                else:
                    assign_label = self.visit(subtree)
                self.cfg.add_edge(labels[0], next_label, label=assign_label)
            else:
                self.connectCompounds(labels[-1], next_label)

    def visit_Num(self, node):
        s = '  node{} [label="{}"]\n'.format(self.ncount, node.token.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

    def visit_BinOp(self, node):
        return self.visit(node.left) + self.s(node.op.value) + self.visit(node.right)

    def visit_UnaryOp(self, node):
        return str(self.visit(node.expr))

    def visit_Assign(self, node):
        self.visit(node.left)
        self.visit(node.right)
        return self.visit(node.left) + ' = ' + self.visit(node.right)

    def visit_Var(self, node):
        return node.value

    def visit_NoOp(self, node):
        pass

    def visit_Num(self, node):
        return str(node.value)

    def visit_NoneType(self, node):
        return None

    def s(self, str):
        return " "+str+" "

    def parse(self):
        self.visit(self.ast)
        self.show()

    def show(self):
        pos = nx.drawing.nx_pydot.pydot_layout(self.cfg)
        nx.draw(self.cfg, pos, with_labels=True, font_weight='bold')
        node_labels = nx.get_node_attributes(self.cfg, 'label')
        nx.draw_networkx_labels(self.cfg, pos, labels=node_labels)
        edge_labels = nx.get_edge_attributes(self.cfg, 'label')
        nx.draw_networkx_edge_labels(self.cfg, pos, labels=edge_labels)
        #plt.show()

        nx.drawing.nx_pydot.write_dot(self.cfg, "cfg.dot")
        print('To visualize : ')
        print('dot -Tpng -o cfg.png cfg.dot')

