class Datatest:
    """ Class to implement a data test (donnée de jeu) by storing all assigments in string format for the interpreter"""

    def __init__(self, text):
        """ a datatest will just store a list of assigments in string format like X=X_i"""
        """ therefore assigments will hold ["X=Xi", "Y=Yi"] """
        self.text = text
        self.assigments = []
        # ini_source is a code piece with label 0, used for main-ta and main-d when we didn't have the cfg yet
        self.ini_source = '0: '
        # ini_assigns is just the block (list) initial assigments
        self.ini_assigns = ''

    def parse(self):
        n = len(self.text)
        """ check that the datatest begins by ( and ends by ) """
        if self.text[0] != '(' or self.text[n-1] != ')':
            self.error()
        assigments = self.text[1:n-1].split(',')
        for assigment in assigments:
            self.add(assigment)
            self.ini_source = self.ini_source + assigment + ' ; '
            self.ini_assigns = self.ini_assigns + assigment + ' ; '

    def add(self, assigment):
        self.assigments.append(assigment)

    def error(self):
        raise Exception('Incorrect syntax to describe a datatest')

class DatatestSet:
    """ Class to implement a set of data tests (jeu de test) by storing all datatests in class format Datatest"""

    def __init__(self, text):
        """ Initialize from text source that must contain a set of datasets"""
        """ Remove comments by spliting lines and removing line with #"""
        lines = text.splitlines()
        text = ''
        for line in lines:
            if line.find('#') == -1:
                """ Only adding lines without # """
                text = text+line
        self.text = text
        self.datatests = []

    def parse(self):
        n = len(self.text)
        """ Check that the format is correct i.e. begins by { and ends by } """
        if self.text[0] != '{' or self.text[n-1] != '}':
            self.error()
        """ get datatests by splitting by comma"""
        datatests = self.text[1:n-1].split(';')
        for datatest in datatests:
            self.add(datatest)

    def add(self, datatest):
        """ Add datatest to the list """
        self.datatests.append(Datatest(datatest))

    def error(self):
        raise Exception('Incorrect syntax to describe set of datatests')

""" TESTING CODE TO CHECK THAT PARSERS WORKS"""
"""
text = '{(X=1,Y=2);(X=-3)}'
dp = DatatestParser(text)
dp.parse()
for datatest in dp.datatests:
    datatest.parse()
    for assigment in datatest.assigments:
        print(assigment)
"""