import traceback

from interpreter.stack import Stack


class NCSInterpreter:
    operator_mapping = {
        '+': '+', '-': '-', '*': '*', '/': '/', '^': '**', '=': '=',
        '@': '-',
        '&&': 'and', '||': 'or',
        '<': '<', '<=': '<=', '==': '==', '!=': '!=', '>=': '>=', '>': '>',
    }
    __header_for_errors = 'NCSInterpreter Error:'
    run_time_errors = {
        'mismatches_types': ('%s\n\tТипи операндів відрізняються: %s %s %s.', 1),
        'undefined_var': ('%s\n\tНевідома змінна \'%s\'.', 2),
        'zero_division': ('%s\n\tДілення на нуль: %s %s %s.', 3),
        'invalid_operand_types': ('%s\n\tНевалідний тип одного або декількох операндів: %s %s %s.', 4),
        'nullable': ('%s\n\tНевизначена зміна \'%s\' не може використовуватись в операціях.', 5),
        'invalid_operator': ('%s\n\tНевідомий світу оператор %s', 322),
    }

    def __init__(self, postfix_code, table_of_ids, table_of_consts, to_view=False):
        self.postfix_code = postfix_code
        self.table_of_ids = table_of_ids
        self.table_of_consts = table_of_consts

        self.stack = Stack()
        self.to_view = to_view

        self.success = True

    def step_to_print(self, step, lex, tok):
        print('\nКрок інтерпретації: {0}'.format(step))
        if tok in ('int', 'float'):
            print(f'Лексема: {(lex, tok)} у таблиці констант: {lex}:{self.table_of_consts[lex]}')
        elif tok in ('ident',):
            print(f'Лексема: {(lex, tok)} у таблиці ідентифікаторів: {lex}:{self.table_of_ids[lex]}')
        else:
            print(f'Лексема: {(lex, tok)}')

        print(f'postfixCode={self.postfix_code}')
        print(self.stack)

    def run(self):
        self.success = self.__interpret()

    def __interpret(self):
        try:
            for i in range(len(self.postfix_code)):
                lex, tok, var_type = self.postfix_code.pop(0)
                if tok in ('int', 'float', 'bool', 'ident'):
                    self.stack.push((lex, tok))
                    # to init a variable
                    if tok == 'ident' and var_type:
                        self.table_of_ids[lex] = (
                            self.table_of_ids[lex][0],
                            var_type,
                            self.table_of_ids[lex][2]
                        )
                else:
                    self.__do_action(lex, tok)

                if self.to_view:
                    self.step_to_print(i + 1, lex, tok)
        except SystemExit as e:
            print("\033[31m")
            print('Parser: Аварійне завершення програми з кодом {0}'.format(e))
            print('\n\033[0m')
            return False
        except Exception as e:
            print(e)
            print(traceback.format_exc())
        else:
            print("\033[32m", end='')
            print('NCSInterpreter: Інтерпретатор завершив роботу успішно')
            print('\n\033[0m', end='')
            return True

    def __do_action(self, lex, tok):
        if lex == "=" and tok == "assign_op":
            lex_right, tok_right = self.stack.pop()
            value_right, type_right = self.__check_token_and_lexeme(tok_right, lex_right)
            lex_left, tok_left = self.stack.pop()
            _, type_left = self.__check_token_and_lexeme(tok_right, lex_right)

            if tok_left == 'ident':
                _type = self.table_of_ids[lex_left][1]
            else:
                _type = type_left

            self.table_of_ids[lex_left] = (
                self.table_of_ids[lex_left][0],
                _type,
                eval(f"{_type}({value_right})")
            )
        elif tok in ('add_op', 'mult_op', 'pow_op'):
            lex_right, tok_right = self.stack.pop()
            lex_left, tok_left = self.stack.pop()

            if (tok_right, tok_left) in (('int', 'float'), ('float', 'int')):
                NCSInterpreter.fail_run_time('mismatches_types', lex_left, lex, lex_right)

            self.__process_operator((lex_left, tok_left), lex, (lex_right, tok_right))

        elif tok == 'unar_minus':
            lex_right, tok_right = self.stack.pop()
            try:
                lex_left, tok_left = 0, self.table_of_ids[lex_right][1]
            except KeyError:
                lex_left, tok_left = 0, self.table_of_consts[lex_right][1]

            # add 0 to table of consts
            self.push_to_table_of_consts(tok_left, lex_left)

            self.__process_operator((lex_left, tok_left), lex, (lex_right, tok_right))

        elif tok in ('rel_op', 'bool_op'):
            lex_right, tok_right = self.stack.pop()
            lex_left, tok_left = self.stack.pop()

            if tok == 'bool_op' and (tok_right, tok_left) != ('bool', 'bool'):
                NCSInterpreter.fail_run_time('invalid_operand_types', lex_left, lex, lex_right)

            if tok == 'rel_op':
                if lex not in ('==', '!=') and not all((tok in ('int', 'float') for tok in (tok_right, tok_left))):
                    NCSInterpreter.fail_run_time('invalid_operand_types', lex_left, lex, lex_right)

            self.__process_operator((lex_left, tok_left), lex, (lex_right, tok_right))

    def __process_operator(self, left, lex, right):
        lex_left, tok_left = left
        lex_right, tok_right = right

        value_left, type_left = self.__check_token_and_lexeme(tok_left, lex_left)
        value_right, type_right = self.__check_token_and_lexeme(tok_right, lex_right)

        self.__run_operator((lex_left, type_left, value_left), lex, (lex_right, type_right, value_right))

    def __check_token_and_lexeme(self, token, lexeme):
        lexeme = str(lexeme)
        if token == 'ident':
            if NCSInterpreter.__is_undefined(self.table_of_ids[lexeme][1]):
                NCSInterpreter.fail_run_time('undefined_var', lexeme)

            return self.table_of_ids[lexeme][2], self.table_of_ids[lexeme][1]
        else:
            return self.table_of_consts[lexeme][2], self.table_of_consts[lexeme][1]

    def __run_operator(self, left, lex, right):
        lex_left, type_left, value_left = left
        lex_right, type_right, value_right = right
        if operator := NCSInterpreter.operator_mapping.get(lex, None):
            try:
                print(f"CALC: {value_left} {operator} {value_right}")
                calc_result = eval(f"{value_left} {operator} {value_right}")
            except ZeroDivisionError:
                NCSInterpreter.fail_run_time('zero_division', value_left, operator, value_right)
            else:
                if lex == "/" and type_right:
                    calc_result = int(calc_result)
                if lex in ('<', '<=', '==', '!=', '>=', '>',):
                    _type = 'bool'
                else:
                    _type = type_left
                self.stack.push((calc_result, _type))
                self.push_to_table_of_consts(_type, calc_result)
        else:
            # \(*_*)/ how it has been happened
            NCSInterpreter.fail_run_time('invalid_operator', operator)

    def push_to_table_of_consts(self, token, value):
        if not self.table_of_consts.get(str(value), None):
            index = len(self.table_of_consts) + 1
            self.table_of_consts[str(value)] = (index, token, value)

    @staticmethod
    def __is_undefined(variable_type: str) -> bool:
        return variable_type == "undefined"

    @staticmethod
    def __is_nullable(variable_value: str) -> bool:
        return variable_value == 'null'

    @staticmethod
    def fail_run_time(error: str, *args) -> None:
        print("\033[31m")
        error_msg, error_code = NCSInterpreter.run_time_errors.get(error, (None, None))
        print(error_msg % (NCSInterpreter.__header_for_errors, *args))
        print('\n\033[0m')
        exit(error_code)
