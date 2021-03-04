# Таблица лексем
tableOfLanguageTokens = {
    'main': 'keyword',
    'int': 'keyword',
    'float': 'keyword',
    'bool': 'keyword',
    'scan': 'keyword',
    'print': 'keyword',
    'for': 'keyword',
    'if': 'keyword',

    'true': 'boolvar',
    'false': 'boolvar',

    '=': 'assign_op',
    '-': 'add_op',
    '+': 'add_op',
    '*': 'mult_op',
    '/': 'mult_op',
    '^': 'pow_op',
    "<": "rel_op",
    "<=": "rel_op",
    "==": "rel_op",
    "!=": "rel_op",
    ">=": "rel_op",
    ">": "rel_op",

    '(': 'brackets_op',
    ')': 'brackets_op',
    '{': 'curve_brackets_op',
    '}': 'curve_brackets_op',

    '.': 'dot',
    ',': 'comma',
    ';': 'op_end',
    ' ': 'ws',
    '\t': 'ws',
    '\n': 'nl',
}

# Таблица идентификаторов и констант
tableIdentFloatInt = {2: 'ident', 5: 'float', 6: 'int'}

classes = {
    "Letter": "abcdefghijklmnopqrstuvwxyz_",
    # "NonZeroDigit": "123456789",
    "Digit": "0123456789",
    "Dot": '.',
    "WhiteSep": " \t",
    "Newline": "\n",
    "Operators": "+-*/^(){}=><!;,"
}

# δ - state-transition_function
stf = {
    (0, 'WhiteSep'): 0,  # WhiteSep
    (0, 'Letter'): 1, (1, 'Letter'): 1, (1, 'Digit'): 1, (1, 'other'): 2,  # Ident
    (0, 'Digit'): 3, (3, 'Digit'): 3, (3, 'Dot'): 4, (3, 'other'): 6, (4, 'Digit'): 4, (4, 'other'): 5,
    # Int or Float
    (0, '!'): 7, (7, '='): 8, (7, 'other'): 102,  # not equals or error
    (0, '='): 9, (0, '>'): 9, (0, '<'): 9, (9, '='): 10, (9, 'other'): 11,  # relative ops and is
    (0, ','): 12, (0, ';'): 12, (0, '+'): 12, (0, '-'): 12, (0, '*'): 12, (0, '/'): 12, (0, '^'): 12, (0, '('): 12, (0, ')'): 12,
    (0, '{'): 12, (0, '}'): 12,  # Operators
    (0, 'Newline'): 13,  # Separator
    (0, 'other'): 101  # error
}

newLineState = 13
operatorsStates = 8, 11, 12

states = {
    'initial': (0,),
    'star': (2, 5, 6, 11),
    'error': (101, 102),
    'final': (2, 5, 6, 8, 10, 11, 12, 13, 101, 102),
    'newLine': (13,),
    'operator': (8, 10, 11, 12),
    'double_operators': (8, 10),
    'const': (5, 6),
    'identifier': (2,),
}
