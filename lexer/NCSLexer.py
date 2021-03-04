from lexer.const import *


class NCSLexer:
    tableOfLanguageTokens = tableOfLanguageTokens
    tableIdentFloatInt = tableIdentFloatInt
    classes = classes
    stf = stf
    states = states

    def __init__(self, nsc_code):
        # Initial code
        self.source_code = nsc_code + " " # to read last symbol
        self.lenCode = len(self.source_code)

        # Tables
        self.tableOfId = {}
        self.tableOfConst = {}
        self.tableOfSymb = {}

        # Current state
        self.state = states["initial"][0]

        # Needed variables
        self.numLine = 1
        self.numChar = 0
        self.char = ''
        self.lexeme = ''

        self.success = (True, 'Lexer')

    def start(self):
        try:
            while self.numChar < self.lenCode:
                self.char = self._next_char()  # read symbol
                self.state = NCSLexer._next_state(self.state, NCSLexer._class_of_char(self.char))  # get next state
                # print(NCSLexer._is_final_state(self.state))
                if NCSLexer._is_initial_state(self.state):
                    self.lexeme = ''  # якщо стан НЕ заключний, а стартовий - нова лексема
                elif NCSLexer._is_final_state(self.state):  # якщо стан заключний
                    self.processing()  # виконати семантичні процедури
                else:
                    self.lexeme += self.char  # якщо стан НЕ закл. і не стартовий - додати символ до лексеми
            print('Lexer: Лексичний аналіз завершено успішно')
        except SystemExit as e:
            # Встановити ознаку неуспішності
            self.success = (False, 'Lexer')
            # Повідомити про факт виявлення помилки
            print('NCSLexer: Аварійне завершення програми з кодом {0}'.format(e))

    def processing(self):

        if self.state in NCSLexer.states['newLine']:
            self.numLine += 1
            self.state = NCSLexer.states['initial'][0]

        elif self.state in (NCSLexer.states['const'] + NCSLexer.states['identifier']):
            token = NCSLexer._get_token(self.state, self.lexeme)
            if token != 'keyword':
                index = self._get_index()
                self.tableOfSymb[len(self.tableOfSymb) + 1] = (self.numLine, self.lexeme, token, index)
            else:
                self.tableOfSymb[len(self.tableOfSymb) + 1] = (self.numLine, self.lexeme, token, '')

            self.lexeme = ''
            self.state = NCSLexer.states['initial'][0]

            self._put_char_back()
        elif self.state in NCSLexer.states['operator']:
            if not self.lexeme or self.state in NCSLexer.states['double_operators']:
                self.lexeme += self.char
            token = NCSLexer._get_token(self.state, self.lexeme)
            self.tableOfSymb[len(self.tableOfSymb) + 1] = (self.numLine, self.lexeme, token, '')
            if self.state in NCSLexer.states['star']:
                self._put_char_back()
            self.lexeme = ''  # In order to get to operators together
            self.state = NCSLexer.states['initial'][0]

        elif self.state in NCSLexer.states['error']:
            self.fail()


    def fail(self):
        if self.state == 101:
            print('NCSLexer: у рядку ', self.numLine, ' неочікуваний символ ' + self.char)
            exit(101)
        if self.state == 102:
            print('NCSLexer: у рядку ', self.numLine, ' очікувався символ =, а не ' + self.char)
            exit(102)

    def print_symbols_table(self):
        print('|#\tЛексема\tТокен\tІндекс|')
        for value in self.tableOfSymb.values():
            print('|{}\t{}\t{}\t{}'.format(*value))

    def print_ids_table(self):
        # print('|#\tЛексема\tТокен\tІндекс|')
        # for value in self.tableOfSymb.values():
        #     print('|{}\t{}\t{}\t{}|'.format(*value))
        print(self.tableOfId)

    def print_const_table(self):
        # print('|#\tЛексема\tТокен\tІндекс|')
        # for value in self.tableOfSymb.values():
        #     print('|{}\t{}\t{}\t{}|'.format(*value))
        print(self.tableOfConst)

    def _get_index(self):
        if self.state in self.states['identifier']:
            return NCSLexer._get_or_set_id_index(self.lexeme, self.tableOfId)
        elif self.state in self.states['const']:
            return NCSLexer._get_or_set_id_index(self.lexeme, self.tableOfConst)

    def _next_char(self):
        char = self.source_code[self.numChar]
        self.numChar += 1
        return char

    def _put_char_back(self):
        self.numChar -= 1

    @staticmethod
    def _get_token(state, lexeme):
        try:
            return NCSLexer.tableOfLanguageTokens[lexeme]
        except KeyError:
            return NCSLexer.tableIdentFloatInt[state]

    @staticmethod
    def _is_initial_state(state):
        return state in NCSLexer.states["initial"]

    @staticmethod
    def _is_final_state(state):
        return state in NCSLexer.states["final"]

    @staticmethod
    def _next_state(state, clazz):
        try:
            return NCSLexer.stf[(state, clazz)]
        except KeyError:
            return NCSLexer.stf[(state, 'other')]

    @staticmethod
    def _class_of_char(char):
        for key, value in classes.items():
            if char in value:
                if key == "Operators":
                    return char
                else:
                    return key
        return "Any classes does not have this symbol"

    @staticmethod
    def _get_or_set_id_index(lexeme, table):
        index = table.get(lexeme)
        if not index:
            index = len(table) + 1
            table[lexeme] = index
        return index


if __name__ == '__main__':
    try:
        with open('../test4_error.ncs', 'r') as f:
            sourceCode = f.read()
            lexer = NCSLexer(sourceCode)
            lexer.start()
            lexer.print_symbols_table()
    except FileNotFoundError as e:
        print("Неправильний шлях до файлу.")
