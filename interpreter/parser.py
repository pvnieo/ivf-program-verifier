###############################################################################
#                                                                             #
#  PARSER                                                                     #
#                                                                             #
###############################################################################

import sys

# Token types
#
# EOF (end-of-file) token is used to indicate that
# there is no more input left for lexical analysis
INTEGER       = 'INTEGER'
INTEGER_CONST = 'INTEGER_CONST'
PLUS          = 'PLUS'
MINUS         = 'MINUS'
MUL           = 'MUL'
PROGRAM       = 'PROGRAM'
DIV   = 'DIV'
LPAREN        = 'LPAREN'
RPAREN        = 'RPAREN'
ID            = 'ID'
ASSIGN        = 'ASSIGN'
BEGIN         = 'BEGIN'
PIPE          = 'PIPE'
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


class AST(object):
    pass

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class UnaryOp(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr

class Label(AST):
    def __init__(self, token, type):
        self.token = token
        self.value = token.value
        self.type = type

class Compound(AST):
    """Represents either a simple block or a IF block or WHILE """
    def __init__(self, type, cblock):
        self.cblock = cblock
        self.type = type
        self.label = None
        self.source = None

class IfBlock(AST):
    """ Represents an IF block, actually made of three"""
    def __init__(self, cond_block, block_true, block_false):
        self.cond_block = cond_block
        self.block_true = block_true
        self.block_false = block_false
        self.label = None
        self.source = None

class WhileBlock(AST):
    """ Represents a WHILE block, actually made of two"""
    def __init__(self, cond_block, block):
        self.cond_block = cond_block
        self.block = block
        self.label = None
        self.source = None

class CondBlock(AST):
    """ Represent a condition block with a label"""
    def __init__(self, label, condition):
        self.label = label
        self.condition = condition

class Assign(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

class Var(AST):
    """The Var node is constructed out of ID token."""
    def __init__(self, token):
        self.token = token
        self.value = token.value

class NoOp(AST):
    pass

class Block(AST):
    def __init__(self, label, statement_list):
        self.label = label
        self.statement_list = statement_list
        self.source = None

class Program(AST):
    def __init__(self, name, compounds):
        self.name = name
        self.compounds = compounds
        self.label = None
        self.source = None

class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        # set current token to the first token taken from the input
        self.current_token = self.lexer.get_next_token()
        self.labels = []

    def error(self):
        raise Exception('Invalid syntax with token ' + self.current_token.type)

    def eat(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def program(self):
        """program : block_list DOT"""
        compounds_node = self.compounds()
        program_node = Program(sys.argv[1], compounds_node)
        return program_node

    def compounds(self):
        """
        compounds : compound | compounds
        """
        node = self.compound()

        results = [node]

        # a new compound node either begins with IF or WHILE or a new label
        while self.current_token.type == IF \
                or self.current_token.type == WHILE \
                or (self.current_token.type == INTEGER_CONST and self.lexer.current_char == ':') :
            results.append(self.compound())

        return results

    def compound(self):
        """ Either if_block or normal block"""
        if self.current_token.type == IF:
            return Compound('IF', self.ifblock())
        elif self.current_token.type == WHILE:
            return Compound('WHILE', self.whileblock())
        else:
            return Compound('SIMPLE', self.block(ASSIGN))

    def ifblock(self):
        self.eat(IF)
        self.eat(LPAREN)
        cond_block = self.condblock(IF)
        self.eat(RPAREN)
        self.eat(LBRACKET)
        true_compounds = self.program()
        self.eat(RBRACKET)
        if self.current_token.type == ELSE :
            self.eat(ELSE)
            self.eat(LBRACKET)
            false_compounds = self.program()
            self.eat(RBRACKET)
        else :
            false_compounds = NoOp()
        return IfBlock(cond_block, true_compounds, false_compounds)

    def whileblock(self):
        self.eat(WHILE)
        self.eat(LPAREN)
        cond_block = self.condblock(WHILE)
        self.eat(RPAREN)
        self.eat(LBRACKET)
        compounds = self.program()
        self.eat(RBRACKET)
        return WhileBlock(cond_block, compounds)

    def condblock(self, type):
        label = self.label(type)
        condition = self.condition()
        return CondBlock(label, condition)

    def condition(self):
        variable = self.variable()
        op = self.current_token
        if op.type == SUPERIOR:
            self.eat(SUPERIOR)
        elif op.type == INFERIOR:
            self.eat(INFERIOR)
        elif op.type == EQUAL:
            self.eat(EQUAL)
        else:
            self.error()
        expr = self.expr()
        return BinOp(variable, op, expr)

    def block(self, type):
        """block : LABEL * statement_list """
        label = self.label(type)
        nodes = self.statement_list()
        root = Block(label, nodes)
        return root

    def label(self, type):
        """
        label: INTEGER * COLON
        """
        peek = self.lexer.current_char
        if peek == ':':
            node = Label(self.current_token, type)
            # add label to list of labels
            self.labels.append(node)
            self.eat(INTEGER_CONST)
            self.eat(COLON)
        else:
            self.lexer.error()
        return node


    def statement_list(self):
        """
        statement_list : statement
                       | statement SEMI statement_list
        """
        node = self.statement()

        results = [node]

        while self.current_token.type == SEMI:
            self.eat(SEMI)
            results.append(self.statement())

        return results

    def statement(self):
        """
        statement : statement_list
                  | assignment_statement
                  | empty
        """
        if self.current_token.type == BEGIN:
            node = self.statement_list()
        elif self.current_token.type == ID:
            node = self.assignment_statement()
        else:
            node = self.empty()
        return node

    def assignment_statement(self):
        """
        assignment_statement : variable ASSIGN expr
        """
        left = self.variable()
        token = self.current_token
        self.eat(ASSIGN)
        right = self.expr()
        node = Assign(left, token, right)
        return node

    def variable(self):
        """
        variable : ID
        """
        node = Var(self.current_token)
        self.eat(ID)
        return node

    def empty(self):
        """An empty production"""
        return NoOp()

    def expr(self):
        """
        expr : term ((PLUS | MINUS) term)*
        """
        node = self.term()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == MINUS:
                self.eat(MINUS)

            node = BinOp(left=node, op=token, right=self.term())

        return node

    def term(self):
        """term : factor ((MUL | INTEGER_DIV | FLOAT_DIV) factor)*"""
        node = self.factor()

        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            elif token.type == DIV:
                self.eat(DIV)

            node = BinOp(left=node, op=token, right=self.factor())

        return node

    def factor(self):
        """factor : PLUS factor
                  | MINUS factor
                  | INTEGER_CONST
                  | REAL_CONST
                  | LPAREN expr RPAREN
                  | variable
        """
        token = self.current_token
        if token.type == PLUS:
            self.eat(PLUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == MINUS:
            self.eat(MINUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == INTEGER_CONST:
            self.eat(INTEGER_CONST)
            return Num(token)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node
        else:
            node = self.variable()
            return node

    def parse(self):
        """
        program :  compounds EOF
        compounds : compound | compounds
        compound : if_block | while_block | block
        if_block : IF(  cond_block  )  {  compounds  }
                    | IF(  cond_block  )  { compounds }  ELSE  {  compounds  }
        while_block : WHILE(  cond_block  )  {  compounds  }
        cond_block : label condition
        block : label statement_list
        condition : variable SUPERIOR|INFERIOR|EQUAL expr
        statement_list : statement
                       | statement SEMI statement_list
        statement : statement_list
                  | assignment_statement
                  | empty
        assignment_statement : variable ASSIGN expr
        empty :
        expr : term ((PLUS | MINUS) term)*
        term : factor ((MUL | INTEGER_DIV )  factor)*
        factor : PLUS factor
               | MINUS factor
               | INTEGER_CONST
               | LPAREN expr RPAREN
               | variable
        variable: ID
        """
        node = self.program()
        if self.current_token.type != EOF:
            self.error()

        return node

