from interpreter.NCSInterpreter import NCSInterpreter
from lexer.NCSLexer import NCSLexer
from parser.NCSParser import NCSParser


class NCS:
    def __init__(self, file_name: str):
        source_code = NCS.__read_file(file_name)

        self.__table_of_ids: dict = {}
        self.__table_of_consts: dict = {}
        self.__table_of_symbols: dict = {}
        self.__table_of_labels: dict = {}

        self.__source_code: str = source_code
        self.__postfix_code: list = []

        self.components = (
            (NCSLexer, (source_code, self.__table_of_ids, self.__table_of_consts, self.__table_of_symbols)),
            (NCSParser, (self.__table_of_symbols, self.__table_of_labels,  self.__table_of_ids, self.__postfix_code, False)),
            (NCSInterpreter, (self.__postfix_code, self.__table_of_ids, self.__table_of_consts, self.__table_of_labels, False))
        )

    def run(self):
        for component_class, args in self.components:
            component = component_class(*args)
            component.run()
            if isinstance(component, NCSInterpreter):
                print(self.__table_of_symbols)
                print(self.__table_of_ids)
                print(self.__table_of_consts)
                print(self.__table_of_labels)
            if not component.success:
                print("\033[31m", end='')
                print("Помилка під час виконання програми. Виконанная аварійно звершено.")
                print('\033[0m', end='')
                exit(2)

    @staticmethod
    def __read_file(filename: str) -> str:
        try:
            with open(filename, 'r') as f:
                return f.read()
        except Exception as e:
            print(f"Помилка при зчитуванні файлу:\n\t{e}")
            exit(1)

if __name__ == '__main__':
    ncs = NCS('temp_test.ncs')
    ncs.run()