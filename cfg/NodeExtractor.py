from interpreter.Interpreter import Interpreter, NodeVisitor
from interpreter.Lexer import Lexer
from interpreter.Parser import Parser
import copy

class NodeExtractor:
    def __init__(self, ast):
        self.ast = ast
        self.search = None
        self.found = None

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
        self.visit(node.cblock)

    def visit_IfBlock(self, node):
        self.visit(node.cond_block)
        self.visit(node.block_true)
        self.visit(node.block_false)

    def visit_WhileBlock(self, node):
        self.visit(node.cond_block)
        self.visit(node.block)

    def visit_CondBlock(self, node):
        if node.label.value == self.search:
            self.found = node.condition

    def visit_Block(self, node):
        if isinstance(node.label,int):
            print(node.label)
        if node.label.value == self.search:
            self.found = node

    def visit_NoOp(self, node):
        pass

    def extractBlockFromLabel(self, label):
        self.search = label
        self.visit(self.ast)
        return self.found

