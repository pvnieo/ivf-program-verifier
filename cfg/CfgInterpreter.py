import networkx as nx
from collections import defaultdict, deque
from interpreter.Lexer import Lexer
from interpreter.Parser import Parser
from interpreter.Interpreter import Interpreter
from cfg.NodeExtractor import NodeExtractor

class CfgInterpreter:

    """
    Interpret a CFG with more general interpreter interpreter.Interpreter
    Visit all nodes
    Show new attributes of data
    """
    def __init__(self, cfgparser):
        self.cfgparser = cfgparser
        self.cfg = cfgparser.cfg
        self.node_labels = nx.get_node_attributes(self.cfg, 'label')
        self.edge_labels = nx.get_edge_attributes(self.cfg, 'label')
        lexer = Lexer(" ")
        parser = Parser(lexer)
        self.interpreter = Interpreter(parser)
        self.visited = []

    def parseCondition(self, code):
        """
        Parse code to get AST nodes
        :param code (ex: ' X < 48 ')
        :return: condition_node
        """
        self.interpreter.parser.lexer.__init__(code)
        self.interpreter.parser.current_token = \
            self.interpreter.parser.lexer.get_next_token()
        return self.interpreter.parser.condition()

    def parseAssigments(self, code):
        """
        Parse code to get AST nodes
        :param code: (ex: ' X = 42 ; Y = X +3 ;')
        :return: list of assigment_node
        """
        self.interpreter.parser.lexer.__init__(code)
        self.interpreter.parser.current_token = \
            self.interpreter.parser.lexer.get_next_token()
        return self.interpreter.parser.statement_list()

    def interpretCondition(self, code):
        """
        Interpret a condition based on code
        :param code: code source (grammar: "[!] condition")
        :return: True | False (evaluation)
        """
        if "!" in code :
            code = code.replace('!', '')
            condition_node = self.parseCondition(code)
            return not self.interpreter.visit(condition_node)
        else:
            condition_node = self.parseCondition(code)
            return self.interpreter.visit(condition_node)

    def interpretAssigments(self, code):
        """
        Interpret an assigment based on code
        :param code: code source (grammer: "statements_list")
        :return: None
        """
        assigments_list = self.parseAssigments(code)
        for statement in assigments_list:
            self.interpreter.visit(statement)
        # print(self.interpreter.GLOBAL_SCOPE)

    def getPaths(self, k):
        """
        Interpret the full CFG
        """
        to_visit = deque()  # next_nodes is a stack of tuples (node, distance of node from START)
        to_visit.append((self.getSourceNode(), 0))

        # Holding current valid path
        local_path = list()

        while to_visit:
            node, node_k = to_visit.pop()
            local_path = local_path[:node_k] + [node]
            if local_path[-1] == self.getTargetNode():
                # we touched the last node
                yield local_path
            elif node_k + 1 <= k:
                succ = list(self.cfg.successors(node))
                if node in self.cfgparser.labelsIf :
                    succ.reverse()
                for s in succ:
                    to_visit.append((s, node_k + 1))

    def getSourceNode(self):
        for n, nbrsdict in self.cfg.adjacency():
            predecessors = [p for p in self.cfg.predecessors(n)]
            if not predecessors :
                # source node is node without predecessors
                return n

    def getTargetNode(self):
         for n, nbrsdict in self.cfg.adjacency():
            successors = [s for s in self.cfg.successors(n)]
            if not successors :
                # target node is node without successors
                return n

    def interpretCfgForIWhile(self):
        """
        :return dict with keys while_label and value: [iter, max]
        """
        while_dict = {}
        target_node = self.getTargetNode()
        current_node = self.getSourceNode()
        self.visited.append(current_node)
        while current_node != target_node:
            #print(current_node)
            # see if there is actually a decision to take when node is (if|while)
            if current_node in self.cfgparser.labelsIf or \
                    current_node in self.cfgparser.labelsWhile:
                decision_node = current_node
                succ = [s for s in self.cfg.successors(current_node)]
                # Modified part
                if current_node in self.cfgparser.labelsWhile:
                    if current_node not in while_dict.keys():
                        while_dict[current_node] = [0, 0]
                    else:
                        while_dict[current_node][0] += 1
                        if while_dict[current_node][0] > while_dict[current_node][1]:
                            while_dict[current_node][1] = while_dict[current_node][0]
                    # get the node executed when cond is not true for while anymore
                node_to_exit = max(succ)
                for s in succ:
                    label = self.cfg.edges[decision_node, s]['label']
                    if self.interpretCondition(label):
                        # rebooting compteur for node
                        if s == node_to_exit and current_node in self.cfgparser.labelsWhile:
                            while_dict[current_node][0] = 0
                        current_node = s
            # else the edge represents an assigment
            # however if the assigment has a while as successor, it means there is
            # a condition to evaluate
            elif current_node in self.cfgparser.labelsAssigns:
                succ = [s for s in self.cfg.successors(current_node)]
                if len(succ) == 1:
                    label = self.cfg.edges[current_node, succ[0]]['label']
                    self.interpretAssigments(label)
                    current_node = succ[0]
            # else finally the node must BE the empty label with no successfors
            else:
                succ = [s for s in self.cfg.successors(current_node)]
                if len(succ) == 0:
                    current_node = target_node
                else:
                    raise Exception('Target node could not be reached')
            self.visited.append(current_node)
        return while_dict

    def interpretCfg(self):
        """
        Interpret the full CFG
        """
        target_node = self.getTargetNode()
        current_node = self.getSourceNode()
        self.visited.append(current_node)
        while current_node != target_node:
            # see if there is actually a decision to take when node is (if|while)
            if current_node in self.cfgparser.labelsIf or \
               current_node in self.cfgparser.labelsWhile :
                decision_node = current_node
                succ = [s for s in self.cfg.successors(current_node)]
                for s in succ:
                    label = self.cfg.edges[decision_node, s]['label']
                    if self.interpretCondition(label):
                        current_node = s
            # else the edge represents an assigment
            # however if the assigment has a while as successor, it means there is
            # a condition to evaluate
            elif current_node in self.cfgparser.labelsAssigns:
                succ = [s for s in self.cfg.successors(current_node)]
                if len(succ) == 1:
                    label = self.cfg.edges[current_node, succ[0]]['label']
                    self.interpretAssigments(label)
                    current_node = succ[0]
            # else finally the node must BE the empty label with no successfors
            else:
                succ = [s for s in self.cfg.successors(current_node)]
                if len(succ) == 0 :
                    current_node = target_node
                else:
                    raise Exception('Target node could not be reached')
            self.visited.append(current_node)

