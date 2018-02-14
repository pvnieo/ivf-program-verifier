import json

###############################################################################
#                                                                             #
#  INTERPRETER                                                                #
#                                                                             #
###############################################################################

# Token types
#
# EOF (end-of-file) token is used to indicate that
# there is no more input left for lexical analysis
INTEGER       = 'INTEGER'
INTEGER_CONST = 'INTEGER_CONST'
PLUS          = 'PLUS'
MINUS         = 'MINUS'
MUL           = 'MUL'
DIV           = 'DIV'
LPAREN        = 'LPAREN'
RPAREN        = 'RPAREN'
ID            = 'ID'
LABEL         = 'LABEL'
PIPE          = 'PIPE'
ASSIGN        = 'ASSIGN'
BEGIN         = 'BEGIN'
END           = 'END'
SEMI          = 'SEMI'
COLON         = 'COLON'
LBRACKET      = 'LBRACKET'
RBRACKET      = 'RBRACKET'
INFERIOR      = 'INFERIOR'
SUPERIOR      = 'SUPERIOR'
EQUAL         = 'EQUAL'
IF            = 'IF'
ELSE          = 'ELSE'
WHILE         = 'WHILE'
EOF           = 'EOF'

class NodeVisitor(object):
    def visit(self, node):
        # to debug and follow which node is visited
        #print(type(node).__name__)
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser
        import collections
        self.GLOBAL_SCOPE = collections.OrderedDict()
        self.visited = []

    def visit_Program(self, node):
        for compound in node.compounds:
            self.visit(compound)

    def visit_Block(self, node):
        self.visited.append(node.label.value)
        # print("VISITED : " + str(node.label.value))
        for statement in node.statement_list:
            self.visit(statement)

    def visit_VarDecl(self, node):
        # Do nothing
        pass

    def visit_Type(self, node):
        # Do nothing
        pass

    def visit_BinOp(self, node):
        #print("##### OP : " + node.op.type)
        if node.op.type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == DIV:
            return self.visit(node.left) // self.visit(node.right)
        elif node.op.type == SUPERIOR:
            return self.visit(node.left) > self.visit(node.right)
        elif node.op.type == INFERIOR:
            return self.visit(node.left) < self.visit(node.right)
        elif node.op.type == EQUAL:
            return self.visit(node.left) == self.visit(node.right)

    def visit_Num(self, node):
        return node.value

    def visit_UnaryOp(self, node):
        op = node.op.type
        if op == PLUS:
            return +self.visit(node.expr)
        elif op == MINUS:
            return -self.visit(node.expr)

    def visit_Compound(self, node):
        self.visit(node.block)

    def visit_IfBlock(self, node):
        if self.visit(node.cond_block):
            self.visit(node.block_true)
        else:
            self.visit(node.block_false)

    def visit_CondBlock(self, node):
        self.visited.append(node.label.value)
        return self.visit(node.condition)

    def visit_WhileBlock(self, node):
        while self.visit(node.cond_block):
            self.visit(node.block)

    def visit_Assign(self, node):
        var_name = node.left.value
        self.GLOBAL_SCOPE[var_name] = self.visit(node.right)

    def visit_Var(self, node):
        var_name = node.value
        var_value = self.GLOBAL_SCOPE.get(var_name)
        if var_value is None:
            # If a variable isn't defined yet, return 0
            return 0
        else:
            return var_value

    def visit_NoOp(self, node):
        pass

    def interpret(self):
        tree = self.parser.parse()
        if tree is None:
            return ''
        return self.visit(tree)
