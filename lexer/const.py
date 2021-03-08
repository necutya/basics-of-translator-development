# Таблица лексем
tableOfLanguageTokens = {
    'main': 'keyword', 'int': 'keyword', 'float': 'keyword', 'bool': 'keyword',
    'scan': 'keyword', 'print': 'keyword', 'for': 'keyword', 'if': 'keyword',

    'true': 'bool', 'false': 'bool',

    '=': 'assign_op', '-': 'add_op', '+': 'add_op', '*': 'mult_op', '/': 'mult_op',
    '^': 'pow_op', "<": "rel_op", "<=": "rel_op", "==": "rel_op", "!=": "rel_op", ">=": "rel_op",
    ">": "rel_op", "&&": "bool_op", "||": "bool_op",

    '(': 'brackets_op', ')': 'brackets_op', '{': 'curve_brackets_op', '}': 'curve_brackets_op',

    '.': 'dot', ',': 'comma', ';': 'op_end', ' ': 'ws', '\t': 'ws', '\n': 'nl',
}

# Таблица идентификаторов и констант
tableIdentFloatInt = {2: 'ident', 5: 'float', 6: 'int', 19: 'int'}

classes = {
    "Letter": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_",
    "NonZeroDigit": "123456789",
    "ZeroDigit": "0",
    "Dot": '.',
    "WhiteSep": " \t",
    "Newline": "\n",
    "Operators": "+-*/^(){}=><!;,&|"
}

# δ - state-transition_function
stf = {
    (0, 'WhiteSep'): 0,  # WhiteSep
    (0, 'Letter'): 1, (1, 'Letter'): 1, (1, 'ZeroDigit'): 1, (1, 'NonZeroDigit'): 1, (1, 'other'): 2,  # Ident
    (0, 'NonZeroDigit'): 3, (3, 'ZeroDigit'): 3, (3, 'NonZeroDigit'): 3, (3, 'Dot'): 4, (3, 'other'): 6,
    (4, 'ZeroDigit'): 4, (4, 'NonZeroDigit'): 4, (4, 'other'): 5, # Int or Float
    (0, '!'): 7, (7, '='): 8, (7, 'other'): 102,  # not equals or error
    (0, '='): 9, (0, '>'): 9, (0, '<'): 9, (9, '='): 10, (9, 'other'): 11,  # relative ops and is
    (0, ','): 12, (0, ';'): 12, (0, '+'): 12, (0, '-'): 12, (0, '*'): 12, (0, '/'): 12, (0, '^'): 12, (0, '('): 12,
    (0, ')'): 12, (0, '{'): 12, (0, '}'): 12,  # Operators
    (0, '&'): 14, (14, '&'): 15, (14, 'other'): 103,  # bool and
    (0, '|'): 16, (16, '|'): 17, (16, 'other'): 104,  # bool or
    (0, 'ZeroDigit'): 18, (18, 'ZeroDigit'): 105, (18, 'NonZeroDigit'): 105, (18, 'Letter'): 105, (18, 'other'): 19,
    (18, 'Dot'): 4, # Float or zero or error
    (0, 'Newline'): 13,  # Separator
    (0, 'other'): 101  # error
}

states = {
    'initial': (0,),
    'star': (2, 5, 6, 11),
    'error': (101, 102, 103, 104, 105),
    'final': (2, 5, 6, 8, 10, 11, 12, 13, 15, 17, 19, 101, 102, 103, 104, 105),
    'newLine': (13,),
    'operator': (8, 10, 11, 12, 15, 17),
    'double_operators': (8, 10, 15, 17),
    'const': (5, 6, 19),
    'identifier': (2,),
}

errors_description = {
    101: 'NCSLexerError: у рядку %s неочікуваний символ %s',
    102: 'NCSLexerError: у рядку %s очікувався символ =, а не %s',
    103: 'NCSLexerError: у рядку %s очікувався символ &, а не %s',
    104: 'NCSLexerError: у рядку %s очікувався символ |, а не %s',
    105: 'NCSLexerError: у рядку %s за нулем не може слідувати символ %s',
}
