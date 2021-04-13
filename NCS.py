from interpreter.NCSInterpreter import NCSInterpreter
from lexer.NCSLexer import NCSLexer
from parser.NCSParser import NCSParser


def main():
    with open('temp_test.ncs', 'r') as f:
        source_code = f.read()
        lexer = NCSLexer(source_code)
        lexer.run()
        if not lexer.success:
            return False

        parser = NCSParser(lexer.tableOfSymb)
        parser.run()
        if not parser.success:
            return False
        translator = NCSInterpreter(parser.postfix_code, lexer.tableOfId, lexer.tableOfConst, to_view=True)
        translator.run()
        if translator.success:
            print(translator.table_of_ids)
            print(translator.table_of_consts)


if __name__ == '__main__':
    main()
