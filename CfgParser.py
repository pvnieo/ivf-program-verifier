from interpreter.Lexer import Lexer
from interpreter.Parser import Parser
import sys
import networkx as nx
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
            self.connectIf(cond_label, node.block_true.label, node.block_false.label)
        else:
            # if no false block must connect to if source node for next compound
            node.label = [node.block_true.label, node.source]
            self.connectIf(cond_label, node.block_true.label, None)

    def visit_WhileBlock(self, node):
        self.visit(node.cond_block)
        self.visit(node.block)
        node.source = node.cond_block.label.value
        node.label = node.block.label
        self.labelsWhile.append(node.source)
        self.connectWhile(node.source, node.label, "")
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

        #for statement in node.statement_list:
        #    self.visit(statement)
        #    s = '  node{} -> node{}\n'.format(node._num, statement._num)
        #    self.dot_body.append(s)

    def addlabel(self, label):
        self.cfg.add_node(label, label=label)
        #if self.previous_label != '':
            #self.cfg.add_edge(self.previous_label, label)
        self.previous_label = label

    def connectIf(self,cl,tl, fl):
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
                self.cfg.add_edge(cl, tl[0], label=self.getCondition(cl))
            else:
                # connect with fist label
                self.connectIf(cl, tl[0], fl)
            if isinstance(fl, int):
                fl = [fl]
            if len(fl) == 1 :
                self.cfg.add_edge(cl, fl[0], label="! "+self.getCondition(cl))
            else:
                # connect with fist label
                self.connectIf(cl, tl,fl[0])
        else:
            if isinstance(tl, int):
                tl = [tl]
            if len(tl) == 1 :
                self.cfg.add_edge(cl, tl[0], label=self.getCondition(cl))
            else:
                # connect with fist label
                self.connectIf(cl, tl[0], fl)

    def connectWhile(self, cl, tl, direction):
        """
        Connect while labels like for connectIF :
        connect decision label to first assigment label
        and last assigment label to decision label
        """
        if isinstance(tl, int):
            tl = [tl]
        # connect decision label to first assigment label
        if len(tl) == 1 and direction != "LAST":
            self.cfg.add_edge(cl, tl[0], label=self.getCondition(cl))
        elif direction != "LAST":
            # connect with fist label
            self.connectWhile(cl, tl[0], "FIRST")
        # connect last assigment label to decision label
        if len(tl) == 1 and direction != "FIRST":
            self.cfg.add_edge(tl[0], cl, label=self.getAssignments(tl[0]))
        elif direction != "FIRST":
            # connect with fist label
            self.connectWhile(cl, tl[-1], "LAST")

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
                self.cfg.add_edge(labels[0], next_label)
            else:
                self.connectCompounds(labels[-1], next_label)

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

    def getCondition(self, label):
        src = self.text_source
        from_pos = src.find(str(label)+':')+len(str(label))+1 #don't want label
        return 'todo'

    def getAssignments(self, label):
        src = self.text_source
        from_pos = src.find(str(label)+':')+len(str(label))+1  #don't want label
        return 'todo'

    def gendot(self):
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


sys.argv.append('input/text_source_complique.txt')
text_source_original = open(sys.argv[1], 'r').read()
cfgparser = CfgParser(text_source_original)
content = cfgparser.gendot()
