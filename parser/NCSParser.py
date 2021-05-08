from parser.const import (
    parser_errors as errors,
    parser_warnings as warnings
)


class NCSParser:

    def __init__(self, table_of_symbols, table_of_labels, table_of_ids, postfix_code, to_view=False):
        self.table_of_symbols = table_of_symbols
        self.table_of_labels = table_of_labels
        self.table_of_ids = table_of_ids
        self.len_table_of_symbols = len(self.table_of_symbols)
        self.row_number = 1

        self.success = True
        self.postfix_code = postfix_code
        self.to_view = to_view

        self.for_loop_temp_vars = []

    def run(self):
        self.success = self.parse_program()

    @staticmethod
    def warning_parse(warning: str, *args):
        print("\033[33m")
        warning_msg = warnings.get(warning, None)
        print(warning_msg % args)
        print('\n\033[0m')

    @staticmethod
    def fail_parse(error: str, *args):
        print("\033[31m")
        error_msg, error_code = errors.get(error, (None, None))
        print(error_msg % args)
        print('\n\033[0m')
        exit(error_code)

    @staticmethod
    def print_lexeme_info(line_number, lex, tok, indent=''):
        print(indent + f'в рядку {line_number} - {(lex, tok)}')

    def print_translator_step(self, lex):
        to_print = "\nTranslator step\n\tlexeme: %s\n\ttable_of_symbols[%s]: %s\n\tpostfix_code %s\n"
        print(to_print % (lex, self.row_number, self.table_of_symbols[self.row_number], self.postfix_code))

    def get_symbol(self):
        if self.row_number > self.len_table_of_symbols:
            NCSParser.fail_parse('eop', self.row_number)
        return self.table_of_symbols[self.row_number][0:-1]

    def parse_token(self, lexeme, token, indent=''):
        line_number, lex, tok = self.get_symbol()

        self.row_number += 1

        if lex == lexeme and tok == token:
            # NCSParser.print_lexeme_info(line_number, lex, tok, indent)
            return True
        else:
            NCSParser.fail_parse('tokens', line_number, lex, tok, lexeme, token)
            return False

    def parse_program(self):
        try:
            self.parse_token('main', 'keyword')
            self.parse_token('{', 'curve_brackets_op')

            self.parse_statements_list()

            if self.row_number < self.len_table_of_symbols:
                NCSParser.fail_parse('after_eop')
            else:
                self.parse_token('}', 'curve_brackets_op')

        except SystemExit as e:
            print("\033[31m", end='')
            print('Parser: Аварійне завершення програми з кодом {0}'.format(e))
            print('\n\033[0m', end='')
            return False

        print("\033[32m", end='')
        print('NCSParser: Синтаксичний аналіз завершився успішно')
        print('\n\033[0m', end='')
        return True

    def parse_statements_list(self):
        while self.parse_statement():
            pass
        return True

    def parse_statement(self):
        line_number, lex, tok = self.get_symbol()

        if tok == 'ident':
            self.postfix_code.append((lex, tok, None))
            if self.to_view:
                self.print_translator_step(lex)

            self.row_number += 1
            if self.get_symbol()[-1] == 'assign_op':
                self.parse_assign()
            else:
                # Statement has no effect
                self.row_number -= 1
                self.parse_expression()
                NCSParser.warning_parse('no_effect', line_number)

            self.parse_token(';', 'op_end', '\t' * 3)
            return True

        elif lex == 'scan' and tok == 'keyword':
            self.parse_scan()
            self.parse_token(';', 'op_end', '\t' * 3)
            return True

        elif lex == 'print' and tok == 'keyword':
            self.parse_print()
            self.parse_token(';', 'op_end', '\t' * 3)
            return True

        elif lex in ('int', 'float', 'bool') and tok == 'keyword':
            self.parse_declaration()
            self.parse_token(';', 'op_end', '\t' * 3)
            return True


        elif lex == 'for' and tok == 'keyword':
            self.parse_for()
            return True

        elif lex == 'if' and tok == 'keyword':
            self.parse_if()
            return True

        elif lex == '}' and tok == 'curve_brackets_op':
            return False

        else:
            # Statement has no effect
            self.parse_expression()
            self.parse_token(';', 'op_end', '\t' * 3)
            NCSParser.warning_parse('no_effect', line_number)
            return True

    def parse_scan(self):

        line_number, lex, tok = self.get_symbol()
        self.row_number += 1

        self.parse_token('(', 'brackets_op', '\t' * 4)
        self.parse_io_content(allow_arithm_expr=False)
        self.parse_token(')', 'brackets_op', '\t' * 4)

    def parse_print(self):
        line_number, lex, tok = self.get_symbol()
        self.row_number += 1

        self.parse_token('(', 'brackets_op', '\t' * 4)
        self.parse_io_content()
        self.parse_token(')', 'brackets_op', '\t' * 4)

    def parse_io_content(self, allow_arithm_expr=True):
        line_number, lex, tok = self.get_symbol()
        if tok in ('ident', 'int', 'float',  'bool') and allow_arithm_expr:
            self.parse_expression()
        elif tok == 'ident':
            self.postfix_code.append(((lex, tok, None)))
            self.row_number += 1
        else:
            NCSParser.fail_parse('not_expected', line_number, lex, tok,
                                 "ідентифікатор (ident)")

        line_number, lex, tok = self.get_symbol()
        if lex == ')' and tok == 'brackets_op':
            if allow_arithm_expr:
                self.postfix_code.append(('OUT', 'out', None))
            else:
                self.postfix_code.append(('INPUT', 'input', None))
            return True

        elif lex == ',' and tok == 'comma':
            if allow_arithm_expr:
                self.postfix_code.append(('OUT', 'out', None))
            else:
                self.postfix_code.append(('INPUT', 'input', None))
            self.row_number += 1
            self.parse_io_content(allow_arithm_expr)

    def parse_assign(self):

        if self.parse_token('=', 'assign_op', '\t' * 3):
            self.parse_expression()
            self.postfix_code.append(("=", 'assign_op', None))
            if self.to_view:
                self.print_translator_step('=')
            return True
        else:
            return False

    def parse_expression(self, required=False):
        self.parse_arithm_expression()

        while self.parse_bool_expr():
            pass

        return True

    def parse_bool_expr(self, required=False):
        line_number, lex, tok = self.get_symbol()
        if tok in ('rel_op', 'bool_op'):
            self.row_number += 1
            self.parse_arithm_expression()
            self.postfix_code.append((lex, tok, None))

            return True
        elif required:
            NCSParser.fail_parse('not_expected', line_number, lex, tok,
                                 required)
        else:
            return False

    def parse_arithm_expression(self):
        self.parse_term()

        while True:
            line_number, lex, tok = self.get_symbol()
            if tok == 'add_op':
                self.row_number += 1
                self.parse_term()
                self.postfix_code.append((lex, tok, None))
                if self.to_view:
                    self.print_translator_step(lex)
            else:
                break
        return True

    def parse_term(self):
        self.parse_power()
        while True:
            line_number, lex, tok = self.get_symbol()
            if tok in 'mult_op':
                self.row_number += 1
                self.parse_power()
                self.postfix_code.append((lex, tok, None))
                if self.to_view:
                    self.print_translator_step(lex)
            else:
                break
        return True

    def parse_power(self):
        self.parse_factor()
        while True:
            line_number, lex, tok = self.get_symbol()
            if tok == 'pow_op':
                self.row_number += 1
                self.parse_factor()
                self.postfix_code.append((lex, tok, None))
                if self.to_view:
                    self.print_translator_step(lex)
            else:
                break
        return True

    def parse_factor(self):
        has_unar = False
        line_number, lex, tok = self.get_symbol()
        if lex == '-':
            has_unar = True
            self.row_number += 1
            line_number, lex, tok = self.get_symbol()

        if tok in ('int', 'float', 'bool', 'ident'):
            self.postfix_code.append((lex, tok, None))
            if self.to_view:
                self.print_translator_step(lex)

            if has_unar:
                self.postfix_code.append(('@', 'unar_minus', None))
                if self.to_view:
                    self.print_translator_step(lex)

            self.row_number += 1

        elif lex == '(':
            self.row_number += 1
            self.parse_arithm_expression()
            self.parse_token(')', 'brackets_op', '\t' * 7)
        else:
            NCSParser.fail_parse('not_expected', line_number, lex, tok,
                                 'rel_op, int, float, ident або \'(\' Expression \')\'')
        return True

    def parse_declaration(self):
        # Parse type
        line_number, lex, tok = self.get_symbol()
        self.row_number += 1
        if lex in ('int', 'float', 'bool') and tok == 'keyword':
            self.parse_var_list(lex)

        else:
            NCSParser.fail_parse('not_expected', line_number, lex, tok,
                                 'int, float або bool.')

    def parse_var_list(self, var_type):
        line_number, lex, tok = self.get_symbol()
        self.row_number += 1

        if tok == 'ident':
            self.postfix_code.append((lex, tok, var_type))
        else:
            NCSParser.fail_parse('not_expected', line_number, lex, tok,
                                 "ідентифікатор (ident)")

        line_number, lex, tok = self.get_symbol()
        if lex == '=' and tok == 'assign_op':
            self.parse_assign()
            line_number, lex, tok = self.get_symbol()

        if lex == ',' and tok == 'comma':
            self.row_number += 1
            self.parse_var_list(var_type)

        elif lex == ';' and tok == 'op_end':
            return True

    def parse_if(self):
        self.parse_token('if', 'keyword', '\t' * 4)

        self.parse_expression(required=True)

        line_number, lex, tok = self.get_symbol()
        m1 = self.create_label()

        if lex == '{' and tok == 'curve_brackets_op':

            self.postfix_code.append((*m1, None))
            self.postfix_code.append(('JF', 'jf', None))

            self.row_number += 1
            self.parse_statements_list()
            self.parse_token('}', 'curve_brackets_op', '\t' * 4)

            self.set_label_val(m1)
            self.postfix_code.append((*m1, None))
            self.postfix_code.append((':', 'colon', None))
        else:
            self.postfix_code.append((*m1, None))
            self.postfix_code.append(('JF', 'jf', None))

            self.parse_statement()

            self.set_label_val(m1)
            self.postfix_code.append((*m1, None))
            self.postfix_code.append((':', 'colon', None))

    def parse_for(self):
        step = self.create_label()
        end = self.create_label()

        # print('\t' * 3, 'parse_for', sep='')
        self.parse_token('for', 'keyword', '\t' * 4)
        self.parse_token('(', 'brackets_op', '\t' * 4)
        self.parse_ind_expression(step, end)
        self.parse_token(')', 'brackets_op', '\t' * 4)

        line_number, lex, tok = self.get_symbol()

        if lex == '{' and tok == 'curve_brackets_op':
            self.row_number += 1
            self.parse_statements_list()

            self.parse_token('}', 'curve_brackets_op', '\t' * 4)



        else:
            self.parse_statement()

        temp = self.for_loop_temp_vars.pop()
        self.postfix_code.append((temp[1], 'ident', None))
        self.postfix_code.append((temp[0], 'ident', None))
        self.postfix_code.append(('=', 'assign_op', None))

        self.postfix_code.append((*step, None))
        self.postfix_code.append(('JMP', 'jump', None))
        self.set_label_val(end)
        self.postfix_code.append((*end, None))
        self.postfix_code.append((':', 'colon', None))

    def parse_ind_expression(self, step, end):

        line_number, lex, tok = self.get_symbol()

        if tok == 'ident':

            self.postfix_code.append((lex, tok, None))
            self.row_number += 1
            self.parse_assign()

            self.set_label_val(step)
            self.postfix_code.append((*step, None))
            self.postfix_code.append((':', 'colon', None))

        else:
            NCSParser.fail_parse('not_expected', line_number, lex, tok,
                                 "ідентифікатор (ident)")

        self.parse_token(';', 'op_end', '\t' * 5)
        self.parse_expression(required=True)
        self.parse_token(';', 'op_end', '\t' * 5)

        self.postfix_code.append((*end, None))
        self.postfix_code.append(('JF', 'jf', None))

        if tok == 'ident':
            _len = len(self.for_loop_temp_vars)
            self.for_loop_temp_vars.append((f'temp_{_len}', lex))
            self.table_of_ids[f'temp_{_len}'] = (len(self.table_of_ids), 'int', 'null')
            self.postfix_code.append((f'temp_{_len}', 'ident', 'int'))

            self.row_number += 1
            self.parse_assign()
        else:
            NCSParser.fail_parse('not_expected', line_number, lex, tok,
                                 "ідентифікатор (ident)")

    def create_label(self) -> tuple:
        label_number = len(self.table_of_labels) + 1
        lexeme = f"m{label_number}"
        if not self.table_of_labels.get(lexeme):
            self.table_of_labels[lexeme] = 'val_undef'
            return lexeme, 'label'
        NCSParser.fail_parse('label_conflict')

    def set_label_val(self, m1: tuple) -> None:
        self.table_of_labels[m1[0]] = len(self.postfix_code)
