from lexer.NCSLexer import NCSLexer
from parser.NCSParser import NCSParser


def main():
    with open('temp_test.ncs', 'r') as f:
        source_code = f.read()
        lexer = NCSLexer(source_code)
        lexer.run()
        if not lexer.success[0]:
            return False
        parser = NCSParser(lexer.tableOfSymb)
        parser.run()


if __name__ == '__main__':
    main()
